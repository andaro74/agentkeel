---
# M05 PR 1 (#30), Security's key. Two things: the workflow change
# (milestones/M05/open.md row 1, and cold review N3), and Security's key on
# the retention change R5's amendment makes (two keys; Product's is pr1.md).
ruling: pr1-security
seat: Security
authorises:
  - .github/workflows/evals.yml
  - infra/workflows.sha256
evidence:
  - SPEC/00-overview.md#8-M05
  - SPEC/05-containment-and-evidence.md
  - milestones/M05/open.md
  - milestones/M05/feasibility.md
  - milestones/M05/rulings/pr1.md
pr: 30
---

# Ruling: M05 PR 1, Security

Ruled by andaro74 as Security, 2026-09-28, as written.

## The workflow

`evals.yml` no longer looks up `milestones/M04/runs/f4_swaps.yaml` or
passes `SWAPS_OBS` to `make evals` (`47f386d`; `open.md` row 1), and its
header says so in the past tense (`457e04b`; cold review N3). The change
only removes: no permission, action, secret or trigger is added, every
`uses:` stays pinned to a commit, and `RULESET_TOKEN` stays behind the
fork guard (security-reviewer on this PR). `infra/workflows.sha256` is
rewritten for it; `make validate`'s `workflow-hash` is the witness on
the PR's `checks` run.

## The retention key (R5)

SPEC/00 R5 is amended: the audit bucket's Object Lock is COMPLIANCE with
**one day** of retention through M05, and seven years is M08's, where
F8.4 measures retention. Moving from R5's seven years is a retention
change and takes two keys. This is Security's; Product's is
`rulings/pr1.md`, ruling 2. Nothing has been written to any audit bucket:
none exists until M05 PR 2.

## What Security rules for PR 2 (SPEC/05 §6, from security-reviewer)

The constraints `security-reviewer` reads on PR 2: the envelope-put role
trusts `main` only and its step runs no PR code; the read-only role and
every role in the security account name their trust, their prefixes and
a boundary; the bucket policy names role ARNs per prefix, never the agent
account's root, grants S6's two object actions (`s3:DeleteObjectVersion`,
`s3:PutObjectRetention`) on `test/*` only, and explicitly denies
`s3:PutObjectLockConfiguration` outside the security account; the
stand-in is assumable by the human's admin role with MFA only, kept off
refagent's refusal-event prefix, and removed once S2 and S3 are read; the
boundary's `s3:PutObject` is its own statement on the audit bucket's
`agents/*`; PR 3's run checks the quarantine is detached before it
measures.

Named, not closed: no gate reads the lock's retention in
`infra/security/`, and `two-key` does not cover that path (SPEC/05 §8).

## What a reader can run

```
git show 47f386d -- .github/workflows/evals.yml   # removals only
make validate                                     # workflow-hash ok
grep -n f4_swaps .github/workflows/evals.yml      # the header's past-tense line only
```
