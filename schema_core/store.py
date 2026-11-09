"""The schema store: schema.json (versioned), layout.json, changelog.jsonl, settings.json.

Writes take a file lock, check `expected_version`, apply typed operations to a copy,
validate (errors block), then write atomically and append to the changelog.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from filelock import FileLock

from .diff import diff as structural_diff
from .models import Schema
from .operations import Ctx, OpError, parse_op
from .validation import Issue, errors, validate

ROOT = Path(os.environ.get("SCHEMA_PLAYGROUND_ROOT", Path(__file__).resolve().parent.parent))
DEFAULT_DIR = ROOT / "schema"
DEFAULT_SETTINGS = {"project": "your-gcp-project", "dataset": "allshares_cdp", "location": "EU"}


class VersionConflict(Exception):
    def __init__(self, expected: str, actual: str):
        super().__init__(f"Schema changed since you read it (expected version {expected}, current {actual}). Reload and retry.")
        self.expected, self.actual = expected, actual


def dump_schema(schema: Schema) -> dict[str, Any]:
    return schema.model_dump(mode="json", exclude_none=True)


def compute_version(data: dict[str, Any]) -> str:
    body = {k: v for k, v in data.items() if k != "version"}
    blob = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


@dataclass
class ApplyResult:
    ok: bool
    version: str
    dry_run: bool
    diff: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class SchemaStore:
    def __init__(self, directory: Path | str = DEFAULT_DIR):
        self.dir = Path(directory)
        self.schema_path = self.dir / "schema.json"
        self.layout_path = self.dir / "layout.json"
        self.changelog_path = self.dir / "changelog.jsonl"
        self.settings_path = self.dir / "settings.json"
        self.lock = FileLock(str(self.dir / "schema.json.lock"), timeout=10)

    # ------------------------------------------------------------------ reads
    def exists(self) -> bool:
        return self.schema_path.exists()

    def load(self) -> tuple[Schema, str]:
        if not self.exists():
            raise FileNotFoundError(f"{self.schema_path} does not exist; run `python -m schema_core import --init` first")
        data = json.loads(self.schema_path.read_text(encoding="utf-8"))
        version = compute_version(data)
        data.pop("version", None)
        return Schema.model_validate(data), version

    def version(self) -> str:
        return self.load()[1]

    def read_layout(self) -> dict[str, Any]:
        if not self.layout_path.exists():
            return {"positions": {}}
        return json.loads(self.layout_path.read_text(encoding="utf-8"))

    def write_layout(self, layout: dict[str, Any]) -> None:
        _atomic_write(self.layout_path, json.dumps(layout, indent=2, sort_keys=True) + "\n")

    def read_settings(self) -> dict[str, Any]:
        s = dict(DEFAULT_SETTINGS)
        if self.settings_path.exists():
            s.update(json.loads(self.settings_path.read_text(encoding="utf-8")))
        return s

    def write_settings(self, settings: dict[str, Any]) -> dict[str, Any]:
        merged = {**self.read_settings(), **{k: v for k, v in settings.items() if k in DEFAULT_SETTINGS}}
        _atomic_write(self.settings_path, json.dumps(merged, indent=2) + "\n")
        return merged

    def changelog(self, limit: Optional[int] = None) -> list[dict[str, Any]]:
        if not self.changelog_path.exists():
            return []
        lines = self.changelog_path.read_text(encoding="utf-8").splitlines()
        entries = [json.loads(l) for l in lines if l.strip()]
        return entries[-limit:] if limit else entries

    # ------------------------------------------------------------------ writes
    def _write(self, schema: Schema) -> str:
        data = dump_schema(schema)
        version = compute_version(data)
        out = {"version": version, **data}
        _atomic_write(self.schema_path, json.dumps(out, indent=2, ensure_ascii=False) + "\n")
        return version

    def _log(self, entries: Iterable[dict[str, Any]]) -> None:
        self.changelog_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.changelog_path, "a", encoding="utf-8", newline="\n") as fh:
            for e in entries:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")

    def initialize(self, schema: Schema, actor: str, reason: str, force: bool = False) -> str:
        """Write a whole schema (first import). Refuses to overwrite unless force=True."""
        with self.lock:
            if self.exists() and not force:
                raise FileExistsError(f"{self.schema_path} already exists; use re-import (diff) instead")
            issues = validate(schema)
            errs = errors(issues)
            if errs:
                raise ValueError("Initial schema does not validate: " + "; ".join(i.message for i in errs[:10]))
            version = self._write(schema)
            self._log([{
                "ts": _now(), "actor": actor, "op": "initialize", "reason": reason,
                "args": {"tables": len(schema.tables), "fields": len(schema.catalogue.fields),
                         "checks": len(schema.catalogue.checks), "field_checks": len(schema.catalogue.field_checks)},
                "version_before": None, "version_after": version,
            }])
            return version

    def apply(
        self,
        ops: list[dict[str, Any]] | list[Any],
        expected_version: str,
        actor: str,
        reason: str = "",
        dry_run: bool = False,
        owner: str = "app",
        source: Optional[str] = None,
    ) -> ApplyResult:
        parsed = [parse_op(o) for o in ops]
        with self.lock:
            schema, current = self.load()
            if expected_version != current:
                raise VersionConflict(expected_version, current)
            before = dump_schema(schema)
            work = schema.model_copy(deep=True)
            ctx = Ctx(owner=owner)
            try:
                for op in parsed:
                    op.apply(work, ctx)
            except OpError as e:
                return ApplyResult(ok=False, version=current, dry_run=dry_run,
                                   errors=[{"severity": "error", "code": "operation", "message": str(e)}], message=str(e))
            # validate_assignment does not catch nested in-place list edits; revalidate the whole model.
            work = Schema.model_validate(dump_schema(work))
            issues = validate(work)
            after = dump_schema(work)
            changes = structural_diff(before, after)
            errs = [i.model_dump() for i in issues if i.severity == "error"]
            warns = [i.model_dump() for i in issues if i.severity == "warning"]
            if errs:
                return ApplyResult(ok=False, version=current, dry_run=dry_run, diff=changes, errors=errs,
                                   warnings=warns, message=f"Blocked by {len(errs)} validation error(s)")
            if dry_run:
                return ApplyResult(ok=True, version=current, dry_run=True, diff=changes, warnings=warns,
                                   message="Dry run: nothing saved")
            new_version = self._write(work)
            ts = _now()
            self._log([{
                "ts": ts, "actor": actor, "op": op.op, "args": op.args(), "reason": reason,
                **({"source": source} if source else {}),
                "version_before": current, "version_after": new_version,
            } for op in parsed])
            return ApplyResult(ok=True, version=new_version, dry_run=False, diff=changes, warnings=warns,
                               message=f"Applied {len(parsed)} operation(s)")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def issues_as_dicts(issues: list[Issue]) -> list[dict[str, Any]]:
    return [i.model_dump() for i in issues]
