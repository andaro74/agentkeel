---
# M02 PR 1 (#11), Engineering's key. Product's file is rulings/pr1.md,
# Security's is rulings/pr1-security.md.
ruling: pr1-engineering
seat: Engineering
authorises:
  - tests/test_bootstrap.py
  - tests/test_m02_seeds.py
  - tests/fixtures/m02/**
  - tests/fixtures/README.md
  - src/verdict/plants.py
  - src/verdict/gate.py
  - .gitattributes
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#5-the-seeded-cases
  - milestones/M02/open.md
pr: 11
---

# Ruling: M02 PR 1, Engineering

Drafted by the session; the human rules as Engineering before the merge.

## The seeds (`tests/fixtures/m02/`, `tests/test_m02_seeds.py`)

Five seeds, six patches and run files, six tests, all `xfail(strict=True)`
until each reader lands at PR 2. A seed is a unified diff applied to a
detached worktree by the test's `seeded` fixture and removed after. The
patches are `-text` in `.gitattributes` so a Windows checkout keeps them
LF; `git apply` matched on this machine in a worktree before the first
seed was committed. The API names the tests import (`src.gates.two_key`,
`src.gates.ruling_cited`, `checks.check_edges`,
`checks.check_golden_ids_against`) are what PR 2 provides; if they land
under other names, PR 2 changes the call and never what a seed adds or
removes.

`g-099` is burned (R11); `tests/fixtures/README.md` says so.

## `tests/test_bootstrap.py` (open.md row 9)

`NEEDED_BY_PROPERTY` and
`test_no_construct_resource_needs_an_action_the_deploy_boundary_denies`.
Fails at `25b2743`, on the table, for `kms:CreateGrant`; passes at
`9ea6405`. Its three rows are from the same handler permissions
`NEEDED_BY_TYPE` was read from; the Kinesis and import rows are there so
the table is not a table of one, and neither fires on the template.

## `src/verdict/plants.py`, `src/verdict/gate.py`

`SEEDS_M02` and `SEEDS_BY_MILESTONE`; `--plants` prints each milestone's
seeded cases under its SPEC section. Listing reads nothing and gates
nothing; the gate's verdict code is untouched.

## What Engineering does not do here

No `src/gates/`, no `validate` change, no `scripts/observe_pr.py`, no
change under `src/baseline/` (ADR-0002), no envelope written or read by
anything but `build` and `gate`.
