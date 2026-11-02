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
| `retire-four-agents` (Security), `retire-four-agents-product` | #59 | the four closed milestones' agents deleted by hand (owner-check, window-check, drill-agent, festival-desk): their stacks, keys, tables, pool, guardrail, log groups, markers and image repositories; registry rows kept with `retired_at`. Read-back owed below |

## Findings

1. **The platform's retire path refuses an agent two platform versions
   behind** (2026-11-02, `rulings/retire-four-agents.md`). The retire
   workflow opened its one-line pull request for window-check and
   drill-agent, and the `platform-check` the repository ruleset requires
   refused each head at m10 (guardrail version 5 not 6; `callers` missing);
   festival-desk's `main` is refused for its guardrail pin. The upgrade pull
   requests fail the same way, since the manifest is the agent's file. An
   agent left behind can neither upgrade nor retire without a person's edit
   and a redeploy. Not repaired: the project is closed. The three were
   deleted by hand under the Security ruling instead.

## Read-back owed

After the deletions under `retire-four-agents`: each stack's
`DELETE_COMPLETE` time, each key's `DeletionDate`, the four registry rows
as read, and `list-stacks` showing `agentkeel-refagent` and
`agentkeel-label-impact` alone. Not yet made.
