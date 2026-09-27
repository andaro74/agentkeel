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
