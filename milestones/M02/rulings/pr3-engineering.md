---
# M02 PR 3 (#13), Engineering's key. Security's file is rulings/pr3-security.md,
# Product's rulings/pr3.md. The rest of PR 3's rulings are written in the PR 3
# session; this file covers the repair carried onto the branch from PR 2's merge.
ruling: pr3-engineering
seat: Engineering
authorises:
  - tests/test_bootstrap.py
  - src/validate/codeowners.py
evidence:
  - SPEC/00-overview.md#8-M02
  - milestones/M02/runs/row10_first_deploy.yaml
  - https://github.com/andaro74/agentkeel/actions/runs/35817173042
pr: 13
---

# Ruling: M02 PR 3, Engineering (the boundary test)

Drafted by the session; the human rules as Engineering before the merge.

`tests/test_bootstrap.py` gains
`test_every_action_the_construct_grants_the_agent_role_is_under_the_agent_boundary`:
every action the construct grants the agent role must be in the agent
boundary's allow list. It fails at `0faf973` on `dynamodb:Scan` and
passes at `c34da39`, the commit that adds the action to the boundary.
The first deploy on which the runtime answered (run 35817173042) refused
all fifteen goldens on that action; nothing at synth had compared the
two lists.

```
git checkout 0faf973 && uv run pytest tests/test_bootstrap.py -k under_the_agent_boundary   # fails on dynamodb:Scan
git checkout c34da39 && uv run pytest tests/test_bootstrap.py -k under_the_agent_boundary   # passes
```

## `src/validate/codeowners.py`

The login check reads with the same token order as the ruleset read
(`GITHUB_TOKEN`, then the gh CLI's). Unauthenticated, the users endpoint
allows 60 calls an hour per address; a day of local `make validate`
runs spent them and the check failed 403 on the developer's machine
while CI, which has `GITHUB_TOKEN`, passed (`951d98e`).
