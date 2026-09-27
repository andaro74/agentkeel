---
# M04 PR 2 (#24), the Data Owner's key. The second key on g-021's
# retirement is the Threshold Owner's, rulings/pr2-threshold-owner.md.
# Product's file is rulings/pr2.md.
ruling: pr2-data-owner
seat: Data Owner
authorises:
  - evals/goldens/v1/g-021.yaml
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md#2-words-used-here
  - milestones/M04/open.md
  - milestones/M04/feasibility.md
  - milestones/M02/rulings/pr2-data-owner.md
  - data/rights_table.json
  - agents/refagent/tools/check_availability.json
pr: 24
---

# Ruling: M04 PR 2, Data Owner

Drafted by the session; the human rules as Data Owner before the merge.
The retirement itself was ruled by the human on 2026-09-27, before tool
grounding landed ("Retire, add nothing").

## 1. `g-021` is retired, and nothing is added (`open.md` row 5)

`g-021` asks whether the sequel "Brackenfield Nine: The Tenth" may be
published on SVOD in the US. The table has no US SVOD row for `t-004`,
so `check_availability` answers `found: false`, `row: null`, with
`ML-2.1` its only candidate. The golden expects the original's row
`r-011` and `ML-2.3`, and `exclusive: false` against `r-011`'s `true`
(`data-owner` F3, F4 on M04 PR 1). Under tool grounding it can never
pass, and it never has.

- Retired at M04 with two keys, this file and the Threshold Owner's, as
  `g-012` was at M02 PR 2. The file stays; its `expected` is untouched;
  the id is never reused (R11).
- Nothing replaces it here. A trap where no row governs needs a golden
  form with no `table_row`, which SPEC/00 §6 does not have; that
  amendment, with the reader that grounds a `found: false` call, is
  M06's, carried into M05's `open.md` at M04's close.
- The expected line is restated before PR 2's run (`data-owner` F16):
  ordinary 9/9, traps 2/2 live, no new id in `never_passed`.

## 2. Grounding does not check the call's input (`data-owner` F5 on PR 1)

Ruled with `g-021`, as SPEC/04 §2 said it would be: **no input check at
M04.** `check_availability` finds a row by its key (title, territory,
platform), so a successful call that returned the answer's row named
that row's title, territory and platform. A call on the wrong title
grounds only an answer that cites the wrong title's row. That answer's
fields are then compared with the golden's, which is where it fails.
What grounding does not catch, and nothing at M04 does: an answer that
cites a row other than the golden's `table_row` with the golden's
fields; `score` compares fields and checks that the row exists and that
the tool returned it, not that it is the expected row. Recorded for the
Data Owner at M06, with the absence form.
