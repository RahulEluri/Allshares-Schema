"""Command line: python -m schema_core <command>

  import --init [--force]     first import: build the draft schema from the workbooks
  diff                        re-import diff (workbooks vs schema.json)
  apply-import ID [ID ...]    apply accepted diff items (use --all-safe for every non-app-owned item)
  validate                    run validation
  conflicts                   list known conflicts
  export [--table T] [--out FILE] [--bq-dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys

from .conflicts import list_conflicts
from .export import bq_dry_run, export_bigquery, parse_check
from .store import SchemaStore
from .validation import validate


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m schema_core")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("import")
    p.add_argument("--init", action="store_true", required=True)
    p.add_argument("--force", action="store_true", help="overwrite an existing schema.json")
    sub.add_parser("diff")
    p = sub.add_parser("apply-import")
    p.add_argument("ids", nargs="*")
    p.add_argument("--all-safe", action="store_true")
    sub.add_parser("validate")
    sub.add_parser("conflicts")
    p = sub.add_parser("export")
    p.add_argument("--table")
    p.add_argument("--out")
    p.add_argument("--bq-dry-run", action="store_true")
    a = ap.parse_args(argv)
    store = SchemaStore()

    if a.cmd == "import":
        from .importer.draft import build_draft
        from .importer.snapshot import build_snapshot
        snap = build_snapshot()
        schema = build_draft(snap)
        v = store.initialize(schema, actor="import", reason="First import from workbooks", force=a.force)
        print(f"Wrote {store.schema_path} (version {v}): {len(schema.tables)} tables, {len(schema.catalogue.fields)} fields, "
              f"{len(schema.catalogue.checks)} checks, {len(schema.catalogue.field_checks)} field-check pairs")
        for n in snap.notices:
            print("notice:", n)
        return 0
    if a.cmd == "diff":
        from .importer.reimport import import_diff
        d = import_diff(store)
        print(json.dumps({"version": d["version"], "summary": d["summary"],
                          "items": [{k: i[k] for k in ("id", "kind", "app_owned", "applicable", "changes")} for i in d["items"]]},
                         indent=2, default=str))
        return 0
    if a.cmd == "apply-import":
        from .importer.reimport import apply_import_items, import_diff
        d = import_diff(store)
        ids = a.ids or [i["id"] for i in d["items"] if a.all_safe and i["applicable"] and not i["app_owned"]]
        if not ids:
            print("Nothing to apply")
            return 0
        res = apply_import_items(store, ids, d["version"], actor="ui")
        print(res.message, res.version)
        return 0 if res.ok else 1
    schema, version = store.load()
    if a.cmd == "validate":
        issues = validate(schema)
        for i in issues:
            print(f"{i.severity:7} {i.code:22} {i.message}")
        print(f"{sum(i.severity == 'error' for i in issues)} error(s), {sum(i.severity == 'warning' for i in issues)} warning(s)")
        return 1 if any(i.severity == "error" for i in issues) else 0
    if a.cmd == "conflicts":
        for c in list_conflicts(schema):
            print(f"- {c['title']}: {c['detail']}")
            for it in c["items"][:15]:
                print(f"    {it}")
        return 0
    if a.cmd == "export":
        st = store.read_settings()
        sql = export_bigquery(schema, st["project"], st["dataset"], st.get("location"), table=a.table)
        chk = parse_check(sql)
        if not chk["ok"]:
            print("sqlglot parse check FAILED:", chk["error"], file=sys.stderr)
            return 1
        if a.out:
            open(a.out, "w", encoding="utf-8").write(sql)
            print(f"Wrote {a.out} ({chk['statements']} statements, sqlglot OK)")
        else:
            sys.stdout.write(sql)
        if a.bq_dry_run:
            print(json.dumps(bq_dry_run(sql, st["project"]), indent=2), file=sys.stderr)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
