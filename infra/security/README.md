# infra/security

The security account's stack, `AgentkeelSecurity` (Security). SPEC/05 §6
names each part; `app.py` builds them. It lives in account 897698239547
(`milestones/M05/runs/security_account.md`), not in the agent account, and
nothing in the agent account deploys or changes it.

What it is for, in one line: every attempt SPEC/05 §5 makes leaves its
record in an S3 bucket that no principal in the agent account can delete,
re-date, unlock or re-policy, and CI reads those records from here.

## Deploy, once, at M05 PR 2

Through the profile `agentkeel-security` (`OrganizationAccountAccessRole`,
assumed by `hector.acevedo` with MFA), from a clean checkout of the PR's
branch:

```sh
aws sts get-caller-identity --profile agentkeel-security        # Account 897698239547
aws iam list-open-id-connect-providers --profile agentkeel-security   # none for token.actions.githubusercontent.com
cd infra/security && npx aws-cdk@2 diff --profile agentkeel-security
npx aws-cdk@2 deploy --profile agentkeel-security
```

`cdk diff` should show only new resources: one bucket and its policy, one
trail, one OIDC provider, one managed policy (the boundary), two roles and
their two policies, four outputs. A second bucket, a Lambda, a custom
resource or an asset parameter is a stop. If GitHub's OIDC provider already
exists in the account, the deploy fails on it: stop and say so, do not
delete it.

Then, **straight after**, delete `OrganizationAccountAccessRole` in
897698239547 (`rulings/pr2-security.md`): as `hector.flores` in the console,
or with the profile before it expires:

```sh
aws iam list-attached-role-policies --role-name OrganizationAccountAccessRole --profile agentkeel-security
aws iam detach-role-policy --role-name OrganizationAccountAccessRole \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess --profile agentkeel-security
aws iam delete-role --role-name OrganizationAccountAccessRole --profile agentkeel-security
```

Any later change to this stack is deployed as `hector.flores`.

## The lock, and taking it down

Object Lock COMPLIANCE, one day (R5 as amended at M05 PR 1; seven years is
M08's). Once written, an object version cannot be deleted or re-dated by
anyone, root included, until its day is up. The stack is retained on
delete (bucket `RETAIN`); to take it down, as `hector.flores`, a day after
the last write: stop and delete the two trails, delete the agent account's
flow log to the bucket, delete every version, then the bucket, then
`npx aws-cdk@2 destroy`.

## What it does not stop

This account's own admin and root, who own the bucket and its policy (the
lock holds each object for its day, not the policy); anything seven years
(M08); a gate on the lock's retention (SPEC/05 §8).
