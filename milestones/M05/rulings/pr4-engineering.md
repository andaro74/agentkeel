---
# Cold review of M05 PR 4 (#33), the close, base main (78bf4ac), head
# 0c0f1ad, by engineering-cold-reviewer from the diff and row 5 only; its
# report is in the PR body verbatim. The diff touches no Engineering path, so
# this file names only itself and takes no key over anything. Product's file
# is pr4.md.
ruling: pr4-engineering
seat: Engineering
authorises:
  - milestones/M05/rulings/pr4-engineering.md
evidence:
  - SPEC/00-overview.md#8-M05
  - evals/history/28634e9a1405b034a3efbe898cc7675ebfab3587.json
  - https://github.com/andaro74/agentkeel/actions/runs/36666223908
  - milestones/M05/feasibility.md
  - milestones/M05/rulings/pr3.md
  - milestones/M05/runs/f5_1_curl.yaml
  - milestones/M05/runs/f5_7_quarantine.yaml
  - src/ledger.py
pr: 33
---

# Cold review: M05 PR 4 (the close)

Ruled by andaro74 as Engineering, 2026-09-30, as written.

`engineering-cold-reviewer` read `git diff 78bf4ac...0c0f1ad` (8 files,
six commits, none under `evals/history/`) and row 5, not the PR body or
the commit bodies. It ran `make ledger` (exit 0) and compared row 5's cell
with the "as row M05 reads it" line for `28634e9` byte for byte in both
READMEs (equal); compared `ledger.plain` with `docs/milestones/README.md`
in memory (equal); ran `validate` (15 of 16, the one failure this file's
absence) and `tests/test_m05_seeds.py` (5 passed, 2 xfailed); and checked
every number in the prose against the envelope, every row of
`milestones/M05/open.md` against a closing or a carry with a seat and a
milestone, and that every M05 commit under `evals/history/` is
`github-actions[bot]`'s (five). **0 BLOCK, 3 FINDING, 5 NOTE.** Its shape
check: a valid close; only Product's paths; no reader built; nothing
under `src/`, `agents/`, `infra/`, `tests/`, `evals/`, `data/`, `rules/`,
`thresholds.yaml` or `.github/`; `src/baseline/` unchanged since `m00`.
The repairs are their own commits after `0c0f1ad`.

| # | Finding | Status |
|---|---|---|
| F1 | The explainer said S1's drop "leaves no record anywhere" and "Nothing can put it in the second account"; the ruling says no flow record, the timeout is in the run file, and M06 `open.md` row 41 says what could record it | **Repaired** (`db5d4f3`, Product): "no network record"; the only record is the timeout the person saw; nothing in M05 puts it there; M08 |
| F2 | The explainer said S7 was "not recorded"; the envelope records the attach, the invocation (305 s) and the detach | **Repaired** (`db5d4f3`, Product): the stop, the question and the lift recorded; the refused model call not, because none was made |
| F3 | The explainer put the misreads in the wrong pull request, and one of the three was a test reading the human's run file, not a record in the audit bucket | **Repaired** (`db5d4f3`, `0b3ae5c`, Product): PR 2 read the first three and had its own reader fixed once; PR 3's first run misread two records; the third repair was a test. The close detail and `pr4.md` §3 say the same |
| N1 | `pr4.md` §2's own-run paragraph is a placeholder | **Filled** from run 36712123730 on `38ef391`: it measured nothing and wrote no envelope (`evals.yml`, "Is this tree already measured?": nothing measured changed since `28634e9`), and gated `28634e9`, GREEN. No bot commit reached the branch; the cell stays keyed to `28634e9` |
| N2 | `pr4.md` §5 listed M05 `open.md` row 16 in neither list | **Repaired** (`0b3ae5c`): split, items a, c, d and k landed; item b, M03 row 14 and the ceiling carried (M06 rows 15, 12, 48, 44) |
| N3 | Security's deploy times cite no file | **Repaired** (`0b3ae5c`): the attestation says they are the human's reading, recorded in the M05 README's PR 2 detail, and only the stand-in's are in a run file |
| N4 | The four `Signed:` lines are blank | Recorded: they gate the tag. Checked on the pushed head before any merge command (M05 `open.md` row 44's lesson) |
| N5 | The two notes judged without a source | Recorded: checked, no M05 file holds either; the judgment holds |

## What a reader can run

```
make ledger                                   # exit 0; row 5 RED, the cell = "as row M05 reads it" for 28634e9
make ledger-plain && git diff --exit-code docs/milestones/README.md
uv run pytest -q tests/test_m05_seeds.py      # 5 passed, 2 xfailed (S1, S7)
git diff --name-only 78bf4ac...HEAD           # docs/** and milestones/** only, and CI's evals/history/ commit
git log --format='%h %an' 4206edf..HEAD -- evals/history   # github-actions[bot] only
```
