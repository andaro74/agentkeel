---
# M01 PR 4 (#10), Engineering's key. `pr4.md` is Product's and carries the
# same `pr`.
ruling: pr4-engineering
seat: Engineering
authorises:
  - src/ledger.py
  - tests/test_cost_cap_and_ledger.py
  - tests/test_adr0007.py
  - milestones/M01/rulings/pr4-engineering.md
evidence:
  - SPEC/00-overview.md#8-M01
  - milestones/M01/rulings/pr4.md
pr: 10
---

# M01 PR 4 — Engineering's key: the ledger applies SPEC/00 §7

**The rule, and what was missing.** SPEC/00 §7 says: "A milestone that
closes without a measurement is RED, never GREEN". `check_measured`
applied that to an empty cell only. From M01 PR 3, the gate can read a
cell as UNMEASURED: a claim read in the runtime, from an envelope that did
not run there (PR 3 cold review, B1). The check then required the State to
equal that verdict, so RED was refused beside it and only UNMEASURED was
accepted, which is the "UNMEASURED-and-quiet" close the skill forbids.

**The change.**
- A cell whose verdict is UNMEASURED may stand beside State RED, and never
  beside GREEN, the same rule as the empty cell. Other states (OPEN) pass,
  as before.
- `make ledger` prints the row-aware reading, "as row M01 reads it", after
  the envelope's own. That was the inventory's NEW-3: the line a close copies
  was the row-unaware one, and for row 1 it said GREEN.

**Tests.**
- `test_a_row_read_as_unmeasured_closes_red_and_never_green`, on the real
  envelope `e97125e`.
- `test_row_1_cannot_close_green_on_a_runner_envelope` (`test_adr0007.py`)
  now matches the new refusal's words. GREEN is refused, as before, and the
  message says why.

**What it touches, and what it does not.** `src/ledger.py` only. The gate,
`build`, the runner and the workflows are unchanged, so no envelope reads
differently. Only the ledger's rule for which State may stand beside a
reading changed. That is also why it departs from half of `pr3-cold-review.md`
finding 9's condition: the condition guarded runtime mode, and this change
cannot make a runner envelope read as the runtime.
