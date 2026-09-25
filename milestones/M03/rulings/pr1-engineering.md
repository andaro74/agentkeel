---
# M03 PR 1 (#19), Engineering's key and the cold review, one file (one
# ruling file per seat per PR). The cold review was drafted by
# engineering-cold-reviewer from the diff 71eff00...faed466 and row 3
# only; its report is in the PR body verbatim. Product's file is
# rulings/pr1.md.
ruling: pr1-engineering
seat: Engineering
authorises:
  - .gitattributes
  - src/gates/__init__.py
  - src/verdict/plants.py
  - tests/test_gates.py
  - tests/test_m03_seeds.py
  - tests/fixtures/README.md
  - tests/fixtures/m03/**
evidence:
  - SPEC/00-overview.md#8-M03
  - SPEC/03-evals-regression-redteam-corpus.md#5-the-seeded-cases
  - milestones/README.md
  - milestones/M03/README.md
pr: 19
---

# Ruling: M03 PR 1, Engineering, with the cold review

Ruled by andaro74 as Engineering, 2026-09-25.

## The cold review

`engineering-cold-reviewer` read `git diff 71eff00...faed466` (28 files)
and row 3, not the PR body or the commit bodies, and ran no tests (0
BLOCK, 5 FINDING, 5 NOTE). Its shape check: PR 1 holds plant material
only, `CONTROLS` is `{}`, no reader of any seed is in the tree, and
nothing makes claim 3 pass. The commits after `faed466` are repairs, each
its own commit; the diff the reviewer read is unchanged beneath them.

| # | Finding | Status |
|---|---|---|
| F1 | history is read whole, so a later pass re-rules an older envelope | **seed S7** (`1e51666`), ruled by the human; reader at PR 2 |
| F2 | a strict xfail with no `raises=` takes any exception | **repaired** (`c3f8c81`): each marker names its exception; `mkdir(exist_ok=True)` in S2 and S6 |
| F3 | S5's test can pass on what the human types | **PR 2**: its marker comes off only in the commit that makes the test call `observe_ingest.py`'s parser on the lookup |
| F4 | no ruling file for the seat-owned paths | **this file**, `pr1.md`, `pr1-rule-owner.md`, `pr1-security.md` |
| F5 | S1's patch has two non-UTF-8 bytes | **stands**: a seed is not edited once planted. A PR 2 test that validates S1's tree reads it with `errors="replace"` or not at all |
| N1 | tests hand `judge` the envelope JSON directly | recorded; precedent `tests/test_gate.py`, no envelope written |
| N2 | S2's and S4's reader column named a control and a data file | **repaired** (`14be616`): `plants.py`, `gate.py` |
| N3 | S1 digested the working tree | **repaired** (`c3f8c81`): a clean worktree of HEAD |
| N4 | 38 words holds only if dates split on hyphens | recorded; PR 2's tokenizer decides, and 34 clears the 12-word bound too |
| N5 | was `docs/milestones/README.md` written by `make ledger-plain` | yes, in `8d16fe5` and `f057725`; Product's |

## Engineering's paths

- `tests/test_m03_seeds.py`, `tests/fixtures/m03/**`,
  `tests/fixtures/README.md`: the seven seeds and the two guards.
- `src/verdict/plants.py`: `SEEDS_M03`, a list `make plants` prints; it
  reads nothing and gates nothing. `CONTROLS` is untouched.
- `src/gates/__init__.py` and `tests/test_gates.py`: the fix to
  `security-reviewer` BLOCK 1 (`10452f9`), ruled by the human. Two tests
  fail without it. It is not a reader of claim 3.
- `.gitattributes`: the M03 patches and the S5 amendment are `-text`.

**Engineering holds for PR 2**, besides every reader in SPEC/03 §6:
`open.md` row 3 (the instruments' loose ends); row 11's items e, g and j;
`score_one` reading the intervening policy (`rule-owner` F3);
`admitted.yaml` checked against its bytes (`data-owner` F7); the table
marker for the runtime match (`security-reviewer` F6); the S5 lookup by
content (`security-reviewer` F7).

## What a reader can run

```
uv run pytest -q                                   # 364 passed, 1 skipped, 7 xfailed at 10452f9
uv run pytest tests/test_m03_seeds.py --runxfail   # S1..S7 each fail for the planted reason
uv run pytest tests/test_gates.py -k "subagent_prompt or keeps_the_seat"
git show 10452f9 -- src/gates/__init__.py          # the only change to a gate
```

## The second cold read, of the repairs

`engineering-cold-reviewer` read `git diff faed466...76b2623` (17 files,
9 commits) with row 3, and ran the seed and gate tests and
`ruling-cited --base main --pr 19` (exit 0): 0 BLOCK, 1 FINDING, 5 NOTE,
in the PR body verbatim. S7 is a false state before any reader and fails
for its planted reason; the `seats_of` change is sound (the base's
`seat:` wins, a rename keeps the old path's seat, a new prompt still
needs Security's CODEOWNERS line); each `raises=` matches; the four
files cover the 35 paths exactly. **The finding**, that `raises=` checks
the exception class only and five seeds raise AssertionError, is
repaired in the docstring, which now says so. Its note on the stale
comment in `plants.py` is repaired in the same commit. Recorded: an
empty prompt on the base falls through to the PR's `seat:`, as an empty
ruling file does; none exists.
