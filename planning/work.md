# work.md: AI-Native Data Discovery (Stack AI Rewire, DS Assignment 3)

**This is the master plan and the live status file.** Any new Claude Code session should read **§0, §1, §2 and §12**, then the section for the current phase in **§9**. Do not redo phases that are already ticked.

- Created 2026-11-19 by the planning session (S0), after a deep review of the whole bundle.
- The detailed review reports are in [`work_notes/`](work_notes/), next to this file. §10 links each one.

---

## Contents
0. [How to use this file](#0-how-to-use-this-file)
1. [Status tracker](#1-status-tracker)
2. [Session log](#2-session-log)
3. [The assignment on one page](#3-the-assignment-on-one-page)
4. [Inputs needed from you](#4-inputs-needed-from-you-open-questions)
5. [Folder review: what is in the bundle, what is missing](#5-folder-review-what-is-in-the-bundle-what-is-missing)
6. [Git repository: yes, one is needed (steps)](#6-git-repository-yes-one-is-needed)
7. [Environment and credentials](#7-environment-and-credentials)
8. [Who does what: roles and red lines](#8-who-does-what-roles-and-red-lines)
9. [Step-by-step plan (phases P1–P13, with prompts)](#9-step-by-step-plan)
10. [Technical cheat sheet per gap (G1–G7)](#10-technical-cheat-sheet-per-gap)
11. [Use-case traps: reviewer checklist for UC1 and UC2](#11-use-case-traps-reviewer-checklist)
12. [Run discipline and foot-guns (read before any pipeline run)](#12-run-discipline-and-foot-guns)
13. [Deliverables checklist](#13-deliverables-checklist)
14. [Rubric fill-in map (Sheet 1 + Sheet 2, TC-001..TC-025)](#14-rubric-fill-in-map)
15. [Packaging and submission](#15-packaging-and-submission)
16. [Inconsistencies found in the bundle docs](#16-inconsistencies-found-in-the-bundle-docs)
17. [Important links mapped to tasks](#17-important-links-mapped-to-tasks)
18. [Command reference and trace cheat sheet](#18-command-reference-and-trace-cheat-sheet)

---

## 0. How to use this file

### Key paths
| Name | Path | Notes |
|---|---|---|
| **BUNDLE** | `/mnt/c/Users/Subhadeep.paul/Downloads/806637_Subhadeep_Paul_data_discovery` | The original download. **Never edit anything in it.** It is the "provided copy" that TC-020 and TC-025 compare against. |
| **WORK** (this file) | `REPO/planning/work.md` (moved here from BUNDLE on 2026-11-25, so it is versioned in git) | Update §1 and §2 at the end of every session |
| **NOTES** | `REPO/planning/work_notes/*.md` | 5 deep-review reports: G1, G3, G4/G5, G6 with live probes, orchestration/gate/check |
| **WORKSHEET** | `REPO/planning/DECISION_WORKSHEET.md` | Every decision you must make: options to tick, and [YOU WRITE: …] placeholders for your own text |
| **REPO** | `~/projects/data-discovery` (= `/home/subhadeep/projects/data-discovery`) | Your git clone of `https://github.com/Subhadeep-paul-TA/data_discovery.git`. The local folder name uses a hyphen; the GitHub repo name uses an underscore. **All work happens here.** Created 2026-11-23 (P1). |

### Rules for every Claude Code session
1. **Work only in REPO.** Read BUNDLE only for reference.
2. **Run every pipeline command (anything that needs a model) with the RUN prefix** (§7):
   `source .venv/bin/activate && set -a && . ./.env && set +a && <command>`
   Never `cat`, print or echo `.env` or the token.
3. **Stop at every STOP** (SKILL.md and §9).
   - Claude **never writes a decision or a reason you did not give**. If you dictate one, Claude transcribes it word for word and notes in `decisions.md` that it was transcribed.
4. **Never hand-edit `outputs/<ID>/`.** Fix the agent (prompt, tool, rule or validator) and re-run.
   - **Snapshot before any re-run whose "before" state you will cite** (§12).
5. **At the end of every session:**
   - tick §1;
   - add one line to §2;
   - commit in REPO (`git add -A && git commit -m "<phase>: <what>"`).
   - Do **not** copy your own decision wording into this file. Your choices and own text go in `planning/DECISION_WORKSHEET.md`; Claude transcribes them word for word into the deliverables when you ask.
6. If a session runs out (the claude.ai 5-hour limit was hit once during planning), start a new session with the resume prompt below.

### Resume prompt (paste into any new session opened in REPO)
```
Read planning/work.md
(sections 0, 1, 2, 12, and the §9 section of the first unticked phase) and this repo's CLAUDE.md.
Then tell me in at most 6 bullets: which phase we are in, what is done (check the repo, not just work.md),
what the next step is, what you need from me, and any risk (for example the Chicago refused-URL count in
outputs/UC1/trace.jsonl). Do not change any file until I confirm.
```

---

## 1. Status tracker
Tick each box as it is finished (◐ = partly done). The "Session" column says whether a **new** Claude Code session is needed. "Needs gateway?" now means **needs a model**: the gateway, or the Claude Code backend from P1b.

**Blockers and decisions (updated 2026-11-26):**
1. **No gateway credentials → decided: use Claude through the Claude Code CLI** (§7 "No credentials: Claude Code backend"). **P1b done 2026-11-25:** the opt-in backend is built and smoke-tested; `.env` selects it with `claude-sonnet-5-5` at effort `high`.
2. **Pushed** (`main` and `work/data-discovery` are on GitHub). The repo is **still public**: make it private when you can (§6 "Status").
3. **Decided 2026-11-23:**
   - Open-Meteo city = **Milan (45.46, 9.19)**, set in the repo by commit `6e7da42` (local only until you run `git push`).
   - Step 2b = **option B**: a Claude web-search fallback inside your `scripts/web_search.py`, verified to work (§7).
4. **Decided 2026-11-26:** no email to the instructor (worksheet B2), and the Claude Code login stays as it is, even though its account email is not yours (§7 "As built").

**Your open to-dos:**
- Worksheet A–C filled; B6 = No; B4 fixed on 2026-11-25 (your reasons and the coordinates are back). Sections D–N come with their phases.
- Run `git push` from `~/projects/data-discovery` (you chose: push now, make it private later).
- The Milan entry for `outputs/artifacts/decisions.md` → "Other decisions" is your B4 text; Claude transcribes it when decisions.md is first edited (P3 or later).

| ☐/☑ | Phase | Assignment task | Main owner | Session | Needs gateway? |
|---|---|---|---|---|---|
| ☑ | **P0** Planning: deep review and this file | — | Claude | S0 (bundle folder) | no |
| ☑ | **P1** Repo and environment setup, `pytest_before.txt`, baseline commit. **Done and pushed 2026-11-23** | Task 1 | Claude (local) + you (push) | — | no |
| ☑ | **P1b** Opt-in **Claude Code model backend** (no gateway credentials): build, smoke test, disclosure draft. **Done 2026-11-25** | setup for Tasks 2–10 | Claude implements, **you review the diff** | **NEW** (in REPO) | no (uses your Claude Code login) |
| ☑ | **P2** Steps 0–2 for UC1 with the skill. **Done 2026-11-26** | Task 2 | Claude runs, **you confirm at STOPs** | **NEW, mandatory** (in REPO) | **yes** |
| ☐ | **P3** Generate `scripts/web_search.py`, then Step 2b suggestions | Task 3 | Claude searches, **you decide each one** | same as P2 | **yes** (+ Gemini) |
| ☐ | **P4** Close G1, G3, G4 | Task 5 | Claude implements, **you review diffs** | NEW (recommended) | no |
| ☐ | **P5a** Inspect links without the LLM, G6 allowlist (can run right after P4) | Tasks 4 + 6 (G6) | Claude inspects, **you decide** | same as P4, or NEW | no |
| ☐ | **P5b** Your `gate_decisions.json` and the pre-check (after P3, when `links.json` is final) | Task 4 | **You write** | any | no |
| ☐ | **P6** Open-Meteo city, full runs UC1 + UC2 (baseline, before G5) | Task 7 | Claude runs, **you choose the city** | NEW | **yes** |
| ☐ | **P7** G7: find, fix and re-run one real agent failure | Task 8 | Claude investigates, **you pick** | NEW | **yes** |
| ☐ | **P8** G5 calibration rules, assess re-runs, before/after | Task 6 (G5) | **You decide the rules**, Claude transcribes and runs | NEW | **yes** |
| ☐ | **P9** Memo reviews, sign-off, `check` | Task 9 | **You write**, Claude gathers evidence and runs check | NEW | no (check) |
| ☐ | **P10** Extend SKILL.md with Steps 3–5 | Task 10a | Claude drafts from what you did, **you edit** | NEW | no |
| ☐ | **P11** Reuse check for UC2 in a fresh, isolated session | Task 10b | **You** drive a fresh Claude session | **NEW, mandatory, separate worktree** | **yes** |
| ☐ | **P12** README Submission notes and `walkthrough.md` | Task 11 | **You write**, Claude gathers evidence | NEW | no |
| ☐ | **P13** TC evidence, `pytest_after`, secret scan, rubric, PR, zip | Task 12 | Claude runs, **you mark Pass/Fail and submit** | NEW | yes (TC-018) |

**Counters to watch.** Update these after every UC1 run (§12 explains why).
- Refused events for the Chicago URL in `outputs/UC1/trace.jsonl`: **0** (must never exceed 2; checked 2026-11-26 after the P2 scout run)
- Any other URL refused 2 or more times: none yet
- `outputs/UC1/run_history.jsonl`: 1 invocation (P2 plan+scout): 5 LLM calls, 85,106 input / 11,396 output tokens, 39 tool calls

**Snapshots taken** (in `outputs/artifacts/snapshots/`): none yet

---

## 2. Session log
| Date | Session | Phase | What was done | Next step |
|---|---|---|---|---|
| 2026-11-18/19 | S0 planning (Claude Code, in BUNDLE) | P0 | Read every bundle file. Extracted the docx/xlsx text. Baseline pytest in a scratch copy = 52 collected / 32 passed / 20 failed (matches the docs). Five deep-review reports saved to `work_notes/`. Live no-LLM probes of the three UC1 links (scratch only). Wrote this file. | You answer §4, then do P1 |
| 2026-11-23 | S0 continued (in BUNDLE) | P1 | Your answers recorded (§4). Cloned `Subhadeep-paul-TA/data_discovery` (found **public** and empty) to `~/projects/data-discovery`. Copied the bundle and verified it byte-identical (77 files). Baseline commit `d87ad92` on `main`. Branch `work/data-discovery` at `9256e97` adds `pytest_before.txt` (`20 failed, 32 passed`). `.venv` built (Python 3.12.4, anthropic 1.17.0). **Nothing pushed.** No `.env` (no credentials). | Decide public vs private, then push (§6). Start **P4** in a NEW session opened in REPO (no credentials needed). Ask the instructor for the gateway credentials (§7). |
| 2026-11-23 | S0 continued | P1b plan | You chose to use Claude instead of gateway credentials, and to push now (the repo stays public until you change it). Verified that Claude Code 2.1.316 supports an isolated headless backend (`-p`, `--system-prompt`, `--tools ""`, `--json-schema`, `--strict-mcp-config`, `--no-session-persistence`, `--effort`). One test call from an empty temp folder succeeded: structured JSON returned, about 1.3k prompt tokens (so no CLAUDE.md or memory leaked in), model claude-opus-5-5. `--bare` cannot be used: it ignores the claude.ai login. City recommendation: Milan (awaiting your confirmation). | You push (§6). Then a NEW session in REPO runs **P1b** (prompt in §9). |
| 2026-11-23 | S0 continued | decisions | You pushed `main` and `work/data-discovery`, and chose **Milan** and **Step 2b option B**. Claude set the Open-Meteo coordinates to 45.46 / 9.19 (only those two lines changed) and committed `6e7da42` locally. Option B tested: a headless `claude -p --tools WebSearch --allowedTools WebSearch` call returned an answer with 3 cited URLs, no permission denials, about 13 s. A lead from that search: Open-Meteo's terms of use may limit the free API to non-commercial use, which matters for UC2 (verify at source; §11). | `git push`; write your Milan reason in decisions.md; start **P1b** in a NEW session in REPO. |
| 2026-11-25 | S0 continued | planning | Moved the plan (`work.md`), the review notes (`work_notes/`) and a copy of `Important_links.md` from BUNDLE into `REPO/planning/`, so they are versioned and pushed; BUNDLE keeps only a pointer `work.md`. Added `planning/DECISION_WORKSHEET.md` (every decision, with options to tick and [YOU WRITE] placeholders). The repo is still public; Claude pushed nothing. | Fill the worksheet (A–C now); decide visibility; `git push`; then P1b in a NEW session. |
| 2026-11-25 | S0 continued | worksheet check | You filled A–C: push now and make private later (B1); email the instructor, with no disclosure text in the deliverables (B2, B5); agents on `claude-sonnet-5-5` (B3); Milan reason written (B4); Step 0 answer (C1); needs table and the three links confirmed (C2, C3). Claude aligned the plan (§7, P1b `.env` and facts list, P3 note, §16) and flagged three items: the B4 sentence about the UCI city, B6 unticked, and the B2 email not yet written. | Revise B4 if you agree; tick B6; send the email; `git push`; then P1b. |
| 2026-11-25 | S0 continued | ready for P1b | You ticked B6 = No and rewrote B4: Milan is the assumed location of the fictional client Valdena for UC1 and UC2, with no assumption about the UCI data's city (this fixes the earlier problem). But the rewrite replaced the whole answer, so the coordinates and your reasons are gone. You said the B2 email facts are acceptable. Claude committed your worksheet edits locally. | Put your B4 reasons back (before P3); `git push`; start **P1b** in a NEW session in REPO. |
| 2026-11-25 | S1 (Claude Code, in REPO) | P1b | Your B4 fix committed separately. Design approved with two decisions: effort `high` in `.env`; keep the CLI's account-email context, with mitigations. Built `discovery_agent/llm_claude_code.py`, `make_llm()` in `llm.py`, two lines in `orchestrator.py`. Probes before coding found three gaps, all fixed: inherited Claude Code session variables (`CLAUDE_EFFORT=max`), `@path` in piped text attaching local files, and the CLI's own context block. The first smoke run found a fourth: the model called agent tools natively and got "No such tool available" (fixed: preamble, plus a stream-json guard that retries). Checks: 44 offline checks with a fake CLI (scratchpad, not committed); pytest unchanged (20 failed, 32 passed); smoke test `--stop-after plan` into a temp folder: 2 `llm_call`, 1 tool call, submit accepted, no prompt text in the trace, no email in the files. `.env` created (3 lines, mode 600). B2 email facts listed in chat. | You: B2 email; check the Claude Code login (§1); `git push`. Then **P2** in a NEW session. |
| 2026-11-26 | S1 continued | decisions | You kept the Claude Code login as it is (the CLI shows its account email to the agents; the mitigations stay) and decided not to send the instructor email (B2). Plan aligned: §1, §4, §5, §7 (disclosure, Step 2b), §13, §14 TC-018, §16, the RUN-prefix wording in §0 and P2, P2's "Needs" row, P3's commit message. Worksheet B2 still shows your earlier tick. | `git push` when you want; start **P2** in a NEW session. |
| 2026-11-26 | S2 (Claude Code, in REPO) | P2 | Skill Steps 0–2 for UC1. Step 0: `step0_checks.md` (pytest 32 passed / 20 failed, all 20 in `test_learner_gaps.py`; 3 tool smoke tests return JSON; gateway variables unset, Claude Code backend recorded). Step 1: `validate-use-case UC1` OK; needs N1–N6 as in the contract. Step 2: plan+scout exit 0 (planner 2 turns, scout 3; 5 LLM calls, 39 tool calls, 0 errors, 0 HTTP, 0 refused; account-email check `0 0`). Scout read all 3 wiki pages and opened all 4 catalog entries; 4 of 30 internal searches had no hits (one parallel batch, none rephrased). Candidates: N1 production, N2, N4, N5 one each; N3 two (vendor expired); N6 and N1 prototype none; Nager not mapped. Noted for G7: both agents report the register's Milan coordinates as contradicting the brief's Lisbon sentence (stale after `6e7da42`); `unmet_needs` mixes unmet needs with caveats. `outputs/UC1/links.json` created once with `cp -n` from the prescribed links after your answer at the STOP. | **P3**: generate `scripts/web_search.py`, then Step 2b (same session or NEW). |

---

## 3. The assignment on one page

**Goal.** You get a working multi-agent data-discovery pipeline:

> Planner → Scout → candidate gate (you) → Profiler ×N → deterministic rules → Risk Assessor → Memo Writer → human sign-off (you)

You must:
- close the graded gaps G1, G3, G4, G5, G6 and G7;
- run UC1 (air quality, traffic, clinic) and UC2 (ice-cream sales, weather, holidays) end to end through the Tiger AI Gateway;
- make and record the human decisions;
- review the memos and sign off;
- extend `SKILL.md` with Steps 3–5 and run a reuse check;
- fill in the rubric, open a PR, and submit a zip.

**Scoring (100 points)**
| Part | Pts | Earned in |
|---|---|---|
| Automatic score of `discovery_results.json` against a hidden key, averaged over UC1 and UC2. It covers discovery recall, verdict calibration, red-flag recall, the assessment of each prescribed link, precision and the overall verdict, **minus guardrail penalties from the trace**. | **40** | P5–P8 (needs all gaps done well, plus run discipline) |
| G1, G3, G4: tests pass, code not hard-coded to the fixtures, edge cases explained in decisions.md | 11 | P4 |
| G5: specific, consistent calibration rules reflected in the verdicts, plus one feasible-for-one-need case | 5 | P8 |
| G7: a real failure fixed at its cause, with measured before/after and the decision it affects | 10 | P7 |
| Memo review: what the agent got wrong or missed, a traced conclusion, agreements (sign-off checks are automatic) | 16 | P9 |
| Skill Steps 3–5, the reuse check and the delivery reflection | 10 | P10–P12 |
| Decisions log: G6 minimality, gate decisions, reasons for each source | 4 | P3, P5 |
| Walkthrough (`outputs/artifacts/walkthrough.md`) | 4 | P12 |

**Red lines.** Breaking any of these costs points or invalidates evidence:
- Do not edit `tests/test_learner_gaps.py`. Do not add test files: TC-020 expects exactly 52 tests.
- Do not change caps or budget in `config/settings.json`. The only allowed config edit is latitude/longitude in `api.open_meteo_archive.default_query`.
- Allowlist **exact hosts only**: no wildcard and no parent domain. **Never add `catalog.data.gov`.**
- Never hand-edit `candidates.json`, records or results.
- Never write a gate, suggestion or sign-off decision that you did not make.
- Never download whole datasets. No personal data in any output.
- No new dependencies without asking.
- **The token must never appear anywhere**: code, outputs, traces, transcripts, git history or the zip.
- Unknown stays unknown: never infer a licence, owner, refresh cadence or consent.

---

## 4. Inputs needed from you (open questions)
Please answer these before or at the phase shown. Each has a default if you don't answer.

**Answers received (2026-11-23)**
| Q | Answer | Consequence |
|---|---|---|
| Q1 | **No credentials.** You decided to use Claude instead ("a new Claude session will do"). | Build the opt-in **Claude Code backend** in **P1b** (§7, §9-P1b). The pipeline still makes and logs every model call; a Claude session never writes the outputs itself. |
| Q3 | Repo `https://github.com/Subhadeep-paul-TA/data_discovery.git` | It is **public**. You push now and make it private later (§6). |
| Q8 | Zip name `806637_Subhadeep_Paul_data_discovery.zip` confirmed | Reviewer name for `signoff.json`: `Subhadeep Paul` |
| Q9 | Review time **not measured** | The delivery reflection must say "not measured" and make **no** time-saving claim. Model usage still comes from `run_history.jsonl`. |
| Q10 | Claude did the local P1 setup on 2026-11-23 | See §6 "Status" |
| Q4 | **Milan** (decided 2026-11-23) | Coordinates 45.46 / 9.19 set in `config/external_sources_register.json` (commit `6e7da42`). You still write the reason, in your own words, in decisions.md → "Other decisions". |
| Q5 | Resolved by Q1 | Claude Code stays on your claude.ai login and also serves the pipeline's model calls through the P1b backend. |
| Step 2b | **Option B** (decided 2026-11-23) | `scripts/web_search.py` = the README prompt plus the fallback sentence in §9-P3. No email to the instructor and no disclosure paragraph (B2, B5; 2026-11-26). Answer truthfully where the README or the rubric asks (§7). |

**Still open:** Q6, Q7 (default: no UC3), Q11–Q13 (default: yes). Q2 applies only if gateway credentials arrive later.

From 2026-11-25, your decisions live in `planning/DECISION_WORKSHEET.md`. So far: B3 = agents on `claude-sonnet-5-5`; B2 = no email to the instructor (changed 2026-11-26).

| # | Question | Blocks | Default if unanswered |
|---|---|---|---|
| **Q1** | Do you have the gateway credentials from the email (`ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`)? Which model id is enabled for your key? | P2 and every LLM run. **P1 and P4 can go ahead without them.** | Do P1 then P4 first; P2 waits. |
| **Q2** | Which Gemini model with citations is enabled on your key for Step 2b: `gemini-3.8-flash` or `gemini-3.5-flash-lite`? | P3 | Try `gemini-3.8-flash`, then the other. If both fail or return no citations, **stop and tell the instructor** (do not write suggestions from memory). |
| **Q3** | Git hosting: GitHub (personal or org)? Repo name? Private? The instructor's GitHub username, so you can add them as a collaborator to review the PR? | P1 push, P13 PR | GitHub, private repo `data-discovery`, instructor added as a collaborator in P13 |
| **Q4** | **Which northern-Italian city (coordinates) should replace the Lisbon default for Open-Meteo, and why?** There is one register entry, shared by UC1 and UC2. See §11 for options. | P6 | Claude stops and asks; Lisbon is not left in for the final runs. |
| Q5 | Claude Code's own login: keep your current claude.ai login and use the gateway only for the pipeline (via `.env`), or launch Claude Code itself on the gateway as the docs assume? | P1/P2 | Keep the claude.ai login; pipeline only via `.env` (§7) |
| Q6 | Deadline, and roughly how much time per day? | scheduling | — |
| Q7 | Optional stretch: a third use case (UC3)? | — | **No** |
| Q8 | Confirm the zip name `806637_Subhadeep_Paul_data_discovery.zip` (taken from the bundle folder name) and the reviewer name `Subhadeep Paul` for `signoff.json`. | P9, P13 | As written |
| Q9 | Will you **time yourself** while reviewing the Step 2b shortlist (P3)? The delivery reflection must use a measured time, or say that none was measured. | P3, P12 | Yes: use a stopwatch and note the minutes in your own notes |
| Q10 | Should Claude run the local part of P1 (copy, venv, pytest_before, commits) once you have created the empty GitHub repo? | P1 | You paste the §6 commands yourself |
| Q11 | TC-018 negative gate runs in a **throwaway copy** of the repo, so the real outputs are not polluted? | P13 | Yes |
| Q12 | Run the reuse check in a **separate git worktree**, so the scored `outputs/UC2` is not overwritten? | P11 | Yes |
| Q13 | Keep evidence snapshots in `outputs/artifacts/snapshots/` (copies only, never edits)? | P6–P8 | Yes |

**Design decisions you will make inside phases.** Defaults are in §10.
- **G1:** is a JSON-LD "Unknown" final? Do ambiguous licences give `None`?
- **G3:** full ISO 3166 list or a regex? What does a string `status` count?
- **G4:** strict grain rule? Staleness skipped when there is no start date?
- **G5:** about 18 calibration topics, including how a partially met must need rolls up (UC2 N2) and the UCI "research only" clause.
- **Gate:** accept all three prescribed links? (The rubric requires accepting Chicago on purpose.)
- **Step 2b:** each suggestion.
- **Sign-off:** verdict, conditions, owners and due dates.

---

## 5. Folder review: what is in the bundle, what is missing

### Bundle contents (all reviewed)
| Item | What it is | Notes from the review |
|---|---|---|
| `Stack AI Rewire - DS - Data Discovery - Assignment Doc.docx` | The spec: gaps table, constraints, 12 learner tasks, deliverables, scoring, submission rule | Source of truth for *what* to deliver |
| `Helper Guide.docx` | Setup, links, commands, hints, troubleshooting, checklist | One embedded image (not reviewed: the extractor ran out of budget). The UC1 command block is garbled onto one line; use the README version. |
| `Stack AI Rewire - DS - Data Discovery - Evaluation Rubric.xlsx` | Sheet 1: 8 scored rows + "Pull request link". Sheet 2: TC-001..TC-025, with "Actual Output" and "Pass/Fail" columns to fill | Mapped in §14. Goes into the zip root, completed. |
| `Important_links.md` | Your reference links | Mapped in §17 |
| `skills/data-discovery-agent/SKILL.md`, `README.md` | The skill runner for Steps 0–2b. You extend it with Steps 3–5. | The copy must also live at `.claude/skills/data-discovery-agent/SKILL.md` |
| `starter-code/` (5,004 lines of py/md/json, 80 files) | The project. It becomes the root of your repo. | See below |

`starter-code/` in more detail:
- **`discovery_agent/`**
  - `agent.py`: tool-use loop and submit validation.
  - `agents.py`: the five agent specs, their toolsets and cross-check validators.
  - `llm.py`: Anthropic SDK client. It reads env vars only, does **not** load `.env`, and defaults to `claude-opus-5-5` if no model is set.
  - `orchestrator.py`: stages plan, scout, profile, assess, memo; the gate; result merging.
  - `cli.py`: run, tool, validate-use-case, check.
  - `validation.py`: `check` and the sign-off checks.
  - `risk_rules.py`: 7 provided rules plus **3 G4 stubs**.
  - `trace.py`: an **append-only** JSONL trace.
  - `tools/`: `licence.py` (**G1 stub**); `formats.py` (**G3 stub**, plus the ungraded G2 stub); `http_client.py` (guardrails); `links.py` (`inspect_dataset_link`, `sample_data_file`); `internal_catalog.py` (BM25 search, wiki backlinks); `public_api.py` (register probes; the vendor feed is refused before any HTTP); `probe.py`; `uci.py`; `summarize.py`.
  - `prompts/` (6 files; `risk_assessor.md` holds the **G5 placeholder**).
  - `schemas/` (5 files).
- **`tests/`**: `test_tools_offline.py` (24 pass), `test_agent_loop.py` (7 pass), `test_learner_gaps.py` (21 tests, 20 fail before the gaps are closed; `test_g6_allowlist_not_wildcarded` already passes), and 8 fixtures.
- **`config/`**:
  - `allowlist.json`: 6 hosts. The matcher accepts the host **or any subdomain**.
  - `settings.json`: 150 requests per run, 2 MB / 5 MB byte caps, stale after 5 years, partial-window threshold 0.95.
  - `external_sources_register.json`: open-data policy; Open-Meteo (default **Lisbon** 38.72, -9.14 in the bundle; set to **Milan** 45.46, 9.19 in the repo on 2026-11-23); Nager.Date; **expired** vendor feed (UC1).
  - `red_flags.json`: 31 codes, each with severity and `detected_by`.
- **`use_cases/`**: UC1 and UC2 JSON contracts and briefs, plus a template. Both have `as_of` 2026-10-15.
- **`internal/`**: UC1 (4 catalog entries, 3 wiki pages); UC2 (3 catalog entries, 2 wiki pages). These hold the planted traps (§11).
- **`links/`**: UC1 example links (3), UC2 (`[]`), and the links and gate templates.
- **`outputs/artifacts/`**: `decisions.md` template, `_TEMPLATE_signoff.json`, `.gitkeep`.
- Top-level files: `README.md` (holds the web_search prompt and the Submission notes questions), `CLAUDE.md` (project rules for Claude), `requirements.txt` (anthropic, jsonschema, pytest), `.env.example`, `.gitignore` (ignores `.env`, `.cache`, `.venv` and so on), `.flake8` (max line 140).

### What is missing, and who provides it
| Missing | Provided by | When |
|---|---|---|
| `scripts/web_search.py` (required in the zip) | You, by prompting Claude Code with the README prompt | P3 |
| Gateway credentials | Not provided, and not needed: the Claude Code backend (P1b) replaces them | — |
| `.claude/skills/data-discovery-agent/SKILL.md` | You copy it in P1 | P1 |
| `outputs/UC1/`, `outputs/UC2/` and every artifact | The pipeline, plus you | P2–P13 |
| Git repo and PR | You (**Q3**) | P1, P13 |

### This machine (checked 2026-11-18)
| Item | State | Consequence |
|---|---|---|
| OS | WSL2 Ubuntu 22.04. The bundle is on `/mnt/c` (slow; every file shows as mode 777). | Put the repo in `~/projects` and normalise file modes (P1) |
| Python | miniconda 3.12.4. `anthropic` is **not installed**; jsonschema and pytest are | Use a venv (P1). 3.12 is fine (3.10+ is required). |
| git | 2.34.1. `user.name` and `user.email` are set. Credential helper = Windows **Git Credential Manager** (HTTPS push opens a browser login). **No SSH keys.** `init.defaultBranch` is not set (would default to `master`). | Use HTTPS. Set the default branch to `main` (P1). |
| `gh` CLI | **not installed** | Open the PR in the GitHub web UI, or `sudo apt install gh` |
| `zip`, `unzip`, `jq` | **not installed** | Use Python's `zipfile` (P13) and Python one-liners for traces (§18) |
| `ANTHROPIC_*` variables | none set in the shell | Use `.env` plus the RUN prefix (§7) |
| Claude Code | 2.1.316, VS Code extension, claude.ai login (5-hour usage limit) | Keep each session to one phase |

---

## 6. Git repository: yes, one is needed

**Why.**
- Task 1 says "Create a git repository and clone it."
- Task 12 says "Commit and push your repository, open a pull request, and paste its URL into the rubric. The instructor reviews the pull request."
- No repo exists yet: the bundle folder is not a git repo.

**Strategy (recommended).**
- `main` holds **one baseline commit containing the provided files, unmodified**.
- All your work goes on the branch `work/data-discovery`.
- The PR `work/data-discovery → main` then shows the instructor **exactly what you changed**:
  - gap code, allowlist, prompts and the skill;
  - every output and artifact.
- It also proves `tests/test_learner_gaps.py` and `config/settings.json` are unchanged (TC-020, TC-025).

### Status (2026-11-23): done locally, not pushed
- **Remote:** `https://github.com/Subhadeep-paul-TA/data_discovery.git`. It was **empty and public**: an anonymous `git ls-remote` succeeded, and the GitHub page returns HTTP 200 without a login.
- **Done by Claude:** steps 2–6 and 8 below.
  - The clone is at `~/projects/data-discovery`.
  - Step 0 was replaced by a repo-local `git symbolic-ref HEAD refs/heads/main`, so your global git config is unchanged.
  - `main` = `d87ad92`: the baseline, 77 files, verified byte-identical to the bundle.
  - `work/data-discovery` = `9256e97`: adds `pytest_before.txt` (`20 failed, 32 passed`).
  - Every file has mode 100644. `.venv`, `.pytest_cache` and `.claude/settings.local.json` are ignored.
- **Not done yet:** step 7 (`.env`, no credentials) and **every push**.
- **Your decision before pushing.** The repo is public, so pushing would publish:
  - the course's starter code and its internal (fictional) documents;
  - later, your traces, answers and the rubric.

  Recommended: make the repo **private** first (GitHub → repo → Settings → General → Danger Zone → Change repository visibility → Private). Then add the instructor as a collaborator when you open the PR. Keep it public only if the program allows that.
- **Then push.** On 2026-11-23 you decided to push now and make the repo private later. Anything pushed while it is public can be copied or cached before you switch. Windows Git Credential Manager asks you to log in the first time:
  ```bash
  cd ~/projects/data-discovery
  git push -u origin main
  git push -u origin work/data-discovery
  ```
- **Pushed (checked 2026-11-23):** GitHub has `main` = `d87ad92` and `work/data-discovery` = `9256e97`. Later commits go up with a plain `git push` from the work branch. `6e7da42` (Milan coordinates) and the `planning/` commit (2026-11-25) are waiting for that push.

### P1 steps (copy and paste into a WSL terminal; owner: you)
```bash
# 0) once
git config --global init.defaultBranch main

# 1) In the browser: GitHub → New repository → name "data-discovery" → Private →
#    do NOT add a README, .gitignore or licence (empty repo) → Create.

# 2) Clone into the Linux filesystem (fast; avoids /mnt/c permission noise)
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/<YOUR-USER>/data-discovery.git
cd data-discovery

# 3) Copy the bundle: starter-code contents at the root, skills/ alongside, plus the skill copy for Claude Code
B="/mnt/c/Users/Subhadeep.paul/Downloads/806637_Subhadeep_Paul_data_discovery"
cp -r "$B/starter-code/." .
cp -r "$B/skills" .
mkdir -p .claude/skills/data-discovery-agent
cp skills/data-discovery-agent/SKILL.md .claude/skills/data-discovery-agent/SKILL.md
# Files copied from /mnt/c arrive executable; normalise them so git does not record mode 755
find . -path ./.git -prune -o -type f -exec chmod 644 {} +
find . -path ./.git -prune -o -type d -exec chmod 755 {} +
# Local-only ignore (never committed): Claude Code's per-user settings file
echo ".claude/settings.local.json" >> .git/info/exclude

# 4) Baseline commit = provided files only, unmodified
git add -A
git status --short | head -20          # expect only starter files + skills/ + .claude/skills/...
git commit -m "Baseline: provided starter code and skill, unmodified"
git push -u origin main                # Windows GCM may open a browser login

# 5) Work branch
git switch -c work/data-discovery

# 6) venv + dependencies
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 7) Secrets file (gitignored): fill in the 3 values from the email. Never commit or print it.
cp .env.example .env && chmod 600 .env && nano .env

# 8) pytest BEFORE any code change: must be 52 collected, 32 passed, 20 failed
python -m pytest tests/ -q > outputs/artifacts/pytest_before.txt 2>&1; tail -1 outputs/artifacts/pytest_before.txt
git add outputs/artifacts/pytest_before.txt
git commit -m "Task 1: pytest before gaps (32 passed, 20 failed)"
git push -u origin work/data-discovery
```

**Your review checkpoint.**
- The last line of `pytest_before.txt` reads `20 failed, 32 passed`.
- `git log --oneline` shows the 2 commits.
- `git check-ignore .env` prints `.env`, so it is ignored.

**Then open VS Code on the repo:** `code ~/projects/data-discovery`, and select the `.venv` interpreter. Every later session starts from there, so `CLAUDE.md` and the skill are loaded.

**Commit cadence afterwards.** Commit at the end of every phase, and push now and then. The git history doubles as before/after evidence.

**At the end (P13).**
- Open the PR in the web UI: `base: main ← compare: work/data-discovery`.
- Add the instructor as a collaborator if the repo is private.
- Paste the PR URL into the rubric, then commit and push the rubric (the PR updates automatically).

---

## 7. Environment and credentials

- `llm.py` reads `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN` (or `ANTHROPIC_API_KEY`), and then `DISCOVERY_MODEL`, `ANTHROPIC_MODEL` and optional `DISCOVERY_EFFORT` **from the environment only**.
  - Never append `/v1` to the base URL.
- **Even a run that makes no LLM call needs the token set,** because `LLM()` is created when the pipeline starts. Examples are the TC-018 gate failures and `--only` with an id that matches nothing.
- The `tool`, `validate-use-case` and `check` commands do **not** need the gateway.

**Recommended pattern (Option A, the default for Q5).**
- Keep the values in `REPO/.env`. It is gitignored, mode 600, and uses the `.env.example` format.
- Load them only into the command that needs them:
  ```bash
  source .venv/bin/activate && set -a && . ./.env && set +a && python -m discovery_agent run --use-case UC1 --stop-after scout --no-input
  ```
- Why: Claude Code's Bash tool starts a fresh shell for every command, so exported variables do not persist between commands.
- Why not export them globally: putting `ANTHROPIC_BASE_URL`/`ANTHROPIC_AUTH_TOKEN` in `~/.bashrc`, or launching Claude Code from a shell that has them exported, would **switch Claude Code itself onto the gateway**.

**Option B (what the docs assume).**
- Export the 3 variables in a terminal, then start `claude` (the CLI) from that terminal.
- Claude Code then also runs on your assignment key and model.
- This is fine if you want it, but it spends the key's budget and changes the model Claude Code uses.

**Step 0's variable check without printing anything:**
```bash
source .venv/bin/activate && set -a && . ./.env && set +a && python -c "import os;print({k: bool(os.environ.get(k)) for k in ['ANTHROPIC_BASE_URL','ANTHROPIC_AUTH_TOKEN','ANTHROPIC_MODEL']})"
```

**Token-leak audit (code read).**
- The trace records only agent, turn, model, stop reason and token usage for LLM calls, plus tool args and HTTP URLs.
- Transcripts store the system prompt, the messages and the tool results. No headers or environment values are written anywhere.
- The real risk is **you pasting the token into a chat or a file**. Don't. The P13 scan double-checks everything.

### No credentials: Claude Code backend (decided 2026-11-23)
No Tiger AI Gateway credentials were provided. **Your decision:** use Claude instead. The honest way to do that:

- **The pipeline still makes every model call itself.**
  - Its agent loop, tools, guardrails, validators, `trace.jsonl` and transcripts stay exactly as they are; only the model endpoint changes.
  - Each call goes to a **fresh, isolated** headless Claude (`claude -p`) through a small opt-in adapter that P1b builds (`DISCOVERY_BACKEND=claude-code`).
  - Claude is then just the model behind the pipeline, exactly as the gateway's model would have been.
- **A Claude Code session must never write the agents' outputs, and never act as the agents.** Two reasons:
  - *Evidence:* the auto-score, `check` and TC-025 assume the pipeline produced `outputs/<ID>/` and logged it.
  - *Independence:* this planning session has read the reviewer expectations in `work_notes/`, so its answers would be steered toward what we expect the answer key to want. They would no longer be the agents' own judgement, and G7 ("find a real agent mistake") would become meaningless.

**Feasibility (verified 2026-11-23 on this machine, Claude Code 2.1.316)**
- The CLI has `-p`, `--output-format json`, `--system-prompt`, `--tools ""` (no tools), `--json-schema` (forced JSON reply), `--strict-mcp-config` (no MCP servers), `--no-session-persistence`, `--model` and `--effort`.
  - `--system-prompt-file` is not listed, so the system prompt is passed inline. The prompts are a few KB, below Linux's 128 KB limit per argument.
- One test call ran from an empty temp folder (no tools, no MCP, replaced system prompt, JSON schema):
  - `structured_output` came back correctly;
  - the whole prompt was about 1.3k tokens, so no CLAUDE.md, memory or work.md leaked in (correction 2026-11-25: the CLI still adds a small context block of its own; see "As built" below);
  - model `claude-opus-5-5`; about 2 seconds.
- `--bare` would isolate even more, but it accepts only `ANTHROPIC_API_KEY`, not your claude.ai login, so it cannot be used.

**As built (P1b, 2026-11-25, Claude Code 2.1.316)**
- **Files.** `discovery_agent/llm_claude_code.py` (stdlib only, same `complete(...)` interface as `llm.LLM`); `make_llm(trace)` in `llm.py`; `orchestrator.py` builds its LLM through `make_llm`.
  - `DISCOVERY_BACKEND` unset: `LLM(trace)`, exactly as before.
  - `claude-code`: the adapter. Any other value stops the run.
  - Tests (still 52) and `config/` unchanged.
- **One model call** = `claude -p --output-format stream-json --verbose --tools "" --strict-mcp-config --setting-sources "" --safe-mode --no-session-persistence --system-prompt <agent prompt> --json-schema <reply schema> --model $DISCOVERY_MODEL --effort $DISCOVERY_EFFORT`.
  - Runs in a fresh empty temp folder, with a 600 s timeout.
  - `--setting-sources ""` loads none of your settings files (checked in the CLI code); `--safe-mode` turns off CLAUDE.md, skills, plugins and hooks.
- **Child environment.** Yours minus every `CLAUDE*` and `ANTHROPIC_*` variable (keeps `CLAUDE_CONFIG_DIR` and `CLAUDE_CODE_OAUTH_TOKEN`), plus `CLAUDE_CODE_MAX_OUTPUT_TOKENS=<max_tokens>` and `DISABLE_AUTOUPDATER=1`.
  - Why: a Claude Code session that starts the pipeline exports `CLAUDE_EFFORT=max` and `CLAUDE_CODE_CHILD_SESSION=1`.
- **stdin.** A protocol-only preamble, then the tools and the conversation as JSON (Messages format), then the reply instruction.
  - Every `@` is written as `@`: the CLI turns `@<path>` in piped text into a local file attachment (verified with a canary file).
  - `@` in the system prompt is not expanded (verified).
- **Reply.** `{"text", "tool_calls": [{"name": <enum of the agent's tools>, "input": object}]}`, sent through the CLI's StructuredOutput tool.
  - Tool inputs are free-form, so the pipeline's validators stay the only judge, and rejected submissions still reach the trace.
- **Native tool calls.** If the model calls an agent tool directly inside the CLI, it sees a fake "No such tool available". The reply is then discarded and the call repeated (`llm_retry` code `native_tool_call`).
  - The preamble prevents it: 4 of 4 replays clean after the fix. Before the fix it happened in the first smoke run.
- **Errors.**
  - A refusal, and a max_tokens cut (the CLI reports "exceeded the N output token maximum"), go to the agent loop as `stop_reason` `refusal` / `max_tokens`, as on the gateway.
  - Login errors, a usage limit, 403 and 404 stop the run. A 400 or "prompt too long" fails the agent at once.
  - Anything else is retried 3 times (2/4/8 s), then `LLMError`.
- **Trace.** The same `llm_call` event as `llm.py`: model `claude-code:claude-sonnet-5-5`, and `input_tokens` include cache writes. `llm_retry` carries only a short code. The model label also appears in `run_summary.json`, `discovery_results.json` and the memo's human-gate line.
- **Context the CLI always adds** (a claude.ai login cannot switch it off): the login's email address, an Environment note (temp folder, OS), the model name and today's date.
  - The preamble tells the model to ignore it; after each run, check the outputs for the email (§18).
  - The login on this machine is not your own address; you chose to keep it (2026-11-26).
- **`.env`** (worksheet B3, and P1b decision 2026-11-25): `export DISCOVERY_BACKEND=claude-code`, `export DISCOVERY_MODEL=claude-sonnet-5-5`, `export DISCOVERY_EFFORT=high`.
  - `high` is the API's default for this model; pinning it stops a CLI update from changing it between P6 and P8.
  - The three gateway variables stay unset.

**Consequences**
- Skill Step 0 will report the three gateway variables as `False`. That is expected. Answer its STOP with "intentional: Claude Code backend", and record the backend instead of a gateway model id in `step0_checks.md`.
- TC-018 can now run, because no token is needed.
- **Usage limits.** Every call uses your claude.ai plan; we hit its 5-hour limit once while planning.
  - Run stage by stage (`--stop-after`, `--only`).
  - **Decided (worksheet B3): `DISCOVERY_MODEL=claude-sonnet-5-5`** for the agents, at effort `high`. Keep the same model and effort for every scored run (P6–P8), so before/after comparisons stay fair.
  - A usage limit stops the run with the CLI's message. Re-run that stage after the reset.
- **Disclosure (your decisions, worksheet B2 and B5; changed 2026-11-26):** no email to the instructor, and no separate disclosure paragraph in the deliverables. Where a question asks about it directly, answer truthfully: the README reuse-check question "what was missing", and the rubric's AI-Native Skill row about `scripts/web_search.py`. The backend is visible anyway in the code diff, the commit messages and the trace (model `claude-code:<model>`).

**Step 2b (P3) without the gateway: decided 2026-11-23 → option B**
- **A. Strict reading of the README.**
  - Generate `scripts/web_search.py` exactly from the README prompt. It will exit with a message naming the missing `ANTHROPIC_AUTH_TOKEN`.
  - Then, as the README says, stop at Step 2b, tell the instructor, and record it.
  - Cost: TC-019 cannot be met (no suggestions, and no accepted source inspected).
- **B. Fallback to Claude web search.**
  - Generate the script from the README prompt, plus one added sentence (it is in the P3 section): when the gateway variables are missing, the script runs `claude -p` with only the WebSearch tool and a JSON schema, then prints the answer and the cited URLs.
  - Step 2b still calls *your* script, and every suggestion still has a citation.
  - The search engine differs from the README (Claude web search instead of Gemini), and the script uses Claude Code's web search internally. There is no email to the instructor (B2); answer the rubric row about the script truthfully.
- **Decided: B.**
  - Feasibility verified 2026-11-23: `claude -p --output-format json --tools WebSearch --allowedTools WebSearch --strict-mcp-config --no-session-persistence --json-schema …`, run from an empty temp folder, returned an answer and 3 cited URLs. There were no permission denials, and it took about 13 s.
  - Keep `--allowedTools WebSearch` next to `--tools WebSearch`, so headless mode cannot block the search; the tested command used both.
  - The CLI's own usage counter showed 0 server-side searches, so the evidence that a search happened is the cited URLs. You still open every URL yourself, as Step 2b requires.

**Other ways forward, if things change**
- **Gateway credentials arrive:** put them in `.env` and remove `DISCOVERY_BACKEND`. Runs that were already made stay valid; their trace shows the model as `claude-code:<model>`.
- **A direct Anthropic API key:**
  - `llm.py` accepts `ANTHROPIC_API_KEY` when `ANTHROPIC_AUTH_TOKEN` is absent (`llm.py:40-43`).
  - Leave `ANTHROPIC_BASE_URL` unset and set `ANTHROPIC_MODEL`.
  - This needs no adapter. Step 2b would still need option A or B.
- **Never acceptable:** writing `outputs/` by hand, or a Claude session answering as the agents (see the two reasons above). Claude Code's built-in WebSearch, called directly by the Step 2b session, also does not count: the rubric requires Step 2b to call **your** `scripts/web_search.py`.

---

## 8. Who does what: roles and red lines

| Activity | Claude may | Claude must not | You must |
|---|---|---|---|
| Code gaps G1, G3, G4 | Explain the design and edge cases first, implement, run tests, draft technical notes | Edit or add tests; hard-code fixtures | Read every diff, be able to explain each rule and threshold, write the decisions.md text in your own words |
| G5 calibration | Propose options with the affected sources; transcribe your rules; run assess | Choose the rules for you | Decide and word the 6–10 rules |
| G6 allowlist | Inspect links, show the refusals; edit the allowlist **after you say "add X"** | Add hosts on its own initiative; try alternate URLs | Decide each host; write the justification and the "not added" reasons |
| Step 2b | Run **your** `scripts/web_search.py`; show publisher, exact URL, needs, coverage *as the page states it*, what still needs checking | Use built-in WebSearch; suggest from memory; decide accept/reject | Open each page yourself; decide accept/reject/revise with a reason; time the review |
| Gate decisions (`outputs/UC1/gate_decisions.json`) | Run the read-only pre-check | Write any decision or reason | Write the file yourself (accept all 3 prescribed links, Chicago on purpose) |
| Pipeline runs | Run them, read traces, propose fixes at the cause, snapshot | Raise caps or `max_turns`; hand-edit outputs; re-profile Chicago without asking | Approve re-runs that touch Chicago |
| G7 | Hunt through traces and transcripts, list candidates with evidence, implement the chosen fix, measure before/after | Pick the failure for you | Pick one; own the explanation |
| Memo review, sign-off, walkthrough, Submission notes | Build evidence packs (fields, flags, trace lines, traceable fields); run `check` | Write your judgements, overrides, verdicts or reflections | Write them in your own words |
| SKILL.md Steps 3–5 | Draft from what was **actually** done (this log, decisions.md, commands used) | Invent generic steps that were not done | Edit, approve, keep both copies identical |
| Rubric | Run every TC command and capture the actual outputs | Mark Pass/Fail or write the Sheet 1 confirmations for you | Paste and mark; fill Sheet 1 |

---

## 9. Step-by-step plan
**Ordering note.** The plan follows the Assignment's task order, with **one deliberate change**: the first full assess run (P6) uses the *provided* Risk Assessor prompt, and the G5 rules are written afterwards (P8). That gives a genuine "before" for the required G5 before/after verdicts.

**Current order (updated 2026-11-23, Claude Code backend):**
P1 (you push) → **P1b** (backend) → P2 → P3 → P4 → P5 (a + b) → P6 → P7 → P8 → P9 → P10 → P11 → P12 → P13.

This is the Assignment's own task order again. P4 and P5a need no model, so they can also run earlier if you want.

Dependencies:
- P5's Eurostat gate decision needs G6 (and G3 for a useful inspection).
- P6 needs G1, G3, G4 and G6 done, plus the gate file and the city (Q4).
- G7 (P7) and G5 (P8) need the P6 runs.
- P9 needs the final runs.
- P10 needs everything you actually did.
- P11 needs the finished skill.

---

### P1: Repo and environment setup (Task 1)
| | |
|---|---|
| Who | **You** (GitHub repo, `.env` values). The terminal commands are in §6 (or Claude runs them, Q10). |
| Session | No Claude session needed |
| Produces | Repo with a baseline commit on `main`, branch `work/data-discovery`, `.venv`, `.env`, `.claude/skills/...`, `outputs/artifacts/pytest_before.txt` |
| You review | `pytest_before.txt` = 52 collected / 32 passed / 20 failed; `.env` is ignored |
| Done when | Both commits are pushed |
| Status 2026-11-23 | Commits made locally (`d87ad92` on `main`, `9256e97` on `work/data-discovery`), **not pushed** (the repo is public; see §6). `.env` not created (no credentials). |

---

### P1b: Opt-in Claude Code model backend (no gateway credentials)
| | |
|---|---|
| Who | Claude designs and implements. **You** approve the design and review the diff. |
| Session | **NEW**, opened in REPO (`code ~/projects/data-discovery`, select the `.venv` interpreter) |
| Needs | P1 done (pushing is not required for P1b). Your Claude Code login. |
| Produces | `discovery_agent/llm_claude_code.py`; a small backend switch (factory) where the pipeline builds its LLM; `.env` with `export DISCOVERY_BACKEND=claude-code` and `export DISCOVERY_MODEL=claude-sonnet-5-5` (gitignored); a smoke-test run in a temp folder (never in `outputs/`); a facts list for your instructor email (worksheet B2) |
| You review | The agent loop, tools, validators, trace and transcripts are unchanged. The default path behaves as before. The tests are still 52 collected (20 failed, 32 passed before the gaps). Each call runs in an empty temp folder with no tools and no MCP. The trace shows `llm_call` events with token counts. The prompt text is never written to the trace. |
| Done when | The smoke test (`--stop-after plan` into a mktemp `--out` folder) produces `search_plan.json`, `llm_call` trace events and a normal-looking planner transcript |
| Commit | "P1b: opt-in Claude Code model backend (no gateway credentials)" |
| Status 2026-11-25 | **Done.** What was built and what the checks found: §7 "As built" and §2. |

**Prompt (paste into the new session):**
```
Read planning/work.md §0, §1, §7 ("No credentials: Claude Code backend")
and §9-P1b, and this repo's CLAUDE.md. We have no Tiger AI Gateway credentials, so the pipeline's model calls will go to Claude
through the Claude Code CLI in headless mode. Build an opt-in backend for that.

Hard rules:
- The pipeline must still make and log every model call itself. Do not change agent.py's loop, the tools, the guardrails, the
  validators, trace.py or how transcripts are written. Never write anything under outputs/ by hand. Do not touch tests/ or config/.
- Default behaviour must not change: the new backend is used only when DISCOVERY_BACKEND=claude-code.

Design (explain it first, then STOP for my OK):
1. New file discovery_agent/llm_claude_code.py, stdlib only. Class ClaudeCodeLLM(trace) with the same
   complete(*, agent, system, messages, tools, max_tokens, turn) method as llm.LLM, and a .model attribute.
2. Each call runs: claude -p --output-format json --tools "" --strict-mcp-config --no-session-persistence
   --system-prompt "<the agent's system prompt>" --json-schema '<response schema>' [--model $DISCOVERY_MODEL] [--effort $DISCOVERY_EFFORT]
   with cwd = a fresh empty temp directory (so no CLAUDE.md, memory or work.md can reach the agent) and a timeout. Do not use
   --bare (it cannot use my claude.ai login). --system-prompt-file is not listed in --help, so pass the prompt inline (a few KB).
   Response schema: {"text": string, "tool_calls": [{"name": <enum of this agent's tool names incl. the submit tool>, "input": object}]}.
3. Stdin carries: the tool list (name, description, input_schema of every tool, including the submit tool), then the whole
   conversation in order: the user task, each assistant turn (text plus tool calls with id, name and input), and each tool
   result (tool_use_id, is_error, content). End with an instruction to reply only through the schema, calling tools the way an
   Anthropic tool-use model would (several independent calls in one turn are allowed).
4. Return an object agent.py can use unchanged: .content (blocks with .type "text" or "tool_use", .text, .id, .name, .input, and
   model_dump(exclude_none=True) so transcripts serialise), .stop_reason ("tool_use" when there are tool calls, else "end_turn"),
   and .usage (input_tokens including cache creation, output_tokens, cache_read_input_tokens from the CLI's usage). Generate ids.
5. Retry up to 3 times with backoff when the CLI exits non-zero, times out, returns is_error, or has no structured_output; then
   raise llm.LLMError. Write the same "llm_call" trace event as llm.py (agent, turn, model "claude-code:<model or default>",
   stop_reason, tokens) and "llm_retry" events on retries. Never write prompt text into the trace.
6. A small factory (for example make_llm(trace) in llm.py), used at the one place orchestrator.py builds LLM(...). It returns
   ClaudeCodeLLM when DISCOVERY_BACKEND=claude-code, otherwise LLM(trace) exactly as before (including its credential check).

After my OK:
- Implement it, show the full diff, and run python -m pytest tests/ -q (still 52 collected: 20 failed, 32 passed; gaps not done).
- Create .env (gitignored, chmod 600) containing only these two lines: export DISCOVERY_BACKEND=claude-code / export DISCOVERY_MODEL=claude-sonnet-5-5
- Smoke test without touching outputs/UC1:
    T=$(mktemp -d); source .venv/bin/activate && set -a && . ./.env && set +a && python -m discovery_agent run --use-case UC1 --stop-after plan --no-input --out "$T"
  Show the llm_call events in $T/trace.jsonl, the first 40 lines of $T/search_plan.json, and whether $T/transcripts/planner.json
  looks like a normal tool-use conversation. If it fails, read the transcript and fix the cause in the adapter, then re-test.
- List in chat only the facts my instructor email needs (worksheet B2): no gateway credentials, what the backend does, the isolation
  flags, the model used, and what stays unchanged. Do not write the email or any decisions.md text; I write those.
- Update work.md §1 and §2, then commit: "P1b: opt-in Claude Code model backend (no gateway credentials)".
```

---

### P2: Steps 0–2 for UC1 with the skill (Task 2)
| | |
|---|---|
| Who | Claude runs the skill. **You** confirm the needs table and answer the dataset-link question. |
| Session | **NEW, mandatory**: open Claude Code in REPO, so CLAUDE.md and the skill load at session start |
| Needs | P1b done: `.env` selects the Claude Code backend. No gateway credentials needed. |
| Produces | `outputs/artifacts/step0_checks.md`; `outputs/UC1/use_case_validation.txt`, `search_plan.json`, `candidates.json`, `trace.jsonl`, `transcripts/`, `run_summary.json`, `run_history.jsonl`; `outputs/UC1/links.json` (a copy of the prescribed links, made **once**) |
| You review | **1. Needs table:** N1–N6 match `use_cases/UC1_air_quality.json` (N1 hourly must; N2 hourly must, production; N3 hourly must; N4 daily should; N5 event could; N6 annual could). **2. Candidates against needs:** did the Scout read the wiki backlinks (`station_network`, `counter_replacement_2024`, `clinic_data_policy`)? Did it include the expired vendor feed (it should, as a finding) and `clinic.patient_visits` (tempting but forbidden)? Did it wrongly map `api.nager_public_holidays` to a UC1 need (no UC1 need is about holidays)? **3. `unmet_needs` and the planner's `external_data_hints`.** Note anything odd: it is G7 material. |
| Done when | `candidates.json` and `links.json` exist; you have answered the STOP |

> **With the Claude Code backend (P1b):** Step 0 will find the three gateway variables unset. That is intentional. When the skill stops there, answer: "Intentional: no gateway credentials were provided; the pipeline uses the opt-in Claude Code backend (DISCOVERY_BACKEND=claude-code in .env, see work.md §7). Record the backend in step0_checks.md and continue."

**Message 1 (context):**
```
Read planning/work.md sections 0, 1, 7, 12 and §9-P2.
Rules for this session: run every pipeline command (anything that needs a model) as
  source .venv/bin/activate && set -a && . ./.env && set +a && <command>
and never print .env or the token. Do not edit anything under outputs/UC1/ by hand.
```
**Message 2 (invoke the skill):**
```
/data-discovery-agent Run Steps 0–2 for UC1 (not 2b yet: I will generate scripts/web_search.py first).
Before Step 1 item 4 run `mkdir -p outputs/UC1` so the tee works. After the scout, give me:
the needs table; need -> candidate source ids -> unmet_needs; the planner's external_data_hints;
which wiki pages the Scout actually read (from trace.jsonl tool_call events); and run_summary totals.
At Step 2 item 4, if I say I use the prescribed links, run exactly:
  cp -n links/UC1_example_links.json outputs/UC1/links.json
and never overwrite outputs/UC1/links.json afterwards. Then STOP.
At the end update work.md §1 and §2 (no decision wording), and commit: "P2: Steps 0-2 UC1".
```
**Your answer at the STOP (your words):** for example, "Yes, I will use the three prescribed links: UCI 360 for N1 prototype, Eurostat for N6 both windows, and Chicago for N1 prototype, which I accept on purpose so its refusal is recorded."

---

### P3: Generate `scripts/web_search.py`, then Step 2b suggestions (Task 3)
| | |
|---|---|
| Who | Claude generates the script **from the README prompt you paste**, then runs the searches. **You** check each publisher page and decide. |
| Session | Same session as P2 (continue), or a new one with the resume prompt |
| Needs | P1b done (the model backend), and Step 2b **option B** (decided: the search script falls back to Claude web search). Review time will **not** be measured (your Q9 answer), so the delivery reflection says so. |
| Produces | `scripts/web_search.py` (committed); `decisions.md` § "Source suggestions" (your decisions, transcribed); accepted links appended to `outputs/UC1/links.json`; inspection output for each accepted link |
| You review | For each suggestion, open the exact URL yourself. Check what coverage the page states (or "not stated"), the licence or terms, the population and the access. Decide accept, reject or revise with a short reason. **At least one accepted source must be inspected through the workflow** (TC-019). Prefer a source on an already allowlisted host (for example `archive.ics.uci.edu` or GitHub), or one exact new host you can justify under G6. |
| Done when | Every suggestion is decided and recorded, at least one accepted link has been inspected, and every refused host has been decided by you |

**Message A: generate the script.** Paste the README prompt verbatim; this is rubric evidence that *you* generated it with Claude Code.
> **Option B is decided (§7).** Add this sentence after the README prompt, in the same message: "If ANTHROPIC_BASE_URL or ANTHROPIC_AUTH_TOKEN is missing, fall back to running `claude -p --output-format json --tools WebSearch --allowedTools WebSearch --strict-mcp-config --no-session-persistence --json-schema <a schema for {answer: string, citations: [string]}>` from an empty temp folder, with the query on stdin; print the answer and the cited URLs, say which backend was used, and never print any token." Disclosure: your instructor email (worksheet B2).
```
Create `scripts/web_search.py`. Use only the Python standard library (urllib, json, os) and add no dependencies. It takes one query argument. It sends a POST to `{ANTHROPIC_BASE_URL}/v1/chat/completions` (no `/v1` added to the base URL) with the header `Authorization: Bearer {ANTHROPIC_AUTH_TOKEN}` and a JSON body: `model` from `WEB_SEARCH_MODEL`, defaulting to `gemini-3.8-flash`; one user message containing the query; and `web_search_options: {}`. It prints the answer text, then the citation URLs from the response. If a variable is missing, exit with a message that names it. Never print the token or the full request.
```
Then:
```
Test it once with the RUN prefix: python scripts/web_search.py "hourly air quality open data Milan Lombardy 2004 2005"
Show the answer, the citation URLs and which backend was used (expect the Claude web-search fallback, because no gateway
variables are set). If there are no citations, STOP. Commit: "P3: generate scripts/web_search.py (README prompt + Claude web-search fallback)".
```
**Message B: Step 2b.**
```
Continue the data-discovery-agent skill at Step 2b for UC1. Use only scripts/web_search.py (never the built-in WebSearch),
start from the planner's external_data_hints, and show at most five suggestions, each with: publisher, exact dataset/record URL
(with its citation), need ids, coverage quoted from the page (or "not stated"), and what still needs checking. Then STOP.
I will check each page myself and dictate accept/reject/revise + reason. Transcribe my words exactly into
outputs/artifacts/decisions.md (Source suggestions table; add a line saying the reasons were dictated by me and transcribed),
append accepted ones to outputs/UC1/links.json in the links template shape with my reason as "note",
then inspect each accepted link (tool inspect_dataset_link, --use-case UC1). If a host is refused, STOP and wait for my G6 decision.
Update work.md §1/§2 and commit "P3: Step 2b decisions".
```
> Accepted suggestions are profiled in P6. They need a gate decision from you and an allowlisted host. They are judged by your review and decisions log, not by the automatic score.

---

### P4: Close G1, G3, G4 (Task 5). No credentials needed.
| | |
|---|---|
| Who | Claude implements (design and edge cases first). **You** review every diff and approve each design choice. |
| Session | **NEW** (recommended; the context is heavy). Split into P4a (G1 + G3) and P4b (G4) if needed. |
| Produces | Changes in `discovery_agent/tools/licence.py`, `discovery_agent/tools/formats.py`, `discovery_agent/risk_rules.py`; drafts of the G1 and G3 edge-case notes, which you rewrite into `decisions.md` |
| You review | §10 lists the review points for each gap. `git diff --exit-code -- tests/test_learner_gaps.py` must show no change. |
| Done when | `-k g1` gives 9 passed; `-k g3` gives 2 passed; `-k g4` gives 7 passed; the full suite shows only G5 and G6 failures (2 failed, 50 passed); the edge-case notes are in your words |
| Commits | One per gap: "P4: G1 extract_licence", "P4: G3 jsonstat_summary", "P4: G4 rules" |

**Session opener:**
```
Read planning/work.md §0, §8, §10 (G1/G3/G4) and §9-P4.
The full design reports are in planning/work_notes/review_G1_licence.md, review_G3_jsonstat.md, review_G4_G5_rules_calibration.md
(read the "DETAILS" sections). Follow CLAUDE.md: explain the design and edge cases first, then make the change for my review.
Never edit tests/test_learner_gaps.py, never add test files, stdlib only.
We do G1 first.
```
Then use the ready prompts, one gap at a time:
- **G1:** `planning/work_notes/review_G1_licence.md` → "PROMPTS → Implement G1 the way the repo's CLAUDE.md requires". Four steps: design, then STOP; implement; tests and checks; DRAFT note.
- **G3:** `planning/work_notes/review_G3_jsonstat.md` → "PROMPTS → Implement G3 per CLAUDE.md". Afterwards, run the read-only "audit of the G3 diff" prompt and the extra-checks heredoc from that file (section 9).
- **G4:** `planning/planning/work_notes/review_G4_G5_rules_calibration.md` → "PROMPTS → Implement G4 rule by rule". STOP after each rule; run `-k g4` each time.
- Optional, to help you defend the code: the "Teach-back" quiz prompt in the G3 report. Do the same for G1 and G4.

Claude may draft decisions.md *facts* in chat. **You** write the final G1 and G3 bullets. Suggested edge cases:
- **G1:** the Kaggle `"Unknown"` JSON-LD licence. It returns name None with `found_in` json-ld, gives LIC-UNKNOWN, and needs Legal review under the register policy.
- **G3:** UC1's real Eurostat response has **no 2006** in its time dimension, so no warning fires. Contrast it with an *empty* latest year, which raises MISSING_CELLS but still overstates `time.last`.

---

### P5: Inspect the links, G6 allowlist, your gate decisions (Tasks 4 + 6/G6)
> **Split because the credentials are missing (2026-11-23):**
> - **P5a** = prompt items 1–3 below: inspection without the LLM, G6, and the Eurostat re-inspection after G3. It can run right after P4. In P5a, take the three URLs from `links/UC1_example_links.json`, because `outputs/UC1/links.json` does not exist until P2.
> - **P5b** = items 4–5: your `gate_decisions.json` and the pre-check. It waits until P3 is finished, because `outputs/UC1/links.json` is created in P2 and may gain accepted suggestions in P3.
| | |
|---|---|
| Who | Claude inspects (no LLM). **You** read the Eurostat pages, decide G6, and **write `gate_decisions.json` yourself**. |
| Session | Continue P4, or start NEW |
| Produces | `outputs/artifacts/inspect_<source_id>.txt` (UCI, Chicago **run once only**, Eurostat before and after G6); `config/allowlist.json` with exactly **`ec.europa.eu`** added (plus any host you approve for an accepted suggestion); the decisions.md G6 section (yours); `outputs/UC1/gate_decisions.json` (yours) |
| You review | Read these pages in your browser before deciding Eurostat: the metadata page `https://ec.europa.eu/eurostat/cache/metadata/en/sdg_11_52_esmsip2.htm`, the copyright notice `https://ec.europa.eu/eurostat/en/help/copyright-notice`, and the data browser `https://ec.europa.eu/eurostat/databrowser/view/sdg_11_52/default/table?lang=en`. **Accept all three prescribed links**, with reasons in your own words of at least 20 characters. Chicago is accepted on purpose, so its refusal becomes a recorded finding. Rejecting UCI or Eurostat would remove them from the automatic per-link score. |
| Done when | `-k g6` gives 2 passed, and the full suite gives 51 passed / 1 failed (G5 only). The gate pre-check lists no problems. |
| Commit | "P5: link inspection, G6 ec.europa.eu, gate decisions" |

**Prompts** (all in `planning/work_notes/review_G6_allowlist_live_probe.md` → PROMPTS):
1. "Task 4: inspect the three UC1 links without the LLM, with Chicago run exactly once." Keep the Chicago output: it is reused for TC-017, so it is never run again.
2. You tell Claude: **"add ec.europa.eu"**, then use the "G6 edit after the learner has decided" prompt. Claude pre-fills only the evidence columns. You write *why nothing broader* and the *hosts not added*, with reasons.
   - Hosts not to add, with draft reasons in the report: `catalog.data.gov`, `europa.eu`, `commission.europa.eu`, `www.eea.europa.eu`, `creativecommons.org`, `doi.org`, `nagerholidays.com`.
3. "Re-inspect Eurostat after G6 and G3, before the gate decision."
4. **You** copy `links/_TEMPLATE_gate_decisions.json` to `outputs/UC1/gate_decisions.json` and write one entry per URL in `outputs/UC1/links.json`. Copy each URL **exactly** from that file.
5. Claude runs the read-only gate pre-check: the heredoc in `planning/work_notes/review_orchestrator_gate_check_signoff.md` §(c).

Expected source ids:
- `link.uci_360`
- `link.europa_sdg_11_52_099aa6`
- `link.data_open_air_chicago_hour_aggre_d4970b`

---

### P6: Open-Meteo city, full runs UC1 + UC2 (baseline, before G5) (Task 7)
| | |
|---|---|
| Who | Claude runs the pipeline, snapshots, and previews the rule flags. The city is decided (Milan, set in commit `6e7da42`). |
| Session | **NEW** |
| Needs | P4 and P5 done (51 tests passing; only G5 is open); the P1b backend; your Milan entry in decisions.md |
| Produces | Full `outputs/UC1/` and `outputs/UC2/` (records, `rule_flags.json`, `risk_assessment.json`, `discovery_results.json`, `feasibility_memo.md`, traces, transcripts); snapshot `outputs/artifacts/snapshots/run1_baseline_pre_G5/` |
| You review | Records against reality (§11 checklist); `rule_warnings` is empty; the Chicago refused count is ≤ 1; nothing reads "PROFILING FAILED"; Open-Meteo's temporal fields are *not* the 2014 probe dates; note candidate agent mistakes for P7 |
| Done when | Both use cases have run through memo, and run 1 is snapshotted and committed |

**Prompt:**
```
Read planning/work.md §0, §7, §11, §12 and §9-P6.
1) The Open-Meteo coordinates are already Milan (45.46, 9.19), commit 6e7da42. Verify that
   git diff main -- config/external_sources_register.json shows only latitude/longitude, and that decisions.md "Other decisions"
   has my city entry with my reason. If the entry is missing, remind me and stop.
2) Pre-flight: python -m pytest tests/ -q (expect 51 passed, only test_g5 failing); config/settings.json identical to
   /mnt/c/.../starter-code/config/settings.json; allowlist has no catalog.data.gov; run the read-only gate pre-check.
   Note line counts of outputs/UC1/trace.jsonl and run_history.jsonl and the refused-URL counts.
3) UC1 (with RUN prefix): python -m discovery_agent run --use-case UC1 --from-stage profile --links-file outputs/UC1/links.json --no-input
4) UC2 (with RUN prefix): python -m discovery_agent run --use-case UC2 --no-input
5) For each UC report: profiled ids, run_summary warnings, PROFILING FAILED records, rule_warnings, refused URLs with counts
   (warn me if any URL >= 2), and a table source_id | verdict | red_flags, plus need_coverage and overall_verdict.
6) Copy (never edit) into outputs/artifacts/snapshots/run1_baseline_pre_G5/<UC>/: discovery_results.json, risk_assessment.json,
   rule_flags.json, transcripts/, records/.
7) Run the "Preview rule flags on real records without any LLM call" check from planning/work_notes/review_G4_G5_rules_calibration.md
   and list suspected profiler misreads as possible G7 candidates. Do not fix anything yet.
Update work.md §1/§2 (+ the Chicago counter) and commit "P6: run 1 UC1+UC2 (pre-G5 baseline)".
```
> **Optional safety step before step 3:** profile only the Chicago link into a scratch `--out` folder to see whether the profiler retries the refused host. If it retries, that is your G7, and you fix it *before* the real run. Ask Claude for "a Chicago dry run in a mktemp --out folder with copies of candidates.json, links.json and gate_decisions.json". It costs a few model calls.

---

### P7: G7, one real agent failure fixed at its cause (Task 8)
| | |
|---|---|
| Who | Claude investigates the traces and transcripts and lists candidates with evidence. **You** pick one. Claude fixes it at the cause and re-runs the narrowest stage. |
| Session | **NEW** (trace reading fills the context) |
| Produces | The fix in `discovery_agent/` (a prompt, tool, tool description, validator or rule); snapshots `snapshots/G7_before/` and `G7_after/`; the decisions.md G7 section with all 8 fields |
| You review | That the failure was **actually observed** in your run (quote the trace line or transcript turn), that the fix is at the cause and not in an output, and that the before/after is **measured** |
| Done when | All 8 decisions.md fields are filled (symptom, evidence with file and line or turn, root cause, fix with diff summary, re-run command, measured before/after, the decision it could affect, the related source or test checked); the full suite still has 51+ passing; Chicago was not re-profiled |
| Commit | "P7: G7 <short name> fix + re-run" |

**Prompt:**
```
Read planning/work.md §0, §10-G7, §12, §18 and §9-P7. Investigation only — change nothing yet.
Using outputs/UC1 and outputs/UC2 (trace.jsonl, transcripts/, records/, rule_flags.json, discovery_results.json) and the
snapshots, check each G7 hypothesis in work.md §10-G7 plus anything else you find. For each real failure give: symptom,
exact evidence (file + line number in trace.jsonl, or transcript file + message index), root cause location (quote the
prompt line / tool code / validator), a minimal at-the-cause fix, the narrowest re-run command (never including
link.data_open_air_chicago_hour_aggre_d4970b), a measurable before/after metric, the project decision it could affect,
and a related test or source to check. Rank them. STOP and let me pick one.
After I pick: snapshot the affected files to outputs/artifacts/snapshots/G7_before/, implement the fix, show the diff,
run python -m pytest tests/ -q, re-run the narrow stage(s) with the RUN prefix (then --from-stage assess so results and memo
are current), snapshot to G7_after/, and give me a before/after table. Draft (in chat only) the factual G7 bullets;
I write the final decisions.md text. Update work.md §1/§2 and commit.
```

---

### P8: G5 verdict calibration, then assess re-runs before and after (Task 6/G5)
| | |
|---|---|
| Who | Claude lays out options and their impact. **You choose and word 6–10 rules.** Claude transcribes them and re-runs assess for both use cases. |
| Session | **NEW** |
| Produces | `prompts/risk_assessor.md`: the G5 comment is replaced by `## Verdict calibration` with a flat `1.` list; snapshots `G5_before/` (= the latest state after P7) and `G5_after/`; the final assess and memo for both use cases; decisions.md sections "G4–G5 feasible for one need/window" and "G5: Verdict calibration" (yours) |
| You review | Every verdict follows your rules. Any change that might be run-to-run noise is labelled as such. Watch the regex trap: the word "calibration" may appear **only in the heading**, with no `###` sub-headings inside the section (§10-G5). |
| Done when | `-k g5` passes, so all 52 tests pass; both use cases have been re-run with `--from-stage assess` (which also regenerates the memo); the before/after table is in decisions.md |
| Commit | "P8: G5 calibration + assess re-runs" |

**Prompt:** use `planning/planning/work_notes/review_G4_G5_rules_calibration.md` → "PROMPTS → G5 drafting session". It covers the before snapshot, the existing inconsistencies in the prompt, 2–3 options per topic, a STOP, transcription of your dictated rules, `-k g5`, the assess re-runs, an audit table, a STOP, then the final `--from-stage assess` run and `check`. Replace "outputs/artifacts/g5_verdicts_before_*.json" in that prompt with `outputs/artifacts/snapshots/G5_before/`.

Decisions you will make here are listed in §10-G5. The key ones:
- one verdict for a source with several targets;
- FRS-STALE on a historical prototype window;
- the UCI "research purposes only" clause;
- UC2 N2 (no code mapping): partially met or unmet, and how it rolls up to the overall verdict.

---

### P9: Memo reviews, sign-off, check (Task 9)
| | |
|---|---|
| Who | Claude builds evidence packs. **You** write `review_UC1.md`, `review_UC2.md`, `outputs/UC1/signoff.json` and `outputs/UC2/signoff.json`. Claude runs `check` and saves its output. |
| Session | **NEW** |
| Produces | `outputs/artifacts/review_UC1.md`, `review_UC2.md`; both `signoff.json` files; `outputs/artifacts/check_UC1.json`, `check_UC2.json` with `"problems": []` |
| You review | Each review records: where you **agree** and why; where you **overrule** the agent and why; **your verdict on each dataset link**; your **gate decision**; refusals recorded as findings (Chicago). Each sign-off has a reviewer, a verdict (`proceed` / `proceed_with_conditions` / `stop`), conditions each with text, owner and due date, at least one agreement or override with a reason, and a `traced_conclusion`. |
| Done when | `check UC1` and `check UC2` both exit 0 with no problems, and the saved JSON is committed |
| Commit | "P9: memo reviews, sign-off, check" |

**Prompts:** in `planning/work_notes/review_orchestrator_gate_check_signoff.md` → PROMPTS, use:
1. "Evidence pack for my memo review", for UC1 and then UC2.
2. You write your files.
3. "(3) Run check and save check_<ID>.json".

The traced-conclusion field must be **non-null and reachable through dict keys only**. `licence.name` is null for Chicago, so it fails; `access.reachable` passes; list indexes fail. Ask Claude to list the traceable fields.

> Never fill in the "Reviewer: ____" line in `feasibility_memo.md`. Your decision lives in `signoff.json` and the review.

---

### P10: Extend SKILL.md with Steps 3–5 (Task 10a)
| | |
|---|---|
| Who | Claude drafts from what you **actually did** (§2 log, decisions.md, commands, checks). **You** edit and approve. |
| Session | **NEW** |
| Produces | `skills/data-discovery-agent/SKILL.md` and `.claude/skills/data-discovery-agent/SKILL.md`, **identical** (`diff` prints nothing) |
| Content (from SKILL.md's own "other deliverable" section) | **Step 3, profile and rule-check:** `--from-stage profile --links-file`; what to check in each `records/*.json` (provenance count ≥ 3, licence evidence and `found_in`, temporal and grain fields, `sample_findings` against the docs, unknowns); how each link type is handled; reading `rule_flags.json` and rule warnings; the rule-flag preview. **Step 4, assess and draft the memo:** your G5 calibration; review of dismissed flags; the memo's 7 required headings; the human review gate. **Step 5, evaluate and hand off:** `check <ID>`; trace checks (refused URLs ≤ 2, live request counts, token totals from `run_history.jsonl`); the G7 before/after pattern; snapshots; what goes into `outputs/artifacts/`. Write it in the same imperative voice as Steps 0–2b, **use-case agnostic** (no UC1/UC2-only values), with STOPs for human decisions. Add the fixes you found, such as `mkdir -p outputs/<ID>` before the tee and `cp -n`. |
| Done when | Both copies are identical and you can say "a fresh session could follow this for a new use case" |
| Commit | "P10: SKILL.md Steps 3-5" |

---

### P11: Reuse check for UC2 in a fresh session (Task 10b)
**Why a separate worktree.** Re-running plan and scout for UC2 inside REPO would overwrite the scored `outputs/UC2` and force you to redo the UC2 review, sign-off and check. The fresh session must also **not** have `scripts/web_search.py` (the doc requires you to regenerate it and record that) and must **not** be pointed at work.md. It gets only the skill and the README.

```bash
cd ~/projects/data-discovery && git switch work/data-discovery && git status   # clean tree first
git worktree add -b reuse-check ../dd-reuse HEAD
cd ../dd-reuse
rm -f scripts/web_search.py && rm -rf outputs/UC2 planning  # fresh project for UC2: no search script, no UC2 outputs, no plan
cp ../data-discovery/.env . && chmod 600 .env             # gitignored; never commit
ln -s ../data-discovery/.venv .venv                       # reuse the venv
code .                                                    # NEW Claude Code session here
```
| | |
|---|---|
| Who | **You** drive the fresh session. Do not paste work.md and do not give extra hints. Note every place you had to help. |
| Session | **NEW, mandatory**, in `~/projects/dd-reuse` |
| Steps | 1. `/data-discovery-agent Run Steps 0–2b for UC2.` 2. When it stops for the missing `scripts/web_search.py`, regenerate it with the README prompt. This is a **missing input**; record it. 3. Decide each suggestion yourself. 4. If you accept a link: create `outputs/UC2/links.json`, write your own `gate_decisions.json`, add an allowlist host if needed (with a justification), and profile it: `--from-stage profile --links-file outputs/UC2/links.json --no-input`. 5. If **none** survives your check, record "none accepted" and stop. UC2's unmet need is usually N2, the internal code mapping, which no public dataset can fill. |
| Record | (a) which steps could not be followed as written, and what was missing; (b) which inputs a data scientist would replace for a new project; (c) values hard-coded for UC1 or UC2 that you found and changed |
| Bring back to REPO | Add a "Reuse check (UC2, fresh session)" subsection to `outputs/artifacts/decisions.md`. Optionally copy evidence into `outputs/artifacts/reuse_check_UC2/` (step0_checks, candidates.json, run_summary.json). If a step failed because of the skill, fix the skill in REPO (P10 files) and note it. |
| Clean up | `cd ~/projects/data-discovery && git worktree remove ../dd-reuse --force && git branch -D reuse-check` |
| Done when | Answers are drafted for the three README reuse questions, and the evidence is in REPO |

---

### P12: README Submission notes and walkthrough (Task 11)
| | |
|---|---|
| Who | **You write.** Claude gives facts only: file paths, field values, `run_history.jsonl` sums (the one-liner in §18). |
| Session | **NEW** (or continue P11) |
| Produces | README.md § "Submission notes": **Reuse check** (3 answers); **Delivery reflection** (what you did versus the assistant, what you still checked, your *measured* review time or "not measured", and model usage from `run_history.jsonl`); **Ownership** (one source you selected or rejected, one rule or correction, one change a new use case would need). Also `outputs/artifacts/walkthrough.md`: one rule explained, one `signoff.json` claim traced to its record field, one rejected source and why, one memo conclusion, each citing your own files. |
| Note | The README calls the walkthrough "15 minutes with your instructor" in one place and a written file elsewhere. Write the file, and be ready to talk it through. |
| Decided (Q9) | Review time was **not measured**. Write exactly that in the delivery reflection, and make no time-saving claim. |
| Commit | "P12: submission notes + walkthrough" |

---

### P13: TC evidence, pytest_after, secret scan, rubric, PR, zip (Task 12)
| | |
|---|---|
| Who | Claude runs every TC command and collects the outputs. **You** paste them, mark Pass/Fail, fill Sheet 1, create the PR and submit. |
| Session | **NEW** |
| Steps | 1. `python -m pytest tests/ -q > outputs/artifacts/pytest_after.txt 2>&1` (expect **52 passed**). 2. TC-018 in a **throwaway copy** (prompt "Reproduce rubric TC-018 safely" in `planning/work_notes/review_orchestrator_gate_check_signoff.md`), saved to `outputs/artifacts/tc018_gate_runs.txt`. 3. TC-023 vendor check, TC-024 secret scan (§15) and the account-email check on `outputs/` (§18, expect `0 0`). 4. Re-run `check UC1` and `check UC2` and re-save them. 5. Collect the actual outputs for every TC in §14 into `outputs/artifacts/rubric_evidence.md`. 6. Copy the rubric xlsx from BUNDLE into the REPO root; you fill both sheets (in Excel, or Claude fills only the "Actual Output" column with openpyxl and you check it). 7. Per worksheet N3, first archive and remove `planning/` (`git branch planning-archive && git rm -r -q planning && git commit -m "Remove planning notes from the submission"`; also push `planning-archive` if you want the notes kept on GitHub). Then push and open the PR (§6), add the instructor, paste the PR URL into rubric cell D11, commit and push again. 8. Build the zip (§15), verify it, and submit to Tiger Academy (Paradiso). |
| Done when | The zip is uploaded, the PR URL is in the rubric, and the token scan is clean |

---

## 10. Technical cheat sheet per gap
Condensed from `work_notes/`. Read the full report before implementing.

### G1: `extract_licence(html, jsonld=None)` in `tools/licence.py` (report: `planning/work_notes/review_G1_licence.md`)
- **Contract.** Returns **exactly** these four keys: `licence_name`, `licence_url`, `snippet` (≤ 400 characters), `found_in` (`"json-ld"`, `"link"`, `"text"` or `None`).
  - Nothing found → all four `None`.
  - Call `jsonld_datasets(html)` only when `jsonld is None`. `[]` means "no JSON-LD"; this is the UCI path.
  - **It must never raise.** `links.py` catches only `NotImplementedTool`, so any other exception loses the whole inspection result.
- **Precedence.**
  1. JSON-LD `license`/`licence`: a URL string, a name or SPDX id, an object with name/url/@id, or a list. An explicit value is **final** even when it is unrecognised (Kaggle "Unknown" → name None, found_in json-ld, raw value in the snippet). An empty value counts as absent.
  2. Licence links in the main content. Strip header, nav and footer, but **not `<aside>`** (Zenodo's rights box is inside one).
  3. Sentences with a licensing cue.
  4. Two different licences in the same stage → None.
- **Normalisation by pattern** (never by fixture lookup):
  - `CC BY[-NC][-ND][-SA] X.Y`
  - `CC0 1.0`
  - `ODbL 1.0`, `ODC-By 1.0`, `PDDL 1.0` (URL form `1.0` or `1-0`)
  - `OGL vN.0`; with no version, plain `OGL`
  - `MIT`, `Apache-2.0`, only when next to the word "licence"/"license"
  - anything else → **None**
- **Why None matters.** `rule_licence` treats only `{unknown, none, null, not found, n/a}` as unknown. A raw string such as "Not specified" or "All rights reserved" would raise **no flag at all**.
- **Tests and real link.** 9 test items (TC-001..005). The live UCI 360 page gives `CC BY 4.0` via a link, so it gets LIC-ATTRIBUTION instead of the LIC-UNKNOWN blocker.
- **Hard-coding smells to avoid:** portal names (zenodo, kaggle, uci), exact-URL dictionaries, only 4.0 or only the tested names, a blanket `except`, keying on `rel="nofollow"` or CSS classes.

### G3: `jsonstat_summary(dataset)` in `tools/formats.py` (report: `planning/work_notes/review_G3_jsonstat.md`)
- **11 keys exactly:** `label`, `updated`, `source`, `dimensions[{id,size,labels}]` (in `dataset["id"]` order), `time{first,last,values}` or None, `geo_codes` (index-**position** order, never translated), `expected_cells` (product of `size`), `value_count` (non-null values; **0 is a value**), `missing_cells`, `status_counts`, `warnings`.
  - `warnings` holds only the bare strings `MISSING_CELLS` and `NON_ISO_GEO_CODES`.
- **Index forms.** `category.index` can be a list or a dict `{code: pos}`; sort the dict by position. A constant dimension may have only `label`.
- **Value forms.** `value` can be a dense list with nulls or a sparse dict. `status` can be a string (applies to all cells), a list or a dict.
- **ISO check.** Use the full **ISO 3166-1 alpha-2** list as a frozenset, not `{UK, EL}`. `UK`, `EL`, `EU27_2020`, `EA20` and NUTS codes are flagged; `IT`, `GR` and `GB` are not.
- **Mistakes the 2 tests do NOT catch:** truthiness counting, hard-coded UK/EL, geo order from dict insertion, dimension order from the dimension dict, a string status counted once. Run the extra-checks heredoc in the report.
- **Real UC1 link** (`sdg_11_52`, IT):
  - Content: "Premature deaths due to exposure to fine particulate matter (PM2.5)"; units NR/RT; time **2005, 2007–2023 (no 2006)**; 36/36 cells; `warnings []`; `updated` 2025-12-09. The `updated` field is a release date, not the data end.
  - Upstream provider: **EEA**.
  - Coverage: prototype only through the 2005 value; production has **no data** (T+2 publication lag) → COV-PARTIAL-WINDOW.
- **G2** (data package) is ungraded. Leave it as a stub.

### G4: three rules in `risk_rules.py` (report: `planning/work_notes/review_G4_G5_rules_calibration.md`)
- **Signature.** `(record, candidate, uc, settings) -> [{"code","evidence"}]`. Return `[]` when nothing fires. Never raise: `evaluate()` catches only NotImplementedError. Use `.get()` everywhere.
- **`rule_temporal_coverage`.**
  - Skip `static` grain and records with no start date.
  - A null end counts up to `uc["as_of"]` (2026-10-15).
  - Windows come from `candidate["target_windows"]`.
  - Compute the inclusive day-fraction covered for each window:
    - every window 0 → **one** `COV-OUT-OF-WINDOW`;
    - otherwise any window `< 0.95` (from settings) → **one** `COV-PARTIAL-WINDOW` naming the short windows.
  - `FRS-STALE` when `end < as_of − 5 years`, i.e. before 2021-10-15.
  - The evidence must name the windows and dates. Never use `date.today()`.
- **`rule_grain`.**
  - Use the `GRAIN_ORDER` positions. Flag when the source grain is coarser than `min_grain` for any need in `need_ids`.
  - `event`, `static`, `unknown` and unknown need ids never fire.
  - **Note:** UC1 N1 is **hourly**, not 15-minute as TC-012's text says. Implement the docstring strictly.
- **`rule_metadata_contradiction`.**
  - Fire only when `declared_metadata.has_missing_values` is False, "no" or "false".
  - Scan `documentation_excerpts`, then `quality_notes`.
  - **Strip negations first** ("no missing values", "Has Missing Values? No"), then match a general vocabulary: missing values/data/readings, NaN, null values, standalone `-200`, `-999` or `-9999`, a quoted `'?'`.
  - Guard against false positives such as "Licence is missing", "-2000 m" and "considered zero".
- **After G4,** any earlier assess run must be redone. `rule_warnings` makes `check` fail.

### G5: `## Verdict calibration` in `prompts/risk_assessor.md` (same report)
- **The test.**
  - The text `LEARNER TODO (G5)` must be gone, so delete the whole comment.
  - Its regex is DOTALL, so: use the word "calibration" **only in the heading**; no `###` inside the section; use a flat `1.` or `-` list (not `1)` or `**1.**`).
  - At least 6 rules are needed.
  - Check with `grep -n -i calibration discovery_agent/prompts/risk_assessor.md`.
- **Inconsistencies already in the prompt that your rules should resolve:**
  - attribution is listed under both `feasible` and `feasible_with_conditions`;
  - the overall-verdict rule ignores a **partially_met must need**, and its "every" vs "any" wording is ambiguous;
  - severity contradicts the Verdicts text: INT-DUPLICATE-SOURCE is minor and COV-GRAIN-MISMATCH is major, yet the text calls both not feasible.
- **Topics you decide** (options are in the report):
  1. severity → default verdict
  2. one verdict for several targets (best or worst)
  3. FRS-STALE on historical windows (keep the flag without a verdict impact, or dismiss it; dismissing removes it from the scored `red_flags`)
  4. partial vs out-of-window for core vs context needs
  5. how coarse is too coarse
  6. unknown, non-commercial, research-only or conflicting licences (UCI 360 says "exclusively for research purposes")
  7. attribution only
  8. expired agreement and refused host
  9. access request only
  10. personal data and purpose limitation
  11. changes inside a window and catalog-vs-wiki conflicts
  12. join keys with no mapping
  13. sentinels
  14. superseded copies
  15. geography and unknowns
  16. when to dismiss a rule flag
  17. severity overrides (suggested default: none)
  18. roll-up to need coverage and the overall verdict (decides UC2)
- **Feasible-for-one-need case for decisions.md:** `link.uci_360` is fully covered for N1 in the prototype window and 0% in production (and research-only). Run the rule with `["prototype"]`, then `["prototype","production"]`, then `["production"]` to show the contrast. Alternatives: Eurostat is annual, so it fits N6 but not N1; the UC2 sales history behaves differently before and after the code change.
- **Verdict vocabulary.**
  - source: `feasible | feasible_with_conditions | not_feasible`
  - need: `met | met_with_conditions | partially_met | unmet`
  - sign-off: `proceed | proceed_with_conditions | stop`
- **LLM noise.** Verdicts can change between identical runs; say so in your before/after.

### G6: allowlist (report: `planning/work_notes/review_G6_allowlist_live_probe.md`)
- **Add exactly one host: `ec.europa.eu`.** It serves the API, the ESMS metadata page and the copyright notice (all verified live).
  - UCI needs nothing new: its API, page, data.csv and zip are all on `archive.ics.uci.edu`.
  - **Never add `catalog.data.gov`.**
- **Matcher behaviour.** The matcher accepts a host *or any subdomain*, and a provided test requires this. Do not edit the matcher, and leave the 6 existing entries alone.
- **Budget accounting.** A refusal costs 0 budget requests. A redirect refusal costs 1 (for example the Nager docs URL → `nagerholidays.com`).
- **Hosts to list as "not added", with reasons:** `catalog.data.gov`, `europa.eu`, `commission.europa.eu`, `www.eea.europa.eu` (your call, given the EEA commercial-reuse exception), `creativecommons.org`, `doi.org`, `nagerholidays.com`, `api.atmosdata.example`.

### G7: ranked hypotheses to check in YOUR traces (observe first; never fix an unobserved failure)
The G7 review agent hit the usage limit, so this section comes from the planning session's own reading plus the other reports.

| # | Hypothesis (README hint) | Where to look | Cause and fix location | Narrow re-run | Measurable before/after | Decision affected |
|---|---|---|---|---|---|---|
| 1 | **The profiler reads `-200` values as real.** The sampler matches sentinels by exact string, so `-200.0` is missed. Verified live: C6H6(GT) has 366 rows of `-200.0` but is reported `non_missing_share 1.0` with `sentinel_counts {}`; CO(GT) misses 91. | `records/link.uci_360.json` `sample_findings`; the `sample_data_file` result in `transcripts/profiler__link.uci_360.json` | `tools/links.py:33` `SENTINELS`, and the comparison around line 103. Fix: numeric-equivalence matching (`float(v) in {-200,-999,-9999}`), optionally plus the tool description. | `run --use-case UC1 --from-stage profile --stop-after profile --only link.uci_360 --no-input`, then `--from-stage assess` | C6H6 sentinel count 0 → 366; non_missing_share 1.0 → ~0.961; CO 1592 → 1683; DQ-SENTINEL-VALUES evidence | Which pollutants are usable for the N1 prototype |
| 2 | **Open-Meteo:** the register probe range 2014-01-01..03 (or the single probe grid point) is recorded as the data period or geography | `records/api.open_meteo_archive.json` `temporal`, `spatial`; `rule_flags.json` (false COV-OUT-OF-WINDOW / FRS-STALE) | `prompts/profiler.md` public_api bullet (line 7): temporal comes from the provider's documented coverage, probing both window ends, and never from the probe range | `--only api.open_meteo_archive` (each UC), then assess | False flags present → absent; temporal fields | The N3 verdict (a must need) |
| 3 | **UC2: the 2024 product-code change is missed for `sales.daily_by_product`.** `product_codes_2024.md` names only `sales.products`, so it is not a backlink of `daily_by_product` (backlinks need the exact entry id, `internal_catalog.py:126`). | `records/internal.sales.daily_by_product.json` `quality_notes`; flags (INT-JOIN-KEY-MISMATCH) | Profiler prompt (internal: also search the wiki for the entry's key columns) or the `get_catalog_entry` backlink logic | `--only internal.sales.daily_by_product`, then assess | Flag absent → present; the note quotes the wiki | UC2 N1/N2 and the overall verdict |
| 4 | **UCI `temporal.end` taken from the docs ("February 2005")** instead of the whole-file sample (2005-04-04) → false COV-PARTIAL-WINDOW (91%) | `records/link.uci_360.json` `temporal.end`; `rule_flags.json` | `profiler.md:21` (the whole-file sample rule) | `--only link.uci_360` | end 2005-02-28 → 2005-04-04; the flag disappears | Prototype coverage verdict |
| 5 | **Catalog-vs-wiki conflicts missed:** VR-03 switched off 2024-06-30 while the catalog says active; traffic counters redefined 2024-03-18 (per direction → combined) | Records for `internal.airq.station_readings` and `internal.traffic.hourly_counts`; scout and profiler `read_wiki_page` calls | Scout or profiler prompt (backlinks exist here, so this is less likely) | `--only <id>` | GOV-CATALOG-WIKI-CONFLICT / DQ flag absent → present | N1 and N2 production feasibility |
| 6 | **Refused host retried or an alternate route tried** (Chicago, Nager docs) | Refused counts per URL (§18); profiler transcript | `profiler.md:18` / `_shared_rules.md:8` / tool message | dry-run folder only (§12) | Refused events per run | Guardrail penalty, `check` |
| 7 | **Risk Assessor copies `raised_by` into `red_flags`** (the schema forbids it) → rejected submits that waste turns (max 8) | `submit` events with `ok:false` for `risk_assessor` | Prompt, or stripping `raised_by` in the orchestrator | `--from-stage assess` | Rejected submits N → 0; turns used | Risk of assess failing |
| 8 | **Eurostat licence asserted without evidence** (the json_stat branch gives no licence evidence) | `records/link.europa_sdg_11_52_099aa6.json` `licence.evidence` | Profiler prompt, or surfacing the ESMS link from `extension.annotation` in `links.py` | `--only link.europa_sdg_11_52_099aa6` | Evidence cites a probed `ec.europa.eu` terms URL, or null with LIC-UNKNOWN | N6 verdict, licence conditions |

---

## 11. Use-case traps: reviewer checklist
> These are **reviewer expectations to check the agent against, not answers to copy.** Verdicts are yours (G5 and the sign-off). Both use cases have `as_of` 2026-10-15.

### UC1: Valdena Civic Health Office (air quality, traffic, clinic)
Windows: prototype 2004-03-10..2005-04-04; production 2024-01-01..2025-12-31.

Needs:
| Need | Description | Priority | Grain | Windows |
|---|---|---|---|---|
| N1 | Pollutants | must | hourly | both |
| N2 | Traffic | must | hourly | production |
| N3 | Temperature and humidity | must | hourly | both |
| N4 | Clinic counts by district | should | daily | production |
| N5 | Patient-level records | could | event | production |
| N6 | Deaths linked to PM2.5 | could | annual | both |

| Expected source | Serves | Planted traps (evidence) | Flags to look for | Verdict question |
|---|---|---|---|---|
| `internal.airq.station_readings` | N1 production | `wiki/station_network.md`: VR-03 switched off 2024-06-30, but the catalog says active; timestamps are `ts_utc` | GOV-CATALOG-WIKI-CONFLICT; COV-PARTIAL-WINDOW only if also targeted at prototype (data starts 2023) | fwc: access request, handle the VR-03 gap |
| `internal.traffic.hourly_counts` | N2 production | `wiki/counter_replacement_2024.md`: from 2024-03-18 counts are both directions combined (before: per direction), with no catalog note; `ts_local` (DST) vs stations' `ts_utc`; no counter↔station key in the catalog | GOV-CATALOG-WIKI-CONFLICT, DQ-SEMANTIC-ENCODING (definition change), possibly DQ-DST-ARTEFACTS / INT-NO-JOIN-KEY | fwc: adjust for the change, align time zones |
| `internal.clinic.resp_visits_daily` | N4 | `wiki/clinic_data_policy.md` says this is the **only** clinic table allowed | none or minor | feasible / fwc (access request) |
| `internal.clinic.patient_visits` | N5 | restricted, `contains_pii`; the policy **forbids** using it; postcode and age band are personal data | GOV-PII (rule), ACC-RESTRICTED (rule), GOV-PURPOSE-LIMITATION, possibly GOV-CONSENT-GAP | likely not_feasible; N5 unmet by design (the brief puts it out of scope) |
| `api.open_meteo_archive` | N3 both windows | Default query: coordinates were **Lisbon**, now Milan (your decision); probe dates 2014-01-01..03. Default variables are `temperature_2m, shortwave_radiation`, which do **not** include humidity (N3 needs `relative_humidity_2m`). This is reanalysis, not station data. **Lead to verify at source:** the terms of use (`https://open-meteo.com/en/terms`) may limit the free API to non-commercial use; check it for the production warning service. | LIC-ATTRIBUTION (verify the licence page); false coverage flags from the probe range | feasible / fwc |
| `api.nager_public_holidays` | **No UC1 need** | Tagged for UC1 in the register, but there is no holiday need: a **precision trap** | It should be rejected without profiling | — |
| `vendor.atmosdata_pro` | N3 (and N1?) | Contract ended 2025-12-31; key revoked 2026-01-01; **never call it** (the tool refuses) | LIC-AGREEMENT-NOT-ACTIVE (rule), ACC-UNREACHABLE | not_feasible (say what would change it) |
| `link.uci_360` | N1 prototype | CC BY 4.0 link vs "exclusively for research purposes. Commercial purposes are fully excluded"; `-200` (and `-200.0`) sentinel; API `has_missing_values: no` vs page "Yes" and the notes; notes say Mar 2004–Feb 2005 while the file runs to 2005-04-04; unnamed "Italian city"; single device; page "last updated" 2024 is not a data date; DD/MM vs M/D date format | LIC-ATTRIBUTION, DQ-METADATA-CONTRADICTION, DQ-SENTINEL-VALUES, FRS-STALE, FRS-METADATA-DATE-MISLEADING; possibly GOV-PURPOSE-LIMITATION / LIC-NONCOMMERCIAL, INT-REPRESENTATIVENESS | fwc for prototype; no production overlap |
| `link.europa_sdg_11_52_099aa6` | N6 both windows | Annual; 2005 and 2007–2023 (no 2006); nothing for 2024–25; `updated` 2025-12-09 is not the data end; upstream EEA (the copyright notice excludes commercial reuse of non-Eurostat data) | COV-PARTIAL-WINDOW; possibly FRS-METADATA-DATE-MISLEADING, LIC-ATTRIBUTION / LIC-MIXED | fwc as national context only |
| `link.data_open_air_chicago_hour_aggre_d4970b` | N1 prototype | Host refused (`DOMAIN_NOT_ALLOWLISTED`); a US city per the link note; the link type cannot be detected | ACC-UNREACHABLE (rule), LIC-UNKNOWN (rule), COV-GEO-MISMATCH | not_feasible; **the refusal is the finding** |

Sketch of likely need coverage (your call):
- N1: met with conditions (UCI for prototype + stations for production)
- N2: met with conditions
- N3: met with conditions
- N4: met or met with conditions
- N5: unmet, by policy
- N6: partially met

The overall verdict is most likely `feasible_with_conditions`.

**Register policy** (`policy.open_data_links`): datasets with an unknown or non-commercial licence, or behind a login, need **Legal review**; **production use of any external dataset needs Legal sign-off**. Use this in conditions.

**Step 2b targets (UC1).** After the scout, the needs most likely unmet are N1 (prototype window: internal data starts 2023) and N6. The prescribed links already address both. Search with your script for, for example, Italian regional environmental-agency (ARPA) open data or EEA historical air-quality data with hourly readings for a *named* northern-Italian city. Only a cited URL from your search counts.

### UC2: Valdena Gelato Shop (sales, weather, holidays)
Windows: history 2023-06-01..2025-05-31; recent 2025-06-01..2026-03-31.

Needs:
| Need | Description | Priority | Grain | Windows |
|---|---|---|---|---|
| N1 | Daily sales by product | must | daily | both |
| N2 | Old↔new product-code mapping | must | static | history |
| N3 | Daily maximum temperature | must | daily | both |
| N4 | Italian public holidays | should | daily | both |
| N5 | Opening days and local events | should | daily | both |

UC2 has no dataset links and no vendor feed.

| Expected source | Serves | Planted traps (evidence) | Flags to look for | Verdict question |
|---|---|---|---|---|
| `internal.sales.daily_by_product` | N1 | `wiki/till_migration_2024.md`: **no rows 2024-02-05..2024-03-10** (treat as missing, not zero), while the catalog shows continuous coverage from 2022; codes changed **2024-04-01** (`product_codes_2024.md`, which is *not* a backlink of this entry); classification confidential | GOV-CATALOG-WIKI-CONFLICT, INT-JOIN-KEY-MISMATCH | fwc |
| `internal.sales.products` | N2 | Lists **only the current codes**; "No mapping table exists"; matching is possible only by name, and some names are not unique | INT-JOIN-KEY-MISMATCH / INT-NO-JOIN-KEY | **N2 partially met or unmet**: the key decision for UC2's overall verdict (G5 roll-up) |
| `internal.store.calendar` | N5 | Refreshed weekly; open to analytics roles | — | feasible |
| `api.open_meteo_archive` | N3 | Needs `daily=temperature_2m_max`. Coordinates = Milan. The recent window ends 2026-03-31, which the archive already holds. **Lead to verify at source (found by the option-B test search):** Open-Meteo's data licence is CC BY 4.0, but its terms of use (`https://open-meteo.com/en/terms`) may limit the free API to non-commercial use, and the gelato shop is a business. The Profiler reads only `terms_url` = `/en/licence`, so it may miss this. That is worth catching in your memo review, and it could be a G7 candidate if the record shows no sign of it. | LIC-ATTRIBUTION; possibly a condition (a commercial API plan) or GOV-PURPOSE-LIMITATION, if the terms confirm it | feasible / fwc |
| `api.nager_public_holidays` | N4 | National holidays only (no local patron-saint day); terms on GitHub (MIT); the docs URL redirects to a refused host | none / minor | feasible / fwc |

**Step 2b (UC2, only in the P11 reuse check).** N2 is internal, and no public source can map private product codes. "None accepted" is a valid, honest outcome.

### Open-Meteo city (Q4): options for your decision
There is one register entry, shared by both use cases, so pick one city. The briefs say Valdena is fictional, in northern Italy, and that no source names the city.

**Decided (2026-11-23): Milan, latitude `45.46`, longitude `9.19`**, set in commit `6e7da42`. The reasons given when it was recommended:
- It is in northern Italy, as both briefs require.
- It is in the Po Valley, one of Europe's worst air-pollution areas, so "poor-air days" are frequent and UC1's question is meaningful.
- It has hot, humid summers, which fits UC2's "hot days raise sales" question.
- Lombardy's regional environment agency publishes open air-quality data, which is worth checking in Step 2b for a same-city N1 source. Its coverage of the 2004–2005 prototype window is not verified.

Write the city, the coordinates and your reason, in your own words, as an assumption under decisions.md → "Other decisions".

**Caveat for your review (true for any city):** the UCI 360 prototype data comes from an unnamed Italian city. Weather for your chosen city therefore only approximates the conditions behind the prototype readings. Mention this in review_UC1.md.

Alternatives:
- **Verona** (about 45.44, 10.99). Station code "VR-03": VR is Verona's province code. That is a weak hint, not proof: "VR" may simply stand for "Via Roma", the station's street.
- **Milan** (about 45.46, 9.19). It sits in the Po Valley, a well-known air-pollution hotspot, which makes it representative for UC1.
- Any other northern-Italian city you can justify.

Record the city, the coordinates and your reason in `decisions.md` → "Other decisions", and say it is an assumption.

---

## 12. Run discipline and foot-guns
1. **The trace is append-only, and `check` counts refused requests per URL across *all* runs.** More than 2 refused events for one URL makes `check` fail **permanently**, and the hidden scorer also applies guardrail penalties from the trace.
   - Profile all UC1 links **once** (P6).
   - Afterwards, re-profile only with `--only <ids>`, and never include `link.data_open_air_chicago_hour_aggre_d4970b`.
   - Re-run the counter after every run (§18) and update §1.
   - If the count ever reaches 3: **stop and ask**. The only clean recovery is to archive `outputs/UC1` outside the repo and do one clean full re-run. Never edit the trace.
2. **Snapshot before any re-run you will cite.** Copy into `outputs/artifacts/snapshots/<label>/`: transcripts, `discovery_results.json`, `risk_assessment.json`, `rule_flags.json`, the relevant records. Transcripts and results are **overwritten** on re-run. Copies are allowed; edits are not.
3. After any re-profile, run `--from-stage assess` (it also runs memo) so the results and memo match the records.
4. After a scout re-run, pass `--links-file outputs/UC1/links.json` (otherwise the stale `candidates_final.json` is reused silently), together with `--only` for any new ids.
5. **Always pass `--no-input`.** Links typed at the interactive gate prompt bypass `gate_decisions.json`.
6. `--only` with a misspelt id profiles nothing, gives no error, and still adds a line to `run_history.jsonl`. Copy ids from `candidates_final.json`.
7. **Every invocation overwrites `run_summary.json` and appends to `run_history.jsonl`**, including failed gate runs. TC-018 therefore runs in a throwaway copy, and model usage is **summed over `run_history.jsonl`**.
8. **Final order:** assess+memo → review → sign-off → `check` → save `check_<ID>.json` → freeze. Any later run means re-running `check` and saving it again.
9. Traced conclusion: the field must be **non-null** and reached through **dict keys only**.
10. `check` only tests that `gate_decisions.json` *exists*. Coverage and reason length are enforced when the pipeline runs, so keep the file consistent with `links.json` (use the pre-check).
11. Never edit `tests/test_learner_gaps.py` or `config/settings.json`, and never add test files. 52 tests is the expected count.
12. A run with no credentials still creates an empty `outputs/<ID>/`, which is harmless.
13. **LLM answers vary between runs.** Interpret a single verdict change cautiously; re-run if it matters and say so.
14. `outputs/artifacts/inspect_*.txt` and other manual tool runs are **not** written to the trace. The rubric still says "do not retry Chicago more than twice", so inspect it once and reuse the output.
15. **Claude Code backend usage.** Every model call spends your claude.ai plan's usage (5-hour limit). Run stage by stage, never re-run a whole pipeline to fix one source, and check the `run_history.jsonl` totals after each run.

---

## 13. Deliverables checklist
Paths are relative to REPO. ✍ means it must be in **your own words**.

| ☐ | Path | Produced by | Phase |
|---|---|---|---|
| ☐ | `.claude/skills/data-discovery-agent/SKILL.md` = `skills/data-discovery-agent/SKILL.md` (Steps 3–5) + `skills/data-discovery-agent/README.md` | You + Claude draft | P1, P10 |
| ☐ | `discovery_agent/` changes for G1, G3, G4, G5, G7, plus the opt-in Claude Code backend (visible in the diff and the trace) | Claude, reviewed by you | P1b, P4, P7, P8 |
| ☐ | `config/allowlist.json` (+ `ec.europa.eu` only) and `config/external_sources_register.json` (lat/long only) | Claude, after your decision | P5, P6 |
| ☐ | `scripts/web_search.py` | Claude, from your README prompt | P3 |
| ☐ | `tests/` unchanged; all 52 pass | — | P13 |
| ☐ | `outputs/UC1/`: search_plan, candidates, candidates_final, records/, rule_flags, risk_assessment, discovery_results, feasibility_memo, trace.jsonl, transcripts/, run_summary, run_history, **links.json**, **gate_decisions.json** ✍, **signoff.json** ✍ | Pipeline + you | P2–P9 |
| ☐ | `outputs/UC2/`: the same set (no links or gate file) + **signoff.json** ✍ | Pipeline + you | P6–P9 |
| ☐ | `outputs/artifacts/decisions.md` ✍: Source suggestions; G1 and G3 edge cases; G4–G5 feasibility case and dismissed flags; G6 table + not-added hosts; G5 rationale + before/after; G7 (8 fields); Other decisions (Open-Meteo city); reuse-check notes | You (Claude drafts facts) | P3–P11 |
| ☐ | `outputs/artifacts/step0_checks.md` | Claude (skill Step 0) | P2 |
| ☐ | `outputs/artifacts/pytest_before.txt`, `pytest_after.txt` | Commands | P1, P13 |
| ☐ | `outputs/artifacts/check_UC1.json`, `check_UC2.json` (`problems: []`) | `check` | P9 (re-saved in P13) |
| ☐ | `outputs/artifacts/review_UC1.md`, `review_UC2.md` ✍ | You | P9 |
| ☐ | `outputs/artifacts/walkthrough.md` ✍ | You | P12 |
| ☐ | Supporting evidence: `inspect_*.txt`, `snapshots/`, `tc018_gate_runs.txt`, `tc024_secret_scan.txt`, `rubric_evidence.md`, optional `reuse_check_UC2/` | Claude | P5–P13 |
| ☐ | `README.md` → "Submission notes" ✍ (reuse check ×3, delivery reflection ×3, ownership ×3) | You | P12 |
| ☐ | `CLAUDE.md`, `requirements.txt`, `.env.example`, `.flake8`, `.gitignore`: unchanged unless documented | — | — |
| ☐ | `internal/`, `links/`, `use_cases/`: unchanged | — | — |
| ☐ | `Stack AI Rewire - DS - Data Discovery - Evaluation Rubric.xlsx` (both sheets filled, PR link in D11) | You | P13 |
| ☐ | The PR, `work/data-discovery → main`, reviewable by the instructor | You | P13 |
| ☐ | `806637_Subhadeep_Paul_data_discovery.zip` uploaded to Paradiso | You | P13 |
| — | `planning/` (this plan, the review notes, your worksheet): **not a deliverable**; removed before the PR and skipped by the zip script | — | P13 |
| — | Optional stretch UC3 (`use_cases/UC3_*`, `internal/UC3_*`, `outputs/UC3/`) | Not planned (Q7) | — |

---

## 14. Rubric fill-in map
**Sheet 1 ("Learner Submission" + "Learner Evidence"; you write these).** Confirm each point in the "What Learner Should Enter" column, citing files:

| Row | Pts | Cite |
|---|---|---|
| Automatic Scoring | 40 | `outputs/UC1/`, `outputs/UC2/` (traces and transcripts kept), `gate_decisions.json`, both `signoff.json`, `check_*.json`, settings unchanged, Chicago accepted with a reason |
| Core Implementation | 11 | licence.py, formats.py, risk_rules.py; pytest_before and pytest_after; decisions.md G1/G3 |
| Calibration | 5 | risk_assessor.md (≥ 6 rules); decisions.md G5 + the feasible-for-one-need case |
| Agent Improvement | 10 | decisions.md G7 (8 fields), snapshots |
| Review Judgement | 16 | review_UC1/UC2.md, both signoff.json, check outputs |
| AI-Native Skill | 10 | both SKILL.md copies, README Submission notes, `scripts/web_search.py` (generated with Claude Code and used by Step 2b) |
| Governance | 4 | allowlist.json, decisions.md G6 + not-added hosts (Chicago) + Source suggestions + gate reasons, `-k g6` |
| Walkthrough | 4 | walkthrough.md |
| Pull request link | — | D11 = the PR URL |

**Sheet 2.** Claude runs these; you paste the actual output and mark Pass/Fail.

| TC | Command / evidence | Phase | Notes |
|---|---|---|---|
| 001–005 | `python -m pytest tests/test_learner_gaps.py -k g1 -v`, plus a python snippet printing `extract_licence` output for each input (prompt in the G1 report) | P4 | — |
| 006–007 | `-k g3 -v`, plus the summaries printed (prompt in the G3 report) | P4 | — |
| 008–014 | `-k g4 -v`, plus `evaluate()` on the TC-014 record | P4 | TC-012 calls N1 "15-minute" but the contract says hourly. TC-014's "NOT_IMPLEMENTED" wording differs from the real warning text. Note both. |
| 015 | `-k g5 -v` + `grep -n -i calibration discovery_agent/prompts/risk_assessor.md` | P8 | — |
| 016 | `-k g6 -v` + allowlist.json + decisions.md G6 | P5 | — |
| 017 | The saved `outputs/artifacts/inspect_<chicago id>.txt` (DOMAIN_NOT_ALLOWLISTED) + gate accept + review finding | P5/P9 | Reuse the saved output; do **not** re-run more than twice |
| 018 | `pytest tests/test_agent_loop.py -k links` + the 3 negative runs **in a throwaway copy** → `tc018_gate_runs.txt` | P13 | Needs `.env` loaded with the RUN prefix (no model calls are made) |
| 019 | decisions.md Source suggestions (exact URL, needs, coverage as stated, your decision and reason, citation) | P3 | — |
| 020 | pytest_before (52 / 32 / 20) and pytest_after (52 / 52); `diff tests/test_learner_gaps.py BUNDLE/starter-code/tests/test_learner_gaps.py` gives no output | P1/P13 | — |
| 021 | `check UC1`, `check UC2` → `problems: []` | P9 | — |
| 022 | Records with null licence/owner/cadence listed in `unknowns` (for example Chicago `licence.name` null) | P9 | — |
| 023 | `pytest tests/test_tools_offline.py -k vendor`; `grep -n "api.atmosdata.example" outputs/UC1/trace.jsonl` should show no `http` events; login walls → ACC-RESTRICTED | P13 | — |
| 024 | `check` reports no email-like values + token grep (§15) → `tc024_secret_scan.txt` | P13 | — |
| 025 | `diff config/settings.json BUNDLE/starter-code/config/settings.json` gives no output; `git log --stat -- outputs/` shows every output came from a pipeline run or a template you filled | P13 | — |

---

## 15. Packaging and submission
**Secret scan.** It never prints the token; exit code 1 means no match.
```bash
cd ~/projects/data-discovery
set -a && . ./.env && set +a
grep -rIlF -f <(printenv ANTHROPIC_AUTH_TOKEN) --exclude-dir=.git --exclude-dir=.venv --exclude=.env . ; echo "exit=$?"
git log -p --all | grep -cF -f <(printenv ANTHROPIC_AUTH_TOKEN)      # expect 0
```

**Zip.** `zip` is not installed, so use Python. Run it from REPO; it writes `~/806637_Subhadeep_Paul_data_discovery.zip`.
```bash
python - <<'EOF'
import os, zipfile, pathlib
repo = pathlib.Path.home() / "projects" / "data-discovery"
name = "806637_Subhadeep_Paul_data_discovery"
out = pathlib.Path.home() / f"{name}.zip"
skip_dirs = {".git", ".venv", "venv", ".cache", "__pycache__", ".pytest_cache", ".vscode", ".idea", "planning"}
skip_rel = {".env", ".claude/settings.local.json"}
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            p = pathlib.Path(root) / f
            rel = p.relative_to(repo).as_posix()
            if rel in skip_rel or f.endswith(".pyc") or f == ".DS_Store":
                continue
            z.write(p, f"{name}/{rel}")
print(out)
EOF
python -m zipfile -l ~/806637_Subhadeep_Paul_data_discovery.zip | grep -E "\.env$|\.git/|\.venv/|__pycache__|\.cache/" ; echo "(nothing above = clean)"
```

**Check the zip against the required structure:**
- `.claude/skills/data-discovery-agent/SKILL.md`
- `config/`, `discovery_agent/`, `internal/`, `links/`, `scripts/web_search.py`, `tests/`, `use_cases/`
- `skills/data-discovery-agent/{SKILL.md,README.md}`
- `outputs/UC1/`, `outputs/UC2/`
- `outputs/artifacts/` (the 9 required files)
- `CLAUDE.md`, `README.md`, `requirements.txt`, `.env.example`, `.flake8`, `.gitignore`
- the rubric xlsx

**Do not include** the Assignment Doc, the Helper Guide or `planning/` (the plan, the review notes, your worksheet). The zip script above skips `planning/`, and P13 removes it from the submission branch before the PR.

Submit the zip in **Tiger Academy (Paradiso)**.

---

## 16. Inconsistencies found in the bundle docs
| # | Inconsistency | How we handle it |
|---|---|---|
| 1 | README §4 uses `cp links/UC1_example_links.json ...`; the Helper Guide and SKILL use `cp -n` | Always `cp -n`, once only |
| 2 | Task 2 says "Steps 0–2"; README §5 says "Steps 0–2b" | Run 0–2 (P2), generate the script, then 2b (P3) |
| 3 | README §10 describes the walkthrough as "15 minutes with your instructor"; elsewhere it is a written `walkthrough.md` | Write the file and be ready to present it |
| 4 | README l.93 ("do not expect every link to show LIC-UNKNOWN") vs l.155 ("Until then, every dataset link is LIC-UNKNOWN") | The code supports l.93 for landing pages; the UCI path has no licence evidence before G1 |
| 5 | README §9 says "G1–G3 edge cases" | G2 is ungraded: document G1 and G3 |
| 6 | Rubric TC-012 calls N1 a "15-minute need" | The UC1 contract says hourly; note it in the rubric |
| 7 | TC-014 says "skipped as NOT_IMPLEMENTED" | The real warning is "<rule> skipped: ... learner TODO (G4)"; paste the real output |
| 8 | README and Helper Guide say `run_history.jsonl` is "one line per stage run" | It is one line per **invocation**, including failed ones; sum it |
| 9 | SKILL Step 1 item 4 tees into `outputs/<ID>/` before that folder exists | `mkdir -p outputs/<ID>` first; record this in the reuse-check answers and fix it in SKILL.md |
| 10 | README §4 expects the Chicago link to be detected as a "Public landing page" | Impossible, because the host is refused; the type stays unknown and the refusal is the finding |
| 11 | Deliverables say "full runs through assess", but `check` requires the memo headings | Always run through memo |
| 12 | The Helper Guide's UC1 command block is concatenated onto one line | Use the README §4 block |
| 13 | `formats.py:18` says G2 is checked by the tests | It is not; ignore |
| 14 | The reuse check "profiles accepted links for UC2" while "UC2 needs no gate file" | An accepted UC2 link needs `outputs/UC2/links.json` + `gate_decisions.json` + an allowlist host. Do it in the separate worktree (P11). |
| 15 | `check` says "for each dataset link" but only tests that the gate file exists | Use the pre-check (P5) |
| 16 | The Assignment and Helper Guide assume Claude Code runs on the gateway ("same values as Claude Code") | Optional (Q5); the pipeline works with `.env` either way |
| 17 | The bundle assumes gateway credentials "Provided by email"; none were provided | The pipeline's model calls use the opt-in Claude Code backend (P1b) with `claude-sonnet-5-5`; Step 2b uses option B (§7). No email to the instructor (B2, 2026-11-26). |

---

## 17. Important links mapped to tasks
These came from `Important_links.md`. The link-summary agent hit the usage limit, so only the JSON-stat spec was actually opened (by the G3 reviewer). The rest are mapped by URL and topic and are **not verified**.

| Link | Topic | Helps with | Priority |
|---|---|---|---|
| https://json-stat.org/format/ | JSON-stat 2.0 format (value/status as array or object, index as array or object, row-major order, role) | **G3** | High (checked) |
| https://www.idescat.cat/dev/api/taules/jsonstat/SKILL.md | A real SKILL.md for an API that serves JSON-stat | **G3**; style ideas for **SKILL Steps 3–5** (P10) | High |
| https://claude.com/resources/articles/building-agents-with-the-claude-agent-sdk | Building agents with the Claude Agent SDK | Understanding agent loops, tools and validation (P2, **G7**) | Medium |
| https://www.freecodecamp.org/news/testing-in-python-with-pytest/ | pytest tutorial | Running `-k` selections and `-v` evidence (P4, P13) | Medium |
| https://dev.to/devasservice/getting-started-with-pytest-2541 | pytest basics | Same as above | Low |
| https://campus.datacamp.com/courses/introduction-to-data-quality/defining-data-quality-terms?ex=6 | Data-quality terminology (DataCamp) | Words for the DQ flags and memo review (G4, G5, P9) | Medium |
| https://www.statcan.gc.ca/en/wtc/data-literacy/catalogue/892000062020001 | Statistics Canada data-literacy training item | Data-quality and metadata background (P9) | Low |
| https://www.youtube.com/watch?v=rRM0pMkLN_I | Video, content not reviewed | Unknown | — |
| https://www.youtube.com/watch?v=lkHkYCkOKcs | Video, content not reviewed | Unknown | — |

---

## 18. Command reference and trace cheat sheet
Run from REPO, using the RUN prefix for commands marked †.
```bash
# Pipeline
† python -m discovery_agent run --use-case UC1 --stop-after scout --no-input                          # plan + scout
  cp -n links/UC1_example_links.json outputs/UC1/links.json                                          # once, after the scout
† python -m discovery_agent run --use-case UC1 --from-stage profile --links-file outputs/UC1/links.json --no-input   # profile→memo
† python -m discovery_agent run --use-case UC2 --no-input                                            # UC2 end to end
† python -m discovery_agent run --use-case UC1 --from-stage assess --no-input                        # rules + assessor + memo
† python -m discovery_agent run --use-case UC1 --from-stage assess --stop-after assess --no-input     # iterate G5 cheaply
† python -m discovery_agent run --use-case UC1 --from-stage profile --stop-after profile --only link.uci_360 --no-input
  python -m discovery_agent tool inspect_dataset_link '{"url": "<link>"}' --use-case UC1            # no LLM
  python -m discovery_agent tool sample_data_file '{"url": "<file>"}' --use-case UC1                # no LLM
  python -m discovery_agent validate-use-case UC1
  python -m discovery_agent check UC1 | tee outputs/artifacts/check_UC1.json; echo "exit=${PIPESTATUS[0]}"

# Tests
python -m pytest tests/ -q
python -m pytest tests/test_learner_gaps.py -q -k g1        # also: g3, g4, g5, g6
git diff --exit-code -- tests/test_learner_gaps.py config/settings.json && echo "unchanged"
```
**Trace cheat sheet.** `jq` is not installed, so these are Python one-liners. Event kinds: `llm_call`, `llm_retry`, `tool_call` (agent, tool, args, ok), `submit` (agent, ok, errors), `http` (agent, url, refused | status, from_cache).
```bash
T=outputs/UC1/trace.jsonl
# refused URLs: each must stay <= 2 across ALL runs
python -c "import json,collections,sys;c=collections.Counter(e['url'] for e in map(json.loads,open(sys.argv[1])) if e.get('kind')=='http' and e.get('refused'));print(c.most_common() or 'none')" $T
# tool calls per agent and tool
python -c "import json,collections,sys;c=collections.Counter((e['agent'],e['tool']) for e in map(json.loads,open(sys.argv[1])) if e['kind']=='tool_call');[print(v,k) for k,v in sorted(c.items())]" $T
# which wiki pages each agent read (VR-03, counter change, clinic policy, till, product codes)
python -c "import json,sys;[print(e['agent'],e['args']) for e in map(json.loads,open(sys.argv[1])) if e['kind']=='tool_call' and e['tool']=='read_wiki_page']" $T
# rejected submissions (validator errors): G7 material
python -c "import json,sys;[print(e['agent'],e['errors']) for e in map(json.loads,open(sys.argv[1])) if e['kind']=='submit' and not e['ok']]" $T
# hosts contacted live
python -c "import json,sys,re;print(sorted({re.sub(r'^https?://([^/]+).*$',r'\1',e['url']) for e in map(json.loads,open(sys.argv[1])) if e['kind']=='http' and not e.get('refused')}))" $T
# the vendor feed must never be fetched (expect no output)
grep -n '"kind": "http".*atmosdata' $T
# no account email in a run's files (the Claude Code backend shows the login's address to the model, §7); expect "0 0"
python -c "import json,pathlib,sys;a=(json.loads((pathlib.Path.home()/'.claude.json').read_text()).get('oauthAccount') or {}).get('emailAddress','').lower();t='\n'.join(p.read_text(errors='replace') for p in pathlib.Path(sys.argv[1]).rglob('*') if p.is_file()).lower();print(t.count(a) if a else 'n/a',t.count('@tigeranalytics'))" outputs/UC1
# model usage over all invocations (for the delivery reflection); inspect the keys first
python -c "import json,sys;rows=[json.loads(l) for l in open(sys.argv[1])];print(len(rows),'invocations; keys:',list(rows[-1].keys()));t=[r.get('totals',{}) for r in rows];print({k:sum(x.get(k,0) for x in t) for k in ('llm_calls','input_tokens','output_tokens','tool_calls')})" outputs/UC1/run_history.jsonl
```
