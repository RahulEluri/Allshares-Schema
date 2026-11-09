# Schema Playground: Allshares CDP

A local tool for designing the BigQuery star schema behind the Allshares CDP enrichment pipeline.
It imports the field catalogue and check catalogue from Excel, proposes a draft star schema, lets you
reshape it in a Power BI-style model view, and produces a ready-to-run BigQuery script. Claude can read
and edit the same schema through an MCP server.

**`schema/schema.json` is the single source of truth.** The UI, the MCP server, the importer and the
exporter all read and write it through `schema_core`. Git is the sharing, review and rollback mechanism:
every change is a reviewable diff. Canvas positions live in `schema/layout.json`, and every applied
operation is appended to `schema/changelog.jsonl` with its actor (`ui`, `claude` or `import`).

## Where to start

Pick the row that matches what you want to do.

| You want to… | Start here |
|---|---|
| **Understand the schema without running anything** | Open [`examples/worked_example_3_companies.xlsx`](examples/worked_example_3_companies.xlsx). Read its **README** sheet (companies, colour legend, sheet index), then the **Trace** sheet, which follows one value from the source document to the delivery table. Every table has its own colour-coded sheet. See [Worked example](#worked-example). |
| **See the BigQuery DDL** | [`schema.sql`](schema.sql): the full script (dataset, 37 tables in dependency order, 1 derived view, `NOT ENFORCED` keys, seed `INSERT`s), checked with sqlglot. |
| **See the design decisions** | [Schema at a glance](#schema-at-a-glance) and [Decisions taken on the inputs](#decisions-taken-on-the-inputs) below. The open questions are listed by `python -m schema_core conflicts` and in the UI's Conflicts panel. |
| **Run the model view and edit the schema** | [Setup](#setup), then [Run](#run), then the 10-minute walkthrough in [DEMO.md](DEMO.md). |
| **Let Claude read and edit the schema** | [MCP server](#mcp-server-claude-code-and-claude-desktop). |
| **Change what the importer reads, or the first-import draft** | [`config/import_mapping.yaml`](config/import_mapping.yaml) (sheet and header mapping) and [`config/draft_schema.yaml`](config/draft_schema.yaml) (tables, columns, views, seeds). |
| **Work on the code** | [How it works](#how-it-works) and [Tests](#tests). |

### Repository layout

| Path | What it is |
|---|---|
| `schema/schema.json` | The schema (source of truth, versioned by hash). Do not edit by hand: use the UI, MCP or CLI |
| `schema/changelog.jsonl`, `schema/layout.json` | Every applied operation; canvas positions |
| `schema.sql` | Exported BigQuery script (regenerate with `python -m schema_core export --out schema.sql`) |
| `examples/` | The worked-example workbook and the script that builds it |
| `inputs/` | The source workbooks: `Book1.xlsx`, `allshares_field_checks.xlsx`, `Allshares_Part1_gate_reference_02Nov.xlsx` |
| `config/` | Import mapping and first-import draft |
| `schema_core/` | Models, operations, validation, import, export (Python) |
| `api/`, `web/`, `mcp_server/` | FastAPI back end, React Flow UI, MCP server |
| `tests/` | pytest suite |

## Schema at a glance

37 tables and 1 derived view, in layers (the colours match the UI and the worked example):

| Layer | Tables |
|---|---|
| **Delivery: dimension** | `dim_company`: one row per company |
| **Delivery: facts** | `fact_company_year` (company × fiscal year), `fact_pay_policy` (company × fiscal year), `fact_pay_line` (one row per disclosed pay line) |
| **Delivery: children** | `company_name_alias`, `company_holder` (shareholders), `company_breakdown` (segment and country splits), `pay_line_role` (every role a pay line covers), `pay_line_total_component` |
| **Derived view** | `v_company_ownership`: controlling owner, ownership type, PE stake and as-of date, calculated from `company_holder` |
| **Provenance** | `dim_source` (source documents), `fact_field_value` (every extracted value with locator, snippet and quote match), `fact_check_result` (one row per value per check) |
| **Catalogue** | `dim_field` (72 fields), `dim_check` (63 checks and rules), `bridge_field_check` (386 field-check pairs) |
| **Reference lists** | 22 `ref_*` tables, e.g. `ref_currency`, `ref_exchange`, `ref_ownership_type`, `ref_role`, `ref_check_result` |

Principle from Allshares: record, do not correct. Extracted values are never overwritten; check results sit beside them.

## Worked example

[`examples/worked_example_3_companies.xlsx`](examples/worked_example_3_companies.xlsx) shows the whole schema filled
for FY2025, with every table on its own sheet. **The three companies are fictional.** All names, people, holders,
IDs and numbers are invented to show how the schema is used.

| Company | What it demonstrates |
|---|---|
| **NVK** Nordvik Kraft AB (SE, SEK) | Controlling family foundation with dual-class votes, a PE holder, a part-year former CEO (months_in_role = 3, not annualised), an aggregate executive line, and the CEO also on the board (one person, two pay lines) |
| **SRS** Saarela Systems Oyj (FI, EUR) | No controlling owner but a PE stake, a CEO who is also acting CFO (one pay line, two rows in `pay_line_role`), and a total that does not reconcile (XF-01 fail) |
| **FJM** Fjordline Marine ASA (NO, NOK) | State-controlled, a holder with a different as-of date (DER-07 review), FTE above headcount (NUM-05 fail), a COO paid in SGD (CUR-1 review) and a quote not found (SRC-1 fail) |

How to read it:

- **README sheet:** companies, colour legend and a linked index of all 40 sheets with row counts.
- **Trace sheet:** NVK CEO base salary, from `dim_source` → `fact_field_value` (locator, snippet, quote match) →
  `fact_check_result` → `fact_pay_line` → catalogue. Each value links to its cell in the table sheets.
- **Colours:** tab and header colour = layer (blue dimension, orange fact, green child, amber derived view, teal
  provenance, purple catalogue, grey reference). Dark headers mark primary-key columns. Row 3 shows each column's
  BigQuery type, PK, FK target, catalogue field and † (column to confirm). Hover a header for its description.
- **Check results:** green pass, red fail, yellow review, grey not run.
- **`v_company_ownership`** uses live Excel formulas over `company_holder`, so edits to a holder flow through.
- **IDs** are deterministic UUID v5 (the same key gives the same ID on every re-run). The pay-line IDs for the NVK
  lines match the examples in the 9 November pay-storage note.

The workbook is generated from `schema.json`, so it always matches the current schema. Rebuild it after a schema change:

```bash
.venv/Scripts/python examples/build_worked_example.py
```

The example data lives in `examples/worked_example_data.py`. The generator sets "recalculate on open"; open and
save the file once in Excel to store the calculated values.

## Setup

Requires Python 3.11+ and Node 18+.

```bash
git clone https://github.com/RahulEluri/Allshares-Schema.git
```

```bash
cd Allshares-Schema
```

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

`schema/schema.json` is already built and committed. Rebuild it from the workbooks in `inputs/` only to start
over (`--force` overwrites the current schema and its edits):

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

The server uses stdio. Register it with Claude Code using the absolute path to the venv's Python in your clone
(the package is installed into the venv, so the working directory does not matter):

```bash
claude mcp add schema-playground -- <path-to-clone>/.venv/Scripts/python.exe -m mcp_server
```

Add `--scope project` to share the registration through `.mcp.json`. For Claude Desktop, add this to
`claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "schema-playground": {
      "command": "<path-to-clone>/.venv/Scripts/python.exe",
      "args": ["-m", "mcp_server"]
    }
  }
}
```

**Read tools:** `get_schema_summary`, `list_tables`, `get_table`, `search`, `get_field`,
`checks_for_column`, `columns_for_check`, `list_ref_values`, `list_conflicts`, `validate`, `get_changelog`.
**Workflow tools:** `import_diff`, `apply_import_items`, `export_bigquery`.
**Write tools:** one per operation (below), plus `set_view` / `delete_view`. Each takes `expected_version` (from
`get_schema_summary` or the previous write), `reason` and `dry_run`. A stale version is rejected, so Claude and
the UI cannot overwrite each other. When the UI is open, Claude's edits appear in it live.

Try: "What checks apply to base_salary and where does it live?" or "Add a `year_of_birth` column to
fact_pay_line linked to its field."

## How it works

| Package | Role |
|---|---|
| `schema_core/models.py` | Pydantic models for `schema.json` (tables, columns, relationships, views, ref seeds, catalogue) |
| `schema_core/operations.py` | Typed operations. Nothing writes raw JSON |
| `schema_core/validation.py` | Errors block a save; warnings don't |
| `schema_core/store.py` | Version hash, file lock, atomic write, changelog |
| `schema_core/importer/` | Header-driven reading (`config/import_mapping.yaml`), draft (`config/draft_schema.yaml`), re-import diff |
| `schema_core/export.py` | BigQuery DDL + views + seed `INSERT`s, sqlglot parse check, optional `bq --dry_run` |
| `schema_core/conflicts.py` | The Conflicts panel |
| `api/` | FastAPI back end; `/api/events` pushes `schema.json` changes over SSE |
| `mcp_server/` | MCP server (official `mcp` SDK, stdio) |
| `web/` | React + TypeScript + Vite + React Flow UI |

**Operations:** `add_table`, `rename_table`, `delete_table`, `add_column`, `alter_column`, `rename_column`,
`delete_column`, `set_primary_key`, `add_relationship`, `delete_relationship`, `set_partition`,
`set_clustering`, `link_column_field`, `add_ref_value`, `update_ref_value`, `delete_ref_value`, `add_field`,
`link_field_check`, `unlink_field_check`. Beyond the brief's list: `alter_table` (layer, grain, description,
needed by the editor), `set_view` and `delete_view` (derived views), and `update_field`, `add_check`,
`update_check`, `update_field_check`, `upsert_note` and `set_internal_reference`, so that accepted re-import
items are ordinary operations too.

**Re-import** compares the workbooks with `schema.json` by stable keys: fields by name, checks by code,
pairs by (field, check), ref values by table + code. Removals are flagged and never applied. Items edited in
the app are marked app-owned and are not selected by default. Accepted items go through the normal
operations, validation and changelog. Changing a field's catalogue text refreshes the lineage on every
column linked to it.

**To change the importer for a new sheet or header**, edit `config/import_mapping.yaml`. To change the
draft schema produced on first import, edit `config/draft_schema.yaml`.

### Derived views

A derived view is a set of values calculated from one table, grouped by key columns. It is exported as
`CREATE OR REPLACE VIEW … AS SELECT … GROUP BY …`. Each calculated column has a BigQuery expression, and can link to
a catalogue field so the field counts as placed and its checks follow. Validation parses every expression with sqlglot
and checks that it only uses columns of the source table. Renaming a source column rewrites the expressions;
deleting the source table needs `cascade`. Views are edited with the `set_view` / `delete_view` operations (MCP tools of
the same name) or in `config/draft_schema.yaml`, and shown in the UI as dashed cards.

## Decisions taken on the inputs

The workbooks differ from the original brief in a few places. These defaults were agreed:

- **No `Fixed Sets` sheet exists.** 17 of 22 ref tables are empty, and the Conflicts panel says so. The importer reads
  a `Fixed Sets` sheet automatically once it is added (tested with a synthetic sheet). `months_in_role` and
  `sector_code` are column validation rules.
- **Conor's 02 Nov changes** come from `inputs/Allshares_Part1_gate_reference_02Nov.xlsx`. The 24 rules are imported as
  checks, with `parent_gates` as a list; status is `existing` where the note says "Existing gate", otherwise
  `to_do`. Gate suggestions are attached as `proposed_change`. Quote matching is stored as notes QM-1…5, and the
  load bar as LB-1…6 in sheet order (LB-2 hard checks, LB-4 review, LB-5 incomplete). Tracker fields come in
  as `new` fields; `year_of_birth`, `role_start_year` and `year_joined` are `parked`.
- **`DER-10` and `DER-11`** (cited in Book1 for `largest_holders`, defined nowhere) are placeholder checks with status `to_do`.
  Totals: 72 fields (55 + 13 Conor + 3 parked + `role_code`), 63 checks (37 + 2 + 24 rules), 386 field-check pairs.
- **Scores and weights are filled in** (not blank), and two modules sum to 1.198 and 1.365, so the MOD-1 warning fires.
- **Ownership lives in the `company_holder` child table**, one row per holder with name, type, % capital, % votes,
  group, tie flag, as-of date, percentage basis and list cutoff. `controlling_owner`, `controlling_owner_name`,
  `ownership_type`, `pe_stake_5pct` and `ownership_as_of` are not stored. The derived view `v_company_ownership`
  calculates them per company and fiscal year (controlling owner = a holder with 20% or more of the votes; PE stake =
  a `private_equity` holder with 5% or more of the capital). `ref_controlling_owner` was removed. Both thresholds
  are to confirm with Allshares.
- **Roles:** `ref_role` holds the standard role list (all `Proposed: confirm with Allshares`), with `role_group`, `is_ceo`,
  `sort_order` and `source_titles`. `fact_pay_line.role_code` is the primary role, used for benchmarking and the
  pay-line ID key. `pay_line_role` lists every role a pay line covers ("CEO and CFO" gives two rows, one `is_primary`),
  with optional start and end dates for part-year roles. `role_code` is a playground field (`extra_fields` in
  `config/draft_schema.yaml`) until it reaches the workbook.
- **Not yet done:** `person_key` (links one person's pay lines; waits on the personal-data decision) and a derived view
  counting roles per pay line.

## Tests

```bash
.venv/Scripts/python -m pytest
```

There is one test per validation error case, plus tests for import counts and quirks, the re-import diff
(an unchanged workbook gives an empty diff, a one-cell edit gives exactly that change, and app edits survive), the export
(sqlglot parse, dependency order, `NOT ENFORCED` keys), derived views, roles, and UI/MCP parity (same diff and changelog,
stale versions rejected). See [DEMO.md](DEMO.md) for a walkthrough.
