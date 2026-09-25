# M03 — Evals, regression bar, red team, corpus admission

## Ledger row

Written at M03 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 3 |
|---|---|
| Claim | The eval gate goes RED on a regression or a silent plant, and never on a never-passed golden |
| Falsifiers | F3.1 the regressed golden merges (live: a regression through the rights table, measured in the runtime against `main`'s table). F3.2 a silent plant and the gate is green. F3.3 the overlapping golden passes `validate`. F3.4 an envelope carries no fingerprint, or a cache state outside `bypass\|disabled\|uncacheable`. F3.5 the unsigned amendment reaches the production bucket (its second half, "or changes an answer", is not measured at M03: the knowledge base is cut to M04). F3.6 a never-passed golden turns the gate RED (live: a control added today, or a pass recorded later, re-rules an older envelope). |
| Seeded commit | `61ac95a` (S1); `c5f5ca3` (S2); `01876a7` (S3); `2fd7128` (S4, no file: the envelope for `8033c2a` is the false state); `149d352` (S5, the attempt to make, `observed: null`); `d229601` (S6); `1e51666` (S7, after the cold review of PR 1, before any reader), each its own commit (SPEC/03 §5); the two guards `92c7b2a`, no marker |
| Expected gate output | PR 1: refagent's envelope in `mode: runtime`, gated and recorded as at M02; it says nothing about claim 3. `make plants` lists S1–S7; `tests/test_m03_seeds.py` shows 7 expected failures and 2 passes (the guards: a regressed golden RED, a never-passed golden not). PR 2, on the PR: S1, S2, S3, S4, S6 and S7 refused by their readers in a copy of the tree, each with its planted reason; **plants 7 of 7** (`g-013`, `g-015` to `g-020`; `g-014`, MASKED, is not counted at M03, since nothing is masked until the knowledge base, ruled at PR 1), stated before the run: `CONTROLS` lands only after the guardrail is on the runner's and the runtime's call, and fewer than 7 leaves PR 2 unable to merge, which is the finding (P10), not a count to lower; `corpus_fingerprint` non-null and equal to the gate's own reading; during PR 2 the human deploys the ingest stack after reading `cdk diff` and uploads S5, and PR 2's run reads it absent from the production bucket (`scripts/observe_ingest.py`), else F3.5 is read at PR 3 as a named P3 exception. From PR 2's merge the gate requires `F3_1`, `F3_2`, `F3_3`, `F3_5`, `F3_6` and a fingerprint on every agent envelope. `F3_1`, `F3_3` and `F3_6` are test-only witnesses of a seed refused in a copy of the tree; no seed PR is opened. RED if a seed's test passes for any reason but its reader, if a silent plant rules GREEN, if plants are under 7 at the close, if the amendment reaches the production bucket, if a guard goes red, or if `make ledger` stops matching rows 0 to 2 when a control lands. |
| Measured | — |
| PRs used / cap | 1 / 4 |
| State | OPEN |

### Open detail (PR 1, 2026-09-25)

- Opened through `/open-milestone`. SPEC/03 was written first and
  `product-spec-reviewer` run on it (3 BLOCK, 12 FINDING, 4 NOTE), pasted
  verbatim in `feasibility.md` §1. The human ruled the three BLOCKs and
  findings F2 and F9 before any seed; SPEC/03 was revised once on them
  and lands in `ac399c0`, before the first seed (`61ac95a`).
- **Two of the claim's three parts were built before this milestone.**
  `verdict.gate.judge` has gone RED on a regressed golden, and has not
  gated a never-passed one, since M00 PR 2. A seed that replayed only
  that would pass today, so they are held by two guard tests with no
  marker (`92c7b2a`). The seeds are the routes by which each part is
  false today: a regression measured against `main`'s table in the
  runtime (S1), a silent plant with its control in the tree (S2), and a
  control added today re-ruling an older envelope RED on goldens that
  never passed (S6, `product-spec-reviewer` B1).
- **Planted** in seven commits, one per seed, `61ac95a` to `d229601` and
  `1e51666` (S7, from the cold review's F1, ruled a seed before any
  reader), each with its test in `tests/test_m03_seeds.py`, before any
  code that reads them. Seven tests are expected failures, each failing for
  its planted reason (checked with `--runxfail`). S4 plants no file: the
  envelope for `8033c2a`, row 2's, says `corpus_fingerprint: null`. S5 is
  an attempt against AWS, `observed: null` until the human makes it
  during PR 2.
- **Read in this PR:** nothing. `CONTROLS` is empty, `validate` has its
  twelve checks, the runtime match reads the bundle alone. `make plants`
  lists S1–S7; S1's, S6's and S7's readers are files already in the tree that
  change at PR 2.
- **Cut at open:** the knowledge base and refagent's retrieval, to M04
  (SPEC/03 cut 6, ruling on F9). F3.5 is read on its production-bucket
  half; "or changes an answer" is not measured at M03. The cached-answer
  seed SPEC/00 §8 names is not planted (ruling on B2) and moves to M04
  with it.
- **Stated before PR 2's run:** plants 7 of 7 (ruling on B3, amended after the seat reports: `g-014` is not counted at M03).
- **Carried work** (`feasibility.md` §6): row 1, ADR-0009, the closed
  list of relaxations amended from the Threshold Owner's proposal; row 2,
  SPEC/01 §9's ceiling bullet; row 9, the M02 video (`47d53c6`, 5:48, 48
  seconds over the ceiling) and the ruling on the ceiling in
  `rulings/pr1.md`; row 11, M02 open.md rows 12 and 13 checked item by
  item, 0 of 11 done, each re-dated. Rows 3, 4, 5 and 8 are readers or
  bars and are PR 2's. The two specialists R8 adds at M03, `red-teamer`
  and `docs-writer`, are in the tree, each exercised once in this PR.
- **This PR's run** writes refagent's envelope as at M02. It does not
  measure claim 3.
