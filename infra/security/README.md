# infra/security

The security account's stack, `AgentkeelSecurity` (Security). SPEC/05 §6
names each part; `app.py` builds them. It lives in account 897698239547
(`milestones/M05/runs/security_account.md`), not in the agent account. No
role in the agent account deploys it or can assume a role in it once
`OrganizationAccountAccessRole` is deleted; the agent account is still the
organization's management account, and what that leaves open is below.

What it is for, in one line: every attempt SPEC/05 §5 makes leaves its
record in an S3 bucket where no principal in the agent account can delete
or re-date an object within its day, turn the lock off, or put a bucket
policy through IAM, and CI reads those records from here. None of those
refusals has been attempted yet (seed S6 is this PR's).

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
lock holds each object for its day, not the policy); the agent account as
the organization's management account, which can enable centralized root
access (`sts:AssumeRoot` with the `S3UnlockBucketPolicy` task policy, which
deletes a bucket policy) or remove this account or attach an SCP to it: not
enabled when read on 2026-09-28 (IAM trusted access off), and nothing here
stops it being enabled (the landing zone's, SPEC/00 §12); anything seven
years (M08); a gate on the lock's retention (SPEC/05 §8).

## M07 PR 2: two prefixes, each written once

Ruled 2026-10-02 (`milestones/M07/rulings/pr2-security.md` items 9 and
11); the read role's listing of `bundles/` is item 13e, not ruled then.
Redeployed by hand after reading the change set: the steps, and what it
should show and nothing else, are `milestones/M07/runs/pr2_by_hand.md`
step B1. Deployed on 2026-10-02 by `hector.flores` in the console, from a
template synthesised from `main` at `3bfd074` (corrected at M07 PR 3: the
profile `agentkeel-security` named above went with
`OrganizationAccountAccessRole` at M05, and step B1 first named it).

- `bundles/<name>/<commit>.tar` and its signature: the signed archive of
  each deploy of an agent from the template, put by `agentkeel-answer-put`
  (deploy.yml on `main`). The Actions artifact expires after 30 days; a
  retired agent's bundle must outlast it.
- `observations/<run id>.json`: what `observe.yml` read from GitHub as the
  platform's observer App, put by `agentkeel-observation-put`, a new role
  trusted for that workflow on `main` only.

Each prefix has one statement in the bucket's policy that refuses a put
without `If-None-Match`, as `envelopes/` has. The lock is still one day:
after it an object is kept by this account's policies, not by the lock.
The read role may list `bundles/` and may list and read `observations/`.
Nothing here has put or refused anything yet.
