# infra/eval-role

Security seat. Ruling on report 2.3 (M00 PR 2): the CI credential path
for `make evals` at M00. Changed at M01 PR 1 (`milestones/M01/rulings/pr1.md`,
open items 12, 14, 18, 20, 28, 32, 33, 34, 35). M01 PR 2's bootstrap stack
absorbs this role under a new name; this stack is deleted after PR 2 merges.

One IAM role, `agentkeel-m00-evals`.

- **Who can assume it:** GitHub Actions in `andaro74/agentkeel`, over the
  account's existing GitHub OIDC provider. `pull_request` runs from any
  branch; `push` runs from `main` only. Both `aud` and `sub` are matched
  with `StringEquals`; there is no wildcard on either.
- **The subject is the immutable one.** This repo has
  `use_immutable_subject` on, so the claim is
  `repo:andaro74@3157440/agentkeel@1376369685:pull_request`, with the
  owner id and repo id in it. The first deploy trusted the classic form,
  `repo:andaro74/agentkeel:pull_request`, which this repo never issues;
  the assume failed with `Not authorized to perform
  sts:AssumeRoleWithWebIdentity` (run 35402876499, attempt 2). If the
  setting is ever turned off, the assume fails again until this is
  changed back. It fails closed both ways.
- **Which workflow:** the trust policy requires `job_workflow_ref` to be
  `andaro74/agentkeel/.github/workflows/evals.yml` at
  `refs/pull/*/merge` or `refs/heads/main` (`StringLike`). `*` matches the
  PR number and anything else, including `/`; the pattern is bounded by
  what GitHub issues, not by the pattern. It is aimed at a second workflow
  file reusing the role.
  A PR that edits `evals.yml` itself still matches: on `pull_request`
  the workflow is the PR's own copy. **Observed on 2026-09-19**, in the
  M00 close PR's own run
  ([35412277571](https://github.com/andaro74/agentkeel/actions/runs/35412277571),
  commit `c547f4f`), the first run to assume the redeployed role. The
  `OIDC claims the role trusts` step printed
  `job_workflow_ref = andaro74/agentkeel/.github/workflows/evals.yml@refs/pull/5/merge`
  and `sub = repo:andaro74@3157440/agentkeel@1376369685:pull_request`,
  and the assume succeeded. So the claim is issued in the classic form
  for `job_workflow_ref` while `sub` is the immutable one, the pinned
  pattern matches it, and STS evaluates it. **Still not observed:** a
  second workflow file being refused. Carried to M01 PR 2, Security. If
  the claim is ever absent or differs, every assume is refused: it fails
  closed.
- **What it can do:** `bedrock:InvokeModel` and
  `bedrock:InvokeModelWithResponseStream` on the inference profiles the
  current milestone calls, and on the foundation models those profiles
  route to (us-east-1, us-east-2, us-west-2) only when the call comes
  through one of those profiles. **At M01 that is two profiles:
  `us.amazon.nova-micro-v1:0` (the control) and
  `us.anthropic.claude-sonnet-4-6` (refagent, item 14; re-ruled at PR 2,
  ruling p, from `us.anthropic.claude-sonnet-5`, which this account cannot
  call).** Both route to the
  same three regions (`aws bedrock get-inference-profile`, 2026-09-18 and
  2026-09-19). Each milestone's PR 1 adds the ARNs that milestone calls,
  to `MODELS` in `app.py`, with a Security ruling. **The human redeploys
  with admin after M01 PR 1 opens and before PR 2's first run**; until
  then the deployed role allows Nova Micro only.
- **What it cannot do:** anything else. No S3, no IAM, no logs, no
  `sts:AssumeRole`. From M01 PR 1 that is also an explicit `Deny`
  statement, `DenyEscalationAndEvidenceDeletion`, on five actions:
  `iam:*`, `sts:AssumeRole`, `logs:Delete*`, `bedrock:*Guardrail*` and
  `s3:PutBucketPolicy`, resource `*` (item 33; the fifth by Security
  ruling D at M01 PR 1). It is meant to hold if a later change attaches a policy
  that allows one of them, which matters because the role has no
  permission boundary until M01 PR 2. **Written, not deployed, not
  observed** at M01 PR 1: it deploys with item 14's redeploy, and no
  refused call on a denied action has been recorded.

## Finding S-1 (Security, M00 PR 2)

Signed: Security, 2026-09-19, on run 35412277571

The first deploy allowed all six pinned models, to any workflow, from
any PR branch, for up to an hour, with `cost-cap` reading only what the
PR's own runner wrote down. M00 calls one model. Fixed in `app.py`: one
profile, one workflow file.

**Deployed: yes, 2026-09-19T00:20:25Z.** Every run up to and including
the M00 PR 2 measurement at `9407615` assumed the wider role as deployed
at `8fb4b80`. The deploy is a console reading, not a file in this repo —
`cdk.out/` is gitignored — so here is the command and what it returned,
for anyone who wants to check it rather than believe it:

```
$ aws cloudformation describe-stacks --stack-name AgentkeelM00EvalRole \
    --region us-west-2 \
    --query 'Stacks[0].[StackStatus,LastUpdatedTime,CreationTime]' --output text
UPDATE_COMPLETE  2026-09-19T00:20:25.359000+00:00  2026-09-18T22:57:54.082000+00:00
```

**Assumed by a run: yes, 2026-09-19, run 35412277571 at `c547f4f`** —
the M00 close PR's own `evals` run, which measured again because that PR
changes `tests/` and this file. It assumed the redeployed role, made the
fifteen Bedrock calls through `us.amazon.nova-micro-v1:0`, and its
envelope is `evals/history/c547f4f….json`. The claims it printed are in
the "Which workflow" bullet above.

Between the `9407615` measurement and the redeploy no run assumed
anything: the two `evals` runs in that window took the "already
measured" path. So the narrowed role has exactly one run behind it, and
that run is the whole of the evidence that STS enforces it. The record
is in `milestones/M00/rulings/pr3.md`. Security signed S-1 at M01 PR 1, on
that observation, not on the deploy (`milestones/M01/open.md`, item 12;
`milestones/M01/rulings/pr1.md`).

Not fixed here:

- **`MaxSessionDuration` stays 3600.** The ruling asked for 900. IAM's
  floor is one hour and CDK refuses less at synth (`must be >= 3600sec`).
  `evals.yml` asks for 900 seconds; a step that mints its own token can
  ask for 3600. Closed at M01 (item 19): 3600 stands, and the Budgets
  action of item 13 compensates. No step assumes the role with a token of
  its own; the diagnostic step requests one and prints its claims (Security
  ruling C, M01 PR 1). The step stays.
- **Spend is not enforced outside the runner.** A Budgets action on this
  role at `daily_usd: 10` (the Threshold Owner's number) is M01 PR 2's
  bootstrap stack (SPEC/01 §6).

## Deploy (with admin; again whenever `app.py` changes)

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

## Redeployed 2026-09-20 (ruling p: the model refagent actually runs on)

`MODELS` named `anthropic.claude-sonnet-5`, which this account cannot
call, so M01 PR 2's first agent run was fifteen `AccessDeniedException`
(run 35529132275). refagent's model is now `anthropic.claude-sonnet-4-6`
(`milestones/M01/rulings/pr2-threshold-owner.md`), and this role's pinned
profiles follow it. Nothing else changed: same role, same trust policy,
one IAM policy and six ARNs.

```
$ aws cloudformation describe-stacks --stack-name AgentkeelM00EvalRole     --query 'Stacks[0].Outputs'
AgentkeelM00EvalRole.EvalRoleArn = arn:aws:iam::581208540944:role/agentkeel-m00-evals
Stack ARN: arn:aws:cloudformation:us-west-2:581208540944:stack/AgentkeelM00EvalRole/61ba98e0-b3b4-11f1-b40f-06ffed3b8d53
Deployment time: 21.79s
```

`aws iam simulate-principal-policy` against the deployed role, same day:

| Action | Resource | Decision |
|---|---|---|
| `bedrock:InvokeModel` | `us.anthropic.claude-sonnet-4-6` | **allowed** |
| `bedrock:InvokeModel` | `us.amazon.nova-micro-v1:0` | **allowed** |
| `bedrock:InvokeModel` | `us.anthropic.claude-sonnet-5` | implicitDeny |
| `iam:CreateUser` | `*` | explicitDeny |
| `sts:AssumeRole` | `*` | explicitDeny |
| `logs:DeleteLogGroup` | `*` | explicitDeny |
| `s3:PutBucketPolicy` | `*` | explicitDeny |
| `bedrock:CreateGuardrail` | `*` | explicitDeny |

The old profile is `implicitDeny` rather than `explicitDeny`, and that is
the pinning working: the role allows the profiles it names and nothing
else, so a model leaving the list needs no Deny to become unreachable.
The five `explicitDeny` rows are item 33's Deny statement, and this is the
first time each has been read off the deployed role rather than the
template.

## What is not here

- No permission boundary (item 28). The boundary is M01 PR 2's bootstrap
  stack, which absorbs this role. Until then the Deny statement above is
  the only thing that holds against a later attach.
- **Spend: unbounded at the account quota until PR 2** (item 34). That is
  the worst-case figure, and it has no smaller number until the Budgets
  action exists. A pull request from any branch of this repo can assume
  the role and spend tokens. `cost-cap` (`thresholds.yaml`) reads the
  spend after the run, and only the spend the PR's own runner wrote down;
  from M01 an over-cap run is a recorded RED, not a missing file. Any
  step of `evals.yml` that runs PR code can mint its own OIDC token,
  assume the role for up to one hour, and invoke either pinned profile at
  the account's quota. The Budgets action of M01 PR 2 is the first thing
  that bounds it, and Budgets data lags by hours.
- Not observed yet: a direct call to a foundation model, and a call
  through an unpinned profile, both being denied (item 18). Two
  `AccessDenied` results from the deployed role would show it. A step in
  `evals.yml` at M01 PR 2.
- `agentkeel-m00-evals` is a fixed name (item 20). M01 PR 2's bootstrap
  stack makes the eval role under a new name, `AWS_EVAL_ROLE_ARN` is
  pointed at it, and this stack is deleted after PR 2 merges (human).
- cdk-nag (`AwsSolutionsChecks`) runs on synth. **Zero findings, zero
  suppressions on 2026-09-19**, cdk-nag 2.38.2, aws-cdk-lib 2.270.0, on
  `app.py` as of M01 PR 1 (two profiles, the five-action Deny statement). The report
  that synth wrote is committed beside this file,
  `AwsSolutions--AgentkeelM00EvalRole-NagReport.csv` (item 32). Nothing
  in CI re-runs it until cdk-nag joins `validate` at M01 PR 2, which needs
  node and the CDK CLI in CI. cdk-nag 3.0.2 fails to load as a Python
  aspect (`aspect.visit is not a function`), so the group pins `<3`.
