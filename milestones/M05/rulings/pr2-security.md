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

Measured first (`open.md` row 20; `runs/bootstrap_size.md`): 49,173 of
51,200 bytes at `5a5720e`, and the 66 bytes accounted for (M04 PR 1's
scratch edit against the committed one; never in the tree at a merge).
**Ruled:** the agent boundary allows `s3:PutObject` on
`arn:aws:s3:::agentkeel-audit-897698239547/agents/*`, as a statement of
its own with its reason beside it (`8e086ea`). It widens a ceiling; it
moves no bar in `thresholds.yaml` and is not on ADR-0009's list: one key.
The S3 gateway endpoint lets that put, and only that put, out to the
security account. After both: **49,685 of 51,200 bytes**, 1,515 left.

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
