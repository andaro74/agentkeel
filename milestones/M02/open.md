# Carried into M02

Started at M01 PR 1, because some items already had M02 as their date
when M01 opened. The M01 close adds whatever else M01 leaves, and
`/open-milestone` reads this file first. An item dated "before M02 PR 1"
is answered before that PR's first commit.

| # | Item | Seat | When |
|---|---|---|---|
| 1 | `cold-review-ruling` passes on a ruling the PR carries itself: its checkout is the PR's merge ref, so a ruling the PR adds counts. Known and by design at M00; the workflow header says so. It is not R9's line, which reads: "No PR in this repo merges before its ruling file is on `main`." Carried with `ruling-cited` (Security ruling E, M01 PR 1; raised by the `security-reviewer` report on M01 PR 1). Since M01 PR 3 the live ruleset requires three contexts, `checks`, `cold-review-ruling` and `evals` (`5693447`). | Security | M02 PR 1 |
| 2 | M01's video. From M01 a milestone's video is committed in the next milestone's PR 1 (ADR-0005 amendment 1). Recorded on `main` at tag `m01`, ≤ 5 minutes and ≤ 40 MiB, committed as an LFS object in M02 PR 1 with its entry in `docs/video/README.md`. | Product | M02 PR 1 |
| 3 | Retire `g-012` (Finding F0.1): `retired: M02`, never renamed. The two-key "merged properly" case of SPEC/00 §8 M02, Door 2. M01 open item 24. | Data Owner | M02 PR 1 |
| 4 | The replacement trap is `g-021`, a sequel that does not inherit the original's rights (`sequel_no_inherit`). The frozen control cannot emit that code, so it never passes; P7 allows that. `g-016` to `g-020` stay red-team at M03. M01 open items 25, 26. | Data Owner, with Threshold Owner | M02 PR 1 |
| 5 | `validate` diffs the live `main` ruleset against `infra/ruleset/main.json`, and fails unless `bypass_actors` is `[]`. M01 open item 31. `milestones/M01/rulings/pr3.md` already runs the same comparison by hand ("the two commands must agree"); this makes it mechanical. | Security | M02 PR 1 |
| 6 | "CI-written" becomes real with `two-key` (`GITHUB_ACTIONS == "true"` is an environment variable). M01 open item 8. | Engineering | M02 |
| 7 | The workflow-hash check can be edited in the same PR as the workflow it guards, and it hashes the workflow's text only, not the `Makefile`, `src/` or `scripts/` it runs (`infra/ruleset/README.md`). `ruling-cited` on `infra/**` closes the first. M01 open item 29. | Security | M02 |

## 8. Carried from M01 PR 2's cold review, and again at PR 3 (Product, `.claude/skills/**`) — M02 PR 1

**A cold review read the tree, not the diff, and nothing would have caught
it.** Of the four seat subagents `/cold-review` called on M01 PR 2, three
reported that Bash was unavailable to them, so they reviewed the tree at
HEAD instead of `git diff main...HEAD`. Their findings therefore cannot say
which of them this PR caused and which predate it, and every one had to be
re-checked by hand before it could be triaged.

The skill names which subagent to call per path and says nothing about the
tools each needs. `make validate` does not read subagent definitions. The
only reason this was noticed is that three of the reports opened by
admitting it — had they not, the review would have read as four seats
agreeing on the state of a diff none of them had seen.

Settle at M02 by one of: granting Bash in each `.claude/agents/*.md` whose
seat reviews a diff; or a line in `.claude/skills/cold-review` requiring
each report to state whether it read the diff or the tree, so a report that
read the tree is visibly a weaker witness. M02 is the milestone whose claim
is that seat-owned files change only with a ruling, and a review that cannot
see the change is that claim's blind spot.

**It happened again at M01 PR 3:** `security-reviewer` said "I could not run
git" and `threshold-owner` said "I read the tree at HEAD e319528, not a git
diff". Only `engineering-cold-reviewer` read the diff.


## Added at the M01 close (PR 4)

The M01 close found every Finding and Unsure item of the milestone that had
no home, and gave each one a row here. Rows 9 and 10 come first: they are
why row 1 closed RED. Sources: `milestones/M01/feasibility.md` (items by
number), `rulings/pr1.md`, `pr2.md`, `pr2-cold-review.md` ("PR2 cold N"),
`pr3.md`, `pr3-cold-review.md` ("pr3-cold"), and the bodies of PRs #7 to #9.

| # | Item | Seat | When |
|---|---|---|---|
| 9 | **The first deploy failed; refagent has never run inside the construct.** Run 35683865472 on `main`, merge commit `616b620`. Attempt 1: repository variable `AWS_DEPLOY_ROLE_ARN` was never set, because `infra/bootstrap/README.md` step 3 sets only `AWS_EVAL_ROLE_ARN`. The human set it on 2026-09-22; the README still has to say so. Attempt 2: `CREATE_FAILED` on the rights table. `TableEncryption.AWS_MANAGED` (`infra/construct/governed_agent.py`, the `aws/dynamodb` key) makes CloudFormation call `kms:CreateGrant`, and `agentkeel-deploy-boundary` denies it (R4). The cause on our side: the DynamoDB handler list includes `kms:CreateGrant`, and PR 3 left it out as "only for a customer key". The fix is `TableEncryption.DEFAULT`, which needs no KMS call and leaves R4 alone, plus a test that fails on any construct resource whose handler needs an action the deploy boundary denies. The human deleted the `ROLLBACK_COMPLETE` stack on 2026-09-22. Image `sha256:6fcd185b…` stays in ECR, tagged with bundle digest `26ed38d1…`; `deploy.yml` reuses it on a rerun. **M01 row 1 stays RED.** A later successful deploy does not reopen it; it gives M02 a runtime to measure. | Security | M02 PR 1 |
| 10 | Read from the first successful deploy, not assumed: whether the image pull goes through the runtime's network interface (pr3.md Unsure, ruling d amended); cfn-exec's `vpc-lattice` actions scoped from CloudTrail (pr3.md Unsure 3, pr3-cold F7); the load check's answer. **Recorded as settled at the close:** SSM parameter resolution (pr3-cold F5), because attempt 2 created its change set and failed only at a resource. | Security | M02 PR 1, after row 9 |
| 11 | The envelope is written by the PR's own code, and since ADR-0007 that includes `mode` (PR2 cold 14; pr3-cold F9). The bytes can change mid-run (pr3-cold F10). The image is not reproducible: the base image is by tag, the packages by range, `agents/__init__.py` sits outside the bundle (pr3-cold F11). A fork PR still merges with no envelope of its own (the remainder of BLOCK C, pr2.md). | Security, with Engineering | M02 PR 1 |
| 12 | The instruments behind F1.1 and F1.3 (PR2 cold 1, 3, 4, 5, 38). **4 first:** the CloudTrail check never reads the refusing `principal`, which weakens F1.1. Also: agent raw not replayable; `both()` merges both halves of F1.1; `message_must_contain`; `thresholds_at`'s fallback. | Engineering | M02 PR 1 |
| 13 | Engineering's smaller items: `agents/refagent/server.py` hard-codes a profile and its docstring is wrong (PR2 cold 7, 8); `run.py`'s dirty check excludes all of `evals/`, goldens included (PR2 cold N4); the gate takes build's token sums as given (pr1 N1, #7 Unsure 8); Makefile paths that write no envelope (pr1 N3); `gate.manifest_at` falls back to the working tree (pr3-cold N4); two IAM5 rows under one reason in the refagent NagReport (pr3-cold N5). | Engineering | M02 |
| 14 | The first real LFS object, with M01's video in row 2 (#7 Unsure 10); `infra` is a default dependency group (#8 Unsure 5). | Engineering | M02 PR 1 |
| 15 | Security's standing items. Agent ceiling `bedrock-agentcore:*` (PR2 cold 17; pr3-cold sec N3). The developer role is assumable account-wide (18). The eval role carries the deploy boundary (19). The key policy leaves two roles unnamed (20). The `--measure` flag (21). `sign-fixture.yml` keeps write and `id-token` permissions (22). The nag-suppression check accepts the literal "SPEC/01 §6" (PR2 cold N2). Nothing constrains an agent-path role's trust policy (pr3.md Unsure 5). The deploy role's `PassRole` has no `iam:PassedToService` (pr3-cold sec N2). A change to `data/rights_table.json` does not reload the table (sec N5). Prefix lists are written by hand (#8 Unsure 2). The construct checks read CDK's typed properties (#8 Unsure 3). | Security | M02 |
| 16 | A second workflow file refused, never observed (item 12). The M00 stack `AgentkeelM00EvalRole` destroyed and `infra/eval-role/` removed (item 20, ruling f, PR2 cold N5). | Security | M02 PR 1 |
| 17 | The instruments' independence. `human_said` in the S4 and S6 observations was reconstructed from CloudTrail, so the check is vacuous at M01; from M02 the human's own output is kept (pr2.md). No instrument is run as its own principal before a run depends on it (pr2.md; the eval role's missing `cloudtrail:LookupEvents` was that case). | Security, with Product | M02 PR 1 |
| 18 | The Threshold Owner's re-rules. Is Nova Micro still a fair control (item 21, PR2 cold 33)? The cap against measured spend: `e97125e` spent 54,156 tokens (`tokens_in` + `tokens_out`, both subjects) against 150,000 (finding 31). The monthly USD 300 (ruling a′). Commit `check_model_access`'s stdout under `runs/` (PR2 cold 34). One cap for two run shapes (32). `max_tokens_per_session` and `daily_usd` land unruled, and `daily_usd` collides with Budgets' figure by name (36). | Threshold Owner | M02 PR 1 |
| 19 | `pinned_roles` carry region and version (#7 threshold-owner NOTE). The T2 limit: the region is the one the client was built with, and Converse does not report the region that served the call (pr3-threshold-owner.md). | Threshold Owner | M04 PR 1 |
| 20 | The Tool Owner's items: semver computed, not asserted (PR2 cold 24); the not-found branch decides the clause (26); nested `row` (25); `pinned_roles` left open (27); `territory` and `platform` typing (29). | Tool Owner | M02 PR 1 |
| 21 | Which seat `two-key` counts for Engineering's key (#7 Unsure 4). | Product | M02 PR 1 |
| 22 | Prose that M01 left wrong. S6's run file uses `--key-id alias/...`, which KMS refuses for `GetKeyPolicy` (pr2.md). ADR-0006 says "the five names", and since ruling d was amended there are seven (an ADR amendment). | Product | M02 PR 1 |
| 23 | Forward to M05: an author who never installs the platform's checks, bound by a CloudFormation Hook or an SCP (BLOCK D, pr2.md, pr3-product.md); the agent ceiling of row 15. | Security | M05 open |
