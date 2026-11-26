# Decisions log

## Source suggestions (Step 2b)
One row per suggestion you accepted, rejected or revised, with your reason. Use the page's own wording for the reason.

| Suggestion (publisher, URL) | Need, window | Decision | Reason |
|---|---|---|---|
| S1: Our World in Data on GitHub (data: Health Effects Institute, State of Global Air 2017), https://github.com/owid/owid-datasets/blob/master/datasets/Absolute%20deaths%20from%20ambient%20PM2.5%20air%20pollution-%20State%20of%20Global%20Air/datapackage.json | N6, prototype | accept | Links are working, and the data looks validated and truatable. |
| S2: Our World in Data (IHME GBD), https://ourworldindata.org/grapher/absolute-number-of-deaths-from-ambient-particulate-air-pollution?tab=map | N6, prototype | accept | Links are working, and the data looks validated and truatable. |
| S3: European Environment Agency, https://sdi.eea.europa.eu/catalogue/srv/api/records/258fa83c-dec6-4d88-b1fb-959f2d90008f | N6, prototype | reject | Link not working, redirects to different website completely unrealted. |
| S4: Meteostat, station Milano/Linate (16080), https://meteostat.net/en/station/16080 | N3, prototype and production | accept | Links are working, and the data looks validated and truatable. |
| S5: NOAA NCEI, Integrated Surface Database (ISD), https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database | N3, prototype and production | accept | Links are working, and the data looks validated and truatable. |

Decisions and reasons dictated by the learner on 2026-11-26 and transcribed word for word by Claude. The learner also stated: "Inspected and checked the data".
The suggestions come from six searches with `scripts/web_search.py`, saved verbatim in `outputs/artifacts/step2b_searches_UC1.md`. The accepted links were appended to `outputs/UC1/links.json`, with the reason as `note`.

Host check (Step 2b item 5; manual `inspect_dataset_link` runs, saved in `outputs/artifacts/inspect_UC1_S*.txt`):
- S1: reachable. HTTP 200, `json_api`, resolved to `raw.githubusercontent.com` (`github.com` and `raw.githubusercontent.com` are both on the allowlist).
- S2: refused, `DOMAIN_NOT_ALLOWLISTED` for host `ourworldindata.org`.
- S4: refused, `DOMAIN_NOT_ALLOWLISTED` for host `meteostat.net`.
- S5: refused, `DOMAIN_NOT_ALLOWLISTED` for host `www.ncei.noaa.gov`.
- G6 decision for these three hosts: not added (see "G6: Allowlist changes").

Inspected through the workflow (at least one accepted extra source):

## G1 and G3: one edge case in each function
- **G1, `extract_licence`**: When the Kaggle page declares its licence as {"name":"Unknown","url":""}, the licence-detection function returns name: None and url: None, identifies the source as json-ld, and retains a snippet showing the original declaration. The search stops at this point because the function treats the JSON-LD declaration as an explicit licence result. It does not continue searching other parts of the page, so another licence mentioned elsewhere cannot override the "Unknown" declaration. The catalog record (`outputs/<ID>/records/<source_id>.json`) therefore stores licence.name as null rather than "Unknown". The Profiler must cite the found_in field for traceability, as specified in profiler.md:19. The LIC-UNKNOWN flag is raised as a blocker. Under the register's policy, datasets with unknown licences require Legal review before use. Other unresolved cases, including multiple conflicting licences, unrecognised licence descriptions, and licences found only in the footer, also result in LIC-UNKNOWN. In contrast, recognised licences such as CC BY 4.0 receive LIC-ATTRIBUTION where applicable, while ODbL, CC0, PDDL, MIT and Apache currently receive no flag. Review note: SA and ND licences currently receive only LIC-ATTRIBUTION. This potential policy gap belongs in rule_licence, not G1, and should be documented in the memo review.
- **G3, `jsonstat_summary`**: The edge case is a year that is absent entirely from the table. In UC1's Eurostat table (sdg_11_52, Italy), the available years are 2005 and then 2007 to 2023; 2006 is missing from the year list. This is based on the planning preview of 2026-11-18, as the real response can only be fetched after G6 adds ec.europa.eu.
  The code does not detect this gap as missing data. jsonstat_summary calculates the expected number of cells from the table dimensions: 2 units × 18 years = 36 cells. Since all 36 cells contain values, missing_cells is 0 and warnings is empty. The gap appears only in time.values, which jumps directly from 2005 to 2007. Consequently, time.first remains 2005 and time.last remains 2023.
  This affects the summary and the catalog record because the Profiler would record temporal.start as 2005-01-01 and temporal.end as 2023-12-31, hiding the missing year within the period. Since no existing rule flags the gap, the Profiler must explicitly document it in quality_notes.
  This is different from an empty latest year. For example, if 2024 is listed but every cell for that year is empty, the MISSING_CELLS warning fires, but time.last still reports 2024. The catalog record would therefore overstate the actual end of the available data, potentially concealing FRS-STALE or COV-PARTIAL-WINDOW issues.

## G4–G5: feasible for one need or window, not another
- Source and the rule or calibration decision:
- Feasible for (need, window), and why:
- Not feasible for (need, window), and why:
- Reason for each red flag you dismissed:

## G6: Allowlist changes
Exact hosts only. For each host: what it provides and why a broader domain is not needed.

| Host added | Needed for (source, page) | Why nothing broader | Date |
|---|---|---|---|
| | | | |

Hosts you chose **not** to add, and why:
- `ourworldindata.org` (S2), `meteostat.net` (S4), `www.ncei.noaa.gov` (S5): each refused with `DOMAIN_NOT_ALLOWLISTED` by `inspect_dataset_link` on 2026-11-26 (`outputs/artifacts/inspect_UC1_S2.txt`, `inspect_UC1_S4.txt`, `inspect_UC1_S5.txt`). Learner's decision, dictated on 2026-11-26 and transcribed word for word: "S2, S4, S5 :- don't add it. Reject all requests to S2, S4, S5."

## G5: Verdict calibration
- What you changed in `prompts/risk_assessor.md`, and the reasoning behind each rule:
- Verdicts that changed after you re-ran `--from-stage assess` (source: before → after, why):

## G7: One agent failure, fixed at its cause
- **Symptom** (what was wrong in the output):
- **Evidence** (trace event or transcript excerpt, with file and line or turn):
- **Root cause** (prompt, tool description, validator, rule, or missing tool):
- **Fix** (file and diff summary):
- **Re-run** (command):
- **Before / after** (measured: e.g. candidates found, flags raised, verdict, tokens, tool calls):
- **Decision this failure could affect:**
- **Related source or test checked:**

## Other decisions
- **Open-Meteo location (assumption):** Milan, Italy (45.46° N, 9.19° E) is selected as the study city. Milan was chosen because it is located in the Po Valley, a region that frequently experiences poor air quality, particularly during periods of atmospheric stagnation. The city also experiences hot summers, making it suitable for examining both air pollution and heat-related weather conditions using a single weather setting. Milan is therefore selected as the assumed location for the fictional client, Valdena, for the purposes of both UC1 and UC2, without making any assumptions about the unknown origin of the UCI prototype dataset. *(The learner's answer to worksheet B4, transcribed word for word on 2026-11-26. The coordinates are set in `config/external_sources_register.json`, `api.open_meteo_archive.default_query`, commit `6e7da42`.)*
