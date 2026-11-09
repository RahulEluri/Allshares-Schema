"""Header-driven workbook reading through config/import_mapping.yaml."""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import openpyxl
import yaml

from ..store import ROOT

CONFIG_DIR = ROOT / "config"


def norm_header(h: Any) -> str:
    s = "" if h is None else str(h)
    s = re.sub(r"\([^)]*\)", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def clean(v: Any) -> Any:
    if isinstance(v, str):
        v = v.strip()
        return v or None
    if isinstance(v, (dt.datetime, dt.date)):
        return v.isoformat()
    return v


@dataclass
class Dataset:
    name: str
    rows: list[dict[str, Any]] = field(default_factory=list)
    found_sheets: list[str] = field(default_factory=list)
    missing: bool = False
    unmapped_headers: list[str] = field(default_factory=list)


class WorkbookReader:
    def __init__(self, mapping_path: Path | str | None = None, root: Path | str | None = None,
                 overrides: Optional[dict[str, str]] = None):
        self.mapping_path = Path(mapping_path or CONFIG_DIR / "import_mapping.yaml")
        self.mapping = yaml.safe_load(self.mapping_path.read_text(encoding="utf-8"))
        self.root = Path(root or ROOT)
        self.paths = {k: self._resolve(v) for k, v in self.mapping["workbooks"].items()}
        if overrides:
            self.paths.update({k: Path(v) for k, v in overrides.items()})
        self._books: dict[str, Any] = {}

    def _resolve(self, p: str) -> Path:
        path = Path(p)
        return path if path.is_absolute() else self.root / path

    def _book(self, key: str):
        if key not in self._books:
            path = self.paths[key]
            self._books[key] = openpyxl.load_workbook(path, data_only=True) if path.exists() else None
        return self._books[key]

    def read(self, name: str) -> Dataset:
        spec = self.mapping["datasets"][name]
        ds = Dataset(name=name)
        wb = self._book(spec["workbook"])
        if wb is None:
            if spec.get("required"):
                raise FileNotFoundError(f"Workbook for dataset '{name}' not found: {self.paths[spec['workbook']]}")
            ds.missing = True
            return ds
        sheets = [s for s in spec["sheets"] if s in wb.sheetnames]
        if not sheets:
            if spec.get("required"):
                raise KeyError(f"None of the sheets {spec['sheets']} for dataset '{name}' exist in {self.paths[spec['workbook']].name}")
            ds.missing = True
            return ds
        if spec.get("single_column"):
            for s in sheets:
                ds.found_sheets.append(s)
                for i, row in enumerate(wb[s].iter_rows(values_only=True), 1):
                    text = clean(row[0]) if row else None
                    if text is not None:
                        ds.rows.append({"text": str(text), "_sheet": s, "_row": i})
            return ds
        # Datasets with alternative sheet names (e.g. a future 'Conor Changes 02Nov') read the first found.
        sheets = sheets if name in ("fields",) else sheets[:1]
        for s in sheets:
            ds.found_sheets.append(s)
            ds.rows.extend(self._read_sheet(wb[s], spec, ds))
        return ds

    def _read_sheet(self, ws, spec: dict, ds: Dataset) -> list[dict[str, Any]]:
        cols: dict[str, list[str]] = spec["columns"]
        rows = list(ws.iter_rows(values_only=True))
        header_idx, colmap = None, {}
        for i, row in enumerate(rows[:10]):
            normed = [norm_header(h) for h in row]
            found = {}
            for logical, aliases in cols.items():
                for a in aliases:
                    na = norm_header(a)
                    if na in normed:
                        found[logical] = normed.index(na)
                        break
            if len(found) >= min(2, len(cols)):
                header_idx, colmap = i, found
                break
        if header_idx is None:
            raise ValueError(f"Could not find a header row in sheet '{ws.title}' for dataset '{ds.name}'")
        mapped = set(colmap.values())
        ds.unmapped_headers += [str(h) for j, h in enumerate(rows[header_idx]) if h is not None and j not in mapped]
        key = spec.get("numeric_key")
        out = []
        for r_i, row in enumerate(rows[header_idx + 1:], header_idx + 2):
            rec = {logical: clean(row[j]) if j < len(row) else None for logical, j in colmap.items()}
            if all(v is None for v in rec.values()):
                continue
            if key and not _is_number(rec.get(key)):
                continue  # section headers ("Identity (8)") and stray totals ("55")
            rec["_sheet"], rec["_row"] = ws.title, r_i
            out.append(rec)
        return out


def _is_number(v: Any) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    return isinstance(v, str) and re.fullmatch(r"\d+(\.\d+)?", v) is not None
