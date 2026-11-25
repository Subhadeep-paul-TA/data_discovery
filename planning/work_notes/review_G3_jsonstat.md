> Deep-review report written 2026-11-18 by a review agent, for work.md (same folder, one level up).
> It is READ-ONLY analysis of the provided starter code. Paths under /tmp/.../scratchpad mentioned below were temporary and no longer exist.
> Facts marked [V] were verified by reading or running the code; [I] are inferences. Live-site facts were observed on 2026-11-18 and may change.

# Gap G3: jsonstat_summary in discovery_agent/tools/formats.py (graded -k g3; rubric TC-006, TC-007), plus the ungraded G2 data-package stub in the same file

## SUMMARY
G3 is a pure, offline function: no gateway, no network, no LLM. formats.py:59-60 is still a stub. Its contract (formats.py:37-58) and two tests (test_learner_gaps.py:61-84) fix 11 exact keys and exactly two warning codes, MISSING_CELLS and NON_ISO_GEO_CODES. A reference implementation in a scratch copy (never the bundle) turned the baseline result (-k g3: 2 failed, 50 deselected) into 2 passed. The full suite went from 32 to 34 passing, and the remaining 18 failures are G1/G4/G5/G6 tests. Mutation probes showed the two tests miss five realistic mistakes. Those mistakes are: counting with `if v` (zeros read as missing), hard-coding NON_ISO to {UK, EL}, geo order taken from dict insertion order, dimension order taken from the dimension dict, and string status. The rubric checks for hard-coding by hand, so extra checks and a diff review are needed. The real UC1 Eurostat link was read with WebFetch on 2026-11-18 (sdg_11_52, geo=IT). Its time dimension is 2005 and 2007-2023, with no 2006, and all 36 of 36 cells are present. That is exactly the README's 'missing year' edge case: a year absent from the dimension raises no warning at all, so it is the recommended G3 edge case for decisions.md. G2 (datapackage_summary) is ungraded and has no tests; leave it as a stub.

## DETAILS
# G3: `jsonstat_summary` (`discovery_agent/tools/formats.py`)

**Grading.** `python -m pytest tests/test_learner_gaps.py -q -k g3` runs 2 tests, which map to rubric Sheet 2 **TC-006** (normal case) and **TC-007** (edge case). Rubric Sheet 1 "Core Implementation" (11 pts, shared with G1 and G4) also requires:
- the tests pass **unedited**;
- the code is "clear and not hard-coded to the fixtures";
- the G3 edge case is explained in `outputs/artifacts/decisions.md`;
- `pytest_before.txt` and `pytest_after.txt` are saved.

**Planning facts**
- The function is pure and offline (no credentials, LLM or network), so it can be done as soon as the cloned repo exists (Task 5).
- Do G3 **before** the real Eurostat inspection, which needs G6 (Task 6). Before G6, the CLI returns `{"error": "DOMAIN_NOT_ALLOWLISTED", ...}` for the link (verified offline). After G6 but without G3, `inspect_dataset_link` returns only `link_type: "json_stat"` plus a `note` (links.py:278-279).
- Baseline `-k g3`: `2 failed, 50 deselected`. With a reference implementation in a scratch copy, `-k g3` gives `2 passed`, and the full suite gives `34 passed, 18 failed` (the 18 are G1/G4/G5/G6 tests).

## 1. Exact contract
The signature is `def jsonstat_summary(dataset: dict) -> dict:` (formats.py:59). The tests import it at test_learner_gaps.py:12.

| Key | Type | Semantics | Tested |
|---|---|---|---|
| `label`, `updated`, `source` | str or None | Copied from the dataset with `.get()`. TC-007 has no `updated` or `source`. | presence only |
| `dimensions` | list of `{"id","size","labels"}` | In **`dataset["id"]` order**. `size` comes from `dataset["size"]`. `labels` is the first 10 `"code: label"` strings in index order. | id order (TC-006) |
| `time` | `{"first","last","values"}` or None | Time-dimension codes, **sorted as strings**. None when there is no time dimension. | TC-006, TC-007 |
| `geo_codes` | list[str] | Geo codes in **index-position order**, never translated. `[]` when there is no geo dimension. | TC-006, TC-007 |
| `expected_cells` | int | Product of `dataset["size"]` | 24 |
| `value_count` | int | Non-null values. `value` can be a dense list (with nulls) or a sparse dict. | 24 / 3 |
| `missing_cells` | int | `expected_cells - value_count` | 0 / 1 |
| `status_counts` | dict | `{flag: count}` from a string, list or dict `status`. `{}` when absent. | `{"p": 1}` |
| `warnings` | list[str] | Only `"MISSING_CELLS"` (when missing_cells > 0) and `"NON_ISO_GEO_CODES"` (any geo code that is not ISO 3166-1 alpha-2, such as UK, EL or EU27_2020) | TC-006 membership; TC-007 exact set |

**Constraints the tests enforce**
- `set(out) == G3_KEYS` (line 68): no extra top-level keys.
- `set(out["warnings"]) == {"MISSING_CELLS","NON_ISO_GEO_CODES"}` (line 84): any extra code that fires on TC-007's data fails. That data has a status flag, no `updated` and no time labels.
- Warnings are bare codes: `"NON_ISO_GEO_CODES: UK"` fails both tests.
- Codes are never translated: mapping UK to GB fails both tests.

## 2. Where the summary flows
- **links.py:275-279** (`inspect_dataset_link`) returns `{**base, "link_type": "json_stat", "summary": jsonstat_summary(obj)}` and catches **only** `NotImplementedTool`. Any other exception (for example a KeyError) reaches `execute()` (base.py:80-81). The Profiler then gets `{"error": "KeyError"}` and loses the whole inspection (status, canonical_ref, source_id). Be defensive with `.get()` and type checks.
- **probe.py:14-15** treats a document as JSON-stat only if `class == "dataset"` and it has `dimension`, `id` and `size`.
- **formats.py:79-85**: the `summarize_jsonstat` tool (in the Profiler toolset, agents.py:9-10) uses `get_json(max_bytes=5_000_000)`. It does **not** check the document type first: a non-dataset JSON gives `expected_cells 1, warnings ["MISSING_CELLS"]` (verified), which is misleading.
- **prompts/profiler.md:15**: "`json_stat`: read the summary (dimensions, time, geo codes, warnings)". Line 25 asks for ISO dates of the data period. Line 29 covers `spatial.code_system` ("Eurostat codes").
- **agent.py:46-50** clips tool results at `tool_result_char_limit` 14000. A summary with 1,500 geo codes reached 14,298 chars, and the trailing `"warnings"` was cut off (verified). This does not affect UC1, which has one geo code.

| Summary field | Catalog-record field | Downstream |
|---|---|---|
| `time.first` / `time.last` (codes) | `temporal.start` = first-01-01, `temporal.end` = last-12-31 | G4 `rule_temporal_coverage`: COV-OUT-OF-WINDOW / COV-PARTIAL-WINDOW / FRS-STALE |
| freq labels (`"A: Annual"`) | `temporal.grain` = `annual` | G4 `rule_grain` against the need's `min_grain` |
| `updated` | `temporal.metadata_last_updated`, **never** `end` | FRS-METADATA-DATE-MISLEADING (judgement) |
| `geo_codes` + NON_ISO | `spatial.coverage`, `code_system`, `notes` | INT-JOIN-KEY-MISMATCH ("'UK' vs 'GB'"), COV-GEO-MISMATCH |
| `missing_cells`, `status_counts` | `quality_notes`, `unknowns` | DQ judgement |

## 3. Test cases (verified from the test code and a reference run)

| TC | Input | Expected |
|---|---|---|
| TC-006 | Fixture `eurostat_isoc_ec_ibuy_2009_2011.json`: id freq, indic_is, ind_type, unit, geo, time; size [1,1,1,1,8,3]; a sparse `value` dict of 24 entries with keys out of order; no `status`; geo index is a dict `BE..PT, UK:7`; label "Internet purchases by individuals (2002-2019)" | Keys are exactly G3_KEYS; dimension ids are in the order above; time first 2009, last 2011; `UK` is in `geo_codes` and `GB` is not; 24 expected / 24 present / 0 missing; NON_ISO_GEO_CODES is raised and MISSING_CELLS is not. Reference output: `warnings ["NON_ISO_GEO_CODES"]`, `status_counts {}`. |
| TC-007 | Constructed: id [geo, time], size [2,2], geo index **list** `["FR","EL"]`, time index **dict** `{"2011":1,"2010":0}` with no labels, `value [1.0, None, 2.0, 3.0]`, `status {"3":"p"}`, no updated/source | `geo_codes == ["FR","EL"]` (not sorted); `time.values == ["2010","2011"]`; `value_count 3`; `missing_cells 1`; `status_counts {"p": 1}`; `set(warnings) == {MISSING_CELLS, NON_ISO_GEO_CODES}`. In row-major order: pos0 = FR/2010 (1.0), pos1 = FR/2011 (None), pos2 = EL/2010, pos3 = EL/2011 (3.0, flagged "p"). |

## 4. Recommended algorithm
The JSON-stat 2.0 behaviour below was checked against json-stat.org/full:
- the value array is in row-major order (the last dimension in `id` varies fastest), with nulls for missing cells;
- `value` and `status` may be sparse objects;
- a string `status` "assigns the same status to all data";
- a single-element status array is a deprecated form;
- `index` may be omitted only for a constant (single-category) dimension, in which case `label` is required;
- `role` (time/geo/metric) sits at the dataset root.

1. `dims = dataset.get("dimension") or {}`, `ids = list(dataset.get("id") or [])`, `sizes = list(dataset.get("size") or [])`. If `len(sizes) != len(ids)`, fall back to the number of codes in each dimension. Optionally raise `ToolError("not a JSON-stat 2.0 dataset")` when `dimension` or `id` is missing.
2. Codes in **position order**:
```python
idx = cat.get("index")
if isinstance(idx, list): codes = [str(c) for c in idx]
elif isinstance(idx, dict): codes = [str(c) for c, _ in sorted(idx.items(), key=lambda kv: kv[1])]
else: codes = [str(c) for c in (cat.get("label") or {})]   # constant dimension
```
3. `expected_cells = math.prod(int(s) for s in sizes)`.
4. Count values, **never by truthiness**:
```python
items = value.values() if isinstance(value, dict) else value if isinstance(value, list) else []
value_count = sum(1 for v in items if v is not None)   # 0 is a real value
```
Optionally count only dict keys that are ints in `[0, expected)`. Otherwise a stray key gives `missing_cells -1` (verified).
5. Time and geo detection: use `role.time` / `role.geo` first, then the ids `time` / `TIME_PERIOD` and `geo` (case-insensitive). Sort time codes as strings: this works for `2005`, `2020-01`, `2020-Q1` and `2020M01`, whereas `int()` would crash on `2020-Q1`. Keep geo codes in index order and untranslated.
6. Status counting:
   - a string gives `{s: expected_cells}`;
   - a one-element list with more than one cell gives the same (deprecated form);
   - otherwise list or dict values go into a `Counter`, skipping None and "".
   - Keep combined Eurostat flags such as `"bp"` as one key.
7. NON_ISO check: use a `frozenset` of the **249 officially assigned** ISO 3166-1 alpha-2 codes. The stdlib has no country list, and CLAUDE.md forbids new dependencies such as pycountry. UK, EL, XK, EU27_2020, EA20 and NUTS codes like ITC4 are not in the set; IT, GR and GB are (verified).
8. Return the 11 keys and nothing more. Emit warnings in a fixed order: MISSING_CELLS, then NON_ISO_GEO_CODES.

## 5. Preview of the real UC1 link (WebFetch, 2026-11-18; not run through the pipeline)
Link: `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sdg_11_52?format=JSON&lang=EN&geo=IT`
- **Structure:** id `["freq","airpol","effect","unit","geo","time"]`, size `[1,1,1,2,1,18]`. The unit dimension has `NR` (Number) and `RT` (Rate). geo is `IT`.
- **Time:** `2005, 2007…2023` (**2006 is absent**).
- **Values:** 36 sparse values; no `status`; no `role`.
- **Dates:** `updated` is `2025-12-09T11:00:00+0100`. The `extension.annotation` entries OBS_PERIOD_OVERALL_OLDEST and LATEST are 2005 and 2023.
- **Predicted summary:** 36 expected / 36 present / 0 missing; `time` 2005 to 2023 (18 values); **`warnings []`**, because IT is ISO.
- **Link to G4 (inference):** this matches TC-009 (2005-01-01 to 2023-12-31, annual, N6, both windows: exactly COV-PARTIAL-WINDOW).
  - Prototype overlap is 94 of 391 days (about 0.24); production overlap is 0.
  - Not stale (inside the 5-year limit before as-of 2026-10-15).
  - Annual grain equals N6's `min_grain`.
- Re-check all of this with the CLI after G6, because the data can be updated.

## 6. Edge cases for decisions.md (README:168 asks for one; decisions.md:14)
All rows below were verified on the reference implementation.

| Edge case | What the code does | Effect on the catalog record |
|---|---|---|
| **Year absent from the time dimension** (real UC1: no 2006) | Cells are counted from the sizes, so there is **no MISSING_CELLS and no warning**. The gap is visible only in `time.values`. | start 2005-01-01 and end 2023-12-31 hide the hole. The Profiler must add a quality_note; no rule flag will see it. |
| **Year present but empty** (latest year not yet published) | `MISSING_CELLS` fires, but `time.last` **still names the empty year** | `temporal.end` is overstated, which can mask FRS-STALE or COV-PARTIAL-WINDOW. Use the last year that has data and note it. |
| Zero values | Counted as values | A real 0 is never read as missing |
| Status p / e / b / c (unverified meanings: provisional, estimated, break in series, confidential) | `status_counts` only, with no warning. A flag on an empty cell still counts. | quality_notes, for example "1 provisional value". A "b" flag means a comparability caveat. |
| EL / UK | Kept as given; NON_ISO_GEO_CODES fires | `code_system` "Eurostat geo codes (EL=GR, UK=GB)". Coverage uses ISO where possible. INT-JOIN-KEY-MISMATCH when joining to ISO-coded data. |
| EU27_2020, EA20, NUTS codes | NON_ISO_GEO_CODES fires | Aggregates are a named area. Do not sum them with member states. Possible COV-GEO-MISMATCH. |
| `updated` field | Copied as is | Goes to `metadata_last_updated`, not `end` |
| Label period vs response (the fixture says "(2002-2019)" but holds 2009-2011) | `time` reflects the response | Use the response period; treat the label as context only |
| No time dimension | `time: None` | start and end null, grain unknown or static; G4 skips the record |

**Recommendation:** write the "missing year" case using UC1's 2006 gap, contrasted with an empty latest year. The text in decisions.md must be in the learner's own words.

## 7. Pitfalls (mutation-tested against the two tests)
These five are **not caught** by the tests (both still pass):
- counting with `if v`, which reads 0 as missing;
- NON_ISO as `code in {"UK","EL"}`, which is hard-coding and misses EU27_2020, EA20 and NUTS codes;
- geo order taken from dict insertion order;
- `dimensions` built from the `dataset["dimension"]` dict order;
- a string status counted once.

These are **caught**:
- sorting geo codes (TC-007);
- time codes in dict insertion order (TC-007);
- an extra warning such as STATUS_FLAGS (TC-007);
- an extra top-level key (TC-006);
- `dataset["source"]` indexing (KeyError in TC-007);
- `len(value)` as the value count (TC-007);
- detail text in a warning (both tests);
- translating UK to GB (both tests);
- filling missing cells with 0 (TC-007).

**Do not add test files to `tests/`.** TC-020 expects exactly 52 tests collected; use the check script below instead.

## 8. G2 stub (ungraded)
- `datapackage_summary` (formats.py:33-34) raises `NotImplementedTool("... (former G2).")`. The README:160 row says "not graded".
- The comment at formats.py:18, "(tests/test_learner_gaps.py checks them)", is **out of date**: no G2 tests exist.
- links.py:269-274 catches the exception and returns a `note`. `test_inspect_login_wall_and_datapackage_and_github` (test_tools_offline.py:188-198) checks only `link_type`.
- Leave G2 as a stub. It matters only if a Step 2b suggestion is a `datapackage.json`.

## 9. Commands (from the repo root)
```bash
python -m pytest tests/ -q > outputs/artifacts/pytest_before.txt 2>&1   # once, BEFORE any gap code
python -m pytest tests/test_learner_gaps.py -q -k g3
python -m pytest tests/ -q
git diff -- discovery_agent/tools/formats.py
diff tests/test_learner_gaps.py "/mnt/c/Users/Subhadeep.paul/Downloads/806637_Subhadeep_Paul_data_discovery/starter-code/tests/test_learner_gaps.py" && echo unedited
python -m pytest tests/test_learner_gaps.py -v -k g3          # rubric TC-006/TC-007 evidence
python -c "import json; from discovery_agent.tools.formats import jsonstat_summary as j; print(json.dumps(j(json.load(open('tests/fixtures/eurostat_isoc_ec_ibuy_2009_2011.json'))), indent=1))"
# after G6 only:
python -m discovery_agent tool inspect_dataset_link '{"url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sdg_11_52?format=JSON&lang=EN&geo=IT"}' --use-case UC1
```
Extra checks (all 8 print PASS on the reference implementation; the string-status line assumes the expected_cells choice):
```bash
python - <<'EOF'
from discovery_agent.tools.formats import jsonstat_summary as js
def ds(geo, years, value, status=None, gidx=None):
    d = {"class": "dataset", "id": ["geo", "time"], "size": [len(geo), len(years)], "value": value,
         "dimension": {"geo": {"category": {"index": gidx or list(geo)}},
                       "time": {"category": {"index": {y: i for i, y in enumerate(years)}}}}}
    return {**d, "status": status} if status is not None else d
checks = {
    "zero is a value": js(ds(["IT"], ["2005", "2007"], {"0": 0, "1": 0.0}))["missing_cells"] == 0,
    "gap year -> no warning": js(ds(["IT"], ["2005", "2007"], [1, 2]))["warnings"] == [],
    "empty latest year -> MISSING_CELLS": js(ds(["IT"], ["2022", "2023"], {"0": 1}))["warnings"] == ["MISSING_CELLS"],
    "EU27_2020 / ITC4 non-ISO": js(ds(["EU27_2020", "ITC4"], ["2020"], [1, 2]))["warnings"] == ["NON_ISO_GEO_CODES"],
    "IT, GR, GB are ISO": js(ds(["IT", "GR", "GB"], ["2020"], [1, 2, 3]))["warnings"] == [],
    "geo dict index by position": js(ds(["PT", "AT"], ["2020"], [1, 2], gidx={"AT": 1, "PT": 0}))["geo_codes"] == ["PT", "AT"],
    "string status -> every cell": js(ds(["IT"], ["2020", "2021"], [1, 2], status="p"))["status_counts"] == {"p": 2},
    "status on empty cell counted": js(ds(["IT"], ["2020", "2021"], {"0": 1}, status={"1": "c"}))["status_counts"] == {"c": 1},
}
for name, ok in checks.items():
    print("PASS" if ok else "FAIL", name)
EOF
```

## 10. Who does what, and sessions
- **Sessions.** No new session is required: G3 fits the Task 5 session with G1 and G4, each reviewed and committed separately. If context runs out, start a fresh Claude Code session in the cloned repo with work.md. Never work in the bundle.
- **Claude:** explains the design, implements it, runs the tests and checks, and drafts the technical facts.
- **Learner:**
  - approves the design choices (ISO list, string-status semantics, role detection);
  - reviews the diff and can explain row-major order, sparse versus dense values, why UK is kept and why a gap year raises no warning;
  - writes the decisions.md text and the rubric cells in their own words;
  - asks for the commit.

Scratch artifacts (may be cleared):
- `/tmp/claude-1000/-mnt-c-Users-Subhadeep-paul-Downloads-806637-Subhadeep-Paul-data-discovery/769f3079-238b-4329-8e4d-d9c978e67fc2/scratchpad/work-g3/discovery_agent/tools/formats.py` (reference implementation, for cross-checking only)
- `/tmp/claude-1000/-mnt-c-Users-Subhadeep-paul-Downloads-806637-Subhadeep-Paul-data-discovery/769f3079-238b-4329-8e4d-d9c978e67fc2/scratchpad/g3-probes/` (probe.py, mutants.py, integration.py, g3_extra_checks.py)

## FACTS
- [V] jsonstat_summary is a stub that raises NotImplementedTool; the contract comment is at formats.py:37-58. :: starter-code/discovery_agent/tools/formats.py:59-60: raise NotImplementedTool("jsonstat_summary is a learner TODO (G3). See discovery_agent/tools/formats.py.")
- [V] The tests require exactly 11 top-level keys and exactly the warning set {MISSING_CELLS, NON_ISO_GEO_CODES} for the TC-007 dataset. :: tests/test_learner_gaps.py:62-63 (G3_KEYS), :68 set(out) == G3_KEYS, :84 set(out["warnings"]) == {"MISSING_CELLS", "NON_ISO_GEO_CODES"}
- [V] Baseline -k g3 gives 2 failed, 50 deselected; a reference implementation gives 2 passed, and the full suite becomes 34 passed, 18 failed (only G1/G4/G5/G6 tests left). :: Ran pytest -p no:cacheprovider in scratchpad/work-g3 (own copy of baseline) before and after adding a reference implementation
- [V] TC-006 fixture: id [freq, indic_is, ind_type, unit, geo, time], size [1,1,1,1,8,3], 24 sparse values with keys out of order, no status, geo index is a dict ending UK:7, time 2009-2011; the label says '(2002-2019)'. :: tests/fixtures/eurostat_isoc_ec_ibuy_2009_2011.json lines 4, 7-48, 94-133
- [V] inspect_dataset_link's JSON-stat branch catches only NotImplementedTool, so any other exception from jsonstat_summary discards the whole inspection result. :: links.py:275-279; base.py:80-81 maps other exceptions to {"error": type(exc).__name__}
- [V] Before G6, the Eurostat link is refused offline with DOMAIN_NOT_ALLOWLISTED by both inspect_dataset_link and summarize_jsonstat. :: python -m discovery_agent tool inspect_dataset_link/summarize_jsonstat in work-g3 printed {"error": "DOMAIN_NOT_ALLOWLISTED", "message": "DOMAIN_NOT_ALLOWLISTED: host 'ec.europa.eu' is not on config/allowlist.json. ..."} with exit code 1
- [V] The real UC1 Eurostat response (sdg_11_52, geo=IT) has id [freq, airpol, effect, unit, geo, time], size [1,1,1,2,1,18], time 2005 and 2007-2023 with 2006 absent, 36 of 36 values, no status, no role, and updated 2025-12-09T11:00:00+0100. :: WebFetch of the UC1 URL on 2026-11-18, transcribed by a summariser; internally consistent (18 = 19 years minus 1; 36 = 2 units x 18). Must be re-checked with the CLI after G6.
- [V] On the UC1 data, a correct implementation returns warnings [] and missing_cells 0, so the 2006 gap is visible only in time.values. :: Reference implementation run on the reconstructed UC1 response (scratchpad/g3-probes/probe.py)
- [I] Rubric TC-009 (2005-01-01 to 2023-12-31, annual, N6, both windows: exactly COV-PARTIAL-WINDOW) appears to be modelled on this Eurostat series. :: rubric.txt TC-009 row; the dates match the time range of the WebFetch preview
- [V] Five realistic mistakes still pass both G3 tests: truthiness counting, a hard-coded {UK, EL} set, geo order from dict insertion order, dimension order from the dimension dict, and a string status counted once. :: scratchpad/g3-probes/mutants.py run against test_g3_eurostat_response and test_g3_list_values_missing_cells_and_status
- [V] Tool results are clipped at 14000 chars; a summary with 1500 geo codes loses its trailing 'warnings' key. :: agent.py:46-50 _clip; settings.json tool_result_char_limit 14000; integration.py printed big summary json chars: 14298 | 'warnings' survives clip: False
- [V] JSON-stat 2.0 says: a string status assigns the same status to all data; a single-element status array is deprecated; index may be omitted only for a constant dimension (then label is required); role (time/geo/metric) sits at the dataset root; values are in row-major order with nulls for missing cells. :: WebFetch of https://json-stat.org/full/ (quoted spec sentences)
- [V] The ISO 3166-1 alpha-2 list used has 249 assigned codes; UK and EL are not in it, GB and GR are; IT, GR and GB pass, while EU27_2020, EA20, ITC4, XK, EL and UK are flagged. :: Count check and probe outputs in work-g3
- [V] There are no G2 (datapackage_summary) tests in test_learner_gaps.py; the comment at formats.py:18 saying the tests check them is out of date. :: grep -rn datapackage tests/ shows only test_tools_offline.py:72,188-198 (link_type checks only)
- [V] Adding new test files would break the TC-020 expectation of exactly 52 tests collected and all 52 passing. :: rubric.txt TC-020: 'Before: 52 tests are collected, 32 pass ... After: all 52 pass'
- [V] summarize_jsonstat passes any JSON to jsonstat_summary; a non-dataset document produces a misleading summary (expected_cells 1, warnings [MISSING_CELLS]) instead of an error. :: formats.py:83-85; reference run on {'error': [...]} returned expected_cells 1, missing_cells 1, warnings ['MISSING_CELLS']
- [I] Eurostat flag meanings: p provisional, e estimated, b break in time series, c confidential, d definition differs, f forecast, r revised, u low reliability, z not applicable. :: General knowledge; the Eurostat API wiki redirected to a login page and could not be read
- [I] The Python standard library has no ISO country list, and CLAUDE.md forbids new dependencies, so the ISO list must be embedded as a constant. :: CLAUDE.md: 'stdlib plus anthropic and jsonschema. Do not add dependencies without asking.'; the stdlib claim is from knowledge

## TASKS
- **Prerequisite: capture pytest_before.txt on the untouched repo** (claude) done_when: outputs/artifacts/pytest_before.txt exists and shows '20 failed, 32 passed'.
    - Confirm that no gap code has been changed yet (git status / git diff is empty for discovery_agent/ and config/).
    - Run the full suite and save the output.
    - Check the counts: 52 collected, 32 passed, 20 failed.
    - If gap code was already changed, regenerate the baseline from a fresh copy of the read-only bundle's starter-code instead.
    - `python -m pytest tests/ -q > outputs/artifacts/pytest_before.txt 2>&1`
    - `tail -3 outputs/artifacts/pytest_before.txt`
    - REVIEW: The baseline was captured before any G1/G3/G4 edits.
- **G3 design walkthrough before any code** (claude_then_learner_review) done_when: The learner has approved the design and each open choice in writing (chat).
    - Claude reads formats.py:37-60, test_learner_gaps.py:61-84, the fixture, links.py:260-282, probe.py:10-16 and profiler.md.
    - Claude explains the 11 keys, the algorithm (position-ordered index, dataset['id'] order, product of sizes, None-only counting, role-then-id detection for time and geo, sorted time codes, unsorted untranslated geo codes, status forms, full ISO list) and the edge cases.
    - Claude lists the design choices: ISO list vs regex, string-status semantics, role detection, optional guard for non-dataset input.
    - The learner decides each choice.
    - REVIEW: The approach is not hard-coded to UK/EL or to the fixtures.
    - REVIEW: No extra keys or warning codes are added.
- **Implement jsonstat_summary** (claude_then_learner_review) done_when: -k g3 gives 2 passed; the full suite has no failures other than gaps not yet closed; the learner has read and accepted the diff; the tests file is unedited.
    - Edit only discovery_agent/tools/formats.py: jsonstat_summary plus small private helpers and an ISO constant; add math/Counter imports from the stdlib.
    - Leave datapackage_summary (G2) and the tool wrappers unchanged.
    - Show the full diff to the learner.
    - Run -k g3, then the full suite.
    - Confirm test_learner_gaps.py is unchanged against the bundle copy.
    - `python -m pytest tests/test_learner_gaps.py -q -k g3`
    - `python -m pytest tests/ -q`
    - `git diff -- discovery_agent/tools/formats.py`
    - `diff tests/test_learner_gaps.py "/mnt/c/Users/Subhadeep.paul/Downloads/806637_Subhadeep_Paul_data_discovery/starter-code/tests/test_learner_gaps.py" && echo unedited`
    - REVIEW: Values are counted with `is not None`, not truthiness.
    - REVIEW: Geo codes are taken by index position.
    - REVIEW: Dimensions follow dataset['id'].
    - REVIEW: .get() is used for label/updated/source.
    - REVIEW: Line length is at most 140 (.flake8).
- **Extra edge-case checks and hard-coding audit** (claude) done_when: All extra checks print PASS and the audit finds no hard-coding.
    - Run the extra-checks heredoc from the work.md G3 section; all 8 must print PASS (adjust the string-status line if the learner chose value_count semantics).
    - Audit the diff against the pitfalls table (the five mistakes the tests do not catch).
    - Do not add any file under tests/.
    - `python - <<'EOF' ... EOF   (heredoc from work.md section 9)`
    - REVIEW: EU27_2020, EA20, ITC4 and XK are flagged; IT, GR and GB are not.
- **Learner teach-back on G3** (learner_with_claude_help) done_when: The learner can explain each design choice without notes; this is needed for the walkthrough and PR review.
    - Claude quizzes the learner one question at a time.
    - Cover: row-major order, sparse vs dense values, why 0 is not missing, why UK stays UK, why the UC1 2006 gap raises no warning, what MISSING_CELLS does not tell you, and how time.first/last map to temporal.start/end and to G4 flags.
    - The learner answers in their own words.
    - REVIEW: The learner owns the explanation.
- **Commit G3** (learner_with_claude_help) done_when: One G3 commit exists on the working branch, containing formats.py only.
    - The learner asks Claude to commit, or commits themselves, on a feature branch (not main).
    - Stage only discovery_agent/tools/formats.py.
    - Use a commit message that names G3 and the design choices.
    - `git checkout -b gaps   # if still on main`
    - `git add discovery_agent/tools/formats.py`
    - `git commit -m "G3: implement jsonstat_summary (JSON-stat 2.0 summary)"`
    - REVIEW: No tests or outputs are in the commit.
- **After G6: inspect the real Eurostat link and verify the summary** (learner_with_claude_help) done_when: The learner has the actual summary, knows any differences from the preview, and has written their own gate decision for the Eurostat link.
    - Only after ec.europa.eu is in config/allowlist.json (G6) and justified in decisions.md.
    - Claude runs inspect_dataset_link via the CLI (no LLM) and compares the result with the preview: ids, size [1,1,1,2,1,18], time 2005 and 2007-2023, 36 of 36 cells, warnings [].
    - Claude lists any differences.
    - The learner reads the publisher page and decides the gate entry in their own words.
    - `python -m discovery_agent tool inspect_dataset_link '{"url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sdg_11_52?format=JSON&lang=EN&geo=IT"}' --use-case UC1`
    - REVIEW: Claude does not write gate_decisions.json.
    - REVIEW: Do not retry a refused host more than twice.
- **Write the G3 edge case in decisions.md** (learner_with_claude_help) done_when: decisions.md has a filled G3 line in the learner's words, with evidence.
    - Claude drafts the technical facts in chat: the missing year (2006 absent: no warning, gap visible only in time.values) versus an empty latest year (MISSING_CELLS, but time.last is overstated), plus the effect on temporal.start/end and quality_notes.
    - The learner writes the final text in their own words on decisions.md line 14.
    - Cite the evidence command and its output.
    - REVIEW: It covers what the code does and how it changes the summary and the catalog record.
- **Rubric evidence for TC-006 and TC-007** (learner_with_claude_help) done_when: TC-006 and TC-007 rows are filled and outputs/artifacts/pytest_after.txt shows 52 passed.
    - Run pytest -v -k g3 and print the summary for the fixture and for the TC-007 dataset.
    - The learner pastes the actual output and marks Pass/Fail in Sheet 2.
    - After all gaps are closed, save pytest_after.txt.
    - `python -m pytest tests/test_learner_gaps.py -v -k g3`
    - `python -m pytest tests/ -q > outputs/artifacts/pytest_after.txt 2>&1`

## RISKS
- The live Eurostat data has changed since the 2026-11-18 WebFetch preview (new year, status flags, missing cells). | Expected warnings, time range or G4 flags differ from the plan. | Re-run inspect_dataset_link after G6 and treat the CLI output as the source of truth. The .cache/http entry keeps later runs reproducible.
- The Profiler maps `updated` (2025-12-09) to temporal.end instead of the last time code (2023). | Wrong coverage: production-window and staleness flags are computed on the wrong end date; the record falls into the 'last updated is not a data date' trap. | Check records/link.*.json after profiling. If it happens, it is a strong G7 candidate (fix in profiler.md).
- An empty latest year makes time.last overstate coverage; MISSING_CELLS is the only signal. | temporal.end is too late, so G4 may miss FRS-STALE or COV-PARTIAL-WINDOW. | Document it in decisions.md. The Profiler should note it in quality_notes. An optional 'years with data' extension needs the learner's explicit decision.
- jsonstat_summary raises on an unexpected shape. | links.py catches only NotImplementedTool, so the whole inspect_dataset_link result is replaced by an error and the Profiler loses status/canonical_ref. | Use .get() and type checks everywhere; run the extra checks, including datasets without time or geo.
- Over-engineering: extra keys, extra warning codes, or detail text in warnings. | TC-006 or TC-007 fail (mutation-verified). | Stick to exactly the 11 keys and 2 bare warning codes; put extra information in decisions.md instead.
- Hard-coded NON_ISO set {UK, EL} or other fixture-shaped logic. | Tests still pass, but the rubric's 'not hard-coded' criterion fails (part of 11 points). | Use the full 249-code ISO list; run the extra checks for EU27_2020, EA20 and ITC4; use the review prompt.
- The learner adds pytest files for the edge cases. | The test count drifts from 52 and contradicts TC-020's expected output. | Keep the edge-case checks as a heredoc whose output goes into decisions.md, not a new file in tests/.
- The learner cannot defend the code in the PR review or walkthrough. | Ownership criteria and walkthrough points are lost. | Run the teach-back quiz prompt before committing.

## ISSUES
- [medium] inspect_dataset_link catches only NotImplementedTool around jsonstat_summary; any other exception aborts the whole inspection. | EVIDENCE: links.py:275-279; base.py:80-81 | REC: Make jsonstat_summary defensive. Change links.py only as a deliberate, documented fix (for example under G7) if a real failure is observed.
- [medium] The G3 tests miss five realistic mistakes (truthiness counting, hard-coded UK/EL, geo dict insertion order, dimension-dict order, string status), so passing the tests does not prove correctness. | EVIDENCE: scratchpad/g3-probes/mutants.py: all five mutants passed TC-006 and TC-007 | REC: Run the extra-checks heredoc and the diff-audit prompt before committing.
- [medium] `time` is derived from the dimension categories, not from observed values: an empty latest year still appears as time.last. | EVIDENCE: Reference run: dropping all 2011 cells from the fixture gives time.last '2011', missing_cells 8, warnings [MISSING_CELLS, NON_ISO_GEO_CODES] | REC: Explain this in decisions.md; have the Profiler cross-check before setting temporal.end.
- [medium] A year absent from the time dimension raises no warning; the real UC1 link has exactly this (no 2006). | EVIDENCE: WebFetch preview: time 2005 and 2007-2023, size 18; reference summary warnings [] | REC: Use this as the G3 decisions.md edge case; the Profiler should record the gap in quality_notes.
- [low] Out-of-date comment: formats.py:18 says tests/test_learner_gaps.py checks the datapackage_summary keys, but no G2 tests exist. | EVIDENCE: grep -rn datapackage tests/ shows only test_tools_offline.py link_type checks | REC: Ignore; G2 is ungraded. Optionally mention it in the PR description.
- [low] Contract gaps: the count for a string status is unspecified, the label fallback when category.label is missing is unspecified, and missing_cells can go negative if a sparse value has out-of-range keys. | EVIDENCE: formats.py:41-55; reference run with an extra key '9' in a 4-cell cube gives missing_cells -1 | REC: Decide (default: string status counts expected_cells; label falls back to the code; count only in-range keys) and note it in decisions.md.
- [low] summarize_jsonstat summarises any JSON without a type check; a non-dataset document yields a misleading summary. | EVIDENCE: formats.py:83-85; reference on {'error': [...]} gives expected_cells 1, warnings ['MISSING_CELLS'] | REC: Optionally raise ToolError when 'dimension'/'id' is missing; execute() maps it to TOOL_ERROR.
- [low] Tool-result clipping at 14000 chars can drop the trailing 'warnings' for summaries with very many geo codes. | EVIDENCE: agent.py:46-50; the 1500-code test summary was 14298 chars and lost 'warnings' | REC: Accept for UC1 (one geo code), or emit warnings and counts before geo_codes (dict order is not tested).
- [low] The dataset label can state a different period from the response (the fixture label says 2002-2019 while the response holds 2009-2011). | EVIDENCE: fixture line 4 vs time index lines 119-133 | REC: The Profiler should take temporal from the summary's time, not from the label; mention it in the review.
- [low] summarize_jsonstat uses max_bytes 5,000,000 while inspect_dataset_link uses 1,500,000; the HTTP cache key includes max_bytes, so calling both on one URL costs an extra request. | EVIDENCE: formats.py:84; links.py:250; http_client.py:103-105 | REC: No change needed; the Profiler should not call summarize_jsonstat after inspect_dataset_link already returned a summary.

## QUESTIONS
- [non-blocking] For NON_ISO_GEO_CODES, should the code embed the full list of 249 officially assigned ISO 3166-1 alpha-2 codes (recommended), or use a regex for two capital letters plus a documented exception set (EL, UK, XK, EU, EA ...)? | why: The rubric penalises code hard-coded to the fixtures; a {UK, EL} set passes the tests but fails that criterion. | default: Embed the full ISO 3166-1 alpha-2 frozenset.
- [non-blocking] Should time and geo dimensions be found through JSON-stat 'role' first (generalises to non-Eurostat providers), or only through the ids 'time' and 'geo' as the contract comment says? | why: It is a generality versus simplicity trade-off; Eurostat responses have no 'role'. | default: role.time / role.geo first, then the ids time / TIME_PERIOD / geo (case-insensitive).
- [non-blocking] When 'status' is a single string (it applies to all data), should status_counts count every cell (expected_cells) or only cells with values (value_count)? | why: The contract does not say; the spec treats a string as shorthand for an array the size of value. | default: expected_cells, documented in decisions.md.
- [non-blocking] Do you want extra edge-case tests as new pytest files, or only as a heredoc check whose output goes into decisions.md? | why: Rubric TC-020 expects exactly 52 tests collected and passing. | default: No new test files; use the heredoc check.
- [non-blocking] Which G3 edge case will you document in decisions.md? | why: The README asks for one edge case per function, and the text must be in your own words. | default: A missing year: UC1's real 2006 gap (no warning) contrasted with an empty latest year (MISSING_CELLS, but time.last is overstated).
- [non-blocking] Should the summary report which years actually hold data (for example an extra sub-key inside 'time'), or stay strictly on the documented contract? | why: It would catch an overstated temporal.end, but it changes the documented shape. | default: Stay on the contract; explain the limitation in decisions.md.
- [non-blocking] Have you already created and cloned your own repo and saved outputs/artifacts/pytest_before.txt from the unmodified code? | why: The 'before' evidence must come from the untouched code, and G3 edits must happen in your repo, never in the bundle. | default: Capture pytest_before.txt first; if code has already changed, regenerate it from a fresh copy of the bundle's starter-code.
- [non-blocking] Leave G2 (datapackage_summary) as an ungraded stub? | why: It has no tests and no graded link uses a data package; it matters only if a Step 2b suggestion is a datapackage.json. | default: Leave it as a stub.

## PROMPTS
### Implement G3 per CLAUDE.md: design first, learner reviews the diff, tests, extra checks, then draft decisions.md facts
We are on Task 5, gap G3. Follow CLAUDE.md. Read discovery_agent/tools/formats.py (G3 contract, lines 37-60), tests/test_learner_gaps.py lines 1-15 and 61-84 (do NOT edit), tests/fixtures/eurostat_isoc_ec_ibuy_2009_2011.json, discovery_agent/tools/links.py lines 260-282, discovery_agent/tools/probe.py lines 10-16, discovery_agent/prompts/profiler.md, and the G3 section of work.md.

Step 1. Before any code, explain in plain words:
- the 11 return keys and their types;
- how you will (a) read category.index in list and dict form by POSITION, falling back to category.label for a constant dimension; (b) keep dimension order from dataset['id']; (c) compute expected_cells as the product of size; (d) count non-null values for the dense list and the sparse dict without treating 0 as missing; (e) find the time and geo dimensions (role.time / role.geo first, then the ids time / TIME_PERIOD / geo), sort the time codes as strings, and keep geo codes in index order, never translated; (f) count status in string, list and dict form; (g) decide NON_ISO_GEO_CODES against the full ISO 3166-1 alpha-2 list, with no hard-coded UK/EL;
- the edge cases: gap year, empty latest year, zero values, status p/e/b/c, EL/UK/EU27_2020/NUTS, missing updated/source, datasets without time or geo.
List the design choices I must make (ISO list vs regex, string-status semantics, role detection) with your recommendation. Then STOP and wait for my OK.

Step 2. After my OK, change only jsonstat_summary plus small private helpers and constants in formats.py: stdlib only, .get() everywhere, exactly the 11 keys, warnings limited to the bare strings MISSING_CELLS and NON_ISO_GEO_CODES. Leave datapackage_summary (G2) and the tool wrappers unchanged. Do not edit or add anything under tests/. Show me the full diff.

Step 3. Run `python -m pytest tests/test_learner_gaps.py -q -k g3`, then `python -m pytest tests/ -q`, and report the counts. Expect 2 passed for g3; any other failures may only be tests for gaps not yet closed. Then run the extra-checks heredoc from work.md and show its output.

Step 4. In chat only (do not write to decisions.md), draft the technical facts for the G3 line of outputs/artifacts/decisions.md about one edge case, a JSON-stat response with a missing year: what the code does, and how it changes the summary and the catalog record (temporal.start/end, quality_notes). I will write the final text in my own words. Do not commit.

### Read-only audit of the G3 diff for hard-coding and the pitfalls the tests do not catch
Review my G3 change read-only (`git diff -- discovery_agent/tools/formats.py`). Do not modify code. For each item, report PASS or FAIL with the line number:
1. values counted with `is not None`, not truthiness (0 is a value);
2. geo codes in index POSITION order (a dict index sorted by its positions, not insertion or alphabetical order), never translated;
3. `dimensions` built from dataset['id'] order, not the dimension dict;
4. time codes sorted as strings, and time is None when there is no time dimension;
5. NON_ISO_GEO_CODES uses a full ISO 3166-1 alpha-2 list: UK, EL, EU27_2020, EA20, ITC4 and XK are flagged; IT, GR and GB are not;
6. exactly the 11 top-level keys;
7. only the two warning codes, as bare strings;
8. .get() for label/updated/source;
9. string, list and dict status all handled;
10. no exception on a dataset without time or geo, or with a constant dimension that has no index;
11. tests/test_learner_gaps.py is identical to /mnt/c/Users/Subhadeep.paul/Downloads/806637_Subhadeep_Paul_data_discovery/starter-code/tests/test_learner_gaps.py.
Then run the extra-checks heredoc from work.md and summarise the findings.

### Teach-back so the learner can defend G3 in the PR review and walkthrough
Quiz me on jsonstat_summary so I can defend it. Ask 8 questions, one at a time; wait for my answer, then correct me briefly and cite the file and line. Cover:
- row-major order and which dimension varies fastest;
- dense list versus sparse dict values;
- why 0 is not a missing cell;
- why UK stays UK in geo_codes;
- why UC1's Eurostat response (no 2006) raises no warning;
- what MISSING_CELLS does and does not tell the Profiler;
- status flags p/e/b;
- how time.first/last become temporal.start/end and which G4 flags they drive for N6.
Do not change any files.

### After G6: inspect the real Eurostat link without the LLM and compare it with the preview
G6 is done: ec.europa.eu is in config/allowlist.json and justified in decisions.md. Without the LLM, run:
python -m discovery_agent tool inspect_dataset_link '{"url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sdg_11_52?format=JSON&lang=EN&geo=IT"}' --use-case UC1

Show me the summary and compare it with the preview in work.md:
- ids freq, airpol, effect, unit, geo, time;
- size [1,1,1,2,1,18];
- time 2005 and 2007-2023, with no 2006;
- 36 of 36 cells, no status, warnings [];
- updated 2025-12-09.
List every difference. Then explain what each field implies for the catalog record (temporal start/end/grain, metadata_last_updated, spatial code_system, the NR/RT units) and which G4 flags to expect for N6 in the prototype and production windows. Do not write gate_decisions.json or decisions.md; I decide the gate myself.

### Produce rubric evidence for TC-006 and TC-007
Produce evidence for rubric Sheet 2 rows TC-006 and TC-007:
1. Run `python -m pytest tests/test_learner_gaps.py -v -k g3`.
2. Print jsonstat_summary as JSON for tests/fixtures/eurostat_isoc_ec_ibuy_2009_2011.json, and for the TC-007 dataset copied from tests/test_learner_gaps.py lines 77-80.
3. For each row, give a short 'Actual output' text (2-3 lines) and Pass/Fail against the rubric's expected behaviour.
Do not edit the rubric or any file; I will paste the results myself.
