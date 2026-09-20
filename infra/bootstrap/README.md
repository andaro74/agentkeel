# infra/bootstrap

Security seat. SPEC/00 §8 M01 and SPEC/01 §6, with
`milestones/M01/feasibility.md` §2.6 rulings a, b, d, e and f. Authorised
by `milestones/M01/rulings/pr2.md`.

Deployed **by hand, by the human with admin**, once, in the agent account,
during M01 PR 2 and before PR 2's first CI run (ruling f, ruling 4). It is
never deployed by CI: the roles CI uses are in it, so a pipeline that
could change it could widen its own permissions.

What it makes is listed at the top of `app.py`. Three things are worth
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

**The Budgets lag is AWS's.** Budgets data refreshes up to three times a
day. The worst case this stack bounds is therefore up to one refresh
interval of Bedrock spend at the account quota. No smaller figure is
invented (ruling a).

**Two parameters are written by hand.** `GovernedAgent` reads five
endpoint destinations from SSM. The three interface endpoints publish
their security group ids from this stack. The two gateway endpoints — S3
and DynamoDB (ADR-0006) — are reached through a managed prefix list, and
AWS gives no CloudFormation attribute for a prefix list id, so those two
parameters are written by the same human, with one command each, below.
Until they exist an agent stack does not deploy.

## Deploying it

```bash
# 1. As the admin, in the agent account, us-west-2.
aws sts get-caller-identity
cd infra/bootstrap
npx aws-cdk@2 diff --parameters BudgetSubscriberEmail=<your address>
npx aws-cdk@2 deploy --parameters BudgetSubscriberEmail=<your address>
```

The email is a CloudFormation parameter, not a value in the repo:
CloudFormation requires at least one Budgets subscriber, and an address
belongs to a person, not to a git history.

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
# 3. Point CI at the new eval role, and check the parameters are all there.
aws cloudformation describe-stacks --stack-name AgentkeelBootstrap \
  --query 'Stacks[0].Outputs' --output table
gh variable set AWS_EVAL_ROLE_ARN --body "arn:aws:iam::<account>:role/agentkeel-evals"
aws ssm get-parameters-by-path --region us-west-2 --path /agentkeel/security --recursive \
  --query 'Parameters[].Name' --output table
```

Then the two attempts, S4 and S6: `milestones/M01/runs/f1_1_laptop.yaml`
and `milestones/M01/runs/f1_3_key_policy.yaml` say what to run and what to
write down. Every attempt's **request id** goes in the run file; PR 2's CI
run looks each one up in CloudTrail (`scripts/observe_attempt.py`) and
that lookup is what writes `checks.F1_1` and `checks.F1_3`. A file a human
wrote feeds no check by itself (SPEC/01 §4).

After PR 2 merges: `cd infra/eval-role && npx aws-cdk@2 destroy` (ruling f).

## What has not been observed

Nothing in this stack has been deployed yet at the time this file was
written. Until the deploy and the two attempts are in the record, no
sentence here or anywhere else may call any of it proven (SPEC/00 §10.5):
what exists is a template, a cdk-nag report and two seeded cases waiting
for their attempt.
