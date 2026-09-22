---
# M02 PR 1 (#11), Security's key. Product's file is rulings/pr1.md,
# Engineering's is rulings/pr1-engineering.md.
ruling: pr1-security
seat: Security
authorises:
  - infra/construct/governed_agent.py
  - infra/bootstrap/README.md
evidence:
  - milestones/M02/open.md
  - https://github.com/andaro74/agentkeel/actions/runs/35683865472
  - docs/adr/ADR-0006-gateway-endpoints-for-s3-and-dynamodb.md
  - docs/adr/ADR-0008-a-ruling-is-on-main-at-the-merge-commit.md
  - docs/adr/ADR-0003-remaining-path-ownership.md
pr: 11
---

# Ruling: M02 PR 1, Security

Drafted by the session; the human rules as Security before the merge.

## `infra/construct/governed_agent.py` (open.md row 9)

The rights table's encryption moves from `TableEncryption.AWS_MANAGED`
to `TableEncryption.DEFAULT`. The first deploy failed at CREATE on the
table (run 35683865472, 2026-09-22): `AWS_MANAGED` is the `aws/dynamodb`
key, the DynamoDB handler calls `kms:CreateGrant` on it, and
`agentkeel-deploy-boundary` denies that on every key (R4). R4 is left as
it is. `DEFAULT` is the DynamoDB-owned key and makes no KMS call. The
table holds the fictional rights table, which is in the repo in clear;
a customer key for it is M05's. The rendered template differs from
`main` by one line: `SSEEnabled` true → false.

`tests/test_bootstrap.py` gains `NEEDED_BY_PROPERTY` and a test that
fails on any construct resource whose handler needs an action the deploy
boundary denies; at `25b2743` it fails on the table for `kms:CreateGrant`
and at `9ea6405` it passes. The test is Engineering's; the reason it
exists is this ruling.

**The deploy.** This PR's merge triggers `deploy.yml` on `main`. The
human reads the template diff in the PR body before merging and runs the
deploy by merging; if it fails again, row 10's reading at PR 2 is of the
failure, and M01 row 1 stays RED either way.

## `infra/bootstrap/README.md`

Step 3 sets `AWS_DEPLOY_ROLE_ARN` as well as `AWS_EVAL_ROLE_ARN` (the
first deploy's attempt 1). The last section is rewritten to say what has
been observed as of this commit: the bootstrap stack deployed during M01
PR 2, S4 and S6 made on 2026-09-20, the agent deploy failed twice on
2026-09-22, no agent stack yet deployed.

## Rule changes under Product's folder that are Security's

- **ADR-0006 amendment 1**: the `endpoint_allowlist` enum has seven
  names since ruling d was amended at M01 PR 3 (open.md row 22).
- **ADR-0008**: `cold-review-ruling`, `ruling-cited` and `two-key` read
  the merge ref; a ruling is on `main` at the merge commit. This closes
  open.md row 1, which was Security's. SPEC/00 §5 and R9 are amended to
  say so.
- **ADR-0003 amendment 2**: `.github/CODEOWNERS` is Security's; SPEC/00
  §5's Security row names it.

## For Security at PR 2 open

`milestones/M02/README.md`, "For the seats": the ruleset change comes
after PR 2 merges; `GITHUB_TOKEN` and the live ruleset; `gates.yml` on a
fork PR; the rule-suites API and a refused `--admin` merge; the M00
eval-role stack; the first successful deploy.
