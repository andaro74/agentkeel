# The reads SPEC/07 §11 owed, made before M07 PR 2's first code commit

Read-only. GitHub with `andaro74`'s own token (`gh`; an admin of
`andaro74/agentkeel`, an owner of `agentkeel-studio`). AWS as
`arn:aws:iam::581208540944:user/hector.acevedo` in the agent account,
us-west-2. Nothing was changed by a read. Two things were changed by the
human before these reads, each named below: one environment setting, and
the Apps installed on a personal account. Each line is one reading by
hand; none is a check, and only the dispatch from a branch is a seeded
case that fired.

## R1. The key's environment, and the dispatch from a branch

| Read at (UTC) | What | Reading |
|---|---|---|
| 2026-10-02T02:12Z | `platform-app`'s rules (`platform_app_environment.json`, `platform_app_branch_policies.json`) | one branch policy, `main`, type branch; `can_admins_bypass: true` |
| 2026-10-02T03:16Z | where the key is stored (`platform_app_read.md`) | `PLATFORM_APP_PRIVATE_KEY` is a secret of the environment only |
| before 04:12Z | **changed by the human as Security**: "Allow administrators to bypass configured protection rules" switched off | read back `false` (`platform_app_environment_after.json`, read 2026-10-02T11:14Z) |
| 2026-10-02T04:12:44Z | **S0's second attempt**: `gh workflow run platform-check.yml --ref m07-pr1`, by `andaro74`, after one empty commit on owner-check's `first-pr` (`3e79a086`) so that `find` had a head to list | run 36963543726 (`f7_0_dispatch_from_branch.json`): `find` success; `evaluate (agentkeel-studio/owner-check, 1, 3e79a086…)` success; **`post` failure, no runner, no steps**, annotation: `Branch "m07-pr1" is not allowed to deploy to platform-app due to environment protection rules.` |
| 2026-10-02T04:20Z | the environment's deployments | this rejected one from `m07-pr1`; the four before it all from `main` (`39031e7` twice, `c7ef180` twice) |

The dispatch was refused by the environment, with admin bypass off, before
any grant. A skip would not have counted: `evaluate` ran, so `post` was
reached. What it does not show: that an admin cannot add a branch policy,
run, and remove it (one person holds every seat, R1).

Side effect, expected: owner-check #1's head is now `3e79a08`. The
scheduled check on `main` failed it at 2026-10-02T04:26:47Z, "3 refused",
the hidden `bypass_actors` among them. The owner's test at M07 starts from
a fresh empty commit after the grant.

## R2. The App's installation

`gh api orgs/agentkeel-studio/installations`, 2026-10-02T04:30Z and again
11:14Z (`platform_app_installation.json`). A user's token with `read:org`
can read it; `GET /user/installations` cannot (HTTP 403), which is what
M07 PR 1 tried.

| | |
|---|---|
| App | `agentkeel-platform`, id 5144253, owned by `agentkeel-studio` |
| Installation | id 166731821, target the organisation, not suspended |
| `repository_selection` | **all** |
| Permissions | administration read; checks write; contents read; metadata read; pull requests read |
| Events | none |
| Pending permission change | none: the installation's set equals the App's registered set (`gh api apps/agentkeel-platform`) |
| On `andaro74` (personal account) | **not installed**. Read by the human in the browser (Settings, Applications, Installed GitHub Apps), 2026-10-02 |

**Changed by the human, 2026-10-02:** four third-party Apps were installed
on the personal account (AWS Amplify, Contentstack Launch, GitHub Learning
Lab, Vercel) and were uninstalled. The page then read "No installed GitHub
Apps". So no App can post a check on `andaro74/agentkeel` today.
`infra/ruleset/main.json` still requires its checks by name, and a commit
status of the right name from a token with `repo` scope would satisfy
one: a named gap (SPEC/06 §8; `open.md` row 36), not closed by this.

## R6. The models

`aws bedrock get-foundation-model`, 2026-10-02T11:12Z
(`model_lifecycle_2026-10-02.json`); `aws bedrock list-inference-profiles`.

| Model | Lifecycle | Profile |
|---|---|---|
| `anthropic.claude-sonnet-4-6` (refagent's pin) | ACTIVE, no end-of-life date | `us.anthropic.claude-sonnet-4-6` ACTIVE |
| `anthropic.claude-haiku-4-5-20251001-v1:0` (the candidate) | ACTIVE, no end-of-life date | `us.anthropic.claude-haiku-4-5-20251001-v1:0` ACTIVE |
| `anthropic.claude-sonnet-4-5-20250929-v1:0` | ACTIVE | not read |
| `anthropic.claude-sonnet-4-20250514-v1:0` (M04's deprecation plant) | LEGACY, `endOfLifeTime` 2026-10-14T08:00Z | not read |

- The eval role may already invoke Haiku 4.5: it is in
  `infra/bootstrap/app.py` `EVAL_CANDIDATES`. No model access is added
  for the swap's own run. refagent's runtime role is built from the
  manifest's pin at synth, so it takes the candidate at the deploy of a
  merged swap and loses it at the deploy of the revert.
- No call was made to Haiku 4.5 in these reads. It answered a call on
  2026-09-26 (`milestones/M04/runs/model_access_2026-09-26.md`).
- refagent's pin has no end-of-life date, so `model-watch` writes no
  `deprecated_after` for it. The one pinned model with a date is M04's
  plant, which no run calls.
- A swap run is about 105,000 tokens (A-vs-A, both subjects twice;
  `thresholds.yaml`), against a cap of 150,000. This PR's two runs were
  49,615 and 48,676.

## R7. What a retirement can delete, and what stays

From the tree at `a2c5a61`, and the account as listed 2026-10-02T11:13Z.

- **The deploy role cannot delete a stack.** `infra/bootstrap/app.py`,
  `DeployThroughCloudFormationOnly`: `CreateStack`, `UpdateStack`,
  change sets, `Describe*`, on `stack/agentkeel-*/*`. No `DeleteStack`.
- **It can update one, and the stack's execution role can delete a
  template agent's runtime**: `bedrock-agentcore:DeleteAgentRuntime` on
  `runtime/refagent*` and `runtime/agentkeel_*`. So a retirement made as
  a stack update to a template without the runtime needs no new grant.
- **The construct keeps three resources when a stack or resource is
  removed** (`infra/construct/governed_agent.py`,
  `RemovalPolicy.RETAIN`): the agent's key, its alias
  `alias/agentkeel-<name>`, and its rights table.
- **No platform role may schedule the key's deletion**: the key policy's
  `NoPlatformRoleChangesThisKey` denies `kms:ScheduleKeyDeletion`,
  `DisableKey`, `PutKeyPolicy` and seven more to every agent role and
  every platform role (R4). M07 PR 1's run file said the key is
  "scheduled for deletion"; that was wrong and was corrected there to
  "R7's to rule". The key stays.
- **What the key encrypts.** The agent's role may `Decrypt` and
  `GenerateDataKey` with it. The rights table uses DynamoDB's default
  encryption, not this key. The audit bucket is in the security account
  under its own encryption. So no record a retirement must keep depends
  on the agent's key.
- **The runtime's log group** is not in the stack: the agent's role may
  `logs:CreateLogGroup` for its own, and AgentCore makes it at run time.
  It is not removed by a stack update or deletion.
- **`bundles/`** is not a prefix of the audit bucket's policy today
  (`infra/security/`): `AWSLogs/`, `agents/`, `test/`, `envelopes/`.
  Writing a bundle there needs one statement in the security account and
  its hand deploy. That is a grant.
- The account, listed: stacks `AgentkeelBootstrap`, `agentkeel-refagent`,
  `AgentkeelAudit`, `AgentkeelIngest`, `AgentkeelGrafana` and its
  connector. The registry holds one row, `refagent`, commit `39031e7`,
  deployed 2026-10-01T12:17:30Z. No stack `agentkeel-owner-check`.
- Not read: `DeleteAgentRuntime`'s behaviour on a runtime with an
  endpoint. It cannot be read without deleting one; S2's attempt is the
  first.

## R8. Grafana

`aws grafana list-workspace-service-account-tokens`, workspace
`g-745446386a`, 2026-10-02T11:13Z: service account 4,
`agentkeel-observer`, Viewer; one token, created 2026-10-01T11:25:43Z,
**expires 2026-10-31T07:00:01Z**, last used 2026-10-02T03:43:55Z.
