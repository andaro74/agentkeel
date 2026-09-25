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

**Two parameters are written by hand.** `GovernedAgent` reads five
endpoint destinations from SSM. The three interface endpoints publish
their security group ids from this stack. The two gateway endpoints — S3
and DynamoDB (ADR-0006) — are reached through a managed prefix list, and
AWS gives no CloudFormation attribute for a prefix list id, so those two
parameters are written by the same human, with one command each, below.
Until they exist an agent stack does not deploy.

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
aws sts get-caller-identity
python scripts/read_back_grants.py > before.md   # the rows the deploy will change show MISMATCH
cd infra/bootstrap && npx aws-cdk@2 diff         # read it before anything touches AWS
npx aws-cdk@2 deploy                             # a redeploy keeps the previous parameters
cd ../.. && python scripts/read_back_grants.py   # mismatches: 0
aws cloudformation describe-stacks --region us-west-2 --stack-name AgentkeelBootstrap \
  --query "Stacks[0].Outputs[?starts_with(OutputKey, 'Guardrail')]" --output table
python scripts/probe_guardrail.py --id <GuardrailIdForTheManifest> --version <GuardrailVersionForTheManifest>
```

The id and version go into `agents/refagent/manifest.yaml` (Rule Owner),
and the probe's table into `milestones/M03/runs/`. Before the deploy the
guardrail does not exist, so `read_back_grants.py` skips the one row that
names it and says so.

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
