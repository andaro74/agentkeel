# The security account's stored template, hashed (2026-10-04)

Answers `milestones/M08/open.md` row 12 and corrects its row 13. Owed
since M07 PR 3 (`milestones/M07/runs/pr2_by_hand.md`, "Still owed"). M07's
files are left as M07 closed them; the correction is here.

**What this rests on.** `hector.flores` ran the commands in CloudShell in
the security account (897698239547) on 2026-10-04 and the human pasted
the output to the session. No session has credentials in that account,
and nothing in CI reads a stack's template. It is one person's read,
recorded; it feeds no check and no envelope.

## What was read

- Caller: `arn:aws:iam::897698239547:user/hector.flores`.
- Stack `AgentkeelSecurity`, us-west-2: `UPDATE_COMPLETE`, last updated
  2026-10-03T12:15:47.542Z. That is the second deploy of M07 (`e68ec46`,
  the observer's trust). The first (`3bfd074`, 2026-10-02) can no longer
  be hashed: its template was replaced by the second.
- The stored template (`get-template --template-stage Original`),
  normalised as `pr2_by_hand.md` gives it (JSON, sorted keys, no spaces),
  hashes to
  `55cad48fb222fc2fc68e12e07770ad4bd592be51ed4aad2c50ca7caf5f1efdfd`.
- `pr2_by_hand.md` expected
  `1a55571da2222787c0966f4004674110637d6a5f651dde69906bddc8e2657721`.
  **They differ.**

## Why they differ

A breakdown per resource, made in the same CloudShell session:

- 13 resources in both. `Description` and `Outputs` equal.
- Every resource equal once its `Metadata` is left out.
- Six resources differ in `Metadata` only.
- The uploaded file has 9 section signs (`§`), all in cdk-nag reasons
  under `Metadata`. The stored template has 0.
- The uploaded file with each `§` replaced by `?`, normalised the same
  way, hashes to `55cad48f…1efdfd` exactly.

So **the stack holds the uploaded template, with its nine section signs
stored as `?`**. No resource, property, policy or output differs.

The observer role's trust, read from the stored template: `sub` is
`repo:andaro74@3157440/agentkeel@1376369685:environment:platform-observer`
and `job_workflow_ref` is
`andaro74/agentkeel/.github/workflows/observe.yml@refs/heads/main`.

## What this corrects

- **`open.md` row 12** ("hashed by nobody"): hashed, for the second
  deploy. The first deploy's template is gone and stays unread.
- **`open.md` row 13** and `milestones/M07/runs/b2_cdk_diff.md`: the loss
  of `§` is not this machine's. `b2_cdk_diff.md` guessed that a hand
  deploy from this machine loses the sign and advised `PYTHONUTF8=1`,
  then found it did not help. The security account's template was
  uploaded through the console from a UTF-8 file and lost the sign too.
  CloudFormation stores it as `?`. The expected hash in `pr2_by_hand.md`
  should have been computed on the `?` form.
- For any later hand deploy: compute the expected hash on the template
  with `§` replaced by `?`, or keep `§` out of cdk-nag reasons.

## What it does not show

- That the first deploy (2026-10-02) held what was uploaded then.
- Anything about the stack's resources as they are now: a template is
  what was asked for, not what exists. No drift detection was run.
- That the person at the console was `hector.flores` rests on the ARN in
  the pasted output.
