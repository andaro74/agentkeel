---
# M05 PR 2, Security's key. The security account, the two new stacks,
# the bootstrap's and the construct's edits, and the workflows. Product's
# file is rulings/pr2.md, Engineering's rulings/pr2-engineering.md, the
# Threshold Owner's rulings/pr2-threshold-owner.md.
ruling: pr2-security
seat: Security
authorises:
  - milestones/M05/runs/security_account.md
evidence:
  - SPEC/00-overview.md#8-M05
  - SPEC/05-containment-and-evidence.md
  - milestones/M05/feasibility.md
  - milestones/M05/rulings/pr1-security.md
pr: 31
---

# Ruling: M05 PR 2, Security

Drafted by the session; the human rules as Security before the merge.

## 1. The security account, and the role deleted after its deploy

The security account is **897698239547**, an existing member of the
organization, reused and cleaned by the human on 2026-09-29
(`runs/security_account.md`; Unsure B on M05 PR 1). The agent account,
581208540944, is the organization's management account, so
`OrganizationAccountAccessRole` in 897698239547 trusts it.

**Ruled:** the human deploys `infra/security/` once through that role
(profile `agentkeel-security`, with MFA), and **deletes
`OrganizationAccountAccessRole` in 897698239547 right after**. From then
on the account is reached as `hector.flores` (console, MFA) or root
(MFA), both confirmed working. A role in the security account that an
agent-account admin can assume would make "an account it cannot change"
false on its first day.

**Recorded:** SCPs never bind a management account. While the agent
account is this organization's management account, no SCP can restrict
its admin, so `open.md` row 17's deferral to the landing zone cannot be
closed by an SCP on the agent account. It changes nothing measured at
M05.
