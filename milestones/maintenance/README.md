# Maintenance

Pull requests after the `m10` close (M10 was the last milestone; building
stopped at its close). A maintenance PR carries no ledger row, no
explainer and no video entry, and is not PR 1 to 4 of anything. It still
ends with a ruling file here, under `rulings/`, one per seat whose path it
touches, so `ruling-cited` and `cold-review-ruling` hold as they did; and
a change to the account is still made by hand by the human, recorded in
the README of the stack it changed.

| Ruling | PR | What |
|---|---|---|
| `endpoints-one-subnet` (Security), `endpoints-one-subnet-engineering`, `endpoints-one-subnet-product` | #58 | the five interface VPC endpoints in one subnet: ten ENIs to five, $74.40 a month to $36.50 expected |
| `retire-four-agents` (Security), `retire-four-agents-product` | #59 | the four closed milestones' agents removed: festival-desk retired through the platform, window-check and drill-agent by hand (finding 1), then all four stacks and their retained keys, tables, pool, guardrail, log groups, markers and image repositories deleted by the admin; registry rows kept with `retired_at`. Read-back owed below |

## Findings

1. **The platform's retire path refuses an agent two platform versions
   behind** (2026-11-02, `rulings/retire-four-agents.md`). The retire
   workflow opened its one-line pull request for window-check (#5) and
   drill-agent (#6), and the `platform-check` the repository ruleset
   requires refused each head at m10: guardrail version 5, not the
   platform's 6; `callers` missing. Their upgrade pull requests fail the
   same way, since the manifest is the agent's own file. An agent left
   behind can neither upgrade nor retire without a person's edit and a
   redeploy. Not repaired: the project is closed. The two were deleted by
   hand under the Security ruling instead.
2. **The platform upgrade moves an own-rules agent's guardrail pin to
   refagent's** (2026-11-02, the same ruling). festival-desk's `main` pins
   its own guardrail `at8e36cosq1r`, as SPEC/09 §2 requires; its upgrade
   pull request (#5) carries refagent's pin, because `platform_upgrade.py`
   treats `guardrail` as platform-owned (SPEC/07 §2), and the check
   refuses it. A retire head moves `rollout` alone, so festival-desk is
   expected to retire through the platform. Whether SPEC/07 §2 is amended
   is Product's.

## Read-back owed

After the deletions under `retire-four-agents`: each security group's
interfaces before its delete, each stack's `DELETE_COMPLETE` time and any
`DELETE_FAILED` reason and retry, each key's `DeletionDate`, the four
registry rows as read, festival-desk's retire run and its `retired.json`,
and `list-stacks` showing `agentkeel-refagent` and `agentkeel-label-impact`
alone. Not yet made.
