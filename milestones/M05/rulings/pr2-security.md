---
# M05 PR 2, Security's key. The security account, the two new stacks,
# the bootstrap's and the construct's edits, and the two workflows.
# Product's file is rulings/pr2.md, Engineering's rulings/pr2-engineering.md,
# the Threshold Owner's rulings/pr2-threshold-owner.md.
ruling: pr2-security
seat: Security
authorises:
  - infra/security/**
  - infra/audit/**
  - infra/bootstrap/app.py
  - infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv
  - infra/construct/**
  - .github/workflows/evals.yml
  - .github/workflows/cold-review-ruling.yml
  - infra/workflows.sha256
  - milestones/M05/runs/security_account.md
  - milestones/M05/runs/bootstrap_size.md
evidence:
  - SPEC/00-overview.md#8-M05
  - SPEC/05-containment-and-evidence.md#6-the-code-that-reads-the-answer-pr-2
  - milestones/M05/feasibility.md
  - milestones/M05/rulings/pr1-security.md
  - milestones/M05/runs/security_account.md
  - milestones/M05/runs/bootstrap_size.md
pr: 31
---

# Ruling: M05 PR 2, Security

Drafted by the session; the human rules as Security before the merge.

## 1. The security account, and the role deleted after its deploy

The security account is **897698239547**, an existing member of the
organization, reused and cleaned by the human on 2026-09-29
(`runs/security_account.md`; Unsure B on M05 PR 1). The agent account,
581208540944, is the organization's management account, so
`OrganizationAccountAccessRole` in 897698239547 trusts it.

**Ruled:** the human deploys `infra/security/` once through that role
(profile `agentkeel-security`, with MFA), and **deletes
`OrganizationAccountAccessRole` in 897698239547 right after**. From then
on the account is reached as `hector.flores` (console, MFA) or root
(MFA), both confirmed working. A role in the security account that an
agent-account admin can assume would make "an account it cannot change"
false on its first day.

**Recorded:** SCPs never bind a management account. While the agent
account is this organization's management account, no SCP can restrict
its admin, so `open.md` row 17's deferral to the landing zone cannot be
closed by an SCP on the agent account. It changes nothing measured at
M05.

## 2. The bootstrap: a ceiling widened, not a bar relaxed

Measured first (`open.md` row 20; `runs/bootstrap_size.md`). The 66 bytes
are the measuring script: read as UTF-8 the template at `5a5720e` is
49,107 bytes, M04 PR 1's figure; read with Windows' default (cp1252), each
of its eleven `§` counts 6 bytes more, 49,173, M04 PR 3's figure. Corrected
on the reviews; the first account (`30a04f5`, a scratch edit) was wrong.
**Ruled:** the agent boundary allows `s3:PutObject` on
`arn:aws:s3:::agentkeel-audit-897698239547/agents/*`, as a statement of
its own with its reason beside it (`8e086ea`). It widens a ceiling; it
moves no bar in `thresholds.yaml` and is not on ADR-0009's list: one key.
The S3 gateway endpoint lets that put, and only that put, out to the
security account. After both: **49,613 of 51,200 bytes** read as UTF-8,
1,587 left.

## 3. Security's constraints on PR 2 (`pr1-security.md`), each held

| Constraint | Where |
|---|---|
| The envelope-put role trusts `main` only; its step runs no PR code | `agentkeel-envelope-put`: `sub` `...:ref:refs/heads/main` and `job_workflow_ref` `evals.yml@refs/heads/main`, both `StringEquals`; the `archive` job runs on a push to `main`, git and the AWS CLI only (`tests/test_evals_workflow.py`) |
| The read role names its trust, reads what the observer needs and not `*`, carries a boundary | `agentkeel-audit-read`: `evals.yml` on a pull request or `main`; `AWSLogs/`, `agents/`, `test/` only; `agentkeel-security-boundary` on every role in the stack |
| The bucket policy names role ARNs per prefix, never the agent account's root but for S6's grant | refagent's role and the stand-in by `aws:PrincipalArn`, each on its prefix; the account root only in S6's `test/*` grant (put, `s3:DeleteObjectVersion`, `s3:PutObjectRetention`, `s3:GetObjectRetention`); an explicit Deny on either role outside `agents/refagent/` (S2's control) |
| It denies `PutObjectLockConfiguration` to every principal outside the security account | `NobodyOutsideThisAccountTurnsTheLockOff`, on `s3:PutBucketObjectLockConfiguration`, the IAM action for that API |
| The stand-in: MFA only, off refagent's refusal-event prefix, removed after S2 and S3 | trusted by the admin user `hector.acevedo` with `aws:MultiFactorAuthPresent`; denied `agents/refagent/events/*` in the bucket policy; `STANDIN = False` in `infra/audit/app.py` once both are read (PR 3) |
| The observer accepts S4's refusal event only if the trail shows refagent's role wrote it | `scripts/observe_containment.py` reads the event's `PutObject` records; `src/verdict/containment.py` refuses any other writer |
| The boundary's `s3:PutObject` is its own statement on `agents/*` | §2; `tests/test_bootstrap.py` |
| PR 3's run checks the quarantine is detached before it measures | the observer reads the last attach or detach of `agentkeel-quarantine` from the trail first; row 5 reads "still attached" as a miss |
| `evals.yml`'s stale header lines corrected | the M02 lines and "the reader taken from main is M05" (now M06, `open.md` row 12) |

## 4. The two stacks

`infra/security/` (deployed in 897698239547) and `infra/audit/` (deployed
in the agent account after it), each by hand after reading `cdk diff`,
each synthesised by `validate` with cdk-nag and its report committed. The
trails log the audit bucket's object events under `agents/`, `test/` and
`envelopes/`, and never under `AWSLogs/`, where they deliver (finding 17).
The agent account's trail is multi-region, for IAM's global events
(seed S7's attach and detach), and logs AgentCore runtime invocations as
data events, the only way CloudTrail records them. The production corpus
bucket's object events ride in the same trail (`open.md` row 13).

## 5. The draft-ruling gate (`open.md` row 44)

`cold-review-ruling` fails while any ruling that names the PR has no
"Ruled by" line, or still says "Drafted" (`1538508`). This PR's own
rulings are drafts until the seats rule them, so the check is red on this
PR until then. It cannot tell who typed the line.

## 6. Not closed here, and named

- Whether VPC flow-log delivery writes into a bucket with Object Lock is
  not documented by AWS; it is read by the first flow record after the
  deploy, before S1 is attempted (Unsure H in the PR body).
- Unsure A (SPEC/01 §9's ceiling as a seeded case): M08, with the hostile
  copy, which makes calls outside the ceiling from the runtime itself.
- Unsure G: the stand-in's MFA condition works when the human's CLI
  profile for it carries `mfa_serial`; read by S2's attempt.
- No gate reads the lock's retention in `infra/security/` (SPEC/05 §8).

## 7. The reviews, and what came of them

`security-reviewer` (0 BLOCK, 6 FINDING, 29 NOTE) and `platform-architect`,
called by Security (0 BLOCK, 6 FINDING, 9 NOTE), each read the diff
`5a5720e...27f2678`, verbatim in the PR body.

| Finding | Status |
|---|---|
| security (two findings, S2 and S6's lock-off): the readers could not tell the named control from a missing grant | **Repaired** (`ec6747b`, Engineering): "explicit deny in a resource-based policy" required |
| security: If-None-Match only a client flag | **Repaired** (`ca0d07d`): the bucket policy denies a put under `envelopes/` without it |
| security, platform F2: the security account's trail missed IAM's events | **Repaired** (`ca0d07d`): multi-region with global events; the role's deletion will reach the bucket once it is made after the deploy |
| security, platform F1: the organization's route to the security account (centralized root access) | **Named** (`ca0d07d`, and SPEC/05 §8): read 2026-09-28, not enabled; nothing stops it being enabled; the landing zone's |
| security: a pattern in `aws:PrincipalArn` may read as public | **Repaired** (`ca0d07d`): refagent by its whole ARN, `ArnEquals`; the first deploy reads whether S3 accepts the policy |
| platform F3: a role handed to the construct skipped the denies | **Repaired** (`ca0d07d`): `_contain` adds them and the record's put; tested |
| platform F4: "every role in that account carries a boundary" | **Worded** (SPEC/05 §6, Product): every role `infra/security/` makes. `ecsTaskExecutionRole` may be deleted by the human; nothing reads it |
| platform F5, F6: controls with no seeded case | **Named** in SPEC/05 §8, none described as working |
| security NOTE, platform NOTE 4: any same-repo PR's code can read `AWSLogs/` | **Accepted for M05**: read-only, both accounts' management events; the reader from `main` is M06's |
| security NOTE: S6's grant to the account root, not the admin | **Kept, and SPEC/05 §6 amended to say so** (Product, `rulings/pr2.md` ruling 7, on the second read's F1): the lock must refuse any principal in the agent account, F5.3's reading, and the grant lists the put and the retention read beside the two actions |
| platform NOTE 3: `PutObjectRetention` on `test/` can lengthen a hold | **Recorded**: the teardown waits for it; not a modification (SPEC/05 §2) |
| platform NOTE 5: the manifest's `s3` comment still says image layers only | **Carried to M06**: a comment in `manifest.yaml` changes the bundle digest and would put this PR's run in the runner |
| platform NOTE 6: the bucket policy names refagent only | **Carried to M06/M07**, with the second agent's code |
| cold review F5: `evals.yml` described the archive as done | **Repaired** (`ca0d07d`) |
| item k, found while testing: `applies_to` dropped by cdk-nag's binding | **Repaired** (`ca0d07d`): `appliesTo`; each row its own reason |

### The second read, of the repairs (`27f2678...a07d6ba`)

`security-reviewer` read the repair diff: 0 BLOCK, 1 FINDING, 14 NOTE,
verbatim in the PR body. Its six first-read findings: closed in code, none
fired. F1 (the S6 row above cited SPEC/05 §6 for what it did not say):
**repaired** by amending §6 and this row. Notes repaired here: the security
stack's suppression reason quotes §6 as amended (N4); the archive job's
comment says it has not run (N5); §6 names the IAM action (N9); this
table's trail row and its count of two findings in one row (N11, N12).
Recorded: N3, the other stacks' suppressions still have no `appliesTo`
(M06, Security); N7, a cross-account `PutBucketPolicy` may be answered
`MethodNotAllowed`, not `AccessDenied`, which the reader would read as not
refused: stated before this PR's run, read by it, and not widened ahead of
the record; N8, the write-once Deny also refuses a multipart put there,
which the archive does not use. N10: the cleanup is dated 2026-09-29 as the
human dated it.

## 8. S1: the origin tried twice, and the finding (ruled 2026-09-29)

S1 was attempted from a CloudShell VPC environment (12:56:42Z) and then,
on the first attempt's absent record, from `agentkeel-seed-s1`, a Lambda
added to `infra/audit/` for it (13:54:22Z): one subnet, refagent's group
`sg-003ad866687089f27` (read the same as refagent's runtime ENIs'), the
default network ACL (read). Both timed out; both ENIs recorded only
NODATA. The reason recorded at `b167dd2`, that CloudShell dropped the
traffic before its ENI, was wrong. The VPC has no route out, so routing
drops the packet before the security group or the network ACL sees it,
and a drop by routing leaves no flow record. The control that refuses S1
is the missing route (ADR-0006), not the security group; it holds, and
nothing can record it.

**Ruled, with Product** (`rulings/pr2.md` ruling 9): S1 is the finding,
unmet for F5.2, and row 5 closes RED on it. The Lambda is removed:
`S1_ORIGIN = False`, and the human redeploys `infra/audit/`, which
deletes the function and its role. Its first deploy had rolled back
(`24e05db`): the function was created before its role's separate policy,
and Lambda's `CreateNetworkInterface` was refused six times; the grant
went inline. `security-reviewer` read `b167dd2` (0 BLOCK, 3 FINDING, 6
NOTE; one subnet, the reason, the group and ACL read beside the invoke:
repaired at `067243b`).
