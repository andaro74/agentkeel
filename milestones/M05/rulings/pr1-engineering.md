---
# M05 PR 1 (#30), Engineering's key and the cold review, one file. Drafted
# by engineering-cold-reviewer from the diff 4206edf...cc36e31 and row 5
# only; repaired and completed by the session. Product's file is
# rulings/pr1.md, Security's rulings/pr1-security.md.
ruling: pr1-engineering
seat: Engineering
authorises:
  - src/verdict/plants.py
  - tests/test_m05_seeds.py
  - tests/test_evals_workflow.py
  - tests/fixtures/README.md
  - tests/fixtures/m05/**
  - Makefile
evidence:
  - SPEC/00-overview.md#8-M05
  - SPEC/05-containment-and-evidence.md
  - milestones/README.md
  - milestones/M05/README.md
  - milestones/M05/feasibility.md
pr: 30
---

# Ruling: M05 PR 1, Engineering, with the cold review

Drafted by the session; the human rules as Engineering before the merge.

The dispositions below were ruled by andaro74, 2026-09-28, "as
proposed" (`feasibility.md` §2.5).

## What was read

`engineering-cold-reviewer` read the diff `4206edf...cc36e31` (28 files)
and row 5 of `milestones/README.md`, and not the PR description. It ran
`uv run pytest tests/test_m05_seeds.py --runxfail -q` (7 failed, each at
its planted line), `make validate` (16 ok), `make plants` and `make
ledger` (exit 0), and the suite on a clean `git archive` export. 1 BLOCK,
3 FINDING, 5 NOTE, verbatim in the PR body.

## What holds

- Every seed commit (`142a2a9` to `06f95d9`) is its run file or fixture,
  its test, one row of `tests/fixtures/README.md` and one line of
  `SEEDS_M05`, and no reader: none touches `server.py`, `build.py`,
  `gate.py`, `thresholds.yaml`, `infra/**` or `agents/**`. All seven come
  after the SPEC (`11490e0`). Nothing makes claim 5 pass.
- S5's fixture differs from `tests/fixtures/m04/s3-a.json` only in
  `g-001`'s `parsed`, `text` and `tool_calls`, and carries only AWS's
  documented example key pair.
- No envelope is written or read by anything in the diff; S5 builds and
  rules under `tmp_path` with M04's harness.
- The swap read's removal breaks nothing: `build` writes `swaps` only with
  `--swaps`; `READ_THE_SWAPS = {"M04"}`; row 4's cell is checked against
  its own envelope (`05bd718`).

## Dispositions

| # | Finding | Status |
|---|---|---|
| B1 | Security's paths changed with no Security ruling on the head; R5's two keys cited and absent | **Repaired**: `pr1.md`, `pr1-security.md` and this file, `pr: 30`, in the PR; each ruled by its seat before the merge, checked on the pushed head |
| F1 | The attempt tests did not read each attempt's own `refused_when` | **Repaired** (`e38747b`, before any reader): matched by position and `event_name`; S1 REJECT and no connection, S2 a resource-based policy, S3 an explicit deny, S6 Object Lock for the two object actions, S7 refagent's own role as the principal denied |
| F2 | `F5_4` could not be witnessed on PR 2's run; attempt tests turn a hand-filled file into a check | **Ruled** (Product): `CLAIM_5_CHECKS` is `F5_1` alone, from S4's and S5's tests; F5.2 to F5.4 live only, read by row 5 (`f8b3e04`) |
| F3 | Prose stated refusals as seen for attempts not made | **Repaired** (`f8b3e04`) |
| N1 | Items beyond PR 1's list, each "at M05 open" | Recorded |
| N2 | `make ledger` will print "swap ... not read" for row 4 once the latest envelope has no `swaps` | **M05 PR 2** (Engineering): print row 4's reading for its own envelope only |
| N3 | Stale `evals.yml` comment | **Repaired** (`457e04b`, Security) |
| N4 | The untracked ruling folder fails an M02 seed test locally | Clears with this commit; re-run after it |
| N5 | "Only the planted line is an assert" was broader than the file | **Repaired** (`f8b3e04`) |

## What a reader can run

```
for c in 142a2a9 962ea72 bfd17c4 d1c1b0f f8601c3 b1dc6c4 06f95d9; do git show $c --stat; done
uv run pytest tests/test_m05_seeds.py -q              # 7 xfailed
uv run pytest tests/test_m05_seeds.py -q --runxfail   # 7 failed at their planted lines
uv run pytest -q                                      # the suite, the seven xfailed
make validate && make ledger && make plants
```
