---
# M04 PR 4 (#28), the close. Product's key. Engineering's file is
# pr4-engineering.md (the code, with the cold review).
ruling: pr4
seat: Product
authorises:
  - SPEC/04-model-swap.md
  - milestones/README.md
  - milestones/M04/README.md
  - milestones/M04/attestations.md
  - milestones/M04/rulings/pr4.md
  - milestones/M04/rulings/pr4-engineering.md
  - milestones/M04/runs/f4_swaps.yaml
  - milestones/M05/open.md
  - docs/milestones/M04.md
  - docs/milestones/README.md
  - docs/video/README.md
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md#51-when-each-is-measured
  - SPEC/04-model-swap.md#7-expected-on-the-plant-row-4
  - https://github.com/andaro74/agentkeel/actions/runs/36362949356
  - evals/history/05bd718feb0cc72ab78df13fccf47c3efb8a9314.json
  - milestones/M04/rulings/pr1.md
  - milestones/M04/rulings/pr2.md
  - milestones/M04/rulings/pr3.md
  - milestones/M04/rulings/swap-breaking.md
  - milestones/M04/rulings/swap-equivalent.md
  - https://github.com/andaro74/agentkeel/pull/25
  - https://github.com/andaro74/agentkeel/pull/26
pr: 28
---

# Ruling: M04 PR 4, Product

Ruled by andaro74 as Product, 2026-09-27, as written.

## 1. What this PR is

PR 4 of M04, the close, and the last: 4 / 4. It records the swaps'
re-runs in `f4_swaps.yaml`, so its own run measures and is the read
(`pr3.md` §4); lands row 4's reading of the swaps (Engineering,
`pr4-engineering.md`); writes row 4's Measured cell from the gate's
reading of the envelope for `05bd718` (CI run 36362949356, bot commit
`a3bae6b`), State RED; the explainer's "What happened"; the M04 video
row (not recorded); `attestations.md`; this file; and
`milestones/M05/open.md`. `make ledger-plain` wrote
`docs/milestones/README.md`.

## 2. The reading of the swaps lands in the close (Unsure A)

SPEC/04 §7, written at PR 3, closes row 4 RED on F4.2 "either way". PR 3
left no way to write that: the cell carried refagent's own GREEN, and
`src/ledger.py` refuses State RED beside a GREEN cell. The human chose,
on 2026-09-27 before any code, to have the cell read the swaps rather
than loosen the ledger or close with "—". The cold review of this PR
found that this is machinery that reads the claim, landing in the last
PR (B1). **Ruled: a second named P3 exception,** written into SPEC/04
§5.1 and row 4's Expected cell (`05bd718`) before the reading run. It
gates no pull request, leaves `rule` unchanged and can only turn row 4's
cell RED; without it, row 4 could close only as "—" RED, with the
measurement thrown away. The finding is PR 3's: its machinery recorded
the swaps but gave the row no way to be decided by them, and neither of
PR 3's two cold reads, nor this session before its first `make ledger`,
saw it.

## 3. The reading

The envelope for `05bd718`: refagent GREEN in `mode: runtime` at
guardrail `1088aw3ujhyd:5`, ordinary 9/9, traps 2/2, plants 7/7, 48,731
tokens. The swaps as recorded:

- **#25, breaking** (Llama 3.1 8B), re-run `d61af92`: RED, eleven
  citing goldens regressed, and `F1_4` failed (wrong fields); no
  REJECTED, access error or cost cap. **F4.1 holds.**
- **#26, equivalent** (Sonnet 4.5), re-run `a86262e`: RED, `g-005`
  regressed; its `evals` red, every other required check green.
  **F4.2 fires**, as on its first run `9ff21d5`, which decides it
  (`pr3.md` §3).

Row 4's cell: "swap #26 equivalent missed: RED, expected GREEN; RED".
The PR body stated it before the run. `make ledger` exits 0 against it.

## 4. Seats named at the close, and cut 1 (Unsure B)

No source named a seat for four carried items; each is proposed in
`milestones/M05/open.md` and ruled here as proposed: k6 (row 23,
Engineering, with the Threshold Owner for the bar it reads); a second
agent's model (row 33, Threshold Owner); `model-watch` (row 35,
Engineering, with Security for the App or token); the Braintrust mirror
(row 37, Engineering, with Security for redaction).

SPEC/04 §9 cut 1, the cheaper swap's run (Haiku 4.5), allowed "only if
the cap is threatened", was never made, and the cap was not threatened
(97,635 of 150,000 at PR 2). No ruling took it at the time. **Recorded
as taken here, not before** (row 39, Threshold Owner, M07), as M03's
cuts 1 to 4 were at M03's close.

## 5. Every Finding and Unsure item

Collected from `feasibility.md`, every ruling file, the seat reports and
cold reviews, and the Unsure lists of #23, #24, #27 and this PR. Each is
closed in M04 (its ruling says where), or in `milestones/M05/open.md`
with a seat and a milestone: 43 rows. Five had no complete home before
the close and have one there: #27 Unsure B (row 24, answered by this
PR's cold review), cut 1 (row 39), `guardrail.yaml`'s stale comments
(row 3), k6 and a second agent's model (rows 23, 33). The M04 video is
row 42. The swap PRs are closed unmerged after this run (Unsure C,
Threshold Owner).

## 6. What red does not mean

Written in `docs/milestones/M04.md`: the gate missed neither swap, and
neither merged. The row is RED because the model named equivalent
before any run lost a question today's model answers right, and the
label was not moved to fit (SPEC/04 §2).
