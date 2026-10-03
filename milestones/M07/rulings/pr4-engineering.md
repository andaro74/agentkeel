---
# M07 PR 4 (#44), the close, Engineering's key, with the cold review of
# origin/main...b310735 (18 files) and what was done with it. The close
# builds no reader.
ruling: pr4-engineering
seat: Engineering
authorises:
  - tests/test_bootstrap.py
  - tests/test_containment_stacks.py
  - tests/test_m06_seeds.py
  - tests/test_m07_readers.py
  - tests/test_m07_seeds.py
  - tests/test_m07_workflows.py
evidence:
  - SPEC/00-overview.md#8-M07
  - milestones/README.md
  - milestones/M07/README.md
  - milestones/M07/runs/pr4_expected.md
  - milestones/M07/rulings/pr3-engineering.md
pr: 44
---

# Ruling: M07 PR 4, Engineering

DRAFT for andaro74 as Engineering. Not ruled until this line is replaced by one that starts with the two words the gate reads.

## What this authorises

Tests only. Nothing under `src/`, the `Makefile`, `pyproject.toml` or
`agents/` changes in this pull request, and no observer or reader is
built or changed: the close reads the attempts with PR 2's and PR 3's
code.

- `tests/test_bootstrap.py`: the execution role holds two actions on
  `runtime/*` in one statement with no condition, and on `Resource: "*"`
  no runtime action but `CreateAgentRuntime`.
- `tests/test_containment_stacks.py`: the observer's put role trusts the
  environment's subject, and `observe.yml`'s job names that environment.
- `tests/test_m07_workflows.py`: `platform-check.yml` has no dispatch
  input and no relaxation step (item 13n).
- `tests/test_m07_readers.py`: three tests of `relax_seed` run against a
  tree where the attempt is not yet recorded (`not_yet_made`), and one
  holds that the tree itself refuses a second attempt.
- `tests/test_m07_seeds.py`, `tests/test_m06_seeds.py`: five run-file
  markers off, each in the commit that wrote its `observed` entry (S0,
  S1, S2, S3 of M07; S3 of M06). S1's test counts one entry per
  repository the run file names and holds `owner-check` among them.

**A run-file test passing is not its falsifier held.** Each passes
because a human-filled entry exists. The readings are `build`'s, on the
envelope of this pull request's run.

## The cold review (`engineering-cold-reviewer`, `origin/main...b310735`): BLOCK 1, FINDING 10, NOTE 12

| # | Finding | Status |
|---|---|---|
| B1 | `pr4-security.md` and `pr4.md` are cited and not in the tree; three deploys preceded them | **Repaired**: both files are in this pull request and say the deploys came first (`pr4-security.md` item 1). Each is ruled by its own first line, not here |
| F1 | Shape: the close carries three repairs | **Said**: `pr4.md`. No reader is built. Each repair was needed by a live attempt and had no other pull request |
| F2 | 13n and the fourteen tests promised "in the close" and not in the diff | 13n **done** (`e0345b0`, `660a0e6`). The fourteen tests **carried** to `milestones/M08/open.md` row 15; the record that said "in the close" is corrected (`runs/pr4_expected.md`, "After the cold review", item 5) |
| F3 | Attempt 1's statement was edited after the attempt began | **Said** in the same section, item 1. The expected readings were not touched. The list it promised is still owed (M08 row 26) |
| F4 | The timed values were measured with the owner starting the platform's jobs | **Said**, item 2 there, and in the close detail: the values are what the platform took once started, and "as stated, every line" is withdrawn. M08 row 18 |
| F5 | S1's seed test passed on empty input | **Repaired** (`660a0e6`): it holds `agentkeel-studio/owner-check` named |
| F6 | Row 7 says F7.3 is read on `owner-check`; it was read on `window-check` | **Product's**: an amendment to row 7, shown to the seat before it is written (`pr4.md`) |
| F7 | The relaxation "waits" for the App's viewpoint and is read without it | **Repaired**: the sentence was wrong; SPEC/07 §12 and the README are corrected |
| F8 | The cdk-nag reason | **Repaired** (Security, `e0345b0`) |
| F9 | `runs/pr2_by_hand.md` contradicts itself; a hash missing | **Repaired** but for the security account's stored hash, owed by hand (`pr4-security.md` item 8) |
| F10 | The first bootstrap deploy's diff not kept; the comparison not re-makeable | **Part**: the comparison is a script with both hashes (`runs/b2_cdk_diff.md`). The first diff is lost and said so |
| N1 | Each statement was pushed before its attempt | Stands. Attempt 2's push time corrected to 03:41:38Z |
| N2 | `78aac19` is `d79915c` amended for its author | Recorded in `milestones/M07/README.md` |
| N3 | `not_yet_made` does not weaken the three tests | Stands |
| N4 | Five markers are off, not four | Corrected above |
| N5, N6, N7 | No reader built; P5 holds; no "governed", "secure" or "proven" | Stand |
| N8 | The bootstrap test claimed "only" and held less | **Repaired** (`660a0e6`) |
| N9 | The environment's branch policy is read by no test | Stands: it is a GitHub setting, read back by the grant's reader on each keyed run |
| N10 | The arithmetic agrees | Stands |
| N11 | Attempt 1's expected F6.1 was "held"; the record says not held on the first commit | The expectation is left as written; the envelope decides |
| N12 | "yours to rule"; the `sorted()` finding in one place | Said in the appended section; M08 row 16 |

**Not read cold again:** the repairs after this review (`e0345b0`,
`660a0e6`, `b81dced`) and everything the close writes after the
envelope. `milestones/M08/open.md` row 23.

## What a reader can run

```
uv run pytest -q                                      # the whole suite
uv run pytest -q tests/test_m07_seeds.py tests/test_m06_seeds.py   # every run-file marker off
git diff origin/main...HEAD --stat -- src/ Makefile agents/        # nothing
git diff d79915c 78aac19                              # empty: the amend changed the author only
```
