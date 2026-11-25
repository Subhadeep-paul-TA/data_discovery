# Decisions log

## Source suggestions (Step 2b)
One row per suggestion you accepted, rejected or revised, with your reason. Use the page's own wording for the reason.

| Suggestion (publisher, URL) | Need, window | Decision | Reason |
|---|---|---|---|
| S1: Our World in Data on GitHub (data: Health Effects Institute, State of Global Air 2017), https://github.com/owid/owid-datasets/blob/master/datasets/Absolute%20deaths%20from%20ambient%20PM2.5%20air%20pollution-%20State%20of%20Global%20Air/datapackage.json | N6, prototype | accept | Links are working, and the data looks validated and truatable. |
| S2: Our World in Data (IHME GBD), https://ourworldindata.org/grapher/absolute-number-of-deaths-from-ambient-particulate-air-pollution?tab=map | N6, prototype | accept | Links are working, and the data looks validated and truatable. |
| S3: European Environment Agency, https://sdi.eea.europa.eu/catalogue/srv/api/records/258fa83c-dec6-4d88-b1fb-959f2d90008f | N6, prototype | reject | *(no reason given yet; asked on 2026-11-26)* |
| S4: Meteostat, station Milano/Linate (16080), https://meteostat.net/en/station/16080 | N3, prototype and production | accept | Links are working, and the data looks validated and truatable. |
| S5: NOAA NCEI, Integrated Surface Database (ISD), https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database | N3, prototype and production | accept | Links are working, and the data looks validated and truatable. |

Decisions and reasons dictated by the learner on 2026-11-26 and transcribed word for word by Claude. The learner also stated: "Inspected and checked the data".
The suggestions come from six searches with `scripts/web_search.py`, saved verbatim in `outputs/artifacts/step2b_searches_UC1.md`. The accepted links were appended to `outputs/UC1/links.json`, with the reason as `note`.

Host check (Step 2b item 5; manual `inspect_dataset_link` runs, saved in `outputs/artifacts/inspect_UC1_S*.txt`):
- S1: reachable. HTTP 200, `json_api`, resolved to `raw.githubusercontent.com` (`github.com` and `raw.githubusercontent.com` are both on the allowlist).
- S2: refused, `DOMAIN_NOT_ALLOWLISTED` for host `ourworldindata.org`.
- S4: refused, `DOMAIN_NOT_ALLOWLISTED` for host `meteostat.net`.
- S5: refused, `DOMAIN_NOT_ALLOWLISTED` for host `www.ncei.noaa.gov`.
- G6 decision for these three hosts: pending (the learner decides; see "G6: Allowlist changes").

Inspected through the workflow (at least one accepted extra source):

## G1 and G3: one edge case in each function
- **G1, `extract_licence`**: the edge case, what the code does with it, and how it changes the `licence` field:
- **G3, `jsonstat_summary`**: the edge case, what the code does with it, and how it changes the summary:

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
