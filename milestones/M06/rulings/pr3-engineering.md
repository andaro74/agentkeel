---
# M06 PR 3 (#36), Engineering's key and the cold review, one file. Drafted
# from engineering-cold-reviewer's read of 39031e7...b3be039. Product's file
# is pr3.md.
ruling: pr3-engineering
seat: Engineering
authorises:
  - src/validate/agent.py
  - tests/test_m06_readers.py
  - tests/test_m06_seeds.py
evidence:
  - SPEC/00-overview.md#8-M06
  - milestones/README.md
  - milestones/M06/README.md
pr: 36
---

# Ruling: M06 PR 3, Engineering, with the cold review

DRAFT for andaro74 as Engineering. Not ruled until this line reads "Ruled by".

## What was read

The diff `39031e7...b3be039` (11 files) and row 6, not the PR body or
commit bodies. Run by the reviewer: `uv run pytest tests/test_m06_readers.py
tests/test_m06_seeds.py -q` (80 passed, 2 xfailed), `src.validate` and
`src.ledger` (exit 0). The repairs after it (`b19db9a`, `cf92716`) were not
read cold again.

## What holds

1. **Shape.** A repair and the amendments that follow from it; no reader
   built, no close. S2 and S3 stay `observed: null`, xfailed.
2. **P5.** No writer or reader of envelopes touched.
3. **Frozen paths.** Nothing under `src/baseline/`, `evals/goldens/`,
   `data/` or `evals/history/`.

## Findings

| # | Finding | Status |
|---|---|---|
| F1 | `pr3.md` cited but not in the tree; no security report | Repaired: `pr3.md`, `pr3-security.md`, this file; the security report in the PR body |
| F2 | The owner test said PR 4's run records it; no reader takes `f6_0` | Repaired (`cf92716`): read by hand, recorded in PR 4's ruling as S3's precondition, not evidence for the cell |
| F3 | Step 1 missed, and the re-export would let it read as held | Repaired (`cf92716`): recorded as missed in the run file and the PR 3 detail |
| F4 | The new export never POSTed; the next POST is inside the timed run | Repaired (`b19db9a`): the owner POSTs `agent.post.json`, the accepted form |
| F5 | The explainer still said PR 3 | Repaired (`cf92716`) |
| N1 | The live fixture typed by hand | Repaired (`b19db9a`): GitHub's response committed and loaded |
| N2 | No margin in PR 4 | Stands: CLAUDE.md's cap; a miss is a RED close |
| N3 | "by the author" against `floresinnovations` | Product's, at the close (`pr3.md`) |
| N4 | "governed" in the claim | Product's, at the close (`pr3.md`) |

## What a reader can run

```
uv run pytest tests/test_m06_readers.py tests/test_m06_seeds.py -q
uv run python -m src.validate
uv run python -m src.ledger
uv run python -c "import json; from src.validate import agent; print(agent.ruleset_errors([json.load(open('milestones/M06/runs/owner_check_ruleset_24310403.json'))]))"   # []
```
