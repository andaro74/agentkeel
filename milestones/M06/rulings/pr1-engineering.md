---
# M06 PR 1 (#34), Engineering's key and the cold review, one file. Drafted
# by engineering-cold-reviewer from the diff 0b96da4...4852e54 and row 6
# only; F1's repair re-read cold from 4852e54...4b8fb4e. Product's file is
# rulings/pr1.md.
ruling: pr1-engineering
seat: Engineering
authorises:
  - src/verdict/plants.py
  - tests/test_m06_seeds.py
  - tests/fixtures/README.md
  - tests/fixtures/m06/**
evidence:
  - SPEC/00-overview.md#8-M06
  - SPEC/06-developer-template.md
  - milestones/README.md
  - milestones/M06/README.md
  - milestones/M06/feasibility.md
pr: 34
---

# Ruling: M06 PR 1, Engineering, with the cold review

Ruled by andaro74 as Engineering, 2026-09-30, as written.

## What was read

**First read:** the diff `0b96da4...4852e54` (28 files, +1565 / -11),
commit subjects, row 6 of `milestones/README.md` and
`milestones/M06/README.md`. Not the PR body, not commit bodies.
**Second read:** the F1 repair, `4852e54...4b8fb4e` (2 files).

Run by the reviewer: `uv run pytest tests/test_m06_seeds.py -q`, 6 xfailed
at `4852e54` and at `4b8fb4e`; with `--runxfail`, 6 failed, each an
`AssertionError` with the message in `feasibility.md` §3; `python -m
src.verdict.gate --plants`; `python -m src.ledger`, exit 0;
`src.ledger.plain(rows())` equal to the committed
`docs/milestones/README.md`. Not run by the reviewer: `make validate`
(the cdk-nag synth, the live ruleset), run by the caller before the push.

## What holds

1. **Shape.** Only PR 1 material: SPEC/06 and SPEC/00 amended,
   `feasibility.md`, row 6 and its README, the explainer draft with "What
   happened" empty, five seeds, and M05's video and the security account's
   record carried from `open.md` rows 1 to 3. Nothing reads a seed:
   `panel_not_in_registry` and `observe_template` appear only in
   `SEEDS_M06`'s strings.
2. **One commit per seed, each with its test**: `672fc1d` S1a, `1a576f4`
   S1b, `0f3b977` S2, `b4eb959` S3, `06c485a` S4, each with its fixture or
   run file, its README row and its `SEEDS_M06` line; none touches
   `src/validate/` or `src/verdict/build.py`.
3. **Each test fails for its planted reason**, `xfail(strict=True,
   raises=AssertionError)`, preconditions `SeedBroken`.
4. **Row 6 matches the tree**: the seed hashes, 6 expected failures,
   `make plants` listing S1a to S4, `1 / 4`, `make ledger` exit 0, every
   seat in both manifests null.
5. **P5.** No envelope written or read; nothing under `evals/history/`.
6. **Frozen and owned paths.** Nothing under `src/baseline`, `evals`,
   `thresholds.yaml`, `rules`, `data`, `.github`, `infra` or `agents`.
   Every new path has a seat: Product (`SPEC/`, `docs/`, `milestones/`),
   Engineering (`src/`, `tests/`).

## Findings

| # | Finding | Status |
|---|---|---|
| 1 | Three seed assertions matched a substring in any check's error, so a new check refusing for another reason would have passed them | **Repaired at `df084ef`**: a refusal counts only from a check outside `BASE_CHECKS` (the sixteen names at `0b96da4`) whose name says what it reads; a base check refusing a fixture is `SeedBroken`. Re-read cold (`4852e54...4b8fb4e`) |
| 2 | `make plants` looks up S4's two readers as one path and can never print "in the tree" (`src/verdict/plants.py`, `SEEDS_M06["S4"]`) | **Open: Engineering, M06 PR 2**: a reader field of several paths, or one entry per reader |
| 3 | `rulings/pr1.md` was cited and not in the tree at `4b8fb4e` | **Repaired**: committed with this file |
| 4 | The S1 split is not enforced across the two tests: a check named for seats that refuses every new agent folder would pass S1a | **Open: Engineering, M06 PR 2**, with the readers: S1a's reader must not refuse S1b and S1b's must not refuse S1a. Today no check refuses either, so the assertions would test nothing (`feasibility.md` §4) |

## Notes

Kept, since each matters at PR 2 or later: **NOTE 1**, S2's and S3's
tests pass once `observed` is filled, refused or not; the ruling is
`build`'s, and an XPASS on either is not F6.2 or F6.3. **NOTE 3**, a run
killed before teardown leaves a worktree registered; `git worktree prune`
clears it. **NOTE 4**, `make plants` prints "in the tree" for S1a and S1b
while neither is read; the markers are the truth. **NOTE 7**, PR 2's
readers are new checks, named in lower case for what they read, naming
the refused path in their error (`feasibility.md` §4).

Dropped as settled: **NOTE 2** (repaired at `df084ef`), **NOTE 5** (row
6's claim keeps "governed" because it is the claim measured), **NOTE 6**
(the video and the security record are carried rows), **NOTE 8** (§3
says its messages are read at `df084ef`).

BLOCK: 0 · FINDING: 4 (1 and 3 repaired; 2 and 4 to PR 2) · NOTE: 8

## What a reader can run

```
git diff 0b96da4...HEAD --stat -- src/validate src/verdict/build.py scripts   # empty: no reader
uv run pytest tests/test_m06_seeds.py -q              # 6 xfailed
uv run pytest tests/test_m06_seeds.py -q --runxfail   # 6 failed, feasibility.md section 3's messages
make plants
make ledger     # exit 0
```
