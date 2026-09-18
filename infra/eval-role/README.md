# infra/eval-role

Security seat. Ruling on report 2.3 (M00 PR 2): the CI credential path
for `make evals` at M00.

One IAM role, `agentkeel-m00-evals`.

- **Who can assume it:** GitHub Actions in `andaro74/agentkeel`, over the
  account's existing GitHub OIDC provider. `pull_request` runs from any
  branch; `push` runs from `main` only. Both `aud` and `sub` are matched
  with `StringEquals`; there is no wildcard.
- **What it can do:** `bedrock:InvokeModel` and
  `bedrock:InvokeModelWithResponseStream` on the six inference profiles
  pinned in `milestones/M00/README.md`, and on the foundation models
  those profiles route to (us-east-1, us-east-2, us-west-2) only when the
  call comes through one of the six profiles.
- **What it cannot do:** anything else. No S3, no IAM, no logs, no
  `sts:AssumeRole`.

## Deploy (once, with admin)

```
cd infra/eval-role
npx cdk diff
npx cdk deploy
```

The stack uses the caller's credentials and needs no CDK bootstrap. It
imports the OIDC provider and fails if the provider is missing. Then set
the repository variable the workflow reads:

```
gh variable set AWS_EVAL_ROLE_ARN --body "$(aws cloudformation describe-stacks \
  --stack-name AgentkeelM00EvalRole --region us-west-2 \
  --query 'Stacks[0].Outputs[?OutputKey==`EvalRoleArn`].OutputValue' --output text)"
```

## What is not here

- No permission boundary. The boundary is M01's bootstrap stack, which
  absorbs this role. Delete this stack then.
- A pull request from any branch of this repo can assume the role and
  spend tokens. `cost-cap` (`thresholds.yaml`) reads the spend after the
  run, not before it. The worst case per run is 15 calls at 512 output
  tokens each.
- cdk-nag (`AwsSolutionsChecks`) runs on synth. Zero findings, zero
  suppressions on 2026-09-18, cdk-nag 2.38.2. cdk-nag 3.0.2 fails to
  load as a Python aspect (`aspect.visit is not a function`), so the
  group pins `<3`.
