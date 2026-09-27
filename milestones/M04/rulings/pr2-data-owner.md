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
Both rulings below were made by the human on 2026-09-27: the retirement
before tool grounding landed ("Retire, add nothing"), and F5 on the
`data-owner` report on this PR ("Require the golden's row").

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
  M06's, carried into M05's `open.md` at M04's close. The Tool Owner's
  question on it (whether a not-found result offers `ML-2.3`; M02
  `pr2-data-owner.md` (b)) goes with it (`data-owner` F3 on this PR). The
  second key is the Threshold Owner's, as at `g-012`: the Tool Owner owns
  no path this retirement touches.
- The expected line is restated before PR 2's run (`data-owner` F16):
  ordinary 9/9, traps 2/2 live, no new id in `never_passed`.

## 2. Grounded on the golden's own row (`data-owner` F5 on PR 1 and on this PR)

An agent's ordinary or trap answer is correct only when it is grounded
**and** its `table_row` is the golden's `expected.table_row`. Agent only;
the control is scored as at `m00`. The row only, not the clause: M04 PR
1's answers cite another clause than the golden's in 7 of 11, and the
clause is the agent's to choose among the tool's candidates.

Why: `check_availability` finds a row by its key, so a successful call
names the title, territory and platform of the row it returns, and the
call's input need not be read. But grounding alone accepted an answer
that cites the row it was given, and a call on the wrong title gives the
wrong row: `g-001` answered from a call on `t-001` (`r-001`) has
`g-001`'s fields and a clause the tool offered, and passed. Now it does
not (`tests/test_build.py`).

What it changes: nothing on record. M04 PR 1's eleven citing answers
(CI run 36331360122's raws) all cite the golden's row. The expected line
stays ordinary 9/9, traps 2/2.
