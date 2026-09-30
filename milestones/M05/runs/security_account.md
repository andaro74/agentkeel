# The security account (SPEC/05 §1; Unsure B on M05 PR 1)

Recorded at M05 PR 2's first commit. What the human chose, cleaned and
confirmed before this PR, and what the human does at this PR's deploy.
Everything below was done or read by the human in AWS; this file writes
it down and reads nothing.

## Which account

| | |
|---|---|
| Security account | **897698239547** ("hectorf44"), an existing member of the organization, created from it on 2020-11-18 (Organizations' record) |
| Agent account | 581208540944, where refagent runs |
| Organization | o-f6jzkm5xqa. **The agent account is the organization's management account** |
| Region | us-west-2 for both |

Reused, not created (the human as Product, before this PR). SPEC/05 §1 said
"a second AWS account, which the human creates and provides during PR 2":
it is provided, from the organization, and was cleaned first.

## What the human removed or confirmed, 2026-09-29

In 897698239547, read live by the human:

- deleted: the role `DeveloperCrossAccountUdemy` and the policy
  `CrossAccountS3Policy`;
- `hector.flores` (AdministratorAccess, console with MFA) has **no access
  keys** (`list-access-keys`, read live; the credential report can be up to
  four hours stale, so it was not the witness);
- root has MFA and no access keys;
- `hector.flores`'s console sign-in and the root password with its MFA
  both confirmed working.

Left in the account, none of it agentkeel's: `ecsTaskExecutionRole`
(trusted by `ecs-tasks` only), AWS service-linked roles, and four tagged
leftovers (one in us-east-1, three in us-west-2).

## How `infra/security/` is deployed, and the role deleted after

`OrganizationAccountAccessRole` in 897698239547 trusts the management
account, which is the agent account. So any admin in the agent account can
become admin of the security account, which is the thing the security
account exists to prevent (SPEC/05 §1: "a separate account it cannot
change").

1. The human deploys `infra/security/` once, through the local CLI profile
   `agentkeel-security`: that role, assumed by `hector.acevedo` in the agent
   account with MFA.
2. **Right after that deploy, the human deletes
   `OrganizationAccountAccessRole` in 897698239547** (Security,
   `rulings/pr2-security.md`). From then on the only ways in are
   `hector.flores` (console, MFA) and root (MFA), both in that account.
3. Any later change to `infra/security/` is deployed as `hector.flores`.

What the deletion does not stop: the management account can still act on
a member through Organizations itself: remove the account from the
organization, attach an SCP to it, update its primary email, or enable
**centralized root access** and then `sts:AssumeRoot` into it with a
root-task policy (`S3UnlockBucketPolicy` deletes a bucket policy;
`IAMCreateRootUserPassword` recovers root). Read-only from the agent
account on 2026-09-28: `aws iam list-organizations-features` answered
"Trusted Access for IAM not enabled by organization", and the
organization's service access lists CloudFormation StackSets and IAM
Identity Center only, so centralized root access is **not enabled**. An
agent-account admin could enable it; nothing stops that. Object Lock
COMPLIANCE still holds each object for its day against root; the bucket's
policy, its default retention for new objects and the delivery are what
that route reaches. Closing it is the landing zone's (SPEC/00 §12),
recorded in SPEC/05 §8 (platform-architect and security-reviewer on M05
PR 2).

The deletion is to be recorded: the security account's trail is
multi-region with IAM's global events, so the `DeleteRole` the human makes
after the deploy reaches the audit bucket under `AWSLogs/897698239547/`.
Until that record is read, the deletion is the human's word.

## SCPs never bind a management account

An SCP applies to member accounts only; it never restricts the
management account or any principal in it. The agent account is the
management account, so **no SCP can bind the agent account's admin**,
whatever the landing zone later writes. This bears on
`milestones/M05/open.md` row 17 (N14, "an SCP, deferred with the landing
zone"), and on SPEC/05 §8's "an SCP is the landing zone's": in this
organization that deferral cannot be closed by an SCP on the agent account
until the agent account is no longer the management account. Recorded
here and in `rulings/pr2-security.md`; it changes nothing measured at M05.

## CloudShell VPC (Unsure E on M05 PR 1)

Answered 2026-09-29 by the human: a CloudShell VPC environment started in
`vpc-0638596d59ee8f1b9` / `subnet-00008bbb7a11551a0` with only
`sg-003ad866687089f27` (refagent's security group). Its ENI was
`eni-0c1971040eeb5c453`, 10.20.0.254, "managed by AWS CloudShell service";
the shell itself sees only 169.254.x.x addresses, so S1 is read from that
ENI's flow record, not from anything the shell prints. The environment was
deleted and its ENI is gone. It is recreated for the real S1 attempt, and
the new ENI id is recorded in `f5_1_curl.yaml`. refagent's runtime ENIs are
10.20.0.190 and 10.20.1.157.

## The stand-in deleted (M05 PR 3; Security's constraint on PR 2)

S2 was read by M05 PR 2's run (`388dbcf`) and S3 by PR 3's first run
(`5a5fe1e`), so `STANDIN = False` (`b465e09`). The human redeployed
`infra/audit/` as `hector.acevedo` on 2026-09-30, after reading `cdk diff`.
The diff showed exactly what `infra/audit/README.md` lists and nothing
else: the stand-in's trust, its Deny `RefagentsExplicitDenies` and its two
seed Allows removed; `[-]` the role `Standin5CE34DD4` and the policy
`StandinDefaultPolicyCB21F6E8`; `[-]` the output `StandinRoleArn`.

- The deploy started at 03:57:52Z. The policy was deleted at 03:57:59Z,
  the role at 03:58:11Z, and the stack reached `UPDATE_COMPLETE` at
  03:58:11Z. The outputs left are `FlowLogId`, `QuarantinePolicyArn` and
  `TrailArn`.
- At 03:58:19Z, `aws iam get-role --role-name agentkeel-refagent-standin`
  answered `NoSuchEntity`.
- Still in the security account's bucket policy: the Allow for the
  stand-in's ARN under `agents/refagent/standin/*`, matched by name.
  Carried to M06 (Security's ruling on PR 3, `security-reviewer` F2), from
  this date.
