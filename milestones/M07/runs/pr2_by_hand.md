# M07 PR 2 and PR 3: what is done by hand, and in what order

For andaro74, as Security. `rulings/pr2-security.md` item 12 is the order;
this is each step with its commands. Nothing here is done by a session,
and no stack is deployed from a commit whose Security ruling still reads
DRAFT (the sentence PR 2's version of this file opened with, restored
after the reviews of PR 3).

Git Bash, from the repository's root. The agent account is 581208540944
(the default profile, the account's admin user). The security account is
897698239547: **no local profile reaches it.** Its stack is updated by
`hector.flores` in the console (B1).

## Corrected at M07 PR 3 (2026-10-02)

This file was written at PR 2 with three faults. Each is corrected below
where it stood.

- **B1 named a profile that does not work.** `agentkeel-security` assumed
  `OrganizationAccountAccessRole`, which was deleted at M05, by design
  (`infra/security/README.md`: "Any later change to this stack is deployed
  as `hector.flores`"). `npx aws-cdk@2 diff --profile agentkeel-security`
  could never have run. B1 is now the console's change set.
- **Sections A and B said "before PR 2 merges".** PR 2 merged (#39,
  `3bfd074`) with only C's precondition met. What was done and what was
  not is the table below.
- **A4 said the two ids go into `rulings/pr2-security.md`.** From PR 3 the
  grant block is `infra/platform_grant.yaml` (item 13j).

| Step | State on 2026-10-02, and where it was read |
|---|---|
| A1, A2 the two new Apps | **Not done.** `gh api orgs/agentkeel-studio/installations` lists one App, `agentkeel-platform` (5144253) |
| A3 the two environments and keys | **Part.** `platform-observer` exists (`gh api repos/andaro74/agentkeel/environments`); `platform-upgrades` does not. Whether a key is in either was not read: a job cannot list them |
| A4 the two ids in the grant block | **Not done.** Both `app_id` are null |
| B1 the security account's stack | **Done**, by `hector.flores` in the console, 2026-10-02, from a template synthesised from `main` (`3bfd074`). The role `agentkeel-observation-put` was created at 15:39:21Z (as the human read it in the console; no session can read that account). `AWS_OBSERVATION_PUT_ROLE_ARN` was set at 15:40:56Z (`gh variable list`). **No put under `bundles/` or `observations/` has been made or refused yet** |
| B2 the bootstrap stack | **Not done.** `AWS_MODEL_WATCH_ROLE_ARN` and `AWS_ENVELOPE_ROW_PUT_ROLE_ARN` are not set |
| B3 Grafana's stack | **Not done** |
| C the grant to `agentkeel-platform` | **Done**, after PR 2 merged. The installation holds Administration: write (`gh api orgs/agentkeel-studio/installations`) |

**The order now, and the one thing held back.** A1, A2, A3, A4's read,
then give the session the two ids; B2 **without its
`AWS_MODEL_WATCH_ROLE_ARN` line**; B3. `model-watch.yml` opens the swap
pull request by itself, at 06:17 UTC or on a dispatch, once three things
exist on `main` and in the repository: that variable, the
`agentkeel-upgrades` id in the grant block, and the App's key in
`platform-upgrades`. The id reaches `main` when PR 3 merges. **So the
variable `AWS_MODEL_WATCH_ROLE_ARN` is set last, and only after the swap's
statement (`runs/f7_3_rollback.yaml`) is pushed.** The role itself may be
deployed with B2: a role with no variable naming it starts nothing.

**When B2 and B3 are deployed is Security's to rule, and is not ruled as
this is written** (security-reviewer 5, platform-architect 2 and cold
review F2 on M07 PR 3: this file first said "from the branch `m07-pr3`",
which changes refagent's key policy from a head no ruling covers). PR 3
adds the two new roles to that key policy (item 13h), so the stack is
deployed once, from a commit that holds it. Either:

- after PR 3 merges, from `main`; or
- before the merge, from `m07-pr3`, only after `rulings/pr3-security.md`
  reads "Ruled by", from one named commit, with the `cdk diff --strict`
  output kept.

Whichever it is, the table below is filled when it is done.

| Stack | Commit deployed (`git rev-parse HEAD`) | Deployed at | The diff read, and where its output is kept |
|---|---|---|---|
| B1 security | `3bfd074` (as the human stated it) | 2026-10-02 | the console's change set; not kept. **Owed** (platform-architect 3 on M07 PR 3): the sha256 of `AgentkeelSecurity.template.json` synthesised at that commit, and the same hash of the template CloudFormation stores, read by `hector.flores` |
| B2 bootstrap | not deployed | | |
| B3 Grafana | not deployed | | |

## A. The two new Apps, their environments and keys

Ruled 2026-10-02 (items 2, 3, 13a). `agentkeel-platform` is not touched.

### A1. `agentkeel-upgrades`, the App that opens pull requests

1. https://github.com/organizations/agentkeel-studio/settings/apps/new
2. Name `agentkeel-upgrades`. Homepage `https://github.com/andaro74/agentkeel`.
3. Webhook: untick **Active**.
4. Repository permissions, and no others: **Contents: Read and write**;
   **Pull requests: Read and write**; Metadata: Read-only (GitHub sets it).
   No organisation permission, no account permission. Not Checks, not
   Administration, not Workflows.
5. "Where can this GitHub App be installed?": **Any account**. It is
   installed on two accounts, and GitHub allows that only for a public
   App (`rulings/pr2-security.md` item 13a; ruled by that file's first line, as the seat confirmed at PR 3).
6. Create. Note the **App ID**. Generate a private key; a `.pem` file
   downloads.
7. Install it on `agentkeel-studio`: **All repositories**.
8. Install it on `andaro74`: **Only select repositories**, `agentkeel`.

### A2. `agentkeel-observer`, the App that reads

1. The same page. Name `agentkeel-observer`. Webhook not active.
2. Repository permissions, and no others: **Administration: Read-only**;
   **Checks: Read-only**; **Contents: Read-only**; **Pull requests:
   Read-only**; Metadata: Read-only.
3. "Where can this GitHub App be installed?": **Only on this account**.
4. Create. Note the **App ID**. Generate a private key.
5. Install it on `agentkeel-studio`: **All repositories**. Not on
   `andaro74`.

### A3. The two environments, each holding one key

In `andaro74/agentkeel`, Settings, Environments, for each of
`platform-upgrades` and `platform-observer` (the second exists; check it
against steps 2 to 4):

1. New environment, by that name.
2. Deployment branches and tags: **Selected branches and tags**; add one
   rule, the branch `main`. No other rule.
3. Untick **Allow administrators to bypass configured protection rules**.
4. Add one environment secret and no other:
   `UPGRADES_APP_PRIVATE_KEY` in `platform-upgrades`,
   `OBSERVER_APP_PRIVATE_KEY` in `platform-observer`. The value is the
   whole `.pem` file. Then delete the `.pem` from disk.

Or, for steps 1 to 3, from the shell (step 4's secret is read from the
`.pem` once and the file removed in the same command):

```sh
for env in platform-upgrades platform-observer; do
  gh api -X PUT "repos/andaro74/agentkeel/environments/$env" \
    -F "can_admins_bypass=false" \
    -F "deployment_branch_policy[protected_branches]=false" \
    -F "deployment_branch_policy[custom_branch_policies]=true"
  gh api -X POST "repos/andaro74/agentkeel/environments/$env/deployment-branch-policies" \
    -f name=main -f type=branch
done
gh secret set UPGRADES_APP_PRIVATE_KEY --env platform-upgrades < agentkeel-upgrades.pem
gh secret set OBSERVER_APP_PRIVATE_KEY --env platform-observer < agentkeel-observer.pem
rm agentkeel-upgrades.pem agentkeel-observer.pem
```

If the `POST` is refused for `platform-observer` because it already has
the `main` policy, that is not a fault; A4 reads what is there.

### A4. Read back, and give the session the two ids

```sh
gh api orgs/agentkeel-studio/installations \
  --jq '.installations[]|[.app_slug,.app_id,.repository_selection,(.permissions|tostring)]|@tsv'
for env in platform-app platform-upgrades platform-observer; do
  gh api "repos/andaro74/agentkeel/environments/$env" --jq '[.name,.can_admins_bypass]|@tsv'
  gh api "repos/andaro74/agentkeel/environments/$env/deployment-branch-policies" --jq '.branch_policies[]|[.name,.type]|@tsv'
  gh api "repos/andaro74/agentkeel/environments/$env/secrets" --jq '.secrets[].name'
done
gh api repos/andaro74/agentkeel/actions/secrets --jq '.secrets[].name'   # no App key among them
```

Expected: three Apps on the organisation, each on `all`, with the
permissions of the grant block and no more; `agentkeel-platform` with
Administration: write (C is done); each environment `false`, one policy
`main branch`, one secret; the repository's own secrets
`AGENTKEEL_GRAFANA_TOKEN` and `RULESET_TOKEN`. That `agentkeel-upgrades`
is on `andaro74` with one repository, and that 5144253 is not there, is
read in the browser (Settings, Applications, Installed GitHub Apps): no
API a user's token may call lists it.

The two App IDs go into `infra/platform_grant.yaml` (`app_id:` under
`agentkeel-upgrades` and `agentkeel-observer`), in a commit of their own
on `m07-pr3`, by the session. Until they are on `main`, every keyed job
of the three new workflows stops at its first step.

## B. The stacks, each after reading its diff

### B1. The security account (items 9, 11, 13e). Done on 2026-10-02.

How it is done, for the next change to this stack. `hector.flores` is the
security account's own admin; nobody else, and no role in the agent
account, can change it.

1. On this machine, from the commit to deploy. No AWS credentials are
   used: the stack names its own account and region.

   ```sh
   unset VIRTUAL_ENV
   CDK_OUTDIR="$HOME/agentkeel-security-out" uv run python -m infra.security.app
   ls "$HOME/agentkeel-security-out/AgentkeelSecurity.template.json"
   ```

2. `hector.flores` signs in to the console of 897698239547, region
   us-west-2, CloudFormation, stack `AgentkeelSecurity`: **Update**,
   **Replace existing template**, upload
   `AgentkeelSecurity.template.json`. No parameter changes. Tick the IAM
   acknowledgement. **Create change set**, not a direct update.
3. Read the change set before executing it. At M07 PR 2 it showed, and
   was to show nothing else:
   - the bucket's policy modified: two new statements,
     `ABundleIsWrittenOnce` and `AnObservationIsWrittenOnce`, each a Deny
     of `s3:PutObject` without `If-None-Match`;
   - the trail modified: two more prefixes in its data-event selector
     (`bundles/`, `observations/`);
   - `agentkeel-audit-read`'s policy modified: `observations/*` added to
     what it lists and reads, `bundles/*` to what it lists (13e);
   - `agentkeel-answer-put`'s policy modified: one new statement,
     `PutSignedBundlesOnly`, on `bundles/*`;
   - one role added, `agentkeel-observation-put`, with its policy,
     trusting `observe.yml@refs/heads/main`, with `s3:PutObject` on
     `observations/*`;
   - one output added, `ObservationPutRoleArn`.

   No replacement of the bucket, and no change to its lock or retention.
   Anything else is a stop.
4. Execute. Then, on this machine:

   ```sh
   gh variable set AWS_OBSERVATION_PUT_ROLE_ARN --body "arn:aws:iam::897698239547:role/agentkeel-observation-put"
   ```

PR 3 changes nothing under `infra/security/` but its README, so B1 is not
made again for PR 3.

### B2. The agent account's bootstrap stack (items 13b, 13c, 13d, 13h)

From the commit Security rules (above). Write the commit down first.

```sh
git fetch origin && git checkout <main, or m07-pr3> && git pull --rebase
git rev-parse HEAD                                               # the commit deployed: into the table above
aws sts get-caller-identity                                      # Account 581208540944
cd infra/bootstrap && npx aws-cdk@2 diff --strict | tee "$HOME/agentkeel-b2-diff.txt"
```

The diff should show, and nothing else:

- `agentkeel-evals`: three new statements,
  `ReadWhichBytesATemplateAgentsRuntimeRuns`, `ReadATemplateAgentsRuntime`
  and `ReadATemplateAgentsImageTags`, each one read-only action (13c);
- one new role, `agentkeel-model-watch`, trusting
  `model-watch.yml@refs/heads/main`, with `bedrock:GetFoundationModel`
  on `foundation-model/*` and the Deny every platform role carries (13b);
- one new table, `agentkeel-envelopes`, key `commit`, retained (13d);
- one new role, `agentkeel-envelope-row-put`, trusting
  `evals.yml@refs/heads/main`, with `dynamodb:Scan` and `dynamodb:PutItem`
  on that table (13d);
- **refagent's key policy** (13h, added at PR 3): the Deny statement
  `NoPlatformRoleChangesThisKey` names two more principals,
  `role/agentkeel-model-watch` and `role/agentkeel-envelope-row-put`. A
  Deny made wider; no Allow changes;
- two new outputs.

No change to the deploy role, the execution role, either boundary, the
VPC or the guardrail, and no other change to the key. Anything else is a
stop. Then:

```sh
npx aws-cdk@2 deploy
cd ../..
gh variable set AWS_ENVELOPE_ROW_PUT_ROLE_ARN --body "arn:aws:iam::581208540944:role/agentkeel-envelope-row-put"
```

**Held back, and set last, after the swap's statement is pushed:**

```sh
gh variable set AWS_MODEL_WATCH_ROLE_ARN --body "arn:aws:iam::581208540944:role/agentkeel-model-watch"
```

### B3. Grafana's stack (item 13d), after B2

```sh
cd infra/grafana && npx aws-cdk@2 diff
```

The diff should show, and nothing else: one new Glue table,
`default.agentkeel-envelopes` (commit, verdict, mode); two new statements
on `agentkeel-registry-connector-role`, `ReadTheEnvelopesRowsOnly` and
`TheEnvelopesSchemaOnly`. No change to the workspace's role, the
connector, the catalog or the workgroup. Then:

```sh
npx aws-cdk@2 deploy
cd ../..
```

Then, in the workspace, import `infra/grafana/panel2.json` as a new
dashboard (Dashboards, New, Import). No data source is added: panel 2
uses `registry`, the one panel 1 uses. Its table is empty until the first
push to `main` after B2, when `evals.yml`'s `envelope-rows` job writes one
row per envelope.

## C. The grant (item 12.4). Done on 2026-10-02, after PR 2 merged.

1. https://github.com/organizations/agentkeel-studio/settings/apps/agentkeel-platform/permissions
   Repository permissions: **Administration: Read and write**. Save.
2. https://github.com/organizations/agentkeel-studio/settings/installations
   Open `agentkeel-platform`; **Review request**; accept the new
   permission.
3. Read back:

```sh
gh api orgs/agentkeel-studio/installations \
  --jq '.installations[]|select(.app_slug=="agentkeel-platform")|.permissions'
gh workflow run platform-check.yml --ref main
gh run list --workflow platform-check.yml --limit 1
```

The run's `post` job reads the grant back first; its artifact
`grant-agentkeel-platform` is what it read.

## D. Before 2026-10-31

Renew the Grafana observer token (it expires 2026-10-31T07:00:01Z), and
set `AGENTKEEL_GRAFANA_TOKEN` to the new one. Until then nothing changes;
after that date, unrenewed, panel 1's and panel 2's live reads are unread.
