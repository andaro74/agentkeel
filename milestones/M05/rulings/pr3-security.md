---
# M05 PR 3, Security's key: the stand-in removed once S2 and S3 are read. Product's file is
# rulings/pr3.md, Engineering's rulings/pr3-engineering.md.
ruling: pr3-security
seat: Security
authorises:
  - infra/audit/app.py
  - infra/audit/AwsSolutions--AgentkeelAudit-NagReport.csv
evidence:
  - SPEC/00-overview.md#8-M05
  - SPEC/05-containment-and-evidence.md#6-the-code-that-reads-the-answer-pr-2
  - milestones/M05/rulings/pr2-security.md
  - evals/history/388dbcf159813a4675f7afa4a40fa07828465624.json
  - evals/history/5a5fe1e2086f24553b44100ee457927cc7bf20ef.json
pr: 32
---

# Ruling: M05 PR 3, Security

Drafted by the session, 2026-09-30. Not ruled.

## The stand-in, removed

Security's constraint on M05 PR 2 (`pr2-security.md` §3): the stand-in is
deleted once S2 and S3 are read. S2 was read by PR 2's run (`388dbcf`:
refused, 295 s); S3 by this PR's first run (`5a5fe1e`: refused by the
stand-in's own explicit deny, 199 s). **`STANDIN = False`** (`b465e09`):
the stack makes no `agentkeel-refagent-standin` and no policy for it; its
cdk-nag suppression is skipped, as `SeedS1Role`'s is, and its five rows
leave the committed report. Nothing else in the stack changes.

**Done by the human after this PR's push, not by its merge** (`infra/audit/`
is deployed by hand, never by a workflow): `cdk diff` shows only the
stand-in role and its policy removed; `cdk deploy`; `aws iam get-role
--role-name agentkeel-refagent-standin` answers `NoSuchEntity`. Pending.

## The review

`security-reviewer` read the diff `59f06c0...d703c48 -- infra`: pending,
verbatim in the PR body.

## What a reader can run

```
uv run pytest -q tests/test_containment_stacks.py     # the stack makes no stand-in
make validate                                         # cdk-nag, every stack: the report matches the synth
cd infra/audit && npx aws-cdk@2 diff                  # before the redeploy: the role and its policy, removed
```
