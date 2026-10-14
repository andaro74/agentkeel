---
# M10 PR 1 (#54), Engineering's key over the Engineering paths this PR
# touches: the seed fixtures, SEEDS_M10, the seed tests, the ledger test's
# row count, and the fixtures README. No reader is in this PR (that is
# PR 2). The cold review runs from PR 2 (R9); this is the open ruling for
# the Engineering paths, as M09 PR 1's pr1-engineering.md was.
ruling: pr1-engineering
seat: Engineering
authorises:
  - tests/fixtures/m10/**
  - tests/test_m10_seeds.py
  - tests/test_cost_cap_and_ledger.py
  - tests/fixtures/README.md
  - src/verdict/plants.py
evidence:
  - SPEC/10-public-caller.md#5-the-seeded-cases
  - milestones/M10/feasibility.md
  - milestones/M10/rulings/pr1.md
pr: 54
---

# Ruling: M10 PR 1, Engineering

DRAFT. Becomes a ruling when the line below reads "Ruled by".

## What this covers

The seeds and their tests, planted in one commit before any reader
(`fba41ad`):

- **S1, the call records** (`tests/fixtures/m10/s1-call-records/`):
  `record_no_caller.json`, today's answer record for festival-desk with
  every field `compose_answer` writes (sixteen) and no caller; and five
  records in SPEC/10 §2's read shape: `call_stranger_answered.json`,
  `call_bypass.json`, `call_wrong_subject.json`, `call_refused_late.json`
  (601 s), `calls_held.json` (the four as stated). Reader:
  `src/verdict/caller.py` `calls(records, stated, callers, max_seconds)`,
  not in the tree. One planted test over all six.
- **S2** (`s2-manifest-no-callers/`): `manifest.yaml`, festival-desk's as
  its repository holds it at `19864419`, read from GitHub on 2026-10-13
  and copied unchanged under its comment; `with_callers.yaml`, the same
  with one subject. Readers: `src/validate/callers.py` `callers_errors`,
  not in the tree; `src/manifest/schema.json`, whose
  `additionalProperties: false` refuses the key today. Two planted tests.
- **S3** (`s3-caller-added/cases.json`): refagent's manifest with
  `callers: []` as a base, a subject added or the key removed with the
  Tool Owner's ruling alone, in a repository built as
  `tests/test_m07_two_key_seed.py` builds its. Reader: `two_key.py`'s
  entry 7, not there. Two planted cases and one guard case.
- **S4**: two guards, no fixture: the fixture agent's stack (M09's
  `s1-festival-desk/`, through `tests/test_m09_platform.synth`) conditions
  both `InvokeModel` allows on its own guardrail at its version and its
  runtime carries no `AuthorizerConfiguration`; the latest CI-written
  envelope reads `plants_expected` 7, `plants_fired` 7, GREEN. The first
  guard's authoriser line is rewritten at PR 2 when the door is added,
  not deleted: it then asserts the authoriser is the pool's.
- **The run file** (`milestones/M10/runs/f10_x_caller_run.yaml`, Product's
  under `milestones/**`): `observed: null`, three preconditions and four
  calls named, read by `scripts/observe_caller.py` after PR 2 merges.
- **`SEEDS_M10`** in `src/verdict/plants.py`: five entries, listed by
  `make plants`; `CONTROLS` unchanged. S3 and S4 read "in the tree" there
  because their readers are files that exist and change at PR 2; the
  strict markers say which seeds are read.
- **`tests/test_cost_cap_and_ledger.py`**: the ledger's row count, ten to
  eleven, for row 10.

`tests/test_m10_seeds.py` shows 3 passed, 6 xfailed; `--runxfail` 3
passed, 6 failed, each with its planted message (`feasibility.md` §3).
The full suite passes with the row count bumped. `git show fba41ad
--stat` shows the seeds, the tests, the README rows and `SEEDS_M10`, and
no reader.

## For PR 2 (the names this PR fixes)

`src/verdict/caller.py` with `from_raw(event)` and `calls(records, stated,
callers, max_seconds)` returning `{read, held, admitted, refused,
expected_admitted, expected_refused, reasons}`, the reasons carrying
"names no caller", "does not admit", "without the door", "other than the
one that called" and "later than"; `src/validate/callers.py` with
`callers_errors(manifest)` naming `callers`; `callers` in
`src/manifest/schema.json`; `two_key.py`'s entry 7 whose refusal names
`<path>: callers` and "ADR-0009 amendment 2"; `scripts/observe_caller.py`
(matched by CODEOWNERS' `observe_*.py` line); `caller` in
`src/verdict/schema.json`; `CLAIM_10_CHECKS` and `READ_THE_CALLER` in
`gate.py`; row 10's reading in `src/ledger.py`; the raw record fixture
from the probe as PR 2's first commit; the door as Security rules. The
cold review (`engineering-cold-reviewer`) runs from PR 2 (R9); its report
on this PR's diff is in the PR body.

## Unsure

- Whether `calls` takes the run file's `stated` steps directly or a
  dict the observer derives from them; proposed: the dict, so the reader
  never opens a Product file. Engineering, PR 2.
- Whether the S4 synth guard, which runs the construct's app in a
  subprocess (about 20 s), should share `test_m09_platform.py`'s
  module-scoped template rather than synthesise again; proposed: share it
  at PR 2 if the suite's time matters, since both read the same fixture.
  Engineering, PR 2.
- `test_m10_seeds.py` imports `SeedBroken` for the docstring's sake and
  marks it `noqa: F401`, as M09's test did without the marker (M09
  finding 17). Engineering; stands.
