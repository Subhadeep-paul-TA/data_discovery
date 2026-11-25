> Deep-review report written 2026-11-18 by a review agent, for work.md (same folder, one level up).
> It is READ-ONLY analysis of the provided starter code. Paths under /tmp/.../scratchpad mentioned below were temporary and no longer exist.
> Facts marked [V] were verified by reading or running the code; [I] are inferences. Live-site facts were observed on 2026-11-18 and may change.

# Orchestration, CLI, gate decisions, self-check and sign-off (TC-018, TC-021, TC-024; rubric 'Review Judgement' and 'Automatic Scoring')

## SUMMARY
The pipeline runs plan -> scout -> profile -> assess -> memo, and the candidate gate sits inside the profile stage. Every link passed with --links-file or --link needs an exact-URL accept or reject decision, with a reason of at least 20 characters, in outputs/<ID>/gate_decisions.json. When the gate fails in a --from-stage profile run, it stops before any model call, but it still overwrites run_summary.json and appends a line to run_history.jsonl, and the gateway variables must be set. So the TC-018 negative runs belong in a throwaway copy; that procedure was dry-run here and left the real outputs byte-identical. The UC1 link ids are link.uci_360, link.europa_sdg_11_52_099aa6 and link.data_open_air_chicago_hour_aggre_d4970b. `check` prints JSON {use_case, problems, trace_stats} to stdout and exits 1 on any problem; every item it checks and its exact message is listed below. The worst foot-gun: check's 'refused URL retried >2 times' guardrail counts every run in the append-only trace.jsonl. Profiling the Chicago link in a third run therefore makes `check UC1` fail permanently. Transcripts and results are also overwritten on re-runs, so G5/G7 before-states must be snapshotted first. Two more traps: a traced conclusion must name a non-null field reached through dict keys only, and running the UC2 reuse check in the same repo would overwrite the scored outputs/UC2.

## DETAILS
# Orchestration, CLI, candidate gate, `check` and sign-off

**Method.** I read the code in `starter-code/` without changing it, then checked its behaviour in a scratch copy (`scratchpad/work-orch`). I ran the real CLI there, and I also drove `Pipeline` with an offline scripted fake LLM. No gateway call was made, and the only "HTTP" event was a guardrail refusal raised inside the process. "(inference)" marks anything I could not verify without the gateway or the hidden answer key.

## (a) Stages, flags and file I/O

`STAGES = ["plan", "scout", "profile", "assess", "memo"]` (`orchestrator.py:29`). `run` executes the stages from `--from-stage` through `--stop-after` in order (`orchestrator.py:261-271`).

| Stage | Reads (exits if missing) | Writes |
|---|---|---|
| plan | use-case JSON + brief | `search_plan.json`, `transcripts/planner.json` |
| scout | `search_plan.json` | `candidates.json`, `transcripts/scout.json` |
| profile | Runs the candidate gate (section c) if the scout ran in the same invocation, or links were passed, or `candidates_final.json` is missing; otherwise reuses `candidates_final.json` | `candidates_final.json` = `{"candidates":[...], "links":[accepted URLs]}`; for each profiled source, `records/<id>.json` and `transcripts/profiler__<id>.json` (4 in parallel) |
| assess | `candidates_final.json` + the `records/*.json` whose id is listed in it | `rule_flags.json` `{"flags":{id:[...]}, "warnings":[...]}`, `risk_assessment.json`, `transcripts/risk_assessor.json`, `discovery_results.json` |
| memo | `discovery_results.json` + records | `feasibility_memo.md` (agent text plus an appended `## Human review gate` section), `transcripts/memo_writer.json` |

- A missing input stops the run with `<abs path> not found. Run the '<stage>' stage first (or start from an earlier --from-stage).`
- An assess stage with no records stops with `No records found. Run the 'profile' stage first.`
- Every invocation overwrites `run_summary.json` and appends one line to `run_history.jsonl`, even when it fails (the write is in a `finally`, `orchestrator.py:270-282`).
- `totals` in `run_summary.json` covers that one invocation only, and `stages` lists only the stages that completed.
- README:149 and the Helper Guide say `run_history.jsonl` has "one line per stage run". In fact it gets one line per `run` command.

**Flags** (`cli.py:27-70`):
- `--from-stage` / `--stop-after`: choices are the five stages. If the order is reversed, the CLI errors with `--from-stage comes after --stop-after`. `--from-stage assess` also runs memo.
- `--links-file F`: a JSON list of `{url, need_ids, target_windows, note}`. It can be combined with `--link` / `--link-needs` / `--link-windows` triples; unequal counts give `give one --link-needs and one --link-windows per --link, in the same order`.
  - Passing any link makes the profile stage re-run the gate and rebuild `candidates_final.json`.
  - A link's `note` becomes its `why_relevant`, and it gets `found_via: "human input"`.
- `--only a,b`: filters the profile stage only (plus the allowlist warning); assess and memo ignore it. An unknown id just prints `profiling 0 sources`, with no error.
- `--no-input`: never prompt. Prompts also need a TTY (`orchestrator.py:130`), so Claude Code never prompts, but a human terminal does.
- `--no-cache`: skips cache reads but still writes the cache. Live GETs count against `max_requests_per_run` = 150, per invocation.
- `--out DIR`: writes to an alternative output folder.

**What a re-run keeps and what it overwrites**
- `trace.jsonl` is append-only (`trace.py:41`) and never truncated, so every run stays in it.
- `transcripts/<agent>.json` is overwritten whenever that agent runs again (`agent.py:106-113`). Copy any G7 "before" transcript before re-running.
- In `records/`, only the ids that were profiled are rewritten. Other records, including stale ones, are never deleted. Assess ignores ids that are not in `candidates_final.json`, but the e-mail scan in `check` still reads them.
- After a `--stop-after profile` re-profile, `discovery_results.json` and the memo stay stale until you run `--from-stage assess`.
- If the scout is re-run in a separate invocation, a later `--from-stage profile` without `--links-file` prints `reusing candidates_final.json (N candidates); pass --link or --links-file to redo the candidate gate` and ignores the new `candidates.json`.

## (b) Source ids

**Rule** (`tools/links.py:47-67`):
- `canonical_ref`: a UCI page (regex `archive\.ics\.uci\.edu/(?:dataset|ml/datasets)/(\d+)`) becomes `uci:<n>`. Any other URL becomes the lowercase host, plus the path without its trailing slash, plus the query with its parameters sorted.
- Source id: `link.uci_<n>` for UCI pages. Otherwise it is `link.`, then a slug of `<second-to-last host label>_<last path segment>` cut to 32 characters, then `_`, then the first 6 hex characters of sha1(canonical_ref).

| Link | source_id (computed and verified) |
|---|---|
| `https://archive.ics.uci.edu/dataset/360/air+quality` | `link.uci_360` (ref `uci:360`) |
| `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sdg_11_52?format=JSON&lang=EN&geo=IT` | `link.europa_sdg_11_52_099aa6` |
| `https://catalog.data.gov/dataset/open-air-chicago-hour-aggregations` | `link.data_open_air_chicago_hour_aggre_d4970b` |

Query order, a trailing slash and host case do not change the id, but the gate compares URL strings exactly. The old UCI form `.../ml/datasets/Air+Quality` gives a different id, `link.uci_air_quality_04a4dc`. Copy the URLs from `links/UC1_example_links.json` exactly as written.

## (c) The candidate gate (`orchestrator.py:103-181`)

**Order of checks inside the gate**
1. Read `candidates.json`. If it is missing, the run stops with the "not found … 'scout'" message.
2. If any links were passed, `_require_gate_decisions` checks them in links-file order and stops at the first failure. Exact messages:
   - `Missing <out>/gate_decisions.json. Record accept or reject, with a reason, for each dataset link before profiling. Format and rules: README section 9, template links/_TEMPLATE_gate_decisions.json.`
   - `No decision for <url> in <out>/gate_decisions.json. Add accept or reject with a reason.` This also fires for a trailing-slash variant of the URL.
   - `Decision for <url> must be 'accept' or 'reject'.` The check is case-sensitive, so `Accept` fails.
   - `Reason for <url> is too short: give at least 20 characters, in your own words.` The reason is stripped before counting; a missing reason also fails.

   Other behaviour of this check:
   - If two entries share a URL, the last one wins silently.
   - Entries whose URL is not in the links file are ignored.
   - A `"url": null` entry or a top-level list raises `AttributeError`, and broken JSON raises `JSONDecodeError`. Each ends the run with a traceback.
   - Rejected links are dropped: they are not profiled, get no record and do not appear in `dataset_links`.
3. Interactive block (only with a TTY and no `--no-input`): you can drop scout candidates by number and type extra links. Typed links are appended after step 2, so they bypass `gate_decisions.json`. Always use `--no-input`.
4. Accepted links are then validated, with these messages:
   - `Dataset links must be https:// URLs: '<url>'`
   - `<url>: need_ids must be from [...]`
   - `<url>: target_windows must be from [...]`
5. A host that is not allowlisted only produces a warning: `dataset link host '<host>' is not allowlisted; inspection will be refused (gap G6)`. The link is still profiled, and the refusal is recorded as a finding.
6. If no link is accepted, `run_summary.json` gets the warning `no dataset links supplied; external datasets were not assessed (README section 4)`.

**When model calls happen**
- In a `--from-stage profile` run, the gate fails before any model call. Verified: `llm_calls` is 0 and no trace line is added.
- In a full run from `plan`, the gate runs only after plan and scout have already spent model calls.
- `LLM()` is built in `Pipeline.__init__` (`orchestrator.py:73`), so even a run that makes no model call needs `ANTHROPIC_AUTH_TOKEN` (or `ANTHROPIC_API_KEY`).
  - Without one, the run exits before any stage with `No gateway credentials found. Export ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN and ANTHROPIC_MODEL ...`.
  - In that case an empty `outputs/<ID>/` is created and no run summary is written.

**UC2**
- `run --use-case UC2 --no-input` passes no links, so the gate is skipped and no gate file is needed.
- `check UC2` skips the link and gate-file items, because UC2 has `links_expected: false` and an empty `dataset_links`.
- If a Step 2b link is accepted for UC2, it needs all of the following:
  - `outputs/UC2/links.json`, started from `[]`.
  - `outputs/UC2/gate_decisions.json`. Both the pipeline and `check` require it once `dataset_links` is non-empty.
  - An exact allowlist entry for its host.
  - The command `run --use-case UC2 --from-stage profile --links-file outputs/UC2/links.json --no-input`.
- If the reuse check re-runs plan and scout in the same repo, the gate rebuilds `candidates_final.json` from the new `candidates.json`.
  - The scored `outputs/UC2/discovery_results.json`, the memo, the review, the sign-off and the check then all have to be redone.
  - Any new candidate that has no record makes `check` report `candidate <id> has no assessment`.

**Read-only pre-check of the learner's gate file.** It mirrors the gate's logic and writes nothing. Run it with `python - UC1 <<'EOF' … EOF` so no file is added to the repo:
```python
import json, sys
uc = sys.argv[1]
links = [l["url"].strip() for l in json.load(open(f"outputs/{uc}/links.json"))]
decs = json.load(open(f"outputs/{uc}/gate_decisions.json"))["decisions"]
urls = [str(d.get("url") or "").strip() for d in decs]; by = dict(zip(urls, decs))
probs = [f"duplicate: {u}" for u in sorted(set(urls)) if urls.count(u) > 1]
probs += [f"not in links.json (ignored by the gate): {u}" for u in urls if u not in links]
for u in links:
    d = by.get(u)
    if d is None: probs.append(f"No decision for {u}"); continue
    if d.get("decision") not in ("accept", "reject"): probs.append(f"decision must be accept or reject: {u}")
    if len((d.get("reason") or "").strip()) < 20: probs.append(f"reason under 20 characters: {u}")
print(json.dumps({"links": len(links), "accepted": sum(by.get(u, {}).get("decision") == "accept" for u in links), "problems": probs}, indent=2))
```

## (d) `check` (`validation.py:100-212`, `cli.py:95-99`)

**Output format.** `check` prints a JSON object to stdout, indented 2: `{"use_case", "problems": [...], "trace_stats": {...}}`. It writes no files. The exit code is 1 if there are any problems and 0 otherwise. To save it:

`python -m discovery_agent check UC1 | tee outputs/artifacts/check_UC1.json; echo "exit=${PIPESTATUS[0]}"`

**Items, in the order checked, with exact text:**
1. `<abs>/discovery_results.json not found: run the full pipeline through the assess stage to produce it`. When this fires, only the sign-off file checks below are run, and `trace_stats` is `{}`.
2. `candidate <id> has no assessment`: an id in `candidates_final.json` with no entry in the results.
3. `<id>: invalid code <code>`: a red-flag code that is not in `config/red_flags.json`.
4. Only when the record file exists:
   - `<id>: fewer than 3 provenance entries`
   - `<id>: profiling failed`
5. `need <Nx> missing from need_coverage`.
6. When `links_expected` is true (the UC1 default) and no links were assessed: `no dataset links assessed: supply links at the candidate gate (README section 4)`.
7. `rules skipped (learner gaps not done?): [...]`. This fires on a non-empty `rule_warnings`, which means G4 is still open.
8. Only when `dataset_links` is non-empty: `gate_decisions.json not found: record accept or reject, with a reason, for each dataset link (format: links/_TEMPLATE_gate_decisions.json)`. This tests that the file exists and nothing more; `{"decisions": []}` passes.
9. `outputs/artifacts/review_<ID>.md not found or empty: write your memo review`. The file is always read from `<repo>/outputs/artifacts`, even when `--out` is given, and a whitespace-only file counts as empty.
10. `signoff.json not found: record your gate decision, reviewer, conditions and one traced conclusion (format: outputs/artifacts/_TEMPLATE_signoff.json)`
11. Sign-off contents:
    - `signoff.json: reviewer is empty`
    - `signoff.json: verdict must be one of ['proceed', 'proceed_with_conditions', 'stop']`
    - `signoff.json: proceed_with_conditions needs conditions, each with text, owner and due`. The format of `due` is not checked.
    - `signoff.json: list at least one agreement or override, each with a reason`. Only that one of the two lists is non-empty is checked; the reasons inside are not.
    - `signoff.json: traced_conclusion.<source_id|record_field|could_change_if> is empty`
    - `signoff.json: traced_conclusion.could_change_if needs at least 20 characters`
    - `signoff.json: traced_conclusion source <id> is not in discovery_results.json`
    - `signoff.json: no record file for <id>`
    - `signoff.json: field <path> is not in the record for <id>`. The path is followed through dict keys only. A list index such as `provenance.0.claim` fails, and so does a key whose value is null. For example, `licence.name` is null for the Chicago link, while `access.reachable` = `false` passes.
12. `feasibility_memo.md not found`, or `memo missing heading '## 1. Executive summary'` for each missing heading.
13. `<file>: contains something that looks like an email address (personal data must not appear)`. The scan covers only `discovery_results.json`, `feasibility_memo.md` and every `records/*.json`. It does not read signoff, review, risk_assessment, trace or transcripts.
14. `guardrail: refused URL retried <n> times (<url>); the agent should record it, not retry`. This fires when one URL has more than 2 refused events in the whole `trace.jsonl`, counted across all runs, not per run (verified with 3 single-attempt runs).

**`trace_stats`** is computed over the whole trace: `llm_calls`, `input_tokens`, `output_tokens`, `tool_calls`, `tool_errors`, `http_live`, `http_refused`, `refused_hosts`. It also lists `unreachable_links`: dataset links flagged ACC-UNREACHABLE, which are findings, not problems. A missing `trace.jsonl` is not flagged at all.

Before any run, `check UC1` and `check UC2` each list 3 problems (results, review and sign-off all missing) and exit 1.

## (e) `discovery_results.json` and what the hidden key plausibly scores

**Structure** (built by `merge_results`, `orchestrator.py:299-320`):
- Top-level keys: `use_case`, `as_of`, `generated_at`, `model`, `overall_verdict`, `overall_rationale`, `need_coverage`, `sources`, `rule_warnings`, `dataset_links`.
- Each `need_coverage` entry: `need_id`, `status`, `best_sources`, optional `gap`.
- Each `dataset_links` entry: `source_id`, `url`, `canonical_ref`, `need_ids`, `target_windows`.
- Each `sources` entry: `source_id`, `kind`, `title`, `location`, `canonical_ref`, `need_ids`, `target_windows`, `verdict`, `red_flags` (sorted codes), `red_flag_details` (each with `code`, `severity`, `evidence`, `raised_by` = `rule` or `judgement`), `dismissed_rule_flags`, `conditions`, `who_can_resolve`, `rationale`.
- Verdict values: `feasible`, `feasible_with_conditions`, `not_feasible`.
- Coverage status values: `met`, `met_with_conditions`, `partially_met`, `unmet`.

**Likely scoring (inference):**

| Score part | Field it reads | What drives it |
|---|---|---|
| Discovery recall | the set of `sources[].source_id` | Scout candidates plus links accepted at the gate. Dropping a candidate or rejecting a link loses recall. |
| Verdict calibration | `sources[].verdict` | G5 calibration rules and G4 rule flags |
| Red-flag recall | `sources[].red_flags` | G4 rules and the assessor's judgement. Dismissed rule flags are not in `red_flags`. |
| Assessment of each dataset link | `dataset_links` matched by id or `canonical_ref`, plus that source's verdict and flags | All three prescribed URLs must be accepted, spelled exactly as given. The Chicago link should carry ACC-UNREACHABLE. |
| Precision | extra codes or sources | over-flagging |
| Overall verdict | `overall_verdict` | the Risk Assessor's overall call |
| Guardrail penalty | the cumulative `trace.jsonl` | refused-URL retries, budget exhaustion, vendor-feed calls |

`need_coverage` may also be scored. Overrides written in `signoff.json` do not change the scored file. Only fixing the agent and re-running does.

## (f) Memo sections

The validator (`agents.py:122-138`) and `check` require these seven headings, written exactly like this:
- `## 1. Executive summary`
- `## 2. Need coverage`
- `## 3. Source assessments`
- `## 4. Red-flag register`
- `## 5. Conditions and owners`
- `## 6. Recommended next steps`
- `## 7. Open questions for the human reviewer`

The memo must also mention every assessed source id. The schema requires `markdown` of at least 800 characters and at least one item in `open_questions_for_human`.

The orchestrator then appends `## Human review gate`, which contains:
- a checklist;
- the blocker flags on sources that were not rejected;
- the open questions;
- the line `Reviewer: ____ Date: ____ Decision: proceed / proceed with conditions / stop`.

Never fill that line in by hand. The decision belongs in `signoff.json` and `review_<ID>.md`.

## (g) TC-018 without polluting the evidence

**What the three negative runs do and need**
- They leave trace, records, `candidates_final.json` and transcripts untouched.
- Each one overwrites `run_summary.json` (with `llm_calls` 0) and appends a line to `run_history.jsonl`.
- They need `candidates.json`, `links.json` and the gateway variables to be present.

**Recommended procedure.** Run them in a throwaway copy, so the rubric command is used word for word and the real `outputs/UC1` is never touched. I dry-ran this end to end, and the sha1 of the real files was unchanged afterwards.
```bash
REPO=$(pwd); T=$(mktemp -d)/tc018; mkdir -p "$T"
tar -C "$REPO" --exclude=.git --exclude=.venv --exclude=.cache --exclude=__pycache__ -cf - . | tar -C "$T" -xf -
cd "$T"; CMD=(python -m discovery_agent run --use-case UC1 --from-stage profile --stop-after profile --links-file outputs/UC1/links.json --no-input)
llm(){ python -c "import json;print('llm_calls =',json.load(open('outputs/UC1/run_summary.json'))['totals']['llm_calls'])"; }
rm -f outputs/UC1/gate_decisions.json; "${CMD[@]}" 2>&1 | tail -1; llm      # (a) Missing ...gate_decisions.json
python -c "import json;l=json.load(open('outputs/UC1/links.json'));json.dump({'decisions':[{'url':l[0]['url'],'decision':'accept','reason':'TEST FIXTURE ONLY - not a real decision.'}]},open('outputs/UC1/gate_decisions.json','w'))"
"${CMD[@]}" 2>&1 | tail -1; llm                                              # (b) No decision for <Eurostat url>
python -c "import json;l=json.load(open('outputs/UC1/links.json'));d=[{'url':x['url'],'decision':'accept','reason':'TEST FIXTURE ONLY - not a real decision.'} for x in l];d[0]['reason']='too short';json.dump({'decisions':d},open('outputs/UC1/gate_decisions.json','w'))"
"${CMD[@]}" 2>&1 | tail -1; llm                                              # (c) Reason for <UCI url> is too short
cd "$REPO"; python -m pytest tests/test_agent_loop.py -k links -q -p no:cacheprovider   # 1 passed, 6 deselected
```
- Save the console output to `outputs/artifacts/tc018_gate_runs.txt` in the real repo.
- Never copy the test gate files back into the real repo.
- Alternative: add `--out <tmpdir>` to the command and copy `candidates.json` and the test gate files into that folder.

## (h) Foot-guns and the run discipline they imply

1. **Close the gaps before the first real profile run.** G1, G3, G4, G5 and G6 should all be closed (all 52 tests green) first, so the first real profile run is the one that counts.
2. **Limit Chicago profile runs to two.** A well-behaved profiler makes one refused request per run for the Chicago link (`prompts/profiler.md:18`, "and stop"), and refusals add up across runs.
   - Profile Chicago in at most 2 invocations over the life of `outputs/UC1/trace.jsonl`.
   - Re-profile other sources with `--only`, leaving the Chicago id out.
   - Count refused URLs after every run:
     `python -c "import json,collections;c=collections.Counter(e['url'] for e in map(json.loads,open('outputs/UC1/trace.jsonl')) if e.get('kind')=='http' and e.get('refused'));print(c.most_common())"`
3. **Snapshot before any re-run you will cite.** Before a G5 or G7 re-run, copy what it will overwrite into `outputs/artifacts/snapshots/`: a verdict list from `discovery_results.json`, the relevant transcripts and records.
4. **Keep results current.**
   - After any re-profile, run `--from-stage assess`.
   - After re-running the scout, pass both `--links-file outputs/UC1/links.json` and `--only <new or changed ids>`.
5. **Finish in this order, then freeze:** assess -> review -> sign-off -> `check` -> save `check_<ID>.json`. Any later run means re-running `check` and saving it again.
6. **Model usage** for the Submission notes comes from summing all lines of `run_history.jsonl`, not from `run_summary.json`.
7. **SKILL Step 1 item 4 needs a folder.** On a fresh repo, `validate-use-case <ID> | tee outputs/<ID>/use_case_validation.txt` fails with `tee: ...: No such file or directory` (verified). Run `mkdir -p outputs/<ID>` first, and note this in the reuse-check answers.
8. **Always pass `--no-input`.** Links typed at the interactive prompt bypass the gate decisions.

**Tested helper scripts** (scratch only, not in the bundle):
- `/tmp/claude-1000/-mnt-c-Users-Subhadeep-paul-Downloads-806637-Subhadeep-Paul-data-discovery/769f3079-238b-4329-8e4d-d9c978e67fc2/scratchpad/sim/tc018.sh`
- `/tmp/claude-1000/-mnt-c-Users-Subhadeep-paul-Downloads-806637-Subhadeep-Paul-data-discovery/769f3079-238b-4329-8e4d-d9c978e67fc2/scratchpad/sim/gate_precheck.py`
- `/tmp/claude-1000/-mnt-c-Users-Subhadeep-paul-Downloads-806637-Subhadeep-Paul-data-discovery/769f3079-238b-4329-8e4d-d9c978e67fc2/scratchpad/sim/traceable_fields.py` (lists record fields with non-null values, for choosing a traced conclusion)
- `/tmp/claude-1000/-mnt-c-Users-Subhadeep-paul-Downloads-806637-Subhadeep-Paul-data-discovery/769f3079-238b-4329-8e4d-d9c978e67fc2/scratchpad/sim/sim_pipeline.py` (the offline fake-LLM pipeline)

## FACTS
- [V] Stage order is plan -> scout -> profile -> assess -> memo; the candidate gate runs inside the profile stage. :: orchestrator.py:29 STAGES; profile() calls candidate_gate() at orchestrator.py:185-186; driver loop orchestrator.py:261-271
- [V] In a --from-stage profile run a failing gate stops before any model call: run_summary.json totals.llm_calls is 0 and trace.jsonl gets no new line. :: CLI runs (a),(b),(c) in scratch copy printed llm_calls = 0; trace.jsonl stayed at 143 lines before and after
- [V] Exact gate messages: 'Missing <out>/gate_decisions.json. Record accept or reject, with a reason, for each dataset link before profiling. Format and rules: README section 9, template links/_TEMPLATE_gate_decisions.json.' / 'No decision for <url> in <out>/gate_decisions.json. Add accept or reject with a reason.' / 'Decision for <url> must be 'accept' or 'reject'.' / 'Reason for <url> is too short: give at least 20 characters, in your own words.' :: orchestrator.py:109,116,118,120; each reproduced with the real CLI (exit code 1)
- [V] Every run invocation, including one that fails at the gate, overwrites run_summary.json and appends one line to run_history.jsonl. :: orchestrator.py:270-282 (finally -> _summary); 11 failing invocations produced 11 run_history lines
- [V] Without ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY, any run exits before the first stage with 'No gateway credentials found. Export ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN and ANTHROPIC_MODEL (see README.md, 'Setup'). Never paste the token into code or commits.' An empty outputs/<ID>/ folder is created and no run_summary.json is written. :: llm.py:40-47; orchestrator.py:69 (mkdir) and :73 (LLM built in __init__); CLI run with no ANTHROPIC_* variables
- [V] The UC1 dataset links get these source ids: link.uci_360, link.europa_sdg_11_52_099aa6 and link.data_open_air_chicago_hour_aggre_d4970b. Their records are records/<id>.json. :: tools/links.py:47-67 applied to links/UC1_example_links.json; the same ids appeared in the simulated pipeline's records/ and candidates_final.json
- [V] The gate matches URLs by exact string equality after strip(). A trailing slash gives 'No decision for <url>' even though the source id does not change. :: orchestrator.py:110-116; CLI case (e)
- [V] Gate-file edge cases: a duplicate URL entry is resolved last-wins without warning; decision values are case-sensitive ('Accept' fails); a missing reason counts as too short. A 'url': null entry, invalid JSON or a top-level list crash with a traceback. :: orchestrator.py:110,117,119; CLI cases (d),(g),(h),(i),(j); duplicate case in the Python simulation
- [V] check prints JSON {use_case, problems, trace_stats} to stdout, writes nothing, and exits 1 if there is any problem, 0 otherwise. Before any run, check UC1 and check UC2 each list 3 problems. :: cli.py:95-99; check UC1 and check UC2 run on the starter copy
- [V] check's guardrail item counts refused HTTP events per URL across the whole append-only trace.jsonl. Three separate runs that each make one refused request to the Chicago URL produce 'guardrail: refused URL retried 3 times (https://catalog.data.gov/dataset/open-air-chicago-hour-aggregations); the agent should record it, not retry'. :: validation.py:193-210 with trace.py:41 (append mode); reproduced with 3 simulated profile runs
- [V] On a re-run, transcripts are overwritten for each agent that runs again, records are overwritten only for the ids profiled in that run, and trace.jsonl is appended to. :: agent.py:106-113; orchestrator.py:203; trace.py:41; after an --only re-profile only records/link.uci_360.json changed its mtime
- [V] --only with an unknown id profiles 0 sources and raises no error. --only has no effect on the assess or memo stages. :: orchestrator.py:190-191; simulation printed 'profiling 0 sources (4 in parallel)'
- [V] If the scout is re-run in an earlier invocation, a later --from-stage profile run without --links-file reuses the old candidates_final.json and ignores the new candidates.json. :: orchestrator.py:185-189 (_ran_scout is only set inside the same invocation); message observed: 'reusing candidates_final.json (5 candidates); pass --link or --links-file to redo the candidate gate'
- [V] check only tests that gate_decisions.json exists (and only when dataset_links is non-empty). It does not check that every link is covered or that reasons are long enough. :: validation.py:102-103; a gate file of {"decisions": []} produced no gate problem in the simulation
- [V] traced_conclusion.record_field must resolve through dict keys to a non-null value. A null value or a list index fails with 'signoff.json: field <f> is not in the record for <id>'. Values false, [] or 0 pass. :: validation.py:91-97 and 141-142; simulated cases: temporal.end=null and provenance.0.claim failed, access.reachable=false passed
- [V] check requires only that the agreements or overrides list is non-empty; the reasons inside entries are not validated. Conditions (text, owner, due) are required only for proceed_with_conditions, and the format of due is not checked. :: validation.py:122-127; simulated sign-off variants
- [V] The e-mail scan in check covers only discovery_results.json, feasibility_memo.md and every records/*.json, including stale record files. :: validation.py:190-192; planted values were flagged in the memo and a stale record but not in signoff.json, risk_assessment.json or review_UC1.md
- [V] UC2 with no links needs no gate file. The run warns 'no dataset links supplied; external datasets were not assessed (README section 4)', and check UC2 does not ask for links because links_expected is false. :: use_cases/UC2_ice_cream.json (links_expected: false); validation.py:177; simulated candidate_gate and check UC2
- [V] If UC2 gets an accepted Step 2b link, the pipeline stops with 'Missing .../outputs/UC2/gate_decisions.json ...', and check requires that file once dataset_links is non-empty. :: simulated UC2 candidate_gate with one link; validation.py:102
- [V] Links typed at the interactive prompt (a TTY and no --no-input) are appended after the gate check, so they bypass gate_decisions.json. :: orchestrator.py:129 (gate check) versus orchestrator.py:145-151 (links.append)
- [V] The memo must contain the 7 exact headings, mention every assessed source id, have markdown of at least 800 characters and at least one open question. The orchestrator then appends a '## Human review gate' section. :: agents.py:122-138; memo.schema.json:8-9; orchestrator.py:256 and 323-338
- [V] 'pytest tests/test_agent_loop.py -k links' selects only test_links_need_a_recorded_gate_decision, and it passes on the starter code. The full baseline is 20 failed, 32 passed. :: ran in scratch copy: 1 passed, 6 deselected; full suite 20 failed, 32 passed
- [V] validate-use-case prints 'UC1: OK' and 'UC2: OK' with exit 0. An unknown id prints "no use_cases/*.json with id 'UC9' (found ['UC1', 'UC2'])" with exit 1. :: ran in scratch copy
- [V] SKILL Step 1 item 4 ('validate-use-case <ID> | tee outputs/<ID>/use_case_validation.txt') does not write its file on a fresh repo, because outputs/<ID>/ does not exist yet. :: SKILL.md:110; reproduced: 'tee: outputs/UC_fresh_none/use_case_validation.txt: No such file or directory', PIPESTATUS 0 1
- [V] The README and Helper Guide say run_history.jsonl has one line per stage run. The code writes one line per run invocation, including failed ones. :: README.md:149 and 251; Helper Guide Commands section; orchestrator.py:281-282
- [V] A profiler failure becomes a failed_record (quality_notes 'PROFILING FAILED', 1 provenance entry), which check reports as '<id>: fewer than 3 provenance entries' and '<id>: profiling failed'. An AgentFailed in plan, scout, assess or memo is not caught and ends the run with a traceback (run_summary.json is still written). :: orchestrator.py:198-203 and 288-296; validation.py:166-172; simulation (a Europa profiler failure and a scout AgentFailed traceback)
- [V] check does not flag a missing trace.jsonl; trace_stats then holds only unreachable_links. :: validation.py:193-211; simulated UC2 check without a trace file
- [I] The hidden scorer probably matches dataset links by source_id or canonical_ref, compares sources[].verdict, sources[].red_flags and overall_verdict with the key, and applies guardrail penalties from the cumulative trace.jsonl. :: Assignment doc Evaluation row; README.md:216; trace.py docstring ('the instructor scorer reads it to check guardrails'). Not verifiable without the hidden key.

## TASKS
- **UC1 Steps 0-2 via the skill: plan and scout, then stop at the candidate gate** (learner_with_claude_help) done_when: outputs/UC1/ contains search_plan.json, candidates.json, trace.jsonl, transcripts/planner.json, transcripts/scout.json, run_summary.json and links.json (a verbatim copy of the 3 prescribed links). step0_checks.md exists without the token, and the learner has confirmed the needs.
    - Start a NEW Claude Code session in the repo root after setup: venv active, the three gateway variables exported in the same shell, and SKILL.md copied to .claude/skills/data-discovery-agent/. Skills are discovered at session start (inference).
    - Paste prompt P1. Claude runs the Step 0 checks (printing booleans only, never the token), pytest (expect 52 collected, 32 passed, 20 gap tests failed) and the tool smoke tests, then writes outputs/artifacts/step0_checks.md.
    - Step 1: run mkdir -p outputs/UC1 first, then validate-use-case UC1 piped to tee (expect 'UC1: OK'). STOP: the learner confirms the needs table.
    - Step 2: Claude runs the scout command. Expect stderr 'Stopped after scout. Review .../candidates.json, then run --from-stage profile.'
    - STOP: the learner says whether to use the prescribed links. Only then does Claude create outputs/UC1/links.json with cp -n, which never overwrites an existing file.
    - `python -c "import os;print({k: bool(os.environ.get(k)) for k in ['ANTHROPIC_BASE_URL','ANTHROPIC_AUTH_TOKEN','ANTHROPIC_MODEL']})"`
    - `mkdir -p outputs/UC1 && python -m discovery_agent validate-use-case UC1 | tee outputs/UC1/use_case_validation.txt`
    - `python -m discovery_agent run --use-case UC1 --stop-after scout --no-input`
    - `cp -n links/UC1_example_links.json outputs/UC1/links.json`
    - REVIEW: candidates.json source ids exist in internal/UC1_valdena_health/catalog_export.json (airq.station_readings, traffic.hourly_counts, clinic.resp_visits_daily, clinic.patient_visits) and the register (api.open_meteo_archive, api.nager_public_holidays, vendor.atmosdata_pro)
    - REVIEW: unmet_needs and the planner's external_data_hints
    - REVIEW: G7 lead: did the Scout read the wiki note about station VR-03?
- **Learner writes outputs/UC1/gate_decisions.json; Claude pre-checks it read-only** (learner_with_claude_help) done_when: The pre-check prints "problems": [], with links = number of entries in links.json and accepted = the learner's intended count (3 or more).
    - Inspect each link without the LLM. The tool command is not traced, so it does not count against the refused-URL guardrail.
    - After G6 adds ec.europa.eu, re-inspect the Eurostat link before deciding it.
    - The learner copies the template and writes one entry per URL in outputs/UC1/links.json. The URL is copied character for character, decision is lowercase 'accept' or 'reject', and the reason is at least 20 characters in the learner's own words.
    - The Chicago link is accepted on purpose (the rubric requires it). Rejecting the UCI or Eurostat link would remove it from the automatic per-link assessment.
    - Claude runs the read-only pre-check heredoc from details (c) and reports any problems. The learner fixes their own file; Claude never writes reasons.
    - `python -m discovery_agent tool inspect_dataset_link '{"url": "https://archive.ics.uci.edu/dataset/360/air+quality"}' --use-case UC1`
    - `python -m discovery_agent tool inspect_dataset_link '{"url": "https://catalog.data.gov/dataset/open-air-chicago-hour-aggregations"}' --use-case UC1`
    - `cp -n links/_TEMPLATE_gate_decisions.json outputs/UC1/gate_decisions.json`
    - REVIEW: Reasons are the learner's own words and match review_UC1.md
    - REVIEW: No URL has been re-spelled (no trailing slash, query order unchanged)
- **TC-018 negative gate runs in a throwaway copy** (claude_then_learner_review) done_when: (a) prints 'Missing ...gate_decisions.json', (b) 'No decision for https://ec.europa.eu/...', (c) 'Reason for https://archive.ics.uci.edu/dataset/360/air+quality is too short...'; llm_calls = 0 three times; pytest shows 1 passed; the real outputs' sha1 is unchanged.
    - Prerequisites: outputs/UC1/candidates.json and links.json exist, and the gateway variables are exported (no model call is made).
    - Run the procedure in details (g) inside a mktemp copy. Test gate files are labelled TEST FIXTURE ONLY and are never copied back.
    - Run pytest tests/test_agent_loop.py -k links in the real repo.
    - Save all console output to outputs/artifacts/tc018_gate_runs.txt. Record sha1 of the real outputs/UC1/run_summary.json and gate_decisions.json before and after to show they are unchanged.
    - The learner pastes the output into rubric Sheet 2, row TC-018, and marks Pass or Fail.
    - `bash tc018.sh (body in details (g))`
    - `python -m pytest tests/test_agent_loop.py -k links -q -p no:cacheprovider`
    - `sha1sum outputs/UC1/run_summary.json outputs/UC1/gate_decisions.json`
    - REVIEW: The evidence file contains no token, only paths under the temporary directory
    - REVIEW: No test gate file leaked into the real repo
- **Real UC1 profile -> assess -> memo run, once G1/G3/G4/G5/G6 are closed** (claude_then_learner_review) done_when: discovery_results.json lists link.uci_360, link.europa_sdg_11_52_099aa6 and link.data_open_air_chicago_hour_aggre_d4970b in dataset_links and sources; feasibility_memo.md has all 7 headings; Chicago refused count is 1 or less.
    - Check preconditions: pytest shows 52 passed; config/allowlist.json contains ec.europa.eu, no catalog.data.gov, and no wildcard or parent domain; config/settings.json matches the starter copy; the gate pre-check passes.
    - Record line counts of run_history.jsonl and trace.jsonl and the refused-URL counts.
    - Run the profile command with --links-file and --no-input.
    - After the run, check: run_summary warnings, no 'PROFILING FAILED' record, rule_warnings empty, the 3 link ids in dataset_links, and the Chicago refused count of 1 or less.
    - Snapshot verdicts and flags to outputs/artifacts/snapshots/ before any later re-run (G5/G7 before-state).
    - `python -m pytest tests/ -q`
    - `python -m discovery_agent run --use-case UC1 --from-stage profile --links-file outputs/UC1/links.json --no-input`
    - `python -c "import json,collections;c=collections.Counter(e['url'] for e in map(json.loads,open('outputs/UC1/trace.jsonl')) if e.get('kind')=='http' and e.get('refused'));print(c.most_common())"`
    - REVIEW: The Chicago link shows ACC-UNREACHABLE (a finding, not an error)
    - REVIEW: No record contains anything resembling an e-mail address
    - REVIEW: The verdicts look defensible before the G5 tuning
- **Iterate safely (G5 re-assess, G7 re-run) without polluting evidence** (claude_then_learner_review) done_when: The decisions.md G5 and G7 entries cite the snapshot files and trace lines, and the Chicago refused count stays at 2 or less.
    - Before each re-run you will cite, copy the files it overwrites (transcripts/<agent>.json, records/<id>.json, a verdict list from discovery_results.json) into outputs/artifacts/snapshots/<tag>/.
    - Re-profile with --from-stage profile --stop-after profile --only <ids>, leaving out the Chicago id; then --from-stage assess.
    - After re-running the scout, use --from-stage profile --stop-after profile --links-file outputs/UC1/links.json --only <new/changed ids>, then --from-stage assess.
    - Never re-profile the Chicago link without the learner's OK. It may be profiled in at most 2 invocations in the lifetime of the trace.
    - After every re-run, re-run check.
    - `python -m discovery_agent run --use-case UC1 --from-stage profile --stop-after profile --only link.uci_360`
    - `python -m discovery_agent run --use-case UC1 --from-stage assess --no-input`
    - REVIEW: Each fix is at its cause (prompt, tool description, validator or rule), never an edited output
    - REVIEW: Measured before/after numbers come from the snapshots and run_history.jsonl
- **UC2 run, and deciding where the reuse check runs** (claude_then_learner_review) done_when: outputs/UC2 contains discovery_results.json, feasibility_memo.md, trace.jsonl, transcripts/ and records/, and check UC2 lists only the learner-file problems (review and sign-off) before sign-off.
    - Run the full UC2 command with --no-input. No links file and no gate file are needed.
    - Expect the run_summary warning 'no dataset links supplied; external datasets were not assessed (README section 4)'.
    - Before Task 10, the learner decides where the reuse check runs (separate clone or worktree is recommended).
    - If a Step 2b link is accepted and profiled into outputs/UC2: create outputs/UC2/links.json starting from [], the learner writes outputs/UC2/gate_decisions.json, add the exact host under G6, run --from-stage profile --links-file outputs/UC2/links.json --no-input, then redo the UC2 review, sign-off and check.
    - `python -m discovery_agent run --use-case UC2 --no-input`
    - `python -m discovery_agent check UC2`
    - REVIEW: overall_verdict and the verdict for each source
    - REVIEW: Whether the 2024 product-code change and the till migration are caught (wiki pages)
- **Memo reviews: outputs/artifacts/review_UC1.md and review_UC2.md** (learner_with_claude_help) done_when: Both files exist and are non-empty, and each covers agreements, overrules, a verdict per link and the gate decision.
    - Claude builds an evidence pack in chat only (prompt P6): for each source, its verdict, flags with evidence, dismissed flags, the record fields behind them, provenance count and trace refusals.
    - The learner writes each review in their own words covering: the gate decision; a verdict per dataset link (UCI, Eurostat, Chicago, plus any Step 2b link); agreements with reasons; overrules with reasons; what the agent got wrong or missed; and one conclusion traced from record field to verdict.
    - State that overrides do not change the scored discovery_results.json.
    - REVIEW: No text drafted by Claude is presented as the learner's judgement
    - REVIEW: Contains no personal data or e-mail addresses
- **Sign-off: outputs/UC1/signoff.json and outputs/UC2/signoff.json** (learner_with_claude_help) done_when: check lists no 'signoff.json:' problems for either use case.
    - Copy outputs/artifacts/_TEMPLATE_signoff.json to outputs/<ID>/signoff.json.
    - The learner fills in reviewer, verdict (proceed, proceed_with_conditions or stop), conditions (each with text, owner and due as YYYY-MM-DD) if proceeding with conditions, at least one agreement or override with a reason, and traced_conclusion.
    - Claude lists the record's fields that have non-null values, reachable through dict keys only, so the chosen record_field passes. Avoid null fields and list indexes.
    - Run check; fix only the learner's own fields.
    - `cp -n outputs/artifacts/_TEMPLATE_signoff.json outputs/UC1/signoff.json`
    - `python -m discovery_agent check UC1`
    - REVIEW: traced_conclusion.source_id is an id in discovery_results.json, e.g. link.uci_360
    - REVIEW: could_change_if is at least 20 characters and specific
- **Run check, save check_UC1.json and check_UC2.json, then freeze outputs** (claude_then_learner_review) done_when: Both saved files show "problems": [] and the command printed exit=0.
    - Run both checks with tee; the saved file is pure JSON from stdout.
    - Classify each problem as an agent/pipeline issue (fix at the cause, then the narrowest re-run) or a learner-file issue (the learner fixes it).
    - Repeat until problems is []; then make no more runs in outputs/UC1 or outputs/UC2. If anything is re-run, re-run check and re-save.
    - `python -m discovery_agent check UC1 | tee outputs/artifacts/check_UC1.json; echo exit=${PIPESTATUS[0]}`
    - `python -m discovery_agent check UC2 | tee outputs/artifacts/check_UC2.json; echo exit=${PIPESTATUS[0]}`
    - REVIEW: trace_stats.refused_hosts contains catalog.data.gov (expected finding)
    - REVIEW: unreachable_links lists the Chicago id
- **TC-021 and TC-024 evidence and rubric cells** (learner_with_claude_help) done_when: With the token variable set, grep exits 1 (no match) and both checks are clean.
    - TC-021: cite check_UC1.json and check_UC2.json with no problems, and name the traced source and field.
    - TC-024: confirm check reports no e-mail-like values. Then grep the final submission folder for the token value, listing file names only so the token is never printed.
    - Save a short summary (no token) to outputs/artifacts/tc024_secret_scan.txt. The learner pastes it into rubric Sheet 2 and marks Pass or Fail.
    - `python -c "import os;print(bool(os.environ.get('ANTHROPIC_AUTH_TOKEN')))"`
    - `grep -rIlF -f <(printenv ANTHROPIC_AUTH_TOKEN) --exclude-dir=.git --exclude-dir=.venv --exclude=.env . ; echo grep_exit=$?`
    - REVIEW: Run the grep on the folder that will be zipped
    - REVIEW: If the token variable is empty, the grep proves nothing

## RISKS
- The cumulative refused-URL count for the Chicago link reaches 3 across runs. check UC1 can then never list zero problems, and the hidden scorer may apply a guardrail penalty. | Blocks 'check lists no problems' (TC-021, Review Judgement, 16 pts) and may cost automatic points (40 pts). | Profile the Chicago link in at most 2 invocations, use --only for re-profiles, and count refused URLs after every run. If the count still reaches 3, ask the learner before archiving outputs/UC1 outside the submission and doing one clean full re-run that reuses the learner's links.json and gate_decisions.json.
- TC-018 negative runs or other experiments overwrite real evidence in outputs/UC1 (run_summary.json, the learner's gate_decisions.json). | Loss or alteration of learner-authored decisions; a misleading run_summary. | Run TC-018 in a throwaway tar copy (details g), or use --out with a temporary folder. Verify with sha1 that the real files are unchanged.
- The UC2 reuse check, run in the same repo, re-runs plan and scout (and maybe profiling) into outputs/UC2 after the review, sign-off and check are done. | The scored discovery_results.json changes; check UC2 may report 'candidate <id> has no assessment'; the review and sign-off become stale. | Run the reuse check in a separate git worktree or clone. If it must be in the same repo, do it before the final UC2 review and sign-off, and redo them afterwards.
- G5/G7 before-state is lost because transcripts, records, discovery_results.json and the memo are overwritten on re-run. | Weak or unverifiable before/after evidence for G5 (5 pts) and G7 (10 pts). | Snapshot the relevant files into outputs/artifacts/snapshots/<tag>/ before every cited re-run, and cite trace.jsonl lines (append-only).
- Stale outputs: a re-profile without re-running assess, or a re-scout followed by a profile run without --links-file (the old candidates_final.json is silently reused). | The memo and results disagree with the records; check may pass on stale data. | Always finish with --from-stage assess; after re-scouting, pass --links-file together with --only.
- A prescribed UC1 link is rejected or re-spelled (trailing slash, old UCI URL). | That link is missing from the automatic per-link assessment, or gets a different source id. | Use the URLs from links/UC1_example_links.json exactly; the rubric requires Chicago to be accepted.
- The traced conclusion names a field whose value is null, or a list index. | check fails with the misleading message 'field X is not in the record'. | Use the traceable-fields helper; choose a field with a non-null value reached through dict keys only.
- Claude writes learner-owned content (gate reasons, sign-off decisions, review text). | Violates the assignment constraints; Review Judgement and Governance marks at risk. | Claude only transcribes reasons the learner dictated, word for word, and says so in decisions.md. Otherwise Claude provides evidence and validation only.
- The token value leaks into evidence files, for example by being pasted into a prompt that is then saved in a transcript. | Submission rule violation. | Never paste the token; run the filename-only grep on the folder to be zipped before submitting.

## ISSUES
- [high] check's guardrail counts refused requests per URL across every run in the append-only trace, not per run. A well-behaved profiler that tries the Chicago link once per run still produces a check problem after the third run. | EVIDENCE: validation.py:193-210; trace.py:41 (open 'a'); profiler.md:18 says stop after a refusal. Simulation: three runs gave 'guardrail: refused URL retried 3 times (https://catalog.data.gov/dataset/open-air-chicago-hour-aggregations)' | REC: Plan at most 2 profile invocations that include the Chicago id; use --only for everything else; monitor the counter after each run. Do not edit the trace.
- [medium] Transcripts and result files are overwritten on re-run, so the 'before' side of G7/G5 evidence disappears unless it is copied first. | EVIDENCE: agent.py:106-113 (write_text in finally); orchestrator.py:203, 241, 244, 257 | REC: Snapshot transcripts, records and verdict lists into outputs/artifacts/snapshots/ before each cited re-run; cite trace.jsonl lines, which persist.
- [medium] When the scout was re-run in a separate invocation, a later profile run without --links-file silently reuses the stale candidates_final.json. | EVIDENCE: orchestrator.py:185-189; observed message 'reusing candidates_final.json (5 candidates); pass --link or --links-file to redo the candidate gate' | REC: After any scout re-run, pass --links-file outputs/<ID>/links.json, with --only for the new or changed ids.
- [medium] check only tests that gate_decisions.json exists, although its message says 'for each dataset link'. Coverage and reason length are enforced only at pipeline time. | EVIDENCE: validation.py:102-103; {"decisions": []} passed check in the simulation | REC: Run the read-only gate pre-check (details c) before the final check, and keep gate_decisions.json consistent with links.json.
- [medium] _dotted() treats a null value like a missing key, so check reports a field that exists as 'not in the record'. List indexes are not supported. | EVIDENCE: validation.py:91-97 and 141-142; temporal.end=null and provenance.0.claim failed in the simulation | REC: Choose a traced field whose value is non-null and reached through dict keys only (helper traceable_fields.py).
- [medium] Links typed at the interactive candidate-gate prompt bypass gate_decisions.json, and interactive 'drop' choices are recorded nowhere. | EVIDENCE: orchestrator.py:129-151 | REC: Always use --no-input with --links-file outputs/<ID>/links.json.
- [medium] Running the UC2 reuse check in the same repo re-runs plan and scout into outputs/UC2 and, if a link is profiled, rebuilds candidates_final.json. That changes the scored results and requires a UC2 gate file. | EVIDENCE: SKILL.md Step 2 item 1 and Step 2b; orchestrator.py:185-186; validation.py:102 and 159-161 | REC: Run the reuse check in a separate worktree or clone, or redo the UC2 review, sign-off and check afterwards.
- [low] --only with an unknown or typo'd id profiles nothing and gives no error; it still appends a line to run_history.jsonl. | EVIDENCE: orchestrator.py:190-191; simulation printed 'profiling 0 sources' | REC: Copy ids from candidates_final.json; check the 'profiling N sources' line.
- [low] README and the Helper Guide say run_history.jsonl keeps 'one line per stage run'. It actually keeps one line per run invocation, including failed gate runs, while run_summary.json holds only the last invocation. | EVIDENCE: README.md:149 and 251; orchestrator.py:277-282 | REC: For the delivery reflection, sum all run_history lines (one-liner in the details) and mention any failed or no-LLM runs.
- [low] The gate file is fragile: a duplicate URL resolves last-wins silently; 'url': null, invalid JSON or a top-level list crash with a traceback instead of a friendly message. | EVIDENCE: orchestrator.py:110; CLI cases (g),(h),(i) | REC: Validate with json.tool and the pre-check before running.
- [low] check does not validate that each agreement or override has a reason, although the template and the error message say so. | EVIDENCE: validation.py:126-127 | REC: Give every agreement and override a reason anyway; Review Judgement is graded by hand.
- [low] check does not flag a missing trace.jsonl, although traces are a required deliverable and are used for guardrail scoring. | EVIDENCE: validation.py:193-211; simulated check UC2 without a trace showed no error | REC: Verify by hand that outputs/UC1/trace.jsonl and outputs/UC2/trace.jsonl exist before zipping.
- [low] SKILL Step 1 item 4 pipes validate-use-case into tee outputs/<ID>/use_case_validation.txt, which fails on a fresh repo because the folder does not exist yet. | EVIDENCE: SKILL.md:110; reproduced 'tee: ...: No such file or directory' | REC: Run mkdir -p outputs/<ID> first, and record this in the reuse-check answer ('steps that could not be followed as written').
- [low] Runs that make zero model calls (TC-018) still need gateway credentials, because LLM() is built in Pipeline.__init__. outputs/<ID>/ is created even when the run exits for lack of credentials. | EVIDENCE: orchestrator.py:69 and 73; llm.py:40-47 | REC: Export the gateway variables before the TC-018 runs; no call is made.
- [low] A full run from plan that includes --links-file checks the gate only after plan and scout have spent model calls and overwritten search_plan.json and candidates.json. | EVIDENCE: orchestrator.py:261-268 and 185-186 | REC: Use the README order: --stop-after scout, write the gate file, then --from-stage profile.
- [low] Gate and check messages embed absolute local paths, which can expose a local username in pasted evidence. | EVIDENCE: orchestrator.py:51 and 109; validation.py:152 | REC: Run TC-018 in a /tmp copy; saved check files are clean when problems is empty.
- [low] The memo's appended human gate ends with 'Reviewer: ____ Date: ____ Decision: ...' inside an output file, which invites hand-editing. | EVIDENCE: orchestrator.py:337 | REC: Never fill it in; record the decision in signoff.json and review_<ID>.md.

## QUESTIONS
- [BLOCKING] Will you accept all three prescribed UC1 links at the gate? The rubric requires the Chicago link to be accepted, and rejecting the UCI or Eurostat link removes it from the automatic per-link assessment. | why: Only accepted links are profiled and scored, and this decision must be yours. | default: Claude does not run the UC1 profile stage until your own gate_decisions.json exists and passes the read-only pre-check; it is used exactly as you wrote it.
- [non-blocking] For TC-018, may Claude run the three negative gate runs in a throwaway copy of the repo and write synthetic test gate files there, labelled 'TEST FIXTURE ONLY'? | why: Running them in the real outputs/UC1 would overwrite run_summary.json and risk your real gate file. The test files are fixtures, not decisions. | default: Yes: use a throwaway copy, never copy anything back, and save the console output to outputs/artifacts/tc018_gate_runs.txt.
- [non-blocking] Where should the UC2 reuse check run: a separate git worktree or clone (keeping the scored outputs/UC2 stable), or this repo (meaning the UC2 review, sign-off and check are redone afterwards)? | why: The reuse check re-runs plan and scout and may profile a Step 2b link, which changes outputs/UC2 and requires a UC2 gate file. | default: A separate worktree or clone after UC2 is final. Decisions and answers go into decisions.md and the README Submission notes; copy its outputs into outputs/artifacts/reuse_check_UC2/ only if you want them as evidence.
- [non-blocking] If the Chicago URL's refused count in outputs/UC1/trace.jsonl reaches 3 (check then fails permanently), may Claude move outputs/UC1 to an archive outside the submission and do one clean full re-run, reusing your links.json and gate_decisions.json? | why: The trace is append-only and must not be hand-edited; a clean regenerated run is the only way back to 'no problems'. | default: Avoid it by limiting Chicago profile runs; if it happens anyway, stop and ask before moving or deleting anything.
- [non-blocking] May Claude save snapshot copies of discovery_results.json verdicts, transcripts and records under outputs/artifacts/snapshots/ before G5 and G7 re-runs? | why: Re-runs overwrite these files, and the decisions log needs measured before/after evidence. | default: Yes. Snapshots are copies, never edits, and are cited in decisions.md.

## PROMPTS
### (1) Run UC1 up to the scout and stop at the candidate gate (skill session)
Use the data-discovery-agent skill (.claude/skills/data-discovery-agent/SKILL.md) and run Steps 0-2 for UC1 only. Never print ANTHROPIC_AUTH_TOKEN; check the three gateway variables with the boolean one-liner from Step 0. Before Step 1 item 4, run mkdir -p outputs/UC1 so the tee works. Step 2 command: python -m discovery_agent run --use-case UC1 --stop-after scout --no-input. When it finishes, show me: the needs table; a need -> candidate source ids table from outputs/UC1/candidates.json, with unmet_needs and the planner's external_data_hints; and the totals and warnings from outputs/UC1/run_summary.json. Then STOP at Step 2 item 4 and wait for my answer. If I say I will use the prescribed links, run cp -n links/UC1_example_links.json outputs/UC1/links.json and never overwrite an existing links.json. Do not write outputs/UC1/gate_decisions.json, do not add hosts to config/allowlist.json, and do not edit any file under outputs/UC1/.

### (2) Profile -> assess -> memo for UC1 after I have written gate_decisions.json
I have written outputs/UC1/gate_decisions.json myself. Do not modify it or write any reason in it. Step 1: run a read-only pre-check, as a python heredoc so no file is added, comparing every url in outputs/UC1/links.json with my decisions: exact string match after strip, decision exactly accept or reject, reason at least 20 characters after strip, and no duplicate or extra entries. Show the result and stop if anything fails. Step 2: confirm that python -m pytest tests/ -q shows 52 passed, that config/allowlist.json has no catalog.data.gov and no wildcard or parent domain, and that config/settings.json matches the starter copy. Step 3: note the current line counts of outputs/UC1/run_history.jsonl and trace.jsonl and the refused-URL counts in the trace. Step 4: run python -m discovery_agent run --use-case UC1 --from-stage profile --links-file outputs/UC1/links.json --no-input. Step 5: report the profiled source ids (link.uci_360, link.europa_sdg_11_52_099aa6 and link.data_open_air_chicago_hour_aggre_d4970b should be among them), the run_summary warnings, any PROFILING FAILED record, rule_warnings, the refused-URL counts per URL (warn me if any URL is at 2 or more), and a table of source_id, verdict and red_flags plus overall_verdict from discovery_results.json. Never hand-edit anything under outputs/UC1. If something looks wrong, propose a fix at the cause (prompt, tool description, validator or rule) and the narrowest re-run command, and never re-profile the Chicago link without asking me.

### (3) Run check and save check_<ID>.json
Run python -m discovery_agent check UC1 | tee outputs/artifacts/check_UC1.json; echo exit=${PIPESTATUS[0]} and the same for UC2 into outputs/artifacts/check_UC2.json. Sort each problem into one of two kinds. (a) Pipeline or agent issue: propose the fix at its cause and the narrowest re-run, without editing anything under outputs/<ID>/. (b) One of my own files (signoff.json, review_<ID>.md, gate_decisions.json): tell me which field fails and which rule it breaks, but do not write my decisions, reasons, agreements, overrides or could_change_if text. For a traced_conclusion problem, list the dotted fields of that record that have a non-null value reached through dict keys only. After any change or re-run, run check again and overwrite the saved file. Done when both files show problems [] and exit=0. Show me the final trace_stats for both.

### Reproduce rubric TC-018 safely in a throwaway copy
Reproduce rubric TC-018 without touching my real outputs/UC1. First record sha1sum of outputs/UC1/run_summary.json and outputs/UC1/gate_decisions.json. Make a throwaway copy of the repo in a mktemp directory using tar, excluding .git, .venv, .cache and __pycache__. Inside the copy only: (a) delete outputs/UC1/gate_decisions.json; (b) write a test gate file that covers only the first link in outputs/UC1/links.json; (c) write a test gate file that covers every link but has one reason under 20 characters. Label every test reason TEST FIXTURE ONLY. After each one, run python -m discovery_agent run --use-case UC1 --from-stage profile --stop-after profile --links-file outputs/UC1/links.json --no-input from the copy's root, and print the last stderr line and totals.llm_calls from the copy's run_summary.json. Then, in the real repo, run python -m pytest tests/test_agent_loop.py -k links -q -p no:cacheprovider. Save all of this output to outputs/artifacts/tc018_gate_runs.txt in the real repo, show that the sha1 values of the real files did not change, and delete the throwaway copy.

### Run UC2 end to end (no dataset links)
Run python -m discovery_agent run --use-case UC2 --no-input. UC2 has no dataset links, so no gate file is needed. First note the line counts of outputs/UC2/run_history.jsonl and trace.jsonl if they exist. Afterwards report: the run_summary warnings (the 'no dataset links supplied' warning is expected), any PROFILING FAILED record, rule_warnings, and a table of source_id, verdict and red_flags plus overall_verdict from outputs/UC2/discovery_results.json. Do not create outputs/UC2/links.json or gate_decisions.json unless I accept a Step 2b link for UC2 and tell you so, and do not edit anything under outputs/UC2/.

### Evidence pack for my memo review (I write the review myself)
Build me an evidence pack for reviewing outputs/UC1/feasibility_memo.md, in chat only, without writing to outputs/. For each source in outputs/UC1/discovery_results.json give: its verdict; each red flag with its evidence and raised_by; dismissed_rule_flags with their reasons; and the record fields behind it (temporal.start, temporal.end, temporal.grain, licence.name, licence.evidence, access.reachable, ownership.owner, unknowns, provenance count), quoted from outputs/UC1/records/<id>.json. Also give any refused HTTP events for that source in trace.jsonl. Then list memo claims that cite no source or disagree with the records, and record fields that would pass check as a traced_conclusion (non-null values reached through dict keys only). Do not write review_UC1.md or signoff.json: I write them.

### TC-024 secret and personal-data scan without printing the token
For TC-024, without ever printing the token: check that ANTHROPIC_AUTH_TOKEN is set, printing only true or false. Then run grep -rIlF -f <(printenv ANTHROPIC_AUTH_TOKEN) --exclude-dir=.git --exclude-dir=.venv --exclude=.env . and report only matching file names and the exit code (1 means no match). Confirm that check UC1 and check UC2 report no problem containing 'email address'. Write a short summary with no token value to outputs/artifacts/tc024_secret_scan.txt.
