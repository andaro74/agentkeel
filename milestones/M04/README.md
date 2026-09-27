# M04 — Model swap

## Ledger row

Written at M04 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 4 |
|---|---|
| Claim | A breaking model swap goes RED; an equivalent swap promotes; A-vs-A is zero diff |
| Falsifiers | F4.1 the breaking swap is GREEN, or RED for a reason other than a citing golden regressed, ungrounded or with wrong fields (a REJECTED, an access error or the cost cap is not the reason) (live: the breaking swap PR, read at PR 4's run). F4.2 the equivalent swap is RED or REJECTED, or a required check on its PR is red for a reason of its own ("promotes" is mergeable, not merged; live: the equivalent swap PR, read at PR 4's run). F4.3 A-vs-A shows a diff: two runs of one pin in one `evals` job with any golden's `pass` different (the milestone stops). F4.4 a run over a `delta_max` bar is GREEN: `p95_ms` over 2.0x, or the agent's tokens over 1.5x, the incumbent's median in the same mode. |
| Seeded commit | `a16e2c7` (S1); `c6b6cb8` (S2); `6f18507` (S3); `63033b7` (S4, two cases), S3's and S4's raw runs remade at `2dc81ae` and `e0ce2ce` before any reader; `8994dcb` (S5, no falsifier: SPEC/00 §8 M04's `deprecated_after`), each its own commit before any reader (SPEC/04 §5) |
| Expected gate output | PR 1: refagent's envelope as at M03; it says nothing about claim 4. PR 1 leaves `agents/refagent/**` and `data/rights_table.json` alone, so its run may be the first `mode: runtime` envelope at guardrail `1088aw3ujhyd:5` (`open.md` row 10); the envelope says whether it is. `make plants` lists S1 to S5; `tests/test_m04_seeds.py` shows 6 expected failures. PR 2, on the PR: S1 to S5 refused by their readers, each for its planted reason; refagent under tool grounding ordinary 9/9, traps 2/2 (`g-021` retired at PR 2 before grounding landed, nothing added; restated before PR 2's run), fewer being the finding; refagent's A-vs-A zero diff, the control's reported and not gated, on PR 2's own run (the `a-vs-a` label); p95 and tokens within their bars. From PR 2's merge the gate requires `F4_1`, `F4_2` and `F4_4` on every agent envelope and `F4_3` where A-vs-A runs; **`F4_1` and `F4_2` from the seed tests alone are test-only witnesses**. During PR 2 the human redeploys the bootstrap stack with the eval role's candidate list after reading `cdk diff --strict`, and opens the two swap PRs from PR 2's head. **A named P3 exception (SPEC/04 §5.1): PR 4's run reads the swap PRs, after their rulings are on `main`;** amended at PR 3, since PR 2 merged before the rulings joined it: PR 3 is the repair and the read's machinery, and the read is recorded in the envelope's `swaps` and gated by nothing (`F4_1` and `F4_2` stay test-only witnesses). The equivalent swap's first run regressed `g-005`, recorded at PR 3 before the reading run. Stated before: the breaking swap RED with at least one citing golden regressed, ungrounded or wrong, and no REJECTED, access error or cost cap; the equivalent swap GREEN with every required check green. RED if a seed's test passes but by its reader, if either swap reads otherwise, if refagent's A-vs-A shows a diff, if a run over a bar rules GREEN, if PR 4's run cannot read the swap PRs, or if `make ledger` stops matching rows 0 to 3. |
| Measured | — |
| PRs used / cap | 3 / 4 |
| State | OPEN |

### Open detail (PR 1, 2026-09-26)

- **Opened through `/open-milestone`.** SPEC/04 was written first and
  `product-spec-reviewer` run on it (1 BLOCK, 12 FINDING, 4 NOTE), pasted
  verbatim in `feasibility.md` §1. The human ruled every item "as
  proposed" before any seed, and SPEC/04 was revised once on the rulings
  (`78b042e`, before the first seed `a16e2c7`). Six rulings made before the
  draft are filed with them (`feasibility.md` §2).
- **The BLOCK was M02 PR 2's trap again.** A swap PR's check cannot be
  green on the run that measures it, and a swap PR's run would read
  itself. Ruled: from PR 2's merge, `F4_1` and `F4_2` come from the seed
  tests alone, as test-only witnesses; the swap PRs are opened during
  PR 2 and read by PR 3's run, a named P3 exception; PR 3 is both that
  read and the repair. There is no fifth PR.
- **Planted** in five commits, one per seed, `a16e2c7` to `8994dcb`; S3's
  and S4's raw runs were remade before any reader, at `2dc81ae` (made on
  the real tool, `data-owner` F9) and `e0ce2ce` (the date the question
  asks about; S3 ruled against the incumbent; a broken seed fails the run
  with `SeedBroken`, cold review F3 and F4). Each
  with its test in `tests/test_m04_seeds.py`, before any code that reads
  them: 6 expected failures (S4 has two cases), each run once with
  `--runxfail` and its message read. Two readings on the way were the
  point of that rule: S1 first failed with `AssertionError` because its
  own fixture was malformed (`build` refused its `guardrail` field), not
  for its planted reason, and S5 raises `ImportError`, not the
  `ModuleNotFoundError` first written in its marker. Both were fixed
  before their commits.
- **What is live today, in the repo:** `score_one` never reads
  `tool_calls` (S1); the eval role may invoke two models (S2); nothing
  compares two runs (S3); nothing reads `p95_ms` or the agent's tokens
  against an incumbent (S4); `validate` never reads `deprecated_after`
  (S5).
- **Read in this PR:** nothing of claim 4. `make plants` lists S1 to S5;
  S1's, S3's and S4's readers are files already in the tree that change
  at PR 2, so it says "in the tree" beside them, and the strict markers
  are what say no seed is read. S2's reader is `infra/bootstrap/app.py`,
  unchanged.
- **Cut at open** (SPEC/04 §9, rulings 4 and 6, finding 7): `model-watch`,
  the judge with its rubric, graded examples and `admitted_false_fails.json`,
  the Braintrust mirror, and `deprecated_after` set from Bedrock, to M07;
  k6 to M05; the knowledge base with the cached-answer seed, F3.5's second
  half and `g-014`, and FRAGILE, to M06. SPEC/00 §8 and §9 are amended
  to say so.
- **Also in this PR:** M03's S1 and S2 tests run with their readers
  switched off (`open.md` row 38); `g-015`'s comment (row 4); the
  `red-teamer` prompt (row 20); ADR-0010 and the CLAUDE.md seat line
  (findings 9, 10); the M03 video (row 24); the gateway probe record.
  Every `open.md` row and the two new items are answered or moved in
  `feasibility.md` §6.
- **This PR's run** wrote refagent's envelope as at M03, and it does
  not measure claim 4. It is the first envelope in `mode: runtime` at
  guardrail version 5 (`open.md` row 10): `e518927`'s, CI run
  36331360122, committed by `github-actions[bot]` as `82dfd42`, GREEN,
  plants 7 of 7, agent 18 of 20 (`g-014`, `g-021` never passed), p95
  5,948 ms, 52,652 tokens; the gate on it exits 0.

### PR 2 detail (the measure, 2026-09-27)

- **`g-021` ruled first** (`open.md` row 5), before grounding: retired
  with two keys, Data Owner and Threshold Owner, nothing added (`fe70686`).
  The absence form it needs is SPEC/00 §6's and goes to M06. The expected
  line was restated before the run: traps 2 of 2 live.
- **The readers, in SPEC/04 §6's order**, each in its own commit, each
  seed's marker off in the commit that lands its reader, and each test
  run once with its reader switched off to see the planted message:
  grounding in `build` (S1, `9b5e3f6`; all eleven live citing answers
  named); `deprecated_after` in `validate` (S5, `7bf5d3c`; read on
  2026-09-27, S5's date is 17 days away, so it met "within 30 days"); the
  `delta_max` bars (`fb1e6e9`, Threshold Owner) and the bars and A-vs-A in
  `build` and the gate (S4 and S3, `1436366`); the eval role's candidate
  list (S2, `2870467`, Security; 49,107 of 51,200 bytes). `pinned_roles`
  carry the whole pin, and the three pin patches were regenerated for
  context only (`02c51d6`; `0c277ab` put back two comment lines that
  M02's S1 patches read). `observe_pr` reads GitHub's record of the swap
  PRs (`b3c41d9`), not wired in `evals.yml` until PR 3; the first draft
  also read each swap's envelope and let `build` rule on it, which the
  cold review blocked (P5), so that part was cut and PR 3 has the gate
  rule the swap's envelope. The flags are wired at `15047b4`, from which the
  gate requires `F4_1`, `F4_2` and `F4_4`, and `F4_3` where the pin moved
  (`cea0a5d`). `tests/test_m04_seeds.py`: six passed, none expected to
  fail.
- **Also here:** `open.md` row 22 items f (the runtime names no model of
  its own) and h (the gate holds the token sums to the control card), and
  row 12 (the cap comment). Item i stays M05.
- **A pre-read, not evidence.** M04 PR 1's run artifact (CI run
  36331360122, raws kept 90 days) scored with the new `build`: ordinary
  9/9 and traps 2/2 under grounding; with its raws doubled as a stand-in
  for A-vs-A, GREEN, 105,304 tokens of 150,000. It found one bug, fixed
  (`89e57ec`).
- **Still to happen during this PR, by the human:** read `cdk diff
  --strict` on the bootstrap stack and deploy it (S2's redeploy; also
  `open.md` row 6); open the two swap PRs from this PR's head, each
  changing only `model` to its `pinned_roles` entry; then this PR gains
  `milestones/M04/runs/f4_swaps.yaml` and the swaps' Threshold Owner
  rulings. PR 3 wires the swap read and is the read.

### PR 3 detail (the repair and the read's machinery, 2026-09-27)

- **PR 2 (#24) merged before its last three items joined it:** the swap
  PRs' numbers (`milestones/M04/runs/f4_swaps.yaml`), their Threshold
  Owner rulings, and the bootstrap redeploy's readback. All three are in
  this PR. The human opened the swap PRs from PR 2's head (`10926b2`):
  #25 breaking (Llama 3.1 8B) and #26 equivalent (Sonnet 4.5), each
  changing only the three lines of `model`.
- **What their first runs found.** Both RED. #25: ordinary 0/9, traps
  0/2, eleven citing goldens regressed, A-vs-A zero diff. #26: ordinary
  8/9, `g-005` regressed the same way in both runs (available, `EM-1`,
  no embargo; 01:30 UTC on 14 May is still 13 May in São Paulo), A-vs-A
  zero diff. Sonnet 4.5 answered every call, so the eval role's
  candidate list is deployed.
- **What the cold review of PR 2 did not find, and the swap PRs did.**
  On both, `checks` was red for the suite's own reason: nine tests (ten
  on #26) treated Sonnet 4.6 as the tree's pin. The seed patches carried
  the planted pin as context, the seeds read their incumbent from the
  working tree, and three tests named the model literally. That also
  failed each swap's `F4_1` to `F4_4`, whose seed tests are their first
  source. Repaired first (`feaa036`): the seeds run against the planted
  pin wherever the tree's pin moved, the others read the manifest. On
  each swap's pin the suite went from 9 and 10 failed to 566 passed.
- **The read, recorded and not gated (Product).** As SPEC/04 §4 was
  first written, `build` would have failed `F4_2` on every envelope that
  read #26, and the one run that read it could not have merged.
  `observe_pr` now reads `f4_swaps.yaml` in every `evals` run,
  `scripts/rule_swaps.py` has the gate rule each swap's own envelope at
  its commit, and `build` copies the verdicts into `swaps`, which the
  ledger's Measured cell prints (`11ef848`). Run here against #25 and #26
  as they stand (not evidence): #25 RED, eleven regressed; #26 RED,
  `g-005` regressed; both with the red seed checks the repair removes.
- **After this PR merges:** `main` is merged into both swap branches,
  their checks run again, and PR 4's run reads them.
