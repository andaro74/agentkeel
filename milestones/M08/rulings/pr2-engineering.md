---
# M08 PR 2, Engineering's key and the cold review, one file. Drafted from
# engineering-cold-reviewer's read of the diff 1083722...HEAD (commits
# 91be2c2, 68bfd58) and row 8 only. The one FINDING was repaired after it
# (the dead-constant fold), which the reviewer did not read cold again — it
# touches no measured path and no envelope exists for this PR yet.
# Product's file is rulings/pr2.md; Security's is rulings/pr2-security.md.
ruling: pr2-engineering
seat: Engineering
authorises:
  - src/verdict/drill.py
  - scripts/observe_drill.py
  - src/verdict/build.py
  - src/verdict/gate.py
  - src/verdict/schema.json
  - src/ledger.py
  - src/verdict/__init__.py
  - Makefile
  - tests/test_m08_seeds.py
  - tests/test_p5_disagree.py
  - tests/test_cost_cap_and_ledger.py
  - tests/test_gate.py
evidence:
  - SPEC/00-overview.md#8-M08
  - SPEC/08-game-day-drill.md
  - milestones/README.md
  - milestones/M08/README.md
  - milestones/M08/feasibility.md
pr: 46
---

# Ruling: M08 PR 2, Engineering

Ruled by andaro74 as Engineering, 2026-10-04, as written.

## What this covers

The instrument that reads the game-day drill, no control (ADR-0013;
SPEC/08 §4, §6):

- **`src/verdict/drill.py`** (new): `run1`, `run2`, `run3`, `evidence`,
  `quarantine` — the five readers the seed tests fix — plus `record` for
  `build`. `run1` counts refused n of 6 and recorded m of 6, and reads each
  attempt's refusal from its own record (`refused_from_record`), never the
  observer's `refused` field (P5).
- **`scripts/observe_drill.py`** (new): reads the three run files and the
  audit bucket as `agentkeel-audit-read`; writes raw records, rules nothing.
- **`build --drill`**, the optional envelope field `drill`, and its schema
  (`additionalProperties: false`).
- **`gate.py`**: `CLAIM_8_CHECKS` (F8_1..F8_5, test-only witnesses),
  `READ_THE_DRILL`, `drill_misses`/`drill_reading`; `measured()` and
  `measured_at()` read `drill` for row 8. `M08_READERS` is set in the commit
  after the one that wired the checks, as M05/M06/M07 were.
- **`src/ledger.py`**: row 8 joins the reading-row union.
- **`Makefile`**: the five F8 case lists and `DRILL_OBS`.
- **tests**: the six S2..S7 markers come off (their reader landed); the three
  run-file tests stay xfail until the runs are made; P5 cases for the new
  checks; the row-4 guard (test_cost_cap_and_ledger) points at a neutral
  milestone and test_gate's exhaustive required_checks(HEAD) assertion adds
  CLAIM_8_CHECKS, since M08 reads the drill now.

## The cold review (engineering-cold-reviewer): 0 BLOCK, 1 FINDING, 7 NOTE

The report is pasted in the PR body verbatim.

| # | Finding | Status |
|---|---|---|
| 1 | `gate.DRILL_RUNS` and `drill.READERS` were dead constants that duplicated the run list the loops hard-coded | **Repaired** (commit after the review): `drill_misses` and `drill_reading` iterate `DRILL_RUNS[1:]`; `drill.READERS` deleted. The named run set now drives the loops, so a run added to it reaches them. |

The seven NOTEs, recorded:

- **The plant goes RED mechanically, in the diff.** The three run files carry
  `observed: null`, so `drill.record` returns each run not made and
  `drill_misses` forces row 8 RED even on a GREEN run; a test asserts it
  (`test_cost_cap_and_ledger.py`). The live 4/6, 5/6 reading is the owner's
  by-hand run, read before close (below).
- **P5 holds.** The observer records and rules nothing; `drill` re-derives each
  refusal from AWS's record; `test_p5_disagree.py` proves build overrides a
  lying observer and the gate overrides a GREEN build with no F8 checks.
- **The quarantine hazard mapping.** `drill.quarantine` maps "no refused call
  in the window" to `read: True, held: False` with a reason that says "unread".
  Intended: S7's fixture test fixes `held is False`, and the ledger F8.5 text
  reads it as the hazard (RED, as M05's S7 closed). The field is `held: False`;
  "unread" is the reason, not a `read: False`.
- No edit under `src/baseline/`, `evals/goldens/`, `evals/history/`,
  `thresholds.yaml`, `rules/`, `data/`, or a manifest id. No "governed",
  "secure" or "proven" about an unfired control.

## Outstanding, read before close (not in this diff)

Row 8's Measured cell is still `—`. The live reading — **refused 4 of 6,
recorded 5 of 6**, row 8 RED on a2 (unread) and a3 (not refused), SPEC/08 §7 —
comes from the owner's by-hand run 1 after the reader is on the branch, read by
PR 2's run (its evidence by PR 3's). The in-repo evidence guarantees RED on the
`observed: null` plant; it does not yet record the live counts. PR 3/PR 4 record
the runs and close the cell (SPEC/08 §5.1).

## What a reader can run to falsify this PR's claims

```
uv run pytest tests/test_m08_seeds.py -q              # 9 passed, 3 xfailed (the run files)
uv run pytest tests/test_m08_seeds.py -q --runxfail   # 9 passed, 3 failed (runs not made)
uv run pytest tests/test_p5_disagree.py -q            # the P5 cases, incl. the M08 ones
make validate                                          # twenty checks, ok (incl. the evals.yml hash)
uv run python -c "import json; from src.verdict import drill; \
  print(drill.run1(json.load(open('tests/fixtures/m08/s3-attempt-answered/observation.json')), 600.0))"
# refused 3, recorded 5, held False, names a4: a reader that passed everything would fail S2..S7
git diff ddfa684...HEAD -- infra thresholds.yaml rules evals/goldens data src/baseline   # empty: no control
```

Any seed test that passes for a reason other than its reader, or a `drill`
field the gate rules on (it must not — recorded only), makes this PR wrong.
