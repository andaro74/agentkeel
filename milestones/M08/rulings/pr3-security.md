---
# M08 PR 3, Security's key for run 2's by-hand egress rule (SPEC/08 §5.1,
# §11 R1). Run 2 removes a1's refusal for the hostile copy alone, which is
# the removal of a live boundary: it waits for this ruling file to carry
# "Ruled by" on its own, and the diff of the add and the remove is kept
# with 2>&1. DRAFT until the human rules; the egress rule is NOT in this
# repository (it is an AWS SG rule on the drill-agent's security group).
# This file documents the deploy and holds its diff; the construct is not
# changed. Product's file is rulings/pr3.md; Engineering's (with the cold
# review) is rulings/pr3-engineering.md.
ruling: pr3-security
seat: Security
authorises:
  - milestones/M08/runs/drill_run2.yaml
evidence:
  - SPEC/00-overview.md#8-M08
  - SPEC/08-game-day-drill.md#5-the-seeded-cases
  - SPEC/08-game-day-drill.md#11-read-before-PR-2
  - docs/developer/incident.md
pr: 47
---

# Ruling: M08 PR 3, Security

Ruled by andaro74 as Security, 2026-10-05, as written.

## What this authorises

**One egress rule, by hand, on the hostile copy's security group alone,
for the duration of run 2.** No construct change (which would open
refagent's group too, SPEC/08 §6). No permission widening in any role.

- **Exact form.** An egress rule on the drill-agent's SG, allowing TCP 443
  to the KMS interface endpoint's SG (the destination the construct uses
  for every agent that declares `kms`, `infra/construct/governed_agent.py`
  §endpoints). Added by hand before the invocation, removed after.
- **Target.** The drill-agent SG (`agentkeel-drill-agent` stack's
  `AgentSecurityGroupId` output), one invocation only. Refagent's SG,
  owner-check's and window-check's are not touched.
- **Duration.** From the add until the remove. The remove closes run 2's
  window (SPEC/08 §2).
- **Diff.** Kept with `2>&1` and transcribed into `drill_run2.yaml`'s
  observed block (the AWS console output of `authorize-security-group-egress`
  and `revoke-security-group-egress`).

## Why it is ruled, not refused

SPEC/08 §11 R1 names this as the one AWS change M08 makes. It is a
removal of a live control for the hostile copy alone, read against §2's
rule: a construct change would widen the boundary of every agent, and is
not made. The rule is added for the second-layer reading (F8.2): IAM's
`AccessDenied` for `kms:ListKeys` in the trail, and the flow record's
`ACCEPT` for the ENI to the KMS endpoint's address.

## What it does not do

- **No construct change.** `infra/construct/`, `infra/bootstrap/`,
  `infra/security/` and `infra/audit/` are not touched.
- **No grant.** The drill-agent role is unchanged; the construct's
  `AGENT_DENIES` and the boundary are unchanged.
- **No key policy change.** The KMS endpoint's policy is unchanged.

## The cold review

To be run on the diff by `security-reviewer` before this PR opens.
Expected: 0 BLOCK, since no `infra/` is changed and no permission is
granted or widened. The report is pasted in the PR body and summarised
in `rulings/pr3-engineering.md`.

## Unsure

- **Which SG id.** The drill-agent's SG id is read from CloudFormation
  outputs at run 2 time; recorded in `drill_run2.yaml.observed` and
  nowhere else. Seat: Security. Recorded under the M08 decision rule.
- **The KMS endpoint SG.** Read from the bootstrap stack's output;
  likewise recorded. Seat: Security. Recorded under the M08 decision rule.
