# M04 — Model swap

## Ledger row

Written at M04 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 4 |
|---|---|
| Claim | A breaking model swap goes RED; an equivalent swap promotes; A-vs-A is zero diff |
| Falsifiers | F4.1 the breaking swap is GREEN, or RED for a reason other than a citing golden regressed (live: the breaking swap PR, read at PR 3). F4.2 the equivalent swap is RED or REJECTED, or a required check on its PR is red for a reason of its own ("promotes" is mergeable, not merged; live: the equivalent swap PR, read at PR 3). F4.3 A-vs-A shows a diff: two runs of one pin in one `evals` job with any golden's `pass` different (the milestone stops). F4.4 a run over a `delta_max` bar is GREEN: `p95_ms` over 2.0x, or the agent's tokens over 1.5x, the incumbent's median in the same mode. |
| Seeded commit | `a16e2c7` (S1); `c6b6cb8` (S2); `6f18507` (S3); `63033b7` (S4, two cases); `8994dcb` (S5, no falsifier: SPEC/00 §8 M04's `deprecated_after`), each its own commit before any reader (SPEC/04 §5) |
| Expected gate output | PR 1: refagent's envelope as at M03; it says nothing about claim 4. PR 1 leaves `agents/refagent/**` and `data/rights_table.json` alone, so its run may be the first `mode: runtime` envelope at guardrail `1088aw3ujhyd:5` (`open.md` row 10); the envelope says whether it is. `make plants` lists S1 to S5; `tests/test_m04_seeds.py` shows 6 expected failures. PR 2, on the PR: S1 to S5 refused by their readers, each for its planted reason; refagent under tool grounding ordinary 9/9, traps 2/3, fewer being the finding; refagent's A-vs-A zero diff, the control's reported and not gated; p95 and tokens within their bars. From PR 2's merge the gate requires `F4_1`, `F4_2` and `F4_4` on every agent envelope and `F4_3` where A-vs-A runs; **`F4_1` and `F4_2` from the seed tests alone are test-only witnesses**. During PR 2 the human redeploys the bootstrap stack with the eval role's candidate list after reading `cdk diff --strict`, and opens the two swap PRs from PR 2's head. **A named P3 exception (SPEC/04 §5.1): PR 3's run reads the swap PRs, after their rulings are on `main`;** PR 3 is both that read and the repair. Stated before: the breaking swap RED with at least one citing golden regressed, ungrounded or wrong, and no REJECTED, access error or cost cap; the equivalent swap GREEN with every required check green. RED if a seed's test passes but by its reader, if either swap reads otherwise, if refagent's A-vs-A shows a diff, if a run over a bar rules GREEN, if PR 3 cannot read the swap PRs, or if `make ledger` stops matching rows 0 to 3. |
| Measured | — |
| PRs used / cap | 1 / 4 |
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
- **Planted** in five commits, one per seed, `a16e2c7` to `8994dcb`, each
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
- **This PR's run** writes refagent's envelope as at M03. It does not
  measure claim 4. PR 1 does not touch `agents/refagent/**` or
  `data/rights_table.json`, so the run may be in `mode: runtime` at
  guardrail version 5, the first (`open.md` row 10); what it says is read
  from the envelope, not from this line.
