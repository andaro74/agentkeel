---
# M02 PR 3 (#13), Security's key on the ruleset export. The rest of PR 3's
# rulings are written in the PR 3 session.
ruling: pr3-security
seat: Security
authorises:
  - infra/ruleset/main.json
  - infra/bootstrap/app.py
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#51-when-each-is-measured
  - milestones/M02/rulings/pr2-security.md
  - milestones/M02/runs/row10_first_deploy.yaml
  - https://github.com/andaro74/agentkeel/actions/runs/35817173042
pr: 13
---

# Ruling: M02 PR 3, Security (the export, and the boundary)

`ruling-cited` and `two-key` were made required on the live `main`
ruleset after PR 2 merged, and the ruleset was exported at once as this
PR's first commit (pr2-security.md item 4). `bypass_actors` is `[]`.

## `infra/bootstrap/app.py`: the agent boundary allows `dynamodb:Scan`

The first deploy on which refagent's runtime answered (run 35817173042,
PR 2's merge) refused all fifteen goldens: the construct grants `Scan`
on the rights table (M01 PR 3) and the boundary, the ceiling on every
platform role (R4), listed `GetItem` and `Query` only. One action added
(`c34da39`); the boundary stays an allow list; `cdk diff` is that one
line. `tests/test_bootstrap.py` now holds the construct's grants under
the boundary (`0faf973`, failing first). The human deployed the
bootstrap stack by hand after reading the diff.

This PR's own `ruling-cited` run refused the three paths of that repair
until this file and `pr3.md`, `pr3-engineering.md` named them: the first
refusal of a real pull request by the gate, and on PR 3 itself, not a
seed.
