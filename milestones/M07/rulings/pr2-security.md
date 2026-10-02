---
# M07 PR 2 (to open as #39), Security's key. Drafted before PR 2's first
# code commit, from the reads in milestones/M07/runs/pr2_reads.md and
# security-reviewer's report on M07 PR 1. It rules what the grant will be.
# It makes no grant: each is made by the human, by hand, at the step named.
# `authorises` lists the Security paths in the tree today that PR 2
# changes; the paths PR 2 adds are added to it in the commit that adds them.
ruling: pr2-security
seat: Security
authorises:
  - .github/workflows/platform-check.yml
  - .github/workflows/deploy.yml
  - .github/workflows/evals.yml
  - infra/workflows.sha256
  - infra/platform_identity.json
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - milestones/M07/open.md
  - milestones/M07/runs/pr2_reads.md
  - milestones/M07/runs/f7_0_dispatch_from_branch.json
  - milestones/M07/runs/platform_app_installation.json
  - milestones/M07/runs/platform_app_environment_after.json
  - milestones/M07/rulings/pr1-security.md
pr: 39
---

# Ruling: M07 PR 2, Security

DRAFT for andaro74 as Security. Not ruled until this line reads "Ruled by".

Each item is a recommendation with its alternative. Where the seat rules
the alternative, the item's text is changed before the line above is.
Nothing here has fired on a seeded case but item 1's dispatch.

## 1. The key's environment (R1; `open.md` row 20). Done, to confirm.

Read back: one deployment branch policy, `main`; the key an environment
secret only; **admin bypass switched off by Security on 2026-10-02**; the
platform check dispatched from `m07-pr1` and its `post` job **rejected by
the environment** (run 36963543726). This came before any grant, as row 2
asks.

- **Rule:** admin bypass stays off on every environment that holds an
  App's key. The permissions reader (item 6) fails if it reads `true`.

## 2. One App or three (Unsure A; security-reviewer 1, 2)

With one App, any job that holds its key can mint every permission the
App has. A split by workflow would be a convention in `main`'s code.

- **Recommended: three Apps, owned by `agentkeel-studio`**, each key in
  its own environment of `andaro74/agentkeel`, deployment branch `main`
  only, admin bypass off.

  | App | Environment | Permissions | Installed on | Used by |
  |---|---|---|---|---|
  | `agentkeel-platform` (5144253, exists) | `platform-app` (exists) | administration **write**; checks write; contents read; metadata read; pull requests read | `agentkeel-studio` | `platform-check.yml`'s `post` job |
  | `agentkeel-upgrades` (new) | `platform-upgrades` (new) | contents write; pull requests write; metadata read | `agentkeel-studio`, and `andaro74` with **only** `agentkeel` selected | `platform-upgrade.yml`, the retire job's pull request, `model-watch.yml` |
  | `agentkeel-observer` (new) | `platform-observer` (new) | checks read; pull requests read; contents read; metadata read; administration read | `agentkeel-studio` | the scheduled observer on `main` |

  The key that can post the check cannot push or open a pull request. The
  key that can open one cannot post the check, and holds no
  administration. The observer writes nothing.
- **5144253 is never installed on `andaro74`.** `main`'s required checks
  are names; an App there with checks write could answer to them.
- **`agentkeel-upgrades` on `andaro74/agentkeel`** (R3) can push a branch
  and open a pull request. It cannot merge to `main`: `main`'s ruleset
  requires the five checks and a pull request, with `bypass_actors: []`.
  It has no `workflows` permission, so it cannot push a change to
  `.github/workflows/`. A pull request it opens starts `evals.yml`, which
  one opened with `GITHUB_TOKEN` would not.
- **Alternative: one App**, with all of the above on 5144253. One key,
  one environment, less to set up. Then SPEC/07 §6 and §8 say the split
  binds nothing, the App is installed on `andaro74/agentkeel` with
  administration write, and security-reviewer's finding 2 stands as a
  named gap. Not recommended.

## 3. Which repositories the installation reaches (Unsure C; security-reviewer 6)

Today: `repository_selection: all`.

- **Recommended: stay on `all`** for the three Apps on `agentkeel-studio`.
  The organisation exists to hold agent repositories, member repository
  creation is off, and the owner creates each one. With `selected`, every
  new agent repository would wait for the owner to add it to three
  installations, inside the timed run's clock, and the platform check
  would post nothing until then.
- **What `all` costs, stated:** Administration: write reaches every
  repository the organisation ever holds, `agent-template` included. The
  permissions reader records `repository_selection` and the organisation's
  repository list at each run, so a repository nobody expected shows.
- **Alternative: `selected`**, each repository added by hand and named in
  a ruling. Tighter; adds a step to the quickstart that only the owner
  can do.

## 4. Which jobs can mint, and never beside agent or pull-request code (row 2; security-reviewer 4)

- Each key is read by exactly one job per workflow, in its environment.
  That job checks out `main` only, runs `agentkeel`'s code only, and
  takes the earlier job's output as an artifact of data.
- `platform-check.yml`: `find` and `evaluate` hold no secret (as today);
  `post` holds `platform-app`'s.
- `platform-upgrade.yml` and the retire job: a first job with no secret
  reads the registry and the agent repository as data and writes the
  diff; a second, in `platform-upgrades`, opens the pull request from it.
- `model-watch.yml`: a first job as the eval role reads Bedrock and
  writes the proposed pin; a second, in `platform-upgrades`, opens the
  pull request.
- The observer: one job in `platform-observer`, `main`'s code.
- No key is in `evals.yml`, which checks out pull-request code.

## 5. `app_token()` (row 2; security-reviewer 7, 20)

- It takes an App id, a key, **a repository and a named permission set**,
  and raises before any request if either is missing or empty. The call
  with no repository (`scope = {}`) is gone.
- `post` mints twice: once with `administration: write` to read the
  rulesets, dropped after the read; once with `checks: write` to post.
- Named sets live in one table in `scripts/platform_check.py`; a set not
  in the table cannot be minted.

## 6. The reader of the grant (row 2; security-reviewer 11, 18, 19, 21)

- `scripts/platform_check.py grant` reads, for each App: the App's
  registered permissions; the installation's permissions,
  `repository_selection` and, with a metadata-only token, its repository
  list; and, for its environment, the branch policies with their type,
  `can_admins_bypass`, and the names of the environment's and the
  repository's secrets. It **writes what it read** as an artifact and
  exits 1 on any value the `grant:` block below does not name.
- It runs first in each keyed job. A failure stops the job before any
  token with write is minted.
- The block is read from this file **on `main`**, so a pull request
  cannot widen the grant it is checked against.
- S0's fixtures and `grant_errors` take one grant per App; PR 2 changes
  the fixtures' shape in its first commit, before the reader, and says so
  (`feasibility.md` §4).

```yaml
grant:
  agentkeel-platform:
    app_id: 5144253
    environment: platform-app
    installed_on: [agentkeel-studio]
    repository_selection: all
    permissions: {administration: write, checks: write, contents: read, metadata: read, pull_requests: read}
  agentkeel-upgrades:
    app_id: null            # filled when the App exists, in a pushed commit, before any attempt
    environment: platform-upgrades
    installed_on: [agentkeel-studio, andaro74]
    repository_selection: {agentkeel-studio: all, andaro74: [agentkeel]}
    permissions: {contents: write, pull_requests: write, metadata: read}
  agentkeel-observer:
    app_id: null
    environment: platform-observer
    installed_on: [agentkeel-studio]
    repository_selection: all
    permissions: {administration: read, checks: read, contents: read, metadata: read, pull_requests: read}
  environments:
    branch_policies: [{name: main, type: branch}]
    can_admins_bypass: false
    secrets: one each, the App's key, and not a repository secret
```

## 7. Whether a read path without write exists (row 2)

Not found. M06 showed Administration: read does not return
`bypass_actors`. GitHub's documentation, as read at M06, says the field
is shown to callers who can administer the ruleset. **Recommended:** rule
that write is needed, and bound it by items 2 to 6. If a narrower
permission is later documented, it replaces write by a new ruling.

## 8. The seeded relaxation (Unsure D; security-reviewer 14)

- **Recommended: made once, from `main`**, by a dispatch input on
  `platform-check.yml` (`relax_seed: owner-check`) that only its `post`
  job reads: one call asking GitHub to remove the required check from
  ruleset 24310403, with the token `post` mints for that repository. The
  key never leaves its environment. The input is checked against the
  agent name pattern and passed through `env:`, never interpolated.
- After owner-check has merged, deployed and taken S1; before it is
  retired. A new head is pushed while the ruleset is changed. The owner
  restores it with the owner's own token and reads it back equal to the
  export.
- I expect GitHub to accept the call, so the reading will be detection,
  not refusal, and is recorded as that.
- **Alternative: not made.** F7.0's reading then says the attempt was not
  made, and "the App's token relaxing a ruleset" stays a control with no
  seeded case (SPEC/07 §8).

## 9. The observer on `main` (Unsure E; R4; security-reviewer 9)

- **Recommended:** a scheduled workflow, `observe.yml`, on `main`, in
  `platform-observer`. It reads the run files as they are on `main` and
  puts its raw observation under `observations/<run id>.json` in the
  audit bucket, through a role that trusts `observe.yml` on
  `refs/heads/main` only, put once. A pull request's `evals` run reads
  the latest object through the existing read role and hands it to
  `build`, which records the run id, the time and "viewpoint: App". The
  prefix and the role's trust are a change to `infra/security/` and
  `infra/bootstrap/`, deployed by hand after reading `cdk diff`: **a
  grant**, made with item 12's.
- Row 7's cell cites PR 4's run's envelope, which names the observation
  it carries.

## 10. `model-watch`'s token (R3)

`agentkeel-upgrades`, item 2. Its drafted ruling file says "Drafted" and
never carries a line that starts "Ruled by" (security-reviewer 8).

## 11. Retirement (Unsure H; R7; security-reviewer 10, 15; legal-compliance 9, 10)

From the reads: the deploy role cannot delete a stack and no platform
role may schedule a key's deletion.

- **Recommended: a retirement is a stack update, not a deletion.** The
  retire job deploys `agentkeel-<name>` from a template without the
  runtime. The stack's execution role already may
  `DeleteAgentRuntime` on `runtime/agentkeel_*`. **No new IAM.**
  refagent's stack is out of reach by name: the retire job refuses
  `refagent`, and refagent's repository is not an agent repository.
- **What stays, by design:** the key, its alias, the rights table (all
  retained by the construct), the runtime's log group, the registry row
  with `retired_at`, and the audit bucket's records. The key is not
  deleted; no kept record is encrypted with it.
- **`bundles/`:** one statement in the audit bucket's policy for the
  answer-put role, under `bundles/<name>/*`, put once. A change to
  `infra/security/`, deployed by hand: **a grant**.
- **The retirement is also written to the audit bucket**, as
  `envelopes/agents/<name>/retired.json`, put once, since the registry
  row is in the agent account and is not write-once.
- The `retire=<name>` input is checked against the name pattern and
  passed through `env:`.

## 12. What the human does, in order. Each is a grant or a setting.

Nothing below is done before this file reads "Ruled by".

1. **Before PR 2's code:** nothing more. Item 1 is done.
2. **During PR 2, before its merge** (so the reader can be tested against
   real ids): create `agentkeel-upgrades` and `agentkeel-observer` in the
   organisation with item 2's permissions; create environments
   `platform-upgrades` and `platform-observer`, branch `main` only, admin
   bypass off; store each key as its environment's secret. Install them
   as item 2 says. Neither new App holds administration or checks write.
3. **During PR 2:** read `cdk diff` for `infra/security/` (the `bundles/`
   and `observations/` statements) and `infra/bootstrap/` (the observer's
   put role), then deploy both by hand.
4. **After PR 2 merges, and only then:** raise `agentkeel-platform`'s
   Administration to write in the App's settings, and accept the new
   permission on the organisation's installation. `main` no longer mints
   a token with no repository at that point.
5. **Before 2026-10-31:** renew the Grafana observer token (Unsure J).

## What a reader can run

```
gh api repos/andaro74/agentkeel/actions/runs/36963543726/jobs --jq '.jobs[]|[.name,.conclusion]'
gh api repos/andaro74/agentkeel/environments/platform-app --jq '.can_admins_bypass'      # false
gh api orgs/agentkeel-studio/installations --jq '.installations[]|[.app_slug,.repository_selection,.permissions]'
grep -n "DeleteStack" infra/bootstrap/app.py                                             # nothing
grep -n "RemovalPolicy.RETAIN" infra/construct/governed_agent.py                         # the table, the key, its alias
```
