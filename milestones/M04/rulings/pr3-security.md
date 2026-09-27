---
# M04 PR 3 (#27), Security's key. Drafted by the session from the
# security-reviewer report on this PR; the human rules as Security before
# the merge. Product's file is rulings/pr3.md.
ruling: pr3-security
seat: Security
authorises:
  - .github/workflows/evals.yml
  - infra/workflows.sha256
evidence:
  - SPEC/04-model-swap.md#4-falsifiers
  - milestones/M04/rulings/pr2-security.md
pr: 27
---

# Ruling: M04 PR 3, Security

Drafted by the session; the human rules as Security before the merge.

## 1. The swap read in `evals.yml`

The observer step, which already runs `scripts/observe_pr.py` on M02's
three run files with `GITHUB_TOKEN`, runs it once more on
`milestones/M04/runs/f4_swaps.yaml`, and the measuring step passes the
result to `make evals` as `SWAPS_OBS`. No new secret, permission, action
or step. `scripts/rule_swaps.py` runs inside `make evals`, with no token:
it reads the swap branches from this checkout (`fetch-depth: 0` already
fetches every branch) and runs the gate in a scratch worktree outside the
tree. `infra/workflows.sha256` carries the new hash.

What reaches the job from a swap PR is its envelope and control card,
read with `git show`, never run: the gate validates the envelope against
the schema and checks the card's hash, and REJECTs anything else.

## 2. The bootstrap redeploy (PR 2's `pr2-security.md` §1)

Carried here because PR 2 merged before it was recorded. Sonnet 4.5
answered every call on #26, so the eval role's candidate list is deployed.
**Still to record, from the human:** the `cdk diff --strict` read against
the checklist (only the EvalRole's policy changed), whether the deployed
side read `§` or `?` (`open.md` row 6), the template size at that head,
and `aws iam get-role-policy` on `agentkeel-evals` read back.
