---
# M04 PR 1 (#23), the Data Owner's key. Product's file is rulings/pr1.md.
ruling: pr1-data-owner
seat: Data Owner
authorises:
  - evals/goldens/v1/g-015.yaml
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md
  - milestones/M04/feasibility.md
pr: 23
---

# Ruling: M04 PR 1, Data Owner

The rulings below were made by andaro74 as the Data Owner, on 2026-09-26
and 2026-09-27, each "as proposed". This file was drafted by the session
from them; the human signs it off before the PR opens. The `data-owner`
reports (0/7/10 on the tree at `74fb9ed`; 0/3/4 on the diff at `688634c`)
are in the PR body verbatim.

**`evals/goldens/v1/g-015.yaml`**: line 1, a comment only, names the rule
the plant is for, `sending-terms-to-a-competitor` (`open.md` row 4;
`6dc922f`). The id, the question, `expected`, `seat`, `added` and
`retired` are unchanged. Not a retirement and not a relaxation. No file
under `data/**` changes.

**Tool grounding is part of CORRECT from PR 2** (finding 4 on SPEC/04):
an ordinary or trap answer passes only when its `table_row` is the `row`
of a successful `check_availability` call in the same answer and its
`clause_id` is among that call's candidates. SPEC/00 §9 is amended to say
so (`data-owner` F11). Grounding does not check that the call's input
names the question's title, territory and platform; whether it must is
ruled with `g-021` at PR 2 (F5).

**Held for PR 2 by this seat, with the Tool Owner:** `g-021` cannot pass
grounded as written: its call returns `found: false`, it expects the
original's row `r-011` with `exclusive: false` against that row's `true`,
and the tool offers `ML-2.1` where it expects `ML-2.3` (F3, F4, N5).
Keeping it as written under today's grounding is ruled out; retire with
two keys and re-add, or keep it with a changed reader, before the reader
lands. If it is retired, the expected trap line is restated before PR 2's
run. The 9/9 and 2/3 counts were never grounded; PR 2's run is their first
measurement (F7).

**Held for M06:** the answer-side overlap for `g-010`, the first row of
M06's `open.md`, ruled before retrieval lands (`open.md` row 3; note 14);
the fourteen corpus clauses outside the clause index (row 18).
