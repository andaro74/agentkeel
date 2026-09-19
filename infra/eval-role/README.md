# infra/eval-role

Security seat. Ruling on report 2.3 (M00 PR 2): the CI credential path
for `make evals` at M00.

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
  `refs/pull/<n>/merge` or `refs/heads/main` (`StringLike`; the `*` is
  the PR number). It is aimed at a second workflow file reusing the role.
  A PR that edits `evals.yml` itself still matches: on `pull_request`
  the workflow is the PR's own copy. **Not observed yet**, either way:
  no run has assumed the role under this condition, and no second
  workflow has been refused. It is not known from the tree that STS
  evaluates this claim, or that this repo issues it in this form; the
  `OIDC claims the role trusts` step in `evals.yml` prints what is
  issued. If the claim is absent or differs, every assume is refused:
  it fails closed.
- **What it can do:** `bedrock:InvokeModel` and
  `bedrock:InvokeModelWithResponseStream` on the inference profiles the
  current milestone calls, and on the foundation models those profiles
  route to (us-east-1, us-east-2, us-west-2) only when the call comes
  through one of those profiles. **At M00 that is one profile:
  `us.amazon.nova-micro-v1:0`.** Each milestone's PR 1 adds the ARNs that
  milestone calls, to `MODELS` in `app.py`, with a Security ruling.
- **What it cannot do:** anything else. No S3, no IAM, no logs, no
  `sts:AssumeRole`.

## Finding S-1 (Security, M00 PR 2)

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

**Assumed by a run: not at the M00 close.** The two `evals` runs between
that measurement and the redeploy took the "already measured" path and
assumed no role at all, and no run had started after the redeploy. The
deploy is observed; the enforcement is not. That STS evaluates the
`job_workflow_ref` condition is still unobserved, exactly as the bullet
above says. The first run that assumes the redeployed role is the close PR's own
`evals` run, because that PR changes `tests/` and this file. It is
recorded in `milestones/M00/rulings/pr3.md`, under "This PR's own
measurement", when the run finishes and before the merge — that path a
later commit can add a line to without re-measuring the tree, which this
file is not. Security signs S-1
on that observation, at M01, not on this deploy
(`milestones/M01/open.md`, item 12).

Not fixed here:

- **`MaxSessionDuration` stays 3600.** The ruling asked for 900. IAM's
  floor is one hour and CDK refuses less at synth (`must be >= 3600sec`).
  `evals.yml` asks for 900 seconds; a step that mints its own token can
  ask for 3600.
- **Spend is not enforced outside the runner.** A Budgets alarm per
  inference profile that disables the role is M01's bootstrap stack.
  Carried to SPEC/01.

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

## What is not here

- No permission boundary. The boundary is M01's bootstrap stack, which
  absorbs this role. Delete this stack then.
- A pull request from any branch of this repo can assume the role and
  spend tokens. `cost-cap` (`thresholds.yaml`) reads the spend after the
  run, and only the spend the PR's own runner wrote down. `make evals` as
  written makes 15 calls at 512 output tokens each, on Nova Micro. That
  is not the worst case. Any step of `evals.yml` that runs PR code can
  mint its own OIDC token, assume the role for up to one hour, and invoke
  Nova Micro at the account's quota. A Budgets alarm on Bedrock would be
  the observation; there is none until M01.
- Not observed yet: a direct call to a foundation model, and a call
  through an unpinned profile, both being denied. Two `AccessDenied`
  results from the deployed role would show it.
- `agentkeel-m00-evals` is a fixed name. An M01 stack that reuses it will
  collide until this stack is deleted.
- cdk-nag (`AwsSolutionsChecks`) runs on synth. Zero findings, zero
  suppressions on 2026-09-18, cdk-nag 2.38.2. cdk-nag 3.0.2 fails to
  load as a Python aspect (`aspect.visit is not a function`), so the
  group pins `<3`.
