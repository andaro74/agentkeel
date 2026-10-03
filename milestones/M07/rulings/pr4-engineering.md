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
  - tests/test_m07_observer.py
  - tests/test_m07_readers.py
  - tests/test_m07_seeds.py
  - tests/test_m07_workflows.py
evidence:
  - SPEC/00-overview.md#8-M07
  - milestones/README.md
  - milestones/M07/README.md
  - milestones/M07/runs/pr4_expected.md
  - milestones/M07/rulings/pr3-engineering.md
  - https://github.com/andaro74/agentkeel/actions/runs/37149475766
  - evals/history/dee74c3cf4102bfb6d4315faafb161c154618ed9.json
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

- `tests/test_m07_observer.py`: the test of "the run files as they
  stand" now holds that every attempt is named and looked up. **It was
  red on the close's first run** (37147871497, on `84dc913`): it still
  held that two attempts were named, the entries had been written since
  `87bbb50`, and the session pushed without having read the suite to its
  end (its command piped `pytest` through `tail`, and the exit code it
  saw was `tail`'s). The gate ruled that run's envelope GREEN; the
  `evals` job and `checks` failed on this one test. Repaired after the
  envelope, so the next run measures again.

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

## The second cold read (`b310735...d653c7d`, 26 files): BLOCK 0, FINDING 5, NOTE 18

It read the repairs after the first review, the test repair and the
close's text, and rebuilt row 7's cell from the envelope by the gate's
own format: byte-identical in both READMEs.

| # | Finding | Status |
|---|---|---|
| F1 | A third hand number (32,260 for 32,264) | **Repaired**: the close detail says three; SPEC/07 §12 and the README give both numbers; `runs/pr4_expected.md` item 9 |
| F2 | "Measured once" against two runs on #43 | **Repaired**: the attestation and the explainer say one pull request, two runs |
| F3 | #44's Unsure items had no home in the tree | **Repaired**: `pr4.md` section 7 |
| F4 | Whether `m07` is tagged was cited to a file that did not say | **Repaired**: `pr4.md` section 8 puts it to Product with both options |
| F5 | The explainer named the deploy role | **Repaired**: "the role the platform creates agents with" |
| N2 | The cap cell lost its pointer to the ruling | Stands: `rulings/grant-ids.md` ruled the cell reads `5 / 4`; the pointer is in the close detail |
| N3 | The workflow's comment cites `pr2-security.md` 13n, not `pr4-security.md` | Left: another edit to the workflow is a measured path. `infra/workflows.sha256` names `pr4-security.md` |
| N4, N5, N6, N7 | Four tests hold less than they could (the relax search covers one job; S1's pull numbers; `Resource: ["*"]`; a stale docstring and an unused helper) | **Carried**: `milestones/M08/open.md` row 23. A test change measures again |
| N8, N9, N15 | "Three ways" against four conditions; the seed-test condition's wording; "first live read" | **Repaired** in the close detail |
| N10, N16, N17 | "Five hours"; two dates for the Apps; the statement in #44's body is not in the tree | **Repaired**: `runs/pr4_expected.md` items 9 to 11; the by-hand table says whose clock; `pr4.md` section 2 |
| N11 | M08's `open.md`: "M08" alone as a date; copied rows keep older row numbers | **Said** in that file's header; M08's open rules each |
| N12 | "Not read cold again" was stale | This table |
| N13, N14 | The read-back's file name and ceiling; the stored template differs at the head | **Repaired**: `docs/video/README.md`; `attestations.md` line 2 |
| N1, N18 | `make ledger` not run by the reviewer; the close's shape | `make ledger` exits 0 as run by the session (`pr4.md`); the shape stands as said |

**Not read cold:** the repairs after the second read (prose only: no
file under `tests/`, `src/`, `infra/`, `scripts/` or `.github/`), and
whatever the human commits when ruling. `milestones/M08/open.md` row 23.

## What a reader can run

```
uv run pytest -q                                      # the whole suite
uv run pytest -q tests/test_m07_seeds.py tests/test_m06_seeds.py   # every run-file marker off
git diff origin/main...HEAD --stat -- src/ Makefile agents/        # nothing
git diff d79915c 78aac19                              # empty: the amend changed the author only
```
