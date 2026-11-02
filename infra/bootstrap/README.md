# infra/bootstrap

Security seat. SPEC/00 §8 M01 and SPEC/01 §6, with
`milestones/M01/feasibility.md` §2.6 rulings a, b, d, e and f. Authorised
by `milestones/M01/rulings/pr2.md`.

Deployed **by hand, by the human with admin**, once, in the agent account,
during M01 PR 2 and before PR 2's first CI run (ruling f, ruling 4). It is
never deployed by CI: the roles CI uses are in it, so a pipeline that
could change it could widen its own permissions.

What it makes is listed at the top of `app.py`. Four things are worth
saying here.

**Two boundaries, one per plane** (ruling s). `agentkeel-boundary` is the
agent plane's allow-list; nothing in this stack carries it, and
`GovernedAgent` puts it on the agent role from the Security-owned
parameter. `agentkeel-deploy-boundary` is the deploy plane's deny-list and
is on every role this stack makes. The first version of this stack applied
the allow-list to everything, which left the execution role able to create
nothing and the Budgets stop unable to attach. When you create the role for
seed S6's attempt, attach **`agentkeel-boundary`** — the agent one.

**The break-glass admin is not in scope.** SPEC/01 §1: "a laptop" means
the developer role this stack creates, boundary on. Stopping the admin who
deploys this stack takes a service control policy, which is landing-zone
work (SPEC/00 §2, §12).

**The daily budget does not stop anything.** AWS Budgets Actions cannot
hang off a daily budget, so the figure the Threshold Owner ruled —
`daily_usd: 10` — notifies, and a second, monthly budget carries the Deny
that stops the eval role (ruling a, amended). Budgets data also refreshes
only up to three times a day. So what this stack bounds is a month's
Bedrock spend plus one refresh interval at the account quota, and a run
that spends the month's figure in an afternoon is stopped after it, not
during it. No smaller figure is invented.

**Two parameters are written by hand.** `GovernedAgent` reads seven
endpoint destinations from SSM. The five interface endpoints publish
their security group ids from this stack. The two gateway endpoints — S3
and DynamoDB (ADR-0006) — are reached through a managed prefix list, and
AWS gives no CloudFormation attribute for a prefix list id, so those two
parameters are written by the same human, with one command each, below.
Until they exist an agent stack does not deploy.

**The interface endpoints are in one subnet** (2026-11-01; deployed
2026-11-02, the record is at the end of this file). AWS bills an interface
endpoint by the ENI-hour, $0.01 in us-west-2. Five endpoints in both
subnets were ten ENIs: $74.40 for October 2026 (Cost Explorer, usage type
`USW2-VpcEndpoint-Hours`, read 2026-11-01), the largest line in the
account. In the first isolated subnet alone (index 0 of the region's AZ
list, `isolated_subnets[0]`; `subnet-00008bbb7a11551a0`, us-west-2a, in
the deployed account) they are five ENIs: 5 x $0.01 x 730 h = $36.50 a
month expected, plus cross-AZ transfer at $0.01 a GB each way for a runtime
placed in the other subnet, cents at eval volumes. Nothing the construct
reads changed: `SubnetIds` is a no-interruption update (the change set of
2026-11-02 read five Modify and no replacement), so each endpoint's
security group id and its parameter are the same, and
`/agentkeel/security/subnet-ids` still names both subnets. What was given
up is the second Availability Zone for the endpoints: an impairment of
us-west-2a now takes every interface endpoint from a runtime in
us-west-2b, including a new runtime's image pull. Shrinking `SubnetIds`
deletes the second ENI live, so deploy this change when no eval or runtime
call is in flight. A NAT gateway was looked at and not taken: $0.045 x
730 h = $32.85 a month before data, so no cheaper than this, and SPEC/01
§6 says no NAT.

**A proposal, not a change (Security's to rule):** the `kms` endpoint,
$7.30 a month in one subnet. AWS's list of endpoints a VPC-mode runtime
needs without internet access names ecr.api, ecr.dkr, the S3 gateway and
logs, not kms (docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-vpc.html,
"Required VPC endpoints", read 2026-11-01), and `agents/refagent/server.py`
opens s3, dynamodb and bedrock-runtime clients and no KMS client (a read of
the code, not of a run). Unknowns: the manifest comment says "kms: the
agent's key"; an in-VPC repeat of seed S6 would then be refused by the
network before the key policy, a different control reading from SPEC/01 §6;
and removing it is a change to every manifest's `endpoint_allowlist` and
to the construct's tests.

## One failure worth knowing about before you deploy

The first attempt failed on the KMS key:

```
CREATE_FAILED AWS::KMS::Key RefagentKey
"The new key policy will not allow you to update the key policy in the future."
```

The policy denied `kms:PutKeyPolicy` to every principal except a named
Security role and the account root. An IAM admin is neither, so the deny
covered the person running the deploy, and KMS will not create a key whose
policy locks out its own creator. The policy now names the principals it
refuses — agent roles by path, and the deploy, execution, eval and
developer roles — rather than excepting the ones it allows. The human with
admin can administer the key, which SPEC/01 §1 already puts in the landing
zone.

If a deploy fails this way again, the stack is left `ROLLBACK_COMPLETE`
and cannot be updated: delete it first. The ECR repository has
`RemovalPolicy.RETAIN`, so a rollback leaves it behind and the next create
fails on a name that already exists; delete that too when it holds no
images.

**An agent's stack whose first create fails** (M07, twice on 2026-10-02:
`milestones/M07/README.md`, "After PR 3 merged"). The stack
`agentkeel-<name>` is left `ROLLBACK_COMPLETE` and keeps what the
construct retains under fixed names: the agent's key, its alias once the
alias was made, and the rights table. Every later deploy run fails
before it starts, and no platform role can clear it: the deploy role has
no `DeleteStack`, and the key's policy denies its deletion to every
platform role. The account's admin, by hand, in this order:

```sh
aws cloudformation delete-stack --stack-name agentkeel-<name> --region us-west-2
aws cloudformation wait stack-delete-complete --stack-name agentkeel-<name> --region us-west-2
aws dynamodb delete-table --table-name agentkeel-<name>-rights --region us-west-2
aws kms delete-alias --alias-name alias/agentkeel-<name> --region us-west-2      # if the alias was made
aws kms schedule-key-deletion --key-id <the retained key> --pending-window-in-days 7 --region us-west-2
```

A key is scheduled, not deleted: it stays in the account for the window,
and the schedule can be cancelled. Each act is written in the
milestone's by-hand file with the principal and the time. Whether this
stays the admin's or becomes a named role is Security's, carried to M08
(platform-architect F3 on M07 PR 4; the landing zone's, deferred item 2).

**After any change to the execution role's runtime statements, one
create of a throwaway agent is made before a developer's**
(platform-architect F2 on M07 PR 4). M06 PR 2 narrowed those statements
and ran no create; the next one was a developer's, and it was refused
twice. What a create checks cannot be read without making one.

## Deploying it

```bash
# 1. As the admin, in the agent account, us-west-2.
aws sts get-caller-identity
cd infra/bootstrap
# `diff` takes no --parameters (CDK CLI 2.1137.0 warns and ignores it);
# only `deploy` does.
npx aws-cdk@2 diff
npx aws-cdk@2 deploy --parameters BudgetSubscriberEmail=<your address>
```

The email is a CloudFormation parameter, not a value in the repo:
CloudFormation requires at least one Budgets subscriber, and an address
belongs to a person, not to a git history.

On a **redeploy** the address can be left off: `deploy` defaults to
`--previous-parameters`, which keeps what the stack already holds. Pass it
again if you want to change it.

```bash
# 2. The two prefix lists, which CloudFormation cannot publish.
for service in s3 dynamodb; do
  id=$(aws ec2 describe-managed-prefix-lists --region us-west-2 \
        --filters "Name=prefix-list-name,Values=com.amazonaws.us-west-2.$service" \
        --query 'PrefixLists[0].PrefixListId' --output text)
  aws ssm put-parameter --region us-west-2 --type String --overwrite \
    --name "/agentkeel/security/prefix-list/$service" --value "$id" \
    --description "agentkeel: the $service gateway endpoint prefix list (ADR-0006)."
done
```

```bash
# 3. Point CI at the new eval role and at the deploy role, and check the
#    parameters are all there. Both variables, or a workflow fails at its
#    assume step: `evals.yml` reads AWS_EVAL_ROLE_ARN, `deploy.yml` reads
#    AWS_DEPLOY_ROLE_ARN. The second was missing until 2026-09-22, and the
#    first deploy on `main` (run 35683865472) failed on it before it failed
#    on anything else (M02 open.md row 9).
aws cloudformation describe-stacks --stack-name AgentkeelBootstrap \
  --query 'Stacks[0].Outputs' --output table
gh variable set AWS_EVAL_ROLE_ARN --body "arn:aws:iam::<account>:role/agentkeel-evals"
gh variable set AWS_DEPLOY_ROLE_ARN --body "arn:aws:iam::<account>:role/agentkeel-deploy"
aws ssm get-parameters-by-path --region us-west-2 --path /agentkeel/security --recursive \
  --query 'Parameters[].Name' --output table
```

Then the two attempts, S4 and S6: `milestones/M01/runs/f1_1_laptop.yaml`
and `milestones/M01/runs/f1_3_key_policy.yaml` say what to run and what to
write down. Every attempt's **request id** goes in the run file; PR 2's CI
run looks each one up in CloudTrail (`scripts/observe_attempt.py`) and
that lookup is what writes `checks.F1_1` and `checks.F1_3`. A file a human
wrote feeds no check by itself (SPEC/01 §4).

Done at M02 PR 3: `AgentkeelM00EvalRole` was destroyed by the human on
2026-09-23 (`DELETE_COMPLETE` at 13:48Z, read with `list-stacks`) and
`infra/eval-role/` removed in the same PR (ruling f; M02 open.md row 16).
The eval role this stack owns, `agentkeel-evals`, is what
`AWS_EVAL_ROLE_ARN` names.

## M03 PR 2, stop A: the narrowed deny and refagent's guardrail

One redeploy of this stack carries SPEC/03 §6's Security commits: every
guardrail action but `ApplyGuardrail` still denied, the rights table's
delete and scan and its marker, and the guardrail built from
`agents/refagent/rules/`. In this order, as the admin:

```sh
aws sts get-caller-identity                      # the admin: no permission boundary on it
python scripts/read_back_grants.py > before.md   # the rows the deploy will change show MISMATCH
cd infra/bootstrap && npx aws-cdk@2 diff         # read it before anything touches AWS
npx aws-cdk@2 deploy                             # a redeploy keeps the previous parameters
cd ../.. && python scripts/read_back_grants.py   # mismatches: 0
aws cloudformation describe-stacks --region us-west-2 --stack-name AgentkeelBootstrap \
  --query "Stacks[0].Outputs[?starts_with(OutputKey, 'Guardrail')]" --output table
aws bedrock get-guardrail --region us-west-2 --guardrail-identifier <id> --guardrail-version <version>   --query description                            # "rules sha256 <the digest the synth printed>"
python scripts/probe_guardrail.py --id <GuardrailIdForTheManifest> --version <GuardrailVersionForTheManifest>
```

The `get-guardrail` answer is the only read of what the deployed version
was built from: no platform role may read a guardrail (security-reviewer
on 0bb1d4a, F3), so it goes into `milestones/M03/runs/` with the probe's
table. The minified template is about 46.7 KB against CloudFormation's
51.2 KB inline limit; a deploy that refuses it as too large does so before
any change.

The id and version go into `agents/refagent/manifest.yaml` (Rule Owner),
and the probe's table into `milestones/M03/runs/`. Before the deploy the
guardrail does not exist, so `read_back_grants.py` skips the one row that
names it and says so.

## M03 PR 3, stop A: guardrail version 5

One redeploy, from a checkout of `0a90d52` with no tracked change, the
same commands as above with `cdk diff --strict`. `guardrail.yaml` gained a
`blocks` map naming the rule for each of its plants (rule-owner F1 on M03
PR 2), so the rules digest changed and the version was replaced: version
**5**, `rules sha256 b2cff2a1…`, READY; version 4 retained. The guardrail
itself, every IAM policy document and the VPC did not change;
`ParamGuardrail`'s description was corrected (security-reviewer N9 on PR
2). The ten metadata-only changes `--strict` printed are the suppression
reasons' `§`, which the deployed template read as `?`
(`milestones/M03/runs/pr3_stop_a_cdk_diff.md`).

`read_back_grants.py`, before and after, byte-identical: 81 cases,
mismatches 0 (`milestones/M03/runs/pr3_stop_a_read_back.md`). The two
rows `milestones/M03/open.md` row 8 asked for, run for the first time:

| Principal | Action | Resource | Decision | Expected |
|---|---|---|---|---|
| `agentkeel-boundary` (ceiling) | `dynamodb:Scan` | `*` | **allowed** | allowed |
| `agentkeel-boundary` (ceiling) | `dynamodb:PutItem` | `*` | implicitDeny | implicitDeny |

A simulation reads IAM, not the service. The minified template is 47,601
bytes at `0a90d52` against CloudFormation's 51,200-byte inline limit.

## What has been observed, and what has not

This stack was deployed by the human during M01 PR 2, and the two
attempts S4 and S6 were made against it on 2026-09-20; their request ids
are in the M01 run files and CloudTrail's record of each is what wrote
`checks.F1_1` and `checks.F1_3` in envelope `e97125e` (run 35680056132).

The first deploy of an **agent** stack through this stack's roles failed
twice on 2026-09-22 (run 35683865472, M02 open.md row 9): first because
`AWS_DEPLOY_ROLE_ARN` was not set, then at CREATE on the rights table,
because `TableEncryption.AWS_MANAGED` needs `kms:CreateGrant` and the
deploy boundary denies it. Nothing was half-built; the stack rolled back
and was deleted. The construct now uses `TableEncryption.DEFAULT`, and
`tests/test_bootstrap.py` reads a handler call the boundary denies before
a deploy does. The first agent stack deployed through these roles at M02
PR 2's merge (run 35817173042, `agentkeel-refagent` `UPDATE_COMPLETE` at
2026-09-23T04:11:23Z; row 10). Its runtime answered every golden with
`AccessDeniedException` on `dynamodb:Scan`: the boundary, not the role,
refused it, the first time the ceiling has refused a call. That was not a
seeded case (SPEC/01 §9 names the ceiling as a control without one); it
is recorded as an observation and nothing here calls the ceiling proven.

The boundary redeploy that followed (`c34da39`, `dynamodb:Scan` added):
`describe-stacks` on `AgentkeelBootstrap` reads `UPDATE_COMPLETE` with
`LastUpdatedTime` 2026-09-23T04:45:35Z, and the stack events between
04:45:35Z and 04:46:00Z name one resource, `BoundaryEA298153`
(`UPDATE_IN_PROGRESS` 04:45:39Z, `UPDATE_COMPLETE` 04:45:57Z), which is
the one line `cdk diff` showed. The first run after it in `mode: runtime`
is envelope `12b4646` (run 35861180676), GREEN.

The GitHub OIDC provider this stack imports by ARN predates the
repository; who created it and when is not recorded anywhere, and its
thumbprint and audience are landing-zone work (SPEC/00 §2). Until then
no sentence here or anywhere else may call the deploy plane proven
(SPEC/00 §10.5).

## M07 PR 2: three reads, one read-only role, and panel 2's table

Not ruled on 2026-10-02: `milestones/M07/rulings/pr2-security.md` items
13b, 13c and 13d put each to the Security seat. Redeployed by hand after
reading `cdk diff --strict`: `milestones/M07/runs/pr2_by_hand.md` step
B2 has the commands and what the diff should show and nothing else.
Deployed by hand on 2026-10-02, twice, from `m07-pr4` (`7a9032d`, then
`81508ab`), with M07 PR 4's change to the execution role below
(`milestones/M07/runs/pr2_by_hand.md`, `b2_cdk_diff.md`).

- `agentkeel-evals` gains three read-only statements on an agent from the
  template (its stack, its runtime, its image's tags), so a pull request's
  run can read whether a retired runtime is gone and which bytes a runtime
  runs after a revert. It invokes no template agent.
- `agentkeel-model-watch`: `model-watch.yml` on `main` asks Bedrock for a
  model's lifecycle as this. One action, `bedrock:GetFoundationModel`.
- `agentkeel-envelopes` and `agentkeel-envelope-row-put`: one row per
  envelope on `main` (commit, verdict, mode), written once by `evals.yml`'s
  `archive` job on `main`. Panel 2 reads the table (`infra/grafana/`). It
  is a copy for a surface, not evidence.

The deploy role does not change, and a retirement needed nothing new: it
is an update of the agent's stack, and the execution role already may
delete a template agent's runtime (`tests/test_bootstrap.py` holds that
no `DeleteStack` and no `UpdateItem` was added; the first retirement,
2026-10-03, deleted `agentkeel_owner_check` with no refusal).

**M07 PR 4: the execution role does change.** One statement,
`WhatCreateAgentRuntimeChecksOnTheRuntimeItHasNotNamedYet`:
`bedrock-agentcore:CreateAgentRuntimeEndpoint` and
`bedrock-agentcore:TagResource` on `runtime/*`, no condition.
`CreateAgentRuntime` checks both against a runtime that has no id yet,
one at a time, and the first two creates of a template agent were refused
without them. It is wider than the platform's runtimes: in this shared
account the role may add an endpoint to, or tag, a runtime that is not
the platform's. It may not update, delete or untag one. Two narrower
forms were not tried: the Resource `runtime/${*}`, IAM's literal
asterisk, and a condition on `aws:TagKeys` for `TagResource`. Trying
either costs a create that may be refused; carried to M08.

## Deploy record, 2026-11-02: the interface endpoints in one subnet

Deployed by the human's admin user, by hand, from `infra/bootstrap` with
`npx aws-cdk@2 deploy`, after `npx aws-cdk@2 deploy --no-execute` and a
read of the change set (`describe-change-set`): six Modify, no
replacement; five `AWS::EC2::VPCEndpoint` on `SubnetIds`, and
`DoorGrants` on metadata only (`cdk diff` had shown its description as a
replacement because the stored template returns `§` as `?`; CloudFormation
did not). `UPDATE_COMPLETE` at 2026-11-02T04:39:52Z.

| Read | Before (2026-11-01) | After (2026-11-02T04:43Z) |
|---|---|---|
| `describe-vpc-endpoints`, interface, subnets per endpoint | 2 (`subnet-0f82c2f36bd203187`, `subnet-00008bbb7a11551a0`) | 1 (`subnet-00008bbb7a11551a0`, us-west-2a, `usw2-az1`) |
| network interfaces per endpoint | 2 | 1 |
| the five endpoint ids | `vpce-036305989f9ac53e7` (bedrock-runtime), `vpce-03a73e385f334f4be` (kms), `vpce-00af6e3d03fa6346a` (logs), `vpce-04b819e1d563554c8` (ecr.api), `vpce-0300e82aa0b42e9b0` (ecr.dkr) | the same five |
| `/agentkeel/security/endpoint/*` | `sg-06b43d057b1b830d6`, `sg-01b80a6e3c1600fd9`, `sg-0081b33b9e519fa3b`, `sg-0d9fa1f8ba484f2ab`, `sg-04915dc609efc1afe` | the same five |
| `/agentkeel/security/subnet-ids` | both subnets | both subnets |
| refagent's runtime, `invoke_agent_runtime` with `g-001`'s question (`src.agent.run.invoke_deployed`, the admin user) | `r-019`, `ML-2.1`, one tool call, 3,528 tokens, 4.7 s | `r-019`, `ML-2.1`, one tool call, 3,528 tokens, 4.3 s |

The two runtime calls are a read, not evidence (`evals/local/` is not
either): the envelope that measures the runtime after this change is the
CI-written one for the first `main` commit after the merge.
