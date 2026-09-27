---
# M04 PR 1 (#23), Engineering's key and the cold review, one file. Drafted
# by engineering-cold-reviewer from the diff 2addb95...688634c and row 4
# only; repaired and completed by the session. Product's file is
# rulings/pr1.md.
ruling: pr1-engineering
seat: Engineering
authorises:
  - .gitattributes
  - src/verdict/plants.py
  - tests/test_m04_seeds.py
  - tests/test_m03_seeds.py
  - tests/fixtures/README.md
  - tests/fixtures/m04/**
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md
  - milestones/README.md
  - milestones/M04/README.md
pr: 23
---

# Ruling: M04 PR 1, Engineering, with the cold review

The dispositions below were ruled by andaro74, 2026-09-27, "as
proposed". This file was drafted by the session from the cold reviewer's
draft and those rulings; the human signs it off as Engineering before the
PR opens.

## What was read

`engineering-cold-reviewer` read the diff `2addb95...688634c` (31 files,
17 commits) and row 4 only, not the PR body or commit message bodies. It
ran `git show --stat` on every commit, `uv run pytest
tests/test_m04_seeds.py tests/test_m03_seeds.py` with and without
`--runxfail` (11 passed, 6 xfailed), `make plants`, and compared
`src.ledger.plain` with `docs/milestones/README.md` (equal). Its report,
0 BLOCK, 5 FINDING, 4 NOTE, is in the PR body verbatim.

**Checks that held:** the shape is PR 1's; no seed commit contains its
reader; every seed fails on its planted line; no code writes or reads an
envelope outside `verdict.build` and `verdict.gate`, and nothing reaches
`evals/history/`; no diff under `src/baseline/`, `evals/history/`,
`thresholds.yaml`, `rules/`, `data/`, `agents/`, `.github/` or `infra/`.

## Findings

| # | Finding | Status |
|---|---|---|
| F1 | The rulings the diff cites were not in the tree | **Repaired**: `rulings/pr1.md`, `pr1-threshold-owner.md`, `pr1-data-owner.md`, `pr1-rule-owner.md` and this file, all `pr: 23` |
| F2 | The ledger named S3's and S4's seed commits, whose fixtures `2dc81ae` rewrote | **Repaired** (`f5922c4`): the seeded-commit cell, the M04 README and `feasibility.md` §3 name `2dc81ae` and `e0ce2ce` beside S3 and S4 |
| F3 | Three strict markers could not tell a broken fixture from the planted failure | **Repaired** (`e0ce2ce`): every precondition raises `SeedBroken`; only the planted line is an `assert`. Checked by corrupting one latency in `s4-slow-raw.json`: FAILED with `SeedBroken`; restored: xfailed |
| F4 | With PR 2's no-incumbent rule, S3's "alone GREEN" would fail and force a change to the seed | **Repaired** (`e0ce2ce`): S3 is ruled against the incumbent history; its first run alone is GREEN and its second alone RED for `g-006` regressed only |
| F5 | CLAUDE.md's seat line missed ADR-0009 entry 6 | **Repaired** (`f5922c4`), with SPEC/00 §5.1 |

## Notes

| # | Note | Status |
|---|---|---|
| N1 | `make plants` says "in the tree" for a reader that does not read its seed yet | PR 2, Engineering: a third state, "seed unread" |
| N2 | One assertion in M03's reader-off test for S2 holds with or without the reader | Recorded; the `pytest.raises` above it is the witness |
| N3 | S1's test does not rule out §7's excluded reasons | PR 3's live read of the breaking swap must; recorded |
| N4 | PR 2's manifest edits will break the pin patches' context | Ruled (`f5922c4`, SPEC/04 §5.1): PR 2 regenerates the patches' context in the commit that edits the manifest and re-runs each seed with `--runxfail`; the lines a patch changes stay as planted |

Also in this seat's paths: the data-owner's F1 and F3 (`e0ce2ce`: the date
the question asks about; `SeedBroken`) and F9 (`2dc81ae`: the tool calls
made on the real tool), and `open.md` row 38 (`22b9cd9`: M03's S1 and S2
seen failing with their readers switched off).

## What a reader can run

```
git show a16e2c7 c6b6cb8 6f18507 63033b7 8994dcb 2dc81ae e0ce2ce --stat
uv run pytest tests/test_m04_seeds.py tests/test_m03_seeds.py
uv run pytest tests/test_m04_seeds.py --runxfail
make plants
```
