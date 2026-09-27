# M04 feasibility note

Written at M04 PR 1 through `/open-milestone`. SPEC/04 was drafted first
and `product-spec-reviewer` run on it before anything else in the PR was
written. §1 is its report, verbatim. §2 is the rulings on it.

## 1. `product-spec-reviewer` on SPEC/04 (draft), verbatim

A report, never a ruling.

product-spec-reviewer: SPEC/04-model-swap.md (DRAFT), M04, before PR 1

Files read: SPEC/04; SPEC/00 §3–§10.3, §14; SPEC/03 §8–§10; milestones/M04/open.md; milestones/README.md rows 3 and 4; milestones/M03/rulings/pr4.md; agents/refagent/manifest.yaml; infra/bootstrap/app.py (MODELS); src/verdict/build.py score_one; src/verdict/gate.py; agents/refagent/agent.py:218-245 (to confirm `tool_calls` exists); ADR-0007; ADR-0009. I also grepped the `mode`, `p95_ms` and `tokens_*` fields in evals/history/ because §2 cites those envelopes.

Check 1 (false state): every one of S1 to S5 can be planted in PR 1 without building its reader. S1 works because `score_one` has no `tool_calls` read (build.py:157-193), while agent.py:243 records the calls. S2 works because MODELS is two ids (app.py:103). This check finds no BLOCK.

---

**BLOCK 1. F4_2 cannot pass where the spec needs it to pass. The equivalent swap cannot be read as promoted.**
- §4: "`F4_1` and `F4_2` have two sources each ... the check passes only when both do." Also: "From PR 2's merge commit the gate requires `F4_1` to `F4_4` on every agent envelope."
- §5.1: "`cold-review-ruling` on a swap PR is green only once its ruling is on `main`, which is PR 2's merge."
- What is wrong: F4_2's second source cannot be green on PR 2's own run. On the equivalent swap PR's own run, observe_pr would look up that same PR, whose `evals` check is still running. So F4_2 fails, the envelope is RED, and the PR can never be all-green.
  - The "if" in §5.1 ("If the equivalent swap's required checks cannot all be read green before PR 2's last run") is in fact a certainty.
  - PR 2 then carries F4_2: fail and cannot merge through `evals`. Row 2 records this same trap at M02, which needed an amendment at PR 2.
- What would settle it: Product rules, before the ledger row states "equivalent GREEN", what `build` writes for F4_1 and F4_2 in two cases: on PR 2's run, and on a swap PR's run when it would read itself (for example, first source only, as M02 did).

**FINDING 2. "Breaking RED" is met by any RED.**
- §5.1: "Stated before the runs: **breaking RED, equivalent GREEN, A-vs-A zero diff.**"
- §7: "if the breaking swap is GREEN".
- What is wrong: the Llama PR would also go RED from BLOCK 1's self-lookup, from an IAM refusal if the redeploy misses it, from REJECTED, or from cost-cap. None of those shows a tool-format break.
- What would settle it: the expected output names the reason, for example "N citing goldens regressed, ungrounded". The Threshold Owner rules it.

**FINDING 3. The p95 and token bars have no defined incumbent and no stated value.**
- §6: "as ratios of the incumbent's median over its envelopes in history. The value is the Threshold Owner's".
- What is wrong, in three parts:
  - At a swap PR's commit the pin is the candidate (T3). The spec does not say how the gate finds "the incumbent". If it means envelopes on the pin at the commit, the candidate has no history and the bar reads nothing.
  - Of the 13 envelopes that carry `mode`, 8 are `runner` and 5 are `runtime`. §2's "eleven" does not say which ones. The swap PRs run as `runner`.
  - No ratio is stated before the run. S4 at 3× only fires under a bar that sits between about 1.6× and about 2.8×.
- What would settle it: the Threshold Owner states three things in PR 1:
  - the ratios;
  - "incumbent = the pin at `main`'s merge-base";
  - which modes count.

**FINDING 4. Tool grounding changes what "pass" means on the incumbent, and no expected output covers that.**
- §6: "a citing answer's `score` requires a successful `check_availability` call whose `row` is the answer's `table_row`".
- What is wrong: if any of the incumbent's current passes (ordinary 9/9, traps 2/3 at `cb06c0d`) is not grounded, PR 2's own run shows that golden as `regressed` and goes RED.
  - §7 states no count for refagent after grounding.
  - The `row` returned by the tool is a record, and the spec does not say which of its keys is compared.
- What would settle it: §7 states the expected ordinary and trap counts under grounding. The Data Owner rules it.

**FINDING 5. F4.3's diff cannot be read from the repo.**
- §6: "The envelope carries the first run's results." §4, F4.3: "any golden's `pass` different".
- What is wrong: `checks` holds pass/fail and a URL, and the schema is `additionalProperties: false`. The second raw run is a CI artifact that is not committed (open.md row 34, item b). So the goldens that differed are not in the repo once the artifact expires.
- What would settle it: Engineering names the envelope field (a schema change) or the committed file that holds the differing ids.

**FINDING 6. A-vs-A ignores SPEC/00's own seed for it.**
- SPEC/00 §8 M00: "Finding F0.4 ... the control is non-deterministic at temperature 0 ... the seed for SPEC/04's A-vs-A design". Also: "it becomes the A-vs-A control at M04".
- What is wrong, in two parts:
  - SPEC/04 never cites F0.4. It does not say whether the control runs A-vs-A, or why refagent should give zero diff when the control does not.
  - After the close, F4_3 is required on every envelope and FRAGILE is cut to M06 (cut d). So one flake RED-blocks every PR in M05.
- What would settle it: Product states the control's role in A-vs-A and what a flake after the close does.

**FINDING 7. A SPEC/00 build item is dropped without a cut.**
- SPEC/00 §8 M04: "`deprecated_after` set from Bedrock".
- SPEC/04 §8: "the Threshold Owner re-reads `modelLifecycle` on every swap PR and records it".
- What is wrong: nothing reads Bedrock, and the item is not in §9. S5's reader compares only a date the patch author typed. A Sonnet 4 pin with `deprecated_after: null` passes `validate`.
- What would settle it: Product adds the item to §9 with its milestone (M07), or builds it.

**FINDING 8. SPEC/04 contradicts SPEC/00 §9 on the knowledge base. SPEC/00 wins.**
- SPEC/00 §9: "The Bedrock Knowledge Base, and refagent retrieving from it, are M04 (SPEC/03 cut 6, taken at open)."
- SPEC/04 §9 cut f moves it to M06.
- What is wrong, in two parts:
  - PR 1 must carry a SPEC/00 §9 amendment, and the spec does not plan one.
  - The judge (M03→M04→M07) and FRAGILE (M03→M04→M06) are on their second move too. The §8 build lists for M06 and M07 do not name what they are receiving.
- What would settle it: a SPEC/00 amendment in PR 1. Product.

**FINDING 9. CLAUDE.md disagrees with ruling (3).**
- CLAUDE.md seat table: "`thresholds.yaml`, judge rubric, judge model id, agent model id + version + region | Threshold Owner | `two-key` on any downward move".
- SPEC/04 §10: "A model id change is not on ADR-0009's list".
- What is wrong: SPEC/00 §5 and ADR-0009 support SPEC/04. CLAUDE.md still reads as two keys for a downward model move, and Sonnet 4.6 → 4.5 is arguably one.
- What would settle it: a CLAUDE.md PR. Product.

**FINDING 10. `deprecated_after` has two seats.**
- §6: "`deprecated_after` (`src/validate/`, Engineering; the manifest field, Threshold Owner)".
- What is wrong: SPEC/00 §5 gives the Threshold Owner only "agent model id + version + region". Every other manifest field defaults to Engineering (ADR-0003 amendment 1). `profile` has no named seat either.
- What would settle it: Product rules the seat. ADR-0003 already has two amendments, so this needs a new ADR.

**FINDING 11. The open.md inbox is not fully disposed, and one reference is broken.**
- §8: "M04 inbox row 40". open.md has 38 rows.
- Rows dated "at M04 open" that SPEC/04 does not place: 1, 2, 4, 20, 21, 23 and 38.
- Row 38 bears on this spec's seed practice (§5 xfail markers): "A test that switches each reader off and asserts the planted reason".
- What would settle it: Product places each row, and fixes the row number in §8.

**FINDING 12. The plain sentence overclaims.**
- SPEC/00 §10.3: "Changing the model is safe or it's blocked | A new model version is tried in the shadows first; if it breaks anything, the PR stays red."
- What is wrong, word by word:
  - "in the shadows" describes model-watch's shadow run, which is cut to M07 (cut a).
  - "new model version": the equivalent candidate is older than the incumbent (§1).
  - "anything": only goldens, p95 and tokens are read, and §8 lists a guardrail-less call as unread.
  - "PR" needs GitHub to be understood.
  - "safe" in the title is used about a control that has not fired.
- What would settle it: Product amends SPEC/00 §10.3 row 04 at open.

**FINDING 13. The cap has nothing left to cut.**
- §9: "None cuts a seed, a seed's reader, A-vs-A, the two swap PRs or the bootstrap candidate list."
- PR 2 carries 11 build items:
  - grounding, with the g-021 ruling;
  - A-vs-A (Security and Engineering);
  - two bars and the gate's reading of them;
  - the `deprecated_after` check;
  - the bootstrap list, the human deploy and `cdk diff`;
  - `pinned_roles`;
  - observe_pr and `f4_swaps.yaml`;
  - `CLAIM_4_CHECKS` and the flags;
  - the `test_p5_disagree` cases;
  - the cap re-rule;
  - the two swap PRs and their rulings.
- What is wrong: the remaining cuts (1: Haiku's run; 2: rows 11 and 22) save almost nothing.
- Expected threat: F4_2's second source is necessarily read at PR 3 (BLOCK 1). If the cold review of PR 2 finds anything, PR 3 is also the repair. One failed read after that is a fifth PR.
- What would settle it: Product records that PR 3 is both the F4_2 read and the repair, and what closes RED if either misses.

**NOTE 14.** §2: "Incumbent ... `us.anthropic.claude-sonnet-4-6`". That is the profile. The manifest `id` is `anthropic.claude-sonnet-4-6`.

**NOTE 15.** §5.1: "Security adds the three candidates to the models the eval role may invoke and to nothing else."
- MODELS also feeds the deploy role's `CopyFromThePinnedProfilesOnly` (app.py:548-550). §6's "a list the eval role alone may invoke" must be a new list, not MODELS.
- If cut 1 is taken, the spec does not say whether Haiku stays on that list. Security.

**NOTE 16.** §6: "The cap is re-ruled against the doubled spend". A raise under `relaxes: up` counts as two keys (ADR-0009 Consequences).
- The spec does not say whether `tokens_in` counts both runs.
- At `cb06c0d` the agent's side was 47,034 in and 5,097 out, against a cap of 150,000. Threshold Owner.

**NOTE 17.** §1, §2 and §10 cite six rulings as "the human as ..., 2026-09-26" with no file.
- SPEC/00 §8 M04 "One policy, not both" is changed by ruling (2) under its "unless a ruling changes it" clause.
- `milestones/M04/rulings/pr1.md` should carry each of the six with its seat. Product.

BLOCK: 1 · FINDING: 12 · NOTE: 4

## 2. Rulings on the report

Ruled by the human, 2026-09-26, "as proposed", before any seed. SPEC/04
was revised once on them. Each is carried in `rulings/pr1.md` with its
seat.

**Before the draft** (the six the report's note 17 asks to be filed):

1. "Promotes" means the equivalent swap PR is mergeable with every
   required check green, not merged. Product, Threshold Owner.
2. `delta_max` applies to p95 and the agent's tokens, not to goldens;
   P7 stands. Threshold Owner.
3. A model id change is not on ADR-0009's list of relaxations.
   Threshold Owner.
4. The knowledge base goes to M06. Product.
5. S5's plant is Sonnet 4 with Bedrock's `endOfLifeTime`, 2026-10-14.
   Threshold Owner.
6. `model-watch`, the judge and Braintrust go to M07. Product.

**On the report:**

| # | Ruling | Seat | Where |
|---|---|---|---|
| B1 | M02's pattern. From PR 2's merge, `F4_1` and `F4_2` on every agent envelope come from the seed tests alone (test-only witnesses, and the ledger says so). The swap PRs are opened during PR 2 from its head, their rulings ride in PR 2, their checks re-run after PR 2 merges, and PR 3's run reads them (named P3 exception). A swap PR's run never reads itself. PR 3 is both this read and the repair; if either misses, row 4 closes RED at PR 4 | Product | SPEC/04 §4, §5.1 |
| F2 | The breaking swap's RED must come with at least one citing golden regressed, ungrounded or with wrong fields, and no REJECTED, access errors or cost cap. Any other RED is a finding | Threshold Owner | SPEC/04 §7 |
| F3 | Incumbent = the pin at the merge-base with `main`; the bar reads the median over envelopes on that pin in the same `mode`; p95 ≤ 2.0×, agent tokens ≤ 1.5×. S4 plants 3× latency and 2× tokens | Threshold Owner | SPEC/04 §2, §5, §6 |
| F4 | Tool-grounded: a successful call whose `row.table_row` is the answer's `table_row` and whose `clause_candidates` include its `clause_id`. Expected at PR 2: ordinary 9/9, traps 2/3; fewer is a finding. `g-021` ruled with the reader | Data Owner; Tool Owner for `g-021` | SPEC/04 §2, §7 |
| F5 | An optional envelope field `a_vs_a` with the ids that differ, for the agent and the control | Engineering | SPEC/04 §6 |
| F6 | F0.4 cited. The control runs A-vs-A, reported, not gated. A-vs-A runs on PR 2's own run and when the pin differs from the incumbent; `F4_3` is required on those envelopes only | Product | SPEC/04 §1, §4 |
| F7 | "`deprecated_after` set from Bedrock" cut to M07 (cut g) | Product | SPEC/04 §9 |
| F8 | SPEC/00 amended in this PR: §9 (knowledge base to M06), the M06 and M07 build lists, and rows 1 and 23 of `open.md` | Product | SPEC/00 §3, §8, §9, §10.3 |
| F9 | CLAUDE.md's seat table: a model id change is measured, not two-keyed | Product | CLAUDE.md |
| F10 | ADR-0010: `profile` and `deprecated_after` are the Threshold Owner's | Product (authorises Threshold Owner) | `docs/adr/ADR-0010-*` |
| F11 | Every `open.md` row placed in §6; "row 40" is new item 40 | Product | §6; SPEC/04 §8 |
| F12 | SPEC/00 §10.3 row 04 amended: "Changing the model is tested, or it's blocked"; "When a team switches the agent to a different model, the switch is tested on its own proposal before it can go in; if a test that used to pass now fails, or answers get much slower, it can't go in." | Product | SPEC/00 §10.3 |
| F13 | Recorded: PR 3 is the swap read and the repair; no fifth PR | Product | SPEC/04 §5.1 |
| N14 | The incumbent's `id` corrected | Product | SPEC/04 §2 |
| N15 | A new eval-role-only list; `MODELS` unchanged; Haiku stays on the list | Security | SPEC/04 §5.1 |
| N16 | The cap raise is two keys; `tokens_*` count every run the job made | Threshold Owner | SPEC/04 §6 |
| N17 | The six rulings above go in `rulings/pr1.md` | Product | `rulings/pr1.md` |

### 2.4 The seat reports on this PR (in the PR body verbatim)

`threshold-owner` (0 BLOCK, 8 FINDING, 11 NOTE), `data-owner` (0, 7, 10)
and `rule-owner` (0, 5, 6), on the branch at `74fb9ed`. None had a shell;
the two diffs they asked for are pasted under their reports in the PR
body. Ruled by the human, 2026-09-27, "as proposed". No specialist is
added at M04 (R8), and none is exercised: `red-teamer` has no M04 seed.

| Finding | Ruling | Seat | Where |
|---|---|---|---|
| threshold F1 to F3 | The bars read the first refagent run: its p95 and its agent-side tokens. Envelopes with no `mode` are not counted. No incumbent envelope in the mode means `F4_4: fail`, RED | Threshold Owner | SPEC/04 §2 |
| threshold F4 | The bars apply to every agent envelope; the mapping is `relative.*` | Threshold Owner | SPEC/04 §2, §6 |
| threshold F5 | `cost_cap` is a budget; "one policy" is about quality bars | Product | SPEC/04 §2; SPEC/00 §8 M04 |
| threshold F6 | ADR-0009 amendment 1, entry 6: `deprecated_after` moved later, nulled or removed is a relaxation; SPEC/02 §2 amended inline | Product (Threshold Owner proposes) | ADR-0009; SPEC/02 §2 |
| threshold F7 | Separate ruling files, one seat each | Product | `rulings/pr1*.md` |
| threshold F8 | `version` records a versioned id's suffix; null only when it has none. Swap PRs follow it; seed patches stay | Threshold Owner | SPEC/04 §2 |
| threshold notes 10, 14, 17 | The p95 clause compares the worst run with the median; lifecycle read in us-west-2 only; CLAUDE.md "in its `relaxes:` direction" | Product | SPEC/04 §2; `runs/model_access_2026-09-26.md`; CLAUDE.md |
| threshold notes 13, 18 | The manifest's judge comment; the incumbent matched on profile and region | Threshold Owner; Engineering | PR 2 |
| data F3, F4, F16 | `g-021` cannot pass grounded as written; row 5 says so | Data Owner, Tool Owner | §6 row 5; PR 2 |
| data F5 | Grounding does not check the call's input against the question; ruled with `g-021` at PR 2 | Data Owner, Tool Owner | SPEC/04 §2 |
| data F7 | The 9/9 and 2/3 counts were never grounded; PR 2's run is their first measurement | Data Owner | SPEC/04 §7 |
| data F9 | S3's and S4's tool calls made on the real tool; `g-021` gets `found: false` (`2dc81ae`, before any reader) | Engineering | `tests/fixtures/m04/` |
| data F11 | SPEC/00 §9: CORRECT includes grounding from PR 2 | Product | SPEC/00 §9 |
| data note 14 | Row 3 is M06 `open.md`'s first row | Data Owner | §6 row 3 |
| rule F3 | Row 2's text as the Rule Owner proposed | Product | §6 row 2 |
| rule F4; data note 2 | `guardrail.yaml`'s stale comments carried by the Rule Owner's next `rules/**` change | Rule Owner | §6 row 17 |
| rule F5, F6; notes 11 | The probe record says what the files show, names the version each round sent or says the files do not record it, and marks inferences | Product | `runs/llm_gateway_probe.md` |
| rule F7 | SPEC/04 §8: a swap's plants fire before the candidate is called | Product | SPEC/04 §8 |
| rule note 2 | `red-teamer` reads the lowest-numbered OPEN row of `milestones/README.md` | Rule Owner | `.claude/agents/red-teamer.md` |

### 2.5 The cold review and the second read, on the diff

`engineering-cold-reviewer` (0 BLOCK, 5 FINDING, 4 NOTE) and the seat
re-reads, each on the diff `2addb95...688634c` and each saying so in its
first line: `threshold-owner` (0, 5, 12), `data-owner` (0, 3, 4),
`rule-owner` (0, 3, 8). All in the PR body verbatim. Ruled by the human,
2026-09-27, "as proposed".

| Finding | Ruling | Seat | Where |
|---|---|---|---|
| cold F1; threshold F2; data F2; rule note 10 | The ruling files, one seat each, `pr: 23` | each seat | `rulings/pr1*.md` |
| cold F3; data F3 | Seed preconditions raise `SeedBroken`; only the planted line is an `assert` (`e0ce2ce`) | Engineering | `tests/test_m04_seeds.py` |
| cold F4 | S3 ruled against the incumbent history: its first run alone GREEN, its second alone RED for `g-006` regressed only (`e0ce2ce`) | Engineering | S3 |
| data F1 | `the_call` takes the date the question asks about; S3 and S4 regenerated (`e0ce2ce`) | Engineering (Data Owner rules the call) | S3, S4 |
| cold F2 | The seeded-commit cell names the fixture commits beside S3 and S4 | Product | ledger row 4; README; §3 |
| threshold F1 | `build` writes the first agent run's tokens as their own optional field; the bar reads it | Threshold Owner | SPEC/04 §2 |
| threshold F4 | Entry 6 compares dates only with `model.id` unchanged; a swap to a `LEGACY` model carries its `endOfLifeTime`, recorded in the swap's ruling | Threshold Owner proposes, Product rules | ADR-0009; SPEC/02 §2; SPEC/04 §2 |
| cold F5; threshold note 15 | CLAUDE.md and SPEC/00 §5.1 name entry 6 beside the bar rule | Product | CLAUDE.md; SPEC/00 |
| threshold F3; rule F1 | ADR-0010 points at ADR-0009 amendment 1; ADR-0009 says a second key is filed by hand for a definition change until the Rule Owner's amendment | Product | the two ADRs |
| threshold F5; cold N4 | `pinned_roles` completed at PR 2 before either swap PR; PR 2 regenerates the pin patches' context in the commit that edits the manifest | Threshold Owner, Engineering | SPEC/04 §5.1 |
| rule F2, F3; notes 5, 6, 9; data notes 4, 7; threshold notes 14, 17 | Row 17 adds line 51; the probe record marks round 2's version as inferred and round 1's as unrecorded; row 5 "under today's grounding"; row 20 cites both commits; S1's positions from 0; the `deprecated_after` sentence moved; the PII rule reads the answer; the ledger's F4.1 names the reasons | Product, Engineering | as named |

**For PR 2, not fixed here:** `make plants` says "in the tree" for a
reader that does not read its seed yet (cold N1); S1's test does not rule
out the excluded reasons, and PR 3's live read must (cold N3); PR 2's
reader tests keep `CONTROLS` off or give the raws their topics (rule N7);
the p95 evidence restated on the counted set (threshold N12); the
incumbent median's ratchet (threshold N13); `g-021`'s tool answer offers
`ML-2.1` where the golden expects `ML-2.3` (data N5).

**Recorded only:** cold N2; threshold notes 6 to 11 and 16; rule notes 4,
8 and 11; data note 6.

## 3. The false state

SPEC/04 §3, in full. Live today: `score_one` never reads `tool_calls`, so
a breaking swap can pass every citing golden (S1); the eval role may
invoke two models, so the equivalent swap cannot be measured (S2);
nothing compares two runs of one pin (S3); nothing reads `p95_ms` or the
agent's tokens against the incumbent (S4); `validate` never reads
`deprecated_after` (S5). Held today: a run on another model counts (the
gate REJECTs it, ADR-0007 T3); a breaking swap that fails a golden
outright merges (claim 3's guard 1).

The commits: `a16e2c7` S1, `c6b6cb8` S2, `6f18507` S3, `63033b7` S4,
`8994dcb` S5; S3's and S4's raw runs remade at `2dc81ae` and `e0ce2ce`,
before any reader. Every precondition in the seed tests raises
`SeedBroken`, so a broken seed fails the run; only the planted line is
an `assert`. `git show <seed> --stat` shows fixtures, a test, the
fixtures README and one line of `SEEDS_M04` (S1 also `.gitattributes`),
and no reader. Each strict marker was checked with `--runxfail`:

| Seed | Raises | The message read |
|---|---|---|
| S1 | `AssertionError` | "answers the tool did not ground passed: ['g-001', … 'g-011', 'g-021']", all twelve, after the seed's own checks (the pin is Llama's, no successful call) passed |
| S2 | `AssertionError` | "the eval role may not invoke the equivalent swap's profile us.anthropic.claude-sonnet-4-5-20250929-v1:0", after the incumbent's profile was read in the same statements |
| S3 | `SystemExit` | argparse: "unrecognized arguments: --a-vs-a …", after each run alone ruled GREEN |
| S4 | `AssertionError` | "p95 3x the incumbent's ruled GREEN: []" and "tokens 2x the incumbent's ruled GREEN: []" |
| S5 | `ImportError` | "cannot import name 'lifecycle' from 'src.validate'", after `check_manifests` accepted the pin |

Two readings changed a marker or a fixture before its commit, which is
what the rule is for. S1 first failed with `AssertionError` because its
own raw run was malformed: its `guardrail` field was an object, and
`build` refused the file. The raw runs now carry `guardrail` and `tools`
as the runner writes them (`src/agent/run.py:169-171`). S5's marker first
named `ModuleNotFoundError`; `from src.validate import lifecycle` raises
its parent, `ImportError`.

## 4. The code that reads the answer

SPEC/04 §6, all PR 2, in order: tool grounding in `score_one` (S1), with
`g-021` ruled first; `validate`'s `deprecated_after` (S5); the two
`delta_max` bars and the gate reading them (S4); A-vs-A in `build` and
`evals.yml`, and the optional `a_vs_a` field (S3); the cap re-ruled; the
eval role's candidate list in the bootstrap stack, deployed by the human
after `cdk diff --strict` (S2); `pinned_roles`; `observe_pr` given
`runs/f4_swaps.yaml`; `CLAIM_4_CHECKS`. The swap PRs are opened during
PR 2 and read at PR 3. None of it is in this PR.

## 5. Falsifiers, and what each would look like in the repo

SPEC/04 §4. `F4_1` and `F4_2` from PR 2's merge are test-only witnesses
of the seed tests, and gain their second source, the swap PRs, at PR 3.
`F4_3` is read on the run's own two runs, where A-vs-A runs. `F4_4` is
read on the run's own `p95_ms` and tokens, and on S4.

## 6. What M03 carried in (`milestones/M04/open.md`), row by row

Every row is answered here or moved on with a seat and a date. None is
dropped. Rows 25 to 37 were already dated to a later milestone and are
carried to M05's `open.md` at the close as dated.

| # | Seat | Now |
|---|---|---|
| 1 | Product | **Done here**: SPEC/00 §9 amended, seven documents, six admitted, five under a page (`78b042e`). |
| 2 | Product (Rule Owner proposes) | **Ruled here: stays one key through M04**, because no M04 PR changes `rules/**`. Until an ADR-0009 amendment lands, the Rule Owner treats any change to a definition's wording as a relaxation and files a second key by hand. The Rule Owner proposes the amendment (any definition change takes two keys, read by `two_key.py`, whose `rule_relaxations` already holds the old and new definition) at **M05 open, or with the first change to `rules/**`, whichever comes first** (`rule-owner` F3 on this PR). |
| 3 | Data Owner | **M06**, with the knowledge base (SPEC/04 §9 cut f). Until refagent reads the corpus, the answer-side overlap reads nothing. It is the first row of M06's `open.md`, ruled before retrieval lands (`data-owner` note 14). |
| 4 | Data Owner | **Done here** (`6dc922f`): the comment names `sending-terms-to-a-competitor`. |
| 5 | Data Owner, Tool Owner | **PR 2**, before tool grounding lands. `g-021` as written cannot pass grounded: its question's call returns `found: false`, and it expects the original's row `r-011` with `exclusive: false` against that row's `true` (`data-owner` F3, F4). Keeping it as written under today's grounding is ruled out: retire with two keys and re-add under a new id (an absence form needs SPEC/00 §6 amended), or keep it with a changed reader. If it is retired, the expected trap line is restated before PR 2's run (`data-owner` F16). |
| 6 | Security | **PR 2**: read from the first bootstrap `cdk diff --strict`, which is the candidate list's redeploy. Locally, the minified template is 47,535 bytes with non-ASCII escaped and 47,491 as UTF-8 at `0100b64`, whose `infra/` is `main`'s; M03 recorded 47,601 at `0a90d52`. |
| 7 | Security | **Measured here**, by local synth, nothing deployed: the three candidates on the eval role's two invoke statements only, `MODELS` unchanged, add 1,572 bytes: **49,107 of 51,200** (2,093 left). A scratch worktree, removed; no infra file changed in this PR. Anything else added to that stack at M04 is measured against 2,093. |
| 8 | Security, Engineering | **M06**, when refagent first reads the corpus, as dated. |
| 9 | Engineering, Security | **M06**, with row 8, in the same ingest redeploy. |
| 10 | Product, Security | **Done here, read from the envelope.** `evals/history/e51892775b6b36236755f0f9a94e6d98d7628206.json`, written by CI run 36331360122 and committed by `github-actions[bot]` (`82dfd42`), is the first envelope in `mode: runtime` at guardrail `1088aw3ujhyd:5`: runtime `refagent-Du2VJx6xWc`, GREEN, plants 7 of 7 (`guardrail_hits` 7), agent 18 of 20 (`g-014` and `g-021` never passed), `regressed` none, every one of the thirteen checks pass, p95 5,948 ms, 52,652 tokens. `python -m src.verdict.gate` on it exits 0. It says nothing about claim 4. |
| 11 | Engineering, Security | **PR 2** if A-vs-A runs in `mode: runtime`; otherwise SPEC/04 §9 cut 2, **M05**. |
| 12 | Threshold Owner | **Here**: `check_model_access` run on every candidate (`runs/model_access_2026-09-26.md`); the control's fairness ruled: the control stays Nova Micro at `m00`, a swap moves the agent only (SPEC/04 §10). **PR 2**: the cap re-ruled against A-vs-A's measured spend (two keys if raised), and the stale `thresholds.yaml` comment corrected with the new bars. |
| 13 | Threshold Owner | **Ruled here**: `delta_max` on p95 (2.0×) and agent tokens (1.5×), not goldens (SPEC/04 §2). The bars land in `thresholds.yaml` at **PR 2**. |
| 14 | Threshold Owner | **PR 2**: a manifest edit changes the bundle, and would cost row 10. |
| 15 | Engineering; Product | **M06**, with the knowledge base (cut f). |
| 16 | Product; Security | **M06** (cut f; SPEC/00 §9 amended). |
| 17 | Rule Owner | **M06**, with retrieval. Meanwhile `agents/refagent/rules/guardrail.yaml`'s comments are stale: "(M04)" and "until M04" for the knowledge base, "at M04, when it reads documents, the answer side is re-examined" at line 51, and "a third party" at line 65. Comments only, not read by `two_key`; the Rule Owner's next change to `rules/**` carries the fix (`rule-owner` F4, `data-owner` note 2). SPEC/04 §8 says a swap's plants fire before the candidate is called (`rule-owner` F7). |
| 18 | Data Owner | **M06**, with retrieval: an answer cites a corpus clause only once refagent reads the corpus. |
| 19 | Product; Threshold Owner; Data Owner | **Done here**: SPEC/04 §9 cuts b, c, d (SPEC/03 cuts 1 to 4) to M07 and M06; SPEC/00 §8 M06 and M07 name them. |
| 20 | Rule Owner | **Done here** (`70c2322`, `688634c`). |
| 21 | Rule Owner | **M05**, with Promptfoo (row 25). |
| 22 | Engineering | **PR 2**: item f (`server.py`'s profile default, which is the model the runtime calls) and item h (build's token sums, which A-vs-A doubles). Item i: **M05**. Cut 2 if the cap is threatened. |
| 23 | Product | **Done here**: SPEC/00 §3 and §10.3 row 03 amended, `docs/milestones/README.md` regenerated, M03's page takes the amended sentence. |
| 24 | Product | **Done here** (`31a026c`): 3:36, 4,323,437 bytes, LFS. The row's Shows cell is confirmed by Product in `rulings/pr1.md`. |
| 25–35 | as dated | **M05**, carried unchanged. |
| 36 | Tool Owner | **M06; M07**, carried unchanged. |
| 37 | Rule Owner | **M08**, carried unchanged. The judge lands at M07 (cut b), before it. |
| 38 | Engineering | **Done here** (`22b9cd9`): each shipped test run with its reader switched off fails with its planted message. |
| 39 (new) | Product, Security, Threshold Owner | **The gateway decision, M05 open.** The probe (`runs/llm_gateway_probe.md`) leaned M05: through an inference target Sonnet 4.6 answered 404; through a passthrough target signed as the gateway's role, two calls with version 5 answered as direct Converse does and one call without the guardrail was refused naming the gateway's role. Open for M05: the pin for every caller and every version, what CloudTrail records, and the refusing statement. |
| 40 (new) | Security | **A seeded refusal of a model call without the pinned guardrail, or around the agent's own profile: M05**, with row 26. Nothing has attempted it in AWS. M04 only if the gateway had landed here; it did not. |

## 7. What PR 1 does not do

- It builds no reader: `score_one`, `build`'s command line, the gate,
  `thresholds.yaml`, `validate` and the bootstrap stack are unchanged.
  The strict markers say so.
- It changes no pin: `agents/refagent/**` is untouched, so the bundle
  digest is `main`'s.
- It moves no bar and touches no AWS. The redeploy and the swap PRs are
  PR 2's, and the human makes them.
- It adds no specialist (R8).
