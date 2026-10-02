# M07 PR 2: what is done by hand, and in what order

For andaro74, as Security. `rulings/pr2-security.md` item 12 is the order;
this is each step with its commands. Nothing here is done by a session,
and nothing here is done before that ruling file reads "Ruled by". None
of it has been done as this file is written.

Git Bash, from the repository's root. The agent account is 581208540944
(the default profile, `hector.acevedo`); the security account is
897698239547 (profile `agentkeel-security`).

**Not in this list, and not before PR 2 has merged:** raising
`agentkeel-platform` (5144253) to Administration: write. That is step C.

## A. Before PR 2 merges: the two new Apps, their environments and keys

Ruled 2026-10-02 (items 2, 3). `agentkeel-platform` is not touched.

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
   App (`rulings/pr2-security.md` item 13a, which is yours to rule).
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
`platform-upgrades` and `platform-observer`:

1. New environment, by that name.
2. Deployment branches and tags: **Selected branches and tags**; add one
   rule, the branch `main`. No other rule.
3. Untick **Allow administrators to bypass configured protection rules**.
4. Add one environment secret and no other:
   `UPGRADES_APP_PRIVATE_KEY` in `platform-upgrades`,
   `OBSERVER_APP_PRIVATE_KEY` in `platform-observer`. The value is the
   whole `.pem` file. Then delete the `.pem` from disk.

Or, for steps 1 to 3, from the shell (step 4's secret is typed, not
piped from a file left on disk):

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
permissions of `rulings/pr2-security.md`'s grant block and no more;
`agentkeel-platform` still with Administration: read; each environment
`false`, one policy `main branch`, one secret; the repository's own
secrets `AGENTKEEL_GRAFANA_TOKEN` and `RULESET_TOKEN`. That
`agentkeel-upgrades` is on `andaro74` with one repository, and that
5144253 is not there, is read in the browser (Settings, Applications,
Installed GitHub Apps): no API a user's token may call lists it.

The two App IDs go into the grant block of `rulings/pr2-security.md`
(`app_id:` under `agentkeel-upgrades` and `agentkeel-observer`), in a
pushed commit, before any attempt. Until they are there, every keyed job
of the three new workflows stops at its first step.

## B. Before PR 2 merges: the stacks, each after reading its diff

### B1. The security account (ruled: items 9 and 11; item 13e is yours to rule)

```sh
aws sts get-caller-identity --profile agentkeel-security        # Account 897698239547
cd infra/security && npx aws-cdk@2 diff --profile agentkeel-security
```

The diff should show, and nothing else:

- the bucket's policy: two new statements, `ABundleIsWrittenOnce` and
  `AnObservationIsWrittenOnce`, each a Deny of `s3:PutObject` without
  `If-None-Match`;
- the trail: two more prefixes in its data-event selector (`bundles/`,
  `observations/`);
- `agentkeel-audit-read`: `observations/*` added to what it lists and
  reads, `bundles/*` to what it lists (13e);
- `agentkeel-answer-put`: one new statement, `PutSignedBundlesOnly`, on
  `bundles/*`;
- one new role, `agentkeel-observation-put`, trusting
  `observe.yml@refs/heads/main`, with `s3:PutObject` on `observations/*`;
- one new output, `ObservationPutRoleArn`.

No change to the bucket itself, its lock or its retention. Anything else
is a stop. Then:

```sh
npx aws-cdk@2 deploy --profile agentkeel-security
cd ../..
gh variable set AWS_OBSERVATION_PUT_ROLE_ARN --body "arn:aws:iam::897698239547:role/agentkeel-observation-put"
```

### B2. The agent account's bootstrap stack (items 13b, 13c, 13d: yours to rule first)

```sh
aws sts get-caller-identity                                      # Account 581208540944
cd infra/bootstrap && npx aws-cdk@2 diff --strict
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
- two new outputs.

No change to the deploy role, the execution role, either boundary, the
key policy, the VPC or the guardrail. Anything else is a stop. Then:

```sh
npx aws-cdk@2 deploy
cd ../..
gh variable set AWS_MODEL_WATCH_ROLE_ARN --body "arn:aws:iam::581208540944:role/agentkeel-model-watch"
gh variable set AWS_ENVELOPE_ROW_PUT_ROLE_ARN --body "arn:aws:iam::581208540944:role/agentkeel-envelope-row-put"
```

If you rule 13d's alternative, do not set the last variable: the
`archive` job then writes nothing and says so.

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
push to `main` after B2, when `evals.yml`'s `archive` job writes one row
per envelope.

## C. After PR 2 has merged, and only then: the grant (item 12.4)

Not before. `main` then no longer mints a token with no repository.

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
`grant-agentkeel-platform` is what it read. This step, and every attempt
after it, is stated before and pushed first (SPEC/07 §5.1): it belongs to
the session that follows the merge, not to PR 2.

## D. Before 2026-10-31

Renew the Grafana observer token (it expires 2026-10-31T07:00:01Z), and
set `AGENTKEEL_GRAFANA_TOKEN` to the new one. Until then nothing changes;
after that date, unrenewed, panel 1's and panel 2's live reads are unread.
