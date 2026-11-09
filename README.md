# Schema Playground: Allshares CDP

A local tool for designing the BigQuery star schema behind the Allshares CDP enrichment pipeline.
It imports the field catalogue and check catalogue from Excel, proposes a draft star schema, lets you
reshape it in a Power BI-style model view, and produces a ready-to-run BigQuery script. Claude can read
and edit the same schema through an MCP server.

**`schema/schema.json` is the single source of truth.** The UI, the MCP server, the importer and the
exporter all read and write it through `schema_core`. Git is the sharing, review and rollback mechanism:
every change is a reviewable diff. Canvas positions live in `schema/layout.json`, and every applied
operation is appended to `schema/changelog.jsonl` with its actor (`ui`, `claude` or `import`).

## Setup

Requires Python 3.11+ and Node 18+.

```bash
python -m venv .venv
```

```bash
.venv/Scripts/python -m pip install -e ".[dev]"
```

```bash
npm --prefix web install
```

(On macOS/Linux use `.venv/bin/python`.)

## Run

The first import builds `schema/schema.json` from the workbooks in `inputs/`. It is already done and
committed; run it again only to start over (`--force` overwrites).

```bash
.venv/Scripts/python -m schema_core import --init --force
```

Start the API (port 8000) and the UI (port 5173), each in its own terminal:

```bash
.venv/Scripts/python -m uvicorn api.main:app --port 8000
```

```bash
npm --prefix web run dev
```

Open http://localhost:5173. Or build the UI once (`npm --prefix web run build`) and use the API alone:
it serves `web/dist` at http://localhost:8000.

### Command line

```bash
.venv/Scripts/python -m schema_core validate
```

```bash
.venv/Scripts/python -m schema_core conflicts
```

```bash
.venv/Scripts/python -m schema_core diff
```

```bash
.venv/Scripts/python -m schema_core export --out schema.sql --bq-dry-run
```

`apply-import ID ...` applies accepted re-import items; `--all-safe` applies every item that is not app-owned.

## MCP server (Claude Code and Claude Desktop)

The server uses stdio. Register it with Claude Code using the absolute path to the venv's Python
(the package is installed into the venv, so the working directory does not matter):

```bash
claude mcp add schema-playground -- C:/Users/EluriKrishnaSaiRahul/Desktop/Allshares/POC/Schema/.venv/Scripts/python.exe -m mcp_server
```

Add `--scope project` to share the registration through `.mcp.json`. For Claude Desktop, add this to
`claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "schema-playground": {
      "command": "C:/Users/EluriKrishnaSaiRahul/Desktop/Allshares/POC/Schema/.venv/Scripts/python.exe",
      "args": ["-m", "mcp_server"]
    }
  }
}
```

**Read tools:** `get_schema_summary`, `list_tables`, `get_table`, `search`, `get_field`,
`checks_for_column`, `columns_for_check`, `list_ref_values`, `list_conflicts`, `validate`, `get_changelog`.
**Workflow tools:** `import_diff`, `apply_import_items`, `export_bigquery`.
**Write tools:** one per operation (below). Each takes `expected_version` (from `get_schema_summary` or the
previous write), `reason` and `dry_run`. A stale version is rejected, so Claude and the UI cannot overwrite
each other. When the UI is open, Claude's edits appear in it live.

## How it works

| Package | Role |
|---|---|
| `schema_core/models.py` | Pydantic models for `schema.json` (tables, columns, relationships, ref seeds, catalogue) |
| `schema_core/operations.py` | Typed operations. Nothing writes raw JSON |
| `schema_core/validation.py` | Errors block a save; warnings don't |
| `schema_core/store.py` | Version hash, file lock, atomic write, changelog |
| `schema_core/importer/` | Header-driven reading (`config/import_mapping.yaml`), draft (`config/draft_schema.yaml`), re-import diff |
| `schema_core/export.py` | BigQuery DDL + seed `INSERT`s, sqlglot parse check, optional `bq --dry_run` |
| `schema_core/conflicts.py` | The Conflicts panel |
| `api/` | FastAPI back end; `/api/events` pushes `schema.json` changes over SSE |
| `mcp_server/` | MCP server (official `mcp` SDK, stdio) |
| `web/` | React + TypeScript + Vite + React Flow UI |

**Operations:** `add_table`, `rename_table`, `delete_table`, `add_column`, `alter_column`, `rename_column`,
`delete_column`, `set_primary_key`, `add_relationship`, `delete_relationship`, `set_partition`,
`set_clustering`, `link_column_field`, `add_ref_value`, `update_ref_value`, `delete_ref_value`, `add_field`,
`link_field_check`, `unlink_field_check`. Beyond the brief's list: `alter_table` (layer, grain, description,
needed by the editor), and `update_field`, `add_check`, `update_check`, `update_field_check`, `upsert_note`
and `set_internal_reference`, so that accepted re-import items are ordinary operations too.

**Re-import** compares the workbooks with `schema.json` by stable keys: fields by name, checks by code,
pairs by (field, check), ref values by table + code. Removals are flagged and never applied. Items edited in
the app are marked app-owned and are not selected by default. Accepted items go through the normal
operations, validation and changelog. Changing a field's catalogue text refreshes the lineage on every
column linked to it.

**To change the importer for a new sheet or header**, edit `config/import_mapping.yaml`. To change the
draft schema produced on first import, edit `config/draft_schema.yaml`.

## Decisions taken on the inputs

The workbooks differ from the original brief in a few places. These defaults were agreed:

- **No `Fixed Sets` sheet exists.** 18 of 22 ref tables are empty, and the Conflicts panel says so. The importer reads
  a `Fixed Sets` sheet automatically once it is added (tested with a synthetic sheet). `months_in_role` and
  `sector_code` are column validation rules.
- **Conor's 02 Nov changes** come from `inputs/Allshares_Part1_gate_reference_02Nov.xlsx`. The 24 rules are imported as
  checks, with `parent_gates` as a list; status is `existing` where the note says "Existing gate", otherwise
  `to_do`. Gate suggestions are attached as `proposed_change`. Quote matching is stored as notes QM-1…5, and the
  load bar as LB-1…6 in sheet order (LB-2 hard checks, LB-4 review, LB-5 incomplete). Tracker fields come in
  as `new` fields; `year_of_birth`, `role_start_year` and `year_joined` are `parked`.
- **`DER-10` and `DER-11`** (cited in Book1 for `largest_holders`, defined nowhere) are placeholder checks with status `to_do`.
  Totals: 71 fields (55 + 13 new + 3 parked), 63 checks (37 + 2 + 24 rules), 386 field-check pairs.
- **Scores and weights are filled in** (not blank), and two modules sum to 1.198 and 1.365, so the MOD-1 warning fires.

## Tests

```bash
.venv/Scripts/python -m pytest
```

There is one test per validation error case, plus tests for import counts and quirks, the re-import diff
(an unchanged workbook gives an empty diff, a one-cell edit gives exactly that change, and app edits survive), the export
(sqlglot parse, dependency order, `NOT ENFORCED` keys), and UI/MCP parity (same diff and changelog, stale
versions rejected). See [DEMO.md](DEMO.md) for a walkthrough.
