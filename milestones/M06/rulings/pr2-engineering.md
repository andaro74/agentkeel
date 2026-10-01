---
# M06 PR 2 (#35), Engineering's key and the cold review, one file. Drafted
# from engineering-cold-reviewer's two reads: ef7e48e...e3a482e, and the
# repairs e3a482e...639e43b. Product's file is pr2.md.
ruling: pr2-engineering
seat: Engineering
authorises:
  - src/**
  - scripts/**
  - tests/**
  - Makefile
evidence:
  - SPEC/00-overview.md#8-M06
  - SPEC/06-developer-template.md
  - milestones/README.md
  - milestones/M06/README.md
pr: 35
---

# Ruling: M06 PR 2, Engineering, with the cold review

DRAFT for andaro74 as Engineering. Not ruled until this line reads "Ruled by".

## What was read

**First read:** the diff `ef7e48e...e3a482e` (63 files) and row 6, not the
PR body, commit bodies or the feasibility note's argument.
**Second read:** the repairs `e3a482e...639e43b` (11 files). Its own four
findings were repaired after it, in `69f8383`, `52ebd57` and `9be344c`,
which no reviewer has read cold.

Run by the reviewer: `uv run pytest tests/test_m06_seeds.py -q` (6 passed,
2 xfailed); with `--runxfail`, S2 and S3 fail "the attempt has not been
made"; `gate --plants`; `src.ledger` exit 0; `git show --stat` on each
reader commit. By the caller at HEAD: the full suite (753 passed, 1
skipped, 4 xfailed before the last repairs; the M06 tests 76 passed, 2
xfailed after) and `make validate`, all nineteen ok.

## What holds

1. **Shape.** PR 2, the measure. Each strict marker came off in its
   reader's commit: S1a `4d961cd` (`seats.py`, after the seats in
   `1dc781b`), S1b `95e3824` (`agent_goldens.py`), S4's query `2a9e793`
   (`panel.py`), S4's comparison `6435f5c` (`template.py`). S2 and S3 stay
   `observed: null`.
2. **P5.** The observer writes raw lists; `template.py` is called by
   `build` alone; `build answer` refuses `evals/history/`; the gate is the
   one reader of `template`. `test_p5_disagree.py` covers claim 6.
3. **Row 6.** `F6_1`, `F6_4` required from `c2a15d0`, built from the seed
   tests alone; `template` read by row 6, RED when absent.
4. **Frozen paths.** Nothing under `src/baseline/`, `evals/goldens/`,
   `data/` or `evals/history/`.

## Findings

| # | Finding | Status |
|---|---|---|
| B1 | No ruling file with `pr: 35`; no Threshold Owner ruling named | **Repaired**: `pr2.md`, `pr2-security.md`, `pr2-threshold-owner.md`, this file |
| F1 | An organisation's own login held a seat by ownership | **Repaired** (`efe9d17`): persons only; a test for both |
| F2 | Panel 1 listing S3's agent was never read | **Repaired** (`efe9d17`): F6.3 needs panel 1's row |
| F3, F6 | F6.2 and F6.1 read `merged`, not mergeable or the App's binding | **Repaired** (`efe9d17`, then second read F1): `mergeable_state` held on `blocked` alone, `unknown` unread; the live required check's `integration_id` read for S2 and S3 |
| F4 | The panel reader passed a UNION, VALUES, subquery or comma join | **Repaired** (`efe9d17`); malformed targets refused |
| F5 | A read error counted as a planted fault | **Repaired** (`efe9d17`); the 404/403 split tested (second read N4) |
| F7 | Docs claimed the unattempted App binding works | **Repaired** (`639e43b`, then second read F3) |
| F8 | The registry row was written before the answer was put | **Repaired** (`56c7c59`); a 412 on a re-put read as put (second read F2) |
| Second read F4 | S3's run file said "refused at its first commit"; the reader accepted any commit | **Repaired** (`69f8383`): F6.1 needs the first commit's fault and the App's failure on it |
| N1 | No pagination past 100 | **Open, PR 3**: one organisation, under ten repositories at M06 |
| N3 | The name in a path at deploy | **Repaired** (`efe9d17`) |
| N4, N6 | `results.A` only; the answer record's repository and commit not compared | **Open, PR 3** |
| N5 | `updated_at` moves on a re-run | Stands: it errs late, toward RED |
| N7 | A template agent's raw record carries refagent's inference config | Stands: recorded, not used |

The seat reports that touched Engineering's paths (threshold-owner N8,
rule-owner's null guardrail, data-owner F4, N2, N6, N8, security-reviewer
F1, F2, F11, N5, N6) are repaired in `1c8dba1`; their tables are in
`pr2-security.md`, `pr2-threshold-owner.md` and the PR body.

## What a reader can run

```
uv run pytest tests/test_m06_seeds.py -q                  # 6 passed, 2 xfailed
uv run pytest tests/test_m06_seeds.py -q --runxfail       # S2, S3: "the attempt has not been made"
uv run pytest tests/test_m06_readers.py tests/test_p5_disagree.py -q
uv run python -m src.verdict.gate --plants                # S1a to S4, readers in the tree
uv run python -m src.ledger                               # exit 0
git show --stat 4d961cd 95e3824 2a9e793 6435f5c           # each marker off with its reader
```
