# Demo walkthrough (about 10 minutes)

## 1. Start

Start the API and UI (see README), then open http://localhost:5173. The header shows the schema version
hash, a green dot when live updates are connected, and the error and conflict counts.

## 2. Look at the draft

- The canvas shows all 37 tables, coloured by layer, plus the derived view `v_company_ownership` as a dashed card
  linked to `company_holder`. Click **Delivery only** to see just `dim_company`, `fact_company_year`,
  `fact_pay_line`, `fact_pay_policy` and their child tables (including `pay_line_role`).
- Relationships are drawn as crow's foot (many) to bar (one). Double-click an edge to delete it.
- Type `hq_city` in the search box. It finds `dim_company.head_office_city` through its CDP alias.

## 3. Conflicts and validation

The bottom panel lists 0 errors, 2 warnings (MOD-1 module weights) and 10 conflicts: the ownership rules to
confirm (20% votes for a controlling owner, 5% capital for a PE stake), the empty country list, 24 unconfirmed list
values (Conor's lists and the proposed `ref_role`), 17 empty ref tables (no Fixed Sets sheet), parked fields,
† columns to confirm, the undefined DER-10/11, rules hanging off "hold off" gates, and Protocol Map entries that
are not column names.

## 4. Checks

Open **Checks** on the left and click `NUM-01`. Every column it applies to is highlighted (the money columns in
`fact_company_year` and `fact_pay_line`). Click `STI-1`: it is one of Conor's rules, so its parent gate NUM-11
is highlighted, and the detail shows "applies when", "result if not" and the hold-off remark.

## 5. Edit in the UI

- Click `fact_pay_line`. The side panel shows grain, PK chips, partitioning, clustering and the column
  grid. Each column shows its lineage (protocol ID, priority, requirement, severity), any validation rule, †
  and its check count.
- From the **Field tray**, drag `role_start_year` onto `fact_pay_line`. An `INT64` column linked to the field
  appears, and the field leaves the tray.
- Drag from `fact_pay_line.pay_currency` (right handle) to `ref_currency.code` (left handle), or remove and
  re-add a relationship to see validation at work. Try typing `VARCHAR` as a type: the save is blocked with
  "not a valid BigQuery type".

## 6. Claude edits through MCP, live

Register the server (README), then ask Claude Code:

> Add a `year_of_birth` column to fact_pay_line linked to its field.

Claude calls `get_schema_summary` (for the version) and then `add_column(table="fact_pay_line",
name="year_of_birth", field_id="year_of_birth", ...)`. The UI shows a "Schema changed on disk" notice,
the column appears on the card and `year_of_birth` leaves the field tray. **Changelog** shows the entry with
actor `claude` next to your `ui` edits.

Also try: "What checks apply to base_salary and where does it live?" (one `get_field` call).

## 7. Re-import

Open **Import diff**. With unchanged workbooks it reads "No differences". Edit a cell, for example a
description in `inputs/Book1.xlsx`, save it, then click **Re-read workbooks**. Exactly that change is listed,
with before and after. Apply it, and the field and every linked column's description update. Ref values you
edited in the app show as app-owned and are not selected by default.

## 8. Export

Open **Export**, set project, dataset and location, then click **Copy full script**. The badge confirms that
every statement parses with sqlglot (BigQuery dialect). Each table also has its own **Copy** button, in
dependency order. If `bq` is installed and authenticated, **bq --dry_run** checks the script against BigQuery.

## 9. Review the change in git

```bash
git diff schema/schema.json
```

Every edit is a readable JSON diff. Commit it on a branch and open a PR for a teammate to review.
