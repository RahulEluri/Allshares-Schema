-- Allshares CDP schema: 37 tables. Keys are NOT ENFORCED.

CREATE SCHEMA IF NOT EXISTS `your-gcp-project.allshares_cdp`
OPTIONS(location="EU");

-- Ref tables

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_country` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  region STRING OPTIONS(description="Region grouping"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Countries (ISO 3166-1 alpha-2). Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_country_currency` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  currency_code STRING OPTIONS(description="ISO 4217 currency of the country"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Each country's own currency, for check CUR-1. code = country code. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_currency` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Currencies (ISO 4217). Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_exchange` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Exchanges (ISO 10383 MIC). Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_exchange_segment` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Exchange market segments. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_listing_status` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Listing status. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_accounting_basis` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Accounting standards. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_ownership_type` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Holder / owner types (family, private equity, state, ...). Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_market_cap_band` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Market cap bands. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_role_disclosure` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Who a pay line discloses. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_pension_type` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Executive pension types. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_period_coverage` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Pay period coverage. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_holder_list_cutoff` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="How the largest-holders list was cut off. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_share_count_basis` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Basis of the share count. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_pct_of` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="What a percentage is a percentage of. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_units` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Reporting units (units, thousands, millions). Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_source_type` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Source document types. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_lti_basis` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Basis of an LTI value (Conor 02 Nov, LTI basis). Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_sti_max_basis` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="How maximum STI is stated (Conor 02 Nov, STI basis). Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_quote_match` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Result of the quote check (Conor 02 Nov, quote matching). Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_check_result` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Outcome of a check. Grain: one row per code.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.ref_role` (
  code STRING NOT NULL OPTIONS(description="Code (primary key)"),
  label STRING OPTIONS(description="Display label"),
  meaning STRING OPTIONS(description="Meaning / when to use"),
  status STRING OPTIONS(description="In use, Proposed (confirm with Allshares) or Review"),
  list_source STRING OPTIONS(description="Where the list comes from"),
  role_group STRING OPTIONS(description="executive or board"),
  is_ceo BOOL OPTIONS(description="The role is the chief executive"),
  sort_order INT64 OPTIONS(description="Seniority order for display"),
  source_titles STRING OPTIONS(description="Titles seen in reports that map to this code"),
  PRIMARY KEY (code) NOT ENFORCED
)
OPTIONS(description="Standard roles for pay lines (role_code). List to agree with Allshares before Tier 2. Grain: one row per code.");

-- Catalogue

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.dim_field` (
  field_name STRING NOT NULL OPTIONS(description="Field name (stable key)"),
  protocol_id STRING,
  cdp_column STRING OPTIONS(description="CDP column per the Protocol Map"),
  module STRING,
  data_category STRING,
  grain STRING,
  field_type STRING OPTIONS(description="direct or derived"),
  format STRING,
  description STRING,
  read_from STRING,
  method STRING,
  priority STRING,
  requirement STRING,
  severity STRING,
  fill_of_50 INT64,
  note STRING,
  status STRING OPTIONS(description="active, new or parked"),
  PRIMARY KEY (field_name) NOT ENFORCED
)
OPTIONS(description="The field catalogue (Book1 plus Conor's tracker fields). Grain: one row per catalogue field.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.dim_check` (
  check_code STRING NOT NULL,
  check_name STRING,
  check_fx STRING OPTIONS(description="direct or derived"),
  check_type STRING OPTIONS(description="hard or soft"),
  applies_to_categories STRING OPTIONS(description="Comma-separated data categories"),
  parent_gate STRING OPTIONS(description="Parent gate(s) for Conor's rules, comma-separated"),
  status STRING OPTIONS(description="active, hold_off, to_do, confirmed or existing"),
  remarks STRING,
  PRIMARY KEY (check_code) NOT ENFORCED
)
OPTIONS(description="The check catalogue (All Checks plus Conor's rules). Grain: one row per check or rule.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.bridge_field_check` (
  field_name STRING NOT NULL,
  check_code STRING NOT NULL,
  pass_criteria STRING,
  fail_criteria STRING,
  example STRING,
  reference STRING,
  remarks STRING,
  score NUMERIC,
  weight NUMERIC OPTIONS(description="Weighted score for the module"),
  PRIMARY KEY (field_name, check_code) NOT ENFORCED,
  CONSTRAINT fk_bridge_field_check_field_name FOREIGN KEY (field_name) REFERENCES `your-gcp-project.allshares_cdp.dim_field`(field_name) NOT ENFORCED,
  CONSTRAINT fk_bridge_field_check_check_code FOREIGN KEY (check_code) REFERENCES `your-gcp-project.allshares_cdp.dim_check`(check_code) NOT ENFORCED
)
OPTIONS(description="Which checks apply to which fields. Grain: one row per field and check.");

-- Dimensions

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.dim_company` (
  company_id STRING NOT NULL OPTIONS(description="CDP company ID"),
  legal_name STRING OPTIONS(description="Registered legal name [Protocol ID: C01; CDP alias: company_name, aliases]"),
  lei STRING OPTIONS(description="Legal Entity Identifier (20 characters, ISO 17442) [Protocol ID: C02; CDP alias: lei]"),
  business_id STRING OPTIONS(description="National registration number [Protocol ID: C03; CDP alias: ref_company_identifiers]"),
  cik STRING OPTIONS(description="SEC Central Index Key (US registrants only; not in the protocol) [Protocol ID: Not in protocol]"),
  country_code STRING OPTIONS(description="Country of incorporation (ISO 3166) [Protocol ID: C08; CDP alias: country_code]"),
  head_office_city STRING OPTIONS(description="Head office city [Protocol ID: C08; CDP alias: hq_city]"),
  website STRING OPTIONS(description="Company website domain [Protocol ID: C09; CDP alias: new]"),
  isin STRING OPTIONS(description="ISIN of the main share line [Protocol ID: C04; CDP alias: isin]"),
  ticker STRING OPTIONS(description="Trading symbol on the primary exchange [Protocol ID: C05; CDP alias: ticker_primary]"),
  exchange STRING OPTIONS(description="Primary exchange (ISO 10383 MIC) [Protocol ID: C05; CDP alias: exchange_primary]"),
  exchange_segment STRING OPTIONS(description="Market segment (e.g. Large Cap, MTF) [Protocol ID: C06; CDP alias: exchange_segment]"),
  listing_status STRING OPTIONS(description="Listed, delisted or suspended [Protocol ID: C07; CDP alias: listing_status]"),
  listing_date DATE OPTIONS(description="Date first admitted to trading [Protocol ID: C07; CDP alias: listed_date]"),
  sector_code STRING OPTIONS(description="National industry code (e.g. SIC, NACE) [Protocol ID: C10; CDP alias: sector_primary; Rule: NACE class 'NN.NN']"),
  sector_code_scheme STRING OPTIONS(description="Which industry code scheme sector_code uses (NACE, SIC, ...)"),
  sub_sector STRING OPTIONS(description="One-sentence business description [Protocol ID: C11; CDP alias: sub_sector]"),
  ultimate_parent STRING OPTIONS(description="Ultimate parent company, if any [Protocol ID: C21; CDP alias: new]"),
  PRIMARY KEY (company_id) NOT ENFORCED,
  CONSTRAINT fk_dim_company_country_code FOREIGN KEY (country_code) REFERENCES `your-gcp-project.allshares_cdp.ref_country`(code) NOT ENFORCED,
  CONSTRAINT fk_dim_company_exchange FOREIGN KEY (exchange) REFERENCES `your-gcp-project.allshares_cdp.ref_exchange`(code) NOT ENFORCED,
  CONSTRAINT fk_dim_company_exchange_segment FOREIGN KEY (exchange_segment) REFERENCES `your-gcp-project.allshares_cdp.ref_exchange_segment`(code) NOT ENFORCED,
  CONSTRAINT fk_dim_company_listing_status FOREIGN KEY (listing_status) REFERENCES `your-gcp-project.allshares_cdp.ref_listing_status`(code) NOT ENFORCED
)
OPTIONS(description="Stable company attributes. Grain: one row per company.");

-- Provenance and facts

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.dim_source` (
  source_id STRING NOT NULL OPTIONS(description="Source ID, e.g. AR-2025-SYD"),
  company_id STRING,
  source_type STRING,
  fiscal_year INT64,
  title STRING,
  url STRING,
  gcs_path STRING,
  publish_date DATE,
  language STRING,
  retrieved_at TIMESTAMP,
  PRIMARY KEY (source_id) NOT ENFORCED,
  CONSTRAINT fk_dim_source_company_id FOREIGN KEY (company_id) REFERENCES `your-gcp-project.allshares_cdp.dim_company`(company_id) NOT ENFORCED
)
OPTIONS(description="Registered source documents (e.g. AR-2025-SYD). Grain: one row per source document.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.fact_company_year` (
  company_id STRING NOT NULL,
  fiscal_year INT64 NOT NULL OPTIONS(description="Fiscal year the data covers [Protocol ID: C15; CDP alias: fiscal_year]"),
  fiscal_year_end DATE OPTIONS(description="Fiscal year end date [Protocol ID: C15; CDP alias: fiscal_year]"),
  reporting_currency STRING OPTIONS(description="Currency of the financial statements (ISO 4217) [Protocol ID: C15; CDP alias: currency]"),
  units STRING OPTIONS(description="Units the financials are stated in"),
  accounting_basis STRING OPTIONS(description="Accounting standard (IFRS, US GAAP, local GAAP) [Protocol ID: C15; CDP alias: accounting basis]"),
  revenue NUMERIC OPTIONS(description="Revenue for the fiscal year [Protocol ID: C12; CDP alias: ref_company_financials]"),
  total_assets NUMERIC OPTIONS(description="Total assets at year end [Protocol ID: C13; CDP alias: ref_company_financials]"),
  ebitda NUMERIC OPTIONS(description="EBITDA, else operating profit (note says which) [Protocol ID: C14; CDP alias: ref_company_financials]"),
  ebitda_basis STRING OPTIONS(description="EBITDA or operating profit (which one ebitda holds)"),
  shares_outstanding INT64 OPTIONS(description="Shares outstanding (not issued) [Protocol ID: C17; CDP alias: for market cap band]"),
  share_price NUMERIC OPTIONS(description="Year-end share price [Protocol ID: C18; CDP alias: for market cap band]"),
  market_cap_band STRING OPTIONS(description="Market cap band: large >= EUR 1bn, mid >= EUR 150m, else small [Protocol ID: Derived: C17 x C18; CDP alias: for market cap band]"),
  headcount INT64 OPTIONS(description="Number of employees [Protocol ID: C16; CDP alias: headcount]"),
  fte NUMERIC OPTIONS(description="Full-time equivalents [Protocol ID: C16; CDP alias: fte]"),
  PRIMARY KEY (company_id, fiscal_year) NOT ENFORCED,
  CONSTRAINT fk_fact_company_year_company_id FOREIGN KEY (company_id) REFERENCES `your-gcp-project.allshares_cdp.dim_company`(company_id) NOT ENFORCED,
  CONSTRAINT fk_fact_company_year_reporting_currency FOREIGN KEY (reporting_currency) REFERENCES `your-gcp-project.allshares_cdp.ref_currency`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_company_year_units FOREIGN KEY (units) REFERENCES `your-gcp-project.allshares_cdp.ref_units`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_company_year_accounting_basis FOREIGN KEY (accounting_basis) REFERENCES `your-gcp-project.allshares_cdp.ref_accounting_basis`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_company_year_market_cap_band FOREIGN KEY (market_cap_band) REFERENCES `your-gcp-project.allshares_cdp.ref_market_cap_band`(code) NOT ENFORCED
)
OPTIONS(description="Company values that change per fiscal year. Grain: one row per company per fiscal year.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.fact_pay_policy` (
  company_id STRING NOT NULL,
  fiscal_year INT64 NOT NULL,
  pension_type STRING OPTIONS(description="Pension type for executives (defined contribution / benefit) [Protocol ID: C23; CDP alias: new]"),
  benefits STRING OPTIONS(description="Benefits offered to executives (car, insurance, ...) [Protocol ID: C23; CDP alias: new]"),
  shareholding_requirement STRING OPTIONS(description="Required executive shareholding (e.g. 100% of base) [Protocol ID: C23; CDP alias: new]"),
  PRIMARY KEY (company_id, fiscal_year) NOT ENFORCED,
  CONSTRAINT fk_fact_pay_policy_pension_type FOREIGN KEY (pension_type) REFERENCES `your-gcp-project.allshares_cdp.ref_pension_type`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_pay_policy_company_id_fiscal_year FOREIGN KEY (company_id, fiscal_year) REFERENCES `your-gcp-project.allshares_cdp.fact_company_year`(company_id, fiscal_year) NOT ENFORCED
)
OPTIONS(description="Company-level executive pay policy. Grain: one row per company per fiscal year.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.fact_pay_line` (
  pay_line_id STRING NOT NULL,
  company_id STRING NOT NULL,
  fiscal_year INT64,
  role_title STRING OPTIONS(description="Role title as disclosed [Protocol ID: R01; CDP alias: role_title_internal]"),
  role_code STRING OPTIONS(description="Primary standard role (used for benchmarking and in the pay_line_id key); all roles are in pay_line_role"),
  role_disclosure STRING OPTIONS(description="Who is disclosed: individual or aggregate; executive or board [Protocol ID: R01; CDP alias: role_title_internal, is_aggregated]"),
  is_aggregated BOOL OPTIONS(description="The line is a group total, and for how many people [CDP alias: is_aggregated]"),
  aggregate_headcount INT64 OPTIONS(description="People in an aggregate line, and who is excluded [Protocol ID: R02; CDP alias: aggregate_headcount]"),
  aggregate_excludes STRING OPTIONS(description="Who an aggregate line excludes [Protocol ID: R02; CDP alias: aggregate_excludes]"),
  months_in_role INT64 OPTIONS(description="Months the person held the role in the pay year [Rule: 1 to 12]"),
  period_coverage STRING OPTIONS(description="Period the pay line covers"),
  pay_currency STRING OPTIONS(description="Currency and unit of the pay table [Protocol ID: R03; CDP alias: currency_code]"),
  units STRING OPTIONS(description="Unit of the pay table [Protocol ID: R03; CDP alias: currency_code]"),
  base_salary NUMERIC OPTIONS(description="Fixed base salary only (no board fees or benefits) [Protocol ID: R04; CDP alias: comp_base_salary]"),
  token_salary BOOL OPTIONS(description="Base is a token amount"),
  benefits_value NUMERIC OPTIONS(description="Value of benefits for the year [Protocol ID: R09; CDP alias: benefits_value_total]"),
  pension_contribution NUMERIC OPTIONS(description="Pension contribution for the year [Protocol ID: R10; CDP alias: pension_contribution]"),
  sti_paid NUMERIC OPTIONS(description="Short-term incentive (bonus) paid for the year [Protocol ID: R05; CDP alias: comp_sti_actual]"),
  sti_target_value NUMERIC OPTIONS(description="Target STI, in the form stated (% of base, months, amount) [Protocol ID: R06; CDP alias: comp_sti_target]"),
  sti_target_basis STRING OPTIONS(description="What sti_target_value is stated as (% of base, months, amount) [Protocol ID: R06; CDP alias: comp_sti_target]"),
  sti_max_value NUMERIC OPTIONS(description="Maximum STI, in the form stated [Protocol ID: R06; CDP alias: comp_sti_max]"),
  sti_max_basis STRING OPTIONS(description="How max STI is stated (STI basis tab)"),
  lti_vested NUMERIC OPTIONS(description="LTI vested, paid out or exercised in the year [Protocol ID: R07; CDP alias: comp_lti_actual]"),
  lti_granted NUMERIC OPTIONS(description="LTI granted in the year, with its form [Protocol ID: R07; CDP alias: comp_lti_actual]"),
  lti_basis STRING OPTIONS(description="Basis of each LTI value (LTI basis tab)"),
  lti_units INT64 OPTIONS(description="As in the LTI basis tab"),
  lti_face_value NUMERIC OPTIONS(description="As in the LTI basis tab"),
  lti_fair_value NUMERIC OPTIONS(description="As in the LTI basis tab"),
  lti_target_value NUMERIC OPTIONS(description="Target LTI award, in the form stated [Protocol ID: R08; CDP alias: comp_lti_target]"),
  lti_target_basis STRING OPTIONS(description="What lti_target_value is stated as [Protocol ID: R08; CDP alias: comp_lti_target]"),
  lti_max_value NUMERIC OPTIONS(description="Maximum LTI award, in the form stated [Protocol ID: R08; CDP alias: comp_lti_max]"),
  lti_max_basis STRING OPTIONS(description="What lti_max_value is stated as [Protocol ID: R08; CDP alias: comp_lti_max]"),
  performance_period_start DATE OPTIONS(description="Start of the period the STI or LTI is measured on"),
  performance_period_end DATE OPTIONS(description="End of that period"),
  total_remuneration NUMERIC OPTIONS(description="Total remuneration as stated (checked against the parts) [Protocol ID: R11; CDP alias: check value]"),
  PRIMARY KEY (pay_line_id) NOT ENFORCED,
  CONSTRAINT fk_fact_pay_line_role_disclosure FOREIGN KEY (role_disclosure) REFERENCES `your-gcp-project.allshares_cdp.ref_role_disclosure`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_pay_line_period_coverage FOREIGN KEY (period_coverage) REFERENCES `your-gcp-project.allshares_cdp.ref_period_coverage`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_pay_line_pay_currency FOREIGN KEY (pay_currency) REFERENCES `your-gcp-project.allshares_cdp.ref_currency`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_pay_line_units FOREIGN KEY (units) REFERENCES `your-gcp-project.allshares_cdp.ref_units`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_pay_line_sti_max_basis FOREIGN KEY (sti_max_basis) REFERENCES `your-gcp-project.allshares_cdp.ref_sti_max_basis`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_pay_line_lti_basis FOREIGN KEY (lti_basis) REFERENCES `your-gcp-project.allshares_cdp.ref_lti_basis`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_pay_line_company_id_fiscal_year FOREIGN KEY (company_id, fiscal_year) REFERENCES `your-gcp-project.allshares_cdp.fact_company_year`(company_id, fiscal_year) NOT ENFORCED,
  CONSTRAINT fk_fact_pay_line_role_code FOREIGN KEY (role_code) REFERENCES `your-gcp-project.allshares_cdp.ref_role`(code) NOT ENFORCED
)
OPTIONS(description="Executive pay as actually paid (no annualised columns; the CDP annualises per use). Grain: one row per disclosed pay line.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.fact_field_value` (
  value_id STRING NOT NULL,
  company_id STRING NOT NULL,
  fiscal_year INT64,
  pay_line_id STRING,
  field_name STRING NOT NULL,
  item_key STRING OPTIONS(description="Holder or segment name for list fields"),
  value_string STRING,
  value_numeric NUMERIC,
  value_date DATE,
  value_bool BOOL,
  currency STRING,
  units STRING,
  source_id STRING,
  locator STRING OPTIONS(description="Where in the source (page, table, cell)"),
  snippet STRING OPTIONS(description="Verbatim source text"),
  quote_match STRING OPTIONS(description="Result of the quote check"),
  as_of_date DATE,
  period_start DATE,
  period_end DATE,
  source_type STRING,
  formula_version STRING,
  extraction_run_id STRING,
  extracted_at TIMESTAMP,
  PRIMARY KEY (value_id) NOT ENFORCED,
  CONSTRAINT fk_fact_field_value_company_id FOREIGN KEY (company_id) REFERENCES `your-gcp-project.allshares_cdp.dim_company`(company_id) NOT ENFORCED,
  CONSTRAINT fk_fact_field_value_pay_line_id FOREIGN KEY (pay_line_id) REFERENCES `your-gcp-project.allshares_cdp.fact_pay_line`(pay_line_id) NOT ENFORCED,
  CONSTRAINT fk_fact_field_value_field_name FOREIGN KEY (field_name) REFERENCES `your-gcp-project.allshares_cdp.dim_field`(field_name) NOT ENFORCED,
  CONSTRAINT fk_fact_field_value_currency FOREIGN KEY (currency) REFERENCES `your-gcp-project.allshares_cdp.ref_currency`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_field_value_units FOREIGN KEY (units) REFERENCES `your-gcp-project.allshares_cdp.ref_units`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_field_value_source_id FOREIGN KEY (source_id) REFERENCES `your-gcp-project.allshares_cdp.dim_source`(source_id) NOT ENFORCED,
  CONSTRAINT fk_fact_field_value_quote_match FOREIGN KEY (quote_match) REFERENCES `your-gcp-project.allshares_cdp.ref_quote_match`(code) NOT ENFORCED,
  CONSTRAINT fk_fact_field_value_source_type FOREIGN KEY (source_type) REFERENCES `your-gcp-project.allshares_cdp.ref_source_type`(code) NOT ENFORCED
)
PARTITION BY DATE(extracted_at)
CLUSTER BY company_id, field_name
OPTIONS(description="Every extracted value with its provenance. Record, do not correct. Grain: one row per entity x field x period (x list item).");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.fact_check_result` (
  result_id STRING NOT NULL,
  value_id STRING,
  check_code STRING,
  company_id STRING OPTIONS(description="Copied from the value, for clustering"),
  field_name STRING OPTIONS(description="Copied from the value, for clustering"),
  result STRING,
  score NUMERIC,
  note STRING OPTIONS(description="LB-2: why a confirmed Fail is correct in the document"),
  incomplete_reason STRING OPTIONS(description="LB-5: why the value is Incomplete"),
  review_decision STRING OPTIONS(description="LB-4: the D&A team's decision on a Review"),
  reviewed_by STRING,
  reviewed_at TIMESTAMP,
  checked_at TIMESTAMP,
  PRIMARY KEY (result_id) NOT ENFORCED,
  CONSTRAINT fk_fact_check_result_value_id FOREIGN KEY (value_id) REFERENCES `your-gcp-project.allshares_cdp.fact_field_value`(value_id) NOT ENFORCED,
  CONSTRAINT fk_fact_check_result_check_code FOREIGN KEY (check_code) REFERENCES `your-gcp-project.allshares_cdp.dim_check`(check_code) NOT ENFORCED,
  CONSTRAINT fk_fact_check_result_result FOREIGN KEY (result) REFERENCES `your-gcp-project.allshares_cdp.ref_check_result`(code) NOT ENFORCED
)
PARTITION BY DATE(checked_at)
CLUSTER BY company_id, field_name
OPTIONS(description="Check results, recorded beside the source value (never overwriting it). Grain: one row per value per check run.");

-- Children and bridges

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.company_name_alias` (
  company_id STRING NOT NULL,
  alias STRING NOT NULL OPTIONS(description="Former or other names [Protocol ID: C01; CDP alias: aliases]"),
  PRIMARY KEY (company_id, alias) NOT ENFORCED,
  CONSTRAINT fk_company_name_alias_company_id FOREIGN KEY (company_id) REFERENCES `your-gcp-project.allshares_cdp.dim_company`(company_id) NOT ENFORCED
)
OPTIONS(description="Former and other names (other_names). Grain: one row per company per alias.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.company_holder` (
  company_id STRING NOT NULL,
  fiscal_year INT64 NOT NULL,
  holder_rank INT64 NOT NULL OPTIONS(description="Rank of the holder in the list (1 = largest)"),
  holder_name STRING OPTIONS(description="Holder name as written in the source [Protocol ID: C19; CDP alias: ownership_detail]"),
  holder_type STRING OPTIONS(description="Type of holder (family, private equity, state, institution, ...) [Protocol ID: C20; CDP alias: has_pe_stake]"),
  capital_pct NUMERIC OPTIONS(description="% of share capital held [Protocol ID: C19; CDP alias: ownership_detail]"),
  votes_pct NUMERIC OPTIONS(description="% of votes held [Protocol ID: C19; CDP alias: ownership_detail]"),
  holder_group STRING OPTIONS(description="Group the holder is consolidated into before ranking (DER-08)"),
  is_tied BOOL OPTIONS(description="Holder ties with another rank (DER-09: ties listed explicitly)"),
  as_of_date DATE OPTIONS(description="As-of date of the shareholder list (DER-07: same for every holder)"),
  share_count_basis STRING OPTIONS(description="Basis of the percentages, e.g. shares outstanding or issued (DER-07)"),
  list_cutoff STRING OPTIONS(description="How the list was cut off (e.g. top 10, all above 5%)"),
  PRIMARY KEY (company_id, fiscal_year, holder_rank) NOT ENFORCED,
  CONSTRAINT fk_company_holder_company_id_fiscal_year FOREIGN KEY (company_id, fiscal_year) REFERENCES `your-gcp-project.allshares_cdp.fact_company_year`(company_id, fiscal_year) NOT ENFORCED,
  CONSTRAINT fk_company_holder_holder_type FOREIGN KEY (holder_type) REFERENCES `your-gcp-project.allshares_cdp.ref_ownership_type`(code) NOT ENFORCED,
  CONSTRAINT fk_company_holder_share_count_basis FOREIGN KEY (share_count_basis) REFERENCES `your-gcp-project.allshares_cdp.ref_share_count_basis`(code) NOT ENFORCED,
  CONSTRAINT fk_company_holder_list_cutoff FOREIGN KEY (list_cutoff) REFERENCES `your-gcp-project.allshares_cdp.ref_holder_list_cutoff`(code) NOT ENFORCED
)
OPTIONS(description="Largest shareholders with their holdings. Controlling owner, ownership type and PE stake are calculated from this table (v_company_ownership). Grain: one row per holder per company per fiscal year.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.company_breakdown` (
  company_id STRING NOT NULL,
  fiscal_year INT64 NOT NULL,
  breakdown_type STRING NOT NULL OPTIONS(description="segment or country"),
  metric STRING NOT NULL OPTIONS(description="revenue or staff"),
  item_name STRING NOT NULL OPTIONS(description="Segment or country name"),
  value NUMERIC,
  PRIMARY KEY (company_id, fiscal_year, breakdown_type, metric, item_name) NOT ENFORCED,
  CONSTRAINT fk_company_breakdown_company_id_fiscal_year FOREIGN KEY (company_id, fiscal_year) REFERENCES `your-gcp-project.allshares_cdp.fact_company_year`(company_id, fiscal_year) NOT ENFORCED
)
OPTIONS(description="Revenue and staff split by segment or country. Grain: one row per company, fiscal year, breakdown, metric and item.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.pay_line_total_component` (
  pay_line_id STRING NOT NULL,
  component_field STRING NOT NULL OPTIONS(description="Pay field included in the total"),
  PRIMARY KEY (pay_line_id, component_field) NOT ENFORCED,
  CONSTRAINT fk_pay_line_total_component_pay_line_id FOREIGN KEY (pay_line_id) REFERENCES `your-gcp-project.allshares_cdp.fact_pay_line`(pay_line_id) NOT ENFORCED
)
OPTIONS(description="Which components the document's total includes (total_components). Grain: one row per pay line per component in its stated total.");

CREATE TABLE IF NOT EXISTS `your-gcp-project.allshares_cdp.pay_line_role` (
  pay_line_id STRING NOT NULL,
  role_code STRING NOT NULL OPTIONS(description="Standard role covered by the pay line"),
  is_primary BOOL OPTIONS(description="The role used for benchmarking (same as fact_pay_line.role_code)"),
  role_order INT64 OPTIONS(description="Order of the role in the disclosed title"),
  source_title STRING OPTIONS(description="Wording for this role in the source, e.g. 'CFO' in 'CEO and CFO'"),
  start_date DATE OPTIONS(description="When the role started, if the report says (part-year roles)"),
  end_date DATE OPTIONS(description="When the role ended, if the report says (part-year roles)"),
  PRIMARY KEY (pay_line_id, role_code) NOT ENFORCED,
  CONSTRAINT fk_pay_line_role_pay_line_id FOREIGN KEY (pay_line_id) REFERENCES `your-gcp-project.allshares_cdp.fact_pay_line`(pay_line_id) NOT ENFORCED,
  CONSTRAINT fk_pay_line_role_role_code FOREIGN KEY (role_code) REFERENCES `your-gcp-project.allshares_cdp.ref_role`(code) NOT ENFORCED
)
OPTIONS(description="Every role a pay line covers, e.g. \"CEO and CFO\" gives two rows. One row is primary and matches fact_pay_line.role_code. Grain: one row per pay line per role it covers.");

-- Derived views

CREATE OR REPLACE VIEW `your-gcp-project.allshares_cdp.v_company_ownership` (
  company_id,
  fiscal_year,
  holder_count OPTIONS(description="Number of holders listed [Derived: COUNT(*)]"),
  controlling_owner OPTIONS(description="A holder has 20% or more of the votes [Protocol ID: C20; CDP alias: controlling_owner; Derived: LOGICAL_OR(votes_pct >= 20)]"),
  controlling_owner_name OPTIONS(description="Largest holder with 20% or more of the votes [Protocol ID: C20; CDP alias: controlling_owner; Derived: ARRAY_AGG(IF(votes_pct >= 20, holder_name, NULL) IGNORE NULLS ORDER BY votes_pct DESC LIMIT 1)[SAFE_OFFSET(0)]]"),
  ownership_type OPTIONS(description="Type of the controlling owner [Protocol ID: C20; CDP alias: has_pe_stake; Derived: ARRAY_AGG(IF(votes_pct >= 20, holder_type, NULL) IGNORE NULLS ORDER BY votes_pct DESC LIMIT 1)[SAFE_OFFSET(0)]]"),
  pe_stake_5pct OPTIONS(description="A private equity holder has 5% or more of the capital [Protocol ID: C20; CDP alias: has_pe_stake; Derived: LOGICAL_OR(holder_type = 'private_equity' AND capital_pct >= 5)]"),
  ownership_as_of OPTIONS(description="As-of date of the list [Derived: MAX(as_of_date)]"),
  as_of_consistent OPTIONS(description="All holdings share one as-of date (DER-07) [Derived: COUNT(DISTINCT as_of_date) <= 1]"),
  capital_listed_pct OPTIONS(description="Capital held by the listed holders (NUM-07: at most 100) [Derived: SUM(capital_pct)]"),
  votes_listed_pct OPTIONS(description="Votes held by the listed holders (NUM-07: at most 100) [Derived: SUM(votes_pct)]")
)
OPTIONS(description="Ownership and control per company and fiscal year, calculated from company_holder")
AS
SELECT
  company_id,
  fiscal_year,
  COUNT(*) AS holder_count,
  LOGICAL_OR(votes_pct >= 20) AS controlling_owner,
  ARRAY_AGG(IF(votes_pct >= 20, holder_name, NULL) IGNORE NULLS ORDER BY votes_pct DESC LIMIT 1)[SAFE_OFFSET(0)] AS controlling_owner_name,
  ARRAY_AGG(IF(votes_pct >= 20, holder_type, NULL) IGNORE NULLS ORDER BY votes_pct DESC LIMIT 1)[SAFE_OFFSET(0)] AS ownership_type,
  LOGICAL_OR(holder_type = 'private_equity' AND capital_pct >= 5) AS pe_stake_5pct,
  MAX(as_of_date) AS ownership_as_of,
  COUNT(DISTINCT as_of_date) <= 1 AS as_of_consistent,
  SUM(capital_pct) AS capital_listed_pct,
  SUM(votes_pct) AS votes_listed_pct
FROM `your-gcp-project.allshares_cdp.company_holder`
GROUP BY company_id, fiscal_year;

-- Seed data

-- ref_country: no seed rows

-- ref_country_currency: no seed rows

-- ref_currency: no seed rows

-- ref_exchange: no seed rows

-- ref_exchange_segment: no seed rows

-- ref_listing_status: no seed rows

-- ref_accounting_basis: no seed rows

-- ref_ownership_type: no seed rows

-- ref_market_cap_band: no seed rows

-- ref_role_disclosure: no seed rows

-- ref_pension_type: no seed rows

-- ref_period_coverage: no seed rows

-- ref_holder_list_cutoff: no seed rows

-- ref_share_count_basis: no seed rows

-- ref_pct_of: no seed rows

-- ref_units: no seed rows

-- ref_source_type: no seed rows

INSERT INTO `your-gcp-project.allshares_cdp.ref_lti_basis` (code, label, meaning, status, list_source) VALUES
  ('realised', 'realised', 'Value vested, released or exercised in the year; realised gain', 'Proposed', 'Conor 02 Nov: LTI basis'),
  ('award_pct', 'award_pct', 'Award as % of base salary; target or maximum award level', 'Proposed', 'Conor 02 Nov: LTI basis'),
  ('face', 'face', 'Number of shares or units granted, with the share price at grant', 'Proposed', 'Conor 02 Nov: LTI basis'),
  ('fair_value', 'fair_value', 'Grant-date fair value (e.g. US Summary Compensation Table \'Stock awards\' or \'Option awards\')', 'Proposed', 'Conor 02 Nov: LTI basis'),
  ('units_only', 'units only', 'Number of options granted', 'Proposed', 'Conor 02 Nov: LTI basis'),
  ('accounting_expense', 'accounting_expense', 'Accounting expense or share-based payment charge (IFRS 2, ASC 718)', 'Proposed', 'Conor 02 Nov: LTI basis');

INSERT INTO `your-gcp-project.allshares_cdp.ref_sti_max_basis` (code, label, meaning, status, list_source) VALUES
  ('base_salary', 'base_salary', '% of base salary', 'Proposed', 'Conor 02 Nov: STI basis'),
  ('target_bonus', 'target_bonus', 'Multiple or % of target bonus (common in US filings)', 'Proposed', 'Conor 02 Nov: STI basis'),
  ('amount', 'amount', 'Fixed amount', 'Proposed', 'Conor 02 Nov: STI basis'),
  ('unknown', 'unknown', 'Not stated', 'Proposed', 'Conor 02 Nov: STI basis');

INSERT INTO `your-gcp-project.allshares_cdp.ref_quote_match` (code, label, meaning, status, list_source) VALUES
  ('exact', 'exact', 'no step needed', 'Proposed', 'Conor 02 Nov: Possible tracker fields / Quote matching'),
  ('normalised', 'normalised', 'steps 1-3 needed', 'Proposed', 'Conor 02 Nov: Possible tracker fields / Quote matching'),
  ('none', 'none', NULL, 'Proposed', 'Conor 02 Nov: Possible tracker fields / Quote matching');

INSERT INTO `your-gcp-project.allshares_cdp.ref_check_result` (code, label, meaning, status, list_source) VALUES
  ('pass', 'Pass', 'The check passed', 'In use', 'Schema playground brief §5b'),
  ('fail', 'Fail', 'The check failed', 'In use', 'Schema playground brief §5b'),
  ('review', 'Review', 'A person must review the value', 'In use', 'Schema playground brief §5b'),
  ('incomplete', 'Incomplete', 'The document does not state the inputs; reason recorded', 'In use', 'Schema playground brief §5b'),
  ('not_run', 'Not run', 'The check was not run (e.g. NUM-04 until ranges are approved)', 'In use', 'Schema playground brief §5b');

INSERT INTO `your-gcp-project.allshares_cdp.ref_role` (code, label, meaning, status, list_source, role_group, is_ceo, sort_order, source_titles) VALUES
  ('ceo', 'CEO', 'Chief executive / managing director', 'Proposed: confirm with Allshares', 'Schema playground proposal, 10 Nov (to agree with Allshares)', 'executive', TRUE, 1, 'CEO; President and CEO; VD; Verkställande direktör; Toimitusjohtaja; Administrerende direktør'),
  ('deputy_ceo', 'Deputy CEO', 'Deputy or vice CEO', 'Proposed: confirm with Allshares', 'Schema playground proposal, 10 Nov (to agree with Allshares)', 'executive', FALSE, 2, 'Deputy CEO; Vice VD; Varatoimitusjohtaja'),
  ('cfo', 'CFO', 'Chief financial officer', 'Proposed: confirm with Allshares', 'Schema playground proposal, 10 Nov (to agree with Allshares)', 'executive', FALSE, 3, 'CFO; Finance Director; Ekonomidirektör; Talousjohtaja'),
  ('coo', 'COO', 'Chief operating officer', 'Proposed: confirm with Allshares', 'Schema playground proposal, 10 Nov (to agree with Allshares)', 'executive', FALSE, 4, 'COO'),
  ('other_executive', 'Other executive', 'Other named executive (individual line)', 'Proposed: confirm with Allshares', 'Schema playground proposal, 10 Nov (to agree with Allshares)', 'executive', FALSE, 5, NULL),
  ('executive_team_aggregate', 'Executive team (aggregate)', 'Other group management reported as one total', 'Proposed: confirm with Allshares', 'Schema playground proposal, 10 Nov (to agree with Allshares)', 'executive', FALSE, 6, 'Other members of group management; Övriga ledande befattningshavare; Muu johtoryhmä'),
  ('board_chair', 'Board chair', 'Chair of the board', 'Proposed: confirm with Allshares', 'Schema playground proposal, 10 Nov (to agree with Allshares)', 'board', FALSE, 7, 'Chair; Chairman; Styrelseordförande; Hallituksen puheenjohtaja'),
  ('board_vice_chair', 'Board vice chair', 'Vice chair of the board', 'Proposed: confirm with Allshares', 'Schema playground proposal, 10 Nov (to agree with Allshares)', 'board', FALSE, 8, NULL),
  ('board_member', 'Board member', 'Non-executive board member', 'Proposed: confirm with Allshares', 'Schema playground proposal, 10 Nov (to agree with Allshares)', 'board', FALSE, 9, 'Board member; Styrelseledamot; Hallituksen jäsen'),
  ('employee_representative', 'Employee representative', 'Employee-elected board member', 'Proposed: confirm with Allshares', 'Schema playground proposal, 10 Nov (to agree with Allshares)', 'board', FALSE, 10, NULL),
  ('board_aggregate', 'Board (aggregate)', 'Board fees reported as one total', 'Proposed: confirm with Allshares', 'Schema playground proposal, 10 Nov (to agree with Allshares)', 'board', FALSE, 11, NULL);

INSERT INTO `your-gcp-project.allshares_cdp.dim_field` (field_name, protocol_id, cdp_column, module, data_category, grain, field_type, format, description, read_from, method, priority, requirement, severity, fill_of_50, note, status) VALUES
  ('legal_name', 'C01', 'company_name, aliases', 'Reference data', 'Identity', 'Company', 'direct', 'Text', 'Registered legal name', 'GLEIF; annual report; legal notice', 'API / Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('other_names', 'C01', 'aliases', 'Reference data', 'Identity', 'Company', 'direct', 'Text', 'Former or other names', 'Annual report; history page', 'Parse / Scrape', 'P4', 'Optional', 'Low', 30, NULL, 'active'),
  ('lei', 'C02', 'lei', 'Reference data', 'Identity', 'Company', 'direct', 'Code', 'Legal Entity Identifier (20 characters, ISO 17442)', 'GLEIF', 'API', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('business_id', 'C03', 'ref_company_identifiers', 'Reference data', 'Identity', 'Company', 'direct', 'Code', 'National registration number', 'Annual report; legal notice (Impressum); GLEIF registeredAs', 'Parse / API', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('cik', 'Not in protocol', NULL, 'Reference data', 'Identity', 'Company', 'direct', 'Code', 'SEC Central Index Key (US registrants only; not in the protocol)', 'SEC EDGAR', 'API', NULL, NULL, NULL, NULL, 'no protocol field ID (cik is outside C01-C23)', 'active'),
  ('country_code', 'C08', 'country_code', 'Reference data', 'Identity', 'Company', 'direct', 'Code', 'Country of incorporation (ISO 3166)', 'GLEIF; annual report', 'API / Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('head_office_city', 'C08', 'hq_city', 'Reference data', 'Identity', 'Company', 'direct', 'Text', 'Head office city', 'GLEIF; annual report; legal notice', 'API / Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('website', 'C09', 'new', 'Reference data', 'Identity', 'Company', 'direct', 'Text', 'Company website domain', 'Annual report; legal notice; about page', 'Parse / Scrape', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('isin', 'C04', 'isin', 'Reference data', 'Listing and market', 'Company', 'direct', 'Code', 'ISIN of the main share line', 'ESMA FIRDS by LEI; OpenFIGI (UK/CH); annual report', 'API / Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('ticker', 'C05', 'ticker_primary', 'Reference data', 'Listing and market', 'Company', 'direct', 'Code', 'Trading symbol on the primary exchange', 'OpenFIGI; annual report; share page', 'API / Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('exchange', 'C05', 'exchange_primary', 'Reference data', 'Listing and market', 'Company', 'direct', 'Code', 'Primary exchange (ISO 10383 MIC)', 'ESMA FIRDS venue + ISO MIC list', 'API', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('exchange_segment', 'C06', 'exchange_segment', 'Reference data', 'Listing and market', 'Company', 'direct', 'Code', 'Market segment (e.g. Large Cap, MTF)', 'Annual report; share page', 'Parse / Scrape', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('listing_status', 'C07', 'listing_status', 'Reference data', 'Listing and market', 'Company', 'direct', 'Code', 'Listed, delisted or suspended', 'ESMA FIRDS', 'API', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('listing_date', 'C07', 'listed_date', 'Reference data', 'Listing and market', 'Company', 'direct', 'Date', 'Date first admitted to trading', 'Annual report; listing notice; share page; FIRDS (C-graded fallback)', 'Parse / API', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('share_price', 'C18', 'for market cap band', 'Reference data', 'Listing and market', 'Company', 'direct', 'Money', 'Year-end share price', 'Annual report share section; share page', 'Parse / Scrape', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('market_cap_band', 'Derived: C17 x C18', 'for market cap band', 'Reference data', 'Listing and market', 'Company', 'derived', 'Text', 'Market cap band: large >= EUR 1bn, mid >= EUR 150m, else small', 'Derived: shares_outstanding x share_price', 'Derived', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('sector_code', 'C10', 'sector_primary', 'Reference data', 'Sector', 'Company', 'direct', 'Code', 'National industry code (e.g. SIC, NACE)', 'Registers: NO, FI, UK; SEC SIC for US registrants', 'API', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('sub_sector', 'C11', 'sub_sector', 'Reference data', 'Sector', 'Company', 'direct', 'Text', 'One-sentence business description', 'Annual report', 'Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('fiscal_year', 'C15', 'fiscal_year', 'Reference data', 'Reporting basis', 'Company', 'direct', 'Number', 'Fiscal year the data covers', 'Pipeline result; annual report', 'Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('fiscal_year_end', 'C15', 'fiscal_year', 'Reference data', 'Reporting basis', 'Company', 'direct', 'Date', 'Fiscal year end date', 'Annual report', 'Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('reporting_currency', 'C15', 'currency', 'Reference data', 'Reporting basis', 'Company', 'direct', 'Text', 'Currency of the financial statements (ISO 4217)', 'Annual report; XBRL', 'Parse / XBRL', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('accounting_basis', 'C15', 'accounting basis', 'Reference data', 'Reporting basis', 'Company', 'direct', 'Text', 'Accounting standard (IFRS, US GAAP, local GAAP)', 'Annual report', 'Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('revenue', 'C12', 'ref_company_financials', 'Company and ownership', 'Financials', 'Company', 'direct', 'Money', 'Revenue for the fiscal year', 'XBRL tag or annual report', 'XBRL / Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('total_assets', 'C13', 'ref_company_financials', 'Company and ownership', 'Financials', 'Company', 'direct', 'Money', 'Total assets at year end', 'XBRL tag or annual report', 'XBRL / Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('ebitda', 'C14', 'ref_company_financials', 'Company and ownership', 'Financials', 'Company', 'direct', 'Money', 'EBITDA, else operating profit (note says which)', 'Annual report key figures; year-end report', 'Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('shares_outstanding', 'C17', 'for market cap band', 'Company and ownership', 'Financials', 'Company', 'direct', 'Number', 'Shares outstanding (not issued)', 'Annual report; share page', 'Parse / Scrape', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('headcount', 'C16', 'headcount', 'Company and ownership', 'Workforce', 'Company', 'direct', 'Number', 'Number of employees', 'Annual report; sustainability report', 'Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('fte', 'C16', 'fte', 'Company and ownership', 'Workforce', 'Company', 'direct', 'Number', 'Full-time equivalents', 'Annual report; sustainability report', 'Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('largest_holders', 'C19', 'ownership_detail', 'Company and ownership', 'Ownership and control', 'Company', 'direct', 'List (name: value)', 'Largest shareholders with % of capital and votes', 'Annual report shareholder table; shareholder page', 'Parse / Scrape', 'P2*', 'Optional', 'Medium', 46, NULL, 'active'),
  ('controlling_owner', 'C20', 'controlling_owner', 'Company and ownership', 'Ownership and control', 'Company', 'direct', 'Text', 'Is there a holder with 20%+ of votes (yes/no)', 'Derived from largest_holders', 'Derived', 'P2', 'Required', 'Medium', 43, NULL, 'active'),
  ('controlling_owner_name', 'C20', 'controlling_owner', 'Company and ownership', 'Ownership and control', 'Company', 'direct', 'Text', 'Name of the controlling owner', 'Derived from largest_holders', 'Derived', 'P4', 'Optional', 'Low', 27, NULL, 'active'),
  ('ownership_type', 'C20', 'has_pe_stake', 'Company and ownership', 'Ownership and control', 'Company', 'direct', 'Text', 'Type of controlling owner (family, PE, state, ...)', 'Derived from largest_holders', 'Derived', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('pe_stake_5pct', 'C20', 'has_pe_stake', 'Company and ownership', 'Ownership and control', 'Company', 'direct', 'Text', 'Private equity holder with 5%+ (yes/no)', 'Derived from largest_holders', 'Derived', 'P3', 'Optional', 'Medium', 43, NULL, 'active'),
  ('ultimate_parent', 'C21', 'new', 'Company and ownership', 'Ownership and control', 'Company', 'direct', 'Text', 'Ultimate parent company, if any', 'GLEIF; annual report; shareholder page', 'API / Parse', NULL, NULL, NULL, NULL, NULL, 'active'),
  ('revenue_by_segment', 'C22', 'new', 'Company and ownership', 'Segment and geography', 'Company', 'direct', 'List (name: value)', 'Revenue split by operating segment', 'Segment note (IFRS 8); year-end report', 'Parse', 'P4', 'Optional', 'Low', 20, NULL, 'active'),
  ('staff_by_segment', 'C22', 'new', 'Company and ownership', 'Segment and geography', 'Company', 'direct', 'List (name: value)', 'Employees split by segment', 'Annual report; sustainability report', 'Parse', 'Skip', 'Optional', 'Never used', 8, NULL, 'active'),
  ('revenue_by_country', 'C22', 'new', 'Company and ownership', 'Segment and geography', 'Company', 'direct', 'List (name: value)', 'Revenue split by country or region', 'Segment note (IFRS 8)', 'Parse', 'P4', 'Optional', 'Low', 17, NULL, 'active'),
  ('staff_by_country', 'C22', 'new', 'Company and ownership', 'Segment and geography', 'Company', 'direct', 'List (name: value)', 'Employees split by country', 'Annual report; sustainability report', 'Parse', 'P4', 'Optional', 'Low', 23, NULL, 'active'),
  ('pension_type', 'C23', 'new', 'Pay and role', 'Pay policy', 'Company', 'direct', 'Text', 'Pension type for executives (defined contribution / benefit)', 'Remuneration policy, then report', 'Parse', NULL, NULL, NULL, NULL, 'Company-level pay policy (one value per company)', 'active'),
  ('benefits', 'C23', 'new', 'Pay and role', 'Pay policy', 'Company', 'direct', 'Text', 'Benefits offered to executives (car, insurance, ...)', 'Remuneration policy, then report', 'Parse', NULL, NULL, NULL, NULL, 'Company-level pay policy (one value per company)', 'active'),
  ('shareholding_requirement', 'C23', 'new', 'Pay and role', 'Pay policy', 'Company', 'direct', 'Text', 'Required executive shareholding (e.g. 100% of base)', 'Remuneration policy, then report', 'Parse', NULL, NULL, NULL, NULL, 'Company-level pay policy (one value per company)', 'active'),
  ('role_disclosure', 'R01', 'role_title_internal, is_aggregated', 'Pay and role', 'Role and disclosure', 'Role', 'direct', 'Text', 'Who is disclosed: individual or aggregate; executive or board', 'Remuneration report', 'Parse', 'P1', 'Required', 'High', 46, 'One value per disclosed executive role', 'active'),
  ('aggregate_headcount', 'R02', 'aggregate_headcount, aggregate_excludes', 'Pay and role', 'Role and disclosure', 'Role', 'direct', 'Number', 'People in an aggregate line, and who is excluded', 'Remuneration report', 'Parse', 'P2', 'Required if aggregate line', 'Medium', 27, 'One value per disclosed executive role', 'active'),
  ('pay_currency', 'R03', 'currency_code', 'Pay and role', 'Pay: fixed', 'Role', 'direct', 'Text', 'Currency and unit of the pay table', 'Remuneration report', 'Parse', 'P1', 'Required', 'High', 46, 'One value per disclosed executive role', 'active'),
  ('base_salary', 'R04', 'comp_base_salary', 'Pay and role', 'Pay: fixed', 'Role', 'direct', 'Money', 'Fixed base salary only (no board fees or benefits)', 'Remuneration report pay table', 'Parse / table read', 'P1', 'Required', 'High', 41, 'One value per disclosed executive role', 'active'),
  ('benefits_value', 'R09', 'benefits_value_total', 'Pay and role', 'Pay: fixed', 'Role', 'direct', 'Money', 'Value of benefits for the year', 'Remuneration report pay table', 'Parse / table read', 'P2', 'Required', 'Medium', 37, 'One value per disclosed executive role', 'active'),
  ('pension_contribution', 'R10', 'pension_contribution', 'Pay and role', 'Pay: fixed', 'Role', 'direct', 'Money', 'Pension contribution for the year', 'Remuneration report pay table', 'Parse / table read', 'P2', 'Required', 'Medium', 40, 'One value per disclosed executive role', 'active'),
  ('sti_paid', 'R05', 'comp_sti_actual', 'Pay and role', 'Pay: STI', 'Role', 'direct', 'Money', 'Short-term incentive (bonus) paid for the year', 'Remuneration report pay table', 'Parse / table read', NULL, NULL, NULL, NULL, 'One value per disclosed executive role', 'active'),
  ('sti_target', 'R06', 'comp_sti_target', 'Pay and role', 'Pay: STI', 'Role', 'direct', 'Number or %', 'Target STI, in the form stated (% of base, months, amount)', 'Remuneration report / policy', 'Parse', NULL, NULL, NULL, NULL, 'One value per disclosed executive role', 'active'),
  ('sti_max', 'R06', 'comp_sti_max', 'Pay and role', 'Pay: STI', 'Role', 'direct', 'Number or %', 'Maximum STI, in the form stated', 'Remuneration report / policy', 'Parse', NULL, NULL, NULL, NULL, 'One value per disclosed executive role', 'active'),
  ('lti_vested', 'R07', 'comp_lti_actual', 'Pay and role', 'Pay: LTI', 'Role', 'direct', 'Money', 'LTI vested, paid out or exercised in the year', 'Remuneration report pay table', 'Parse / table read', NULL, NULL, NULL, NULL, 'One value per disclosed executive role', 'active'),
  ('lti_granted', 'R07', 'comp_lti_actual', 'Pay and role', 'Pay: LTI', 'Role', 'direct', 'Money', 'LTI granted in the year, with its form', 'Remuneration report', 'Parse / table read', NULL, NULL, NULL, NULL, 'One value per disclosed executive role', 'active'),
  ('lti_target', 'R08', 'comp_lti_target', 'Pay and role', 'Pay: LTI', 'Role', 'direct', 'Number or %', 'Target LTI award, in the form stated', 'Remuneration report / policy', 'Parse', NULL, NULL, NULL, NULL, 'One value per disclosed executive role', 'active'),
  ('lti_max', 'R08', 'comp_lti_max', 'Pay and role', 'Pay: LTI', 'Role', 'direct', 'Number or %', 'Maximum LTI award, in the form stated', 'Remuneration report / policy', 'Parse', NULL, NULL, NULL, NULL, 'One value per disclosed executive role', 'active'),
  ('total_remuneration', 'R11', 'check value', 'Pay and role', 'Pay: total', 'Role', 'direct', 'Money', 'Total remuneration as stated (checked against the parts)', 'Remuneration report pay table', 'Parse / table read', 'P1', 'Required', 'High', 40, 'One value per disclosed executive role', 'active'),
  ('months_in_role', NULL, NULL, 'Pay and role', NULL, 'Role', NULL, 'Number', 'Months the person held the role in the pay year', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: Integer 1-12. Unblocks: PAY-3, PAY-6; annualisation', 'new'),
  ('performance_period_start', NULL, NULL, 'Pay and role', NULL, 'Role', NULL, 'Date', 'Start of the period the STI or LTI is measured on', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: Date. Unblocks: Performance-period gates', 'new'),
  ('performance_period_end', NULL, NULL, 'Pay and role', NULL, 'Role', NULL, 'Date', 'End of that period', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: Date. Unblocks: Performance-period gates', 'new'),
  ('lti_basis', NULL, NULL, 'Pay and role', NULL, 'Role', NULL, 'Code', 'Basis of each LTI value (LTI basis tab)', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: One of: realised, award_pct, face, fair_value, accounting_expense. Unblocks: LTI-2', 'new'),
  ('lti_units', NULL, NULL, 'Pay and role', NULL, 'Role', NULL, 'Number', 'As in the LTI basis tab', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: Number / amount / amount. Unblocks: LTI-2', 'new'),
  ('lti_face_value', NULL, NULL, 'Pay and role', NULL, 'Role', NULL, 'Money', 'As in the LTI basis tab', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: Number / amount / amount. Unblocks: LTI-2', 'new'),
  ('lti_fair_value', NULL, NULL, 'Pay and role', NULL, 'Role', NULL, 'Money', 'As in the LTI basis tab', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: Number / amount / amount. Unblocks: LTI-2', 'new'),
  ('sti_max_basis', NULL, NULL, 'Pay and role', NULL, 'Role', NULL, 'Code', 'How max STI is stated (STI basis tab)', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: One of: base_salary, target_bonus, amount, unknown. Unblocks: STI-1', 'new'),
  ('total_components', NULL, NULL, 'Pay and role', NULL, 'Role', NULL, 'List (name: value)', 'Which components the document\'s total includes', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: List. Unblocks: PAY-1', 'new'),
  ('token_salary', NULL, NULL, 'Pay and role', NULL, 'Role', NULL, 'yes/no text', 'Base is a token amount', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: Boolean. Unblocks: PAY-4', 'new'),
  ('is_aggregated', NULL, NULL, 'Pay and role', NULL, 'Role', NULL, 'yes/no text', 'The line is a group total, and for how many people', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: Boolean / integer. Unblocks: PAY-5', 'new'),
  ('ownership_as_of', NULL, NULL, 'Company and ownership', NULL, 'Company', NULL, 'Date', 'As-of date of the ownership list', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: Date. Unblocks: OWN-1', 'new'),
  ('quote_match', NULL, NULL, NULL, NULL, 'Value', NULL, 'Code', 'Result of the quote check', NULL, NULL, NULL, NULL, NULL, NULL, 'Type: One of: exact, normalised, none. Unblocks: SRC-1', 'new'),
  ('year_of_birth', NULL, NULL, 'Pay and role', 'Role and disclosure', 'Role', NULL, 'Year', 'Year of birth of the person in the role', NULL, NULL, NULL, NULL, NULL, NULL, 'Conor 02 Nov: add or park (needed for AGE-1)', 'parked'),
  ('role_start_year', NULL, NULL, 'Pay and role', 'Role and disclosure', 'Role', NULL, 'Year', 'Year the person started in the current role', NULL, NULL, NULL, NULL, NULL, NULL, 'Conor 02 Nov: add or park (needed for AGE-2)', 'parked'),
  ('year_joined', NULL, NULL, 'Pay and role', 'Role and disclosure', 'Role', NULL, 'Year', 'Year the person joined the company', NULL, NULL, NULL, NULL, NULL, NULL, 'Conor 02 Nov: add or park (needed for AGE-3)', 'parked'),
  ('role_code', NULL, NULL, 'Pay and role', 'Role and disclosure', 'Role', NULL, 'Code', 'Standard role of the pay line; the primary role when one line covers several roles', NULL, NULL, NULL, NULL, NULL, NULL, 'Added 10 Nov; list in ref_role, to agree with Allshares before Tier 2', 'new');

INSERT INTO `your-gcp-project.allshares_cdp.dim_check` (check_code, check_name, check_fx, check_type, applies_to_categories, parent_gate, status, remarks) VALUES
  ('CORE-01', 'Locator and verbatim snippet present', 'direct', 'hard', 'Identity, Listing and market, Sector, Reporting basis, Financials, Workforce, Ownership and control, Segment and geography, Pay policy, Role and disclosure, Pay: fixed, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('CORE-02', 'Snippet re-parses to the same value', 'direct', 'hard', 'Identity, Listing and market, Sector, Reporting basis, Financials, Workforce, Ownership and control, Segment and geography, Pay policy, Role and disclosure, Pay: fixed, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('CORE-03', 'Source ID exists and is registered', 'direct', 'soft', 'Identity, Listing and market, Sector, Reporting basis, Financials, Workforce, Ownership and control, Segment and geography, Pay policy, Role and disclosure, Pay: fixed, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('CORE-04', 'As-of or period date present', 'direct', 'soft', 'Identity, Listing and market, Sector, Reporting basis, Financials, Workforce, Ownership and control, Segment and geography, Pay policy, Role and disclosure, Pay: fixed, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('CORE-05', 'Schema type matches (number, date, code, text)', 'direct', 'soft', 'Identity, Listing and market, Sector, Reporting basis, Financials, Workforce, Ownership and control, Segment and geography, Pay policy, Role and disclosure, Pay: fixed, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('COD-01', 'Value exists in controlled list or taxonomy', 'direct', 'hard', 'Identity, Listing and market, Sector, Reporting basis, Role and disclosure', NULL, 'active', 'Confirm if this is needed for bronze layer or make it Soft'),
  ('COD-02', 'Taxonomy or list version recorded', 'direct', 'soft', 'Listing and market, Sector, Role and disclosure', NULL, 'active', NULL),
  ('COD-03', 'Format check (e.g. LEI length and structure)', 'direct', 'hard', 'Identity', NULL, 'active', NULL),
  ('COD-04', 'Name matches source legal name', 'direct', 'soft', 'Identity', NULL, 'active', NULL),
  ('COD-05', 'Status from fixed set', 'direct', 'soft', 'Listing and market, Role and disclosure', NULL, 'active', NULL),
  ('COD-06', 'Fiscal year end is a valid date', 'direct', 'hard', 'Reporting basis', NULL, 'active', NULL),
  ('NUM-01', 'Reporting currency recorded and ISO 4217', 'direct', 'hard', 'Financials, Pay: fixed, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('NUM-02', 'Units recorded (thousands, millions, units)', 'direct', 'soft', 'Financials, Segment and geography, Pay: fixed, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('NUM-03', 'Value annualised where applicable', 'direct', 'soft', 'Pay: fixed, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('NUM-04', 'Magnitude within plausible range', 'direct', 'soft', 'Financials, Workforce, Pay: fixed, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('NUM-05', 'Counts are whole numbers and FTE <= headcount', 'direct', 'hard', 'Workforce', NULL, 'active', NULL),
  ('NUM-06', 'Percentages between 0 and 100', 'direct', 'hard', 'Ownership and control, Pay: STI', NULL, 'active', NULL),
  ('NUM-07', 'Combined holdings <= 100%', 'direct', 'hard', 'Ownership and control', NULL, 'active', NULL),
  ('NUM-08', 'Segments sum to total within tolerance', 'direct', 'soft', 'Segment and geography', NULL, 'active', 'define tolerance'),
  ('NUM-09', 'Valuation basis stated (grant, face, realised)', 'direct', 'hard', 'Pay: LTI', NULL, 'hold_off', 'hold off'),
  ('NUM-10', 'Performance period recorded', 'direct', 'soft', 'Pay: STI, Pay: LTI', NULL, 'hold_off', 'hold off'),
  ('NUM-11', 'Payout <= maximum opportunity', 'direct', 'hard', 'Pay: STI', NULL, 'hold_off', 'hold off'),
  ('NUM-12', 'Period and as-of date consistent across pay fields', 'direct', 'soft', 'Pay: fixed, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('DES-01', 'Each claim tied to a locator', 'direct', 'hard', 'Pay policy', NULL, 'active', NULL),
  ('DES-02', 'Enumerated values use allowed list', 'direct', 'hard', 'Pay policy', NULL, 'active', NULL),
  ('DER-01', 'Formula and version recorded', 'derived', 'soft', 'Workforce, Ownership and control, Segment and geography, Role and disclosure, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('DER-02', 'Inputs pass own checks (otherwise blocked)', 'derived', 'hard', 'Workforce, Ownership and control, Segment and geography, Role and disclosure, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('DER-03', 'Recalculated value matches stored value', 'derived', 'hard', 'Workforce, Ownership and control, Segment and geography, Role and disclosure, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('DER-04', 'Inputs share currency, period, scope and basis', 'derived', 'soft', 'Role and disclosure, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('DER-05', 'Denominator non-zero and result plausible', 'derived', 'hard', 'Workforce, Segment and geography, Role and disclosure, Pay: STI, Pay: LTI', NULL, 'active', NULL),
  ('DER-06', 'Output marked as derived (provenance flag)', 'derived', 'soft', 'Workforce, Ownership and control, Segment and geography, Role and disclosure, Pay: STI, Pay: LTI, Pay: total', NULL, 'active', NULL),
  ('DER-07', 'All holdings share as-of date and percentage basis', 'derived', 'hard', 'Ownership and control', NULL, 'active', NULL),
  ('DER-08', 'Entity consolidation applied before ranking', 'derived', 'soft', 'Ownership and control', NULL, 'active', NULL),
  ('DER-09', 'Ties listed explicitly', 'derived', 'soft', 'Ownership and control', NULL, 'active', NULL),
  ('XF-01', 'Total reconciles to fixed + STI + LTI', 'derived', 'hard', 'Pay: total', NULL, 'active', NULL),
  ('XF-02', 'Source-reported total matches pipeline total', 'derived', 'soft', 'Pay: total', NULL, 'active', NULL),
  ('XF-03', 'Ratios recalculate from stored inputs', 'derived', 'hard', 'Workforce, Segment and geography, Role and disclosure', NULL, 'active', NULL),
  ('DER-10', 'Undefined check (cited for largest_holders)', NULL, NULL, NULL, NULL, 'to_do', 'Cited in the field catalogue but not defined in All Checks'),
  ('DER-11', 'Undefined check (cited for largest_holders)', NULL, NULL, NULL, NULL, 'to_do', 'Cited in the field catalogue but not defined in All Checks'),
  ('STI-1', 'Paid STI <= max STI % x base salary x 1.10', NULL, 'hard', NULL, 'NUM-11', 'to_do', '10% tolerance: STI is often paid on last year\'s base. If the max is stated another way (STI basis tab), the rule does not apply: Review.'),
  ('STI-2', 'Target STI % <= max STI %', NULL, 'hard', NULL, 'NUM-11', 'to_do', NULL),
  ('STI-3', 'No paid STI', NULL, 'soft', NULL, 'NUM-11', 'to_do', NULL),
  ('STI-4', 'Paid STI <= 3 x base', NULL, 'soft', NULL, 'NUM-04', 'to_do', NULL),
  ('PCT-1', 'Value is a whole percentage: 15 means 15%', NULL, 'hard', NULL, 'NUM-06', 'to_do', 'Between 0 and 1 means a fraction was entered (0.15). Above 1,000 means an amount was entered.'),
  ('LTI-1', 'Target LTI % <= max LTI %', NULL, 'hard', NULL, 'NUM-11', 'to_do', NULL),
  ('LTI-2', 'The value has a basis from the LTI basis tab', NULL, 'soft', NULL, 'NUM-09', 'to_do', 'This is the gate behind the 92 unmapped LTI labels.'),
  ('PAY-1', 'Total = sum of the listed components, within the existing tolerance', NULL, 'hard', NULL, 'XF-01, XF-02', 'to_do', 'Record which components the document\'s total includes; documents differ (some totals include pension, some do not).'),
  ('PAY-2', 'One pay period across all pay fields for the role', NULL, 'hard', NULL, 'NUM-12', 'existing', 'Existing gate.'),
  ('PAY-3', 'The value is the amount actually paid, with months_in_role set', NULL, 'soft', NULL, 'NUM-03', 'to_do', 'Do not annualise in the tracker. The CDP decides annualisation per use.'),
  ('PAY-4', 'Kept, with token_salary = true', NULL, 'soft', NULL, 'NUM-04', 'to_do', 'Genuine (e.g. a 1 USD CEO salary), but left out of benchmarks.'),
  ('PAY-5', 'is_aggregated = true and aggregate_headcount set', NULL, 'hard', NULL, 'NUM-04', 'to_do', 'A group total read as one person distorts every benchmark.'),
  ('PAY-6', 'months_in_role set', NULL, 'soft', NULL, 'NUM-03', 'to_do', 'These are usually part-year roles.'),
  ('PEN-1', 'Pension <= 60% of base', NULL, 'soft', NULL, 'NUM-04', 'to_do', NULL),
  ('BEN-1', 'Benefits <= base', NULL, 'soft', NULL, 'NUM-04', 'to_do', NULL),
  ('CUR-1', 'Currency is the country\'s own, or EUR, USD, GBP or CHF', NULL, 'soft', NULL, 'NUM-01', 'to_do', NULL),
  ('AGE-1', 'Age in the pay year is 18 to 80', NULL, 'hard', NULL, 'NUM-04', 'to_do', NULL),
  ('AGE-2', 'Role start year is not after the pay year, and is at least 16 years after birth', NULL, 'hard', NULL, 'NUM-04', 'to_do', NULL),
  ('AGE-3', 'Joined the company no later than the current role started', NULL, 'soft', NULL, 'NUM-04', 'to_do', NULL),
  ('SRC-1', 'The quoted source text is found in the document under the Quote matching rules', NULL, 'hard', NULL, 'CORE-01, CORE-02', 'to_do', 'This is the gate behind the 208 values.'),
  ('EXC-1', 'Stored as an ISO 10383 MIC (e.g. XSTO), not a name', NULL, 'hard', NULL, 'COD-01', 'to_do', NULL),
  ('OWN-1', 'The list has an as-of date', NULL, 'soft', NULL, 'CORE-04, DER-07', 'to_do', 'Needed for the 20% voting-control rule.'),
  ('LEI-1', 'ISO 17442 check digits pass', NULL, 'hard', NULL, 'COD-03', 'existing', 'Existing gate, all passing.'),
  ('SEG-1', 'Segments sum to total revenue within 1%', NULL, 'soft', NULL, 'NUM-08', 'existing', 'Existing gate. Review, not Fail: an unallocated or eliminations line often explains the gap.');

INSERT INTO `your-gcp-project.allshares_cdp.bridge_field_check` (field_name, check_code, pass_criteria, fail_criteria, example, reference, remarks, score, weight) VALUES
  ('revenue', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'revenue recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.02127659574468085),
  ('revenue', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'revenue: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.02127659574468085),
  ('revenue', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.010638297872340425),
  ('revenue', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.010638297872340425),
  ('revenue', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', 'Is it only for date or also for others', 1.0, 0.010638297872340425),
  ('revenue', 'NUM-01', 'Currency recorded and is ISO 4217', 'No currency, or a non-ISO code such as \'EURO\'', 'unit \'EUR\' (ISO 4217)', 'ISO 4217', NULL, 2.0, 0.02127659574468085),
  ('revenue', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', 'Confirm the range', 1.0, 0.010638297872340425),
  ('revenue', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', 'Confirm the range', 1.0, 0.010638297872340425),
  ('total_assets', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'total_assets recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.02127659574468085),
  ('total_assets', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'total_assets: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.02127659574468085),
  ('total_assets', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.010638297872340425),
  ('total_assets', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.010638297872340425),
  ('total_assets', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', 'Is it only for date or also for others', 1.0, 0.010638297872340425),
  ('total_assets', 'NUM-01', 'Currency recorded and is ISO 4217', 'No currency, or a non-ISO code such as \'EURO\'', 'unit \'EUR\' (ISO 4217)', 'ISO 4217', NULL, 2.0, 0.02127659574468085),
  ('total_assets', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.010638297872340425),
  ('total_assets', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.010638297872340425),
  ('ebitda', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'ebitda recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.02127659574468085),
  ('ebitda', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'ebitda: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.02127659574468085),
  ('ebitda', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.010638297872340425),
  ('ebitda', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.010638297872340425),
  ('ebitda', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.010638297872340425),
  ('ebitda', 'NUM-01', 'Currency recorded and is ISO 4217', 'No currency, or a non-ISO code such as \'EURO\'', 'unit \'EUR\' (ISO 4217)', 'ISO 4217', NULL, 2.0, 0.02127659574468085),
  ('ebitda', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.010638297872340425),
  ('ebitda', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.010638297872340425),
  ('shares_outstanding', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'shares_outstanding recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.02127659574468085),
  ('shares_outstanding', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'shares_outstanding: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.02127659574468085),
  ('shares_outstanding', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.010638297872340425),
  ('shares_outstanding', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.010638297872340425),
  ('shares_outstanding', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.010638297872340425),
  ('shares_outstanding', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.010638297872340425),
  ('shares_outstanding', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.010638297872340425),
  ('legal_name', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'legal_name recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('legal_name', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'legal_name: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('legal_name', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('legal_name', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('legal_name', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('legal_name', 'COD-04', 'Name matches the source legal name', 'Name differs from the source legal name', 'legal_name \'Sydbank A/S\' matches the filing cover', 'Allshares reference list (to confirm)', NULL, 1.0, 0.005917159763313609),
  ('other_names', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'other_names recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('other_names', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'other_names: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('other_names', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('other_names', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('other_names', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('lei', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'lei recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('lei', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'lei: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('lei', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('lei', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('lei', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('lei', 'COD-03', 'LEI is 20 characters and passes ISO 17442 check digits', 'Length, character set or mod-97 check fails', 'LEI 5493001KJTIIGC8Y1R12 (ISO 17442 example)', 'ISO 17442', NULL, 2.0, 0.011834319526627219),
  ('business_id', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'business_id recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('business_id', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'business_id: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('business_id', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('business_id', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('business_id', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('cik', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'cik recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('cik', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'cik: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('cik', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('cik', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('cik', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('country_code', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'country_code recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('country_code', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'country_code: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('country_code', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('country_code', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('country_code', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('country_code', 'COD-01', 'Value is in the controlled list or taxonomy', 'Code not in the list, or exchange stored as a name not a MIC', 'country_code DK; exchange XCSE (ISO 10383 MIC)', 'ISO 3166 / ISO 10383 / Allshares lists', NULL, 2.0, 0.011834319526627219),
  ('head_office_city', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'head_office_city recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('head_office_city', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'head_office_city: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('head_office_city', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('head_office_city', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('head_office_city', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('website', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'website recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('website', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'website: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('website', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('website', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('website', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('isin', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'isin recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('isin', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'isin: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('isin', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('isin', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('isin', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('ticker', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'ticker recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('ticker', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'ticker: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('ticker', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('ticker', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('ticker', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('exchange', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'exchange recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('exchange', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'exchange: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('exchange', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('exchange', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('exchange', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('exchange', 'COD-01', 'Value is in the controlled list or taxonomy', 'Code not in the list, or exchange stored as a name not a MIC', 'country_code DK; exchange XCSE (ISO 10383 MIC)', 'ISO 3166 / ISO 10383 / Allshares lists', NULL, 2.0, 0.011834319526627219),
  ('exchange_segment', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'exchange_segment recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('exchange_segment', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'exchange_segment: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('exchange_segment', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('exchange_segment', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('exchange_segment', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('listing_status', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'listing_status recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('listing_status', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'listing_status: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('listing_status', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('listing_status', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('listing_status', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('listing_status', 'COD-05', 'Status is from the fixed set', 'Status outside listed / delisted / suspended / not listed', 'listing_status \'listed\'', 'Allshares reference list (to confirm)', NULL, 1.0, 0.005917159763313609),
  ('listing_date', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'listing_date recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('listing_date', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'listing_date: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('listing_date', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('listing_date', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('listing_date', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('share_price', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'share_price recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('share_price', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'share_price: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('share_price', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('share_price', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('share_price', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('market_cap_band', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'market_cap_band recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('market_cap_band', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'market_cap_band: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('market_cap_band', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('market_cap_band', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('market_cap_band', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('largest_holders', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'largest_holders recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.015267175572519083),
  ('largest_holders', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'largest_holders: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.015267175572519083),
  ('largest_holders', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('largest_holders', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('largest_holders', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('largest_holders', 'NUM-06', 'Percentages between 0 and 100', 'Percentage below 0 or above 100', 'Holder 11.6%; STI target 50% of salary', 'Allshares reference range (to set)', NULL, 2.0, 0.015267175572519083),
  ('largest_holders', 'NUM-07', 'Combined listed holdings not above 100%', 'Listed holdings total above 100%', 'Holders total 96%', 'Allshares reference range (to set)', NULL, 2.0, 0.015267175572519083),
  ('largest_holders', 'DER-07', 'All holdings share one as-of date and percentage basis', 'Holdings lack an as-of date or a basic/diluted basis', 'All holdings at 2025-12-31, basic shares', 'Part 1 derived-check rules', NULL, 2.0, 0.015267175572519083),
  ('largest_holders', 'DER-08', 'Holders consolidated before ranking', 'Same economic owner listed twice', 'Parent and subsidiary shown as one holder', 'Part 1 derived-check rules', NULL, 1.0, 0.007633587786259542),
  ('largest_holders', 'DER-09', 'Ties listed explicitly', 'Tie hidden: two holders at the same percentage shown as one', 'Two holders at 10% both listed', 'Part 1 derived-check rules', NULL, 1.0, 0.007633587786259542),
  ('controlling_owner', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'controlling_owner recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.015267175572519083),
  ('controlling_owner', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'controlling_owner: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.015267175572519083),
  ('controlling_owner', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('controlling_owner', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('controlling_owner', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('controlling_owner_name', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'controlling_owner_name recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.015267175572519083),
  ('controlling_owner_name', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'controlling_owner_name: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.015267175572519083),
  ('controlling_owner_name', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('controlling_owner_name', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('controlling_owner_name', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('ownership_type', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'ownership_type recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.015267175572519083),
  ('ownership_type', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'ownership_type: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.015267175572519083),
  ('ownership_type', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('ownership_type', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('ownership_type', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('pe_stake_5pct', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'pe_stake_5pct recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.015267175572519083),
  ('pe_stake_5pct', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'pe_stake_5pct: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.015267175572519083),
  ('pe_stake_5pct', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('pe_stake_5pct', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('pe_stake_5pct', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('ultimate_parent', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'ultimate_parent recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.015267175572519083),
  ('ultimate_parent', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'ultimate_parent: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.015267175572519083),
  ('ultimate_parent', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('ultimate_parent', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('ultimate_parent', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.007633587786259542),
  ('pension_type', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'pension_type recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.015037593984962405),
  ('pension_type', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'pension_type: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.015037593984962405),
  ('pension_type', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.007518796992481203),
  ('pension_type', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.007518796992481203),
  ('pension_type', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.007518796992481203),
  ('pension_type', 'DES-01', 'Each policy claim tied to a locator', 'Claim has no locator', 'pension_type with locator page 42', 'Allshares allowed list (to confirm)', NULL, 2.0, 0.015037593984962405),
  ('pension_type', 'DES-02', 'Enumerated value maps to the allowed list', 'Free text not mappable to the allowed list', 'pension_type \'defined contribution\' maps to defined contribution', 'Allshares allowed list (to confirm)', NULL, 2.0, 0.015037593984962405),
  ('benefits', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'benefits recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.015037593984962405),
  ('benefits', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'benefits: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.015037593984962405),
  ('benefits', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.007518796992481203),
  ('benefits', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.007518796992481203),
  ('benefits', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.007518796992481203),
  ('benefits', 'DES-01', 'Each policy claim tied to a locator', 'Claim has no locator', 'pension_type with locator page 42', 'Allshares allowed list (to confirm)', NULL, 2.0, 0.015037593984962405),
  ('shareholding_requirement', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'shareholding_requirement recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.015037593984962405),
  ('shareholding_requirement', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'shareholding_requirement: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.015037593984962405),
  ('shareholding_requirement', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.007518796992481203),
  ('shareholding_requirement', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.007518796992481203),
  ('shareholding_requirement', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.007518796992481203),
  ('shareholding_requirement', 'DES-01', 'Each policy claim tied to a locator', 'Claim has no locator', 'pension_type with locator page 42', 'Allshares allowed list (to confirm)', NULL, 2.0, 0.015037593984962405),
  ('pay_currency', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'pay_currency recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.017241379310344827),
  ('pay_currency', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'pay_currency: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.017241379310344827),
  ('pay_currency', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.008620689655172414),
  ('pay_currency', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.008620689655172414),
  ('pay_currency', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.008620689655172414),
  ('pay_currency', 'NUM-01', 'Currency recorded and is ISO 4217', 'No currency, or a non-ISO code such as \'EURO\'', 'unit \'EUR\' (ISO 4217)', 'ISO 4217', NULL, 2.0, 0.017241379310344827),
  ('base_salary', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'base_salary recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.017241379310344827),
  ('base_salary', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'base_salary: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.017241379310344827),
  ('base_salary', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.008620689655172414),
  ('base_salary', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.008620689655172414),
  ('base_salary', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.008620689655172414),
  ('base_salary', 'NUM-01', 'Currency recorded and is ISO 4217', 'No currency, or a non-ISO code such as \'EURO\'', 'unit \'EUR\' (ISO 4217)', 'ISO 4217', NULL, 2.0, 0.017241379310344827),
  ('base_salary', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.008620689655172414),
  ('base_salary', 'NUM-03', 'Value annualised where applicable', 'Value is a monthly or pro-rated figure labelled annual', 'Base salary 420,000 EUR per year, annualised', 'Allshares reference range (to set)', NULL, 1.0, 0.008620689655172414),
  ('base_salary', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.008620689655172414),
  ('base_salary', 'NUM-12', 'All pay fields for one role share one period', 'Periods differ across pay fields, or one is missing', 'base_salary, sti_paid and total all 2025-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.008620689655172414),
  ('benefits_value', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'benefits_value recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.017241379310344827),
  ('benefits_value', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'benefits_value: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.017241379310344827),
  ('benefits_value', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.008620689655172414),
  ('benefits_value', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.008620689655172414),
  ('benefits_value', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.008620689655172414),
  ('benefits_value', 'NUM-01', 'Currency recorded and is ISO 4217', 'No currency, or a non-ISO code such as \'EURO\'', 'unit \'EUR\' (ISO 4217)', 'ISO 4217', NULL, 2.0, 0.017241379310344827),
  ('benefits_value', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.008620689655172414),
  ('benefits_value', 'NUM-03', 'Value annualised where applicable', 'Value is a monthly or pro-rated figure labelled annual', 'Base salary 420,000 EUR per year, annualised', 'Allshares reference range (to set)', NULL, 1.0, 0.008620689655172414),
  ('benefits_value', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.008620689655172414),
  ('benefits_value', 'NUM-12', 'All pay fields for one role share one period', 'Periods differ across pay fields, or one is missing', 'base_salary, sti_paid and total all 2025-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.008620689655172414),
  ('pension_contribution', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'pension_contribution recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.017241379310344827),
  ('pension_contribution', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'pension_contribution: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.017241379310344827),
  ('pension_contribution', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.008620689655172414),
  ('pension_contribution', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.008620689655172414);

INSERT INTO `your-gcp-project.allshares_cdp.bridge_field_check` (field_name, check_code, pass_criteria, fail_criteria, example, reference, remarks, score, weight) VALUES
  ('pension_contribution', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.008620689655172414),
  ('pension_contribution', 'NUM-01', 'Currency recorded and is ISO 4217', 'No currency, or a non-ISO code such as \'EURO\'', 'unit \'EUR\' (ISO 4217)', 'ISO 4217', NULL, 2.0, 0.017241379310344827),
  ('pension_contribution', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.008620689655172414),
  ('pension_contribution', 'NUM-03', 'Value annualised where applicable', 'Value is a monthly or pro-rated figure labelled annual', 'Base salary 420,000 EUR per year, annualised', 'Allshares reference range (to set)', NULL, 1.0, 0.008620689655172414),
  ('pension_contribution', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.008620689655172414),
  ('pension_contribution', 'NUM-12', 'All pay fields for one role share one period', 'Periods differ across pay fields, or one is missing', 'base_salary, sti_paid and total all 2025-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.008620689655172414),
  ('total_remuneration', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'total_remuneration recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.021739130434782608),
  ('total_remuneration', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'total_remuneration: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.021739130434782608),
  ('total_remuneration', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.010869565217391304),
  ('total_remuneration', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.010869565217391304),
  ('total_remuneration', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.010869565217391304),
  ('total_remuneration', 'NUM-01', 'Currency recorded and is ISO 4217', 'No currency, or a non-ISO code such as \'EURO\'', 'unit \'EUR\' (ISO 4217)', 'ISO 4217', NULL, 2.0, 0.021739130434782608),
  ('total_remuneration', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.010869565217391304),
  ('total_remuneration', 'NUM-03', 'Value annualised where applicable', 'Value is a monthly or pro-rated figure labelled annual', 'Base salary 420,000 EUR per year, annualised', 'Allshares reference range (to set)', NULL, 1.0, 0.010869565217391304),
  ('total_remuneration', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.010869565217391304),
  ('total_remuneration', 'NUM-12', 'All pay fields for one role share one period', 'Periods differ across pay fields, or one is missing', 'base_salary, sti_paid and total all 2025-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.010869565217391304),
  ('total_remuneration', 'XF-01', 'Total equals base + benefits + pension + STI paid + LTI vested (within 1% or 1,000)', 'Total outside tolerance of the component sum', 'Total 1,050,000 vs components 1,049,600', 'Part 1 cross-field rules', NULL, 2.0, 0.021739130434782608),
  ('fiscal_year', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'fiscal_year recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('fiscal_year', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'fiscal_year: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('fiscal_year', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('fiscal_year', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('fiscal_year', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('fiscal_year_end', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'fiscal_year_end recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('fiscal_year_end', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'fiscal_year_end: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('fiscal_year_end', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('fiscal_year_end', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('fiscal_year_end', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('fiscal_year_end', 'COD-06', 'Fiscal year end is a valid date', 'Not a valid YYYY-MM-DD date (e.g. 31 February)', 'fiscal_year_end 2025-12-31', 'Allshares reference list (to confirm)', NULL, 2.0, 0.011834319526627219),
  ('reporting_currency', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'reporting_currency recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('reporting_currency', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'reporting_currency: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('reporting_currency', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('reporting_currency', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('reporting_currency', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('accounting_basis', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'accounting_basis recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('accounting_basis', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'accounting_basis: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('accounting_basis', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('accounting_basis', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('accounting_basis', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('accounting_basis', 'COD-01', 'Value is in the controlled list or taxonomy', 'Code not in the list, or exchange stored as a name not a MIC', 'country_code DK; exchange XCSE (ISO 10383 MIC)', 'ISO 3166 / ISO 10383 / Allshares lists', NULL, 2.0, 0.011834319526627219),
  ('role_disclosure', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'role_disclosure recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('role_disclosure', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'role_disclosure: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('role_disclosure', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('role_disclosure', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('role_disclosure', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('role_disclosure', 'COD-01', 'Value is in the controlled list or taxonomy', 'Code not in the list, or exchange stored as a name not a MIC', 'country_code DK; exchange XCSE (ISO 10383 MIC)', 'ISO 3166 / ISO 10383 / Allshares lists', NULL, 2.0, 0.009345794392523364),
  ('role_disclosure', 'COD-02', 'Taxonomy or list version recorded', 'Version not stored with the code', 'sector_code 45102010 with taxonomy GICS 2025', 'Allshares reference list (to confirm)', NULL, 1.0, 0.004672897196261682),
  ('role_disclosure', 'COD-05', 'Status is from the fixed set', 'Status outside listed / delisted / suspended / not listed', 'listing_status \'listed\'', 'Allshares reference list (to confirm)', NULL, 1.0, 0.004672897196261682),
  ('aggregate_headcount', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'aggregate_headcount recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('aggregate_headcount', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'aggregate_headcount: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('aggregate_headcount', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('aggregate_headcount', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('aggregate_headcount', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('sector_code', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'sector_code recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('sector_code', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'sector_code: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('sector_code', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('sector_code', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('sector_code', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('sector_code', 'COD-01', 'Value is in the controlled list or taxonomy', 'Code not in the list, or exchange stored as a name not a MIC', 'country_code DK; exchange XCSE (ISO 10383 MIC)', 'ISO 3166 / ISO 10383 / Allshares lists', NULL, 2.0, 0.011834319526627219),
  ('sector_code', 'COD-02', 'Taxonomy or list version recorded', 'Version not stored with the code', 'sector_code 45102010 with taxonomy GICS 2025', 'Allshares reference list (to confirm)', NULL, 1.0, 0.005917159763313609),
  ('sub_sector', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'sub_sector recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('sub_sector', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'sub_sector: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.011834319526627219),
  ('sub_sector', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('sub_sector', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('sub_sector', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.005917159763313609),
  ('revenue_by_segment', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'revenue_by_segment recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.0136986301369863),
  ('revenue_by_segment', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'revenue_by_segment: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.0136986301369863),
  ('revenue_by_segment', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('revenue_by_segment', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('revenue_by_segment', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('revenue_by_segment', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.00684931506849315),
  ('revenue_by_segment', 'NUM-08', 'Segments sum to total revenue within 1%', 'Segments differ from total revenue by more than 1%', 'Segments 7,548 vs revenue 7,548 (DKK millions)', 'Allshares reference range (to set)', NULL, 1.0, 0.00684931506849315),
  ('staff_by_segment', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'staff_by_segment recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.0136986301369863),
  ('staff_by_segment', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'staff_by_segment: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.0136986301369863),
  ('staff_by_segment', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('staff_by_segment', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('staff_by_segment', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('staff_by_segment', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.00684931506849315),
  ('revenue_by_country', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'revenue_by_country recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.0136986301369863),
  ('revenue_by_country', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'revenue_by_country: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.0136986301369863),
  ('revenue_by_country', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('revenue_by_country', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('revenue_by_country', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('revenue_by_country', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.00684931506849315),
  ('revenue_by_country', 'NUM-08', 'Segments sum to total revenue within 1%', 'Segments differ from total revenue by more than 1%', 'Segments 7,548 vs revenue 7,548 (DKK millions)', 'Allshares reference range (to set)', NULL, 1.0, 0.00684931506849315),
  ('staff_by_country', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'staff_by_country recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.0136986301369863),
  ('staff_by_country', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'staff_by_country: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.0136986301369863),
  ('staff_by_country', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('staff_by_country', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('staff_by_country', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('staff_by_country', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.00684931506849315),
  ('headcount', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'headcount recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.0136986301369863),
  ('headcount', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'headcount: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.0136986301369863),
  ('headcount', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('sti_paid', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'sti_paid recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('sti_paid', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'sti_paid: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('sti_paid', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('sti_paid', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('sti_paid', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('sti_paid', 'NUM-01', 'Currency recorded and is ISO 4217', 'No currency, or a non-ISO code such as \'EURO\'', 'unit \'EUR\' (ISO 4217)', 'ISO 4217', NULL, 2.0, 0.009345794392523364),
  ('sti_paid', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_paid', 'NUM-03', 'Value annualised where applicable', 'Value is a monthly or pro-rated figure labelled annual', 'Base salary 420,000 EUR per year, annualised', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_paid', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_paid', 'NUM-10', 'Performance period start and end recorded', 'Start or end missing', 'Performance period 2025-01-01 to 2027-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_paid', 'NUM-11', 'Paid STI not above the maximum', 'Paid STI above the maximum opportunity', 'sti_paid 180,000 EUR; sti_max 250,000 EUR', 'Allshares reference range (to set)', NULL, 2.0, 0.009345794392523364),
  ('sti_paid', 'NUM-12', 'All pay fields for one role share one period', 'Periods differ across pay fields, or one is missing', 'base_salary, sti_paid and total all 2025-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_target', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'sti_target recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('sti_target', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'sti_target: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('sti_target', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('sti_target', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('sti_target', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('sti_target', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_target', 'NUM-03', 'Value annualised where applicable', 'Value is a monthly or pro-rated figure labelled annual', 'Base salary 420,000 EUR per year, annualised', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_target', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_target', 'NUM-06', 'Percentages between 0 and 100', 'Percentage below 0 or above 100', 'Holder 11.6%; STI target 50% of salary', 'Allshares reference range (to set)', NULL, 2.0, 0.009345794392523364),
  ('sti_target', 'NUM-10', 'Performance period start and end recorded', 'Start or end missing', 'Performance period 2025-01-01 to 2027-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_target', 'NUM-12', 'All pay fields for one role share one period', 'Periods differ across pay fields, or one is missing', 'base_salary, sti_paid and total all 2025-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_max', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'sti_max recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('sti_max', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'sti_max: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('sti_max', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('sti_max', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('sti_max', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('sti_max', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_max', 'NUM-03', 'Value annualised where applicable', 'Value is a monthly or pro-rated figure labelled annual', 'Base salary 420,000 EUR per year, annualised', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_max', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_max', 'NUM-06', 'Percentages between 0 and 100', 'Percentage below 0 or above 100', 'Holder 11.6%; STI target 50% of salary', 'Allshares reference range (to set)', NULL, 2.0, 0.009345794392523364),
  ('sti_max', 'NUM-10', 'Performance period start and end recorded', 'Start or end missing', 'Performance period 2025-01-01 to 2027-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('sti_max', 'NUM-12', 'All pay fields for one role share one period', 'Periods differ across pay fields, or one is missing', 'base_salary, sti_paid and total all 2025-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_vested', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'lti_vested recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('lti_vested', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'lti_vested: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('lti_vested', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('lti_vested', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('lti_vested', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('lti_vested', 'NUM-01', 'Currency recorded and is ISO 4217', 'No currency, or a non-ISO code such as \'EURO\'', 'unit \'EUR\' (ISO 4217)', 'ISO 4217', NULL, 2.0, 0.009345794392523364),
  ('lti_vested', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_vested', 'NUM-03', 'Value annualised where applicable', 'Value is a monthly or pro-rated figure labelled annual', 'Base salary 420,000 EUR per year, annualised', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_vested', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_vested', 'NUM-09', 'Valuation basis is grant, face or realised', 'Basis missing, or a label that is not grant, face or realised', 'lti_granted 300,000 EUR, valuation basis \'face value\'', 'Allshares reference range (to set)', NULL, 2.0, 0.009345794392523364),
  ('lti_vested', 'NUM-10', 'Performance period start and end recorded', 'Start or end missing', 'Performance period 2025-01-01 to 2027-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_vested', 'NUM-12', 'All pay fields for one role share one period', 'Periods differ across pay fields, or one is missing', 'base_salary, sti_paid and total all 2025-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_granted', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'lti_granted recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('lti_granted', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'lti_granted: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('lti_granted', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('lti_granted', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('lti_granted', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('lti_granted', 'NUM-01', 'Currency recorded and is ISO 4217', 'No currency, or a non-ISO code such as \'EURO\'', 'unit \'EUR\' (ISO 4217)', 'ISO 4217', NULL, 2.0, 0.009345794392523364),
  ('lti_granted', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_granted', 'NUM-03', 'Value annualised where applicable', 'Value is a monthly or pro-rated figure labelled annual', 'Base salary 420,000 EUR per year, annualised', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_granted', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_granted', 'NUM-09', 'Valuation basis is grant, face or realised', 'Basis missing, or a label that is not grant, face or realised', 'lti_granted 300,000 EUR, valuation basis \'face value\'', 'Allshares reference range (to set)', NULL, 2.0, 0.009345794392523364),
  ('lti_granted', 'NUM-10', 'Performance period start and end recorded', 'Start or end missing', 'Performance period 2025-01-01 to 2027-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_granted', 'NUM-12', 'All pay fields for one role share one period', 'Periods differ across pay fields, or one is missing', 'base_salary, sti_paid and total all 2025-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_target', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'lti_target recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('lti_target', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'lti_target: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('lti_target', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('lti_target', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('lti_target', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('lti_target', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_target', 'NUM-03', 'Value annualised where applicable', 'Value is a monthly or pro-rated figure labelled annual', 'Base salary 420,000 EUR per year, annualised', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_target', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_target', 'NUM-09', 'Valuation basis is grant, face or realised', 'Basis missing, or a label that is not grant, face or realised', 'lti_granted 300,000 EUR, valuation basis \'face value\'', 'Allshares reference range (to set)', NULL, 2.0, 0.009345794392523364),
  ('lti_target', 'NUM-10', 'Performance period start and end recorded', 'Start or end missing', 'Performance period 2025-01-01 to 2027-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_target', 'NUM-12', 'All pay fields for one role share one period', 'Periods differ across pay fields, or one is missing', 'base_salary, sti_paid and total all 2025-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_max', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'lti_max recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('lti_max', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'lti_max: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.009345794392523364),
  ('lti_max', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('lti_max', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('lti_max', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.004672897196261682),
  ('lti_max', 'NUM-02', 'Units recorded (thousands, millions, units)', 'Unit field empty', 'unit \'DKK millions\'', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_max', 'NUM-03', 'Value annualised where applicable', 'Value is a monthly or pro-rated figure labelled annual', 'Base salary 420,000 EUR per year, annualised', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_max', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_max', 'NUM-09', 'Valuation basis is grant, face or realised', 'Basis missing, or a label that is not grant, face or realised', 'lti_granted 300,000 EUR, valuation basis \'face value\'', 'Allshares reference range (to set)', NULL, 2.0, 0.009345794392523364),
  ('lti_max', 'NUM-10', 'Performance period start and end recorded', 'Start or end missing', 'Performance period 2025-01-01 to 2027-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('lti_max', 'NUM-12', 'All pay fields for one role share one period', 'Periods differ across pay fields, or one is missing', 'base_salary, sti_paid and total all 2025-12-31', 'Allshares reference range (to set)', NULL, 1.0, 0.004672897196261682),
  ('headcount', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('headcount', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('headcount', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.00684931506849315),
  ('headcount', 'NUM-05', 'Headcount is a whole number; FTE not above headcount on the same basis', 'Non-whole headcount, or FTE above headcount on the same basis', 'headcount 1,240; fte 1,105 (both year-end)', 'Allshares reference range (to set)', NULL, 2.0, 0.0136986301369863),
  ('fte', 'CORE-01', 'Locator recorded', 'Value has no page, table or line locator', 'fte recorded with locator: page 42, table 3', 'Part 1 core checks', NULL, 2.0, 0.0136986301369863),
  ('fte', 'CORE-02', 'Snippet re-parses to the same value', 'Snippet not found verbatim in the source, or parses to a different value', 'fte: quoted snippet matches the stored value', 'Part 1 core checks', NULL, 2.0, 0.0136986301369863),
  ('fte', 'CORE-03', 'Source ID exists and is registered', 'No source ID, or source not in the register', 'Source ID \'AR-2025-SYD\' registered as annual report FY2025', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('fte', 'CORE-04', 'As-of or period date present (static fields: retrieved_at used)', 'No period end date on a time-bound field', 'period_end 2025-12-31', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('fte', 'CORE-05', 'Value matches its schema (number, ISO date, list, text)', 'Value not a number, not an ISO date, or list not in name: value form', 'fiscal_year_end 2025-12-31 (ISO date)', 'Part 1 core checks', NULL, 1.0, 0.00684931506849315),
  ('fte', 'NUM-04', 'Magnitude within the plausible range for the field', 'Outside the range Allshares sets for the field', 'Revenue within the range set for the company\'s size', 'Allshares reference range (to set)', NULL, 1.0, 0.00684931506849315),
  ('fte', 'NUM-05', 'Headcount is a whole number; FTE not above headcount on the same basis', 'Non-whole headcount, or FTE above headcount on the same basis', 'headcount 1,240; fte 1,105 (both year-end)', 'Allshares reference range (to set)', NULL, 2.0, 0.0136986301369863),
  ('largest_holders', 'DER-10', NULL, NULL, NULL, NULL, 'Cited in Book1 \'Checks applied\'; not in Field Checks', NULL, NULL),
  ('largest_holders', 'DER-11', NULL, NULL, NULL, NULL, 'Cited in Book1 \'Checks applied\'; not in Field Checks', NULL, NULL);
