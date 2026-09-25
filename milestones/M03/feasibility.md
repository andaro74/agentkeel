# M03 feasibility note

Milestone M03, claim 3: *The eval gate goes RED on a regression or a
silent plant, and never on a never-passed golden.* SPEC/03 is
`SPEC/03-evals-regression-redteam-corpus.md`. Opened at M03 PR 1,
2026-09-24, through `/open-milestone`.

This note names the commit and inputs that make the claim false (§3), the
code that reads the answer (§4), the falsifiers (§5), and what happened to
every item M02 carried in (`milestones/M03/open.md`, §6).

## 1. `product-spec-reviewer` report (pasted verbatim, 2026-09-24)

Run against SPEC/03 as first drafted, before anything else in PR 1 was
written. SPEC/03 was revised once afterwards, on the rulings in §2; the
report is of the first draft and is not edited to match.

---

product-spec-reviewer: SPEC/03, before M03 PR 1 (draft, uncommitted; base 71eff00, tag m02)

This is a report, not a ruling. Findings are in the order they were checked.

## Your two questions, answered briefly

**(1) The two parts SPEC/03 calls held.**
- **Part 3 (a never-passed golden never turns the gate RED)** does have a false state today, and SPEC/03 does not seed it. The plant rule reads the working tree, not the envelope's commit. PR 2's own `CONTROLS` row will make that false state true, and it will break the guard that §5.2 says must stay green. See B1.
- **The cache case** that SPEC/03 lists as held is not held for refagent. See B2.
- **S1** is a false state for F3.1 as F3.1 is worded ("the regressed golden merges"). It is not a false state of `verdict.gate`. Its reader is the runtime match (`scripts/runtime_for_tree.py` and `deploy.yml`), which is ADR-0007's instrument. See F2.

**(2) The cut list.** The order is defensible, but the list only cuts the light items. The item I expect to break the cap, the knowledge base with retrieval, is on the never-cut list, and its reason for being there is weak. See F9.

## BLOCK

**B1. Check 1/8. §5.2: "Each must stay green through PR 2 and PR 3". §3 item 7: "Held since M00 PR 2."**
- What is wrong: `gate.rule` calls `plants.plant_ids(kinds, ROOT)` (`src/verdict/gate.py:438`), and `plant_ids` checks `(root / CONTROLS[kind]).exists()` against the working tree (`src/verdict/plants.py:54`). The goldens and the cap are read at the envelope's commit; the plant rule is not.
- What happens at PR 2: once `CONTROLS` names `agents/refagent/rules/guardrail.yaml` and that file is in the tree, re-ruling `8033c2a` gives "plants_expected=0, the plant rule gives 3" and "silent plant: expected 3, fired 0". Both reasons come from `g-013` to `g-015`, which have never passed. That is F3.6 happening.
- Consequences:
  - `test_f3_1_guard_…` goes red if it rules through `rule`, because its expected reason list changes.
  - `test_f3_6_guard_…` goes red outright.
  - `make ledger` exits 1: row 2's Measured cell (GREEN) no longer matches `measured_at` (RED). `src/ledger.py:60` re-rules through `gate.rule`.
- So part 3 has a false state that can be planted in PR 1: a strict-xfail test that patches `CONTROLS` and puts `guardrail.yaml` in a copy of the tree beside `8033c2a`.
- What would settle it: Product rules whether this becomes a sixth seed, and whether the guards call `rule` or `judge`. Engineering names the reader.

**B2. Check 1/6/8. §3 item 8: "`build` refuses a reply with `cacheReadInputTokens`. Held since M01 PR 2 for the model call."**
- What is wrong: `agents/refagent/agent.py:146,166` builds `usage` from three keys only (`inputTokens`, `outputTokens`, `totalTokens`), so `cacheReadInputTokens` never reaches the observation. `invoke_deployed` returns that same observation in runtime mode.
- Effect: the refusal at `src/verdict/build.py:455` cannot fire on any refagent run. `cache_state: "disabled"` is a constant (`build.py:507`), not a reading.
- SPEC/00 §8 M03 seeds "a cached answer graded as fresh". SPEC/03 replaces it with S4 on a premise the code contradicts, so a seeded case is cut.
- What would settle it: Product restores a cache seed (a Converse response carrying cache-read tokens through `agent.answer`) or records why not. Engineering names the reader.

**B3. Check 4. §7: "`plants_expected` is 8 … and `plants_fired` is whatever the guardrail blocks".**
- What is wrong: no expected count is stated before the run. The structure also predicts 0 of 8 on PR 2:
  - PR 2 changes `agents/refagent/rules/`, so the bundle digest differs and the run is in the runner.
  - `agent.answer` calls `converse` with no guardrail config.
  - `score_one` passes a guardrail or redteam golden only on `stop_reason == "guardrail_intervened"` (`build.py:150`).
  - Separately, three of the five attacks (override the embargo, ignore the holdback, a pasted amendment) fall under none of SPEC/00 §9's three guardrail rules.
- Effect: a RED on PR 2's own `evals`, which is a required check, stops PR 2 merging. M02 PR 2 hit exactly this (ledger row 2: "PR 2 could not have merged through the ruleset it measures"). "PR 3 repairs the guardrail" then has no merged PR 2 to follow.
- What would settle it: Product, with the Rule Owner, states the expected `plants_fired` before the run, says which commit makes `CONTROLS` live relative to the guardrail being live in the runner, and names the P3 exception.

## FINDING

**F1. Check 1. §3.1: "the next deploy loads the PR's table and the golden fails on the next run, after the merge."**
- What is wrong: `deploy.yml` triggers only on `agents/refagent/**`, `infra/construct/**` and `deploy.yml` (lines 53–56), not on `data/**`.
- Effect: main's run after the merge also matches the runtime, reads the stale table, and is GREEN. The failure shows up on some later PR that changes the bundle. That PR runs in the runner, reads the tree's table, and takes the blame. Also, `load_rights_table.py` never deletes, so a removed row persists in DynamoDB.
- What would settle it: Product corrects the false state. Security names the `deploy.yml` trigger in §6.

**F2. Check 1/2. §1: "seeds the routes by which each part is false **today**". §2: "This is S1 (§5)."**
- What is wrong: S1's reader is `runtime_for_tree`/`deploy.yml`, not `verdict.gate`. What S1 breaks is ADR-0007's promise that a runtime-mode run measured the tree's bytes, which is claim 1's instrument. The claim sentence says "the eval gate goes RED".
- What would settle it: Product rules whether "the eval gate" in claim 3 means the whole `evals` job (then S1 is claim 3's) or `verdict.gate` alone (then S1 is a finding against row 1's instrument, and part 1 has only a guard).

**F3. Check 1/3. The S4 row: "The test puts a `data/corpus/` beside it in a copy of the tree and asks the gate". §6: "`verdict.gate` works it out again at the envelope's commit and requires it from M03 PR 2's merge."**
- What is wrong: `8033c2a` comes before that merge, and at that commit git holds no `data/corpus/`. The reader as specified reads neither the copy nor the date, so S4's test cannot pass when its reader lands.
- What would settle it: Engineering, with Product, picks one: an envelope after the boundary, or a reader that reads the copy.

**F4. Check 1. The S2 row: "The test adds both to the envelope for `8033c2a`, in memory … and the gate says GREEN".**
- What is wrong: adding `g-016` without also changing `kinds` and the envelope's `never_passed` makes `judge` RED today ("the envelope's goldens are not the goldens in the tree", `gate.py:290`). The strict xfail would then pass for the wrong reason.
- Also, `rule` cannot read a copy of the tree, because `ROOT` is fixed.
- What would settle it: Engineering makes the S2 test assert the reason "silent plant", not just the verdict.

**F5. Check 8. SPEC/00 §8 M03: "fingerprint change without a ruling is RED".**
- What is wrong: SPEC/03 §6 recomputes the fingerprint and goes RED on a mismatch, but no build item, falsifier or seed reads "without a ruling".
- What would settle it: Product.

**F6. Check 4. §2: "The Data Owner sets the run length at PR 2."**
- What is wrong: whether S3 is refused depends on a parameter fixed after the plant. A long enough run length lets S3 pass `validate`.
- What would settle it: the Data Owner rules the run length, or its upper bound, in PR 1.

**F7. Check 3/4/7. F3.5: "no refusal recorded at the scan or the ruling step".**
- What is wrong: it is not stated which step is expected to refuse. A guardrail and PII scan has no reason to refuse an unsigned amendment, and nothing checks for a signature.
- The ruling step also has no named path. §6 gives it both "Security: `infra/`" and "Data Owner: the ruling step", so its seat is unclear.
- What would settle it: Product names the expected refusal step. The Data Owner names where the pipeline reads the ruling from.

**F8. Check 3. F3.1: "a merge commit on `main` whose PR envelope is GREEN while the tree it names fails a golden that has passed before".**
- What is wrong: no code reads that repo state. The only in-repo observation would be a later envelope, which depends on a later bundle deploy (F1). `F3_1` is a unit test on a digest plus a guard that passes today.
- What would settle it: Product.

**F9. Check 6. §9: "Never cut: … the knowledge base and refagent's retrieval (without them F3.5's second half cannot be false)".**
- The count:
  - §6 has 11 items that cannot be cut, all in PR 2.
  - Three of them are new AWS surfaces: the Bedrock Guardrail, the ingest stack with two buckets and Object Lock, and the knowledge base.
  - The cut list's five items are the lighter ones.
  - `open.md` rows 1, 2, 3, 4, 5, 8 and 9 are dated "M03 PR 1".
- Why the knowledge base: I expect it to threaten the cap. It is a new deploy (M01's first deploy failed on `kms:CreateGrant`). It changes the tokens of every answer (`open.md` row 7's cap re-rule). It can regress ordinary goldens on PR 2's run.
- F3.5 is an "or": the production-bucket half can be shown false without retrieval.
- What would settle it: Product rules whether the knowledge base and retrieval become cut 6.

**F10. Check 7/8. §6: "Drafted by `red-teamer`."**
- What is wrong: SPEC/00 §5.1 R8 says a specialist is written in PR 1 of the milestone that adds it (M03 adds `red-teamer` and `docs-writer`), and must be exercised on that milestone's seeded case. SPEC/03 does not list either file in PR 1.
- What would settle it: Product.

**F11. Check 8. `open.md` row 4: "the regression bar lands as `delta_max`".**
- What is wrong: this contradicts §1's position that the bar is `judge`'s `regressed`, held since M00, and sits close to R2.
- What would settle it: the Threshold Owner, with Product.

**F12. Check 5. §10.3 row 03: "A test that used to pass and now fails stops the deploy; the attacks we planted must all be caught; a fake contract never reaches the agent."**
- "Stops the deploy": the gate stops a merge. `deploy.yml` does not read `evals`, and S1 is a deploy that carries a regression.
- "Must all be caught" reads as a result.
- "Never" is used about a pipeline that has not fired, and the rights-table route (S1) is a fake contract reaching the agent.
- What would settle it: Product.

## NOTE

**N1. Check 7. §2: "`guardrail` → `agents/refagent/rules/guardrail.yaml`".**
- The plant counts once a yaml file exists, not once a guardrail is attached to the call.
- Guardrail content has two seats: the Rule Owner's yaml and Security's construct resource. SPEC/00 §5 says Security "may not define scope".
- Settled by the Rule Owner and Security.

**N2. Check 8.** The overlap check has three names:
- SPEC/00 §8: "judge/retrieval overlap check"
- CLAUDE.md: "golden/retrieval overlap"
- SPEC/03 §6: "golden/corpus overlap"

`open.md` row 6 records CLAUDE.md's version. Settled by Product.

**N3. Check 8. SPEC/00 §9: "The documents are written in M01 under `data/corpus/`".** SPEC/03 §2 records the cut, but SPEC/00 is not amended. Settled by Product.

**N4. Check 6. §9: "`cost-cap` … is not M03 work."** The cap re-rule for a knowledge base (`open.md` row 7) is not in SPEC/03. Settled by the Threshold Owner.

## Files
- C:\Users\andar\code\agentkeel\SPEC\03-evals-regression-redteam-corpus.md
- C:\Users\andar\code\agentkeel\src\verdict\gate.py (lines 290, 438)
- C:\Users\andar\code\agentkeel\src\verdict\plants.py (line 54)
- C:\Users\andar\code\agentkeel\src\verdict\build.py (lines 150, 455, 507)
- C:\Users\andar\code\agentkeel\agents\refagent\agent.py (lines 146, 166)
- C:\Users\andar\code\agentkeel\.github\workflows\deploy.yml (lines 50–56)
- C:\Users\andar\code\agentkeel\src\ledger.py (line 60)
- C:\Users\andar\code\agentkeel\milestones\M03\open.md (rows 4, 6, 7)

BLOCK: 3 · FINDING: 12 · NOTE: 4

---

## 2. Rulings

Every BLOCK is ruled here, with its seat, before any seed was committed.
SPEC/03 was revised once on these rulings, and that revision is the
first commit of this PR. **Ruled** means the human ruled it on
2026-09-25, before the seeds; **draft** means Product's draft, which the
human rules in `rulings/pr1.md` with the rest of the PR.

### 2.1 The BLOCKs, ruled before any seed

| Item | Seat | Ruling |
|---|---|---|
| B1 the plant rule reads the working tree | Product; Engineering names the reader | **Ruled: a sixth seed, S6** (F3.6). A worktree of HEAD with `guardrail.yaml` in it and `CONTROLS` naming it re-rules `8033c2a` RED on `g-013` to `g-015`; the reader is the plant rule reading the control at the envelope's commit (`git show`, as `thresholds_at`), landing before `CONTROLS` is filled. The two guards call `judge`, not `rule`, so no change to the plant rule changes what they read. |
| B2 the cache refusal cannot fire on refagent | Product; Engineering | **Ruled: not seeded at M03.** SPEC/00 §8's "a cached answer graded as fresh" moves to M04 with the knowledge base (cut 6), whose retrieval is the cache it was written for. SPEC/03 §3 and §8 say `cache_state: disabled` is a constant, not a reading, until then. `agent.py` keeping `cacheReadInputTokens` is Engineering's at M04 PR 1 (§6, row 16 below). |
| B3 no expected plant count; PR 2 cannot merge on a silent plant | Product, with the Rule Owner | **Ruled: 8 of 8, stated before the run** (SPEC/03 §5.1). The Rule Owner widens the guardrail to block all five attacks as well as SPEC/00 §9's three rules. `CONTROLS` names the controls in the commit after the guardrail is attached to the runner's and the runtime's `converse`, never before. Fewer than 8 on PR 2's run leaves PR 2 unable to merge, and that is the finding (P10), not a count to lower. |

### 2.2 The FINDINGs

| Item | Seat | Ruling |
|---|---|---|
| F1 `deploy.yml` does not run on `data/**` | Product (the false state); Security (the trigger) | **Draft.** §3.1 corrected: `main`'s own run after the merge is GREEN too, and a later bundle PR takes the blame. `deploy.yml` runs on `data/rights_table.json` and `load_rights_table.py` deletes rows the file lacks, both in S1's reader at PR 2 (SPEC/03 §6). |
| F2 "the eval gate" | Product | **Ruled: the whole `evals` job.** S1 is claim 3's seed for F3.1. |
| F3 S4's reader cannot read the copy | Engineering, with Product | **Draft.** The gate's reading of the fingerprint is a function of the tree at a commit; `judge` takes the gate's own reading as an argument and `rule` computes it at the envelope's commit. S4's test passes the reading of a copy of the tree. |
| F4 S2 would pass for the wrong reason | Engineering | **Draft.** S2's test sets `kinds` and `never_passed` to match, computes plant ids from a copy of the tree, calls `judge`, and asserts the reason `silent plant`, not only RED. Every seed test asserts its planted reason (SPEC/03 §5). |
| F5 "fingerprint change without a ruling" | Product | **Draft.** Held by `ruling-cited` on `data/**` since M02: the fingerprint is read from `data/corpus/admitted.yaml`, which changes only with a Data Owner ruling. SPEC/03 §2 says so. No seed. |
| F6 overlap run length set after the plant | Data Owner | **Draft for the Data Owner: 12 words**, an upper bound fixed now. S3 carries `g-010`'s whole question, 38 words. PR 2 may lower it, never raise it past 12 without a ruling that re-reads S3. |
| F7 which step refuses the amendment | Product; Data Owner | **Draft.** The expected refusal is **no admission**: promotion to the production bucket happens only for an object that `data/corpus/admitted.yaml` on `main` names by sha256 with its ruling. The scan runs and is recorded; it is not expected to refuse. Seats: the file is the Data Owner's, the pipeline that reads it Security's. |
| F8 no code reads F3.1's merge on `main` | Product | **Draft.** Said plainly in SPEC/03 §4: `F3_1`, `F3_3` and `F3_6` are test-only witnesses of a seed refused in a copy of the tree, as M02 PR 2's first source of `F2_1` was. No seed PR is opened. |
| F9 the knowledge base on the never-cut list | Product | **Ruled: cut 6, taken at open, to M04.** F3.5 is read on its production-bucket half; "or changes an answer" is not measured at M03, and SPEC/03 §4 and §8 say so. |
| F10 `red-teamer` and `docs-writer` not in PR 1 | Product | **Draft.** Both are written in this PR (R8), with their CODEOWNERS lines (Security). `red-teamer` is exercised on S2: it drafts the five attacks and `redteam.yaml` as a report for PR 2. `docs-writer` is exercised on the explainer draft. |
| F11 `delta_max` against R2 | Threshold Owner, with Product | **Draft.** At M03 the regression bar is P7 as `judge` holds it; `delta_max` is SPEC/00 §8 M04's relative policy. `open.md` row 4's other half, `bars` reading one level deep, is PR 2's (§6). |
| F12 the plain sentence | Product | **Draft.** SPEC/00 §10.3 row 03 amended inline in this PR: "A test that used to pass and now fails stops the change from merging; every attack we planted must be caught, or the change stops; a contract nobody signed never reaches the agent's documents." |

### 2.3 The NOTEs

| Item | Seat | Ruling |
|---|---|---|
| N1 a yaml file is not a guardrail on the call | Rule Owner, Security | Answered by B3's ruling: `CONTROLS` lands after the guardrail is on the call. The Rule Owner writes what it blocks; Security builds the resource from that file and does not decide its scope. |
| N2 three names for one check | Product | One name, **golden/corpus overlap**, in SPEC/03. CLAUDE.md's line is corrected with the check at PR 2 (row 6). |
| N3 SPEC/00 §9 still says M01 | Product | SPEC/00 §9 amended inline in this PR: the documents land at M03 PR 2; the knowledge base is M04. |
| N4 the cap re-rule | Threshold Owner | Row 7, at PR 2, against PR 2's measured spend: five goldens more per run, no retrieval. |

### 2.4 The seat reports on this PR (in the PR body verbatim)

`threshold-owner` on row 1 (0 BLOCK, 5 FINDING, 4 NOTE): proposed the six
entries ADR-0009 carries. `red-teamer`, its first exercise, on S2 (0
BLOCK, 4 FINDING, 3 NOTE): drafts `g-016` to `g-020` and the two rule
files for PR 2, keeps S2's `g-016` word for word, and finds that `g-014`
(MASKED) may not be passable at M03 with no license text to read (Unsure
A; ruled in §2.5). `docs-writer`, its first exercise: the explainer
draft. Both were run through a general-purpose agent handed the prompt
file, since the two were not yet registered as agent types in the
session that wrote them.

### 2.5 Ruled after the seat reports on the diff

The cold review and the three seat reports read the diff `71eff00...faed466`
(1 BLOCK, 25 FINDING, 20 NOTE among them; all four in the PR body
verbatim). The human ruled four items on 2026-09-25 before the PR
opened; each repair is its own commit after the diff the reviewers read.

| Item | Seat | Ruling |
|---|---|---|
| `security-reviewer` BLOCK 1: `ruling-cited` reads CODEOWNERS from the base, where no line owns the two new prompts, so no ruling could cover them | Product; Security, Engineering | **Ruled: the gate reads a prompt's own `seat:`** (`10452f9`), from the base when the file is there and from the PR when it is new, as it already did for ruling files (SPEC/00 §5, last row). Two tests fail without it. This PR changes the gate that judges it; the ruling files say so. |
| cold review F1: history is read whole, so a later pass of a never-passed golden re-rules an older envelope RED | Product; Engineering names the reader | **Ruled: a seventh seed, S7** (`1e51666`), before any reader. Reader at PR 2: history limited to the envelope's ancestors. Verified by the call before the ruling: one later pass of `g-013` turns row 2 RED, `regressed: g-013`. |
| `g-014` (MASKED) cannot fire at M03: `rule-owner` F2, `data-owner` F5, `red-teamer` | Product, with the Rule Owner and the Data Owner | **Ruled: 7 of 7, `g-014` not counted at M03** (SPEC/03 §5.1, `4d04332`). Not edited, not retired; each control names its plants by id, so the plant rule leaves `g-014` out until the knowledge base at M04. B3's ruling stands as amended: the count is stated before the run. |
| ADR-0009, the additions the reports proposed | Product | **Ruled: entry 5 only** (`ce8f9e7`), a rule dropped from a control file or its action weakened (`rule-owner` F5). **Not added**, and so still one key: a boundary deny narrowed (`security-reviewer` F1), an Object Lock retention or mode weakened (F4), the overlap bound raised (`data-owner` F2), a rights-table row deleted (NOTE 5). Each is recorded in `rulings/pr1.md` with the seat that holds it. |

The test repairs from the cold review (F2 and N3: `raises=` on each
marker, `exist_ok` on two `mkdir` calls, S1 digesting a clean worktree
of HEAD) are `c3f8c81`. No seed file was edited: S1's two non-UTF-8
bytes (cold F5, `data-owner` N13) and S3's path, which the real holdback
schedule must not take (`data-owner` F4), stand as planted, and
`rulings/pr1.md` says what PR 2 does about each.

## 3. The false state

SPEC/03 §3, in full. Live today: a regression through the rights table,
measured in the runtime against `main`'s table (S1); a silent plant with
its control in the tree (S2); a golden that overlaps the corpus (S3); an
envelope with no fingerprint (S4); the unsigned amendment reaching the
production bucket (S5); a control added today re-ruling an older
envelope RED on goldens that never passed (S6). Held today: a regressed
golden, measured, merging; a never-passed golden with no control
involved turning the gate RED; a cache state outside the enum. Not held
and not seeded: a cached answer graded as fresh (B2; M04).

The commits: `61ac95a` S1, `c5f5ca3` S2, `01876a7` S3, `2fd7128` S4,
`149d352` S5, `d229601` S6, the guards `92c7b2a`, and `1e51666` S7 after
the cold review, before any reader. `git show <seed>
--stat` shows a fixture, a test and the fixtures README, and no reader.
Each strict marker was checked with `--runxfail` to fail for its planted
reason: S1 the same digest with and without the patch; S2 the plant rule
giving `[]`; S3 no `src.validate.overlap`, after today's checks pass on
the patch; S4 no `gate.corpus_fingerprint`; S5 `observed` null; S6
"silent plant: expected 3, fired 0" on row 2's envelope, which the same
call rules GREEN with no control in the tree. S7 "regressed: g-013 has
passed before and fails now" against a copy of history holding one later
pass.

## 4. The code that reads the answer

SPEC/03 §6, all PR 2, in the order the commits are to land: the plant
rule at the envelope's commit (S6); the red-team goldens and
`redteam.yaml`; the guardrail on the call; `CONTROLS` filled after it
(S2); the runtime match covering the table, `deploy.yml` on
`data/rights_table.json`, `load_rights_table.py` deleting (S1);
`validate`'s golden/corpus overlap (S3); the corpus and `admitted.yaml`;
the ingest pipeline, deployed by the human after `cdk diff`; the
fingerprint in `build` and `gate` (S4); `scripts/observe_ingest.py`
(S5); `CLAIM_3_CHECKS`. None of it is in this PR.

## 5. Falsifiers, and what each would look like in the repo

SPEC/03 §4. `F3_1`, `F3_3` and `F3_6` are test-only witnesses of a seed
refused in a copy of the tree. `F3_2` is read on the run's own results.
`F3_4` is read by the gate from the envelope and the tree. `F3_5` is read
from AWS by the observer. F3.5's second half is not measured at M03.

## 6. What M02 carried in (`milestones/M03/open.md`), row by row

Every row is answered here or moved on with a seat and a date. None is
dropped. Rows 1, 2, 9 and 11 were the four the human named for this PR,
in that order; rows 3, 4, 5 and 8 are readers or bars and are PR 2's.

| # | Seat | Now |
|---|---|---|
| 1 | Product, with the Threshold Owner | **Done here, for ruling**: ADR-0009 (`8ac5682`), from the `threshold-owner` proposal, six entries; SPEC/02 §2 and SPEC/00 §5 amended inline. Status Proposed until Product rules each entry in `rulings/pr1.md`. The readers (`two_key.py`, `ruling_cited.py`, `validate`) are Engineering's at M03 PR 2, before any commit that moves a bar. |
| 2 | Product (the bullet); Security (the case) | **Done here** for the bullet: SPEC/01 §9, "observed once, unplanned", run 35817173042 (`a695ae9`). The seeded case: Security, **M05 open**. |
| 3 | Engineering | **PR 2**: they are readers. `build.check_from_bypass` reads `ci_red_lines`; `gate.rule` prints `where`; `lines_naming` strips before it removes the timestamp; `judge`'s default of claim 1 only, which `CLAIM_3_CHECKS` makes worse if left. |
| 4 | Threshold Owner, Engineering | **PR 2** for `bars` reading one level deep. `delta_max`: **M04** (ruling on F11; SPEC/03 §10). R10's N as `up`: PR 2, with its `relaxes:` entry. |
| 5 | Data Owner, Tool Owner, Engineering | **PR 2**: how an absence trap cites and how scoring compares the cited row. `g-021` stays never passed (SPEC/03 §10) unless those rulings say otherwise. |
| 6 | Product | **PR 2**, with the overlap check: CLAUDE.md's line is corrected in the commit that lands `validate`'s golden/corpus overlap (note N2). |
| 7 | Threshold Owner | **PR 2**, against PR 2's measured spend: five goldens more per run, no retrieval (cut 6). The control answering the retired `g-012` every run: the same ruling. |
| 8 | Security | **PR 2**: `read_back_grants.py` gains the two DynamoDB probes (Engineering); the human runs it once with admin and the rows go in `infra/bootstrap/README.md`. |
| 9 | Product | **Done here**: the M02 video (`47d53c6`, 5:48, 6.0 MB, tag `m02`, LFS) and its row, which says it is 48 seconds over. The ruling on whether the ceiling or the recordings stand is in `rulings/pr1.md`, a draft for the human. |
| 10 | Product, Security (the human) | Seed PRs 14 to 18: **closed unmerged, branches kept** (the human, 2026-09-24). The two `doors:` blocks in `f2_2_three_doors.yaml` and the image `822fe2b5` in ECR: not known to this session; **Unsure B**. |
| 11 | Engineering | **Done here**: checked item by item against the code, `pr2-engineering.md` and `pr2-cold-review.md`. Neither ruling claims any item. **0 of 11 done**, 2 partly (e, f). Re-dated below. |
| 12 | Threshold Owner | **M04 PR 1**, as dated. |
| 13 | Tool Owner | **M06; M07**, as dated. |
| 14 | Security | **M05 open**, as dated. |
| 15 | Product, Engineering | **Done here**: row 2 read from the envelope `8033c2a`, and `make ledger` exits 0 against it. `12b4646`, `47258f2` and `6daf6c4` each rule RED ("checks.F2_2 is missing from an agent envelope"), read by the gate on 2026-09-25; no Measured cell cites them. From M03 PR 2's merge every agent envelope also carries claim 3's checks or is RED. |
| (B2) | Engineering | New: `agents/refagent/agent.py` keeps `cacheReadInputTokens`, so `build`'s prompt-cache refusal can fire: **M04 PR 1**, with the knowledge base and the cached-answer seed. |

**Row 11, item by item** (M02 open.md rows 12 and 13; file:line at
`71eff00`):

| Item | State | Evidence | Re-dated to |
|---|---|---|---|
| a. the CloudTrail check reads the refusing `principal` | not done | written at `scripts/observe_attempt.py:69`, never read by `build.py:293-306` | M05 open (Security, Engineering): evidence integrity |
| b. agent raw replayable | not done | only the control's raw is committed (`evals.yml:482,487`); the agent's is an artifact | M05 open |
| c. `both()` keeps F1.1's two halves apart | not done | `build.py:309-315` ANDs them and keeps the first URL | M05 open |
| d. `message_must_contain` required | not done | `build.py:305-306` falls back to any AccessDenied | M05 open |
| e. `thresholds_at` falls back to the tree | partly | fallback at `gate.py:124-125`; where it read is printed at `gate.py:513-515` | M03 PR 2, with S6's reader: the same reading at a commit |
| f. `server.py` profile and docstring | partly | env-var test `tests/test_construct.py:191`; default still `server.py:30`; docstring still wrong, `server.py:11` against `:47` and `agent.py:65` | M04 PR 1, with the model fields |
| g. `run.py`'s dirty check excludes the goldens | not done | `src/agent/run.py:68`, `:(exclude)evals` | M03 PR 2, when five goldens land |
| h. the gate takes build's token sums as given | not done | `gate.py:340` | M04 PR 1 |
| i. Makefile paths that write no envelope | not done | `Makefile:15` still says a run always writes one; `cost_cap.py:53-58` | M04 PR 1 |
| j. `gate.manifest_at` falls back to the tree | not done | `gate.py:146-147` | M03 PR 2, with e |
| k. IAM5 rows under one reason | not done | now four rows, `infra/construct/AwsSolutions--AgentkeelRefagent-NagReport.csv:7-10`, one reason | M05 open (Security) |

## 7. What PR 1 does not do

- It builds no reader: `CONTROLS` stays `{}`; no overlap check; the
  runtime match still reads the bundle alone; no fingerprint; no
  pipeline; no observer. The strict markers say so.
- It adds no golden and no rule: `g-016` to `g-020`, `redteam.yaml` and
  `guardrail.yaml` are PR 2's, drafted by `red-teamer` in the PR body.
- It moves no bar: `thresholds.yaml` is untouched.
- It touches no AWS and deploys nothing. The ingest stack is PR 2's, and
  the human reads `cdk diff` and deploys it.
- It does not change the ruleset.
