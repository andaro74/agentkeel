# SPEC/07 — Upgrade, retire, surfaces

Status: DRAFT · Owner: Product seat · Milestone M07 · Opened at M07 PR 1
(`milestones/M07/rulings/pr1.md`) · Build list: SPEC/00 §8 M07, which is
the ruling for this milestone's build paths (`SPEC/00-overview.md#8-M07`),
as cut in §9 and as amended at this PR (§10) · Reviewed by
`product-spec-reviewer` before the rest of PR 1 was written, but for
M06's video and one read (3 BLOCK, 26 FINDING, 12 NOTE on `83eb558`;
`milestones/M07/feasibility.md` §1) and revised once on the rulings in §2
of that note, all made by the human on 2026-10-01, "as proposed". §12,
added at M07 PR 2, says how §11's reads were ruled on 2026-10-02 and
where the build differs from §6's words.

## 1. The claim

**Claim 7.** An agent takes a platform, model or retirement upgrade
without a workflow edit.

For a director: *a new platform version, a new model, or a retirement
arrives as a PR; the team never edits the pipeline* (SPEC/00 §10.3 row
07).

Threats answered (SPEC/00 §3): model regression or deprecation (M04
showed a swap is tested on its own pull request; M07 shows the platform
opens that pull request once the Threshold Owner has named a candidate,
and that a merged swap can be put back); the negligent developer (never
upgrades; leaves a retired agent answering); the insider on the platform
team (an upgrade arrives as a pull request the agent's seats can read,
not as an edit nobody saw).

**The precondition, stated first.** An upgrade needs an agent made from
the template to upgrade. At M06's close no such agent exists: the
platform's App refused every head of every agent repository (row 6 RED,
`milestones/M07/open.md` row 2). So **M07 carries the template's repair
as its first seeded case (S0, §5), and M06's timed quickstart (S3 of
SPEC/06) is received here and read by this milestone's run**. The agents
that take the upgrades are the owner's test agent (`owner-check`) and
the agent the second developer makes in the timed run; refagent takes
the model swap and its rollback. Nothing below is measured until S0 is
read as held.

**"Takes an upgrade" means all four of these, and nothing less.** Each is
read from a record; none is taken on anyone's word.

1. **Arrives as a pull request.** The upgrade is a pull request the
   platform opened, as the platform's App, in the repository it changes:
   a draft, carrying the change and nothing else. No person wrote it.
2. **Gated as any change.** It merges only when the checks that gate every
   change in that repository are green: the platform check in an agent
   repository, the gates in `agentkeel`. Nothing is skipped for it.
3. **No workflow edit, and no person's edit.** No file under
   `.github/workflows/` is touched by it or added for it, in the agent
   repository (the template ships none) or in `agentkeel`
   (`infra/workflows.sha256` is unchanged across it); and no commit by a
   person was needed on it to make it green. **A ruling file under
   `milestones/*/rulings/` is not a person's edit** (BLOCK 2): a seat
   ruling a change is the gate working, as it does for every change in
   `agentkeel`.
4. **Live.** After the merge the deployed runtime runs the bytes the tree
   now gives (`scripts/runtime_for_tree.py`'s match, read for that agent);
   for a retirement the runtime is gone and the registry row says so; for
   a rollback the digest before the swap is live again.

**Three kinds**, one seeded case each (§5):

- **Platform.** The template is re-made from a later `agentkeel` commit
  (§2). Every agent whose `platform_version` is behind gets a draft pull
  request from the platform with the platform-owned files at the new
  version. **Major** when the platform check at the new version refuses
  the agent's default-branch head as it stands (its guardrail pin, image
  files or manifest no longer pass), **minor** otherwise; the check at the
  new version says which, and the pull request records it. Which S1 will
  be is not stated: it is read.
- **Model.** `model-watch` (SPEC/04 §9 cut a) polls Bedrock, writes
  `deprecated_after` from `modelLifecycle.endOfLifeTime`, and opens a
  draft pull request moving a pin to the candidate the Threshold Owner
  has named. A person names the candidate; the platform opens the pull
  request. Its shadow run is the pull request's own `evals` run, which
  M04's gate rules (F4.1, F4.2, F4.4). A merged swap that is then
  reverted must put the previous digest live (F7.3).
- **Retirement** (BLOCK 1). The platform opens a draft pull request in
  the agent's repository that sets the manifest's `rollout` to `retired`.
  It opens when the registry row is flagged idle (no answer record for
  90 days), when the pin's `deprecated_after` is within 30 days with no
  swap open, or when the owner dispatches the retire workflow for that
  agent, which is the seeded trigger. The agent's seats merge it. The
  platform's deploy path, finding `rollout: retired` at a head the App
  passed, retires instead of deploying: it removes the runtime and writes
  `retired_at` on the registry row, which stays. Archiving the repository
  is the owner's last step, not the trigger.

**The measured value for claim 7** is `upgrade.taken`: how many of the
three seeded upgrades arrived as a pull request the platform opened and
went live with no workflow edit and no person's edit, **n of 3**, with
each one's elapsed time from the platform's record of the trigger to the
record of it live (§2), every time GitHub's or AWS's. Row 7 is GREEN only
at 3 of 3 with every F7 held.

**Claim 6's later reading.** SPEC/06's F6.1 live half and F6.3 are read
by `template` on M07's envelopes when the timed run is made, and quoted
in row 7's cell as claim 6's later reading. Row 6's cell stays on
`245eb9b` and row 6 stays RED; `milestones/M06/README.md` gains the
reading as a dated note. A quickstart over its bar does not fire F7.0
(item 14): the agent it made exists and can be upgraded.

## 2. Words used here

- **The platform's version.** The `agentkeel` commit the template was
  last made from (`scripts/make_template.py` prints it), written in the
  template manifest's `platform_version`. At M06's close the template
  (`agentkeel-studio/agent-template`, `a4c3788`) was made from `39031e7`
  and its manifest says `m06`, a literal. From M07 PR 2
  `make_template.py` writes the tag when `HEAD` carries one and the short
  commit otherwise, and the manifest schema's pattern (`^m[0-9]{2}$`
  today) takes both. **Behind** is ancestry in `agentkeel`: an agent's
  version is behind when the commit it names is an ancestor of the
  template's and not equal to it (item 5). The template is re-made after
  an `agentkeel` merge that changes a platform-owned file; at M07 the
  owner pushes it by hand, as at M06 (§11, R5).
- **Platform-owned files** in an agent repository: `manifest.yaml`'s
  `platform_version` and `guardrail` (the pin every agent from the
  template carries, `src/validate/agent.py`), `server.py`'s import shim
  and `__init__.py`. Everything else in the repository is the agent's own
  after creation (`agent.py`, `prompt.txt`, `tools/`, `data/`, `goldens/`,
  the other manifest fields). A platform upgrade pull request touches
  platform-owned files only. A retirement pull request touches
  `manifest.yaml`'s `rollout` only.
- **A workflow edit.** A change to any file under `.github/workflows/`,
  in `agentkeel` or in an agent repository, made to take an upgrade. An
  agent repository has none to edit (SPEC/06 §2: the template ships no
  workflow). In `agentkeel`, `infra/workflows.sha256` is the record: if
  it changes between the trigger and the merge of an upgrade, the upgrade
  needed one.
- **A person's edit.** A commit on an upgrade pull request whose author
  is not the platform's App and which touches any path but a ruling file
  under `milestones/*/rulings/`; or a commit on the default branch
  between the pull request's opening and its merge that touches the same
  files. GitHub's record of each commit's author and paths is what is
  read. Agent repositories ask for no ruling (SPEC/06 §8), so there any
  person's commit on an upgrade pull request is an edit.
  **Amended at M07 PR 3 (Product, `rulings/pr3.md`), before any swap pull
  request exists.** On a pull request in `agentkeel`, and in no agent
  repository, CI's own envelope commit is not a person's edit, and its
  files are not paths the upgrade changes. It is that commit only when
  GitHub records all of these: its author and its committer are both
  `github-actions[bot]`; every file it touches is
  `evals/history/<commit>.json`, `<commit>.baseline-card.json` or
  `<commit>.baseline-raw.json`; and `<commit>` is the full id of another
  commit of the same pull request. A commit by that login that touches
  one path more, or names a commit the pull request does not hold, is a
  person's edit as before. What this rests on: GitHub does not sign that
  commit (`evals.yml` pushes it with the job's token), so the login is a
  name a person's commit can carry; the paths are what bound it. A
  hand-made file under `evals/history/` is `two-key`'s to refuse
  (SPEC/02 §2), not F7.1's.
- **The trigger** and **live**, per kind, every time GitHub's or AWS's,
  none a runner's clock or a pusher's (item 9):

  | Kind | Trigger (the record) | Live (the record) |
  |---|---|---|
  | platform | GitHub's push record of the template repository's commit that moved `platform_version` (the push event's time, not the commit's `committer.date`) | the deploy run that deployed the merged upgrade, completed (GitHub's `completed_at`); `runtime_for_tree`'s match for that agent |
  | model | `model-watch`'s run that opened the pull request (GitHub's run `created_at`) | the deploy run of the merge, completed; for the rollback, the deploy run of the revert's merge, completed, with the runtime's image digest equal to the tree's at the revert |
  | retirement | the retire workflow's run that opened the pull request (GitHub's run `created_at`) | `DeleteAgentRuntime` in CloudTrail (`eventTime`), after the pull request's `merged_at` |

- **The limits** (item 15). Three, each a bar in `thresholds.yaml` under
  `upgrade:` from PR 2, `relaxes: up`, added before any attempt (adding a
  bar is not a relaxation, ADR-0009): `arrive_max_seconds` 4,500 (the
  pull request's `created_at` after the trigger; `platform-upgrade.yml`
  and the retire job run every 15 minutes, `*/15 * * * *`, so one period
  plus an hour); `deploy_max_seconds` 3,600 (the deploy run completed
  after a merge); `retire_max_seconds` 3,600 (`DeleteAgentRuntime` after
  the retirement pull request's merge). A miss is a finding, not a bar to
  move.
- **The digest.** The sha256 of the packed bundle archive, which
  `deploy.yml` tags the image with (`src/bundle/pack.py`;
  `scripts/runtime_for_tree.py` steps 1 to 4). "The new digest live"
  (F7.3) means `GetAgentRuntime` names an image whose tags hold the
  swap's digest after the revert's deploy completed.
- **A rollback.** A pull request that reverts a merged upgrade, merged
  and redeployed by `deploy.yml`. SPEC/00 §12 calls rollback "manual
  re-point to the previous digest"; M07 measures the revert, and no
  re-point by hand is made or read.
- **Retired.** `DeleteAgentRuntime` is in CloudTrail for the agent's
  runtime; `GetAgentRuntime` on its ARN returns
  `ResourceNotFoundException`; **one invocation of that ARN by the retire
  job, after the deletion, is refused the same way** (item 4), recorded
  raw; the registry row carries `retired_at`; the signed bundle archive
  is under `bundles/<name>/<commit>.tar` in the audit bucket, put there
  **at deploy time** (item 17: the Actions artifact expires after 30
  days), write-once (R5). **How long** (legal-compliance 8, 9): the audit
  bucket's lock is one day (R5 as amended at M05; seven years is M08's
  F8.4), so a bundle and an answer record are locked for a day and after
  that kept only by the security account's policies. M07 changes no
  retention. The registry row is in the agent account's table and is not
  write-once. "Still answers" (F7.2) means that invocation
  answered, or the runtime still exists `retire_max_seconds` after the
  merge, or an answer record for the agent under
  `envelopes/agents/<name>/` has `LastModified` after the deletion.
- **Panel 2.** The verdict history panel (SPEC/06 §9 cut 1, received
  here): one row per envelope, with its commit and its verdict as
  stored, read by Grafana through Athena (§11, R8). Its query names that
  source and returns the verdict column as stored; a query that computes
  a verdict is refused (S4's reader). **A GREEN on panel 2 is the run's
  own verdict, not a row's**: the envelope for `245eb9b` stores GREEN and
  row 6 is RED, by the ledger's reading of `template`.
  `docs/platform/surfaces.md` says so (item 25).
- **The surfaces.** Grafana panels 1 and 2. Panels 3 and 4 are §9's cut
  d. A surface's **plant** is a seeded case, listed by the surfaces'
  control in `src/verdict/plants.py`, that the surface's reader must
  refuse. The control names **two**: S4 of SPEC/06 (panel 1) and S4 here
  (panel 2). `plants_expected` and `plants_fired` for the surfaces are
  counted from those readers' results in the run, as M03's plant rule
  counts golden plants (F7.5). S5 is the test of the counter and is not
  counted (item 21).
- **The owner's test** (SPEC/06 §2 "the template works";
  `milestones/M06/runs/f6_0_owner_test.yaml`, steps 2 to 4): the owner's
  own agent repository, `agentkeel-studio/owner-check`, created
  2026-10-01T13:05:37Z, whose pull request 1 (head `0c596c1`) was refused
  at M06 on the seats, the goldens and the hidden `bypass_actors`. At M07
  it is read by CI, not by hand (S0, §5): a new head on pull request 1
  with the template's content is refused on the seats and the goldens and
  nothing else; the fixed head passes, merges, deploys, answers, and is
  listed. Pull requests 1 and 2 are left as M06 left them until the step
  that needs each.
- **The viewpoint.** Who asked GitHub: anonymous (a pull request's run,
  whose `GITHUB_TOKEN` has no rights in `agentkeel-studio`), or the App
  (a run of `main`'s code holding the key from the `platform-app`
  environment). Every GitHub reading in `template` and `upgrade` carries
  it, with the raw state beside the verdict (`open.md` row 3).
- **Stated before.** As SPEC/06 §2: an expected reading committed **and
  pushed** before the attempt it states.

## 3. The false state

Claim 7 is false if any of these is on `main`. Each names something a
reader can look at.

**Live today, at `57b9bf6` (tag `m06`).**

1. **No agent from the template exists** (every falsifier; F7.0).
   `scripts/platform_check.py` `POST_PERMISSIONS` asks `administration:
   read`; GitHub shows a ruleset's `bypass_actors` only to a caller that
   can administer it; so `src/validate/agent.py` `ruleset_errors` returns
   "ruleset 24310403's bypass_actors is not shown to the App's token" for
   every head. `gh api repos/agentkeel-studio/owner-check/commits/0c596c1/check-runs`
   shows the App's failure with that reason (14:24:31Z); #2's head
   `e3a8083` the same (15:24:56Z); `f6_0_owner_test.yaml`'s `merge_commit`
   is null. The registry holds `refagent` and nothing else.
2. **`app_token()` with no repository mints every permission on every
   repository** (`scripts/platform_check.py`, `scope = {}` when
   `repository is None`). Nothing in the tree reads which repositories the
   installation reaches, which permissions it holds, or whether the
   `platform-app` environment limits deployments to `main`
   (`milestones/M07/open.md` rows 2, 20). Read by hand at
   2026-10-02T02:12Z (`milestones/M07/runs/platform_app_branch_policies.json`:
   one branch policy, `main`, type branch;
   `runs/platform_app_environment.json`: `can_admins_bypass: true`). A
   reading by hand feeds no check.
3. **The observer's reading depends on who asks** (F7.0's input through
   `template`). `evals.yml` runs `scripts/observe_template.py` with
   `agentkeel`'s own `GITHUB_TOKEN`, which has no rights in
   `agentkeel-studio`; the envelope keeps `F6_2`'s verdict and not the raw
   `mergeable_state` or the viewpoint (row 3).
4. **Nothing opens an upgrade** (F7.1). No file under `.github/workflows/`
   is named `platform-upgrade` or `model-watch`; `scripts/` has no module
   that computes an agent's upgrade diff; `make upgrade` is not a Makefile
   target. `platform_version` is written once by `make_template.py`
   (`"m06"`, a literal) and read by the manifest schema as a pattern and
   by nothing else. refagent's `deprecated_after` is null and nothing
   polls Bedrock for it (`src/validate/lifecycle.py` reads the manifest's
   date only).
5. **Nothing retires an agent** (F7.2). `src/manifest/schema.json` allows
   `rollout` one value, `all-at-once`; `deploy.yml` has no job that
   removes a runtime; `scripts/registry.py` writes `name`, `repository`,
   `repository_id`, `commit_sha`, `deploy_run_id`, `deployed_at` and no
   `retired_at`; the audit bucket's prefixes are `envelopes/`, `AWSLogs/`,
   `agents/`, `test/` and no `bundles/` (`infra/security/`). An archived
   repository is skipped by `platform_check.repositories()`, so it is
   neither checked nor deployed again, and its runtime keeps answering.
6. **Nothing reads a rollback** (F7.3). `scripts/runtime_for_tree.py`
   matches refagent's runtime to the tree for a pull request's run and
   writes `mode`; nothing compares the runtime's digest with the tree's
   after a merge to `main`, and nothing records a revert as one
   (`milestones/M07/open.md` row 57).
7. **Panel 2 does not exist, and nothing compares a panel's verdict with
   an envelope** (F7.4). `infra/grafana/panel1.json` has one panel;
   `src/validate/panel.py` reads panel 1's query only;
   `src/verdict/template.py` compares panel 1's names with the registry
   and nothing with `evals/history/`.
8. **The surfaces have no plant list** (F7.5). `src/verdict/plants.py`
   names golden plants by kind and lists seeds by milestone; no control
   there names a surface's plants, so nothing counts them and a surface
   reader that stops refusing its fixture is noticed by nobody but a seed
   test.

## 4. Falsifiers

| Id | Fires when | What it looks like in the repo |
|---|---|---|
| F7.0 | no agent from the template exists to upgrade (amendment, §10) | `checks.F7_0: fail` from S0's three fixture tests; live, `upgrade.F7_0` fired or unread: the owner's test's new head refused for a reason other than the seats and the goldens, its fixed head refused, not merged, not deployed within `deploy_max_seconds`, not answering, not listed; the timed run's agent not merged, deployed, answering and listed; or `platform-check.yml` dispatched from a branch reaching the key (its `post` job not refused by the environment) |
| F7.1 | an upgrade requires a manual edit: no pull request the platform opened arrives, or a workflow or a person's commit was needed to merge it (amended wording, §10) | `checks.F7_1: fail` from S1's fixture test (a diff that touches a path outside the platform-owned files); live, `upgrade.F7_1` fired: a trigger with no draft pull request from the App within `arrive_max_seconds`; a pull request touching `.github/workflows/`; a person's edit on it (§2); `infra/workflows.sha256` changed between trigger and merge |
| F7.2 | a retired agent still answers | `checks.F7_2: fail` from S2's fixture test; live, `upgrade.F7_2` fired: the retire job's invocation after the deletion answered; `GetAgentRuntime` still finding the runtime `retire_max_seconds` after the merge; an answer record under `envelopes/agents/<name>/` after the deletion; no `bundles/<name>/<commit>.tar` |
| F7.3 | a rollback leaves the new digest live | `checks.F7_3: fail` from S3's fixture test; live, `upgrade.F7_3` fired: after the revert's deploy completed, the runtime's image tags hold the upgrade's digest, or do not hold the digest the tree gives at the revert's merge |
| F7.4 | a Grafana panel shows GREEN where the envelope says RED (read through Grafana's query API, as F6.4; amended from "Playwright asserts", §10) | `checks.F7_4: fail` from S4's two tests; live: panel 2's rows, as `/api/ds/query` returns them, name a commit whose row says GREEN and whose `evals/history/<commit>.json` says RED or UNMEASURED |
| F7.5 | `plants_expected ≠ plants_fired` for the surfaces | `checks.F7_5: fail` from S5's test and the run's count: `upgrade.surfaces.plants_expected` (the surfaces' control's list at the commit, 2) ≠ `plants_fired` (the readers that refused their fixture in the run). A test-only reading; it has no live half (item 18) |

**Where each reading comes from** (M04's, M05's and M06's lesson, planned
at open).

- **On every agent envelope, from PR 2's merge: `F7_0` to `F7_5`**, from
  the fixture tests of S0 to S5: each reader refusing its fixture.
  Test-only witnesses, and the ledger says so. `CLAIM_7_CHECKS` in the
  gate is those six (item 10).
- **The live readings are recorded, not gated.** They live in agent
  repositories, in the organisation, in AWS and in Grafana, after PR 2
  merges (§5.1). `scripts/observe_upgrade.py` (Engineering) writes raw
  observations only: for each run file under `milestones/M07/runs/` with
  an `observed` entry, what GitHub, AWS and Grafana returned, with the
  time each was read and the viewpoint beside every GitHub reading.
  `build` rules on them into an optional envelope field `upgrade`; the
  gate rules nothing on it. **Row 7's Measured cell reads `upgrade` and
  `template`**, as row 6's read `template`: anything fired or unread
  makes row 7's cell RED whatever refagent's own verdict.
- **Which run the cell cites** (item 8). A pull request's run cannot hold
  the App's key, so it reads from the anonymous viewpoint and says so.
  The App-viewpoint observation is made by a scheduled workflow on `main`
  (`main`'s code, the key from the environment), which reads the run
  files as they are on `main` and stores what it read with its run id and
  time. **Row 7's cell cites PR 4's run's envelope**, which carries that
  stored observation, named, beside its own anonymous one. So every
  attempt's `observed` entry must be on `main` before PR 4's run: they
  are committed in PR 3. An attempt recorded only on PR 4's branch is
  read from the anonymous viewpoint alone. R4 (§11) settles the storage
  before PR 2; if it changes this paragraph, the change is stated before
  PR 2's run.
- **A human-written file feeds no reading by itself.** A run file names a
  repository, a pull request, an agent, a commit. The observer reads
  GitHub, AWS and Grafana. A name it cannot find is unread.
- **P5.** Observers write raw observations; `verdict.build` writes the
  checks and `upgrade`; the gate reads the envelope and the ledger reads
  the gate. `tests/test_p5_disagree.py` gains a case for each new check.

## 5. The seeded cases

Planted at PR 1, one commit per seed, each before any reader. Code seeds
are fixtures under `tests/fixtures/m07/`; attempt seeds are run files
under `milestones/M07/runs/`, each the attempt to make with `observed:
null`. Each has its tests in `tests/test_m07_seeds.py`, marked
`xfail(strict=True, raises=...)` naming the one exception its planted
reason raises, run once with `--runxfail` so the message is read;
preconditions raise `SeedBroken`. Each is named in
`tests/fixtures/README.md` and in `src/verdict/plants.py` as `SEEDS_M07`;
none is copied to `evals/history/`. SPEC/06's S3 is received, not
re-planted: its run file and its test stay where M06 put them.

| Seed | Falsifier | Planted as | Fails today because | Read by (PR 2) |
|---|---|---|---|---|
| S0 the template's repair, read by CI | F7.0 | `runs/f7_0_owner_test.yaml`, three attempts, `observed: null`: the owner's test, steps 2 to 4 again on `owner-check` pull request 1; `platform-check.yml` dispatched from a branch (item 6); the App's token asked to relax `owner-check`'s ruleset. And `tests/fixtures/m07/s0-app-token/`: the installation as the API returns it (`repositories`, `permissions`) and the environment (`deployment-branch-policies`, `can_admins_bypass`), each twice: as the ruling will name it, and with a grant no ruling covers | the attempts are not made: every head is refused (§3 item 1). `app_token()` accepts no repository (§3 item 2); nothing reads the installation's permissions or the environment back | `scripts/platform_check.py`: `POST_PERMISSIONS` with `administration: write`; `app_token()` refusing a call with no repository; a `permissions` reader that takes the installation and the environment and fails on any value no ruling names. `src/validate/agent.py` failing closed on a hidden field and passing `[]`. The observer reading pull request 1's heads with the App's reasons, and the dispatched run's record |
| S1 a platform bump opens a draft pull request | F7.1 | `runs/f7_1_platform_upgrade.yaml`: the re-make of the template after PR 2 merges, and the draft pull request it must open in `owner-check` (the timed run's repository is added, pushed, when Product names the agent; item 7), `observed: null`. And `tests/fixtures/m07/s1-platform-upgrade/`: an agent folder at `platform_version: m06` with a workflow file of its own and an edited `agent.py`, beside the platform-owned files at a later version | the attempt is not made: nothing opens one (§3 item 4). No module computes the upgrade diff | `.github/workflows/platform-upgrade.yml` on `main` (Security), every 15 minutes: for each registered agent behind the template's version, a draft pull request as the App with the platform-owned files and the check's verdict at the new version (major or minor) in its body. `scripts/platform_upgrade.py` `diff` (Engineering), which the seed test calls on the fixture: it must change platform-owned files only, and leave the workflow file and `agent.py` alone. The observer reading the pull request |
| S2 a retired agent's target is gone | F7.2 | `runs/f7_2_retire.yaml`: the retire workflow dispatched for `owner-check` after it has deployed, answered, been listed and taken S1; the draft pull request setting `rollout: retired`; its merge; `observed: null`. And `tests/fixtures/m07/s2-retired-agent/`: CloudTrail's `DeleteAgentRuntime` record, a `GetAgentRuntime` answer that still finds the runtime, the retire job's invocation answered, and an answer record dated after the deletion | the attempt is not made (§3 item 5); nothing reads the records against each other | `deploy.yml`'s `retire` job (Security) from `main`; `scripts/retire_agent.py` and `scripts/registry.py retire` (Engineering); the schema's `rollout` enum; `build.f7_2` over the observer's records |
| S3 a `model-watch` pull request is merged and rolled back | F7.1 (the model upgrade arriving), F7.3 | `runs/f7_3_rollback.yaml`: `model-watch` opening a draft swap pull request moving refagent's pin to `pinned_roles.m04_cheaper_swap` (Haiku 4.5, never run; item 16), its merge if GREEN, its revert; and **the fallback, named here before any run**: if the swap's envelope is RED it is not merged, and the rollback is read on `owner-check`'s platform upgrade, merged and then reverted. `observed: null`. And `tests/fixtures/m07/s3-rollback/`: the tree's digest at a revert beside a `GetAgentRuntime` answer whose image tags hold the upgrade's digest | the attempt is not made (§3 item 6); nothing compares the two digests after a merge | `.github/workflows/model-watch.yml` on `main` (Security); `scripts/model_watch.py` (Engineering); `scripts/runtime_for_tree.py` given an agent, reused by the observer after each deploy; `build.f7_3` |
| S4 panel 2 forced to show GREEN on a RED envelope | F7.4 | `tests/fixtures/m07/s4-panel2/`: `dashboard.json`, a panel 2 whose query maps every verdict to GREEN; `frame.json`, panel 2's rows as `/api/ds/query` returns them, GREEN for `6f3d1618f42a…`; the envelope `evals/history/6f3d1618f42acbb217f7bcd62ecf2fc000ac4a9f.json` on `main`, RED (item 3) | nothing reads a panel 2 query or compares a panel's verdict with an envelope (§3 item 7) | `validate` refuses a panel 2 query that does anything but select the verdict from its source (`src/validate/panel.py`); `build.panel_verdict_mismatch(frame, history_dir)` compares by commit |
| S5 a surface plant goes silent | F7.5 | `tests/fixtures/m07/s5-silent-surface-plant/`: `results.json`, the surfaces' two plants with one reader's result missing from a run | nothing counts a surface's plants (§3 item 8) | `plants.SURFACE_PLANTS` naming the two; `build.surface_plants(results)` giving `plants_expected` 2 and `plants_fired` 1 on the fixture, written to `upgrade.surfaces` and `checks.F7_5` |

S0's fixture files are the shape of the reads row 2 demands, not the
reads: the live installation is read with the App's JWT, which no test
holds, first by `platform-check.yml`'s `post` job on `main` after PR 2
merges (item 11).

### 5.1 When each is measured

**A named P3 exception**, M06's again. The platform check posts from
`agentkeel`'s `main`, the deploy role trusts `main` only, the template is
published from what `main` holds, and `model-watch`, `platform-upgrade`
and the retire job run from `main`. Nothing live can be read before PR 2
merges, and the grant that lets the App read a ruleset is a GitHub
setting made by hand after a Security ruling.

- **PR 1, the plant.** Thirteen seed tests expected to fail: S0 four
  (three bounds, one run file), S1 to S3 two each (a fixture, a run
  file), S4 two (one per reader), S5 one. M06's video committed.
  `legal-compliance` written and run once (R8): on `data/slate.json` and
  `data/corpus/` for real IP, and on S2, the retirement, for the
  compliance map's row on a retired agent's records and their retention
  (item 40). Row 20's environment read recorded. No reader, no grant, no
  attempt.
- **Before PR 2's first commit: the rulings §11 owes**, by the human.
  None is a grant: they say what the grant will be. **And the dispatch
  from a branch** (S0's second attempt): it needs nothing M07 builds, so
  it is made, with R1 ruled and applied, and read as refused **before any
  grant** (`open.md` row 2: it "comes first"; security-reviewer 3).
- **PR 2's run, on the PR.** The nine fixture tests pass, each by its
  reader, and their markers are off; the four run-file tests stay
  expected failures (item 20). `checks.F7_0` to `F7_5` pass from them.
  `upgrade` on the envelope with every live reading unread. It cannot
  read the live grant: the key is `main`'s.
- **After PR 2 merges, each attempt stated before and pushed.** The
  grant comes first, and only now (item 36): `main` no longer carries
  `scope = {}`.
  1. Security makes the grant as ruled, and only if the dispatch from a
     branch was read as refused; the organisation accepts it;
     `platform-check.yml`'s `post` job on `main` reads the installation
     and the environment back.
  2. SPEC/06's S2 gets a new head: the owner pushes one empty commit to
     `s2-standin` (items 12, 13). The repaired App checks it; it is read
     **before** owner-check #1 merges, so "behind" cannot enter.
     `floresinnovations` is not touched.
  3. The owner's test, steps 2 to 4, on `owner-check` pull request 1.
  4. SPEC/06's S3, the timed quickstart, once, by `floresinnovations`,
     Act 1 recorded during it; before it, `f6_3_quickstart.yaml` and
     SPEC/06 §7's "five records" restated (`open.md` rows 4, 31), and
     every step above read as held, and Product agreeing.
  5. The template re-made from PR 2's merge; S1's pull requests arrive
     in `owner-check` and the timed run's repository; each merged by its
     seat when green.
  6. The seeded relaxation (S0's third attempt) on `owner-check`, with a
     new head pushed while the ruleset is changed; restored by the owner
     with the owner's own token and read back equal to the export.
  7. `owner-check` retired (S2), last, after the fallback rollback if S3
     needs it. A retirement is one-way: nothing restores the runtime.
  **Independent of 2 to 7** (item 30): `model-watch`'s pull request on
  refagent, at any time after the grant R3 rules; merged if GREEN, then
  reverted. The swap and its revert are pull requests on `main` outside
  the cap, by a line in the ledger, as #1 and #29 were.
  A step is attempted only when the steps it needs have been read as
  held; a miss stops what depends on it and nothing else.
- **PR 3 is the repair**, and carries every attempt's `observed` entry to
  `main`. **PR 4 is the close**, whose run's envelope the cell cites
  (§4). If PR 2 slips, panel 2 with S4's and S5's readers lands in PR 3;
  nothing else moves. A miss at PR 4 is a RED close with the finding.
  There is no fifth PR.
- **SPEC/06's S3 is made once** (SPEC/00 §10.5).
- **Act 2** is recorded against M02's pull requests at the close. Acts
  3, 4 and 6 are §9's cuts 2 and 3.

## 6. The code that reads the answer (PR 2)

None of it is in PR 1. Each with one seat and one path.

- **The grant** (Security; by hand, after PR 2 merges): the App
  `agentkeel-platform` (5144253) granted what
  `milestones/M07/rulings/pr2-security.md` names and nothing else,
  accepted by the organisation's owner. That file rules each bound of
  `open.md` row 2 and **the mint points and permission sets, one per
  workflow** (item 33): `platform-check.yml`'s `post`
  (`administration: write`, `checks: write`, `contents: read`), per
  repository; `platform-upgrade.yml` and the retire job (`contents:
  write`, `pull_requests: write`, per repository, no `checks`, no
  `administration`); the observer (`pull_requests: read`, `checks:
  read`, `contents: read`). **With one App and one key this split binds
  nothing** (security-reviewer 1): a token is narrowed by the request
  that mints it, the installation holds the union, and any job that holds
  the key can mint all of it, so it could open a change, post the check
  that passes it and merge it. The proposal put to Security under R2 is
  therefore **three Apps, each with its own key in its own environment
  limited to `main`**: the platform's (5144253) for the check; a second
  for opening pull requests (`contents: write`, `pull_requests: write`,
  no `checks`, no `administration`); a third, read-only, for the
  observer. 5144253 is never installed on `andaro74/agentkeel`, whose
  required checks are names any App could answer to (security-reviewer
  2). Each App and each permission is a grant, made by the human after
  its ruling; if Security keeps one key, this section and §8 say the
  split is a convention in `main`'s code.
- **The token** (`scripts/platform_check.py`, Engineering):
  `POST_PERMISSIONS` asks `administration: write`; `app_token()` requires
  a repository and a named permission set and refuses a call without
  either; a `permissions` reader takes the installation (`GET
  /app/installations/{id}`) and the environment
  (`deployment-branch-policies`, `can_admins_bypass`) and exits 1 on any
  value not named by a `grant:` block in a ruling file under
  `milestones/M07/rulings/`. `platform-check.yml` runs it first in `post`
  (Security).
- **The reader** (`src/validate/agent.py`, Engineering): `ruleset_errors`
  fails closed on a hidden `bypass_actors` (as today) and passes `[]`;
  the test reads both.
- **The seeded relaxation** (Security; S0's third attempt): the App's
  token, minted as `post` mints it, asked to change `owner-check`'s
  ruleset. Expected: refused, if GitHub has a read-only form of the
  grant; otherwise accepted, and the next platform check refuses every
  head until the owner restores the export, which is detection, not
  refusal, and is said so. Which it is comes from the attempt.
- **The observer's viewpoint** (Security; row 3; §4): a scheduled
  workflow on `main` with the observer's permission set, storing its
  observation; `scripts/observe_template.py` and `observe_upgrade.py`
  record the viewpoint and the raw `mergeable_state` beside every GitHub
  reading; `build` rules on `blocked` as today and names the viewpoint.
  The App's key never enters a job that checks out pull-request code.
- **The template's version** (`scripts/make_template.py`,
  `src/manifest/schema.json`, Engineering; item 34): the tag or the
  short commit; the schema's pattern takes both. **The re-make** is the
  owner's push to `agent-template` at M07 (Security, R5).
- **`platform-upgrade`** (`.github/workflows/platform-upgrade.yml`,
  Security; `scripts/platform_upgrade.py`, Engineering): every 15
  minutes on `main`; reads the registry and each agent's
  `platform_version`; for each behind the template's, computes the
  platform-owned files' diff, evaluates the agent's head with
  `src.validate.agent` at `main` to record major or minor, and opens one
  draft pull request as the App in that repository. `make upgrade` runs
  `platform_upgrade.py diff` locally and opens nothing (§9 cut 5). Two
  jobs, as `platform-check.yml` has: one with no secret that reads the
  agent repository as data and computes the diff; one with the key that
  runs `main`'s code on the first's artifact. The retire job the same
  (security-reviewer 4; `open.md` row 2: "never beside agent-repository
  or pull-request code").
- **`model-watch`** (`.github/workflows/model-watch.yml`, Security;
  `scripts/model_watch.py`, Engineering): scheduled on `main`; reads
  `modelLifecycle` for refagent's pin and `pinned_roles`
  (`bedrock:GetFoundationModel`, as the eval role); opens a draft pull
  request writing `deprecated_after` from `endOfLifeTime` when it
  differs, and a draft swap pull request when the Threshold Owner's
  named candidate differs from the pin. Each carries a drafted ruling
  file for the seat to rule. A pull request in `agentkeel` needs a token
  the workflow can hold (Security, R3); one opened with `GITHUB_TOKEN`
  starts no workflow.
- **Retirement** (`deploy.yml`'s `retire` job and the archive step in
  `deploy-agent`, Security; `scripts/retire_agent.py`,
  `scripts/registry.py retire`, the schema's `rollout` enum,
  Engineering; the audit bucket's `bundles/` statement and its
  principal, `infra/security/`, Security, deployed by hand after reading
  `cdk diff`; item 32): every deploy puts the signed archive once under
  `bundles/<name>/<commit>.tar`. On dispatch for an agent, or for a row
  flagged idle or a pin within 30 days of `deprecated_after`, the job
  opens the draft retirement pull request. For a row whose passed head
  carries `rollout: retired`: `DeleteAgentRuntime` and the stack's
  deletion through the deploy role, one invocation of the ARN, recorded,
  then `retired_at`. The idle flag: `idle_since` on a row with no answer
  record for 90 days. refagent is never retired by this path.
- **The rollback reading** (`scripts/runtime_for_tree.py` given an agent
  name, Engineering): after each deploy run completed, the observer
  reads the runtime's image tags and the tree's digest at the deployed
  commit; `build.f7_3` compares them for the revert's merge.
- **Panel 2** (`infra/grafana/panel2.json` and its Athena table,
  Security): one row per envelope, `commit`, `verdict`, `mode`, as
  stored. Its query check in `validate` (`src/validate/panel.py`,
  Engineering): the source, the columns, no expression over `verdict`.
- **The surfaces' plants** (`src/verdict/plants.py`, Engineering):
  `SURFACE_PLANTS`, two; `build.surface_plants` counts them from the
  seed tests' results (`JUNIT`, as `F0_2` is read).
- **`upgrade`, `CLAIM_7_CHECKS`, row 7's reading** (`src/verdict/`,
  `src/ledger.py`, Engineering; the steps in `evals.yml`, Security):
  `upgrade.F7_0` to `F7_5`, `upgrade.taken`, each with `read`, `held`,
  `reasons`, `viewpoint`; `READ_THE_UPGRADE = {"M07"}`; row 7 reads
  `upgrade` and `template`.
- **The bars** (`thresholds.yaml`, Threshold Owner): `upgrade.*` (§2),
  with `relaxes:`. A two-key test on `quickstart.max_seconds` is owed
  (`open.md` row 23).
- **The documents** (Product): `docs/developer/upgrade.md`;
  `docs/platform/surfaces.md`; `docs/compliance/map.md` as
  `legal-compliance` drafts it, doc-only (§9 cut 1).
- **The seats** (Security): none change. `legal-compliance`'s front
  matter names Product; CODEOWNERS gains its line under Product in PR 1.

## 7. Expected on the plant (row 7)

- **PR 1.** refagent's envelope, gated and recorded as at M06; it says
  nothing about claim 7. `make plants` lists S0, S1, S2, S3, S4 and S5
  (seeds, not golden plants). `uv run pytest tests/test_m07_seeds.py`
  shows thirteen expected failures. `make validate` passes: nothing reads
  an installation, an upgrade, a retirement, a rollback, panel 2 or a
  surface's plant. `make ledger` exits 0 with row 7 OPEN and its Measured
  cell empty. `uv run pytest tests/test_m06_seeds.py` still shows one
  expected failure, S3's.
- **PR 2's run, stated before it** (pushed first).
  `tests/test_m07_seeds.py`: nine passed, four expected failures (the run
  files). `checks.F7_0` to `F7_5` pass. `upgrade` written with every
  live reading unread, `surfaces.plants_expected` 2 and `plants_fired`
  2, `taken` 0 of 3. refagent otherwise as at M06: ordinary 9/9, traps
  2/2, guardrail 2/3, red team 5/5, golden plants 7/7, `template` as at
  `245eb9b`.
- **PR 4's run, stated before each attempt** (§5.1). The installation
  and the environment as ruled; the dispatch from a branch refused at
  `post`. S2 of SPEC/06: its new head refused by the App on its null
  seats and goldens and nothing else, `blocked` from the App's
  viewpoint, the stand-in's run a success. The owner's test: pull
  request 1's new head refused on the seats and the goldens and nothing
  else; the fixed head passed; merged; deployed within 3,600 s; one
  answer record; the registry row; panel 1 listing `owner-check`.
  S3 of SPEC/06 under 28,800 s with all four records read. S1: one draft
  pull request from the App in each repository within 4,500 s of the
  template's push, changing `manifest.yaml`'s `platform_version` and
  whichever platform-owned file PR 2 changed (stated by name before the
  re-make), no person's edit, merged green, deployed; major or minor as
  read; `taken` 1 of 3. S3: a draft pull request from the App on
  `agentkeel` moving the pin to Haiku 4.5; its envelope as the gate
  rules it, **not stated**: Haiku 4.5 has never been run. If GREEN:
  merged, reverted, the runtime's tags holding the tree's digest at the
  revert and not the swap's; row 58's `F4_4` on the first `main`
  envelope after the merge recorded as read. If RED: not merged, and
  F7.3 read on `owner-check`'s platform upgrade reverted. `taken` 2 of 3
  only if a model pull request merged and went live; with the fallback
  the model kind is not taken and the row is RED on `taken`, with F7.3
  still read. S2: the draft pull request from the App within 4,500 s of
  the dispatch; merged; `DeleteAgentRuntime` within 3,600 s; the
  invocation refused; the runtime gone; the bundle under `bundles/`;
  `retired_at`; no answer record after; `taken` 3 of 3.
- **The row goes RED** if F7.0 is unread or fired; if `taken` is under 3;
  if any trigger gets no pull request from the platform, or one that
  needed a workflow or a person's edit; if the retired agent answers or
  its runtime stands; if a revert leaves the upgrade's digest live; if
  panel 2 shows GREEN on a RED envelope or the surfaces' counts differ;
  if a seed's test passes for a reason other than its reader; if PR 4's
  run cannot read an attempt; or if `make ledger` stops matching rows 0
  to 6.

## 8. Controls with no seeded case at M07

SPEC/00 §10.5: no document describes these as working.

- **The App's write token relaxing a ruleset.** The seeded attempt (§6)
  reads one call. It does not read the token removing the required check
  bound to 5144253, changing a collaborator, or editing a setting; each
  is possible with Administration: write and is detected only by the
  next platform check, if at all. The permissions reader reads the grant,
  not its use.
- **The App merging its own pull request** (item 33). With `contents:
  write` on an agent repository the platform could merge what it opened.
  The permission sets are split so that the token that opens cannot post
  the check; no seed attempts a merge by the App.
- **One key behind every permission set**, unless Security rules three
  Apps (§6). Nothing mechanical reads which job minted which token.
- **Who can change what the keyed job does** (security-reviewer 5): the
  `post` job runs `scripts/platform_check.py`, `src/validate/agent.py`
  and whatever `uv.lock` installs, all Engineering paths gated by
  `cold-review-ruling`; `infra/workflows.sha256` covers the workflow file
  only. The reader of the grant lives in the file it guards. One person
  holds every seat (R1), and nothing mechanical stops an edit that
  removes the reader.
- **A ruling line's author is not read** (security-reviewer 8):
  `cold-review-ruling` looks for a line that starts "Ruled by", not for
  who committed it. `model-watch` drafts its ruling file and must not
  write that line.
- **A platform pull request edited after it arrived.** F7.1 reads the
  commits' authors; nothing stops an owner merging one a person changed.
- **A platform upgrade moves `guardrail` in an agent repository with no
  Rule Owner ruling** (item 35): agent repositories ask for none.
- **The "touching `.github/workflows/`" arm of F7.1 has a plant in the
  fixture only** (item 24): no live upgrade can touch a workflow in a
  repository that has none.
- **A platform change that is not in the platform-owned files**: a change
  to `agent.Dockerfile`, the construct or `deploy.yml` reaches every agent
  at its next deploy with no pull request anywhere. No M07 falsifier
  reads it.
- **`model-watch`'s candidate is named by a person.** Which model is
  equivalent is the Threshold Owner's (SPEC/04 §2). A model changing
  under an unchanged pin is caught only inside one job's A-vs-A.
- **`deprecated_after` written from Bedrock** (item 19): refagent's pin
  has no end-of-life date, so the seeded run writes nothing; no seed has
  a pin with one.
- **Retirement by `deprecated_after` or by the idle flag**: the seeded
  trigger is the dispatch. No seed can wait 30 or 90 days. A repository
  deleted or archived without a retirement leaves a runtime answering
  and a row GitHub cannot match: flagged, not retired.
- **A GREEN on panel 2 under a RED row** (item 25, §2).
- **Panel 2 reads what the workspace can reach**, not the envelope the
  ledger reads, unless the comparison says so.
- **Nothing asserts what a person sees rendered**: Playwright is not
  used (§10); the query API is what is read.
- **`agentkeel`'s own required checks are names** (SPEC/06 §8, row 27);
  the reader is the pull request's own code (row 36). Unchanged.
- **The judge, FRAGILE, the knowledge base, Braintrust, HITL as a Gateway
  tool, `ratings-helper`'s code, the gateway, k6, the CLI**: not built
  (§9, §10).
- Every `milestones/M07/open.md` row: its seat and where it goes is in
  `milestones/M07/feasibility.md` §6.

## 9. Cut list

Ruled at open (BLOCK 3, option a). Cuts a to e are **taken at open**:
none feeds an M07 falsifier, and the cap already holds S0, SPEC/06's S3
and five seeds. The numbered cuts are taken in order, item 1 first, only
if the cap is threatened. **None cuts S0, SPEC/06's S3 or Act 1, S1 to
S5, their readers, Act 2, or the rulings §11 owes.**

M08 adds no code path (SPEC/00 §8 M08). So a code item cut from M07 is
**not built in this project**, and is recorded in SPEC/00 §12 with how
many times it moved.

| # | Item | Goes to | Why |
|---|---|---|---|
| a | The Bedrock Knowledge Base over the production bucket and refagent retrieving from it (`open.md` rows 32, 45, 48, 49, 50, 51) | not built in this project (SPEC/00 §12) | Its fifth move. With it, **not measured in this project**: the cached-answer seed, F3.5's second half (claim 3's), `g-014` as a plant (it stays never-passed) |
| b | The judge (Bedrock Evaluations, its rubric, the graded examples, `admitted_false_fails.json`, `model-watch` over it) and FRAGILE (`open.md` rows 52, 63) | not built in this project (SPEC/00 §12) | R6's judge of record never lands. "Correct" stays the answer's fields compared by code, tool-grounded (M04 PR 2) |
| c | The Braintrust mirror, its divergence check, redaction (`open.md` row 64) | not built in this project (SPEC/00 §12) | Its third move |
| d | Grafana panels 3 and 4 (call graph, containment) | doc-only (SPEC/00 §8 M07's second cut): `docs/platform/surfaces.md` | No M07 falsifier reads them |
| e | HITL as a Gateway tool with its own edge, budget and audit; `ratings-helper`'s code; the gateway; Identity-only credentials; the per-agent Budgets filter; the nightly graph diff; k6; the CLI (`agent upgrade`, `agent evals --local`, P11); the Rule Owner's filter on tool results and S5 of SPEC/05's live half; Promptfoo as the runner (`open.md` rows 35, 39, 53, 54, 59, 60, 61) | not built in this project (SPEC/00 §12) | Direct Converse was ruled 2026-09-27; a second agent's code would be measured by no M07 falsifier. **Not measured in this project**: S5 of SPEC/05's live half (row 35) |
| 1 | The compliance map page | doc-only (SPEC/00 §8 M07's first cut): `legal-compliance` drafts the rows for M00 to M07's controls with their evidence paths; Product commits what it accepts | SPEC/00 §15 asks it to link evidence for every control it names |
| 2 | Act 6 (upgrade and retire) | M08 PR 4 (SPEC/00 §8 M07's third cut) | A recording |
| 3 | Act 4 (a model swap) and Act 3 (the reference agent, M06's cut 2) | M08 PR 4. Act 3's script loses its HITL refusal and its Braintrust trace (cuts c, e) | Recordings |
| 4 | `docs/developer/manifest.md`, `goldens.md`, `edges.md` (M06's cut 3) | M08 PR 4 | Guides; `docs/developer/upgrade.md` stays |
| 5 | `make upgrade` as a local command | the workflow alone | The pull request arrives from the platform |

**What cuts a to e break downstream**, each a recorded contradiction in
SPEC/00, ruled at M08 open and carried in M08's `open.md` at M07's close
(M08's text is M08's to rewrite; one milestone per session):

1. R6 (SPEC/00 §11): there is no judge of record.
2. SPEC/00 §8 M08 run 1's sixth attempt, "prompt injection aimed at the
   judge rubric", and `open.md` row 74: no judge to aim at.
3. F8.5's "revoke the Gateway policy": there is no gateway; quarantine is
   the deny-all M05 measured.
4. SPEC/00 §8 M08 PR 3's "Braintrust experiments for all three".
5. SPEC/00 §10.2 Act 3's "a HITL refusal" and "the Braintrust trace".
6. SPEC/00 §15's "at least seven are GREEN": rows 1, 4, 5 and 6 are RED,
   so at most five of nine can be. Read from the ledger today, not at
   M08.

## 10. The amendments to SPEC/00 made at this PR

Ruled by the human as Product on 2026-10-01, before any seed
(`milestones/M07/feasibility.md` §2; `rulings/pr1.md`).

1. **SPEC/00 §8 M07, build and seeded cases.** Gains **S0, the
   template's repair read by CI through the owner's test**, and receives
   **SPEC/06's S3** (the timed quickstart, with Act 1), both never cut.
   "Platform major bump opens a draft PR" reads "a platform bump opens a
   draft PR; major when the platform check at the new version refuses
   the agent's head, recorded". "A Playwright plant goes silent" reads "a
   surface plant goes silent"; the build line's "Playwright over the
   surfaces with a plants-fired list" reads "a plants-fired list for the
   surfaces" (item 38). The retirement workflow's trigger is a pull
   request (BLOCK 1). SPEC/00 §6's `platform_version` is "the platform
   tag or commit the template was made from".
2. **SPEC/00 §8 M07, falsifiers.** Gains **F7.0**, "no agent from the
   template exists to upgrade". **F7.1** reads "an upgrade requires a
   manual edit: no pull request the platform opened arrives, or a
   workflow or a person's commit was needed to merge it; a ruling file is
   not a person's edit". As written it could not fire in an agent
   repository, which has no workflow. **F7.4** reads "(read through
   Grafana's query API, as F6.4)" in place of "(Playwright asserts)":
   Managed Grafana authenticates through Identity Center, which a browser
   under test cannot pass with a service-account token. SPEC/00 §13's
   Playwright row is marked not used.
3. **SPEC/00 §8 M07, cut list**: §9's, with cuts a to e taken at open and
   recorded in SPEC/00 §12; the six contradictions above recorded in
   SPEC/00 §8 M07 for M08's open.
4. **SPEC/00 §10.5** stands as M06 PR 4 wrote it (`open.md` row 7). NOTE
   23 of `milestones/M06/feasibility.md` extends to S3's attempt at M07:
   `andaro74` stays on GitHub Pro and `floresinnovations` stays as it is
   until then (`open.md` row 11).
5. **Row 6's claim keeps "governed"** (`open.md` row 8): a claim is not
   rewritten at its close. No M07 prose uses "governed", "secure" or
   "proven" of F6.1 to F6.3, F7.0 to F7.5, or the App's grant.

Also not in M07:

- Any change to `src/baseline/` (ADR-0002), to an existing bar, or to a
  golden id.
- The landing zone, SCPs, and `open.md` row 75 (deferred with the landing
  zone; re-ruled at M08 open).
- The rows dated M08 in `milestones/M07/open.md` (34, 68 to 75) stay M08's.

## 11. Read before PR 2

Each read is put to the human with a recommendation and ruled by the
human in the seat named before PR 2's first commit; the outputs of reads
are committed under `milestones/M07/runs/` (M06 PR 4, Unsure E). None is
a code change and none is a grant.

| # | Seat | Read | Then rule |
|---|---|---|---|
| R1 | Security | Row 20: the `platform-app` environment (read 2026-10-02T02:12Z: one branch policy, `main`, type branch; `can_admins_bypass: true`). Whether an admin's bypass reaches a deployment branch policy (item 37) | whether `can_admins_bypass` is inside the bound or is switched off first; the dispatch from a branch is S0's second attempt, made and read as refused **before the grant**. Read 2026-10-02T03:16Z (`runs/platform_app_read.md`): `PLATFORM_APP_PRIVATE_KEY` is a secret of the environment only; the repository's own secrets are `AGENTKEEL_GRAFANA_TOKEN` and `RULESET_TOKEN` (security-reviewer 11) |
| R2 | Security | The installation as the App's JWT returns it: `repository_selection`, `repositories`, `permissions`; GitHub's documentation of which permission shows `bypass_actors` and whether a read-only form exists | row 2's bounds, one by one, and the permission set per workflow (§6), in `rulings/pr2-security.md`, with its `grant:` block; one App or three (§6); how a new agent repository enters the grant (`selected` or `all`) and what that does to S3's clock; whether `agent-template` is in it; where S0's third attempt mints its token (security-reviewer 1, 2, 6, 14). The grant itself after PR 2 merges |
| R3 | Security | Whether the App can be installed on `andaro74/agentkeel` with `contents: write` and `pull_requests: write` for `model-watch`'s pull requests, or a fine-grained token in the `platform-app` environment is the smaller grant; whether a pull request opened by an App installation token starts `evals.yml` | the token `model-watch` opens pull requests with |
| R4 | Security; Engineering | Where the scheduled observer on `main` stores its observation, and how a pull request's run takes it as data without the key | row 3's design; §4's paragraph on which run the cell cites, restated if it changes |
| R5 | Security | Whether the platform pushes the re-made template or the owner does, by hand, as at M06 | proposed: the owner, at M07 |
| R6 | Threshold Owner | `GetFoundationModel` for refagent's pin and `pinned_roles`; Haiku 4.5's access (`scripts/check_model_access.py`) and whether the eval role and refagent's runtime role may call it; the cost of a swap run against `cost_cap` | the candidate as named (item 16) or another, before `model-watch` runs; `open.md` rows 58, 65 to 67; what is done if the revert's own envelope is not GREEN, named in S3's run file before the swap is merged; with Security, whether the candidate's access stays after the revert (security-reviewer 16) |
| R7 | Security | `DeleteAgentRuntime`'s behaviour on a runtime with an endpoint; what the stack's deletion through the deploy role needs that it does not have; the agent key's deletion window; the `bundles/` statement | the retirement path's grants, as a diff for the Security seat's PR, and the security account's hand deploy; every resource of a retired agent listed as deleted or kept (the construct keeps the key, its alias and the rights table when a stack is deleted; the log group), and what the key encrypts, committed under `runs/` before the dispatch; the deletes scoped in IAM so refagent's and the bootstrap's stacks are out of reach; whether the retire job also writes the retirement to the audit bucket (legal-compliance 9, 10; security-reviewer 10, 15) |
| R8 | Security | Where panel 2 reads envelopes: Athena over the audit bucket's `envelopes/` prefix in the security account, or a copy the deploy path writes in the agent account; the Grafana observer token's renewal before 2026-10-31 (`open.md` row 9) | panel 2's source; who renews the token and when |
| R9 | Product | `milestones/M06/runs/f6_3_quickstart.yaml`'s "after M06 PR 3" and "PR 4's run"; SPEC/06 §7's "five records" against four | the restatements, pushed before S3 |
| R10 | Product; Security | Which pull request carries the owner's test at M07 | proposed: a new head on `owner-check` #1 with the template's content (an empty commit), then the fix; S0's run file names it before the attempt |

## 12. Ruled before PR 2, and what PR 2 built

Added at M07 PR 2 (Product). §1 to §11 stand as PR 1 wrote them; this
section says how §11's reads were ruled and where PR 2's build differs
from §6's words. No claim, falsifier or seeded case changes. Where this
section and §6 differ, this section is what was built.

**Ruled on 2026-10-02, "as proposed", before any PR 2 code**
(`rulings/pr2-security.md` items 1 to 12; `rulings/pr2-threshold-owner.md`
items 1 to 4; the reads in `runs/pr2_reads.md`):

| Read | Ruled |
|---|---|
| R1 | Admin bypass off on every environment that holds an App's key. The platform check dispatched from a branch was refused by the environment on 2026-10-02, before any grant (run 36963543726): S0's second attempt, made |
| R2 | **Three Apps**, each key in its own environment limited to `main`: `agentkeel-platform` (5144253) posts the check; `agentkeel-upgrades` opens pull requests; `agentkeel-observer` reads. The installations stay on "all repositories". 5144253 is never installed on `andaro74`. §6's "one App and one key binds nothing" is therefore not the case built, and §8's "one key behind every permission set" does not apply |
| R3 | `model-watch` opens its pull requests as `agentkeel-upgrades`, installed on `andaro74` for `agentkeel` alone |
| R4 | The observer on `main` stores its observation under `observations/` in the audit bucket, through a role that trusts `main` only. §4's paragraph on which run the cell cites stands unchanged |
| R5 | The owner pushes the re-made template, by hand, at M07 |
| R6 | The candidate is Haiku 4.5. If its revert is RED on `F4_4` alone, one stated second run; if RED on a regressed golden or RED twice, refagent stays on Haiku 4.5 until a pin change passes, F7.3 is read on the fallback, and `taken` stays under 3 (`runs/f7_3_rollback.yaml`) |
| R7 | **A retirement is a stack update that removes the runtime**, with no new IAM: §2's and §6's "the stack's deletion" is not built, and the stack stays. What is removed and what is kept is `runs/f7_2_removed_and_kept.md`. The retirement is also put once in the audit bucket. `bundles/` gets its put-once statement |
| R8 | **Not ruled on 2026-10-02.** Panel 2's source is put to Security as item 13d of `rulings/pr2-security.md`: a table in the agent account, `agentkeel-envelopes`, written on a push to `main`. The Grafana token is renewed by the human before 2026-10-31 |
| R9, R10 | Restated before S3 and before the owner's test, after PR 2 merges, as §5.1 says |
| The bars | `upgrade.arrive_max_seconds` 4,500, `deploy_max_seconds` 3,600, `retire_max_seconds` 3,600, each relaxes up. The p95 bar stays at 2.0; the rule for a miss is SPEC/04 §2 |

**Where the build differs from §6's words, each said in a ruling file:**

- **"The token."** `app_token()` takes a repository and the *name* of a
  permission set from one table, `PERMISSION_SETS`. `post` mints twice per
  repository: `rulesets` (Administration: write) for the one read, revoked
  after it, then `check`.
- **"`platform-upgrade`."** It lists agents from GitHub (the heads the App
  passed), not from the registry, so it holds no AWS credentials (item
  13g).
- **"`model-watch`."** It reads Bedrock as a role of its own,
  `agentkeel-model-watch`, not as the eval role (item 13b).
- **"Retirement."** As R7. The idle trigger (no answer record for 90 days)
  is not built: nothing writes `idle_since`. The dispatch and a pin 30
  days from `deprecated_after` are. refagent's own deploy does not put
  its bundle under `bundles/`.
- **"Live"** (§1 item 4), for an upgrade a later deploy has since
  replaced: read from the deploy run of its merge and from the image its
  tree's digest names, not from the runtime as it stands when the cell's
  run reads it. A rollback (F7.3) is read from the runtime as it stands.
- **The seeded relaxation.** The script refuses any repository but the one
  S0's run file names on `main`.
- **A pull request the platform opens is opened once per branch name**
  (`platform-upgrade/<version>`, `platform-retire`, `model-watch/<role>`).
  After a merged upgrade is reverted, the same upgrade is not opened a
  second time.
- **`agentkeel-upgrades` is a public App**, because GitHub installs a
  private one on its owner alone (item 13a).

**Controls with no seeded case, added to §8 by this build:**

- A public App installed by a stranger: recorded by the reader of the
  grant from the App's own listing, with no token asked for on that
  account (repaired after security-reviewer BLOCK 1 on PR 2: until then
  the reader minted a metadata token on every installation). No seed
  installs it elsewhere.
- The names of an environment's secrets: read by hand, by an admin. No job
  can list them.
- The table panel 2 reads is a copy an admin of the agent account can
  edit. The comparison with the envelopes (F7.4) is what would notice.
- A second run of a pull request that is RED on `F4_4` alone (SPEC/04
  §2): no gate reads whether the rule was followed.

**After the seat reviews of PR 2** (the four reports read
`a2c5a61...1b376a3`; `milestones/M07/rulings/pr2-engineering.md` and
`pr2-security.md` carry each finding and what was done). What the build
does differently from the text above, and what it still does not do:

- **A retirement is recorded only when the runtime is gone.** The retire
  job writes `retired.json` and `retired_at` only after one invocation is
  refused with `ResourceNotFoundException`. On any other result it fails
  and the next run asks again. A retired name is not deployed again:
  the registry refuses it.
- **The dispatch from a branch is a refusal only on GitHub's own word**:
  the annotation on the `post` job that says the branch is not allowed to
  deploy to `platform-app`. A relaxation is refused only on a 403.
- **A pull request that has not merged is unread**, not held.
- **Every word the platform writes as an App** (a title, a body, a
  drafted ruling) is written by the keyed job from what it checked.
- **Panel 2's table is written through `replay_history`**, by
  `scripts/envelope_rows.py`, in a job of its own.

**Controls with no seeded case, added to §8 after the reviews.** No
document describes these as working:

- **A person's edit, as §2 defines it, includes CI's own commit.**
  `evals.yml` pushes `evals/history/<commit>.json` to every `agentkeel`
  pull request as `github-actions[bot]`. By §2 that is a commit "whose
  author is not the platform's App and which touches any path but a
  ruling file". So the model upgrade cannot read as held, and
  `upgrade.taken` is at most 2 of 3, until Product amends §2. The reader
  keeps to §2 as written, and a test holds it there. Product rules,
  before the swap is opened.
- **"No person's edit" rests on a commit's author as GitHub attributes
  it.** A commit made with the App's noreply address would read as the
  App's. The observer now writes each commit's committer and GitHub's
  verification; nothing rules on them until a commit by
  `agentkeel-upgrades` exists to read.
- **The bytes a platform upgrade proposes are the plan's.** The keyed
  job holds the paths, the manifest's fields and the version, not the
  content of `server.py`, which the plan job takes from the template
  repository's default branch. Whoever can push there sets what is
  proposed to every agent. It is a draft a seat still merges.
- **A retirement is a stack update from a head nobody signed.** The
  retire job checks that the head says `rollout: retired`; it does not
  hold the rest of the manifest to the commit the registry holds, so
  another field can move with it. No compute uses the result.
- **Put-once on `bundles/` and `observations/`**, and **the trust of
  `agentkeel-model-watch`, `agentkeel-envelope-row-put` and
  `agentkeel-observation-put` to one workflow on `main`**: template
  tests only. None has refused anything.
- **A row of panel 2's table is put once by a condition in the script**,
  not by IAM: the role holds `PutItem`.
- **The two roles PR 2 adds are not in the agent key policies' list of
  platform roles.** The deploy boundary and the absence of a kms Allow
  hold R4 for them.
- **The grant block, the seeded relaxation's repository and the reader
  of the grant are on Product's and Engineering's paths**
  (`milestones/**`, `scripts/**`), so a pull request that widens them
  meets no Security gate. One person holds every seat (R1).
- **The seeded relaxation is refused a second time only once the run
  file on `main` records the first.**
- **The `agentkeel-upgrades` key on `andaro74/agentkeel`** can push to
  any branch but `main`, and a pull request it opens runs `evals.yml`
  with that workflow's roles and tokens, as any collaborator's does.
- **`two-key` does not read `deprecated_after`** (ADR-0009 amendment 1
  says it does from M04 PR 2). `model-watch`'s own refusal is the only
  thing that stops the platform proposing a later date.
- **The App's stored observation may be older than the run's.** Where
  the run read a commit or a merge the stored record lacks, the run's
  own reading is used. Nothing else compares their times.

**At M07 PR 3 (the repair; Product, `milestones/M07/rulings/pr3.md`,
2026-10-02).** §1 to §11 stand as written but for §2's dated amendment.
What this section corrects, and what the repair built.

**§5.1's "PR 3 is the repair, and carries every attempt's `observed`
entry to `main`", and §4's "they are committed in PR 3", cannot hold.**
The first deploy of an agent from the template failed in the platform's
own `deploy.yml` (run 37023118799): `sign-agent` uploaded three paths
under two roots, GitHub rooted the artifact at their common parent, and
`deploy-agent` did not find the signature. The deploy runs from `main`,
so no later attempt can be made until the fix is merged, and a fifth
pull request is a RED close. So: **PR 3 is the workflow fix and every
repair owed before the next attempts, merged once, and carries one
`observed` entry, the owner's test's. PR 4 carries every other attempt's
entry and is the close.** The consequence §4 already names: an attempt
recorded only on PR 4's branch is read from the anonymous viewpoint
alone. The App's viewpoint will have read what `main`'s run files name:
the owner's test, the dispatch, and SPEC/06's S2.

**F7.0 fired on the owner's test.** Made once, on 2026-10-02, as stated.
The new head was refused on the seats and the goldens and nothing else;
the fixed head passed and merged (`5249dec`, 14:39:32Z); the App passed
the merge commit. The deploy did not complete within
`upgrade.deploy_max_seconds`. The attempt is not re-made and not
restated. Row 7 is expected to close RED on it. The other attempts are
still made and measured.

**Repaired at PR 3, each named above as open or as a control with no
seeded case.** Each is held by tests on fixtures or a seeded case. None
has run live, and no document describes any as working.

| What | Was | Now | Before |
|---|---|---|---|
| A person's edit (§2) | CI's own envelope commit was one | amended; the reader follows it | the swap |
| Who made a commit (cold review F5) | the author's login | GitHub's record: the App's bot as author, verified, the bot or GitHub's signer as committer. Anything else is not the App's | S1 |
| The relaxation's times (cold review F6) | compared by the observer; "after the restore" was any pass after the call | compared by `build`; the restore is the ruleset's own last change, when it equals the export | the relaxation |
| The observer's keyed job (security-reviewer 12) | the key held through every read; a bearer token sent on a redirect | tokens minted first and the key let go; no tree packed beside it; no credential to the storage host | its first keyed run |
| The two new roles and the key policies (13h) | in neither list | in both | owner-check's first deploy |
| The grant and its reader (13j) | on Product's and Engineering's paths | `infra/platform_grant.yaml`; `scripts/platform_check.py` Security's (ADR-0012) | binds from the next pull request |
| The bytes an upgrade proposes (13l) | the plan's | each file held to the template at the commit the plan names, read by the keyed job; the guardrail to `main`'s | S1 |
| A retirement's head (13i) | checked for `rollout: retired` only | held to the manifest at the registry row's commit; any other move refused | S2 |
| `two-key` and `deprecated_after` | not read | read, after its seeded case | `model-watch`'s first run |
| SPEC/04 §2's second-run rule | no ADR | ADR-0011 | not used yet |

**Controls with no seeded case, added by this repair:**

- **No commit by `agentkeel-upgrades` has been read.** The rule on who
  made a commit takes two committers because which one GitHub writes for
  the App's commit is not known from this tree. A third reads as a
  person's edit.
- **CI's envelope commit is told by a login and by its paths.** GitHub
  does not sign it. A person can push a commit that carries the login;
  it can then touch only envelope files named for the pull request's own
  commits, and a hand-made file there is `two-key`'s to refuse.
- **`bypass_actors` after the restore is shown to neither viewpoint.**
  The App's own pass after the restore, read with its `rulesets` token,
  is what reads it.
- **Who may push to the template repository's default branch** still
  sets what is proposed to every agent. The keyed job now proves the
  proposal is the template's, not that the template is right.
- **The grant file names the ruling that rules it.** A test holds the
  reader to that. Nothing live has refused a draft.
- **ADR-0011's rule is read by no gate.**

**Not in PR 3:** item 13n (the seeded relaxation's step is removed at PR
4, after the attempt); threshold-owner F5 on PR 2 (a swap leaves the old
model's `deprecated_after`), moot while refagent's is null, and
`model-watch`'s paths fixed to M07 (threshold-owner N13): both to M08's
open list at the close.

**After the seat reviews of PR 3** (four reports on `3bfd074...936eb17`;
`milestones/M07/rulings/pr3-engineering.md`, `pr3-security.md` and
`pr3-threshold-owner.md` carry each finding and what was done). Repaired
in code: a restore is a change to the ruleset after the detection, not
after the call; `two-key` reads an unquoted timestamp by its day; the
observer revokes its tokens and sends one only to GitHub's API host; the
`open` job compares text and says so. Still true, and said here so no
document describes these as working:

- **The cost of the row's amendment.** None of PR 3's repairs has run
  live: the artifact's layout, the keyed observer, the rule on who made a
  commit, the retire job's check, the `open` job's check. Each first runs
  during an attempt. A fault one of them shows then has no pull request
  left to repair it in: PR 4 is the close. It is recorded as a finding.
- **A platform role added after an agent's key exists.** A template
  agent's key policy is made with its stack and names the platform's
  roles. No platform role may change a key policy afterwards. So a later
  change to that list changes the policy in the template, CloudFormation
  is refused the change, and that agent's next stack update fails, its
  retirement included. No key exists yet; PR 3's two names land before
  the first. Nothing tests the case.
- **`two-key` reads `deprecated_after` in `agentkeel` only.** An agent
  repository has no `two-key`; a date moved later there takes one commit
  and switches the 30-day check off for that agent.
- **The grant file is tied to its ruling by name.** The reader checks the
  named ruling is Security's and ruled, not that it rules these bytes.
  `ruling-cited` on `/infra/` is what holds a later change.
- **The files that hold PR 3's new checks stay Engineering's**
  (`scripts/platform_upgrade.py`, `scripts/retire_agent.py`,
  `scripts/observe_upgrade.py`, `scripts/platform_pr.py`,
  `scripts/registry.py`, `src/validate/agent.py`). A pull request that
  weakens one meets `cold-review-ruling` and no Security gate.
- **The bundle put under `bundles/` is the artifact's file.** The deploy
  job verifies its own re-pack against the signature and then puts the
  artifact's `bundle.tar`; nothing compares the two digests before the
  put. `image.tar` is carried in the same artifact and is not signed.
- **What is deployed in the security account rests on one person's
  statement.** No role in either account reads that stack back, and no
  hash of the template deployed on 2026-10-02 was kept.
- **The Deny for the two new roles has not fired.** They are named in
  both lists. Neither holds a kms Allow, so a refusal could not be shown
  to be the key policy's.
- **"No role the platform creates"** is still what refagent's key says of
  itself. Its policy names seven roles and the agent path; the Grafana
  connector's, the ingest's and the audit's are not among them.

**To M08's open list at the close, by name:** the six items above that
are not repaired; threshold-owner F2 on PR 2 (item 3's sentence on the
revert's median, restated in ADR-0011 and not in the ruling), its F5 (a
swap leaves the old model's date) and N9 (the manifest's stale judge
comment), N13 (`model-watch`'s paths fixed to M07); item 13n.
