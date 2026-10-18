---
# M10 PR 3 (#56), the repair. Security's key over the Security paths this PR
# touches: the bootstrap stack and its regenerated NagReport, the construct's
# pool and docstring, and the security stack's calls delivery (the subscriber
# role's trust and the destination's policy). Each repair answers a refusal
# the platform's own deploy path met between PR 2's merge and the first door
# that stood (milestones/M10/README.md, "Repair detail (PR 3, 2026-10-16)").
# Product's file is rulings/pr3.md; Engineering's (with the cold review) is
# pr3-engineering.md.
ruling: pr3-security
seat: Security
authorises:
  - infra/bootstrap/app.py
  - infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv
  - infra/construct/governed_agent.py
  - infra/security/app.py
evidence:
  - SPEC/00-overview.md#8-M10
  - SPEC/10-public-caller.md
  - milestones/M10/README.md
  - milestones/M10/rulings/pr2-security.md
  - https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-logging.html
  - https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CreateDestination.html
pr: 56
---

# Ruling: M10 PR 3, Security

DRAFT. Ruled by: pending.

## How the by-hand deploys stand to this file

Both hand-deployed stacks were deployed from this branch before this file
was ruled, each to answer a refusal and let the next deploy go on: the
bootstrap three times (2026-10-16 04:26Z; 2026-10-17 16:58Z; after the
log-delivery grant), the security stack twice from CloudShell as a plain
template (2026-10-17, PR 2's delivery; 2026-10-18, the subscriber role's
trust). This is M09's carry, "deploy on an unsigned draft ruling", again,
and the cold review's F1. Ruling this file is what makes those deploys
ruled. The destination policy narrowed after the seat reads (security F3)
is deployed by hand after this file is ruled, not before.

## What this PR changes, each from the refusal that named it

| # | Refusal | Repair |
|---|---|---|
| 1 | bootstrap deploy, 2026-10-16: "Maximum policy size of 10240 bytes exceeded for role agentkeel-cfn-exec" | DoorGrants is a customer managed policy (`agentkeel-cfn-exec-door`) |
| 2 | festival-desk deploy run 38997315544: the stage could not read its log group's ARN (`logs:DescribeLogGroups`); `logs:PutSubscriptionFilter` not authorised on the destination | DescribeLogGroups on `*`; PutSubscriptionFilter on the one destination's ARN |
| 3 | run 39052047504: "Insufficient permissions to enable logging ... logs:CreateLogDelivery" | six vended-delivery actions on `*`; `DeleteLogDelivery` left to the deploy boundary's deny |
| 4 | each failed first deploy left a pool behind: 55 | the pool and its users `RetainExceptOnCreate`; the log groups stay `Retain` |
| 5 | run 39076739413's three access-log lines: DeliveryErrors 1, nothing under `calls/agents/` | the subscriber role trusts Logs on behalf of both accounts |
| 6 | security F3 below | the destination admits `role/agentkeel-cfn-exec` alone |

## What this seat accepts by name

- **`logs:PutResourcePolicy` on `*`, and the log-delivery grants with PR 2's
  `/apis/*`** (security F1, F2; cold F2). They reach the whole shared
  account: any named Logs resource policy in the region, the access log of
  any HTTP API. The deploy boundary does not cap them, and a policy written
  this way is not removable by the deploy plane. Accepted for the door's
  stage, with a test that the construct writes no `AWS::Logs::ResourcePolicy`.
  The `aws:ViaAWSService` condition the read proposes is not taken here: it
  is unmeasured, and the only reader of it is a door deploy that fails if it
  is wrong. It is PR 4's to try on a throwaway agent or to leave standing.
- **`DeleteLogDelivery` not granted** (security N7; cold N3). A stage's
  delete, a change of its log destination, or a retirement of a doored agent
  may end in `DELETE_FAILED` or `UPDATE_ROLLBACK_FAILED`. Unmeasured; carried.
- **`RetainExceptOnCreate` has not fired** (security N6). The 55 orphans
  were deleted by hand. Not described as working.

## Seat report: security-reviewer on PR 3 (verbatim)

Dispositions: F1 accepted by name above, reason text corrected; F2 accepted
by name, reason text names the reach; F3 repaired (99e6807, the destination
admits the execution role alone, a test holds it); F4 repaired (99e6807, the
reason says what the boundary caps); F5 repaired (99e6807, the docstring
says a removed subject's user stays); N13 repaired (55, in the construct,
the test and the README). N6, N7, N9 carried to PR 4 in pr3.md's Unsure.

> Security seat report: M10 PR 3 (repair), branch m10-pr3 against 917601d. This is a draft for the PR body, not a ruling.
>
> I could not run `git diff` because this session has no shell. I read the files as they stand on the branch: infra/bootstrap/app.py, its NagReport CSV, infra/construct/governed_agent.py, infra/construct/door.py, infra/security/app.py and milestones/M10/README.md lines 167-246. I took what is new in PR 3 from the "M10 PR 3" comments and the repair detail. This PR touches no workflow, no key policy and no egress rule, so checks 1, 4 and 5 have nothing to read here.
>
> **Findings**
>
> - **FINDING 1. `logs:PutResourcePolicy` on `*` reaches the account's shared Logs resource policies.** infra/bootstrap/app.py:917-922: `actions=[... "logs:PutResourcePolicy", "logs:DescribeResourcePolicies"], resources=["*"]`.
>   - In account 581208540944 this lets the execution role create or overwrite any named Logs resource policy in us-west-2. Other projects in the account share those policies, and the quota is ten per region.
>   - An overwrite can remove another project's delivery grant. It can also let a service principal `logs:PutLogEvents` into any log group, including `/agentkeel/doors/*/access`, which is the source of the call records.
>   - The deploy boundary does not cap this. Its Allow is `"*"` (line 431), and its Deny lists no `PutResourcePolicy` (lines 445-448).
>   - Because `logs:Delete*` is denied, a policy written this way cannot be removed by the deploy plane either.
>   - Anything that runs as the execution role can use it. That is every `stack/agentkeel-*` template that deploy.yml applies from main, so a template that declares `AWS::Logs::ResourcePolicy` would be honoured.
>   - What would settle it: add the condition `Bool aws:ViaAWSService: true` to the six vended-delivery actions, so only API Gateway's forward-access call can use them and a template's own call cannot. Prove it on one door deploy, and add a test that no agent template carries `AWS::Logs::ResourcePolicy`. If the condition breaks the deploy, the reason text must say the grant is account-wide and uncapped. Security rules.
> - **FINDING 2. The log-delivery grants plus PR 2's API grant reach every HTTP API in the account.** infra/bootstrap/app.py:919 `logs:CreateLogDelivery`, `logs:UpdateLogDelivery` on `*`, together with :884-887 `apigateway:PATCH ... /apis/*`.
>   - Together they let the execution role repoint the access log of any HTTP API in the shared account, not only a door's.
>   - The `/apis/*` breadth was ruled in PR 2. PR 3 adds the delivery half.
>   - What would settle it: Security rules whether the reason text names this reach, or whether the API grant is held by an `aws:ResourceTag` condition where API Gateway supports one. Security rules.
> - **FINDING 3. The trust repair makes a forgery path live.** infra/security/app.py:485-488 now trusts Logs for `aws:SourceAccount: [SECURITY_ACCOUNT, AGENT_ACCOUNT]`. The trust is still bound to the two accounts, so it does not reopen the cross-account confused deputy. But:
>   - infra/security/app.py:501, from PR 2, is `"Principal": {"AWS": AGENT_ACCOUNT}`. Any principal in the shared agent account that holds `logs:PutSubscriptionFilter` can subscribe any log group to `agentkeel-calls`.
>   - The stream keeps only the message (line 469, `DataMessageExtraction`) and partitions on the line's own `.agent` (line 471). A line from any log group that claims `"agent": "festival-desk"` lands under `calls/agents/festival-desk/`, and the reader cannot tell it from a door's line.
>   - Before PR 3 every agent-account event was refused, so this path was dead. The repair is what makes it live.
>   - What would settle it: narrow the destination policy's principal to `arn:aws:iam::581208540944:role/agentkeel-cfn-exec`. Its own `PutSubscriptionFilter` is held to the door log groups (bootstrap app.py:896-898). Then add a seeded case: a subscription from another principal is refused. Security rules, and the Data Owner rules the record's shape if the log group is to be carried.
> - **FINDING 4. Two sentences in the cdk-nag suppression are untrue.**
>   - infra/bootstrap/app.py:1726 says "The deploy boundary (seed S4) caps it." The boundary caps none of the six vended-delivery actions or `DescribeLogGroups`. It denies only `logs:Delete*` among logs actions.
>   - infra/bootstrap/app.py:1737 appends `{CEILING}` (line 1663: "A ceiling, not a grant: a Deny must cover every resource..."). DoorGrants is a grant, not a ceiling, and holds no Deny.
>   - Both sentences appear in every DoorGrants row of AwsSolutions--AgentkeelBootstrap-NagReport.csv (lines 42-49).
>   - What would settle it: replace both with what is true: "the deploy boundary caps only its logs:Delete*; PutResourcePolicy is account-wide and uncapped". Security rules.
> - **FINDING 5. A construct docstring claim is untrue.** infra/construct/governed_agent.py:619 says "a subject removed from the list removes that user and no other." With line 643 (`RETAIN_ON_UPDATE_OR_DELETE` on each user), removing a subject keeps the user and the credential the owner set.
>   - The authoriser still refuses it, because infra/construct/door.py:100 checks `claims.get("username") in CALLERS`. So admission holds, but the sentence is false.
>   - Re-admitting the same subject later will fail with "user already exists" and roll the update back.
>   - What would settle it: correct the sentence. The Tool Owner rules on removal semantics; Security rules on the retained credential.
>
> **Notes**
>
> - **NOTE 6. RetainExceptOnCreate cannot delete a pool that holds a credential under the stated process.** infra/construct/governed_agent.py:636 `pool.apply_removal_policy(cdk.RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE)`.
>   - CloudFormation deletes the pool only when the operation that created it rolls back. Credentials are set by hand after a successful deploy (SPEC/10 §5.1).
>   - If an update replaces the pool and succeeds, the old pool and its credentials are retained but orphaned. The admitted caller is then refused, and the old pool stays tagged and readable by the deploy role (bootstrap app.py:992-997).
>   - This repair has not fired on its seeded case: no failed first deploy has run since, and the orphans were deleted by hand. Do not call it working.
>   - What would settle it: one deliberately failed first door deploy on a throwaway agent, with the pool count read before and after. Engineering measures; Security rules.
> - **NOTE 7. `logs:DeleteLogDelivery` is left out on purpose.** infra/bootstrap/app.py:914-916.
>   - A stage delete or a rollback after the stage exists may end `DELETE_FAILED` or `UPDATE_ROLLBACK_FAILED`. This is unmeasured.
>   - What would settle it: the same throwaway failed deploy as NOTE 6, failed after the stage is made. Security rules.
> - **NOTE 8. `logs:DescribeLogGroups` on `*`** (infra/bootstrap/app.py:906-910). It is read-only and lists every log group name, retention and KMS key in the shared account. `ListLogDeliveries` and `DescribeResourcePolicies` (line 920) likewise read other projects' configuration. The stated reason is specific and true.
> - **NOTE 9. "None of which takes a resource" is unverified for `logs:PutResourcePolicy`.** infra/bootstrap/app.py:1735. My understanding is that CloudWatch Logs has recently added resource-scoped resource policies, but I could not check that here. What would settle it: read the Service Authorization Reference row for this action and quote it in the reason. Security rules.
> - **NOTE 10. `PutSubscriptionFilter` is on the one destination ARN** (infra/bootstrap/app.py:923-927). It is the narrowest grant that works, it has no wildcard, and the destination's own policy still decides.
> - **NOTE 11. The move to a customer managed policy** (infra/bootstrap/app.py:928-932) carries the role's deploy boundary, through `PermissionsBoundary.of(self)` at line 285. The execution role cannot rewrite DoorGrants: `iam:CreatePolicyVersion` and `iam:DeletePolicy` are denied at :936, and `iam:CreatePolicyVersion` again by the boundary at :439.
> - **NOTE 12. The trust condition pairs its two keys independently** (infra/security/app.py:486-488). It would admit, for example, SourceAccount=security with SourceArn=agent. Logs sets the two consistently, so this has no effect in practice.
> - **NOTE 13. The orphan count differs.** The brief says 53 orphan pools. milestones/M10/README.md:212-214 and governed_agent.py:617 say four. Product to reconcile the prose against the account.
>
> **Can it be switched off from inside?** Everything here is in `infra/**`, which belongs to Security. The bootstrap and security stacks are deployed by hand, from CloudShell for the security stack. No workflow deploys either. Who can change a grant is whoever holds admin in the two accounts. Nothing in this PR gates that further.
>
> BLOCK: 0 · FINDING: 5 · NOTE: 8
