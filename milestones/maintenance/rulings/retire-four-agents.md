---
# Maintenance PR #59. Security's key over the by-hand deletion of four
# agent stacks in the agent account after the m10 close, and the finding
# that the platform's own retire path refused three of them. The M10 close
# ruled "nothing is deleted without a Security ruling"
# (milestones/M10/rulings/pr4-security.md, "What stands in AWS after the
# close"); this is that ruling. Product's file for the README row is
# retire-four-agents-product.md.
ruling: retire-four-agents
seat: Security
authorises:
  - milestones/maintenance/rulings/retire-four-agents.md
evidence:
  - SPEC/07-upgrade-retire-surfaces.md
  - milestones/M07/runs/f7_2_removed_and_kept.md
  - milestones/M07/runs/f7_2_retire.yaml
  - milestones/M10/rulings/pr4-security.md
  - https://github.com/agentkeel-studio/drill-agent/pull/6
  - https://github.com/agentkeel-studio/window-check/pull/5
  - https://github.com/agentkeel-studio/festival-desk/pull/5
  - https://github.com/andaro74/agentkeel/actions/runs/41454360702
  - https://github.com/andaro74/agentkeel/actions/runs/41455395838
  - https://github.com/andaro74/agentkeel/actions/runs/41456176090
pr: 59
---

# Ruling: maintenance PR #59, Security

Drafted by Claude Fable 5.1 for Security, 2026-11-02; not yet ruled. The seat replaces this line with `Ruled by <login> as Security, <date>, as written` (or with the changes it made named) before the merge; `cold-review-ruling` fails while it reads Drafted.

## What is ruled

The human with admin, by hand, in the agent account (581208540944,
us-west-2), deletes the four stacks `agentkeel-owner-check`,
`agentkeel-window-check`, `agentkeel-drill-agent` and
`agentkeel-festival-desk`, writes `retired_at` on the three registry rows
that lack it, and then deletes the resources the construct retains, named
below. `agentkeel-refagent`, `agentkeel-label-impact`, `AgentkeelBootstrap`,
`AgentkeelAudit`, `AgentkeelIngest`, `AgentkeelGrafana`, the registry table
and everything in the security account are not touched.

Why: the four agents exist for milestones that are closed (owner-check and
window-check for M07, drill-agent for M08, festival-desk for M09 and M10).
Nothing on `main` calls their runtimes; `observe_drill.py` and
`observe_caller.py` read records already in the audit bucket. drill-agent
is leaky by design (SPEC/08 §2, a3) and festival-desk holds a public door.
Each costs about $1 a month in its key and cents in its table and logs.

## Finding 1: the platform's retire path refuses an agent two platform versions behind

The retire workflow was dispatched for window-check (run 41454360702),
drill-agent (41455395838) and festival-desk (41456176090) on 2026-11-02.
`retire-plan` and `retire-open` ran and the `agentkeel-upgrades` App opened
the one-line draft pull requests SPEC/07 §2 describes (window-check #5,
drill-agent #6). Each agent repository's ruleset
(`infra/ruleset/agent.json`) requires the `platform-check` check from the
`agentkeel-platform` App before any merge, and that check, which runs
`main`'s `src/validate/agent.evaluate` at m10, refused every retire head:

| Repository | Head | The check's refusal, verbatim |
|---|---|---|
| drill-agent #6 | `ed642a8` | the platform's guardrail: manifest.yaml: guardrail {'id': '1088aw3ujhyd', 'version': '5'} is not the platform's {'id': '1088aw3ujhyd', 'version': '6'}; callers: missing; an agent's manifest says who may call it, even if nobody (`callers: []`) |
| window-check #5 | `5f7b665` | the same two |
| festival-desk, its upgrade #5 (`5ebb4c7`), and so any retire head from the same `main` | the agent's own guardrail: manifest.yaml: guardrail {'id': '1088aw3ujhyd', 'version': '6'} is refagent's; an agent with rules/ is guarded by its own (SPEC/09 §2; R10) |

The same check refuses each agent's open "Platform upgrade to m10" pull
request (drill-agent #5, window-check #4, festival-desk #5), because the
manifest is the agent's own file and the upgrade touches platform-owned
files only (SPEC/07 §2). So an agent at m06 or m07 can neither take the
m10 upgrade nor retire through the platform without a person's edit to its
manifest, a deploy at m10, and only then a retirement. The retire job
itself would also refuse a retire head whose manifest moved any field but
`rollout` (`scripts/retire_agent.py same`). SPEC/07's claim 7 was measured
GREEN for `taken 2 of 3` at `m07`, on an agent at the platform's own
version; it says nothing about an agent left behind, and this is the case
it did not cover. Nothing is changed in the platform by this ruling: the
project is closed, and the repair (a retirement that validates against the
platform version the agent was deployed at, not the newest) is written
down here and not built.

The platform's retirement record (`envelopes/agents/<name>/retired.json`,
written once by the retire job in the security account) is therefore not
written for these three. The record of their retirement is this ruling,
the registry row (`retired_at`, `retire_run_id: by-hand-2026-11-02`,
`retired_commit` the deployed commit), and CloudTrail's `DeleteStack` and
`DeleteAgentRuntime` events in `agentkeel-audit`.

## What each deletion removes and what it keeps

Read from the stacks on 2026-11-02 (`describe-stack-resources`) and from
`milestones/M07/runs/f7_2_removed_and_kept.md`.

**Removed by `delete-stack`** (not RETAIN in the construct): the runtime
(`agentkeel_window_check-YBt5st7kMX`, `agentkeel_drill_agent-jUPi0ADoVd`,
`agentkeel_festival_desk-379Sz3GgxZ`; owner-check's,
`agentkeel_owner_check-G4vMbRB3Dx`, was deleted by the retire job on
2026-10-03) and its endpoint; the agent role and its policies; the security
group and its two egress rules; the application inference profile; for
festival-desk the door: HTTP API `ohw3eeegoa`, its authoriser, route, stage
and integration, the two Lambda functions and their permissions, the
subscription filter to `agentkeel-calls`, the pool's clients, resource
server and user `lantern-desk`.

**Retained by the construct's policy, deleted by hand under this ruling:**

| Agent | Key (`alias/agentkeel-<name>`) | Table | Other |
|---|---|---|---|
| owner-check | `23a1ee05-87e8-440e-93fc-61e7c85beebd` | `agentkeel-owner-check-rights` | log group `/aws/bedrock-agentcore/runtimes/agentkeel_owner_check-G4vMbRB3Dx-DEFAULT`; marker `/agentkeel/marker/owner-check/rights-table-digest`; ECR `agentkeel/owner-check` |
| window-check | `7eaab44d-b441-492a-9ce0-b195d64ff805` | `agentkeel-window-check-rights` | log group `…/agentkeel_window_check-YBt5st7kMX-DEFAULT`; marker; ECR `agentkeel/window-check` |
| drill-agent | `bd223f80-0bcf-4210-9895-d682d162a4fe` | `agentkeel-drill-agent-rights` | log group `…/agentkeel_drill_agent-jUPi0ADoVd-DEFAULT`; marker; ECR `agentkeel/drill-agent` |
| festival-desk | `122a23f1-3907-4f6d-9d5b-43b6dadb209b` | `agentkeel-festival-desk-rights` | pool `us-west-2_f8kyzKF0P` and its domain `agentkeel-festival-desk-581208540944` (RetainExceptOnCreate); guardrail `at8e36cosq1r` and its version 1; log groups `/agentkeel/doors/festival-desk/access`, `/aws/lambda/agentkeel-festival-desk-door-authoriser`, `/aws/lambda/agentkeel-festival-desk-door-proxy`, `…/agentkeel_festival_desk-379Sz3GgxZ-DEFAULT`; marker; ECR `agentkeel/festival-desk` |

Each key is scheduled with the seven-day window, not deleted at once; the
key policies deny `kms:ScheduleKeyDeletion` to every platform role and to
agent roles, not to the admin (R4). No retained record depends on any of
the four keys: the tables use DynamoDB's default key and the audit bucket
is S3-managed (`f7_2_removed_and_kept.md`, "What the key encrypts").

**Kept, by design, and not touched:** the registry rows (with
`retired_at`; `claim` refuses the name afterwards, so none of the four can
be deployed again under its name); every object under `agents/<name>/`,
`envelopes/agents/<name>/`, `bundles/<name>/` and `calls/agents/<name>/`
in the security account's audit bucket, which `observe_drill.py` and
`observe_caller.py` on `main` still read; the four repositories, archived
by the owner so the platform check skips them; AgentCore's network
service-linked role; the security account's `agentkeel-calls` destination
and Firehose, which are the platform's, not festival-desk's.

## Order

1. The six open pull requests closed (drill-agent #5 and #6, window-check
   #4 and #5, festival-desk #2 and #5), so no scheduled run deploys or
   retires while the stacks are deleted.
2. One stack at a time: `delete-stack`, `wait stack-delete-complete`,
   `registry.py retire` (not for owner-check, already retired), then the
   retained resources. festival-desk's pool domain before its pool.
3. The read-back recorded in `milestones/maintenance/README.md` under this
   ruling: each stack's `DELETE_COMPLETE` time, each key's `DeletionDate`,
   the four registry rows as read after, and
   `list-stacks` showing `agentkeel-refagent` and `agentkeel-label-impact`
   alone.

## Unsure

- Whether Product wants finding 1 carried into SPEC/07 §11 as an open item
  (a Product PR). This ruling records it here only.
- The `run_id` written on the three registry rows is the string
  `by-hand-2026-11-02`, not a workflow run id. `registry.py retire` takes
  any string; the row's reader (`platform_check.py deployable`) reads
  `retired_at` alone.
