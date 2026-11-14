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
| `readme-first-visit` (Product) | #60 | the README rewritten for a first-time visitor, with a header image and four diagrams under `docs/assets/`; no claim, no measurement; "Governed" removed from its first line |

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

## Read-back: the four agents removed, 2026-11-06 and 2026-11-07

Under `rulings/retire-four-agents.md`. Made by the human's admin user while
the ruling was a draft (as M09 finding 4 and M10 pr3.md Unsure G record a
deploy made before "Ruled by"); read from the account on 2026-11-07T15:40Z.

**festival-desk, through the platform.** The retire workflow dispatched;
the App opened `agentkeel-studio/festival-desk#6` "Retire festival-desk",
whose `platform-check` passed (finding 2 held: the retire head kept the
agent's own pin); merged with a merge commit 2026-11-07T02:21:03Z
(`67cf11c`). The retire job on the next schedule, run 42329724674, removed
the runtime, invoked the old ARN once (`refused: ResourceNotFoundException`),
put `envelopes/agents/festival-desk/retired.json` once in the audit bucket,
and wrote the row: `retired_at 2026-11-07T02:38:56Z`, `retire_run_id
42329724674`. Merge to `retired_at`: 1,073 s, inside SPEC/07's 3,600 s.

**The stacks.** Every `delete-stack` ran as the stack's own role,
`agentkeel-cfn-exec`. Each first attempt on a stack with a live runtime
failed on the security group while AgentCore's two `agentic_ai` interfaces
(owner `amazon-aws`, not deletable by the admin) were still attached;
they were released within eight hours and the retry completed.

| Stack | Attempts | `DELETE_COMPLETE` |
|---|---|---|
| `agentkeel-window-check` | `AgentSg56A0E748` DELETE_FAILED 2026-11-06T05:24:10Z ("has a dependent object", `sg-07094a71a99a53f20`); interfaces gone by 22:01Z | 2026-11-06T22:11:30Z |
| `agentkeel-owner-check` | none failed (no runtime since 2026-10-03) | 2026-11-06T22:18:19Z |
| `agentkeel-drill-agent` | `AgentSg56A0E748` DELETE_FAILED 2026-11-06T22:34:15Z, 22:53:01Z and 2026-11-07T02:12:03Z (`sg-0c90a9e079b0d4533`, `eni-06666a876d629c16b` and `eni-0ecfa247aa98b5783` attached) | 2026-11-07T15:25:06Z |
| `agentkeel-festival-desk` | `AgentDoorStageC6BAC22B` DELETE_FAILED 2026-11-07T02:33:24Z: "Unable to delete stage. Insufficient permissions to delete logging. User: arn:aws:sts::581208540944:assumed-role/agentkeel-cfn-exec/AWSCloudFormation is not authorized to perform: logs:DeleteLogDelivery" (M10 pr3 C, now read: the boundary's `logs:Delete*` deny does refuse a door stage's delete); the stage then DELETE_COMPLETE 02:38:24Z on the next attempt; `AgentSg56A0E748` DELETE_FAILED 03:09:05Z (`sg-0e509fadcce8014e1`) | 2026-11-07T15:25:59Z |

**The registry rows**, read 2026-11-07T15:40Z:

| name | `retired_at` | `retire_run_id` |
|---|---|---|
| owner-check | 2026-10-03T14:35:17Z | 37129778736 |
| window-check | 2026-11-06T22:12:15Z | by-hand-2026-11-02 |
| drill-agent | 2026-11-07T15:25:25Z | by-hand-2026-11-02 |
| festival-desk | 2026-11-07T02:38:56Z | 42329724674 |
| refagent, label-impact | none | none |

**The keys**, `PendingDeletion`: owner-check `23a1ee05…` 2026-11-13T22:36Z;
window-check `7eaab44d…` 2026-11-13T22:12Z; drill-agent `bd223f80…`
2026-11-14T15:25Z; festival-desk `122a23f1…` 2026-11-14T15:26Z; and the
orphan refagent key `9120aa75…` (scheduled 2026-11-02) 2026-11-09T04:59Z.

**Gone, read:** the four rights tables; festival-desk's guardrail
`at8e36cosq1r`, pool `us-west-2_f8kyzKF0P`, API `ohw3eeegoa` and both door
functions; the image repositories `agentkeel/owner-check`,
`agentkeel/window-check`, `agentkeel/drill-agent`, `agentkeel/festival-desk`;
the markers for owner-check and window-check; the four runtimes
(`list-agent-runtimes` reads `refagent` and `agentkeel_label_impact` alone);
`list-stacks` reads `agentkeel-refagent` and `agentkeel-label-impact` alone.

**Still standing at the 15:40Z read, finished by the owner the same day** (each read back as not found at 2026-11-07T17:30Z; the four repositories archived then): log groups
`/aws/bedrock-agentcore/runtimes/agentkeel_drill_agent-jUPi0ADoVd-DEFAULT`,
`/aws/bedrock-agentcore/runtimes/agentkeel_festival_desk-379Sz3GgxZ-DEFAULT`
and `/agentkeel/doors/festival-desk/access` (with its retained subscription
filter to `agentkeel-calls`); markers
`/agentkeel/marker/drill-agent/rights-table-digest` and
`/agentkeel/marker/festival-desk/rights-table-digest`; two orphan pools
named `agentkeel-festival-desk` from the failed first door deploys of
2026-10-17 (`us-west-2_x4675vxZ6`, `us-west-2_x8GNAuj5i`; M10 pr3 counted
55 and deleted them, these two were made after that count); the four
repositories not yet archived.
