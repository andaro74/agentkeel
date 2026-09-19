# M01 — Signed bundle, construct, first tenant

## Ledger row

Written at M01 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 1 |
|---|---|
| Claim | An unsigned or tampered bundle never loads; refagent runs inside the construct |
| Falsifiers | F1.1 an unsigned bundle, a bundle altered after signing, a stack with egress not in the manifest, a deploy from a laptop (the developer role), or an agent built outside the construct loads, deploys or synthesises. F1.2 the construct accepts a role without the boundary. F1.3 the agent role can read its own KMS key policy. F1.4 refagent answers an ordinary golden without a `table_row` and a `clause_id` that exist. |
| Seeded commit | `a7b088e` (S1); `df7c735` (S2); `48669ba` (S3); `1b4c2f6` (S4); `19131e9` (S5); `091cc45` (S6); `2f4cacb` (S7); `6b8b8cf` (S8), each its own commit (SPEC/01 §5) |
| Expected gate output | PR 1: no agent under test, so the envelope is the control's, in M00's form (`control_card_ref` null), gated and recorded as at M00; it says nothing about claim 1. `make plants` lists S1–S8, S7's reader in the tree. On S7: 12 of 12 ordinary and trap results `score` true, `cites` false, `pass` false; `checks.F1_4` fail; build and gate RED. PR 2, on the PR: S1, S2 refused by `verify`, each with its planted reason; S3 (both forms), S5, S8 refused at synth; refagent's envelope has `checks.F1_1`, `F1_2`, `F1_4` pass. No count of refagent's passes is expected: agent history is empty (P7), so the checks decide the row. First `main` run after PR 2 merges: S4 and S6 refused and recorded; `checks.F1_3` from S6; refagent answers from inside the construct. |
| Measured | — |
| PRs used / cap | 1 / 4 |
| State | OPEN |

### Open detail (PR 1, #7, 2026-09-19)

- Opened through `/open-milestone`. SPEC/01 first, then
  `product-spec-reviewer` on it (3 BLOCK, 14 FINDING, 4 NOTE), pasted
  verbatim in `feasibility.md` §1. The seats ruled the three BLOCKs
  before anything else was committed (§2.2); SPEC/01 was revised once on
  them.
- `platform-architect` (R8, seat Security) is written in this PR and was
  run once on SPEC/01's bootstrap and construct design: 4 BLOCK, 21
  FINDING, 4 NOTE. Report in the PR body. It was run as a general agent
  reading `.claude/agents/platform-architect.md` as its instructions,
  because the session that wrote the file could not call it by name yet.
  It is exercised on S3, S5 and S8 at PR 2.
- **Planted** in eight commits, one per seed, `a7b088e` to `6b8b8cf`,
  each with its own test in `tests/test_m01_seeds.py`, before any code
  that reads them. At `6b8b8cf` all eight tests are expected failures;
  `feasibility.md` §3 has each commit's `pytest` result.
- **Read in this PR:** S7 only, by `verdict.build` and `verdict.gate`
  (F1.4; ADR-0004 amendment 2). S7 goes RED. The seven others have no
  reader until PR 2.
- **This PR's run** writes the control's envelope, in M00's form: there
  is no agent under test until PR 2 (ruling A, `feasibility.md` §2.5). It
  is gated and recorded as at M00 and does not measure claim 1.
- The seats' rulings on all 35 items M00 carried in are in
  `feasibility.md` §6, item by item, and in `rulings/pr1.md`.
- Before PR 2's first run: the human redeploys `infra/eval-role` with
  admin (Sonnet 5's profile, item 14; the Deny statement, item 33).

### For Security, at M01 PR 2 open

From the `platform-architect` report, not settled in SPEC/01's text:

- the Budgets action's delay, its filter if the per-agent profile is cut,
  and the worst-case figure it leaves;
- the key policy naming agent roles that do not exist yet: match on a
  role path, and say whether adding an agent is a Security redeploy;
- Gateway targets and Identity credential providers call out with no
  security group: allowlisted, or deferred to M05;
- how an `endpoint_allowlist` hostname becomes a security group rule;
- the S3 and DynamoDB endpoints are gateway endpoints, not interface
  endpoints as SPEC/00 §8 says;
- the eval role's grant for calling refagent's runtime on `main`;
- cosign verify pinning the source-repository id;
- `product-spec-reviewer` finding 5 (who makes S4 and S6, and whether a
  human-written observation can feed a check) and finding 9 (where the
  signed digest lives), with Product.

From the `security-reviewer` report on this PR:

- record the redeploy of items 14 and 33 (`describe-stacks`) and one
  refused call on a denied action.

Ruled in this PR (`feasibility.md` §2.5): item 19's wording (C);
`s3:PutBucketPolicy` added to the Deny (D); `cold-review-ruling` and a
PR-carried ruling, carried to M02 PR 1 as item 1 of `milestones/M02/open.md` (E).

From the `threshold-owner` report on this PR, for the Threshold Owner:

- rule the cap again against PR 2's first agent envelope (150,000 is not
  a measurement);
- refagent's model `version` stays null until Bedrock returns a version
  for `us.anthropic.claude-sonnet-5`; re-ruled at PR 2 with the cap
  (ruling G). `modelLifecycle` for `anthropic.claude-sonnet-5` in
  us-west-2 read ACTIVE on 2026-09-19 (`list-foundation-models`).

For Product, at M01 PR 2 open: whether Gateway and Identity are never-cut
(`product-spec-reviewer` finding 17).
