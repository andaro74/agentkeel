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
| Measured | agent: traps 2/3 (g-010, g-011); ordinary 9/9; guardrail 2/3; redteam 5/5; control: traps 0/3; ordinary 0/9; guardrail 0/3; redteam 0/5; mode runner; never_passed 2; regressed 0; plants 7/7; F0_2 pass https://github.com/andaro74/agentkeel/actions/runs/36270471757; F0_3 pass https://github.com/andaro74/agentkeel/actions/runs/35401176820/job/105781176255; F1_1 pass https://github.com/andaro74/agentkeel/actions/runs/36270471757; F1_2 pass https://github.com/andaro74/agentkeel/actions/runs/36270471757; F1_3 pass https://github.com/andaro74/agentkeel/actions/runs/36270471757; F1_4 pass https://github.com/andaro74/agentkeel/actions/runs/36270471757; F2_1 pass https://github.com/andaro74/agentkeel/actions/runs/36270471757; F2_2 pass https://github.com/andaro74/agentkeel/actions/runs/36270471757; F3_1 pass https://github.com/andaro74/agentkeel/actions/runs/36270471757; F3_2 pass https://github.com/andaro74/agentkeel/actions/runs/36270471757; F3_3 pass https://github.com/andaro74/agentkeel/actions/runs/36270471757; F3_5 pass https://github.com/andaro74/agentkeel/actions/runs/36270471757; F3_6 pass https://github.com/andaro74/agentkeel/actions/runs/36270471757; GREEN; envelope `cb06c0dbf0019088c664c6df1ce7d67cc64f7d58`; base b0219756 |
| PRs used / cap | 4 / 4 |
| State | GREEN |

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

### PR 2 and PR 3 (2026-09-26)

- **PR 2 (#20), the measure**, merged as `a423292`. Its run's envelope,
  `0225d84`, ruled GREEN: plants 7 of 7, every claim 3 check passing,
  `mode: runner`, guardrail `1088aw3ujhyd:4`. The rulings are
  `rulings/pr2*.md`; its Unsure list carried item C to PR 3.
- **PR 3, the repair**: Unsure C. `guardrail.yaml` names the rule each of
  its own plants must be blocked by, as `redteam.yaml` does, so dropping
  `sending-terms-to-a-competitor` now silences `g-015`. Guardrail version
  5 was cut by the human's bootstrap redeploy (stop A) and the ingest
  stack redeployed with it (stop B); the manifest pins 5. The row's
  Measured cell is PR 4's, from this PR's envelope or a later one.

### Close detail (PR 4, the close, 2026-09-26)

**Row 3 is GREEN.** The cap was four and four were used. Every seed was
refused by its reader, `build` counted the seven plants as fired, each
only with its named rule among the topics, and no guard went red.

**The measurement.** The Measured cell is copied from `make ledger`'s
reading of the envelope for `cb06c0dbf0019088c664c6df1ce7d67cc64f7d58`,
written by CI run 36270471757 and committed by `github-actions[bot]`
(`013a1c5`), PR 3's run on the tree that shipped. `make ledger` exits 0
against it. As numbers: agent ordinary 9/9, traps 2/3 (`g-010`, `g-011`),
guardrail 2/3, red team 5/5; control ordinary 0/9, traps 0/3, guardrail
0/3, red team 0/5; plants 7/7 (`guardrail_hits` 7); `never_passed` 2
(`g-014`, not counted until M04; `g-021`); `regressed` 0; F0_2 to F3_6,
thirteen checks, pass; `corpus_fingerprint` `e12988c5…`, the gate's own
reading; `cache_state: disabled`, a constant; `mode: runner`; guardrail
`1088aw3ujhyd:5`; 52,131 tokens (47,034 in, 5,097 out) against 150,000.

**Why this envelope and not a later one.** `main`'s run 36272077628 found
nothing measured had changed since `cb06c0d` and ruled that envelope
GREEN without spending. This PR changes only `docs/**` and
`milestones/**/*.md`, which `evals.yml` does not measure, so its run
does the same. **No envelope reads the runtime at version 5.** The merge
deploy's load check (run 36272077619: 20 observations, 0 errors, the
seven plants `guardrail_intervened`, `g-014` `end_turn`; transcribed in
`runs/pr3_merge_deploy_load_check.md`) is a deploy log, and it prints no
topics and no version. The first `mode: runtime`
envelope at `:5` is `milestones/M04/open.md` row 10.

**Row 3's RED conditions, each checked at the close:** no seed's test
passes but by its reader (`uv run pytest tests/test_m03_seeds.py`, 9
passed; each strict marker came off in the commit that landed its reader,
`pr2-engineering.md`. **For S1 and S2 this is recorded, not measured**:
their test bodies changed with their readers (its N1), so no commit shows
the shipped test failing without its reader; M04 `open.md` row 38);
no silent plant ruled GREEN (7 of 7); plants are not under 7; the
amendment is not in the production bucket (F3_5, CI's lookup in run
36270471757); both guards green; `make ledger` matches rows 0 to 2.

**What GREEN does not mean.** The runtime was not measured at version 5.
`F3_1`, `F3_3` and `F3_6` are test-only witnesses: seeds S1, S3, S6 and
S7 refused in a copy of the tree, no PR opened. F3.5's second half, "or
changes an answer", is not measured: nothing reads the corpus until M04.
None of the ingest stack's own refusals has been attempted in AWS. Until
the judge exists, "correct" is the answer's fields compared by code. One
person holds every seat.

**Found at the close: SPEC/03 cuts 1 to 4 were never built, and no
ruling took them.** The Braintrust mirror (with its divergence check and
redaction), the Bedrock Evaluations judge, `admitted_false_fails.json`
and the FRAGILE state are in SPEC/00 §8's M03 build list; SPEC/03 §9
allowed each cut "only if the cap is threatened", and no PR recorded one.
Recorded as taken here (`rulings/pr4.md`), not before, each to M04 as §9
names; cut 5, Promptfoo, to M05. `milestones/M04/open.md` rows 19 and 25.

**Findings and Unsure items: every one has a home.** By source:

| Source | Count | Where each is held |
|---|---|---|
| `product-spec-reviewer` on SPEC/03 | 3 BLOCK, 12 FINDING, 4 NOTE | `feasibility.md` §2, each ruled before or with the seeds; B2's reader and seed are M04 `open.md` row 15; F11 row 13 |
| PR 1 (#19) seat reports and cold reviews | cold 0/5/5 and 0/1/5; security 1/7/8; rule-owner 0/6/6; data-owner, red-teamer | `rulings/pr1*.md` tables; the M04 and M05 items are M04 `open.md` rows 20, 25, 30, 31 |
| PR 2 (#20) seat reports and cold review | cold 1/7/9; security 0/4/14 and five partial reads; rule-owner 1/5/8; data-owner 0/3/14; platform-architect, red-teamer | `rulings/pr2*.md` tables; recorded items with no date before this close are M04 `open.md` rows 9 (N7), 11 (`security-reviewer` F1 on `606bece`), 17, 18, 21 (N9); the rest rows 26, 29, 33, 35 |
| PR 3 (#21) seat reports and cold review | cold 0/1/6; security 0/4/16, 0/2/16, 0/2/12; rule-owner 0/3/13, 0/3/5, 0/1/7; threshold-owner 0/1/11 | `rulings/pr3*.md` tables; M04 `open.md` rows 6, 7, 8, 12, 26, 27, 28, 32 |
| Unsure, #19 (A to G) | 7 | A, B ruled (`pr1.md` rulings 6, 5); C ruled (`pr2.md` ruling 1); D M04 `open.md` row 30 (M05); E closed: `red-teamer` was exercised twice more in PR 2 (#20's first comment); F done at PR 2 (the deny narrowed, 79 cases); G done (#19) |
| Unsure, #20 (A to G) | 7 | A, B, E M04 `open.md` rows 1, 2, 3; C repaired at PR 3; D read by the merge deploy's load check, a log; F done (`a9c8ff6`); G row 29 (M05) |
| Unsure, #21 (A to G) | 7 | A row 4; B the eval role read by `cb06c0d`, the runtime's condition by run 36272077619's load check (a log; row 10); C closed here, negatively: no `mode: runtime` envelope at `:5` exists (row 10); D row 6; E ruled, M05 (row 28); F row 5; G ruled in `pr3-security.md` (rows 7, 8, 26, 27) |
| PR 4 (this PR) cold reads | 0/6/6; second read 0/3/6 | `rulings/pr4-engineering.md` table, each repaired or held; the second read's F3 is M04 `open.md` row 38 |
| M03 `open.md` rows 1 to 15 | 15 | `feasibility.md` §6 answered each at PR 1; rows 3 to 8 at PR 2 and PR 3; row 11's items e and j done at PR 2 (`src/verdict/__init__.py`, the readers at a commit) and g done (`src/agent/run.py`, the goldens no longer excluded); what was dated M04 or later, and row 11's items f, h, i and a to d, k, are M04 `open.md` rows 12 to 15, 22, 34 and 36 |

**Still open, for the human after the merge:** sign
`milestones/M03/attestations.md`; `git tag m03` on `main`; record the M03
video at the tag for M04 PR 1 (M04 `open.md` row 24).
