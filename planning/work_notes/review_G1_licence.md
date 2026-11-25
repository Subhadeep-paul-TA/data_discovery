> Deep-review report written 2026-11-18 by a review agent, for work.md (same folder, one level up).
> It is READ-ONLY analysis of the provided starter code. Paths under /tmp/.../scratchpad mentioned below were temporary and no longer exist.
> Facts marked [V] were verified by reading or running the code; [I] are inferences. Live-site facts were observed on 2026-11-18 and may change.

# Gap G1 — extract_licence (discovery_agent/tools/licence.py)

## SUMMARY
G1 is a pure offline function: page HTML string in, a dict with exactly four keys out (licence_name, licence_url, snippet, found_in). It is graded by 9 test items (-k g1, rubric TC-001..TC-005) plus the rubric's 'not hard-coded to the fixtures' and 'edge cases in decisions.md' checks. Its output decides whether a dataset link gets LIC-ATTRIBUTION/LIC-NONCOMMERCIAL or the LIC-UNKNOWN blocker. One trap: risk_rules.rule_licence only treats {unknown, none, null, not found, n/a} as unknown, so strings like 'Not specified', 'Other (specified in description)' or 'All rights reserved' raise no flag at all if passed through. I prototyped the recommended design in a scratch copy only (the bundle is untouched): 9/9 G1 tests pass, the full suite goes from 32 to 41 passed (the remaining 11 failures are G3–G6), and on the live UCI 360 page inspect_dataset_link returns 'CC BY 4.0' with found_in 'link'. Three ordering rules: save pytest_before.txt before any gap edit, finish G1 before the UC1 profile stage (Task 7d), and use the Kaggle 'Unknown' case as the decisions.md entry. That last one is in the learner's own words.

## DETAILS
# G1: `extract_licence` (discovery_agent/tools/licence.py)

**Bottom line.** G1 is a pure function: no network and no LLM. HTML goes in and four keys come out. It is graded by 9 test items (`python -m pytest tests/test_learner_gaps.py -k g1 -q`, rubric TC-001..TC-005). The rubric's Core Implementation row (11 pts, shared with G3/G4) also checks that the code is "clear and not hard-coded to the fixtures" and that "the G1 and G3 edge cases are explained in decisions.md".

I prototyped the design below **only in a scratch copy**. Results:
- 9/9 G1 tests pass.
- The full suite goes from 32 to **41 passed / 11 failed**. All 11 remaining failures are G3/G4/G5/G6.
- `inspect_dataset_link` on the live UCI 360 page returns `CC BY 4.0`, found_in `link`.

## (a) The exact contract (tests + callers)

| Item | Requirement | Source |
|---|---|---|
| Signature | `extract_licence(html: str, jsonld: list[dict] \| None = None) -> dict`. The input is the page **HTML string**, not a URL. Never fetch anything. | licence.py:62,74; links.py:202,213,230 |
| Keys | **Exactly** `licence_name`, `licence_url`, `snippet`, `found_in`. No `note`, no extra keys. | test_learner_gaps.py:18,23,58 |
| `found_in` | The exact strings `"json-ld"`, `"link"`, `"text"`, or `None` | licence.py:68; tests :23,:29,:35 |
| `snippet` | A non-empty str of at most **400** chars when found. Clip at the end. | licence.py:67; test :24 |
| `licence_name` | A normalised name, or `None` when nothing is found or the page says unknown/unspecified. Recommended: also `None` when the value is unrecognised or the evidence is ambiguous. | licence.py:63-65,73 |
| `licence_url` | The URL that was found, or `None`. An empty string from JSON-LD becomes `None`. | test :30 |
| Nothing found | Return exactly `{"licence_name": None, "licence_url": None, "snippet": None, "found_in": None}` | test :58 |
| Explicit unknown in JSON-LD | `licence_name` None, **but** `found_in == "json-ld"` and the snippet contains the raw value (`Unknown`) | test :35 |
| Negative prose | A page sentence like "No terms are given" or "License: Unknown" must still give the all-None dict. Only JSON-LD can produce the "declared but unknown" state. | test :52,58 |
| `jsonld` default | Call `jsonld_datasets(html)` only when `jsonld is None`. An empty list `[]` means "no JSON-LD" (this is the UCI path), so test with `is None`, not `or`. | licence.py:73; links.py:202 |
| Never raise | `_licence_or_note` catches **only** `NotImplementedTool`. Any other exception makes `execute()` return `ok=False`, and the whole `inspect_dataset_link` result is lost (metadata, files). `test_inspect_landing_page_with_jsonld` (test_tools_offline.py:180) would then fail. | links.py:211-215; base.py:66-81 |
| Dependencies | Standard library only (`re`, `json`, `html`, `unicodedata`). CLAUDE.md says to ask before adding dependencies. Remove the now-unused `NotImplementedTool` import. | CLAUDE.md; licence.py:7 |

## (b) Test matrix (9 items; all fail at baseline with NotImplementedTool)

| Test (test_learner_gaps.py) | Input | Must return |
|---|---|---|
| `test_g1_uci_page_link_or_text` l.21 (TC-001) | `uci_321_repository_page.html`, jsonld None | the 4 keys; `CC BY 4.0`; found_in `link` or `text`; snippet non-empty and at most 400 chars |
| `test_g1_zenodo_jsonld_url` l.27 (TC-002) | `zenodo_record_landing_page.html` | `CC BY 4.0`; `json-ld`; `creativecommons.org/licenses/by/4.0` in the URL |
| `test_g1_kaggle_unknown_is_not_a_licence` l.33 (TC-003) | `kaggle_ecommerce_landing_page.html` | name None; `json-ld`; `Unknown` in the snippet |
| `test_g1_jsonld_variants[jsonld0]` (TC-004) | `<html></html>` + license `http://opendatacommons.org/licenses/odbl/1.0/` | `ODbL 1.0` |
| `[jsonld1]` | license `https://choosealicense.com/licenses/cc0-1.0/` | `CC0 1.0` |
| `[jsonld2]` | license `{"@type": "CreativeWork", "name": "CC BY-NC-SA 4.0", "url": ""}` | `CC BY-NC-SA 4.0`. The empty url must fall back to the name. |
| `test_g1_text_and_links[html0]` (TC-005) | `<a href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/">Open Government Licence v3.0</a>`, jsonld `[]` | `OGL v3.0` |
| `[html1]` | `<a href=".../licenses/by-nc/4.0/legalcode">Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)</a>`, `[]` | `CC BY-NC 4.0` |
| `[html2]` | `<p>No terms are given on this page.</p>`, `[]` | exactly the all-None dict |

## Where the licence actually is (verified)

- **UCI 321 fixture.**
  - 0 JSON-LD blocks.
  - Under `<h1>License</h1>`, inside `<main>` (chars 28070-40987): `This dataset is licensed under a <a href="https://creativecommons.org/licenses/by/4.0/legalcode" rel="nofollow">Creative Commons Attribution 4.0 International</a> (CC BY 4.0) license.`
  - This is the only creativecommons.org link on the page.
  - The link uses `rel="nofollow"`, not `rel="license"`.
- **Zenodo fixture.**
  - One JSON-LD block, at the very end of the page (line 1455). `@type` is the URL `https://schema.org/Dataset`. The license is the string URL `https://creativecommons.org/licenses/by/4.0/legalcode`.
  - A "Rights" box sits **inside `<aside>`**. It holds the title "Creative Commons Attribution 4.0 International", a versionless sentence ("The Creative Commons Attribution license allows…") and `<a class="license-link" href=".../by/4.0/legalcode">Read more</a>`.
  - `data-record='{…"rights":[…]}'` JSON sits inside attributes (lines 931, 976).
  - A footer "Terms of Use" link points to `https://about.zenodo.org/terms`. That is the site's terms, not a dataset licence.
- **Kaggle fixture.**
  - The license is `{"@type": "CreativeWork", "name": "Unknown", "url": ""}`.
  - The body is a JavaScript shell with 24 visible characters. There are no licence links and no licence text.
- **Live UCI 360 page** (fetched 2026-11-18; 132,964 bytes; HTTP 200 with the agent's own user agent).
  - Same template as 321: 0 JSON-LD and a single link `https://creativecommons.org/licenses/by/4.0/legalcode`, followed by "(CC BY 4.0) license.".
  - DOI 10.24432/C59K5F.
  - The UCI API has no licence field (`licence_in_api: None`, uci.py:5,60), so this link is the only evidence.
  - Before G1, the tool returns the all-None stub plus `note: "extract_licence is a learner TODO (G1)…"`.

## How the output flows (verified from code)

1. **Callers.** Only `tools/links.py` calls it:
   - `_resolve_uci` (l.197-208) calls `_licence_or_note(html, [])`.
   - `_landing_page` (l.218-234) passes the raw JSON-LD Dataset dicts.
   - `uci.py` only documents it. `summarize.py`, `agents.py`, `validation.py` and `orchestrator.py` never call it.

   So it only affects `dataset_link` candidates, through the Profiler-only tool `inspect_dataset_link` (agents.py:9-10). UC2 without links, public APIs and the UC1 **Eurostat JSON-stat link** (links.py:275-279; its fixture has no licence field) all bypass it. Their licence must come from the Profiler probing a terms page.
2. **Profiler** (prompts/profiler.md:19): "use the licence from `inspect_dataset_link` and say where it was found (`found_in`)… look once on the provider's terms page with `probe_url`… Otherwise record null."
3. **Record** (catalog_record.schema.json:240-296). The `licence` object has `name`, `url`, `commercial_use` (yes/no/unknown/not_applicable), `mixed_sources`, `attribution_text`, `agreement_status` and `evidence`. `name` and `evidence` are required, and `additionalProperties` is false. There is **no `found_in` field**: `found_in` and the snippet must be written into `licence.evidence`.
4. **Rule** (risk_rules.py:37-51), applied to `licence.name`:
   - empty, or in `{"unknown","none","null","not found","n/a"}` → `LIC-UNKNOWN` (blocker)
   - otherwise, `\bNC\b|non[- ]?commercial` → `LIC-NONCOMMERCIAL` (blocker)
   - otherwise, `\bBY\b|attribution|OGL|open government` → `LIC-ATTRIBUTION` (minor)
   - `mixed_sources` → `LIC-MIXED` (major)

   The Risk Assessor must keep each rule flag, or dismiss it with a written reason (agents.py:104-108).

**Rule outcomes (I ran these names through the rule):**

| Names | Flag |
|---|---|
| CC BY, BY-SA, BY-ND (any version), `CC BY`, `ODC-By 1.0`, `OGL v3.0`, `OGL` | `LIC-ATTRIBUTION` |
| any NC variant | `LIC-NONCOMMERCIAL` |
| `CC0 1.0`, `PDM 1.0`, **`ODbL 1.0`**, `PDDL 1.0`, `MIT`, `Apache-2.0`, `GPL-3.0` | no LIC flag |
| None, `""`, `Unknown`, `None`, `n/a` | `LIC-UNKNOWN` |
| `Not specified`, `Other (specified in description)`, `See website`, `All rights reserved`, `Proprietary`, `License not specified`, `notspecified` | **no flag at all** |

So an unrecognised string must become `None` and never be passed through.

**The README claim** ("Without G1, the profiler may still read a licence from the page itself", README l.93) is true, but it depends on the path:
- Landing pages already expose `jsonld_datasets[].license` (licence.py:46) and `licence_snippets` (links.py:230).
- The UCI path exposes neither. The Profiler would have to call `probe_url`, which returns `licence_snippets` and `licence_links` (probe.py:50-52).
- README l.155 ("Until then, every dataset link is LIC-UNKNOWN") contradicts l.93. The code supports l.93.

## (c) Recommended algorithm

The first stage that yields evidence decides, and the search stops there.

0. **Prepare.** Set `jsonld = jsonld_datasets(html)` only if `jsonld is None`. Build `content` from the HTML:
   - Remove comments and the `<script|style|noscript|svg|template|head>` blocks.
   - Then remove `<header>`, `<nav>` and `<footer>`. Site chrome usually carries the *website's* licence.
   - **Do not strip `<aside>`**: Zenodo's Rights box is inside one.
1. **JSON-LD.**
   - For each Dataset dict, in order, take the first key matching `license`/`licence` (case-insensitive, optional prefix such as `dct:`) whose value is non-empty.
   - Optional fallback: `distribution[].license`.
   - Accept these value shapes:
     - a URL string;
     - a name or SPDX id string (`CC-BY-4.0`, `MIT`);
     - an object: url from `url`, `@id` or `sameAs`; label from `name`, `alternateName`, `text` or `identifier`;
     - a list of any of the above.
   - For each item, try the URL rules first, then the label rules.
   - **An explicit value is final, even if it is unrecognised** (`Unknown`, `Other…`, a custom terms URL). Return name None, `licence_url` = the URL if there is one, `found_in="json-ld"` and `snippet=json.dumps(value)[:400]`.
   - An empty value (`""`, `{}`, `{"name":"","url":""}`) counts as **absent**: continue to the next stage.
2. **Links.**
   - Order of candidates:
     1. `<link rel="license">` and `<a rel="license">`;
     2. any `<a>` in `content` whose href matches a URL rule;
     3. anchors whose short text (at most ~150 chars) matches a label rule.
   - The name comes from the **href first**, because it identifies the legal text. Use the anchor text only when the href is not a licence URL.
   - `licence_url` = the href.
   - Snippet = the visible text of the enclosing block (p, li, dd, td, div). Widen it when the block is only "Read more". Clip to 400.
3. **Text.**
   - Split `content` into blocks, then into sentences.
   - Keep only sentences with a licensing cue: `licen[cs]`, "released/available/distributed under", "creative commons", `CC BY`, `CC0`, "open government", `ODbL`, `PDDL`, `ODC-By`.
   - Apply the label rules. The snippet is the sentence; `licence_url` is None.
4. **Decide within a stage.**
   - Fold a versionless name into a versioned name of the same family: `CC BY` + `CC BY 4.0` → `CC BY 4.0`. Zenodo's own text needs this.
   - One distinct name → return it.
   - Two or more different names (dual licence, BY vs BY-NC, 3.0 vs 4.0) → name None, with all the evidence joined in the snippet.
5. Nothing found anywhere → return the all-None dict.

Guard input types (non-dict JSON-LD items, numbers, empty HTML) instead of using a blanket try/except.

**Normalisation table** (pattern rules on the lower-cased URL with the scheme, `www.`, query and fragment stripped; never a lookup of fixture URLs):

| Family | URL forms | Label / text forms | Output |
|---|---|---|---|
| CC BY family | `creativecommons.org/licenses/by[-nc][-nd][-sa]/X.Y[/port][/legalcode \| /deed.xx]` | `CC BY-NC-SA 4.0`, `CC-BY-4.0`, "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International", "Attribution 4.0 International (CC BY 4.0)" | `CC BY[-NC][-ND][-SA] X.Y`. Modifier order is NC, ND, SA. 3.0 ports are kept (`CC BY 3.0 IGO`). With no version, output `CC BY`. Never invent a version. |
| CC0 | `creativecommons.org/publicdomain/zero/1.0`, choosealicense `cc0-1.0`, SPDX `CC0-1.0` | `CC0`, `CC0: Public Domain`, "CC Zero" | `CC0 1.0` (the only version that exists) |
| ODC | `opendatacommons.org/licenses/{odbl,by,pddl}/(1.0\|1-0)`; optional CKAN `opendefinition.org/licenses/odc-*` | `ODbL`, "Open Database License", `ODC-By`, `PDDL`, "Public Domain Dedication and License" | `ODbL 1.0`, `ODC-By 1.0`, `PDDL 1.0` |
| OGL (UK) | `nationalarchives.gov.uk/doc/open-government-licence/version/N/`; the same path with no version | "Open Government Licence v3.0", `OGL v3`, `OGL-UK-3.0` | `OGL vN.0`. With no version, output `OGL`. Exclude "Open Government Licence – Canada" and "– Ontario". |
| Software | choosealicense / spdx / opensource.org slugs, `apache.org/licenses/LICENSE-2.0`, gnu.org | "MIT License", "licensed under the MIT", "Apache License, Version 2.0", `Apache-2.0` | `MIT`, `Apache-2.0` (optional: `GPL-3.0`, `BSD-3-Clause`) |
| Not a licence | n/a | `Unknown`, `Other (…)`, `Not specified`, `notspecified`, `See website`, `Various`, `Proprietary`, `All rights reserved`, `Copyright…`, "public domain" in plain prose | `None` (keep the snippet when it came from JSON-LD) |

Require "MIT" or "Apache" to appear next to the word licence/license. Bare "MIT" (a university) or "Apache Spark" must not match. I checked both baits against the prototype.

## (d) Edge cases for decisions.md (each with its effect on the record and flags)

| Edge case | Code result | Record effect | Flag effect |
|---|---|---|---|
| **E1 Kaggle `{"name":"Unknown","url":""}`** (TC-003; the helper guide hints at this case in l.141) | name None, url None, found_in `json-ld`, raw value in the snippet. The search stops, so page links cannot override it. | `licence.name` null, `url` null, `evidence` cites inspect_dataset_link + JSON-LD "Unknown", `commercial_use` "unknown", licence listed in `unknowns` | `LIC-UNKNOWN` (blocker). The open-data policy note in external_sources_register.json says "Datasets … with an unknown licence … need Legal review before use". |
| E2 `Other (specified in description)`, `Not specified`, `All rights reserved` | None (+ snippet if from JSON-LD) | same as E1 | `LIC-UNKNOWN` only because the name is null. Passing the raw string through would raise **no** flag (verified). |
| E3 versionless `CC BY` or `OGL` | kept without a version | the attribution text needs the version, so a human checks it | `LIC-ATTRIBUTION` |
| E4 two different licences (JSON-LD list, or two different links) | None; the snippet lists both | null; the Profiler may set `mixed_sources` | `LIC-UNKNOWN` (+ `LIC-MIXED`) |
| E5 licence link only in the header/nav/footer | ignored → all None | null | `LIC-UNKNOWN` |
| E6 UCI: licence only on the human page; `_resolve_uci` passes `[]` | `CC BY 4.0`, found_in `link` | `commercial_use` yes; the attribution text should be recorded (orchestrator.py:331 checklist) | `LIC-ATTRIBUTION` (minor) instead of the blocker |
| E7 ODbL, CC BY-SA, CC BY-ND | correct names | name set | ODbL raises **no** flag; SA and ND raise only `LIC-ATTRIBUTION`. Share-alike and no-derivatives terms need a human note in the review. |
| E8 empty JSON-LD value | treated as absent → links/text | depends on the next stage | depends on the next stage |
| E9 page truncated at max_bytes, or malformed JSON-LD | that evidence is silently missing → may be None | null | `LIC-UNKNOWN` |

## (e) What would look "hard-coded to the fixtures"

- Branching on portal names or hosts (`zenodo`, `kaggle`, `uci`, `svelte`).
- Exact-string URL dictionaries that do not cover http/https, `www`, `1.0`/`1-0`, `/legalcode`, `/deed.xx` or query strings.
- A name table that only covers the 6 tested names, only version 4.0, or only BY and BY-NC.
- Matching only the exact case-sensitive `"Unknown"`, instead of "anything unrecognised → None".
- Keying on `rel="nofollow"`, `class="license-link"`, `<h1>License</h1>`, character offsets or line numbers.
- Treating every "terms" link as a licence (Zenodo's `about.zenodo.org/terms`).
- Scanning the raw HTML for licence URLs, which also matches Zenodo's `data-record` attributes.
- A snippet sliced so it happens to fit within 400 chars on the fixture, instead of a final `[:400]`.
- A blanket `except: return {...}`.
- Re-parsing JSON-LD when `jsonld=[]` was passed.

## (f) Existing helpers and their quirks (verified)

- `jsonld_datasets` (licence.py:10-26) is reused by `summarise_jsonld_dataset` and covered by `test_jsonld_from_real_portal_pages`. **Leave it unchanged** and record its limits.
  - It matches only `type="application/ld+json"` exactly. A `; charset=utf-8` suffix → 0 found.
  - It uses strict `json.loads`, so a raw newline inside a string → the block is silently skipped.
  - It reads only the top level, a list, or `@graph`. A list containing an `@graph`, or a Dataset under `mainEntity`, → 0 found.
  - It uses a substring test, `"Dataset" in str(@type)`. This accepts the URL form `https://schema.org/Dataset`.
  - Multiple script blocks are handled.
- `summarise_jsonld_dataset` passes `license` through raw.
- `html_summary` (summarize.py:99-114) uses a 160/220-char window and is **not** used by `extract_licence`.

## Verification evidence (scratch, may be cleared on reboot)

- Prototype: `/tmp/claude-1000/-mnt-c-Users-Subhadeep-paul-Downloads-806637-Subhadeep-Paul-data-discovery/769f3079-238b-4329-8e4d-d9c978e67fc2/scratchpad/work-g1/discovery_agent/tools/licence.py` (289 lines in total; the helper functions are kept). It returns **`None`** for "GNU General Public License v3" because the long GNU form was not added.
- Edge-case script: `/tmp/claude-1000/-mnt-c-Users-Subhadeep-paul-Downloads-806637-Subhadeep-Paul-data-discovery/769f3079-238b-4329-8e4d-d9c978e67fc2/scratchpad/g1-scripts/edge_cases.py`.
- `inspect_dataset_link` before/after G1 on UCI 360: `/tmp/claude-1000/-mnt-c-Users-Subhadeep-paul-Downloads-806637-Subhadeep-Paul-data-discovery/769f3079-238b-4329-8e4d-d9c978e67fc2/scratchpad/g1-live/inspect360_before.json` and `/tmp/claude-1000/-mnt-c-Users-Subhadeep-paul-Downloads-806637-Subhadeep-Paul-data-discovery/769f3079-238b-4329-8e4d-d9c978e67fc2/scratchpad/g1-live/inspect360_after.json`.
- The implementing session should rebuild G1 with the learner and keep it explainable. The core is stages 0-5 plus the table above. These are optional: `rel=license`, distribution licences, CKAN, PDM, GPL/BSD and 3.0 ports.

## Placement in the overall plan

- **Order.**
  1. Task 1: save `pytest_before.txt` (52 collected / 32 passed / 20 failed) **before** editing any gap. Otherwise the "before" file shows 41 passed.
  2. Task 4: inspect UCI 360 with the stub. That gives a useful "before" observation.
  3. Task 5: G1.
  4. Re-run the inspect: CC BY 4.0, link.
  5. G1 must be finished before Task 7(d) `--from-stage profile`. Otherwise the link records must be re-profiled, which costs LLM calls and request budget.
- **Session.** Use the same session or a fresh one in the repo; CLAUDE.md loads automatically. A fresh session is advisable if the Steps 0-2b session is long. G1 needs no gateway credentials.
- **Learner review points.**
  - the exact 4 keys;
  - why an explicit "Unknown" stops the search;
  - ambiguous → None;
  - removing header/nav/footer, but not aside;
  - no invented versions;
  - why `None` and not raw strings, given rule_licence's narrow unknown set;
  - never raising.


## FACTS
- [V] extract_licence is a stub that raises NotImplementedTool; the contract is documented in the comment block above it. :: starter-code/discovery_agent/tools/licence.py:56-75 (raise at line 75; contract at lines 61-73)
- [V] There are 9 G1 test items (3 plain + 3 + 3 parametrised); at baseline all 9 fail with NotImplementedTool. :: Ran 'python -m pytest tests/test_learner_gaps.py -k g1 -q' in a scratch copy: '9 failed, 12 deselected'; tests/test_learner_gaps.py:21-58
- [V] The output must have exactly the keys licence_name, licence_url, snippet, found_in; a page with no licence must return all four as None (exact dict equality). :: tests/test_learner_gaps.py:18 (G1_KEYS), :23 (set(out) == G1_KEYS), :58 (out == {all None})
- [V] The Kaggle case must return licence_name None with found_in 'json-ld' and 'Unknown' in the snippet, i.e. an explicit JSON-LD 'Unknown' is reported as evidence, not as 'not found'. :: tests/test_learner_gaps.py:33-35; Kaggle fixture JSON-LD license = {"@type": "CreativeWork", "name": "Unknown", "url": ""}
- [V] The UCI 321 fixture has no JSON-LD; its licence is a single anchor to https://creativecommons.org/licenses/by/4.0/legalcode (rel='nofollow', text 'Creative Commons Attribution 4.0 International') inside <main>, followed by '(CC BY 4.0) license.' :: tests/fixtures/uci_321_repository_page.html line 114-116; 0 'application/ld+json' matches; <main> spans chars 28070-40987, the link is at char 40666
- [V] The Zenodo fixture's JSON-LD (line 1455, the last block on the page) has @type 'https://schema.org/Dataset' and license 'https://creativecommons.org/licenses/by/4.0/legalcode'; its Rights box sits inside <aside>. :: Parsed tests/fixtures/zenodo_record_landing_page.html; <aside> spans chars 24194-69980 and contains the 'Read more' license-link at line 1180
- [V] The live UCI 360 page (fetched 2026-11-18) uses the same template: no JSON-LD and one CC BY 4.0 legalcode link with '(CC BY 4.0) license.'; DOI 10.24432/C59K5F. :: curl fetch plus the agent's own HttpClient (inspect_dataset_link in a scratch copy, HTTP 200, 132,964 bytes)
- [V] Before G1, inspect_dataset_link on UCI 360 returns licence {licence_name: null, licence_url: null, snippet: null, found_in: null, note: 'extract_licence is a learner TODO (G1). See discovery_agent/tools/licence.py.'} and no licence snippets. :: Scratch run saved at scratchpad/g1-live/inspect360_before.json; code at links.py:197-215
- [V] The only callers are links.py: _resolve_uci passes jsonld=[] (line 202) and _landing_page passes the parsed Dataset dicts (line 230), both via _licence_or_note, which catches only NotImplementedTool (lines 211-215). :: grep across the package: no calls in summarize.py, agents.py, validation.py or orchestrator.py; uci.py only mentions it in its docstring (lines 5-6)
- [V] Any exception other than NotImplementedTool inside extract_licence would make execute() return ok=False and lose the whole inspect_dataset_link payload; test_inspect_landing_page_with_jsonld would fail. :: tools/base.py:66-81 (execute catch-all); tests/test_tools_offline.py:180-185 asserts ok
- [V] The catalog record licence object has no found_in field (additionalProperties false; required name and evidence), so found_in and the snippet must go into licence.evidence. :: discovery_agent/schemas/catalog_record.schema.json:240-296
- [V] rule_licence treats only empty names or {unknown, none, null, not found, n/a} as unknown; 'Not specified', 'Other (specified in description)', 'See website', 'All rights reserved', 'Proprietary', 'License not specified' and 'notspecified' raise no LIC flag at all. :: risk_rules.py:43; ran rule_licence on each string in the baseline copy
- [V] ODbL 1.0, CC0 1.0, PDDL 1.0, PDM 1.0, MIT, Apache-2.0 and GPL-3.0 raise no LIC flag; CC BY-SA and CC BY-ND raise only LIC-ATTRIBUTION; any NC variant raises LIC-NONCOMMERCIAL; OGL and ODC-By raise LIC-ATTRIBUTION. :: Ran risk_rules.rule_licence on the normalised names; risk_rules.py:45-48
- [V] Without G1, landing pages still expose the raw JSON-LD license and licence_snippets to the Profiler, but the UCI path does not; the Profiler would need probe_url (which returns licence_snippets and licence_links). :: links.py:227-230 vs 197-208; probe.py:50-52; html_summary output on the fixtures
- [V] README line 93 ('do not expect every link to show LIC-UNKNOWN') contradicts README line 155 ('Until then, every dataset link is LIC-UNKNOWN'). :: starter-code/README.md:93 and :155
- [V] The Eurostat JSON-stat path never calls extract_licence, and the Eurostat fixture has no licence field (source 'ESTAT' only). :: links.py:275-279; grep of tests/fixtures/eurostat_isoc_ec_ibuy_2009_2011.json
- [V] jsonld_datasets misses JSON-LD with type='application/ld+json; charset=utf-8', with raw newlines inside strings, a Dataset nested under mainEntity, or a list containing an @graph; it handles @graph, multiple blocks and the URL-form @type. :: Ran jsonld_datasets on synthetic HTML in the scratch copy; licence.py:17-25
- [V] The prototype design passes all 9 G1 tests; the full suite goes to 41 passed / 11 failed (only G3, G4, G5 and G6 tests remain), including test_inspect_landing_page_with_jsonld. :: Scratch copy work-g1: 'pytest tests/ -q' gives '11 failed, 41 passed'; '-k g1' gives '9 passed'
- [V] With the prototype, inspect_dataset_link on UCI 360 returns CC BY 4.0, found_in 'link', url .../by/4.0/legalcode, and a snippet of 100 chars. :: scratchpad/g1-live/inspect360_after.json
- [V] The open-data policy says datasets with an unknown or non-commercial licence need Legal review before use. :: config/external_sources_register.json:18 (policy.open_data_links notes)
- [V] The helper guide explicitly suggests the Kaggle 'Unknown' case as the G1 edge case, and decisions.md has a G1 bullet slot. :: helper_guide.txt:141; outputs/artifacts/decisions.md:13
- [V] Rubric TC-020 expects exactly 52 tests collected (32 passing before, all 52 passing after), so adding new test files would change the stated counts. :: rubric.txt Sheet 2, TC-020
- [I] Hugging Face dataset pages express licences as choosealicense.com URLs, and Kaggle uses licence names such as 'CC0: Public Domain' or 'Attribution 4.0 International (CC BY 4.0)'. :: General knowledge of these portals; this explains why the test variants include choosealicense; not checked against live pages
- [I] The hidden answer key likely expects LIC-ATTRIBUTION (not LIC-UNKNOWN) for link.uci_360, so G1 affects the automatic red-flag score. :: Inferred from the rubric's automatic scoring (red-flag recall) and the live page licence

## TASKS
- **Precondition: save pytest_before.txt before any gap edit** (claude_then_learner_review) done_when: outputs/artifacts/pytest_before.txt exists and shows 52 collected, 32 passed, 20 failed.
    - In the learner's repo root, after setup (Task 1), with the venv active, run the full suite and save its output.
    - Check that the last line reports 20 failed and 32 passed (52 collected).
    - Only then start G1.
    - `python -m pytest tests/ -q > outputs/artifacts/pytest_before.txt 2>&1; tail -3 outputs/artifacts/pytest_before.txt`
    - REVIEW: The learner confirms the numbers match TC-020 before any gap code exists.
- **G1 design walkthrough and decisions (no code yet)** (learner_with_claude_help) done_when: The learner can state each decision and its reason in one or two sentences, without notes.
    - Paste the main G1 prompt (Step 1 only); Claude explains the contract, precedence, normalisation rules, None semantics and robustness.
    - The learner decides: (1) an explicit JSON-LD 'Unknown' is final; (2) ambiguous or multiple licences give None; (3) strip header, nav and footer but not aside; (4) never invent a version; (5) core vocabulary versus optional extras.
    - The learner writes these decisions down in their own words; they feed the decisions.md G1 entry.
    - REVIEW: Why 'Unknown' gives None but found_in 'json-ld'
    - REVIEW: Why unrecognised strings must not pass through (rule_licence's narrow unknown set)
    - REVIEW: Why the footer is excluded
- **Implement extract_licence in discovery_agent/tools/licence.py** (claude_then_learner_review) done_when: -k g1 shows 9 passed; no previously passing test fails (the suite gains exactly 9 passes if G1 is the first gap closed); tests/test_learner_gaps.py is unchanged.
    - Edit only discovery_agent/tools/licence.py: replace the stub with extract_licence plus small private helpers; keep jsonld_datasets and summarise_jsonld_dataset unchanged; remove the unused NotImplementedTool import.
    - Use only the standard library (re, json, html, unicodedata); keep lines at 140 characters or fewer (.flake8).
    - Show the full diff; the learner reads it and asks about any regex they cannot explain.
    - Run the G1 tests, then the full suite.
    - `python -m pytest tests/test_learner_gaps.py -k g1 -q`
    - `python -m pytest tests/ -q`
    - `git diff --stat && git diff -- discovery_agent/tools/licence.py`
    - `git diff --exit-code -- tests/test_learner_gaps.py`
    - REVIEW: Returns exactly 4 keys and uses the exact found_in strings
    - REVIEW: jsonld default uses 'is None'
    - REVIEW: No fixture-specific strings, portal names or exact-URL dictionaries
    - REVIEW: Never raises on odd input
    - REVIEW: Snippet clipped to 400
- **Verify on real and adversarial inputs without the LLM** (claude) done_when: UCI 360 gives CC BY 4.0 via link; every extra case matches the agreed decisions and none raises.
    - Run inspect_dataset_link on UCI 360 and show only the licence object (expect CC BY 4.0, found_in link).
    - Run a throwaway python -c check, not a new test file, on extra cases: a JSON-LD dual-licence list; {name: 'Other (specified in description)'}; 'CC-BY-4.0'; the opendatacommons odbl/1-0 URL; creativecommons publicdomain/zero/1.0; a footer-only CC link; 'Released under CC BY.'; 'researchers at MIT'; an OGL link without version; JSON-LD license: 42.
    - Save the output for decisions.md and the rubric evidence.
    - `python -m discovery_agent tool inspect_dataset_link '{"url": "https://archive.ics.uci.edu/dataset/360/air+quality"}' --use-case UC1`
    - REVIEW: The learner spot-checks two cases by hand against the decisions.
- **Write the G1 entry in outputs/artifacts/decisions.md** (learner_with_claude_help) done_when: The G1 bullet names the edge case, what the code does with it, and how the licence field and LIC flags change, in the learner's own words.
    - Claude drafts the technical facts for the Kaggle 'Unknown' case: the input, the returned dict, why the search stops, and how licence.name, url, evidence, commercial_use and unknowns change; the result is LIC-UNKNOWN (blocker) and Legal review per the policy note.
    - Optionally add E2: why 'Other' or 'Not specified' must be None, because rule_licence would raise no flag for the raw string.
    - The learner rewrites it in their own words under '## G1 and G3: one edge case in each function'.
    - REVIEW: No copied draft text left verbatim
    - REVIEW: It cites the actual function output
- **Fill rubric Sheet 2 TC-001..TC-005** (learner_with_claude_help) done_when: Rows TC-001 to TC-005 have actual outputs and a Pass/Fail mark entered by the learner.
    - Claude runs 'pytest -k g1 -v' and prints extract_licence's output for each rubric input as one JSON line per case.
    - The learner pastes the actual outputs and marks Pass or Fail personally.
    - `python -m pytest tests/test_learner_gaps.py -k g1 -v`
    - REVIEW: The outputs pasted match the current code, not the prototype
- **After the UC1 profile stage: audit licence fields in records (report only)** (claude_then_learner_review) done_when: Every dataset-link record's licence fields agree with the inspect output, and any discrepancy is logged for the learner (possibly as G7).
    - For each outputs/UC1/records/link.*.json, list licence.name, url, evidence, commercial_use, whether licence appears in unknowns, and the LIC-* codes in outputs/UC1/rule_flags.json.
    - Expected: link.uci_360 is CC BY 4.0 with LIC-ATTRIBUTION; Chicago (refused) is null with LIC-UNKNOWN plus ACC-UNREACHABLE; Eurostat depends on the Profiler probing a terms page.
    - Flag any raw non-vocabulary licence name, or evidence that does not mention found_in or a terms URL, as a possible G7 candidate; never hand-edit records.
    - REVIEW: The learner decides whether any discrepancy becomes the G7 fix

## RISKS
- A licence link in the site footer or header is mistaken for the dataset's licence, hiding a LIC-UNKNOWN blocker. | A source the human should have checked looks usable (minor LIC-ATTRIBUTION instead of a blocker); this hurts verdict calibration and red-flag recall. | Remove header, nav and footer before the link and text stages (not aside); keep an explicit JSON-LD declaration final; test a footer-only case.
- Loose text patterns match non-licences ('researchers at MIT', 'Apache Spark', 'cc by email'). | A false licence again replaces the LIC-UNKNOWN blocker. | Use cue-gated sentences; require 'MIT License' or 'Apache License 2.0'-style phrases; include bait cases in the ad-hoc checks.
- Unrecognised strings ('Not specified', 'Other', 'All rights reserved') reach licence.name as raw text. | rule_licence raises no flag at all (verified), so the source looks licence-clean. | Use a closed vocabulary where anything else gives None; audit the records after the profile stage; consider this as a G7 fix if the Profiler writes raw strings.
- extract_licence raises on unusual input (non-dict JSON-LD items, numbers, truncated HTML). | _licence_or_note only catches NotImplementedTool, so the whole inspect_dataset_link result (metadata, files) is lost for that link. | Guard input types; run the full suite (test_inspect_landing_page_with_jsonld) and junk-input checks.
- The evaluator judges the code as hard-coded to the fixtures. | Lost points in the 11-point Core Implementation row. | Use table-driven pattern rules (any version, all CC modifiers, http/https, 1.0 and 1-0, legalcode/deed); no portal names or exact fixture URLs; document the vocabulary.
- pytest_before.txt is saved after G1 is implemented. | The 'before' evidence shows 41 passed instead of 32, contradicting TC-020. | Save it in Task 1, before any gap edit.
- The profile stage runs before G1 is finished. | The UCI link record is built without licence evidence; re-profiling costs LLM calls and the 150-request budget per run. | Finish G1 (and G3/G6) before Task 7(d) --from-stage profile.
- The implementation is too clever for the learner to defend in the walkthrough or review. | Weak ownership; Review Judgement and walkthrough marks are at risk. | Keep the core small and named; add optional extras only if the learner can explain them; the learner reviews every regex.

## ISSUES
- [medium] _licence_or_note only catches NotImplementedTool, so any other exception in extract_licence breaks the entire inspect_dataset_link result. | EVIDENCE: discovery_agent/tools/links.py:211-215; tools/base.py:66-81 | REC: Write extract_licence so it never raises (type guards); do not change links.py unless the learner chooses to; check with the full suite.
- [medium] rule_licence's unknown set is narrow ({unknown, none, null, not found, n/a}); common non-licence strings raise no flag. | EVIDENCE: risk_rules.py:43; ran it on 'Not specified', 'Other (specified in description)', 'See website', 'All rights reserved', 'Proprietary', 'notspecified': no flags | REC: G1 returns None for anything unrecognised; audit records after profiling; widening the set (or tightening the Profiler prompt) is a candidate G7 fix if a real run shows it.
- [low] rule_licence does not flag the obligations of ODbL (attribution plus share-alike: no flag at all), CC BY-SA or CC BY-ND (only LIC-ATTRIBUTION). | EVIDENCE: Ran rule_licence: 'ODbL 1.0' gives []; 'CC BY-SA 4.0' and 'CC BY-ND 4.0' give ['LIC-ATTRIBUTION'] | REC: Note it in the memo review for any such source; do not encode extra words into licence_name to game the regex.
- [low] The README contradicts itself about licences before G1. | EVIDENCE: README.md:93 ('do not expect every link to show LIC-UNKNOWN') vs README.md:155 ('Until then, every dataset link is LIC-UNKNOWN') | REC: Rely on the code: landing pages expose licence evidence without G1, the UCI path does not unless the Profiler calls probe_url.
- [low] The UCI resolver returns no licence snippets, unlike landing pages, so before G1 the UCI licence is visible only if the Profiler probes the page. | EVIDENCE: links.py:197-208 (no licence_snippets) vs links.py:230 | REC: Implement G1 before the profile stage; mention it in the G1 notes or the SKILL.md Step 3 checks.
- [low] jsonld_datasets silently misses some valid JSON-LD (charset suffix in the type attribute, raw control characters, nested mainEntity, a list containing an @graph). | EVIDENCE: licence.py:17-25; synthetic checks gave 0 Datasets for each of these shapes | REC: Leave it unchanged (it is tested and shared); the link and text stages are the fallback; record it as a known limitation.
- [low] The contract's example vocabulary mixes naming styles ('OGL v3.0', 'CC0 1.0' vs 'Apache-2.0'). | EVIDENCE: licence.py:63-64 | REC: Match the tested strings exactly and document the vocabulary for licences that are not tested.
- [low] Rubric TC-020 states the literal counts '52 collected / all 52 pass'; extra learner test files would change them. | EVIDENCE: rubric.txt Sheet 2 TC-020 | REC: Prefer ad-hoc checks recorded in decisions.md, or explain the new count if extra tests are added.

## QUESTIONS
- [BLOCKING] Have you already saved outputs/artifacts/pytest_before.txt in your own repository (52 collected / 32 passed / 20 failed)? | why: It must be captured before any gap code changes; implementing G1 first would make the 'before' evidence wrong. | default: Capture it first, then start G1.
- [non-blocking] When a page's JSON-LD explicitly says the licence is 'Unknown' (or 'Other'), should that be final, even if a licence link appears elsewhere on the page? | why: Both choices pass the tests; 'final' is the conservative choice (keeps the LIC-UNKNOWN blocker) but may miss a licence stated only in the body. | default: Final: return None with found_in 'json-ld' and the raw value as the snippet.
- [non-blocking] If a page shows two different licences (dual licence, or a CC BY link and a CC BY-NC link), should G1 return None (ambiguous) or the first one found? | why: None is the 'never guess' choice and raises the LIC-UNKNOWN blocker for a human to resolve; 'first found' is simpler but can hide a non-commercial restriction. | default: None, with both pieces of evidence in the snippet.
- [non-blocking] Do you want extra licence test cases added as a new file under tests/, or kept as ad-hoc checks recorded in decisions.md? | why: Extra tests show generalisation but change the rubric's literal '52 tests' count (TC-020). | default: Ad-hoc checks only; no new test files.
- [non-blocking] May Claude install flake8 locally to lint licence.py (it is not in requirements.txt)? | why: CLAUDE.md says to ask before adding dependencies; .flake8 exists, so an evaluator may run it. | default: Do not install; keep lines at 140 characters or fewer and imports clean by inspection.
- [non-blocking] Core vocabulary only (CC family, CC0, ODbL/ODC-By/PDDL, OGL, MIT, Apache-2.0), or also the optional extras (rel=license, per-distribution licences, CKAN opendefinition URLs, GPL/BSD, CC 3.0 ports)? | why: More coverage generalises better but is more code you must be able to defend. | default: Core vocabulary plus rel=license; add other extras only if you can explain them.

## PROMPTS
### Implement G1 the way the repo's CLAUDE.md requires (design and edge cases first, learner diff review, tests, decisions.md draft)
We are closing gap G1: extract_licence in discovery_agent/tools/licence.py. Follow CLAUDE.md: explain the design and edge cases first, then make the change for my diff review. Do not edit tests/test_learner_gaps.py, config/ or outputs/.

Read first: discovery_agent/tools/licence.py (contract comment at lines 56-75); tests/test_learner_gaps.py lines 17-58; the three fixtures tests/fixtures/uci_321_repository_page.html, zenodo_record_landing_page.html and kaggle_ecommerce_landing_page.html (find where the licence actually is in each); discovery_agent/tools/links.py lines 197-234 (_resolve_uci passes jsonld=[], _landing_page passes the parsed Datasets, _licence_or_note only catches NotImplementedTool); discovery_agent/risk_rules.py rule_licence (lines 37-51); the LIC-* codes in config/red_flags.json; and the licence block of discovery_agent/schemas/catalog_record.schema.json (line 240 onwards).

STEP 1, design only, no code. In at most 25 bullets cover:
- The exact contract: exactly 4 keys; found_in values; snippet of at most 400 chars; the all-None dict when nothing is found; jsonld defaults to jsonld_datasets(html) only when it is None.
- Precedence: JSON-LD license/licence (URL string, name or SPDX id, object with name/url/@id, list) first; then licence links (rel=license, anchors whose href is a licence URL, anchors whose text names a licence) in the main content, with header, nav and footer removed but not aside; then sentences that contain a licensing cue.
- Normalisation as pattern rules, not a lookup of fixture URLs: CC BY with NC/ND/SA and any version; CC0; ODbL, ODC-By and PDDL (1.0 or 1-0); OGL vN (versionless stays 'OGL'); MIT; Apache-2.0. Output names exactly as in the contract.
- None semantics: Unknown, Other, Not specified, See website, All rights reserved and anything unrecognised give None. When the evidence came from JSON-LD, keep found_in and the snippet. An explicit JSON-LD value is final; an empty value counts as absent; two or more different licences in one stage give None; never invent a version.
- Robustness: never raise.
- How each choice changes the catalog record and the LIC-* flags, including rule_licence's narrow unknown set.
Then STOP and wait for my decisions.

STEP 2, after I approve: implement only in discovery_agent/tools/licence.py. Use the standard library only. Keep jsonld_datasets and summarise_jsonld_dataset unchanged. Use small named helpers, keep lines at 140 characters or fewer, and remove the unused NotImplementedTool import. Show me the full diff.

STEP 3, run in order:
- python -m pytest tests/test_learner_gaps.py -k g1 -q (expect 9 passed)
- python -m pytest tests/ -q (nothing that passed before may fail)
- python -m discovery_agent tool inspect_dataset_link '{"url": "https://archive.ics.uci.edu/dataset/360/air+quality"}' --use-case UC1, and show only the licence object
Then run a throwaway python -c check, not a new test file, on: a JSON-LD dual-licence list; {name: 'Other (specified in description)'}; 'CC-BY-4.0'; https://opendatacommons.org/licenses/odbl/1-0/; http://creativecommons.org/publicdomain/zero/1.0/; a footer-only CC link; 'Released under CC BY.'; 'researchers at MIT'; an OGL link with no version; license: 42. Print the four keys for each.

STEP 4: draft, but do not finalise, the G1 bullet for outputs/artifacts/decisions.md about the Kaggle 'Unknown' case: what the code returns, why it stops there, and how it changes licence.name, url, evidence, commercial_use and unknowns, plus the LIC-UNKNOWN blocker (cite the policy note in config/external_sources_register.json). Label it DRAFT; I will rewrite it in my own words.

### Produce the actual-output evidence for rubric Sheet 2 rows TC-001..TC-005
Do not edit any file. Run python -m pytest tests/test_learner_gaps.py -k g1 -v. Then use a python -c snippet to call discovery_agent.tools.licence.extract_licence on each input the rubric rows TC-001..TC-005 describe: the UCI 321 fixture, the Zenodo fixture, the Kaggle fixture, the three JSON-LD variants, and the OGL, CC BY-NC and no-terms HTML exactly as written in tests/test_learner_gaps.py lines 38-58. Print one JSON line per case. Give me a compact table: TC id, input, actual output, and whether it meets the rubric's expected behaviour. I will paste the outputs and mark Pass or Fail myself.

### Audit licence evidence in the UC1 records after the profile stage (report only)
Report only; never hand-edit outputs/<ID>/ (CLAUDE.md). For every outputs/UC1/records/link.*.json, print source_id, licence.name, licence.url, licence.evidence, licence.commercial_use, and whether 'licence' appears in unknowns. Next to each, print the LIC-* codes for that source from outputs/UC1/rule_flags.json and its verdict and red flags from outputs/UC1/discovery_results.json. Flag: (1) any licence.name outside the normalised vocabulary (for example 'Not specified', 'Other', 'See website'), because rule_licence raises no flag for those; (2) any evidence that does not mention inspect_dataset_link found_in or a probed terms URL; (3) any mismatch with what python -m discovery_agent tool inspect_dataset_link returns for the same URL. Suggest whether a finding could be my G7 fix, and where the cause would be fixed (prompt, tool description, validator or rule). Do not decide for me.

### Resume G1 work in a fresh session without losing context
Read work.md (the G1 section) and CLAUDE.md. Then tell me in 5 bullets where G1 stands: is extract_licence implemented (check discovery_agent/tools/licence.py for the NotImplementedTool stub); what python -m pytest tests/test_learner_gaps.py -k g1 -q reports right now; does outputs/artifacts/pytest_before.txt exist and show 32 passed / 20 failed; does decisions.md have a G1 edge-case entry; and what is the next step in work.md. Do not change any file until I confirm the next step.
