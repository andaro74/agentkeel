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
  - .github/workflows/platform-upgrade.yml
  - .github/workflows/model-watch.yml
  - .github/workflows/observe.yml
  - infra/workflows.sha256
  - infra/platform_identity.json
  - infra/construct/**
  - infra/security/**
  - infra/bootstrap/**
  - infra/grafana/**
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

## Made on 2026-10-02, before any PR 2 code

andaro74, as Security, ruled every item of this file as its recommended
option on 2026-10-02 ("as proposed"), before PR 2's first code commit
(`16d9f84` is the last commit before it). Recorded here by the session.
The line above stays a draft until the seat changes it at the end of the
PR, as in PR 1. No alternative was taken, so no item's text changes.

| Item | As ruled, 2026-10-02 |
|---|---|
| 1 | Admin bypass stays off on every environment that holds an App's key; the reader fails on `true` |
| 2 | Three Apps: `agentkeel-platform` (5144253, the check), `agentkeel-upgrades` (opens pull requests), `agentkeel-observer` (reads only). Each key in its own environment limited to `main`, admin bypass off. 5144253 is never installed on `andaro74` |
| 3 | The organisation's installations stay on "all repositories" |
| 4 | One keyed job per workflow, `main`'s code only, the earlier job's output taken as data; no key in `evals.yml` |
| 5 | `app_token()` takes a repository and a named permission set and refuses a call without either; `post` mints twice |
| 6 | The reader of the grant, run first in each keyed job, against the `grant:` block read from this file on `main` |
| 7 | Administration: write is needed to read `bypass_actors`; bounded by items 2 to 6 |
| 8 | The seeded relaxation is made once, from `main`, through a dispatch input on `platform-check.yml`'s `post` job |
| 9 | The observer on `main` stores its observation under `observations/` in the audit bucket, through a role that trusts `main` only |
| 10 | `model-watch` opens pull requests as `agentkeel-upgrades`; its drafted ruling never carries a line that starts "Ruled by" |
| 11 | A retirement is a stack update that removes the runtime, with no new IAM; it is also written to the audit bucket; `bundles/` gets its one statement |
| 12 | The order of the human's steps, as written. Nothing is granted to `agentkeel-platform` until PR 2 has merged |

Items added after this ruling are marked "not ruled on 2026-10-02" where
they stand, and wait for the seat.

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
    public: true            # item 13a, not ruled on 2026-10-02: installed on two accounts, so GitHub makes it public
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

Nothing below is done before this file reads "Ruled by". The exact steps
and commands for 2 and 3 are `milestones/M07/runs/pr2_by_hand.md`.

1. **Before PR 2's code:** nothing more. Item 1 is done.
2. **During PR 2, before its merge** (so the reader can be tested against
   real ids): create `agentkeel-upgrades` and `agentkeel-observer` in the
   organisation with item 2's permissions; create environments
   `platform-upgrades` and `platform-observer`, branch `main` only, admin
   bypass off; store each key as its environment's secret. Install them
   as item 2 says. Neither new App holds administration or checks write.
3. **During PR 2:** read `cdk diff` for `infra/security/` (the `bundles/`
   and `observations/` statements and the observer's put role, which is
   in the security account, where the bucket's other put roles are) and
   for `infra/bootstrap/` and `infra/grafana/` (item 13b to 13d, if the
   seat rules them), then deploy by hand.
4. **After PR 2 merges, and only then:** raise `agentkeel-platform`'s
   Administration to write in the App's settings, and accept the new
   permission on the organisation's installation. `main` no longer mints
   a token with no repository at that point.
5. **Before 2026-10-31:** renew the Grafana observer token (Unsure J).

## 13. Not ruled on 2026-10-02: found while building, put to the seat

The ruling of 2026-10-02 covers items 1 to 12 as they stood at `16d9f84`.
Each item below was met while building PR 2. Each is built as its
recommended option, so that the diff shows it, and **none is deployed,
granted or set**: every one that is a permission waits for the seat. If
the seat rules an alternative, the code changes before this file's first
line does.

**13a. `agentkeel-upgrades` has to be public.** A GitHub App that is "only
on this account" can be installed on its owner alone. Item 2 installs
`agentkeel-upgrades` on the organisation and on `andaro74`, so it must be
"any account". Anybody can then install it on an account of their own.
That gives the platform's key reach into their repositories and gives
them nothing here: `app_token()` mints only for a repository whose owner
the caller names, and the callers name the organisation and `andaro74`.

- **Recommended:** the grant block says `public: true` for that App; the
  reader records an installation on an unnamed account (`not_ours`) and
  does not fail on it. Otherwise a stranger could stop every keyed job by
  installing the App. `agentkeel-platform` and `agentkeel-observer` stay
  "only on this account", and an installation of either on any other
  account is still refused by the reader.
- **Alternative:** a second App owned by `andaro74`, installed there
  only, with its own key and environment, for `model-watch`. Four Apps;
  none public.

**13b. `model-watch` reads Bedrock as a role of its own, not as the eval
role.** Item 4 says "a first job as the eval role". The eval role trusts
`evals.yml` only, may invoke models, and is trusted for a pull request's
run; the read needs none of that.

- **Recommended:** `agentkeel-model-watch` (`infra/bootstrap/`): trusted
  for `model-watch.yml` on `main` only; one action,
  `bedrock:GetFoundationModel`, on `foundation-model/*`. A new role with
  one read-only permission: **a grant**.
- **Alternative:** widen the eval role's trust to `model-watch.yml` and
  add the action to it. One role fewer; a role that can invoke models
  then runs in a second workflow.

**13c. The eval role reads a template agent's runtime, not only
refagent's.** F7.2 and F7.3 are read by a pull request's run: is the
retired runtime gone, and which bytes does a runtime run after a revert.
Today the eval role may read refagent's alone.

- **Recommended:** three read-only statements (`infra/bootstrap/`):
  `cloudformation:DescribeStacks` on `stack/agentkeel-*/*`,
  `bedrock-agentcore:GetAgentRuntime` on `runtime/agentkeel_*`,
  `ecr:DescribeImages` on `repository/agentkeel/*`. No invoke of a
  template agent. **A grant**: a read widened.
- **Alternative:** not granted. Then F7.2's runtime read and F7.3's on
  the fallback are unread, and row 7 is RED on them at the close.

**13d. Where panel 2 reads envelopes (SPEC/07 §11, R8).** Not among the
drafts ruled. An envelope file is printed over many lines, which Athena's
JSON reader cannot take, so reading `envelopes/` in the audit bucket
directly would need a second copy written in another form.

- **Recommended:** a copy in the agent account, as R8's second option: a
  DynamoDB table `agentkeel-envelopes` (commit, verdict, mode), read by
  panel 2 through the connector, catalog, workgroup and data source panel
  1 already uses; one row per envelope, written once by `evals.yml`'s
  `archive` job on a push to `main`, as a new role
  `agentkeel-envelope-row-put` trusted for that workflow on `main` only
  (`Scan`, `PutItem` on that table). The connector's role gains read on
  that table and its Glue schema. The workspace's role does not change,
  and no new data source is made by hand. **Grants**: one table, one
  role, two statements on the connector's role. The table is a copy for
  a surface: `build.panel_verdict_mismatch` holds its rows to the
  envelopes, and that comparison is F7.4.
- **Alternative:** no source at M07. `validate`'s check and build's
  comparison stay (S4's readers); panel 2's live read is unread and row 7
  is RED on F7.4 at the close.

**13e. The read role lists `bundles/`.** Item 11 gives `bundles/` its
put. For F7.2 the observer must see that a retired agent's bundle is
there. **Recommended:** list only, no read of a bundle's bytes
(`infra/security/`, with item 9's `observations/` read). **A grant.**

**13f. What the reader of the grant does not read, and how it reads.**

- The names of an environment's secrets, and the repository's: no token
  a job holds may list them. **Recommended:** read by hand by an admin
  (`gh api repos/andaro74/agentkeel/environments/<name>/secrets`) and
  recorded under `milestones/M07/runs/`; the artifact says they were not
  read. The alternative is a token with secrets read in each keyed job,
  which is a wider grant than the gap.
- A value narrower than the grant is not an error. Before step 12.4 the
  installation holds Administration: read; the reader passes, the
  `rulesets` mint is refused by GitHub (422), and every head is refused
  for a ruleset that could not be read. **Recommended**, since the other
  reading stops `post` posting anything until the grant is made.

**13g. Smaller choices, each Security's or Engineering's.**

- `platform-upgrade.yml` lists agents from GitHub (the heads the App
  passed), not from the registry, so it holds no AWS credentials. An
  agent the App passed and the deploy has not yet reached can get its
  upgrade a deploy early.
- The seeded relaxation can be pointed at one repository only, the one
  seed S0's run file names on `main`. It is a tool for one attempt.
- A retirement's idle trigger (a registry row with no answer for 90
  days) is not built: nothing writes `idle_since`. The dispatch and a pin
  30 days from its date are built.
- refagent's own deploy does not put its bundle under `bundles/`: its
  two jobs are unchanged, and it is never retired.
- A pull request the platform opens is opened once per branch name,
  ever. A closed draft is a seat's answer.

**13h to 13n. Found by the seat reviews of `a2c5a61...1b376a3`, and not
ruled.** Each is left as the code stands, named in SPEC/07 §12, and is
the seat's to rule before the attempt it bears on.

- **13h. The two new roles and the agent key policies** (platform-architect
  F2). `agentkeel-model-watch` and `agentkeel-envelope-row-put` are not
  in `PLATFORM_ROLES` (the construct) or in refagent's key policy list
  (the bootstrap). The deploy boundary and no kms Allow hold R4 for
  them. **Recommended:** add both to both lists in PR 3, before
  owner-check's first deploy: no template agent's key exists yet, and
  after one does the execution role cannot change its policy.
  Alternative: leave the lists, as SPEC/07 §12 now says.
- **13i. A retirement's head is not held to the deployed manifest**
  (platform-architect F4; security-reviewer 17). **Recommended:** in PR
  3, the retire job compares the retired head's manifest with the one at
  the registry row's commit and refuses any move but `rollout`. The cost:
  a head that failed to deploy before it was retired cannot be retired
  until it is fixed. Alternative: the gap stays named in SPEC/07 §12.
- **13j. The grant block and the reader are not on Security's paths**
  (security-reviewer 5). **Recommended:** in PR 3 the block moves to
  `infra/platform_grant.yaml`, and `.github/CODEOWNERS` gives
  `scripts/platform_check.py` to Security. Alternative: named in §12.
- **13k. What the `agentkeel-upgrades` key reaches on
  `andaro74/agentkeel`** (security-reviewer 7): any branch but `main`,
  and a pull request it opens runs `evals.yml` with that workflow's roles
  and tokens. **Recommended:** accepted, and said in §12: it is what any
  collaborator with write has. Alternative: 13a's fourth App.
- **13l. The bytes a platform upgrade proposes** (security-reviewer 4;
  cold review N7). The titles, bodies and drafted rulings are now the
  keyed job's own. The content of `server.py` and `__init__.py` is still
  the plan's, from the template repository's default branch.
  **Recommended:** in PR 3 the `open` job fetches the template as data at
  the commit the plan names and requires each proposed file to equal it,
  and `guardrail` to equal `main`'s. Before S1.
- **13m. `retired.json` is under `envelopes/`** (cold review F15), keyed
  one per name (security-reviewer 8), and `agentkeel-answer-put` may put
  under `bundles/*`, not `bundles/<name>/*` (security-reviewer 15).
  **Recommended:** it stays where item 11 put it: it is the retire job's
  record, not an envelope, it carries no verdict and the gate never
  reads it; one per name fits a name retired once. `bundles/<name>/*`
  cannot be said in a role's policy for names not yet known; left, and
  named. Alternative: a prefix of its own, which is a grant.
- **13n. The seeded relaxation after it is made** (security-reviewer 6).
  It is now refused once the run file on `main` records it.
  **Recommended:** PR 3 also removes the dispatch input and the step,
  once the attempt is recorded.

## 14. The seat reviews, and what was done

Read on the diff `a2c5a61...1b376a3` (98 files), before the pull request
was opened. Both reports are in the pull request's body, verbatim.
Repairs are `b3196d6` (scripts and workflows) and `ccb2be8` (readers);
the documents are the commit after them.

**security-reviewer: BLOCK 1, FINDING 7, NOTE 12.**

| # | Finding | Status |
|---|---|---|
| 1 BLOCK | `read_grant` minted a metadata token on every installation, a stranger's included, and three places said it did not; a stranger's suspended installation stopped every keyed job | **Repaired** (`b3196d6`): it mints only on an account the grant names; any other is recorded from the App's own listing; a stranger's suspension stops nothing. Tested through `check_grant`, live and suspended |
| 2 | The installation list was read one page deep | **Repaired**: every page |
| 3 | The environment was compared only inside a named installation's pass | **Repaired**: once, in `check_grant`. Still true: the "key was read in environment X" check cannot fire live, since the name read is the grant's own |
| 4 | The keyed jobs re-check a plan's shape, not its content | **Part repaired**: titles, bodies and the drafted ruling are the keyed job's own. The files' bytes are not: item 13l, PR 3, before S1 |
| 5 | The grant block, the seed's repository and the reader are on Product's and Engineering's paths | **Open**: item 13j. Named in SPEC/07 §12 |
| 6 | "Made once" was a sentence | **Repaired**: refused once the run file on `main` records it. Item 13n for the rest |
| 7 | What the `agentkeel-upgrades` key reaches on `andaro74/agentkeel` | **Open**: item 13k. Named in §12 |
| 8 | A retirement's records did not survive a second deploy; the first reading was the only one kept | **Repaired**: `claim` and `write` refuse a retired name; nothing is recorded unless the runtime is gone, so the record put once is never of a runtime that answered. One record per name stays: item 13m |
| 9 to 22 | Notes | 9: the repository name is now held to a character set before any request. 10: `check`, `open` and `observe` tokens are still not revoked; they never leave the process; kept. 12: the observer has no keyless half, and `artifact_json` sends its bearer token on a redirect; PR 3, before the first keyed observer run. 14: the row-put role's docstring and `surfaces.md` now say the once-only is the script's condition. 15: item 13m. 20: `pr2_by_hand.md` A3's words corrected; the by-hand read of the secrets' names is recorded when it is made. 21: within one App the two-token split is `main`'s code; stands as said. The rest need nothing |

**platform-architect: BLOCK 1, FINDING 5, NOTE 9.**

| # | Finding | Status |
|---|---|---|
| B1 | The retire job wrote `retired_at` and `retired.json` whatever the invocation returned | **Repaired** (`b3196d6`): `invoke` exits 5 unless the error is `ResourceNotFoundException`; `record` refuses any other invocation; the step fails, nothing is put, the row stays open and the next run asks again |
| F1 | "No new IAM" rested on one action name | **Read** (2026-10-02, `pr2_reads.md` R7): the type's delete handler names five actions and the execution role holds all five; a test asserts them. What the service calls beyond the type's list is unread until S2 |
| F2 | The two new roles are in neither key policy's list | **Open**: item 13h |
| F3 | `f7_2_removed_and_kept.md`: four corrections | **Repaired**, all four, and the one-way section restated |
| F4 | A retirement is a stack update from an unsigned head | **Open**: item 13i |
| F5 | Controls with no seeded case that §12 did not name | **Repaired** in SPEC/07 §12; the construct's refusal of a retired refagent has a test; the row-put role's docstring is reworded |
| N1 to N9 | Notes | N4 (the table's stack) is 13d's to rule. N8 reworded in `deploy.yml`. N9: the construct test still compares resource types, not properties; kept, said here. The five deferred items are landing-zone work (SPEC/00 §2, §12) |

## What a reader can run

```
uv run pytest -q tests/test_m07_readers.py -k "stranger or page or made_once or environment_is_compared"
uv run pytest -q tests/test_m07_platform.py -k "gone or retired_name or keyed_jobs_own or refagent"
uv run pytest -q tests/test_m07_workflows.py -k "shared_reader or retirement"
aws cloudformation describe-type --type RESOURCE --type-name AWS::BedrockAgentCore::Runtime --region us-west-2 --query Schema --output text | python -c "import json,sys;print(json.load(sys.stdin)['handlers']['delete']['permissions'])"
gh api repos/andaro74/agentkeel/check-runs/110702392789/annotations --jq '.[].message'
gh api repos/andaro74/agentkeel/actions/runs/36963543726/jobs --jq '.jobs[]|[.name,.conclusion]'
gh api repos/andaro74/agentkeel/environments/platform-app --jq '.can_admins_bypass'      # false
gh api orgs/agentkeel-studio/installations --jq '.installations[]|[.app_slug,.repository_selection,.permissions]'
grep -n "DeleteStack" infra/bootstrap/app.py                                             # nothing
grep -n "RemovalPolicy.RETAIN" infra/construct/governed_agent.py                         # the table, the key, its alias
```
