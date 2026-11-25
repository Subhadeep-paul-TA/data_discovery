> Deep-review report written 2026-11-18 by a review agent, for work.md (same folder, one level up).
> It is READ-ONLY analysis of the provided starter code. Paths under /tmp/.../scratchpad mentioned below were temporary and no longer exist.
> Facts marked [V] were verified by reading or running the code; [I] are inferences. Live-site facts were observed on 2026-11-18 and may change.

# Gap G6 (config/allowlist.json minimal exact hosts; -k g6; TC-016, TC-017) + live no-LLM inspection of the UC1 dataset links

## SUMMARY
The smallest G6 change is one line: add `ec.europa.eu` to config/allowlist.json. The Eurostat link, its metadata page and the Eurostat copyright notice all live on that host (checked live). UCI 360 needs nothing new, because its API, page, data.csv and zip are all on `archive.ics.uci.edu`, which is already listed. The Chicago host `catalog.data.gov` must never be added. In a scratch copy, adding only that line turns `-k g6` from 1 fail / 1 pass into 2 passes, and the full suite goes from 32 to 33 passing. `host_allowed()` matches a host and all its subdomains, and an existing test requires that. So the matcher and the six existing entries should be left alone. 'Exact host' means listing the full host name you need, never a shorter parent such as `europa.eu`. Live checks also turned up several things for the plan. The UCI page says CC BY 4.0, but the dataset's own notes say research use only. `sample_data_file` misses the `-200.0` spelling of the -200 code. Eurostat covers only 2005–2023 (2006 is absent), so the production window has no data, and the upstream provider is EEA, which may limit commercial reuse. The Nager docs URL redirects to a host that is not allowlisted. The biggest trap: outputs/<ID>/trace.jsonl is append-only, and `check` fails once any refused URL appears more than twice. So profile the Chicago link only once, and use `--only` for every re-run.

## DETAILS
# G6 allowlist + live UC1 link inspection (no LLM)

All live observations were made on **2026-11-18** in a scratch copy (`.../scratchpad/work-g6`), never in the bundle. The bundle and the baseline are unchanged (the allowlist checksum is identical and neither has a `.cache/`). I made 17 live GETs in total and no LLM calls. Every number below marked "observed" came from those runs. Live sites change, so re-check before you cite anything.

## 0. Bottom line
- **The smallest G6 change is one host: `ec.europa.eu`.** Nothing else is needed for the three prescribed UC1 links.
- In the scratch copy, adding exactly that line gives `pytest tests/test_learner_gaps.py -k g6` → `2 passed` (baseline: `1 failed, 1 passed`), and `pytest tests/ -q` → 33 passed / 19 failed (baseline 32/20).
- Do **not** edit `host_allowed()` or remove or broaden the six existing entries.
- The biggest practical risk is not the allowlist itself. `outputs/UC1/trace.jsonl` is **append-only** (trace.py:41, orchestrator.py:70), and `check` reports `guardrail: refused URL retried {n} times (...)` whenever one refused URL appears **more than 2 times across all runs** (validation.py:205-210). Profile the Chicago link once, and use `--only` for every re-run.

## 1. How the guardrail behaves (code facts)
| Behaviour | Where | Consequence |
|---|---|---|
| Match = `host == d or host.endswith("." + d)`, case-insensitive, trailing dot stripped | http_client.py:56-58 | Every entry also admits its subdomains. `ec.europa.eu` admits `webgate.ec.europa.eu`, but NOT `europa.eu` or `commission.europa.eu`. `tests/test_tools_offline.py:18-22` *requires* subdomain matching, so do not "fix" it |
| Scheme must be https, IP literals refused, host must match | http_client.py:61-74 | Codes `SCHEME_NOT_ALLOWED`, `IP_LITERAL_REFUSED`, `DOMAIN_NOT_ALLOWLISTED` |
| Redirects re-checked on every hop | http_client.py:77-83, 156-158 | Trace says `"refused": "REDIRECT_NOT_ALLOWLISTED"`; tool payload says `DOMAIN_NOT_ALLOWLISTED: host '<target>'` |
| Budget: counter increments **after** the allowlist and cache checks | http_client.py:130-143 | A refusal costs **0** requests and a cache hit costs 0. A **redirect** refusal costs **1** (observed) |
| Cache writes only `status == 200` with no error; key = sha256(`url|max_bytes`) | http_client.py:103-118 | 404s and refusals are never cached and are retried live on re-runs. The same URL fetched with a different `max_bytes` is a new request (inspect = 1.5 MB, `summarize_jsonstat` = 5 MB, `probe_url` = 2 MB) |
| GET only, byte cap = min(requested, 5,000,000) | http_client.py:129,145 | |
| `python -m discovery_agent tool ...` uses `Trace(None)`; exit code 1 when the tool fails | cli.py:80,85 | Manual CLI inspections are **not** in `outputs/UC1/trace.jsonl`, so they do not count toward `check`, but TC-017 still says "not more than twice" |
| The gate warns `WARNING: <host> is not in config/allowlist.json...` | orchestrator.py:163-169 | Expected for Chicago on every gate run |

## 2. (a) Minimal hosts for the three UC1 links
| Link (source_id) | Hosts it actually needs (observed) | Already allowlisted? | Justification to adapt |
|---|---|---|---|
| UCI 360 (`link.uci_360`) | `archive.ics.uci.edu`: `/api/dataset?id=360`, `/dataset/360/air+quality`, `/static/public/360/data.csv`, `/static/public/360/air+quality.zip` | Yes | "The UCI API, landing page and both files are served from archive.ics.uci.edu; no other host is fetched (the CC BY licence is read from the link URL on the page, not fetched)." |
| Eurostat (`link.europa_sdg_11_52_099aa6`) | `ec.europa.eu`: the JSON-stat API, the reference metadata page `/eurostat/cache/metadata/en/sdg_11_52_esmsip2.htm`, and the copyright notice `/eurostat/en/help/copyright-notice` | **No → add it (G6)** | "ec.europa.eu serves the link, its documentation and its terms page. `europa.eu` would admit every EU institution site (commission., eur-lex., www.eea. …) and is rejected by test_g6_allowlist_not_wildcarded." |
| Chicago (`link.data_open_air_chicago_hour_aggre_d4970b`) | `catalog.data.gov` (and its file hosts, which are unknown because the page is refused) | No, and **never add it** | The refusal is the finding (assignment doc line 68; Helper Guide line 105; TC-017). |

## 3. (b) Hosts to list as "chose not to add"
| Host | Where it shows up | Reason not to add |
|---|---|---|
| `catalog.data.gov` (and `data.gov`) | Chicago link | Forbidden by the spec. The refusal is the finding. `data.gov` would also be a parent domain |
| Chicago's data-file host(s) | not knowable | The landing page is refused. Do not look for "another route" (http_client.py:73 message; `_shared_rules.md:8`) |
| `europa.eu` | parent of ec. | Explicitly banned by test_learner_gaps.py:173; far too broad |
| `www.ec.europa.eu` | — | Not used. The suffix matching would admit it anyway |
| `commission.europa.eu` | Footer "Legal notice" on the Eurostat pages. `https://ec.europa.eu/info/legal-notice_en` **301-redirects there and is refused** (observed, costs 1 request) | The Eurostat-specific copyright notice on ec.europa.eu already gives the reuse terms |
| `eur-lex.europa.eu` | The copyright notice links Decision 2011/833/EU | Legal background only; not needed for discovery |
| `www.eea.europa.eu` | The metadata page links the EEA datahub (upstream provider) | Not needed to profile the link. **Your call**: reading EEA's own terms bears on the commercial-reuse exception (see §5) |
| `creativecommons.org` | Licence links on the UCI page and the Eurostat notice | The licence is identified from the URL/text; nothing needs to be fetched |
| `doi.org` | DOIs `10.24432/C59K5F` (UCI), `10.2908/SDG_11_52` (Eurostat) | Resolver only; redirects to pages already reachable |
| `nagerholidays.com` | Register `docs_url` `https://date.nager.at/Api` **301 → `https://nagerholidays.com/Api`, refused** (observed) | The docs are not needed. Terms are on github.com and the API answers on date.nager.at |
| `api.atmosdata.example` | Expired vendor feed (UC1 only) | `call_public_api` refuses vendor feeds before any HTTP (public_api.py:38-42) |
| semanticscholar, nsf.gov, cml.ics.uci.edu, googletagmanager | Links on the UCI page | Not needed |

## 4. (c) The existing entries: leave them alone
| Entry | Used by (observed) | Note |
|---|---|---|
| `archive.ics.uci.edu` | UCI API, page and files | Needed |
| `archive-api.open-meteo.com` | Register endpoint (200) | Redundant, because `open-meteo.com` already admits it through suffix matching. Harmless and self-documenting |
| `open-meteo.com` | `docs_url` and `terms_url` (`/en/licence`) both 200, no redirect | A registrable domain, so it admits every `*.open-meteo.com`. That is the price of the matcher, not a learner addition |
| `date.nager.at` | `/api/v3/PublicHolidays/2025/IT` → 200 | Its `/Api` docs page redirects off-list (see §3) |
| `github.com` | Nager `terms_url` → 200 (shows "MIT license") | Also admits gist./api./docs.github.com |
| `raw.githubusercontent.com` | Only for GitHub blob links (`github_raw()`, links.py:42-44) and possibly LICENSE files | Not used by the prescribed links. Provided for "your own links" |

Recommendation: **do not touch them.** Only *added* hosts need a justification (rubric Governance row, TC-016). Removing `open-meteo.com` or `github.com` would make the register terms unreadable (→ LIC-UNKNOWN in both use cases). TC-025 compares config against the provided copy. One optional sentence in decisions.md is enough: "pre-existing entries left as provided; the matcher admits subdomains, so `archive-api.open-meteo.com` is redundant with `open-meteo.com`."

## 5. (d) Live findings per link (scratch copy)
### UCI 360: `link_type: uci_dataset_page`
- Hosts: `archive.ics.uci.edu` only. Two GETs (API 6,242 B with `content-type: text/plain`; page 132,964 B), no redirects. `files`: `.../static/public/360/air+quality.zip` and `.../static/public/360/data.csv`. `next_steps`: `sample_data_file on .../data.csv`. Licence: `"note": "extract_licence is a learner TODO (G1)..."`.
- Licence and terms on the page: **no JSON-LD**. There is a link to `https://creativecommons.org/licenses/by/4.0/legalcode` and the text "This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license". **But** the dataset summary says "This dataset can be used exclusively for research purposes. Commercial purposes are fully excluded." This is a licence conflict for you and the Risk Assessor. G1 will report CC BY 4.0, so `rule_licence` alone raises only LIC-ATTRIBUTION. The register policy also says non-commercial terms need Legal review.
- Coverage: the notes say "March 2004 to February 2005", but `data.csv` actually runs **2004-03-10 18:00 → 2005-04-04 14:00**, which matches the prototype window exactly. The city is never named ("an Italian city"). `metadata_last_updated: "Sun Mar 10 2024"` is the page date, not a data date. Donated 3/22/2016; created 2008.
- Contradictions: the API says `has_missing_values: "no"`, the page says "Has Missing Values? Yes", and the notes say "Missing values are tagged with -200 value." `variable_info` says `Date (DD/MM/YYYY)`, but data.csv uses M/D/YYYY. The API says `num_instances` 9358, but data.csv has 9,357 rows. The PT08.* sensor columns are typed "Categorical".
- `sample_data_file` (1 GET): plain CSV (not a zip), 741,211 B, `sample_is_whole_file: true`, 15 columns, 9,357 rows. The `-200` counts it reports: CO(GT) 1592, NMHC(GT) 8443 (only 9.8% non-missing), NOx(GT) 1639, NO2(GT) 1642, and 366 each for the sensor columns and T/RH/AH. **It misses `-200.0`**: C6H6(GT) is reported as `non_missing_share: 1.0`, `sentinel_counts: {}` with `min: -200.0` and `negative_count: 366`, and CO(GT) misses 91 `-200.0` values (true total 1683). The cause is the exact-string `SENTINELS` (links.py:33,103). This is a good G7 candidate.
- Likely flags (my inference; the decision is yours or the agent's): DQ-SENTINEL-VALUES, DQ-METADATA-CONTRADICTION, FRS-STALE (the G4 test expects exactly this for 2004-03-10..2005-04-04), FRS-METADATA-DATE-MISLEADING, LIC-ATTRIBUTION plus a research-only concern, and possibly INT-REPRESENTATIVENESS (single device) or COV-GEO-MISMATCH (unnamed city). It also contains T/RH/AH, which is relevant to N3 even though the link was given for N1.

### Eurostat `sdg_11_52` (IT)
- Before G6: `{"error": "DOMAIN_NOT_ALLOWLISTED", "message": "DOMAIN_NOT_ALLOWLISTED: host 'ec.europa.eu' is not on config/allowlist.json. Do not try another route to it; record the source as unreachable and say which host would need approval."}`, CLI exit 1, 0 requests.
- After adding `ec.europa.eu` (scratch only): `link_type: json_stat`, `source_id: link.europa_sdg_11_52_099aa6`, 1 GET, 200, 5,827 B, `application/json`, no `last-modified`, no redirect, `"note": "jsonstat_summary is a learner TODO (G3)..."` (with ok=true). **Re-run after G3** to get the summary.
- Content (stdlib read of the cached response): label "Premature deaths due to exposure to fine particulate matter (PM2.5)"; `source: ESTAT`; `updated: 2025-12-09T11:00:00+0100`. Dimensions `freq(1: A) · airpol(1: PM2_5) · effect(1: PMD) · unit(2: NR Number, RT Rate) · geo(1: IT) · time(18)`. Time = **2005, 2007–2023 (2006 absent)**. `expected_cells` 36, values 36, missing 0, no `status`. G3 should therefore give `warnings: []`, but the 2006 gap is a *missing category*, not a missing cell, which is a good G3 edge case to write up. Italy NR: 70,924 (2005) → 43,083 (2023); RT: 122 → 73.
- Metadata page: "deaths attributable to long-term exposure to concentrations of PM2.5 above 5µg/m3 (the World Health Organization's guideline level)". Units: "Total number..." and "per 100 000 people". Source data "EEA/European Topic Centre on Health and Environment". Timeliness "T+2 years". "Data for 2006 is missing because there are no interpolated PM2.5 maps for that year." Copyright: "Eurostat Copyright/Licence Policy is applicable."
- Coverage against the windows: the prototype window (2004-03-10..2005-04-04) overlaps only through the 2005 annual figure. The production window (2024–2025) has **no data** (latest 2023; T+2). That points to COV-PARTIAL-WINDOW, the same pattern as `test_g4_partial_window_across_two_windows` (2005-01-01..2023-12-31, annual). The `updated` field is a release timestamp, not the end of the data period.
- Terms: the copyright notice allows reuse "for commercial or non-commercial purposes ... provided the source is acknowledged". **Exception:** "Data identified as belonging to sources other than Eurostat" may not be reused commercially. The JSON-stat response names `SOURCE_INSTITUTIONS: European Environment Agency (EEA)`. Whether that exception applies is your judgement or a question for Legal (LIC-ATTRIBUTION vs LIC-MIXED, or a condition).

### Chicago: refused, no link type detected
README:81 says the agent "should detect" a "Public landing page", but with the host refused it never can. Expect `access.reachable=false` → ACC-UNREACHABLE (blocker, from `rule_access`), probably LIC-UNKNOWN as well, and your judgement on geography (the link note says "a US city").

## 6. (e) Chicago refusal (run exactly once, through `execute()`, the same code path as the CLI)
```
{
  "error": "DOMAIN_NOT_ALLOWLISTED",
  "message": "DOMAIN_NOT_ALLOWLISTED: host 'catalog.data.gov' is not on config/allowlist.json. Do not try another route to it; record the source as unreachable and say which host would need approval."
}
```
It consumed **0** budget requests, made no DNS or TCP connection, and wrote nothing to the cache. CLI exit code 1 (observed on the identical Eurostat refusal path). In a pipeline run the trace line will be `{"kind": "http", "agent": "profiler__link.data_open_air_chicago_hour_aggre_d4970b", "url": "https://catalog.data.gov/dataset/open-air-chicago-hour-aggregations", "refused": "DOMAIN_NOT_ALLOWLISTED"}`. `check` lists it under `refused_hosts` (validation.py:204), which is your evidence for review_UC1.md.

## 7. (f) Settings and budget
`timeout_s 25`, `max_bytes_default 2,000,000`, `max_bytes_hard_cap 5,000,000`, `max_requests_per_run 150` (settings.json:3-8). Do not change any of them (TC-025). The budget is per HttpClient, meaning per `run` or per `tool` invocation, shared by the 4 parallel profilers under a lock. My estimate for a fresh full UC1 run (inference, not measured) is about 12–25 live requests: UCI 3-4, Eurostat 3-4 (inspect plus summarize_jsonstat use different cache keys), Open-Meteo 3-5, Nager 3-5 (the docs redirect costs 1), Chicago 0, internal and vendor 0. Exhausting 150 would take a looping agent (10 sources × 16 profiler turns is the theoretical ceiling). `REQUEST_BUDGET_EXHAUSTED` would be a finding or a G7 candidate, never a reason to raise the cap. Minor quirk: `probe_url`'s schema says the default is 1,500,000, but the code applies 2,000,000 (probe.py:25 vs 28).

## 8. (g) Eurostat pages to read (in your browser, which the allowlist does not restrict)
- Metadata (ESMS): `https://ec.europa.eu/eurostat/cache/metadata/en/sdg_11_52_esmsip2.htm`: **verified 200**
- Copyright notice: `https://ec.europa.eu/eurostat/en/help/copyright-notice`: **verified 200**
- Data browser: `https://ec.europa.eu/eurostat/databrowser/view/sdg_11_52/default/table?lang=en`: **verified 200**, but it is a JS app (the tool sees only "You are using an outdated browser"), so read it in a browser
- Info note PDF (from the API annotations): `https://ec.europa.eu/eurostat/databrowser-backend/api/public/explanatory-notes/get/Info_note_SDG_20260528.pdf`: **to verify** (not fetched)
- DOI `https://doi.org/10.2908/SDG_11_52` and the EEA datahub page: **to verify** (other hosts)
- Dead links: `https://ec.europa.eu/eurostat/about-us/policies/copyright` returns **404**. The metadata page links `http://ec.europa.eu/eurostat/statistics-explained/index.php/Copyright/licence_policy`, which the tool refuses with `SCHEME_NOT_ALLOWED`; its https form redirects on the same host to Statistics Explained `Main_Page`.

All three key pages are on `ec.europa.eu`, so no second host is needed.

## 9. Register probes (no vendor feed)
- `list_external_register`: UC1 = policy, open_meteo, nager, `vendor.atmosdata_pro` (expired). UC2 = the same minus the vendor.
- Open-Meteo with the default query → 200 from `archive-api.open-meteo.com`, grid `38.69947, -9.196167` (Lisbon, elevation 64 m), 2014-01-01..03, 72 hourly stamps. Both briefs say "The register's default (Lisbon) is not the client's location". Changing lat/lon is the **one allowed config edit**, and choosing the location is your decision, to be logged in decisions.md.
- Nager `PublicHolidays/2025/IT` → 200 from `date.nager.at`, 13 holidays, 2025-01-01..2025-12-26.

## 10. Order of work and ownership
1. **Task 4 (before G6), learner_with_claude_help.** Claude runs `inspect_dataset_link` on UCI (OK), Eurostat (refused) and Chicago (refused, **once**), and saves the outputs to `outputs/artifacts/inspect_*.txt`. Reuse the Chicago output for TC-017 rather than re-running it. You read the Eurostat pages in §8.
2. **G6 edit, claude_then_learner_review**, and only after you explicitly say "add ec.europa.eu" (CLAUDE.md rule). One line, then `-k g6` and the full suite, then review `git diff config/allowlist.json`.
3. **decisions.md G6 section, learner.** Claude can pre-fill the URLs and evidence. You write the "why nothing broader" reasons and the not-added list in your own words.
4. **Re-inspect Eurostat after G3**, then you write the gate reason. Accept Chicago on purpose, with your own reason.
5. **After runs, claude.** Audit refused events per URL in both traces and run `check`. Use `--only` (without `--links-file`, `candidates_final.json` is reused) for any re-profiling that should skip Chicago.

### Draft evidence row (rewrite the reason yourself)
`| ec.europa.eu | link.europa_sdg_11_52_099aa6: JSON-stat API .../statistics/1.0/data/sdg_11_52?format=JSON&lang=EN&geo=IT; metadata .../cache/metadata/en/sdg_11_52_esmsip2.htm; terms .../eurostat/en/help/copyright-notice | <your words: why not europa.eu / why no second host> | <date> |`

## FACTS
- [V] host_allowed() matches the exact host OR any subdomain of an entry (suffix match), case-insensitive, trailing dot stripped. :: starter-code/discovery_agent/tools/http_client.py:56-58 `return any(host == d or host.endswith("." + d) for d in allowlist)`; tested live: with ec.europa.eu listed, webgate.ec.europa.eu and www.ec.europa.eu are allowed, europa.eu and commission.europa.eu are not.
- [V] Subdomain matching is required by an offline test, so the matcher must not be changed to exact-only. :: tests/test_tools_offline.py:18-22 asserts host_allowed("api.open-meteo.com", ["open-meteo.com"]) is True.
- [V] The G6 tests require ec.europa.eu to be allowed and forbid any '*' entry, any entry without a dot, and the entries com/org/eu/europa.eu/github.io. :: tests/test_learner_gaps.py:164-173.
- [V] On the baseline, -k g6 gives 1 failed (test_g6_supplementary_hosts_allowlisted[ec.europa.eu]) and 1 passed. Adding only "ec.europa.eu" gives 2 passed, and the full suite goes to 33 passed / 19 failed. :: pytest -p no:cacheprovider run in scratchpad/baseline (read-only) and in scratchpad/work-g6 after a one-line allowlist edit.
- [V] Allowlist and scheme refusals happen before the budget counter increments, so they consume 0 requests and never touch the network. :: http_client.py:130-143 (_check_url, then cache, then the _count increment). Observed: budget counter '0 of 150' for the Chicago and pre-G6 Eurostat refusals.
- [V] A redirect to a non-allowlisted host consumes 1 budget request. The trace logs refused=REDIRECT_NOT_ALLOWLISTED while the tool payload reports DOMAIN_NOT_ALLOWLISTED for the redirect target. :: http_client.py:139-158. Observed with https://date.nager.at/Api (301 to https://nagerholidays.com/Api) and https://ec.europa.eu/info/legal-notice_en (redirects to https://commission.europa.eu/legal-notice_en): budget '1 of 150'.
- [V] The HTTP cache stores only status-200, error-free responses, keyed by sha256(url|max_bytes). Refused or 404 responses are re-requested on every run, and the same URL with a different max_bytes is a separate live request. :: http_client.py:103-105 and 116-118. The cache listing in work-g6 holds only 200 entries; the 404 and refused URLs are absent.
- [V] `python -m discovery_agent tool` writes no trace (Trace(None)) and exits 1 when the tool fails, for example on a refusal. :: cli.py:80 and 85. Observed exit=1 for the Eurostat refusal via the real CLI.
- [V] outputs/<ID>/trace.jsonl is append-only across all runs, and `check` errors when one refused URL appears more than 2 times. :: trace.py:41 open("a"); orchestrator.py:70 Trace(self.out / "trace.jsonl"); validation.py:205-210 `if n > 2: errs.append(f"guardrail: refused URL retried {n} times ({url}); ...")`.
- [V] Exact Chicago refusal: {"error": "DOMAIN_NOT_ALLOWLISTED", "message": "DOMAIN_NOT_ALLOWLISTED: host 'catalog.data.gov' is not on config/allowlist.json. Do not try another route to it; record the source as unreachable and say which host would need approval."} :: scratchpad/g6-runs/run4_chicago_refused.out (single run). Trace event refused=DOMAIN_NOT_ALLOWLISTED, budget 0.
- [V] The pipeline source ids are link.uci_360, link.europa_sdg_11_52_099aa6 and link.data_open_air_chicago_hour_aggre_d4970b. :: link_source_id() evaluated on links/UC1_example_links.json in baseline.
- [V] UCI 360 inspection: link_type uci_dataset_page. It contacts only archive.ics.uci.edu (API 6,242 B, page 132,964 B) with no redirects, and lists files .../static/public/360/data.csv and .../air+quality.zip. :: scratchpad/g6-runs/run2_uci360.out plus cache metadata.
- [V] The UCI 360 page states CC BY 4.0 (link to creativecommons.org/licenses/by/4.0/legalcode plus text) and has no JSON-LD, while the dataset summary says 'This dataset can be used exclusively for research purposes. Commercial purposes are fully excluded.' :: Stdlib scan of the cached page HTML: 0 ld+json blocks; quoted text.
- [V] UCI 360 metadata contradicts itself: the API says has_missing_values 'no', the page says 'Has Missing Values? Yes', and the notes say 'Missing values are tagged with -200 value.' :: inspect_dataset_link metadata.declared plus page text.
- [V] UCI data.csv is a plain CSV (not a zip) of 741,211 bytes, read in full: 9,357 rows by 15 columns, dates 2004-03-10 to 2005-04-04 in M/D/YYYY. The documentation says 'March 2004 to February 2005', 'Date (DD/MM/YYYY)' and 9358 instances. :: scratchpad/g6-runs/run6_uci360_sample.out plus a stdlib recount of the cached body.
- [V] sample_data_file misses the '-200.0' sentinel spelling: C6H6(GT) is reported non_missing_share 1.0 with sentinel_counts {} although 366 rows are -200.0, and CO(GT) is undercounted by 91 (1592 reported vs 1683 actual). :: links.py:33 (SENTINELS exact strings) and 103-104. Stdlib recount of the cached data.csv.
- [V] After allowlisting (scratch copy), the Eurostat link resolves as link_type json_stat in 1 GET (200, 5,827 B, application/json, no redirect). The payload carries note 'jsonstat_summary is a learner TODO (G3)...' with ok=true. :: scratchpad/g6-runs/run5_eurostat_allowed.out.
- [V] Eurostat sdg_11_52 for IT: label 'Premature deaths due to exposure to fine particulate matter (PM2.5)', updated 2025-12-09T11:00:00+0100. Dimensions freq/airpol/effect/unit(NR,RT)/geo(IT)/time with sizes [1,1,1,2,1,18]. Time covers 2005 and 2007-2023 (2006 absent), 36 of 36 cells present, no status field. :: Stdlib analysis of the cached JSON-stat body in work-g6/.cache/http.
- [V] Eurostat metadata: deaths attributable to PM2.5 above 5 µg/m3 (WHO guideline), units are the number of deaths and deaths per 100 000 people, data provider is EEA, timeliness is T+2 years, and 2006 is missing because there are no interpolated PM2.5 maps for that year. :: probe of https://ec.europa.eu/eurostat/cache/metadata/en/sdg_11_52_esmsip2.htm (200); text quoted from sections 4.1, 4.2, 4.5, 5.2 and 6.3.
- [V] The Eurostat copyright notice at https://ec.europa.eu/eurostat/en/help/copyright-notice allows commercial and non-commercial reuse with source acknowledgement. It excludes commercial reuse of 'Data identified as belonging to sources other than Eurostat'. :: probe_url returned 200; text quoted from the cached page.
- [V] The metadata page's copyright link is http:// and is refused with SCHEME_NOT_ALLOWED. Its https form redirects on the same host to Statistics Explained Main_Page, and https://ec.europa.eu/eurostat/about-us/policies/copyright returns 404. :: scratchpad/g6-runs/probe_*.out.
- [V] The Open-Meteo register default query points at Lisbon (grid 38.69947, -9.196167) for 2014-01-01..03, which matches neither use case's location nor windows. :: call_public_api probe (200, archive-api.open-meteo.com). use_cases/UC1_air_quality.md:19 and UC2_ice_cream.md:18 say to choose an Italian location.
- [V] The register terms and docs pages for Open-Meteo (open-meteo.com) and Nager (github.com/nager/Nager.Date, 'MIT license') return 200 on already-allowlisted hosts. The Nager docs_url redirects off the allowlist. :: probe_url runs in work-g6. curl -I https://date.nager.at/Api shows 'HTTP/2 301 location: https://nagerholidays.com/Api'.
- [I] A fresh full UC1 run should make about 12-25 live HTTP requests, well under the 150-request budget. :: Estimate from the per-tool request counts observed above and the agent toolsets (agents.py:8-11); not measured with a real pipeline run.

## TASKS
- **Task 4 pre-G6: inspect the three UC1 links without the LLM and save the outputs** (learner_with_claude_help) done_when: Four saved outputs exist: UCI inspection OK, Eurostat DOMAIN_NOT_ALLOWLISTED, Chicago DOMAIN_NOT_ALLOWLISTED, UCI sample. Chicago has been inspected via the CLI exactly once.
    - Claude runs inspect_dataset_link for UCI 360, Eurostat and Chicago, each exactly once, and saves each output under outputs/artifacts/.
    - For UCI, also run sample_data_file on https://archive.ics.uci.edu/static/public/360/data.csv and save the output.
    - The learner reads each output and notes link_type, refusals with their exact codes, coverage, licence evidence and files.
    - Reuse the saved Chicago output as the 'actual output' for rubric TC-017 instead of running it again.
    - `python -m discovery_agent tool inspect_dataset_link '{"url": "https://archive.ics.uci.edu/dataset/360/air+quality"}' --use-case UC1 > outputs/artifacts/inspect_link.uci_360.txt 2>&1`
    - `python -m discovery_agent tool sample_data_file '{"url": "https://archive.ics.uci.edu/static/public/360/data.csv"}' --use-case UC1 > outputs/artifacts/sample_link.uci_360.txt 2>&1`
    - `python -m discovery_agent tool inspect_dataset_link '{"url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sdg_11_52?format=JSON&lang=EN&geo=IT"}' --use-case UC1 > outputs/artifacts/inspect_eurostat_before_g6.txt 2>&1`
    - `python -m discovery_agent tool inspect_dataset_link '{"url": "https://catalog.data.gov/dataset/open-air-chicago-hour-aggregations"}' --use-case UC1 > outputs/artifacts/inspect_chicago_refusal.txt 2>&1`
    - REVIEW: Check that the CLI exit code was 1 for both refusals and that the outputs contain JSON, not a traceback.
    - REVIEW: Note the sentinel undercount for C6H6(GT) and CO(GT) ('-200.0') as a possible G7 candidate.
- **Read the Eurostat publisher pages yourself (browser) before deciding the Eurostat link** (learner) done_when: You can say in your own words what the indicator measures, which years it covers, which unit you would use, and on what terms.
    - Open https://ec.europa.eu/eurostat/cache/metadata/en/sdg_11_52_esmsip2.htm: read sections 4.1, 4.2, 4.5, 5.2 and 6.3.
    - Open https://ec.europa.eu/eurostat/en/help/copyright-notice: read the general principles and the exception for data from sources other than Eurostat.
    - Open https://ec.europa.eu/eurostat/databrowser/view/sdg_11_52/default/table?lang=en in a browser (it is a JS app).
    - Decide whether the EEA upstream source affects the licence judgement for your use (context only).
- **G6 edit: allowlist exactly ec.europa.eu** (claude_then_learner_review) done_when: -k g6 gives 2 passed, git diff shows exactly one added host, and settings.json is unchanged.
    - Only after the learner explicitly says 'add ec.europa.eu' (CLAUDE.md rule), Claude appends "ec.europa.eu" to config/allowlist.json domains and changes nothing else.
    - Run the g6 tests and the full suite.
    - The learner reviews the diff: one added line, the six existing entries untouched, no '*', no europa.eu.
    - `python -m pytest tests/test_learner_gaps.py -k g6 -q`
    - `python -m pytest tests/ -q`
    - `git diff config/allowlist.json config/settings.json`
    - REVIEW: The matcher admits subdomains (http_client.py:56-58), so do not add www.ec.europa.eu or europa.eu.
    - REVIEW: Do not edit host_allowed(); test_tools_offline.py:18-22 depends on it.
- **Write the G6 section of outputs/artifacts/decisions.md** (learner_with_claude_help) done_when: The G6 table has one row per added host, the not-added list names catalog.data.gov with a reason, and the wording is the learner's own (rubric Governance, TC-016).
    - Claude pre-fills the evidence column for ec.europa.eu with the three verified URLs (API, ESMS metadata page, copyright notice) and source_id link.europa_sdg_11_52_099aa6.
    - The learner writes 'Why nothing broader' and the date in their own words.
    - Under 'Hosts you chose not to add', the learner lists at least catalog.data.gov (Chicago; the refusal is the finding), europa.eu, commission.europa.eu, www.eea.europa.eu, creativecommons.org and doi.org, plus nagerholidays.com if it appears in a trace, each with a reason.
    - Optional one line: existing entries were left as provided; archive-api.open-meteo.com is redundant with open-meteo.com because of subdomain matching.
- **Re-inspect Eurostat after G6 (and after G3), then decide the gate** (learner_with_claude_help) done_when: A json_stat summary is visible (no NOT_IMPLEMENTED note) and the gate decision for the Eurostat URL is written by the learner.
    - Claude re-runs inspect_dataset_link on the Eurostat link once G6 is in place, and again after G3 is implemented, to show the summary.
    - Check that the summary matches: time first 2005, last 2023, 2006 absent from the values, geo_codes ['IT'], expected_cells 36, value_count 36, missing_cells 0, warnings [].
    - The learner writes the Eurostat gate decision and reason in outputs/UC1/gate_decisions.json, noting coverage against both windows and the terms.
    - `python -m discovery_agent tool inspect_dataset_link '{"url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sdg_11_52?format=JSON&lang=EN&geo=IT"}' --use-case UC1 > outputs/artifacts/inspect_eurostat_after_g6.txt 2>&1`
- **Protect the Chicago and Nager refusals from the >2-retry check during pipeline runs** (learner_with_claude_help) done_when: python -m discovery_agent check UC1 and check UC2 list no 'guardrail: refused URL retried' problems, and refused_hosts shows catalog.data.gov as a finding.
    - The learner accepts Chicago at the gate with their own reason (at least 20 characters).
    - Run the full UC1 profile once with --links-file.
    - For any later re-profiling, use --only with the non-Chicago ids and omit --links-file, so the existing candidates_final.json is reused.
    - After each run, Claude audits refused events per URL in outputs/UC1/trace.jsonl and outputs/UC2/trace.jsonl.
    - If the profiler retried a refused host more than twice in one run, treat it as a G7 candidate and record it. Do not hand-edit the trace.
    - `python -m discovery_agent run --use-case UC1 --from-stage profile --stop-after profile --only link.uci_360,link.europa_sdg_11_52_099aa6 --no-input`
    - `python -c "import json,collections; ev=[json.loads(l) for l in open('outputs/UC1/trace.jsonl') if l.strip()]; c=collections.Counter((e['url'],e['refused']) for e in ev if e.get('kind')=='http' and e.get('refused')); [print(n,code,url) for (url,code),n in c.most_common()]"`
    - `python -m discovery_agent check UC1`
    - REVIEW: The Chicago id is link.data_open_air_chicago_hour_aggre_d4970b; it must not appear in any re-run --only list.
    - REVIEW: The Nager docs_url redirect (date.nager.at/Api) also produces a refused event on every profile of api.nager_public_holidays that probes it.
- **Choose the Open-Meteo location (the one allowed config edit)** (learner) done_when: default_query no longer points at Lisbon (38.72, -9.14), and decisions.md records the city and reason.
    - Pick a northern-Italy location you can justify; neither brief names the city.
    - Change only latitude and longitude in api.open_meteo_archive default_query in config/external_sources_register.json.
    - Record the city and the reason in decisions.md.
    - Claude then runs one probe to confirm the API returns data for those coordinates.
    - `python -m discovery_agent tool call_public_api '{"source_id": "api.open_meteo_archive", "query": {"start_date": "2024-06-01", "end_date": "2024-06-02"}}' --use-case UC2`

## RISKS
- The refused Chicago URL piles up in the append-only outputs/UC1/trace.jsonl across profile re-runs. Once it appears 3 or more times, `check UC1` fails and cannot be cleared without hand-editing outputs, which is forbidden. | Task 9 cannot complete (check must list no problems), with knock-on effects on TC-017 and the automatic guardrail penalties. | Profile Chicago exactly once. Use --only with the other source ids for every re-run. Audit refused counts after each run. Optionally dry-run in a scratch --out folder first.
- Under G7 pressure, someone adds a parent domain (europa.eu, data.gov) or catalog.data.gov to make a refusal go away. | test_g6_allowlist_not_wildcarded fails and the rubric Governance and TC-016/TC-017 points are lost. | Allow only ec.europa.eu. Treat every other refusal as a finding and record it in the 'not added' list.
- The JSON-stat path of inspect_dataset_link returns no licence or terms link, so the profiler may guess a terms URL. Observed: the obvious guesses 404 (/eurostat/about-us/policies/copyright), redirect off-list (ec.europa.eu/info/legal-notice_en → commission.europa.eu) or are http-only. | The Eurostat record may end up LIC-UNKNOWN (blocker) or produce extra refused events in the trace. | In review_UC1.md, cite the verified terms URL https://ec.europa.eu/eurostat/en/help/copyright-notice. If the profiler mis-handles terms, consider a G7 fix at the cause (prompt or tool), without hard-coding.
- Live sources change after 2026-11-18. Eurostat may add 2024 data (T+2 timeliness), and Nager.Date may move its API to nagerholidays.com. | Coverage findings and the reachability of register APIs could differ at run time. | Re-inspect right before the gate. Quote dates and outputs from your own run, not from this analysis.
- The licence judgement is ambiguous for both links: UCI is CC BY 4.0 on the page but research-only in the dataset notes, and Eurostat data comes upstream from EEA, which hits the copyright notice's exception for non-Eurostat sources. | Over-optimistic verdicts (feasible) or missed Legal-review conditions in sign-off. | Raise both as conditions or open questions for Legal in review and sign-off. Do not let G1's 'CC BY 4.0' alone decide.
- Running more than 2 CLI inspections of Chicago across Step 0, Step 2b.5, Task 4 and TC-017. | The TC-017 expectation 'does not retry the link more than twice' could be judged failed. | Inspect it once, save the output to outputs/artifacts/, and reuse that file for TC-017 and the review.

## ISSUES
- [high] check_run counts refused events per exact URL across the whole append-only trace (all runs), not per run. Legitimate re-runs of the profile stage can therefore trip 'guardrail: refused URL retried N times'. | EVIDENCE: validation.py:205-210 (n > 2); trace.py:41 append mode; orchestrator.py:70 one trace file per use case. | REC: Plan runs so refused URLs (Chicago, the Nager docs redirect) are hit at most twice in total. Use --only for re-runs. Do not edit the trace or the validator to get around it.
- [medium] sample_data_file's sentinel detection is an exact string match, so '-200.0' is treated as a real measurement. C6H6(GT) is reported 100% non-missing although 366 rows are -200.0, and CO(GT) misses 91 values. | EVIDENCE: links.py:33 SENTINELS = {..., "-200", ...}; links.py:103-104. Observed in the data.csv profile (C6H6 min -200.0, negative_count 366, sentinel_counts {}). | REC: A strong G7 candidate ('Does a profiler read the -200 values as real measurements?'). Fix at the cause in the tool (numeric-equivalence check), re-run with --only link.uci_360, and record before/after.
- [medium] The Nager.Date register docs_url https://date.nager.at/Api 301-redirects to https://nagerholidays.com/Api, which is refused. Each attempt costs 1 budget request and is never cached. | EVIDENCE: curl -I shows 301 with location nagerholidays.com. The probe_url trace shows refused=REDIRECT_NOT_ALLOWLISTED and budget '1 of 150'. | REC: Do not add nagerholidays.com, since terms are on github.com and the API works on date.nager.at. List it under 'hosts not added' if it appears in a trace, and watch the >2 count.
- [low] The inspect_dataset_link json_stat branch drops the response's extension.annotation links (ESMS_HTML metadata page, info-note PDF) and yields no licence evidence, so the profiler must guess the terms page. | EVIDENCE: links.py:275-279. The cached Eurostat response has annotation ESMS_HTML → https://ec.europa.eu/eurostat/cache/metadata/en/sdg_11_52_esmsip2.htm. | REC: Possible G7 improvement (surface the metadata link). Otherwise cite the verified copyright-notice URL in the review.
- [low] The Eurostat metadata page links its licence policy over http:// (refused with SCHEME_NOT_ALLOWED), and the https form of that link is dead (redirects to the Main_Page). | EVIDENCE: Observed probes: http:// gives SCHEME_NOT_ALLOWED; https:// lands on final_url .../statistics-explained/index.php?title=Main_Page. | REC: Use https://ec.europa.eu/eurostat/en/help/copyright-notice (verified 200) as the terms source.
- [low] README section 4 says the agent should detect the Chicago link as a 'Public landing page', but because the host is refused the tool can never detect a link type. Only a refusal is recorded. | EVIDENCE: README.md:81 versus the observed DOMAIN_NOT_ALLOWLISTED output with no link_type. | REC: In the review, state that the type is unknown because of the refusal, and do not infer content.
- [low] Because of subdomain matching, the existing entry archive-api.open-meteo.com is redundant with open-meteo.com, and the 'exact host' entries still admit subdomains. | EVIDENCE: http_client.py:56-58; allowlist.json lines 5-6. | REC: Leave the existing entries as provided. Mention the matcher semantics in the G6 'why nothing broader' column.
- [low] probe_url's input schema advertises a default max_bytes of 1500000, but the code passes None, so the HttpClient default of 2,000,000 applies. | EVIDENCE: probe.py:25 versus probe.py:28; http_client.py:129. | REC: Cosmetic; no action needed for G6.
- [low] Trace totals and check stats count a redirect-refused request as refused rather than live, although it did consume budget and network. | EVIDENCE: trace.py:35-39; http_client.py:139-158. Observed: http_requests 0 while the budget counter showed 1. | REC: When reporting request counts in the delivery reflection, note that http_live slightly undercounts actual network use.
- [low] The UCI 360 documentation conflicts with the data file on several points: the notes say 'March 2004 to February 2005' but the data runs to 2005-04-04; DD/MM/YYYY is documented but M/D/YYYY is used; 9358 instances are declared but 9357 rows exist; the API says has_missing_values 'no' while the page says 'Yes'. | EVIDENCE: inspect_dataset_link metadata, the UCI page text and the data.csv recount (observed). | REC: Evidence for DQ-METADATA-CONTRADICTION and for the review. Take temporal.end from the whole-file sample (2005-04-04), as the profiler prompt allows when the sample is the whole file.

## QUESTIONS
- [non-blocking] Will you accept any Step 2b suggestion whose host is not yet allowlisted? If so, each needs its own exact-host G6 row (and a check of its file and terms hosts) before the pipeline can reach it. | why: The minimal G6 set covers only the three prescribed UC1 links; accepted suggestions may need more hosts. | default: Allowlist only ec.europa.eu; any refused suggestion host is recorded as unreachable, not added.
- [non-blocking] Do you want the agent to read the upstream EEA terms (www.eea.europa.eu), given the Eurostat copyright notice excludes commercial reuse of data belonging to non-Eurostat sources and sdg_11_52 names EEA as provider? | why: It changes whether you treat the Eurostat licence as plain attribution or as mixed/needs Legal review; adding the host would be a second G6 entry you must justify. | default: Do not add www.eea.europa.eu; record the EEA-source question as a Legal-review condition in review/sign-off.
- [BLOCKING] Which northern-Italy location (city and coordinates) should replace the Lisbon default in api.open_meteo_archive, and why? | why: Both briefs require you to choose and justify it; it is the only config edit allowed, and Claude must not choose for you. | default: Claude stops before the full UC1/UC2 runs and asks again; the Lisbon default stays untouched.
- [non-blocking] When you have decided on G6, will you tell Claude explicitly 'add ec.europa.eu to the allowlist' (Claude edits, you review the diff), or edit config/allowlist.json yourself? | why: CLAUDE.md says hosts are added only when the learner asks; the decision and justification must be yours. | default: Claude waits for an explicit instruction and only prepares the evidence for decisions.md.
- [non-blocking] Do you want an optional dry run of the Chicago profiling in a scratch --out folder before the real UC1 profile run, to see whether the profiler retries the refused host? | why: Retries would land in outputs/UC1/trace.jsonl permanently and can make `check UC1` fail; a dry run costs a few model calls. | default: No dry run; profile Chicago once in the real run and use --only for every re-run.

## PROMPTS
### Task 4: inspect the three UC1 links without the LLM, with Chicago run exactly once
For UC1, run `python -m discovery_agent tool inspect_dataset_link` once on each URL in outputs/UC1/links.json and save each output to outputs/artifacts/inspect_<source_id>.txt. Also run sample_data_file once on the data file the UCI inspection lists. Inspect the Chicago link exactly once and never retry it. Do not change config/allowlist.json or settings.json, and do not try alternate URLs for refused hosts. For each link, report: link_type, every host contacted, any redirect, refusals with the exact error code and message, coverage dates, licence evidence and files. Do not write any gate decision or reason for me.

### G6 edit after the learner has decided
I have decided the G6 allowlist change: add exactly one host, ec.europa.eu, to config/allowlist.json. Keep the six existing entries unchanged and add nothing else. Show me `git diff config/allowlist.json`, then run `python -m pytest tests/test_learner_gaps.py -k g6 -q` and `python -m pytest tests/ -q` and report the counts. Then pre-fill only the evidence column of the G6 table in outputs/artifacts/decisions.md: source link.europa_sdg_11_52_099aa6, the API URL, https://ec.europa.eu/eurostat/cache/metadata/en/sdg_11_52_esmsip2.htm and https://ec.europa.eu/eurostat/en/help/copyright-notice. Leave 'Why nothing broader', the date and the 'hosts not added' reasons as empty placeholders for me to write.

### Re-inspect Eurostat after G6 and G3, before the gate decision
Re-run inspect_dataset_link on https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sdg_11_52?format=JSON&lang=EN&geo=IT with --use-case UC1 and save the output to outputs/artifacts/inspect_eurostat_after_g6.txt. Show label, updated, the dimensions with sizes, time first/last/values, geo_codes, expected_cells, value_count, missing_cells, status_counts and warnings. Compare the years with the UC1 prototype window (2004-03-10..2005-04-04) and production window (2024-01-01..2025-12-31), list the years absent from the time dimension, and explain why 'updated' is not the data end date. Do not decide the gate for me.

### Re-profile safely without touching the Chicago link
Re-profile only link.uci_360 for UC1, reusing the existing outputs/UC1/candidates_final.json (do not pass --links-file): `python -m discovery_agent run --use-case UC1 --from-stage profile --stop-after profile --only link.uci_360 --no-input`. Before running, confirm that link.data_open_air_chicago_hour_aggre_d4970b is not in --only. Afterwards, count refused HTTP events per URL in outputs/UC1/trace.jsonl and warn me if any URL is at 2 or more. Do not edit anything under outputs/UC1/.

### Post-run guardrail audit for the review and the rubric
Audit outputs/UC1/trace.jsonl and outputs/UC2/trace.jsonl without editing them. List: (1) every refused HTTP event grouped by URL and refusal code, with counts; (2) every distinct host contacted live; (3) live requests per stage run from run_history.jsonl; (4) any URL refused more than twice. Then run `python -m discovery_agent check UC1` and `check UC2`, save the outputs to outputs/artifacts/check_UC1.json and check_UC2.json, and summarise the problems. Draft, but do not finalise, a 'Refusals as findings' paragraph for review_UC1.md that quotes the Chicago refusal; I will rewrite it in my own words.
