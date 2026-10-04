---
# M08 PR 1 (#45), Engineering's key over the Engineering paths this PR
# touches: the seed fixtures and run files, SEEDS_M08, the seed tests, and
# the fixtures README. No reader is in this PR (that is PR 2). The cold
# review runs from PR 2 (R9); this is the open ruling for the Engineering
# paths, as M07 PR 1's pr1-engineering.md was.
ruling: pr1-engineering
seat: Engineering
authorises:
  - tests/fixtures/m08/**
  - tests/test_m08_seeds.py
  - tests/fixtures/README.md
  - src/verdict/plants.py
evidence:
  - SPEC/08-game-day-drill.md#5-the-seeded-cases
  - milestones/M08/feasibility.md
  - milestones/M08/rulings/pr1.md
pr: 45
---

# Ruling: M08 PR 1, Engineering

Ruled by andaro74 as Engineering, 2026-10-04, as written.

## What this covers

The seeds and their tests, planted before any reader (`e5266cc`):

- **S1, the hostile copy** (`tests/fixtures/m08/s1-hostile-copy/`): a
  faithful mini-agent with the six attempts in `agent.py` — a3 in the
  tool wrapper (inside the answer), a1, a2, a4, a5, a6 in
  `_attempts_after_the_answer`, each with a 5 s timeout, all inside one
  try/except, so a hanging connect cannot make the answer record
  UNMEASURED (BLOCK 2 on SPEC/08). `evaluate()` admits it — verified in a
  worktree through M06's stand-in lookup — which the guard test holds.
  Its two goldens carry the Data Owner's seat (SPEC/08 §11 R7); the
  fixture folder is under `tests/**`, Engineering's, and carries that
  Data Owner ruling, as `agents/<name>/**` is split by field today.
- **S2–S7** (observation fixtures): each read by a function
  `src/verdict/drill.py` adds at PR 2 (`run1`, `run2`, `run3`,
  `evidence`, `quarantine`). The module is not in the tree; the fixture
  tests fail on that, which is the planted failure. Each reader's shape
  is `{read, held, reasons}` (`run1` also `{refused, recorded}` counts);
  `run3` records both goldens' `pass` and gates on the verdict alone
  (finding 3); `evidence` names which of its cases came from an attempt's
  record and which from the sweep for unnamed refusals (finding 9).
- **The three run files** (`milestones/M08/runs/drill_run{1,2,3}.yaml`,
  Product's under `milestones/**`): `observed: null`, read by
  `scripts/observe_drill.py` after PR 2 merges. Their tests stay expected
  failures until each run is recorded.
- **`SEEDS_M08`** in `src/verdict/plants.py`: the ten entries, listed by
  `make plants` with `drill.py` "not in the tree yet" beside S2–S7.

`tests/test_m08_seeds.py` shows 3 passed (S1's guards) and 9 xfailed;
`--runxfail` shows 3 passed, 9 failed, each with its planted message
(`feasibility.md` §3). `git show e5266cc --stat` shows the seeds, the
tests, the README rows and `SEEDS_M08`, and no reader.

## For PR 2 (the names this PR fixes)

PR 2 adds `src/verdict/drill.py` with `run1`, `run2`, `run3`, `evidence`
and `quarantine`; `scripts/observe_drill.py`; `drill` on the envelope and
in `src/verdict/schema.json`; `CLAIM_8_CHECKS` and `READ_THE_DRILL` in
`src/verdict/gate.py`; row 8's reading in `src/ledger.py`; and the
observer's step in `evals.yml` (Security). The cold review
(`engineering-cold-reviewer`) runs from PR 2 (R9).

## Unsure

- Whether `run1` should return `refused` and `recorded` as counts (n of
  6, m of 6) or as the per-attempt lists the ledger cell quotes;
  proposed: both, the counts for the cell and the lists for the reasons.
  Engineering, PR 2.
