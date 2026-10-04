# Incident runbook — a hostile agent

For the on-call (one person; every seat, R1). Drafted by `incident-responder`
at M08 PR 1, committed by Product at M08 PR 2 (SPEC/08 §6, §10 amendment 2).
It is followed for the first time during the M08 game-day drill (run 1), and
again whenever a real agent misbehaves.

Four steps: detect, quarantine, forensics, restore. Nothing here is
automatic. No alarm, Lambda, EventBridge rule or workflow attaches the
quarantine; the platform records, a person acts (SPEC/08 §2, §8).

## 1. Detect

A person reads the audit bucket in the security account as
`agentkeel-audit-read` (`hector.flores`, console or CloudShell). Nothing
pages you; the records are there to be read, not to alert.

What a hostile agent leaves, and where:

- an API call it was refused: a CloudTrail record under
  `AWSLogs/<account>/CloudTrail/…`, with an `errorCode` of `AccessDenied`;
- a connect its security group dropped: a VPC flow record under
  `AWSLogs/<account>/vpcflowlogs/…`, reading `REJECT`;
- a credential it leaked into an answer: the answer record under
  `envelopes/agents/<agent>/<commit>.json`, where `build.carries_credential`
  read the key and failed that golden.

A connect the VPC's missing route drops leaves **nothing** — no flow record
and no trail event (M05 S1). The agent's own log under
`agents/<agent>/events/` is an **index, not a reading**: take the request ids
from it and look each up in the trail. An attempt you cannot find in AWS's
own record is unread, not refused (P5).

## 2. Quarantine

Attach `agentkeel-quarantine` (Deny `*` on `*`) to the agent's role by hand.
The command is the one in [`infra/audit/README.md`](../../infra/audit/README.md),
**with the stack name substituted** for the agent you are containing — for
the drill, `agentkeel-drill-agent`, not `agentkeel-refagent`:

```sh
ROLE=$(aws cloudformation describe-stacks --region us-west-2 --stack-name agentkeel-drill-agent \
  --query "Stacks[0].Outputs[?OutputKey=='AgentRoleArn'].OutputValue" --output text | sed 's#.*/##')
aws iam attach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::581208540944:policy/agentkeel-quarantine
```

Keep the output with `2>&1`. Quarantining the wrong role leaves the hostile
agent acting and gives F8.5 no call of the right role to read (SPEC/08 §2).

**The time from the first attempt to the attach is your reaction time.** It
is recorded and held to no bar: no SLA is claimed for a person noticing.

**A caveat (the M05 S7 hazard).** Under a role-wide deny-all the runtime may
not start at all — it cannot pull its image, write its logs or call its model
— so its attempts never run and no call by that role reaches the trail. Then
there is no refused call to read, which reads as *unread*, not as the
quarantine having failed. A miss here is the finding, not a pass (SPEC/08 §2).

## 3. Forensics

Read, prefix by prefix, as `agentkeel-audit-read`:

- `AWSLogs/` — the trail and the flow records (a1, a4, a5, a6's only records);
- `agents/<agent>/` — the agent's own event log (an index, above);
- `envelopes/agents/<agent>/` — the answer record (a3);
- `observations/` — any stored observation.

For each attempt: request id → the trail record → its `eventTime` (AWS's
time, never a person's) and the time its object reached the bucket
(`LastModified`). The gap is the attempt's detection latency.

Read each record's completeness (F8.4): is it there, in one version, under a
lock, and was it last written no later than its run closed? The audit
bucket's lock is COMPLIANCE for one day (R5); after that a record rests on
the bucket's policy and the account's boundary, not on the lock. An expired
lock is not a protection and nothing here calls it one (SPEC/08 §8).

`bundles/` is list-only for this role: its retention is not read here.

## 4. Restore

Recover the agent, in this order:

1. Remove the hostile behaviours from its `agent.py` and declare any endpoint
   it needs; open the pull request, let the platform check pass it, merge, and
   let it deploy.
2. If an egress rule was added by hand for a drill (run 2), remove it — a
   change to a live boundary, so under a Security ruling that reads "Ruled
   by", with the diff kept.
3. Detach the quarantine:
   ```sh
   aws iam detach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::581208540944:policy/agentkeel-quarantine
   ```
4. Ask it its goldens. Its answer record should read GREEN, with no refusal
   by its role and no `REJECT` flow in the window, and its registry row should
   read as any agent's (SPEC/08 §2, run 3).

Retirement is one-way: a retired agent is not un-retired (SPEC/07). Restore
by fixing and redeploying, not by reviving a retired runtime.
