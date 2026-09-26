---
# Cold review of M03 PR 4 (#22), the close, base main (c73eb9e), head
# e20d3c9, by engineering-cold-reviewer from the diff and row 3 only; its
# report is in the PR body verbatim. The diff touches no Engineering path, so
# this file names only itself and takes no key over anything. Drafted by the
# session; to be ruled by andaro74 as Engineering.
ruling: pr4-engineering
seat: Engineering
authorises:
  - milestones/M03/rulings/pr4-engineering.md
evidence:
  - SPEC/00-overview.md#8-M03
  - milestones/README.md
  - evals/history/cb06c0dbf0019088c664c6df1ce7d67cc64f7d58.json
  - evals/history/cb06c0dbf0019088c664c6df1ce7d67cc64f7d58.baseline-card.json
  - https://github.com/andaro74/agentkeel/actions/runs/36270471757
  - milestones/M03/runs/f3_5_amendment.yaml
pr: 22
---

# Cold review: M03 PR 4 (the close)

`engineering-cold-reviewer` read `git diff c73eb9e...e20d3c9` (7 files, 6
commits) and row 3, not the PR body or the commit bodies. It ran
`src.ledger` (exit 0), checked in memory that `gate.measured_at` of
`cb06c0d` equals row 3's cell byte for byte and that `ledger.plain` equals
`docs/milestones/README.md`, ran `validate` (15 of 15), `gate --plants`,
the seed tests (9 passed) and `pytest -q` (533 passed, 1 skipped), and
checked that every commit under `evals/history/` since `m02` is
`github-actions[bot]`'s. **0 BLOCK, 6 FINDING, 6 NOTE.** Its shape check:
a valid close; only `docs/**` and `milestones/**`; no reader built;
nothing under `src/`, `evals/`, `data/`, `rules/`, `thresholds.yaml` or
`.github/`. The repairs are their own commits after `e20d3c9`.

| # | Finding | Status |
|---|---|---|
| F1 | "each reader switched off, its seed failed again" is recorded nowhere in the tree | **repaired** `e240864`: reworded to the markers coming off with their readers, and `pr2-engineering.md` N1 |
| F2 | `rulings/pr4.md` cited before it exists | **held**: `pr4.md`, in this PR, carries the cuts (ruling 1) |
| F3 | the runtime numbers rest on a deploy log not in the tree | **repaired** `e240864`: `runs/pr3_merge_deploy_load_check.md`, named a log, cited where the numbers are used |
| F4 | "by the rule named for it" cannot be replayed; the agent's raw is not committed | **repaired** `ae2debf`, `e240864`: build's counting, said as such; attestation 1 names the control's raw as the one committed; M04 `open.md` row 34, item b |
| F5 | "What M03 shows" goes past what fired | **repaired** `ae2debf`: the table route refused in a test, the locks untried, the admin's way round, all named |
| F6 | M04 `open.md` rows 22 and 34 point at M02 `open.md` row 11 | **repaired** `e240864`: M03 `open.md` row 11 and its feasibility table |
| N1 | the explainer's count of routes misses S4 | **repaired** `ae2debf` |
| N2 | the generated plain sentence claims more than row 3 measured | M04 `open.md` row 23 (Product, SPEC/00 §10.3); the generated file is not edited |
| N3 | Object Lock stated as fact | **repaired** `e240864`: "is configured with" |
| N4 | row 11 items e, g, j have no home | **repaired** `e240864`: named done in the close detail |
| N5 | sources in PR bodies and comments cannot be checked from the tree | recorded; the ledger's design |
| N6 | numbers checked against their sources | recorded; no change |

## What a reader can run

```
uv run python -m src.ledger; echo $?                   # 0
uv run python -m src.validate                          # 15 ok
uv run pytest -q                                       # with Git's usr/bin on PATH on Windows
git diff --name-only c73eb9e HEAD | grep -v -e '^docs/' -e '^milestones/'   # empty
```
