---
# Maintenance PR #59. Security's key over the by-hand deletion of four
# agent stacks in the agent account after the m10 close, and two findings
# on the platform's retire and upgrade paths. The M10 close ruled "nothing
# is deleted without a Security ruling"
# (milestones/M10/rulings/pr4-security.md, "What stands in AWS after the
# close"); this is that ruling. Product's file for the README row is
# retire-four-agents-product.md. The security-reviewer's read of the first
# draft (0 BLOCK, 6 FINDING, 6 NOTE) is in the PR body; its repairs are
# taken here.
ruling: retire-four-agents
seat: Security
authorises:
  - milestones/maintenance/rulings/retire-four-agents.md
evidence:
  - SPEC/07-upgrade-retire-surfaces.md
  - SPEC/09-per-agent-rules.md
  - milestones/README.md
  - milestones/M07/runs/f7_2_removed_and_kept.md
  - milestones/M07/runs/f7_2_retire.yaml
  - milestones/M10/rulings/pr4-security.md
  - infra/construct/governed_agent.py
  - scripts/platform_check.py
  - scripts/platform_upgrade.py
  - scripts/registry.py
  - https://github.com/agentkeel-studio/drill-agent/pull/6
  - https://github.com/agentkeel-studio/window-check/pull/5
  - https://github.com/agentkeel-studio/festival-desk/pull/5
  - https://github.com/andaro74/agentkeel/actions/runs/41454360702
  - https://github.com/andaro74/agentkeel/actions/runs/41455395838
  - https://github.com/andaro74/agentkeel/actions/runs/41456176090
pr: 59
---

# Ruling: maintenance PR #59, Security

Ruled by andaro74 as Security, 2026-11-07, as written.

## What is ruled

The human with admin, by hand, in the agent account (581208540944,
us-west-2):

1. retires `festival-desk` through the platform's own path (SPEC/07 §2:
   the retire workflow dispatched, the one-line pull request merged, the
   retire job on `main`'s schedule removing the runtime and the door and
   writing `retired_at` and `envelopes/agents/festival-desk/retired.json`);
2. retires `window-check` and `drill-agent` by hand, because the platform's
   path refuses them (finding 1): their stacks deleted, `retired_at`
   written on their registry rows with `scripts/registry.py retire`;
3. deletes the stacks `agentkeel-owner-check` (retired 2026-10-03 by the
   retire job, stack kept by design) and, after step 1,
   `agentkeel-festival-desk`;
4. deletes the resources the construct retains, named below, for all four.

`agentkeel-refagent`, `agentkeel-label-impact`, `AgentkeelBootstrap`,
`AgentkeelAudit`, `AgentkeelIngest`, `AgentkeelGrafana`, the registry
table itself and everything in the security account are not touched.

Why: the four agents exist for closed milestones (owner-check and
window-check for M07, drill-agent for M08, festival-desk for M09 and M10).
Nothing on `main` calls their runtimes. What `main` still reads of them,
and what it reads after this ruling: `observe_drill.py` and
`observe_caller.py` read records already in the audit bucket, unchanged;
`observe_upgrade.py --read aws` on every `evals.yml` run reads the
registry, each named agent's runtime image and its ECR repository, and
`observe_rules.py --read guardrail` reads festival-desk's pin by
`get_guardrail`; after the deletions those reads record an error
(`RepositoryNotFound` is not the `ImageNotFound` the observer reads as
empty), recorded and never gated (SPEC/07 §4; `evals.yml`: "It never fails
the job"), and rows 7 and 9 cite fixed envelopes (`dee74c3`, `c503324`),
so no ledger cell moves. Those reads go unread from now on, by this
ruling. drill-agent is leaky by design (SPEC/08 §2, a3) and festival-desk
holds a public door. Each agent costs about $1 a month in its key and
cents in its table and logs.

## Finding 1: the platform's retire path refuses an agent two platform versions behind

The retire workflow was dispatched on 2026-11-02 for window-check (an
earlier dispatch had opened its pull request; run 41454360702 read "the
branch platform-retire exists; nothing is opened twice"), for owner-check
(41455395838: "no agent named owner-check has a head the platform's App
passed, or it is already retired", correct) and for drill-agent
(41456176090: "opened #6"). The `agentkeel-upgrades` App opened the
one-line draft pull requests SPEC/07 §2 describes: window-check #5 (head
`5f7b665`), drill-agent #6 (head `ed642a8`). Each agent repository's
ruleset (`infra/ruleset/agent.json`) requires the `platform-check` check
from the `agentkeel-platform` App before any merge, and that check, which
runs `main`'s `src/validate/agent.evaluate` at m10, refused both heads
with the same two lines, verbatim:

> the platform's guardrail: manifest.yaml: guardrail {'id': '1088aw3ujhyd', 'version': '5'} is not the platform's {'id': '1088aw3ujhyd', 'version': '6'} (SPEC/06 section 6, item 6: one guardrail for every agent at M06; an agent with rules/ pins its own)
>
> an agent's manifest says who may call it, even if nobody: callers: callers: missing; an agent's manifest says who may call it, even if nobody (`callers: []`)

Both agents are at platform m06 or m07; the guardrail moved to version 6
at M09 and `callers` arrived at M10. The same check refuses each one's
"Platform upgrade to m10 (major)" pull request (window-check #4,
drill-agent #5): the manifest is the agent's own file, and SPEC/07 §1 says
a major upgrade is one "the platform check at the new version refuses the
agent's default-branch head as it stands", with no path but a person's
edit. So an agent left behind can neither take the upgrade nor retire
through the platform without a person's edit to its manifest, a deploy at
m10, and only then a retirement; and the retire job would itself refuse a
retire head whose manifest moved any field but `rollout`
(`scripts/retire_agent.py same`). What the ledger measured for the
retirement is row 7's `F7_2 held 368 s` on owner-check, an agent at the
platform's own version (row 7 is RED on F7_0, `milestones/README.md`);
the agent left behind is the case it did not cover, and SPEC/07 §8 does
not list it. Nothing in the platform is changed by this ruling: the
project is closed, and the repair (a retirement validated against the
platform version the agent was deployed at, not the newest) is written
down here and not built.

So for window-check and drill-agent the platform's retirement record
(`envelopes/agents/<name>/retired.json`, written once by the retire job in
the security account) is not written. Their record is this ruling, the
registry row (`retired_at`, `retired_commit` the deployed commit,
`retire_run_id` the string `by-hand-2026-11-02`), and CloudTrail's
`DeleteStack` and `DeleteAgentRuntime` events in `agentkeel-audit`. This
ruling makes the admin a second writer of one field on two registry rows;
`deploy.yml` on `main` is otherwise the registry's one writer (SPEC/06
§2). The table is not write-once; accepted by name.

## Finding 2: the platform upgrade moves an own-rules agent's guardrail pin to refagent's

festival-desk's `main` (`747c836`, the deployed commit) pins its own
guardrail `at8e36cosq1r` version 1 and lists its caller, as SPEC/09 §2 and
SPEC/10 §2 require. Its "Platform upgrade to m10 (minor)" pull request
(#5, head `5ebb4c7`) is refused by the check with:

> the agent's own guardrail: manifest.yaml: guardrail {'id': '1088aw3ujhyd', 'version': '6'} is refagent's; an agent with rules/ is guarded by its own, built from them on the baseline, not by refagent's six topics (SPEC/09 section 2; R10)

That refusal is the upgrade's doing, not festival-desk's: `platform_upgrade.py`
treats `guardrail` as a platform-owned manifest field (`MANIFEST_FIELDS`,
SPEC/07 §2) and moved the pin to refagent's, which SPEC/09 §2 made the
agent's own for an agent with `rules/`. A retire head moves `rollout`
alone (`retire_agent.py entry_errors`), so festival-desk's retire head
keeps its own pin and is expected to pass the check: the retire workflow
was not dispatched for festival-desk on 2026-11-02, and step 1 above is
that dispatch. If the check refuses the retire head after all, festival-desk
is retired by hand as window-check and drill-agent are, and the refusal
is quoted in the read-back. Whether SPEC/07 §2 gains the amendment (the
guardrail field is platform-owned only for an agent without `rules/`) is
Product's; recorded here, not built.

## What each deletion removes and what it keeps

Read from the stacks on 2026-11-02 (`describe-stack-resources`), the
construct's removal policies (`infra/construct/governed_agent.py` lines
285, 448-450, 531-532, 640, 647, 711, 716, 730) and
`milestones/M07/runs/f7_2_removed_and_kept.md`.

**Removed by `delete-stack`** (no removal policy in the construct): the
runtime (`agentkeel_window_check-YBt5st7kMX`,
`agentkeel_drill_agent-jUPi0ADoVd`; festival-desk's
`agentkeel_festival_desk-379Sz3GgxZ` and owner-check's
`agentkeel_owner_check-G4vMbRB3Dx` are removed by their retirements) and
its endpoint; the agent role and its policies; the security group and its
two egress rules; the application inference profile; for festival-desk,
what the retirement's stack update has not already removed of the door:
HTTP API `ohw3eeegoa`, its authoriser, route, stage and integration, the
two Lambda functions and their permissions, the pool's two clients, its
resource server and its domain `agentkeel-festival-desk-581208540944`.

**Retained by the construct's policy, deleted by hand under this ruling:**

| Agent | Key (`alias/agentkeel-<name>`) | Table | Other |
|---|---|---|---|
| owner-check | `23a1ee05-87e8-440e-93fc-61e7c85beebd` | `agentkeel-owner-check-rights` | log group `/aws/bedrock-agentcore/runtimes/agentkeel_owner_check-G4vMbRB3Dx-DEFAULT`; marker `/agentkeel/marker/owner-check/rights-table-digest`; ECR `agentkeel/owner-check` |
| window-check | `7eaab44d-b441-492a-9ce0-b195d64ff805` | `agentkeel-window-check-rights` | log group `…/agentkeel_window_check-YBt5st7kMX-DEFAULT`; marker; ECR `agentkeel/window-check` |
| drill-agent | `bd223f80-0bcf-4210-9895-d682d162a4fe` | `agentkeel-drill-agent-rights` | log group `…/agentkeel_drill_agent-jUPi0ADoVd-DEFAULT`; marker; ECR `agentkeel/drill-agent` |
| festival-desk | `122a23f1-3907-4f6d-9d5b-43b6dadb209b` | `agentkeel-festival-desk-rights` | pool `us-west-2_f8kyzKF0P` with its user `lantern-desk` (both RETAIN_ON_UPDATE_OR_DELETE; the user goes with the pool); guardrail `at8e36cosq1r` and its version 1 (RETAIN); log groups `/agentkeel/doors/festival-desk/access` with its subscription filter to `agentkeel-calls` (both RETAIN; the filter goes with the group), `/aws/lambda/agentkeel-festival-desk-door-authoriser`, `/aws/lambda/agentkeel-festival-desk-door-proxy`, `…/agentkeel_festival_desk-379Sz3GgxZ-DEFAULT`; marker; ECR `agentkeel/festival-desk` |

The runtime's own log group, the marker and the ECR repository are in no
stack. Each key is scheduled with the seven-day window, not deleted at
once; the key policies deny `kms:ScheduleKeyDeletion` to agent roles and
to the platform roles by name and allow the account's admin (R4). No
retained record depends on any of the four keys: the tables use DynamoDB's
default key and the audit bucket is S3-managed
(`f7_2_removed_and_kept.md`, "What the key encrypts").

**Kept, by design, and not touched:** the registry rows (with
`retired_at`; `registry.py claim` refuses the name afterwards, so none of
the four can be deployed again under its name); every object under
`agents/<name>/`, `envelopes/agents/<name>/`, `bundles/<name>/` and
`calls/agents/<name>/` in the security account's audit bucket;
AgentCore's network service-linked role; the security account's
`agentkeel-calls` destination and Firehose, which are the platform's, not
festival-desk's. Nothing in the security account names the four agents by
name: the audit bucket's policy admits template agents by role path and
tag.

## The role the deletes run under

Every one of the four stacks was created and updated with
`--role-arn arn:aws:iam::581208540944:role/agentkeel-cfn-exec`, and a
`delete-stack` with no `--role-arn` runs as the role the stack holds: the
execution role, inside the deploy boundary. Two refusals are on record for
that role and may recur: a security group whose two AgentCore network
interfaces are still attached is refused (`f7_2_removed_and_kept.md`: two
`in-use` four and a half hours after owner-check's runtime went; AWS says
up to eight hours), and the boundary denies every `logs:Delete*`, which a
door stage's access-log delivery may need (`infra/bootstrap/app.py`,
"DeleteLogDelivery ... is left out"; M10 pr3 C, "no doored agent has been
retired": festival-desk's deletion is where that is read, and the result
is recorded either way). So the Order below runs each delete as the
stack's own role, reads `describe-stack-events` on a `DELETE_FAILED`, and
retries: after the interfaces are gone for a security group; with
`--retain-resources <logical ids>` for a resource the boundary refuses,
which the admin then deletes by hand, named in the read-back. No new IAM
is made.

## Order

1. The five upgrade and seed pull requests closed (drill-agent #5 and #6,
   window-check #4 and #5, festival-desk #2 and #5), so no scheduled run
   deploys or retires while the stacks are deleted. festival-desk's retire
   pull request, once opened, is the one that is merged.
2. festival-desk retired through the platform: `gh workflow run deploy.yml
   -f retire=festival-desk`; the draft pull request's check green; merged
   with a merge commit; the retire job's run on the next schedule read:
   `get-agent-runtime` on `agentkeel_festival_desk-379Sz3GgxZ` answers
   `ResourceNotFoundException`, the row carries `retired_at`,
   `envelopes/agents/festival-desk/retired.json` is in the audit bucket.
3. One stack at a time, window-check, drill-agent, festival-desk,
   owner-check: `describe-network-interfaces` for the stack's security
   group, `delete-stack`, `wait stack-delete-complete`; on `DELETE_FAILED`
   the events read and the retry above; then `registry.py retire`
   (window-check and drill-agent only); then the retained resources from
   the table.
4. Each repository archived on GitHub once its row says `retired_at`:
   `platform_check.py` lists repositories `if not archived`, and that,
   not `retired_at`, is what takes an agent out of every scheduled run
   (`platform-check.yml` every five minutes, `deploy.yml` every ten; a
   default-branch head whose commit differs from the row's would otherwise
   stay in the deploy list and be refused at `registry.py claim` on each
   run).
5. The read-back recorded in `milestones/maintenance/README.md` under this
   ruling: each security group's interfaces before the delete, each
   stack's `DELETE_COMPLETE` time and any `DELETE_FAILED` reason and
   retry, each key's `DeletionDate`, the four registry rows as read,
   festival-desk's retire run and its `retired.json`, and `list-stacks`
   showing `agentkeel-refagent` and `agentkeel-label-impact` alone.

Nothing mechanical gates any step of this ruling: the admin holds
`kms:*` by each key policy, `DeleteStack` as the account's admin, and the
registry's `PutItem`. The gates on this PR read the ruling file, not the
account. The record is this file and CloudTrail under `AWSLogs/` in the
security account (R5), which no platform role can delete.

## Made before this file was ruled

The deletions were made on 2026-11-06 and 2026-11-07 while this file read
Drafted, as the owner chose; the read-back in `milestones/maintenance/README.md`
records each attempt and what stood after. Finding 2 held: festival-desk's
retire head passed the check and the platform retired it (run 42329724674).
M10 pr3 C is now read: the first delete of festival-desk's door stage was
refused on `logs:DeleteLogDelivery` by the deploy boundary, and the retry
completed it.

## Unsure

- Whether Product carries finding 1 and finding 2 into SPEC/07 §8 or
  SPEC/00 §12 as open items (a Product PR). This ruling records them here
  only.
- Whether festival-desk's retire head passes the check (finding 2 says it
  is expected to). Settled by the dispatch in step 2.
