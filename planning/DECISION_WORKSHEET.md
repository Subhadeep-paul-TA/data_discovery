# Decision worksheet

Everything **you** have to decide or write for this assignment, in the order you will need it.

**How to fill it in**
- **Choices:** tick one box per decision by changing `[ ]` to `[x]`. *(Recommended)* marks my suggestion; the choice is yours, and you can change a tick later.
- **Your own text:** wherever you see **[YOU WRITE: …]**, replace the brackets with your own words.
  - Claude never writes these.
  - When you ask, Claude copies your text word for word into the right file, and notes there that you dictated it.
- **When:** each item names the phase it is needed in (P1b … P13; the phase list is in `planning/work.md` §1) and the file where the answer ends up. Items marked "after Px" depend on results you have not seen yet.

**Where things stand (2026-11-25)**
- **Your repo:** `~/projects/data-discovery`, on GitHub as `Subhadeep-paul-TA/data_discovery`, which is currently **public**.
  - `main` holds the untouched starter code.
  - Your work is on the branch `work/data-discovery`.
- **Done:**
  - setup, and `pytest_before.txt` (32 passed, 20 failed);
  - the Milan coordinates;
  - this `planning/` folder (the plan, the review notes, this worksheet).
- **Next:** a new Claude Code session builds the "Claude Code backend" (phase P1b). No gateway credentials were provided, so the pipeline's agents will call Claude through the `claude` command instead.
- **To continue:**
  1. In a WSL terminal, run `code ~/projects/data-discovery`.
  2. Start a new Claude Code session.
  3. Paste the prompt from the "### P1b" section of `planning/work.md`.

---

## A. Already decided (for reference)
| # | Decision | Your choice | Still to write |
|---|---|---|---|
| A1 | How the agents reach a model, given no gateway credentials | Through the Claude Code CLI (an opt-in backend, built in P1b) | Disclosure text → B5 |
| A2 | Step 2b search (P3) | Option B: your `scripts/web_search.py` falls back to Claude web search when there is no gateway | Disclosure text → B5 |
| A3 | Weather location (Open-Meteo) | **Milan**, 45.46 / 9.19 (already set in the repo) | Your reason → B4 |
| A4 | Zip name, reviewer name | `806637_Subhadeep_Paul_data_discovery.zip`; reviewer "Subhadeep Paul" | — |
| A5 | Review time (delivery reflection) | Not measured: you will say so and make no time-saving claim | — |
| A6 | GitHub repo | `https://github.com/Subhadeep-paul-TA/data_discovery.git` | Visibility → B1 |

---

## B. Now (before P1b)

**B1. Repo visibility.** When: before your next push.
- Context: the repo is public.
- `planning/` contains our analysis of how the assignment is scored, and later the repo will hold your traces, answers and rubric.
- Anything pushed while it is public can be copied.

Options:
- [ ] Make it private first (GitHub → repo → Settings → General → Danger Zone → Change visibility), then push *(Recommended)*
- [x] Push now, make it private later
- [ ] Keep it public

**B2. Tell the instructor that no credentials were provided, and how you worked around it?** When: now, or before P13.
- [x] Yes. Email them now: no gateway credentials; the pipeline uses the Claude Code backend; Step 2b uses the Claude web-search fallback *(Recommended)*. No need to disclose it anywhere.
- [ ] No. Only disclose it in decisions.md, the README notes and the PR

[YOU WRITE: the email text, if you send one]

**B3. Model for the pipeline's agents.** When: P1b. Goes into: `.env` (`DISCOVERY_MODEL`).
- [ ] Claude Code's default model (Opus 5.5): best quality, but it uses more of your plan's usage limit *(Recommended)*
- [x] `claude-sonnet-5-5`: cheaper and faster, but the agents may be less careful, which affects the 40-point automatic score

**B4. Your reason for choosing Milan.** When: any time before P6. Goes into: `outputs/artifacts/decisions.md` → "Other decisions".
- Background only, not your text:
  - the briefs require northern Italy;
  - Milan is in the Po Valley, with frequent poor-air days;
  - it has hot summers;
  - one weather setting serves both use cases;
  - the UCI prototype data comes from an unnamed Italian city.

[YOU WRITE: the city, the coordinates (45.46, 9.19) and why you chose it. Mark it as an assumption.]
Answer :- Milan is therefore selected as the assumed location for the fictional client, Valdena, for the purposes of both UC1 and UC2, without making any assumptions about the unknown origin of the UCI prototype dataset.

**B5. Disclose the two workarounds.** When: after P1b (backend) and after P3 (search fallback); Claude first lists the facts in chat. Goes into: decisions.md → "Other decisions", the README "Submission notes", and the PR description.

[YOU WRITE: that no gateway credentials were provided, what you did instead and why, and what stayed unchanged in the pipeline]
No need to write anywhere.

[YOU WRITE: why Step 2b uses the fallback search, and how you checked every cited page yourself]
*(Need some context)*

**B6. Optional stretch: a third use case (UC3).**
- [x] No *(Recommended)*
- [ ] Yes

---

## C. P2: Steps 0–2 for UC1 (the skill run)

**C1. Step 0 will report the three gateway variables as missing.**
- [x] Answer "Intentional: the pipeline uses the Claude Code backend" and continue *(Recommended)*
No need of reporting

**C2. Confirm the UC1 needs table.** The skill stops and asks you. The needs:
| Need | Description | Priority |
|---|---|---|
| N1 | Hourly air pollutants | must |
| N2 | Hourly traffic (production only) | must |
| N3 | Hourly temperature and humidity | must |
| N4 | Daily clinic visit counts by district | should |
| N5 | Patient-level clinic records | could |
| N6 | National yearly PM2.5 deaths | could |

- [x] Confirm as is *(Recommended: the contract is provided, and changing it changes what is scored)*
- [ ] Change it: [YOU WRITE: what and why]

**C3. Dataset links for UC1.** The skill asks whether you have links.
- [x] Use the three prescribed links *(Recommended; the rubric requires them)*:
  - UCI 360 for N1, prototype window;
  - Eurostat `sdg_11_52` for N6, both windows;
  - Chicago for N1, prototype window, accepted on purpose so that its refusal is recorded.
- [ ] Something else: [YOU WRITE]

---

## D. P3: Step 2b suggestions (UC1)
Claude runs your search script and fills in the facts for up to five suggestions. **You open each page yourself**, then decide.
- At least one accepted suggestion must be inspected through the workflow (rubric TC-019), so accept at least one good source if one exists.
- Prefer a source whose host is already allowed (UCI, GitHub), or a single new host you can justify.
- Optional: [YOU WRITE: any search ideas of your own]

The table goes into decisions.md → "Source suggestions". Accepted suggestions are added to `outputs/UC1/links.json`.

| # | Publisher and exact URL *(Claude fills)* | Need ids, window | Coverage as the page states it *(Claude fills, or "not stated")* | Your decision | Your reason |
|---|---|---|---|---|---|
| S1 | | | | accept / reject / revise | [YOU WRITE] |
| S2 | | | | accept / reject / revise | [YOU WRITE] |
| S3 | | | | accept / reject / revise | [YOU WRITE] |
| S4 | | | | accept / reject / revise | [YOU WRITE] |
| S5 | | | | accept / reject / revise | [YOU WRITE] |

**D2. If an accepted suggestion's website is refused by the allowlist** (decide per host):
- [ ] Add that exact host: [YOU WRITE: what the host serves and why nothing broader is needed]
- [ ] Do not add it; record the refusal as a finding

---

## E. P4: design choices for the code gaps (G1, G3, G4)
Claude implements these; you approve the choices and review every change.

### G1: licence finder
**E1. A page's structured data says the licence is "Unknown" or "Other".**
- [ ] Treat that as final: no licence, which raises the LIC-UNKNOWN flag *(Recommended)*
- [ ] Keep searching the rest of the page

**E2. Two different licences appear on one page.**
- [ ] Report no licence (ambiguous) and keep both in the evidence *(Recommended)*
- [ ] Take the first one found

**E3. Which licences to recognise.**
- [ ] Core set: Creative Commons family, CC0, ODbL / ODC-By / PDDL, UK OGL, MIT, Apache-2.0 *(Recommended)*
- [ ] Core plus extras (GPL/BSD, older Creative Commons ports, per-file licences)

**E4. Extra tests.**
- [ ] Throwaway checks only, no new test files *(Recommended: the rubric expects exactly 52 tests)*
- [ ] Add a new test file

**E5. The G1 edge case for decisions.md.**
- [ ] The Kaggle page whose licence is "Unknown" *(Recommended)*
- [ ] Other: [YOU WRITE]

[YOU WRITE after P4: the edge case, what the code does with it, and how it changes the licence field and the flags]

### G3: JSON-stat summary
**E6. Country-code check.**
- [ ] The full list of official two-letter country codes *(Recommended)*
- [ ] A two-letter pattern plus a list of exceptions

**E7. Finding the time and country dimensions.**
- [ ] The format's role markers first, then the names "time"/"geo" *(Recommended)*
- [ ] Names only

**E8. A single status flag given for the whole table counts as…**
- [ ] every cell *(Recommended)*
- [ ] only the cells that have values

**E9. The G3 edge case for decisions.md.**
- [ ] A missing year: UC1's Eurostat table has no 2006, which raises no warning, unlike an empty latest year *(Recommended)*
- [ ] Other: [YOU WRITE]

[YOU WRITE after P4: the edge case, what the code does with it, and how it changes the summary and the catalog record]

**E10. The ungraded G2 (data-package summary).**
- [ ] Leave it as a stub *(Recommended)*
- [ ] Implement it

### G4: three deterministic rules
**E11. Grain rule.**
- [ ] Strict: any grain coarser than the need raises the flag; any tolerance belongs in the G5 calibration *(Recommended)*
- [ ] Tolerant

**E12. Staleness when a source's start date is unknown.**
- [ ] Skip, as the rule's own description says *(Recommended)*
- [ ] Compute it anyway

**E13. The contradiction rule reads…**
- [ ] documentation and quality notes only *(Recommended)*
- [ ] also the sample findings

[YOU WRITE after P4: for each rule, one UC1 or UC2 case where it changes the verdict, and why. This goes into decisions.md → "G4–G5".]

---

## F. P5: allowlist (G6) and gate decisions
**F1. Add `ec.europa.eu` to the allowlist.** Eurostat's API, metadata page and copyright page are all on that host.
- [ ] Yes, this exact host only *(Recommended; a test requires it)*
- [ ] No

[YOU WRITE: what ec.europa.eu provides and why a broader domain is not needed]

**F2. Hosts you choose not to add.** Write one reason each; this goes into decisions.md → "G6".

| Host | Your reason |
|---|---|
| `catalog.data.gov` (the Chicago link) | [YOU WRITE] |
| `europa.eu` | [YOU WRITE] |
| `commission.europa.eu` | [YOU WRITE] |
| `www.eea.europa.eu` (Eurostat's upstream data provider) | [YOU WRITE] |
| `creativecommons.org`, `doi.org` | [YOU WRITE] |
| `nagerholidays.com` (where the holiday API's docs link redirects) | [YOU WRITE] |
| `api.atmosdata.example` (the expired vendor feed) | [YOU WRITE] |

**F3. Eurostat's terms say non-Eurostat data (here, from the EEA) may not be reused commercially.**
- [ ] Record it as a Legal-review condition, and do not add the EEA host *(Recommended)*
- [ ] Add `www.eea.europa.eu` to read EEA's terms (this needs its own justification)

**F4. The six hosts already in the allowlist.**
- [ ] Leave them unchanged *(Recommended)*
- [ ] Change them

**F5. Gate decisions:** one per link, in `outputs/UC1/gate_decisions.json`. Each reason must be at least 20 characters, in your own words.

UCI 360:
- [ ] accept *(Recommended)*
- [ ] reject

[YOU WRITE: reason]

Eurostat `sdg_11_52`:
- [ ] accept *(Recommended)*
- [ ] reject

[YOU WRITE: reason]

Chicago:
- [x] accept on purpose (required by the rubric)

[YOU WRITE: reason]

Each accepted Step 2b suggestion: accept / reject, with [YOU WRITE: reason]

**F6. Test the Chicago link once in a scratch folder before the real UC1 run?** This shows whether the agent retries the refused host. Three refusals of the same URL would make the self-check fail permanently.
- [ ] Yes. It costs a few model calls *(Recommended)*
- [ ] No

---

## G. P6: full runs
**G1. Keep "before" copies of the results before any re-run** (in `outputs/artifacts/snapshots/`).
- [ ] Yes *(Recommended)*
- [ ] No

**G2. If the Chicago link is still refused a third time in the UC1 trace:**
- [ ] Stop. Claude asks you, then archives `outputs/UC1` outside the repo and does one clean full re-run *(Recommended)*
- [ ] Stop and leave it

---

## H. P7: G7, one real agent mistake
Claude first lists the mistakes it actually finds in your traces. **Pick one you actually saw:**
- [ ] The data sampler missed the "-200.0" missing-value codes in the UCI data
- [ ] The weather API's 2014 test dates were recorded as the data period
- [ ] UC2: the 2024 product-code change was missed for the daily sales table
- [ ] UCI's end date was taken from its documentation (Feb 2005) instead of the data (Apr 2005)
- [ ] A catalog-versus-wiki conflict was missed (station VR-03, or the 2024 traffic counter change)
- [ ] The agent retried a refused host
- [ ] The Risk Assessor's submissions were rejected again and again
- [ ] A licence was stated without evidence (Eurostat), or Open-Meteo's terms of use were not read
- [ ] Other: [YOU WRITE]

[YOU WRITE after P7: the symptom, in your words; the project decision this mistake could affect; why the fix is at the cause. Claude provides the measured before/after facts.]

---

## I. P8: G5 calibration (how red flags turn into verdicts)
Tick one option per topic. Claude turns your picks into 6–10 rules for the Risk Assessor and shows you the wording to approve.

**I1. Severity → verdict.**
- [ ] Blocker → not feasible, unless a named owner can clear it within the project. Major → feasible with one condition per flag. Minor only → feasible *(Recommended)*
- [ ] Any blocker → not feasible, always

**I2. One source with several targets (needs or windows) and different outcomes.**
- [ ] Give the verdict for the best target it can serve, and name the failing targets in the rationale *(Recommended)*
- [ ] Give the verdict for the worst target

**I3. Stale data on a historical window (UCI 360 ends in 2005).**
- [ ] Keep the flag; it does not lower the verdict when every target window is historical *(Recommended)*
- [ ] Dismiss the flag with a reason

**I4. Partial window coverage.**
- [ ] Recommended, by case:
  - context ("could") need: feasible with conditions, stating the years covered;
  - must need: feasible with conditions only if another source fills the gap;
  - no overlap at all: not feasible.
- [ ] Any partial coverage → feasible with conditions

**I5. A grain coarser than needed.**
- [ ] Any coarser grain on a must need → not feasible for that need; on other needs → feasible with conditions *(Recommended)*
- [ ] Only two or more steps coarser → not feasible

**I6. Licence or terms in conflict.** Cases: the UCI page says CC BY but its notes say "research use only"; Open-Meteo's free API may be non-commercial; Eurostat has its EEA exception.
- [ ] The most restrictive statement applies until Legal confirms. That means feasible with conditions, with "Legal review" (or the provider's paid plan) as a named condition, and not feasible only if no one can clear it within the project *(Recommended)*
- [ ] Judge by the licence name only

Which flag to use for UCI's research-only clause:
- [ ] GOV-PURPOSE-LIMITATION *(Recommended)*
- [ ] LIC-NONCOMMERCIAL

**I7. Attribution is the only flag.**
- [ ] Feasible, with the attribution text recorded *(Recommended)*
- [ ] Feasible with conditions

**I8. Expired agreement or refused host.**
- [ ] Not feasible, saying what would change it *(Recommended)*

**I9. Only an access request is needed.**
- [ ] Feasible with conditions, naming the owner; never not feasible for access alone *(Recommended)*
- [ ] Not feasible until access is granted

**I10. A written policy forbids the use (the patient-level clinic data).**
- [ ] Not feasible, whatever approvals exist *(Recommended)*
- [ ] Feasible with conditions (approval)

**I11. Changes inside a window** (station VR-03 switched off, traffic counters redefined, the till gap, product codes changed).
- [ ] Feasible with conditions naming the fix; not feasible for that need only if no fix exists *(Recommended)*
- [ ] Not feasible

**I12. Codes that cannot be joined.** UC2 N2: there is no old-to-new product-code mapping, and only products with unique names can be matched.
- [ ] N2 partially met *(Recommended)*
- [ ] N2 unmet

**I13. Missing values coded as numbers (-200).**
- [ ] Feasible with conditions: recode them as missing and report the missing share; never plain feasible *(Recommended)*

**I14. A superseded copy of another source.**
- [ ] Not feasible for the weaker copy, naming the replacement *(Recommended)*

**I15. Geography.**
- [ ] Another country → not feasible. Same country, other city → prototype only. Unknown period or grain → never plain feasible *(Recommended)*

**I16. When a rule flag may be dismissed.**
- [ ] Only when the rule misread a field, quoting that field; otherwise keep the flag and explain *(Recommended)*
- [ ] Whenever the flag does not matter for the verdict

**I17. Changing a flag's severity.**
- [ ] Never; always use the severity in the flag catalogue *(Recommended)*
- [ ] Allowed, with a reason

**I18. The overall verdict when a must need is only partially met.**
- [ ] Count it as "met with conditions" if a named, achievable fix exists; otherwise count it as unmet *(Recommended)*
- [ ] Any partially met must need → overall not feasible

**I19. The "feasible for one need, not another" case for decisions.md.**
- [ ] UCI 360: fine for the prototype window, nothing for production *(Recommended)*
- [ ] Eurostat: fine for N6 (yearly context), useless for N1 (hourly)
- [ ] UC2 sales: the recent window is fine; the history window needs the code mapping

[YOU WRITE after P8: your calibration rationale; which verdicts changed between the before and after runs, and why; the reason for each red flag you dismissed]

---

## J. P9: memo review and sign-off (fill after reading the memos)
Claude gives you an evidence pack for each use case first.

### UC1 sign-off (`outputs/UC1/signoff.json`)
**Verdict:**
- [ ] proceed
- [ ] proceed with conditions
- [ ] stop

**Conditions.** Each needs a text, an owner and a due date; add as many as you need.
- Condition: [YOU WRITE]
- Owner (tick one):
  - [ ] Environment Monitoring Unit
  - [ ] Mobility Office
  - [ ] Clinical Analytics
  - [ ] Data Protection Office
  - [ ] Legal
  - [ ] Procurement
  - [ ] Other: [YOU WRITE]
- Due: [YOU WRITE: YYYY-MM-DD]

**Agreements and overrides** (at least one in total, each with a reason):
- [YOU WRITE: source id + why you agree with the agent]
- [YOU WRITE: source id + what you overrule and why]

**Traced conclusion.** The field must exist and be non-empty in that source's record; Claude checks this after P6.
- [ ] `link.uci_360` → `temporal.end`
- [ ] `link.data_open_air_chicago_hour_aggre_d4970b` → `access.reachable`
- [ ] Other: [YOU WRITE]

What could change this conclusion: [YOU WRITE: at least 20 characters]

### UC2 sign-off (`outputs/UC2/signoff.json`)
**Verdict:**
- [ ] proceed
- [ ] proceed with conditions
- [ ] stop

**Conditions.**
- Condition: [YOU WRITE]
- Owner (tick one):
  - [ ] Retail Operations
  - [ ] Store Operations
  - [ ] Legal
  - [ ] Other: [YOU WRITE]
- Due: [YOU WRITE: YYYY-MM-DD]

**Agreements and overrides:** [YOU WRITE]

**Traced conclusion:**
- [ ] `internal.sales.daily_by_product` → `temporal.start`
- [ ] `api.open_meteo_archive` → `licence.name`
- [ ] Other: [YOU WRITE]

What could change this conclusion: [YOU WRITE]

### Memo reviews (`outputs/artifacts/review_UC1.md`, `review_UC2.md`), all in your words
- [YOU WRITE: where you agree with the agent, and why]
- [YOU WRITE: where you overrule it, and why]
- [YOU WRITE: your verdict on each dataset link]
- [YOU WRITE: your gate decision; for UC1, describe the Chicago refusal as a finding]
- [YOU WRITE: what the agent got wrong or missed. Section 11 of `planning/work.md` lists what to check, including Open-Meteo's terms of use for the gelato shop.]

---

## K. P10: skill Steps 3–5
Claude drafts these from what you actually did.
- [ ] Approve the draft after your edits: [YOU WRITE: your edits]

---

## L. P11: reuse check (UC2, in a fresh session)
**L1. Where to run it.**
- [ ] A separate copy of the repo (a git worktree), so the scored UC2 results are untouched *(Recommended)*
- [ ] This repo (the UC2 review, sign-off and check must then be redone)

**L2. UC2 search suggestions.**
- Per suggestion: accept / reject, with [YOU WRITE: reason]
- [ ] None accepted

**Your answers for the README's reuse-check questions:**
- [YOU WRITE: which steps could not be followed as written, and what was missing]
- [YOU WRITE: which inputs a data scientist would replace for a new project]
- [YOU WRITE: which values were hard-coded for UC1/UC2, and what you changed]

---

## M. P12: README "Submission notes" and the walkthrough
**Delivery reflection.** Pick one bounded activity, for example reviewing the Step 2b shortlist.
- [YOU WRITE: the steps you did yourself, and what the assistant did]
- [YOU WRITE: what you still had to check yourself]
- Review time: not measured (decided). [YOU WRITE: say so, then give the model usage, which Claude totals for you from `run_history.jsonl`]

**Ownership:**
- [YOU WRITE: one source you selected or rejected, and why]
- [YOU WRITE: one rule or agent correction you made, and what it changed]
- [YOU WRITE: one change a new use case would need]

**Walkthrough** (`outputs/artifacts/walkthrough.md`), citing your own files.

One rule:
- [ ] a G4 rule
- [ ] a G5 calibration rule

[YOU WRITE]

One claim in `signoff.json`, traced to its record field: [YOU WRITE]

One rejected source, and why:
- [ ] a Step 2b suggestion you rejected
- [ ] the patient-level clinic table
- [ ] the expired vendor feed

[YOU WRITE]

One memo conclusion: [YOU WRITE]

---

## N. P13: submission
**N1. Gate-failure tests (TC-018)** run in a throwaway copy, so your real results stay clean.
- [ ] Yes *(Recommended)*

**N2. Rubric.**
- Sheet 1: [YOU WRITE: 8 short confirmations, one per row]
- Sheet 2: you mark Pass/Fail after Claude pastes each actual output.

**N3. The `planning/` folder.**
- [ ] Remove it from the submission branch before the PR, and keep a copy on a `planning-archive` branch *(Recommended)*
- [ ] Keep it in the PR, and only leave it out of the zip

**N4. Instructor access to the PR.** [YOU WRITE: the instructor's GitHub username, if the repo is private]

**N5. PR description.**
- [ ] Claude drafts it from the work done, and you edit it *(Recommended)*: [YOU WRITE: your edits]

**N6.** Upload `806637_Subhadeep_Paul_data_discovery.zip` to Tiger Academy (Paradiso). You do this yourself.
