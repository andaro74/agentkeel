---
# M02 PR 2 (#12), the Data Owner's key: Door 2. The second key on g-012's
# retirement is the Threshold Owner's, rulings/pr2-threshold-owner.md.
ruling: pr2-data-owner
seat: Data Owner
authorises:
  - evals/goldens/v1/g-012.yaml
  - evals/goldens/v1/g-021.yaml
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#51-when-each-is-measured
  - milestones/M02/open.md
  - data/rights_table.json
  - data/clause_index.json
pr: 12
---

# Ruling: M02 PR 2, Data Owner

Drafted by the session; the human rules as Data Owner before the merge.

## `g-012` retired (open.md row 3)

`retired: M02`, in place, never renamed (R11). The file stays so that
history keyed on the id still reads. Finding F0.1: the frozen control
passes this trap by luck, and has on every card since `m00`. Two keys:
this file covers the path; the Threshold Owner's names it. The gate's
`two-key` job on this PR's head is Door 2's check run.

## `g-021` added (row 4)

`sequel_no_inherit`, a trap. The question tempts inheriting the
original's US SVOD grant (`r-011`, 'Brackenfield Nine') for its sequel,
'Brackenfield Nine: The Tenth' (`t-004`), which the table lists in the US
and GB for theatrical and PVOD only; there is no US SVOD row for it, so
there is nothing to publish under. Clause `ML-2.3`: a grant for one
title conveys no rights in another. Expected `available: false`,
`exclusive: false`, `constraints: [sequel_no_inherit]`. Worked by hand:
`r-011` is `t-003 US SVOD 2024-02-01 to 2027-01-31 exclusive`; the
question's date is inside that window, which is the temptation; the
sequel is `t-004`, a separate title, with no row for US SVOD. Neither
prompt in the tree lists the code, so no agent passes it until a ruling
teaches one; the control never will (P7). `g-021` differs from `g-012`
in that `g-012`'s sequel had a row of its own with a window not yet
open (`window_not_open`), a code both prompts know; `g-021`'s has none.

Fictional slate, fictional contract clauses; no real title, person or
studio detail.

## What the Data Owner does not do here

No golden's `expected` changes. No id is reused. `g-099` stays burned.

## What a reader can falsify

```
make validate                                    # golden citations exist in data/: ok
uv run pytest tests/test_retired.py
grep -c sequel_no_inherit src/baseline/prompt.txt agents/refagent/prompt.txt   # 0 and 0
python -c "import json; print([r for r in json.load(open('data/rights_table.json')) if r['title_id']=='t-004' and r['platform']=='SVOD'])"   # []
```
