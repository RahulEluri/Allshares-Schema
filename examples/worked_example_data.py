"""Illustrative data for three FICTIONAL companies (FY2025) used by build_worked_example.py.

Every company, person, holder, ID and number here is invented to show how the schema is filled.
Nothing describes a real company.
"""
from __future__ import annotations

import datetime as dt
import uuid

FY = 2025
FY_START, FY_END = dt.date(2025, 1, 1), dt.date(2025, 12, 31)
RUN_ID = "run-2026-11-08-01"
EXTRACTED_AT = dt.datetime(2026, 11, 8, 14, 2, 11)
CHECKED_AT = dt.datetime(2026, 11, 8, 14, 9, 40)
EXAMPLE = "Example (worked example, fictional)"

# Deterministic IDs (UUID v5), as in the 9 Nov pay-storage note.
NS_ROLE = uuid.uuid5(uuid.NAMESPACE_URL, "cdp.allshares/pay_role")
NS_VALUE = uuid.uuid5(uuid.NAMESPACE_URL, "cdp.allshares/pay_value")
NS_RESULT = uuid.uuid5(uuid.NAMESPACE_URL, "cdp.allshares/check_result")


def role_line_id(company_id, fy, disclosure, role_code, person_name=""):
    key = f"{company_id}|{fy}|{disclosure}|{role_code}|{person_name.strip().lower()}"
    return str(uuid.uuid5(NS_ROLE, key))


def value_id(*parts) -> str:
    return str(uuid.uuid5(NS_VALUE, "|".join(str(p) for p in parts)))


def result_id(vid: str, code: str) -> str:
    return str(uuid.uuid5(NS_RESULT, f"{vid}|{code}"))


COMPANIES = [
    {"company_id": "NVK", "name": "Nordvik Kraft AB", "country": "SE", "currency": "SEK"},
    {"company_id": "SRS", "name": "Saarela Systems Oyj", "country": "FI", "currency": "EUR"},
    {"company_id": "FJM", "name": "Fjordline Marine ASA", "country": "NO", "currency": "NOK"},
]

# ------------------------------------------------------------------ ref tables (example values)
REF = {
    "ref_country": [
        {"code": "SE", "label": "Sweden", "region": "Nordics"},
        {"code": "FI", "label": "Finland", "region": "Nordics"},
        {"code": "NO", "label": "Norway", "region": "Nordics"},
        {"code": "DK", "label": "Denmark", "region": "Nordics"},
        {"code": "GB", "label": "United Kingdom", "region": "Western Europe"},
        {"code": "US", "label": "United States", "region": "North America"},
    ],
    "ref_country_currency": [
        {"code": "SE", "label": "Sweden", "currency_code": "SEK"},
        {"code": "FI", "label": "Finland", "currency_code": "EUR"},
        {"code": "NO", "label": "Norway", "currency_code": "NOK"},
        {"code": "DK", "label": "Denmark", "currency_code": "DKK"},
        {"code": "GB", "label": "United Kingdom", "currency_code": "GBP"},
        {"code": "US", "label": "United States", "currency_code": "USD"},
    ],
    "ref_currency": [{"code": c, "label": l} for c, l in [
        ("SEK", "Swedish krona"), ("EUR", "Euro"), ("NOK", "Norwegian krone"), ("DKK", "Danish krone"),
        ("USD", "US dollar"), ("GBP", "Pound sterling"), ("CHF", "Swiss franc"), ("SGD", "Singapore dollar")]],
    "ref_exchange": [{"code": c, "label": l} for c, l in [
        ("XSTO", "Nasdaq Stockholm"), ("XHEL", "Nasdaq Helsinki"), ("XOSL", "Oslo Børs")]],
    "ref_exchange_segment": [{"code": c, "label": l} for c, l in [
        ("large_cap", "Large Cap"), ("mid_cap", "Mid Cap"), ("small_cap", "Small Cap"), ("first_north", "First North")]],
    "ref_listing_status": [{"code": c, "label": l} for c, l in [
        ("listed", "Listed"), ("delisted", "Delisted"), ("suspended", "Suspended")]],
    "ref_accounting_basis": [{"code": c, "label": l} for c, l in [
        ("ifrs", "IFRS"), ("us_gaap", "US GAAP"), ("local_gaap", "Local GAAP")]],
    "ref_ownership_type": [{"code": c, "label": l} for c, l in [
        ("family", "Family / founder"), ("private_equity", "Private equity"), ("state", "State"),
        ("institution", "Institutional investor"), ("foundation", "Foundation"), ("individual", "Individual")]],
    "ref_market_cap_band": [
        {"code": "large", "label": "Large", "meaning": "Market cap >= EUR 1bn"},
        {"code": "mid", "label": "Mid", "meaning": "Market cap >= EUR 150m"},
        {"code": "small", "label": "Small", "meaning": "Below EUR 150m"}],
    "ref_role_disclosure": [
        {"code": "individual_executive", "label": "Individual, executive", "meaning": "Used directly in role percentiles"},
        {"code": "aggregate_executive", "label": "Aggregate, executive", "meaning": "Per-head average only; needs aggregate_headcount"},
        {"code": "individual_board", "label": "Individual, board", "meaning": "Board-fee benchmarks only; no STI or LTI"},
        {"code": "aggregate_board", "label": "Aggregate, board", "meaning": "Board-fee averages with headcount"}],
    "ref_pension_type": [{"code": c, "label": l} for c, l in [
        ("defined_contribution", "Defined contribution"), ("defined_benefit", "Defined benefit")]],
    "ref_period_coverage": [{"code": c, "label": l} for c, l in [("full_year", "Full year"), ("part_year", "Part year")]],
    "ref_holder_list_cutoff": [{"code": c, "label": l} for c, l in [
        ("top_10", "Ten largest holders"), ("top_20", "Twenty largest holders"), ("above_5pct", "All holders above 5%")]],
    "ref_share_count_basis": [{"code": c, "label": l} for c, l in [
        ("outstanding", "Shares outstanding"), ("issued", "Shares issued")]],
    "ref_pct_of": [{"code": c, "label": l} for c, l in [("base_salary", "% of base salary"), ("target_bonus", "% of target bonus")]],
    "ref_units": [{"code": c, "label": l} for c, l in [("units", "Units"), ("thousands", "Thousands"), ("millions", "Millions")]],
    "ref_source_type": [{"code": c, "label": l} for c, l in [
        ("annual_report", "Annual report"), ("remuneration_report", "Remuneration report"), ("lei_record", "GLEIF LEI record")]],
}
for rows in REF.values():
    for r in rows:
        r.setdefault("status", EXAMPLE)
        r.setdefault("list_source", EXAMPLE)

# ------------------------------------------------------------------ delivery tables
DIM_COMPANY = [
    dict(company_id="NVK", legal_name="Nordvik Kraft AB", lei="5493000NVK0EXAMPLE01", business_id="556000-0101",
         country_code="SE", head_office_city="Stockholm", website="nordvikkraft.example", isin="SE0000000101",
         ticker="NVK B", exchange="XSTO", exchange_segment="large_cap", listing_status="listed",
         listing_date=dt.date(2015, 6, 12), sector_code="35.11", sector_code_scheme="NACE",
         sub_sector="Generates and sells hydro and wind power in the Nordics."),
    dict(company_id="SRS", legal_name="Saarela Systems Oyj", lei="7437000SRS0EXAMPLE02", business_id="2000001-2",
         country_code="FI", head_office_city="Espoo", website="saarela.example", isin="FI0000000202",
         ticker="SAARELA", exchange="XHEL", exchange_segment="mid_cap", listing_status="listed",
         listing_date=dt.date(2018, 3, 20), sector_code="62.01", sector_code_scheme="NACE",
         sub_sector="Develops payroll and HR software for Nordic employers."),
    dict(company_id="FJM", legal_name="Fjordline Marine ASA", lei="5967000FJM0EXAMPLE03", business_id="900 000 303",
         country_code="NO", head_office_city="Bergen", website="fjordline-marine.example", isin="NO0000000303",
         ticker="FJM", exchange="XOSL", exchange_segment="mid_cap", listing_status="listed",
         listing_date=dt.date(2011, 10, 4), sector_code="50.20", sector_code_scheme="NACE",
         sub_sector="Operates ferry routes and offshore supply vessels on the Norwegian coast.",
         ultimate_parent="Kingdom of Norway"),
]

COMPANY_NAME_ALIAS = [
    dict(company_id="NVK", alias="Nordvik Energi AB"),          # former legal name
    dict(company_id="SRS", alias="Saarela Systems Abp"),        # Swedish-language parallel name
]

FACT_COMPANY_YEAR = [
    dict(company_id="NVK", fiscal_year=FY, fiscal_year_end=FY_END, reporting_currency="SEK", units="millions",
         accounting_basis="ifrs", revenue=18450, total_assets=52300, ebitda=6120, ebitda_basis="EBITDA",
         shares_outstanding=412_000_000, share_price=118.40, market_cap_band="large", headcount=2140, fte=2085),
    dict(company_id="SRS", fiscal_year=FY, fiscal_year_end=FY_END, reporting_currency="EUR", units="millions",
         accounting_basis="ifrs", revenue=286.4, total_assets=410.2, ebitda=52.7, ebitda_basis="EBITDA",
         shares_outstanding=38_500_000, share_price=21.60, market_cap_band="mid", headcount=1620, fte=1590),
    dict(company_id="FJM", fiscal_year=FY, fiscal_year_end=FY_END, reporting_currency="NOK", units="millions",
         accounting_basis="ifrs", revenue=7420, total_assets=21800, ebitda=2210, ebitda_basis="EBITDA",
         shares_outstanding=96_000_000, share_price=74.50, market_cap_band="mid", headcount=980, fte=1005),
]

_H = dict(share_count_basis="outstanding", list_cutoff="top_10")
COMPANY_HOLDER = [
    dict(company_id="NVK", fiscal_year=FY, holder_rank=1, holder_name="Lind Family Foundation", holder_type="family",
         capital_pct=22.0, votes_pct=36.5, holder_group="Lind family", is_tied=False, as_of_date=FY_END, **_H),
    dict(company_id="NVK", fiscal_year=FY, holder_rank=2, holder_name="Fjällgren Capital Fund IV", holder_type="private_equity",
         capital_pct=8.4, votes_pct=6.1, holder_group="Fjällgren Capital", is_tied=False, as_of_date=FY_END, **_H),
    dict(company_id="NVK", fiscal_year=FY, holder_rank=3, holder_name="Nordic Pension Fund", holder_type="institution",
         capital_pct=5.2, votes_pct=3.8, is_tied=False, as_of_date=FY_END, **_H),
    dict(company_id="NVK", fiscal_year=FY, holder_rank=4, holder_name="Halvorsen Invest AB", holder_type="institution",
         capital_pct=3.1, votes_pct=2.3, is_tied=False, as_of_date=FY_END, **_H),
    dict(company_id="SRS", fiscal_year=FY, holder_rank=1, holder_name="Kuusela Pension Insurance", holder_type="institution",
         capital_pct=11.8, votes_pct=11.8, is_tied=False, as_of_date=FY_END, **_H),
    dict(company_id="SRS", fiscal_year=FY, holder_rank=2, holder_name="Mikko Saarela", holder_type="family",
         capital_pct=9.5, votes_pct=9.5, holder_group="Saarela family", is_tied=False, as_of_date=FY_END, **_H),
    dict(company_id="SRS", fiscal_year=FY, holder_rank=3, holder_name="Arctic Growth Partners III", holder_type="private_equity",
         capital_pct=6.2, votes_pct=6.2, is_tied=False, as_of_date=FY_END, **_H),
    dict(company_id="SRS", fiscal_year=FY, holder_rank=4, holder_name="Lakeside Funds", holder_type="institution",
         capital_pct=4.0, votes_pct=4.0, is_tied=False, as_of_date=FY_END, **_H),
    dict(company_id="FJM", fiscal_year=FY, holder_rank=1, holder_name="Kingdom of Norway", holder_type="state",
         capital_pct=51.0, votes_pct=51.0, is_tied=False, as_of_date=FY_END, **_H),
    dict(company_id="FJM", fiscal_year=FY, holder_rank=2, holder_name="Havbris Holding AS", holder_type="family",
         capital_pct=12.3, votes_pct=12.3, holder_group="Havbris family", is_tied=False,
         as_of_date=dt.date(2025, 11, 30), **_H),   # different as-of date -> DER-07 review
    dict(company_id="FJM", fiscal_year=FY, holder_rank=3, holder_name="Nordsjø Pensjon", holder_type="institution",
         capital_pct=4.8, votes_pct=4.8, is_tied=False, as_of_date=FY_END, **_H),
]

COMPANY_BREAKDOWN = []
for cid, btype, metric, items in [
    ("NVK", "segment", "revenue", [("Hydro", 9800), ("Wind", 5200), ("Trading", 3450)]),
    ("NVK", "country", "revenue", [("Sweden", 12100), ("Norway", 4100), ("Finland", 2250)]),
    ("NVK", "country", "staff", [("Sweden", 1500), ("Norway", 420), ("Finland", 220)]),
    ("SRS", "segment", "revenue", [("Payroll SaaS", 190.0), ("HR services", 96.4)]),
    ("SRS", "country", "staff", [("Finland", 1100), ("Sweden", 380), ("Estonia", 140)]),
    ("FJM", "segment", "revenue", [("Ferries", 4100), ("Offshore supply", 3000)]),   # 7,100 vs 7,420 -> SEG-1 review
]:
    for item, val in items:
        COMPANY_BREAKDOWN.append(dict(company_id=cid, fiscal_year=FY, breakdown_type=btype, metric=metric,
                                      item_name=item, value=val))

FACT_PAY_POLICY = [
    dict(company_id="NVK", fiscal_year=FY, pension_type="defined_contribution", benefits="Company car, health insurance",
         shareholding_requirement="100% of base salary (CEO)"),
    dict(company_id="SRS", fiscal_year=FY, pension_type="defined_contribution", benefits="Phone, health insurance",
         shareholding_requirement="50% of base salary"),
    dict(company_id="FJM", fiscal_year=FY, pension_type="defined_benefit", benefits="Car allowance"),
]

# Pay lines: person_name is used only for the deterministic ID key (it is not stored; see open decisions).
PAY_LINES_SPEC = [
    # company, person, disclosure, role_code, line fields
    ("NVK", "Anna Lind", "individual_executive", "ceo", dict(
        role_title="President and CEO", months_in_role=12, period_coverage="full_year", pay_currency="SEK",
        units="thousands", base_salary=9200, token_salary=False, benefits_value=180, pension_contribution=2760,
        sti_paid=3100, total_remuneration=15240, is_aggregated=False)),
    ("NVK", "Erik Berg", "individual_executive", "ceo", dict(
        role_title="CEO (until 31 March 2025)", months_in_role=3, period_coverage="part_year", pay_currency="SEK",
        units="thousands", base_salary=2100, token_salary=False, benefits_value=40, pension_contribution=630,
        total_remuneration=2770, is_aggregated=False)),
    ("NVK", "", "aggregate_executive", "executive_team_aggregate", dict(
        role_title="Other members of group management", months_in_role=12, period_coverage="full_year",
        pay_currency="SEK", units="thousands", is_aggregated=True, aggregate_headcount=6, aggregate_excludes="CEO",
        base_salary=21400, benefits_value=620, pension_contribution=5350, sti_paid=5900, total_remuneration=33270)),
    ("NVK", "Karin Holm", "individual_board", "board_chair", dict(
        role_title="Chair of the board", months_in_role=12, period_coverage="full_year", pay_currency="SEK",
        units="thousands", is_aggregated=False, total_remuneration=1450)),
    ("NVK", "Anna Lind", "individual_board", "board_member", dict(
        role_title="Board member (CEO, no board fee)", months_in_role=12, period_coverage="full_year",
        pay_currency="SEK", units="thousands", is_aggregated=False, total_remuneration=0)),
    ("SRS", "Laura Saarinen", "individual_executive", "ceo", dict(
        role_title="CEO and acting CFO", months_in_role=12, period_coverage="full_year", pay_currency="EUR",
        units="units", base_salary=520000, token_salary=False, benefits_value=18000, pension_contribution=98000,
        sti_paid=140000, total_remuneration=790000, is_aggregated=False)),   # parts sum to 776,000 -> XF-01 fail
    ("SRS", "", "aggregate_executive", "executive_team_aggregate", dict(
        role_title="Other members of the management team", months_in_role=12, period_coverage="full_year",
        pay_currency="EUR", units="units", is_aggregated=True, aggregate_headcount=5, aggregate_excludes="CEO",
        base_salary=1140000, benefits_value=41000, pension_contribution=205000, sti_paid=260000,
        total_remuneration=1646000)),
    ("SRS", "Petri Ahola", "individual_board", "board_chair", dict(
        role_title="Chair of the board", months_in_role=12, period_coverage="full_year", pay_currency="EUR",
        units="units", is_aggregated=False, total_remuneration=98000)),
    ("FJM", "Ingrid Solheim", "individual_executive", "ceo", dict(
        role_title="CEO", months_in_role=12, period_coverage="full_year", pay_currency="NOK", units="thousands",
        base_salary=6400, token_salary=False, benefits_value=210, pension_contribution=1150, sti_paid=1900,
        total_remuneration=9660, is_aggregated=False)),
    ("FJM", "Henrik Dahl", "individual_executive", "cfo", dict(
        role_title="CFO", months_in_role=12, period_coverage="full_year", pay_currency="NOK", units="thousands",
        base_salary=3900, token_salary=False, benefits_value=150, pension_contribution=690, sti_paid=900,
        total_remuneration=5640, is_aggregated=False)),
    ("FJM", "Tor Eide", "individual_executive", "coo", dict(
        role_title="COO (Singapore office)", months_in_role=12, period_coverage="full_year", pay_currency="SGD",
        units="thousands", base_salary=410, token_salary=False, benefits_value=30, pension_contribution=60,
        sti_paid=0, total_remuneration=500, is_aggregated=False)),   # SGD in Norway -> CUR-1 review
    ("FJM", "Kari Nygaard", "individual_board", "board_chair", dict(
        role_title="Chair of the board", months_in_role=12, period_coverage="full_year", pay_currency="NOK",
        units="thousands", is_aggregated=False, total_remuneration=820)),
]

FACT_PAY_LINE, PAY_LINE_ROLE, PAY_LINE_TOTAL_COMPONENT, PERSON_OF_LINE = [], [], [], {}
for cid, person, disc, role, fields in PAY_LINES_SPEC:
    pid = role_line_id(cid, FY, disc, role, person)
    PERSON_OF_LINE[pid] = person or "(aggregate)"
    FACT_PAY_LINE.append(dict(pay_line_id=pid, company_id=cid, fiscal_year=FY, role_code=role, role_disclosure=disc, **fields))
    PAY_LINE_ROLE.append(dict(pay_line_id=pid, role_code=role, is_primary=True, role_order=1,
                              source_title="CEO" if fields["role_title"] == "CEO and acting CFO" else fields["role_title"]))
    if fields["role_title"] == "CEO and acting CFO":
        PAY_LINE_ROLE.append(dict(pay_line_id=pid, role_code="cfo", is_primary=False, role_order=2,
                                  source_title="acting CFO", start_date=dt.date(2025, 5, 1)))
    if fields.get("base_salary") is not None and role in ("ceo",):
        for comp in ("base_salary", "benefits_value", "pension_contribution", "sti_paid"):
            if fields.get(comp) is not None:
                PAY_LINE_TOTAL_COMPONENT.append(dict(pay_line_id=pid, component_field=comp))
    if role == "ceo" and fields.get("months_in_role") == 3:
        PAY_LINE_ROLE[-1]["end_date"] = dt.date(2025, 3, 31)

DIM_SOURCE = []
for c in COMPANIES:
    cid = c["company_id"]
    DIM_SOURCE += [
        dict(source_id=f"AR-2025-{cid}", company_id=cid, source_type="annual_report", fiscal_year=FY,
             title=f"{c['name']} Annual Report 2025", url=f"https://example.com/{cid.lower()}/annual-report-2025.pdf",
             gcs_path=f"gs://cdp-sources/2025/{cid}/AR-2025-{cid}.pdf", publish_date=dt.date(2026, 3, 18),
             language="en", retrieved_at=dt.datetime(2026, 11, 2, 9, 15)),
        dict(source_id=f"RR-2025-{cid}", company_id=cid, source_type="remuneration_report", fiscal_year=FY,
             title=f"{c['name']} Remuneration Report 2025", url=f"https://example.com/{cid.lower()}/remuneration-report-2025.pdf",
             gcs_path=f"gs://cdp-sources/2025/{cid}/RR-2025-{cid}.pdf", publish_date=dt.date(2026, 3, 18),
             language="en", retrieved_at=dt.datetime(2026, 11, 2, 9, 16)),
        dict(source_id=f"LEI-{cid}", company_id=cid, source_type="lei_record", fiscal_year=FY,
             title=f"GLEIF LEI record for {c['name']}", url="https://example.com/gleif/lei-record",
             language="en", retrieved_at=dt.datetime(2026, 11, 2, 9, 10)),
    ]
