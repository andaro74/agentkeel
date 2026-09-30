---
# M05 PR 3, Security's key: the stand-in removed once S2 and S3 are read. Product's file is
# rulings/pr3.md, Engineering's rulings/pr3-engineering.md.
ruling: pr3-security
seat: Security
authorises:
  - infra/audit/app.py
  - infra/audit/AwsSolutions--AgentkeelAudit-NagReport.csv
  - infra/audit/README.md
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

`security-reviewer` read the diff `59f06c0...d703c48 -- infra` (2 files):
0 BLOCK, 2 FINDING, 5 NOTE, verbatim in the PR body.

| # | Finding | Status |
|---|---|---|
| F1 | The constraint is met by the redeploy, not by this PR; nothing records the deletion | **Pending, done by the human before the ruling line**: `cdk diff` as `infra/audit/README.md` lists it, the deploy, and `get-role` answering `NoSuchEntity`, recorded in `milestones/M05/runs/security_account.md` with its time |
| F2 | The security account's bucket policy still **allows** the stand-in's ARN a put under `agents/refagent/standin/*`, matched by name; a role recreated with that name and path (by the admin, or `agentkeel-cfn-exec` from `main`) gets it back | **Carried to M06, Security** (ruled by the human as Security, 2026-09-30): no second hand deploy in the security account at M05. Its reach: that one prefix; the Deny on `events/` stands, so S4's refusal event cannot be forged; a write adds a version and modifies nothing. PR 4 puts it in M06's `open.md` with the date the role is deleted |
| N3 | Keep both Denies naming the stand-in | Kept: this PR does not touch `infra/security/` |
| N4 | Nothing else in the stack changes | Recorded; the `cdk diff` is the check |
| N5 | The README does not list the expected diff | **Repaired** (`a3bcb61`) |
| N6 | The docstring and the stack description still describe the stand-in | Docstring **repaired** (`a3bcb61`); the description kept, so the diff shows no stack-level update |
| N7 | Do not call the removal secure or done | Held: nothing here calls it either |

## What a reader can run

```
uv run pytest -q tests/test_containment_stacks.py     # the stack makes no stand-in
make validate                                         # cdk-nag, every stack: the report matches the synth
cd infra/audit && npx aws-cdk@2 diff                  # before the redeploy: the role and its policy, removed
```
