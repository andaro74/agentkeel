---
# M01 PR 4 (#10), the close. Ruling B: one seat per file. This file is
# Product's and keys the close's Product paths; `pr4-engineering.md` keys
# the one Engineering path, `src/ledger.py`, and its tests, and has the same
# `pr`.
ruling: pr4
seat: Product
authorises:
  - milestones/README.md
  - milestones/M01/README.md
  - milestones/M01/attestations.md
  - milestones/M01/rulings/pr4.md
  - milestones/M02/open.md
  - docs/milestones/M01.md
  - docs/milestones/README.md
  - docs/video/README.md
evidence:
  - SPEC/00-overview.md#8-M01
  - evals/history/e97125e970ccfc6d044612eb006cdbdbcdb99337.json
  - https://github.com/andaro74/agentkeel/actions/runs/35680056132
  - https://github.com/andaro74/agentkeel/actions/runs/35683865472
  - milestones/M01/rulings/pr3-cold-review.md
pr: 10
---

# M01 PR 4 — the close: row 1 is RED

Closed through `/close-milestone`. PR 4 of four; there is no fifth.

**The three refusals the skill checks, and what they found:**

| Check | Found | Now |
|---|---|---|
| 1. The Measured cell and the envelope disagree | They could not agree. SPEC/00 §7 makes an unmeasured close RED, but `src/ledger.py` refused State RED beside a cell whose verdict is UNMEASURED | **Ruled** (Product and Engineering, the human, 2026-09-22): State RED, and `src/ledger.py` applies §7 to an UNMEASURED reading (`pr4-engineering.md`). `make ledger` exits 0 |
| 2. A Finding with no home | About sixty, from every PR of the milestone | **Each has a row** in `milestones/M02/open.md`, rows 9 to 23, with a seat and a date |
| 3. An Unsure item with no seat and milestone | PR #7 items 4, 8 (half) and 10; PR #8 items 2, 3 and 5; PR #9 had none in its body, and pr3.md's Unsure 4 and 5 were unrecorded | **Each is in `milestones/M02/open.md`** (rows 13, 14, 15, 21), or settled here (pr3.md Unsure 4 = pr3-cold F5, SSM resolution) |

Also checked: "What happened" is written, and every number in it is the
envelope's. The State is the verdict the gate reads. A close without a
measurement is RED. The PR count is four.

**The row.** Copied from the gate's reading of `e97125e`, by
`gate.measured_at(..., milestone="M01")`: `make ledger` now prints that line
under "as row M01 reads it", beside the envelope's own reading. The two
differ in exactly the words `not read in the runtime (mode runner)` and in
the verdict, UNMEASURED against GREEN. The close copies the first. RED on
the second half of the claim; the first half held on every seeded case.

**This PR's own run.** `src/ledger.py` is a measured path, so this PR's CI
run writes its own envelope. Row 1 stays on `e97125e` by ruling, as row 0
stayed on `9407615` at M00's close: the ledger rule does not reopen the
claim. Its run id and envelope are recorded here once CI writes them. If a
check fails in it, this PR is RED and the row is rewritten before the tag.

**The explainer.** "What happened" leads with RED and the table of seeded
cases. Every number in it is `e97125e`'s: 9 of 9 ordinary, 3 of 3 traps,
0 of 3 forbidden requests refused. Why RED is said in two plain sentences,
and so is why the three forbidden requests do not count against it.
"What we planted" had one stale sentence: construct tenancy as "the next
milestone's PR". It now says that every result records where the agent
ran, and a test-machine result cannot make this milestone green.

**What RED does not mean.** It does not mean a signed bundle loaded
unsigned, or that a laptop deployed: every seeded case of the first half was
refused. It means one thing only: refagent has never run inside the
construct, so the second half is unread. That sentence is in the explainer.

**Tag.** `git tag m01` on `main`, after this PR merges and after the four
attestation lines are signed. Never on the branch.

## What a reader can run to falsify this file

```bash
uv sync --frozen
make ledger ; echo "exit $?"                 # exit 0, row 1 RED
uv run python -c "
from pathlib import Path; from src.verdict import gate; from src import ledger
p = Path('evals/history/e97125e970ccfc6d044612eb006cdbdbcdb99337.json')
cell = gate.measured_at(p, milestone='M01')
for s in ('RED', 'GREEN'): print(s, ledger.check_measured({'#':'1','M':'M01','Measured':cell,'State':s}, gate.HISTORY))"
# RED None; GREEN row 1: State GREEN beside an UNMEASURED reading
grep -c '^| [0-9]* |' milestones/M02/open.md   # 22 numbered rows
git log --format=%an m00..HEAD -- evals/history/ | sort | uniq -c   # github-actions[bot] only
```
