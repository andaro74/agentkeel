# SPEC/07 — Upgrade, retire, surfaces

Status: DRAFT · Owner: Product seat · Milestone M07 · Opened at M07 PR 1
(`milestones/M07/rulings/pr1.md`) · Build list: SPEC/00 §8 M07, which is
the ruling for this milestone's build paths (`SPEC/00-overview.md#8-M07`),
as cut in §9 and as amended at this PR (§10) · Reviewed by
`product-spec-reviewer` before anything else in PR 1 was written
(`milestones/M07/feasibility.md` §1) and revised once on the rulings in
§2 of that note.

## 1. The claim

**Claim 7.** An agent takes a platform, model or retirement upgrade
without a workflow edit.

For a director: *a new platform version, a new model, or a retirement
arrives as a PR; the team never edits the pipeline* (SPEC/00 §10.3 row
07).

Threats answered (SPEC/00 §3): model regression or deprecation (M04
showed a swap is tested on its own pull request; M07 shows the pull
request arrives by itself, and that a merged swap can be put back); the
negligent developer (never upgrades; leaves a retired agent answering);
the insider on the platform team (an upgrade arrives as a pull request
the agent's seats can read, not as an edit nobody saw).

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
   person was needed on it to make it green.
4. **Live.** After the merge the deployed runtime runs the bytes the tree
   now gives (`scripts/runtime_for_tree.py`'s match, read for that agent);
   for a retirement the runtime is gone and the registry row says so; for
   a rollback the digest before the swap is live again.

**Three kinds**, one seeded case each (§5):

- **Platform.** The template is re-made from a later `agentkeel` commit
  (§2). Every agent whose `platform_version` is older gets a draft pull
  request from the platform with the platform-owned files at the new
  version. **Major** when the platform check at the new version refuses
  the agent's default-branch head as it stands (its guardrail pin, image
  files or manifest no longer pass), **minor** otherwise; the check at the
  new version says which, and the pull request records it.
- **Model.** `model-watch` (SPEC/04 §9 cut a) polls Bedrock, writes
  `deprecated_after` from `modelLifecycle.endOfLifeTime`, and opens a
  draft pull request moving a pin when the Threshold Owner's list names a
  candidate. Its shadow run is the pull request's own `evals` run, which
  M04's gate rules (F4.1, F4.2, F4.4). A merged swap that is then
  reverted must put the previous digest live (F7.3).
- **Retirement.** An agent is retired when its repository is archived,
  or its pin's `deprecated_after` has passed with no swap merged. The
  platform removes the runtime, archives the signed bundle in the audit
  bucket, and writes `retired_at` on the registry row, which stays. An
  agent with no answer record for 90 days is **flagged** idle on its row
  and nothing more (SPEC/00 §8 M07: "90-day idle flag").

**The measured value for claim 7** is `upgrade.taken`: how many of the
three seeded upgrades arrived as a pull request the platform opened and
went live with no person's edit, **n of 3**, with each one's elapsed
time from the platform's record of the trigger to the record of it live
(§2), every time GitHub's or AWS's. There is no bar on the time; it is
recorded. Row 7 is GREEN only at 3 of 3 with every F7 held and F7.0 read
as held.

## 2. Words used here

- **The platform's version.** The `agentkeel` commit the template was
  last made from (`scripts/make_template.py` prints it), written in the
  template manifest's `platform_version`. At M06's close the template
  (`agentkeel-studio/agent-template`, `a4c3788`) was made from `39031e7`
  and its manifest says `m06`, the tag that commit was closed under. From
  M07 PR 2 `make_template.py` writes the tag when `HEAD` carries one and
  the short commit otherwise, and the template is re-made after each
  `agentkeel` merge that changes a platform-owned file. Re-making the
  template is the owner's push to the template repository (§6; whether
  the platform pushes it itself is a Security ruling, §11).
- **Platform-owned files** in an agent repository: `manifest.yaml`'s
  `platform_version` and `guardrail` (the pin every agent from the
  template carries, `src/validate/agent.py`), `server.py`'s import shim
  and `__init__.py`. Everything else in the repository is the agent's own
  after creation (`agent.py`, `prompt.txt`, `tools/`, `data/`, `goldens/`,
  the other manifest fields). A platform upgrade pull request touches
  platform-owned files only.
- **A workflow edit.** A change to any file under `.github/workflows/`,
  in `agentkeel` or in an agent repository, made to take an upgrade. An
  agent repository has none to edit (SPEC/06 §2: the template ships no
  workflow). In `agentkeel`, `infra/workflows.sha256` is the record: if
  it changes between the trigger and the merge of an upgrade, the upgrade
  needed one.
- **A person's edit.** A commit on an upgrade pull request whose author
  is not the platform's App, or a commit on the default branch between
  the pull request's opening and its merge that touches the same files.
  GitHub's record of each commit's author is what is read.
- **The trigger** and **live**, per kind, every time GitHub's or AWS's:

  | Kind | Trigger (the record) | Live (the record) |
  |---|---|---|
  | platform | the template repository's commit that moved `platform_version` (its `committer.date`) | the deploy run that deployed the merged upgrade, completed (GitHub's `completed_at`); `runtime_for_tree`'s match for that agent |
  | model | `model-watch`'s run that opened the pull request (GitHub's run `created_at`) | the deploy run of the merge, completed; for the rollback, the deploy run of the revert's merge, completed, with the runtime's image digest equal to the tree's at the revert |
  | retirement | GitHub's record that the repository is archived, as first read by the platform's scheduled run (that run's `created_at`); or `deprecated_after`'s date | `DeleteAgentRuntime` in CloudTrail (`eventTime`) and `retired_at` on the registry row |

- **The digest.** The sha256 of the packed bundle archive, which
  `deploy.yml` tags the image with (`src/bundle/pack.py`;
  `scripts/runtime_for_tree.py` steps 1 to 4). "The new digest live"
  (F7.3) means `GetAgentRuntime` names an image whose tags hold the
  swap's digest after the revert's deploy completed.
- **Retired.** The registry row carries `retired_at`; `GetAgentRuntime`
  on the agent's runtime ARN returns `ResourceNotFoundException`; the
  signed bundle archive is under `bundles/<name>/<commit>.tar` in the
  audit bucket (write-once, R5). "Still answers" (F7.2) means an answer
  record for the agent under `envelopes/agents/<name>/` with
  `LastModified` after `retired_at`, or a runtime that still exists an
  hour after it.
- **Panel 2.** The verdict history panel (SPEC/06 §9 cut 1, received
  here): one row per envelope under `evals/history/`, with its commit and
  its verdict, read by Grafana through Athena over the envelopes the
  platform's deploy path puts in the audit bucket, or over `evals/history/`
  as the workspace can reach it (§11). Its query names that source and
  returns the verdict column as stored; a query that computes a verdict
  is refused (S4's reader).
- **The surfaces.** Grafana panels 1 and 2. Panels 3 and 4 are §9's
  second cut. A surface's **plant** is a seeded case under
  `tests/fixtures/m06/s4-panel1/` or `tests/fixtures/m07/`, listed by the
  surfaces' control in `src/verdict/plants.py`, that the surface's reader
  must refuse; `plants_expected` and `plants_fired` for the surfaces are
  counted from those readers' results in the run, as M03's plant rule
  counts golden plants (F7.5).
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
   (`milestones/M07/open.md` rows 2, 20). Read by hand on 2026-10-02
   (`milestones/M07/runs/platform_app_environment.json`): one branch
   policy, `main`. A reading by hand feeds no check.
3. **The observer's reading depends on who asks** (F7.0's input through
   `template`). `evals.yml` runs `scripts/observe_template.py` with
   `agentkeel`'s own `GITHUB_TOKEN`, which has no rights in
   `agentkeel-studio`; the envelope keeps `F6_2`'s verdict and not the raw
   `mergeable_state` or the token (row 3).
4. **Nothing opens an upgrade** (F7.1). No file under `.github/workflows/`
   is named `platform-upgrade` or `model-watch`; `scripts/` has no module
   that computes an agent's upgrade diff; `make upgrade` is not a Makefile
   target. `platform_version` is written once by `make_template.py`
   (`"m06"`, a literal) and read by the manifest schema as a string and by
   nothing else. refagent's `deprecated_after` is null and nothing polls
   Bedrock for it (`src/validate/lifecycle.py` reads the manifest's date
   only).
5. **Nothing retires an agent** (F7.2). `deploy.yml` has no job that
   removes a runtime or a stack; `scripts/registry.py` writes `name`,
   `repository`, `repository_id`, `commit_sha`, `deploy_run_id`,
   `deployed_at` and no `retired_at`; `scripts/platform_check.py`
   `repositories()` skips an archived repository, so an archived agent is
   neither checked nor deployed again, and its runtime keeps answering.
   The audit bucket's prefixes hold `envelopes/`, `AWSLogs/`, `events/`
   and no `bundles/`.
6. **Nothing reads a rollback** (F7.3). `scripts/runtime_for_tree.py`
   matches refagent's runtime to the tree for a pull request's run and
   writes `mode`; nothing compares the runtime's digest with the tree's
   after a merge to `main`, and nothing records a revert as one
   (`milestones/M07/open.md` row 57). SPEC/00 §12 names rollback as "manual
   re-point to the previous digest (M07)".
7. **Panel 2 does not exist, and nothing compares a panel's verdict with
   an envelope** (F7.4). `infra/grafana/panel1.json` has one panel;
   `src/validate/panel.py` reads panel 1's query only;
   `src/verdict/template.py` compares panel 1's names with the registry
   and nothing with `evals/history/`.
8. **The surfaces have no plant list** (F7.5). `src/verdict/plants.py`
   names golden plants by kind and lists seeds by milestone; no control
   there names a surface's plants, so `plants_expected` counts none and a
   surface reader that stops refusing its fixture is noticed by nobody but
   a seed test.

## 4. Falsifiers

| Id | Fires when | What it looks like in the repo |
|---|---|---|
| F7.0 | no agent from the template exists to upgrade (amendment, §10) | `upgrade.F7_0` fired or unread: the owner's test's new head refused for a reason other than the seats and the goldens, its fixed head refused, not merged, not deployed within an hour, not answering, not listed; or `template.F6_1` or `template.F6_3` (SPEC/06's S3, the timed run) unread or not held |
| F7.1 | an upgrade requires a manual edit: no pull request the platform opened arrives for a trigger, or a workflow or a person's commit was needed to merge it (amended wording, §10) | `upgrade.F7_1` fired: S1's trigger with no draft pull request from the App within one schedule period plus an hour; a pull request touching `.github/workflows/`; a commit by a person on it; `infra/workflows.sha256` changed between trigger and merge |
| F7.2 | a retired agent still answers | `upgrade.F7_2` fired: an answer record under `envelopes/agents/<name>/` after `retired_at`; `GetAgentRuntime` still finding the runtime an hour after; the registry row with no `retired_at` an hour after the trigger; no `bundles/<name>/<commit>.tar` |
| F7.3 | a rollback leaves the new digest live | `upgrade.F7_3` fired: after the revert's deploy completed, the runtime's image tags hold the swap's digest, or do not hold the digest the tree gives at the revert's merge |
| F7.4 | a Grafana panel shows GREEN where the envelope says RED (read through Grafana's query API, as F6.4; amended from "Playwright asserts", §10) | S4's fixture passed by its reader (`checks.F7_4: fail` from the seed test); live: panel 2's rows, as `/api/ds/query` returns them, name a commit whose row says GREEN and whose `evals/history/<commit>.json` says RED or UNMEASURED, or a query that computes the verdict |
| F7.5 | `plants_expected ≠ plants_fired` for the surfaces | S5's fixture passed by its reader (`checks.F7_5: fail` from the seed test); live: `upgrade.surfaces.plants_expected` (the surfaces' control's list at the commit) ≠ `plants_fired` (the readers that refused their fixture in the run) |

**Where each reading comes from** (M04's, M05's and M06's lesson, planned
at open).

- **On every agent envelope, from PR 2's merge: `F7_4` and `F7_5`**, from
  S4's and S5's seed tests: their readers refusing their fixtures in a
  copy of the tree. Test-only witnesses, and the ledger says so.
  `CLAIM_7_CHECKS` in the gate is `F7_4`, `F7_5`.
- **F7.0 to F7.3 and the live halves of F7.4 and F7.5 are recorded, not
  gated.** They live in agent repositories, in the organisation, in AWS
  and in Grafana, after PR 2 merges (§5.1). `scripts/observe_upgrade.py`
  (Engineering) writes raw observations only: for each run file under
  `milestones/M07/runs/` with an `observed` entry, what GitHub, AWS and
  Grafana returned, with the time each was read and **the token's
  viewpoint** (anonymous, `GITHUB_TOKEN`, or the App) beside every GitHub
  reading (row 3). `build` rules on them into an optional envelope field
  `upgrade`; the gate rules nothing on it. **Row 7's Measured cell reads
  `upgrade` and `template`**, as row 6's read `template`: anything fired
  or unread makes row 7's cell RED whatever refagent's own verdict.
  `template` keeps reading M06's run files, so SPEC/06's S3 is read by the
  code M06 built (`src/verdict/template.py` `f6_1`, `f6_3`), and the
  owner's test by the same reader pointed at
  `milestones/M07/runs/f7_0_owner_test.yaml`.
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
null`. Each has its test in `tests/test_m07_seeds.py`, marked
`xfail(strict=True, raises=...)` naming the one exception its planted
reason raises, run once with `--runxfail` so the message is read;
preconditions raise `SeedBroken`. Each is named in
`tests/fixtures/README.md` and in `src/verdict/plants.py` as `SEEDS_M07`;
none is copied to `evals/history/`. SPEC/06's S3 is received, not
re-planted: its run file and its test stay where M06 put them.

| Seed | Falsifier | Planted as | Fails today because | Read by (PR 2) |
|---|---|---|---|---|
| S0 the template's repair, read by CI | F7.0 | `runs/f7_0_owner_test.yaml`: the owner's test, steps 2 to 4 again on `owner-check` pull request 1, `observed: null`; and `tests/fixtures/m07/s0-app-token/`: the App's installation as the API returns it (`repositories`, `permissions`) and the environment's branch policies, two files each: one as granted today, one with a grant no ruling covers | the attempt is not made: every head is refused (§3 item 1). `app_token()` accepts no repository (§3 item 2); nothing reads the installation's permissions or the environment back | `scripts/platform_check.py`: `POST_PERMISSIONS` with `administration: write`, `app_token()` refusing a call with no repository, a `permissions` subcommand that records the installation's grant and the environment's branch policy and fails on any change no ruling in `milestones/M07/rulings/` covers; `src/validate/agent.py` failing closed on a hidden field and passing `[]`; the observer reading pull request 1's heads with the App's reasons |
| S1 a platform bump opens a draft pull request | F7.1 | `runs/f7_1_platform_upgrade.yaml`: the re-make of the template after PR 2 merges, and the draft pull requests it must open in `owner-check` and the timed run's repository, `observed: null`; and `tests/fixtures/m07/s1-platform-upgrade/`: an agent folder at `platform_version: m06` beside the platform-owned files at a later version | the attempt is not made: nothing opens one (§3 item 4). No module computes the upgrade diff | `.github/workflows/platform-upgrade.yml` on `main` (Security), scheduled: for each registered agent behind the template's version, a draft pull request as the App with the platform-owned files and the check's verdict at the new version (major or minor) in its body; `scripts/platform_upgrade.py diff` (Engineering), which the seed test calls on the fixture and which must touch no workflow file; the observer reading the pull request |
| S2 a retired agent's target is gone | F7.2 | `runs/f7_2_retire.yaml`: `owner-check` archived by its owner after it has deployed, answered, been listed and taken S1, `observed: null`; and `tests/fixtures/m07/s2-retired-agent/`: a registry row with `retired_at`, a `GetAgentRuntime` answer that still finds the runtime, and an answer record dated after `retired_at` | the attempt is not made (§3 item 5); nothing reads the three records against each other | `deploy.yml`'s `retire` job (Security) from `main`: for a registry row whose repository is archived or whose pin's `deprecated_after` has passed, archive the bundle under `bundles/`, `DeleteAgentRuntime` and destroy the stack, write `retired_at`; the idle flag; `build.f7_2` (Engineering) over the observer's three records |
| S3 a `model-watch` pull request is merged and rolled back | F7.3 | `runs/f7_3_rollback.yaml`: `model-watch` opening a draft swap pull request on refagent, its merge, its revert, `observed: null`; and `tests/fixtures/m07/s3-rollback/`: the tree's digest at a revert beside a `GetAgentRuntime` answer whose image tags hold the swap's digest | the attempt is not made (§3 item 6); nothing compares the two digests after a merge | `.github/workflows/model-watch.yml` on `main` (Security), scheduled: `ListFoundationModels` for each pinned model's lifecycle, `deprecated_after` written from it, a draft pull request as the App when the Threshold Owner's candidate list names a newer or cheaper pin; `scripts/runtime_for_tree.py` reused by the observer after each deploy; `build.f7_3` |
| S4 panel 2 forced to show GREEN on a RED envelope | F7.4 | `tests/fixtures/m07/s4-panel2/`: `dashboard.json`, a panel 2 whose query maps every verdict to GREEN; `frame.json`, panel 2's rows as `/api/ds/query` returns them, GREEN for `133959f`; the envelope `evals/history/133959f….json` on `main`, RED | nothing reads a panel 2 query or compares a panel's verdict with an envelope (§3 item 7) | `validate` refuses a panel 2 query that does anything but select the verdict from its source (`src/validate/panel.py`); `build.panel_verdict_mismatch(frame, history)` compares by commit |
| S5 a surface plant goes silent | F7.5 | `tests/fixtures/m07/s5-silent-surface-plant/`: a surfaces' plant list naming S4 of M06 and S4 of M07, and a panel 2 query that names the right source and still computes GREEN inside a `CASE`, which a reader that checks the source alone passes | nothing counts a surface's plants (§3 item 8); the reader that would pass it does not exist either | the surfaces' control in `src/verdict/plants.py` naming its plants; `build` counting `plants_expected` and `plants_fired` for the surfaces from the readers' results, written to `upgrade.surfaces` and `checks.F7_5` |

S0's two fixture files are the shape of the reads row 2 demands, not the
reads: the live installation is read with the App's JWT, which no test
holds. S0's attempt waits for the grant (§5.1, §6).

### 5.1 When each is measured

**A named P3 exception**, M06's again. The platform check posts from
`agentkeel`'s `main`, the deploy role trusts `main` only, the template is
published from what `main` holds, and `model-watch` and
`platform-upgrade` run from `main`. Nothing live can be read before PR 2
merges, and the grant that lets the App read a ruleset is a GitHub
setting made by hand after a Security ruling.

- **PR 1, the plant.** Seven seed tests expected to fail (S0 three, one
  per bound; S1 to S5 one each). M06's video committed. `legal-compliance`
  written and run once on `data/slate.json`, `data/corpus/` and this
  SPEC's cut list (R8). Row 20's environment read recorded
  (`runs/platform_app_environment.json`). No reader, no grant, no
  attempt.
- **Before PR 2's first commit: the rulings §11 owes**, by the human:
  row 2's bounds (which repositories, which jobs, no `scope = {}`, the
  seeded relaxation attempt, a read path without write, the permissions
  reader), then the grant and the organisation's acceptance; the observer's
  token (row 3); `model-watch`'s token for a pull request in `agentkeel`;
  whether the platform pushes the template.
- **PR 2's run, on the PR.** S0's bounds, S4 and S5 read by their tests
  (test-only witnesses); the permissions reader reading the grant as
  ruled; the environment read with a seeded refusal from a branch
  (`platform-check.yml` dispatched from a branch, its `post` job refused
  by the environment, read by the workflow-run record). `upgrade` on the
  envelope with every live reading unread.
- **After PR 2 merges, in this order, each stated before and pushed:**
  1. the owner's test, steps 2 to 4 on `owner-check` pull request 1
     (S0's attempt), read by the next run;
  2. SPEC/06's S2 read again (`milestones/M06/runs/f6_2_standin.yaml`,
     owner-check pull request 2, head `e3a8083`), with the viewpoint
     recorded; not remade (`milestones/M06/rulings/pr4.md`, Unsure B);
  3. SPEC/06's S3, the timed quickstart, once, by `floresinnovations`,
     Act 1 recorded during it; before it, `f6_3_quickstart.yaml` and
     SPEC/06 §7's "five records" restated (`open.md` rows 4, 31);
  4. the template re-made from PR 2's merge; S1's pull requests arrive in
     `owner-check` and the timed run's repository; each merged by its
     seat when green;
  5. `model-watch`'s pull request on refagent, merged if GREEN, then
     reverted (S3);
  6. `owner-check` archived (S2).
  **PR 3 is the repair** of what PR 2's cold review and these reads find,
  and **PR 4 is the close**, whose run reads every attempt. If a step
  misses, the steps after it are not attempted, and row 7 closes RED at
  PR 4 with the miss as the finding. There is no fifth PR.
- **SPEC/06's S3 is made once** (SPEC/00 §10.5). The second developer's
  one clean attempt is spent only after every precondition above it has
  been read as held and Product agrees (`milestones/M07/open.md` row 4).
- **Act 2** is recorded against M02's pull requests at the close; **Act
  4** against M04's; **Act 6** is §9's third cut.

## 6. The code that reads the answer (PR 2)

None of it is in PR 1. Each with one seat and one path.

- **The grant** (Security; by hand, after the ruling §11 owes): the App
  `agentkeel-platform` (5144253) granted Administration: write on the
  organisation's installation, accepted by the organisation's owner.
  Before it, each bound of `milestones/M07/open.md` row 2 ruled in
  `milestones/M07/rulings/pr2-security.md`.
- **The token** (`scripts/platform_check.py`, Engineering):
  `POST_PERMISSIONS` asks `administration: write`; `app_token()` requires
  a repository and refuses a call without one; the token is minted in the
  `post` job only, per repository, and is never in a job that checks out
  an agent repository or pull-request code; a `permissions` subcommand
  reads the installation (`GET /app/installations/{id}`, `repositories`
  and `permissions`) and the environment's branch policies, and exits 1
  on any value not named by a ruling file under `milestones/M07/rulings/`
  with `authorises: [infra/platform_identity.json]` and a `grant:` block.
  `platform-check.yml` runs it first in `post` (Security).
- **The reader** (`src/validate/agent.py`, Engineering): `ruleset_errors`
  fails closed on a hidden `bypass_actors` (as today) and passes `[]`;
  the test reads both.
- **The seeded relaxation** (Security; `runs/f7_0_owner_test.yaml`'s
  second attempt): the App's token, minted as `post` mints it, asked to
  `PUT` a change to `owner-check`'s ruleset. Expected: refused, if the
  grant can be read-only for rulesets; otherwise accepted, and the next
  platform check refuses every head until the owner restores the export,
  which is detection, not refusal, and is said so. Which it is comes from
  the attempt, not from this text.
- **The observer's token** (Security; row 3): the App's viewpoint for the
  runs on `main`, from a job that runs `main`'s code with the key from
  the `platform-app` environment; the anonymous viewpoint for a pull
  request's run. `scripts/observe_template.py` and `observe_upgrade.py`
  record the viewpoint and the raw `mergeable_state` beside every GitHub
  reading; `build` rules on `blocked` as today and names the viewpoint
  in `template`'s and `upgrade`'s reasons. The App's key never enters a
  job that checks out pull-request code.
- **`platform-upgrade`** (`.github/workflows/platform-upgrade.yml`,
  Security; `scripts/platform_upgrade.py`, Engineering): scheduled on
  `main`; reads the registry and each agent's `platform_version`; for
  each behind the template's, computes the platform-owned files' diff
  from `make_template.py` at the two versions, evaluates the agent's head
  with `src.validate.agent` at `main` to record major or minor, and opens
  one draft pull request as the App in that repository, touching
  platform-owned files only. The App needs `contents: write` and
  `pull_requests: write` on agent repositories for it (Security, §11).
  `make upgrade` runs `platform_upgrade.py diff` locally and opens
  nothing: an upgrade arrives from the platform, not from a laptop.
- **`model-watch`** (`.github/workflows/model-watch.yml`, Security;
  `scripts/model_watch.py`, Engineering): scheduled on `main`; reads
  `modelLifecycle` for refagent's pin and `pinned_roles`
  (`bedrock:GetFoundationModel`, as the eval role); writes
  `deprecated_after` from `endOfLifeTime` into a draft pull request when
  it differs (Threshold Owner's field, ADR-0010: the pull request carries
  the ruling the gate asks for, drafted, for the seat to rule); opens a
  draft swap pull request when `pinned_roles.m07_watch_candidate` (named
  by the Threshold Owner before the run) differs from the pin. Its pull
  request's own `evals` run is the shadow run. A pull request in
  `agentkeel` needs a token the workflow can hold: the App installed on
  `andaro74/agentkeel` too, or a fine-grained token (Security, §11); a
  pull request opened with `GITHUB_TOKEN` starts no workflow.
- **Retirement** (`deploy.yml`'s `retire` job, Security;
  `scripts/registry.py retire`, `scripts/retire_agent.py`, Engineering):
  on the deploy schedule, for each registry row whose repository GitHub
  reports archived, or whose deployed manifest's `deprecated_after` is
  past: copy the signed archive the registry's commit was deployed from to
  `bundles/<name>/<commit>.tar` in the audit bucket (put once,
  If-None-Match), `DeleteAgentRuntime` and the stack's deletion through
  the deploy role, `retired_at` on the row. The idle flag: `idle_since`
  on a row with no answer record for 90 days, read from the bucket.
  refagent is never retired by this path (its repository is `agentkeel`).
- **The rollback reading** (`scripts/runtime_for_tree.py` given an agent
  name, Engineering): after each deploy run `completed`, the observer
  reads the runtime's image tags and the tree's digest at the deployed
  commit; `build.f7_3` compares them for the revert's merge.
- **Panel 2** (`infra/grafana/panel2.json`, Security; the Athena table
  over the envelopes' prefix, `infra/grafana/`): one row per envelope,
  `commit`, `verdict`, `mode`, as stored. Its query check in `validate`
  (`src/validate/panel.py`, Engineering): the source, the columns, no
  expression over `verdict`.
- **The surfaces' plants** (`src/verdict/plants.py`, Engineering): a
  control `surfaces` naming S4 of M06, S4 and S5 of M07 by fixture path
  and reader; `build` counts them from the seed tests' results
  (`JUNIT`, as `F0_2` is read) into `upgrade.surfaces` and `checks.F7_5`.
- **`upgrade`, `CLAIM_7_CHECKS`, row 7's reading** (`src/verdict/`,
  `src/ledger.py`, Engineering; the steps in `evals.yml`, Security):
  `upgrade.F7_0` to `F7_5`, `upgrade.taken`, each with `read`, `held`,
  `reasons`, `viewpoint`; `READ_THE_UPGRADE = {"M07"}`; row 7 reads
  `upgrade` and `template`.
- **The bar.** None added. `quickstart.max_seconds` stays; a two-key test
  on it is owed (`open.md` row 23, Engineering; Threshold Owner).
- **The documents** (Product): `docs/developer/upgrade.md`; the three
  guides if §9 does not cut them. `docs/compliance/map.md` as
  `legal-compliance` drafts it, doc-only if cut.
- **The seats** (Security): none change. `legal-compliance`'s front
  matter names Product; CODEOWNERS gains its line under Product.

## 7. Expected on the plant (row 7)

- **PR 1.** refagent's envelope, gated and recorded as at M06; it says
  nothing about claim 7. `make plants` lists S0, S1, S2, S3, S4 and S5
  (seeds, not golden plants). `uv run pytest tests/test_m07_seeds.py`
  shows seven expected failures. `make validate` passes: nothing reads an
  installation, an upgrade, a retirement, a rollback, panel 2 or a
  surface's plant. `make ledger` exits 0 with row 7 OPEN and its Measured
  cell empty. `uv run pytest tests/test_m06_seeds.py` still shows one
  expected failure, S3's.
- **PR 2's run, stated before it** (pushed first). S0's three bounds read
  by their tests: `app_token()` refusing no repository; the permissions
  reader refusing the fixture with the uncovered grant and passing the one
  as ruled; the environment fixture the same. S4 and S5 refused by their
  readers for their planted reasons. `upgrade` written with `F7_0` to
  `F7_3` unread, `F7_4` and `F7_5` pass from the seed tests,
  `surfaces.plants_expected` 3 and `plants_fired` 3. refagent otherwise
  as at M06: ordinary 9/9, traps 2/2, guardrail 2/3, red team 5/5, golden
  plants 7/7, `template` as at `245eb9b`.
- **PR 4's run, stated before each attempt** (§5.1). The owner's test:
  pull request 1's new head refused by the App on the seats and the
  goldens and nothing else; the fixed head passed; merged; deployed
  within an hour; one answer record; the registry row; panel 1 listing
  `owner-check`. S2 of SPEC/06 as at M06, `blocked` from the App's
  viewpoint. S3 of SPEC/06 under 28,800 s with all four records read.
  S1: one draft pull request from the App in each of the two
  repositories within one schedule period plus an hour of the template's
  commit, touching platform-owned files only, no person's commit, merged
  green, deployed; `taken` 1 of 3. S3: a draft pull request from the App
  on `agentkeel` moving the pin to `m07_watch_candidate`; its envelope
  GREEN and merged, else recorded RED and the rollback unread; the revert
  merged; the runtime's tags holding the tree's digest at the revert and
  not the swap's; `taken` 2 of 3. S2: `retired_at` within an hour of the
  archive being read; `DeleteAgentRuntime` in CloudTrail; the runtime
  gone; the bundle under `bundles/`; no answer record after `retired_at`;
  `taken` 3 of 3.
- **The row goes RED** if F7.0 is unread or fired; if any trigger gets no
  pull request from the platform, or one that needed a workflow or a
  person's commit; if the retired agent answers or its runtime stands; if
  the revert leaves the swap's digest live; if panel 2 shows GREEN on a
  RED envelope or the surfaces' counts differ; if a seed's test passes for
  a reason other than its reader; if PR 4's run cannot read an attempt;
  or if `make ledger` stops matching rows 0 to 6.

## 8. Controls with no seeded case at M07

SPEC/00 §10.5: no document describes these as working.

- **The App's write token relaxing a ruleset.** The seeded attempt (§6)
  reads one call. It does not read the token removing the required check
  bound to 5144253, changing a collaborator, or editing a setting; each
  is possible with Administration: write and is detected only by the
  next platform check, if at all. The permissions reader reads the grant,
  not its use.
- **The platform's pull request merged by the platform.** Every upgrade
  pull request is merged by a seat. Nothing stops an owner merging a
  platform pull request that was edited by hand after it arrived; F7.1
  reads the commits' authors.
- **A platform upgrade that is not in the platform-owned files**: a change
  to `agent.Dockerfile`, the construct or `deploy.yml` reaches every agent
  at its next deploy with no pull request anywhere. That is the platform
  changing under the agent, and no M07 falsifier reads it (SPEC/06 §8:
  "an App result is final for its commit").
- **`model-watch`'s candidate is named by a person.** `ListFoundationModels`
  gives the catalogue; which model is equivalent is the Threshold Owner's
  (SPEC/04 §2). A model changing under an unchanged pin is caught only
  inside one job's A-vs-A.
- **The judge, FRAGILE, the knowledge base, Braintrust, HITL as a Gateway
  tool, `ratings-helper`'s code, k6, the gateway**: §9, §10.
- **Retirement by `deprecated_after`** is read on the deployed manifest's
  date; a Bedrock end-of-life that `model-watch` has not yet written is not
  a retirement. A repository deleted, not archived, leaves a registry row
  whose repository GitHub cannot find: flagged, not retired.
- **The 90-day idle flag** is written and shown; nothing acts on it, and
  no seed can wait 90 days.
- **Panel 2 reads what the workspace can reach.** If the envelopes it
  reads are the audit bucket's, a bucket write by the deploy role is what
  it shows; if `evals/history/`'s, the bot's commits. Neither is the
  envelope the ledger reads unless the comparison says so.
- **Playwright** is not used (§10). Nothing asserts what a person sees
  rendered; the query API is what is read.
- **`agentkeel`'s own required checks are names** (SPEC/06 §8, row 27);
  the reader is the pull request's own code (row 36). Unchanged.
- **What an agent repository's pull requests are not asked** (row 27):
  unchanged; a platform upgrade pull request carries no ruling file.
- Everything `milestones/M07/open.md` carries that §9 and §10 do not
  place: each row has its seat and milestone in
  `milestones/M07/feasibility.md` §6.

## 9. Cut list

In order, if the cap is threatened. The first five are taken at open
(§10): none of them feeds an M07 falsifier, and the cap already holds
S0, SPEC/06's S3 and five seeds. **None cuts S0, SPEC/06's S3 or Act 1,
S1 to S5, their readers, Act 2, or the three rulings §11 owes.**

| # | Item | Goes to | Why |
|---|---|---|---|
| a | The Bedrock Knowledge Base over the production bucket and refagent retrieving from it, with the cached-answer seed, F3.5's second half and `g-014` as a plant (`open.md` rows 32, 45, 48, 49, 50, 51) | **not built in this project**: recorded in SPEC/00 §12 with the finding | Its fifth move. M08 adds no code path, so a cut from M07 is a cut from the project. F3.5's second half was claim 3's and is unmeasured; said so in SPEC/00 §12 |
| b | The judge (Bedrock Evaluations, its rubric, the graded examples, `admitted_false_fails.json`, `model-watch` over it) and FRAGILE (`open.md` rows 52, 63) | **not built in this project**: SPEC/00 §12 | R6's judge of record never lands. "Correct" stays the answer's fields compared by code, tool-grounded (M04 PR 2) |
| c | The Braintrust mirror, its divergence check, redaction (`open.md` row 64) | **not built in this project**: SPEC/00 §12 | Its third move. SPEC/00 §13's row stays as the job it would have had |
| d | Grafana panels 3 and 4 (call graph, containment) | doc-only (SPEC/00 §8 M07 cut 2) | `docs/platform/surfaces.md` says what each would show and from which record |
| e | HITL as a Gateway tool with its own edge, budget and audit; `ratings-helper`'s code; the gateway; Identity-only credentials; the per-agent Budgets filter; the nightly graph diff; k6 (`open.md` rows 53, 54, 59, 60, 61) | **not built in this project**: SPEC/00 §12 | Direct Converse was ruled 2026-09-27; a second agent's code would be measured by no M07 falsifier |
| 1 | The compliance map page | doc-only (SPEC/00 §8 M07 cut 1): `legal-compliance` drafts the rows for M00 to M07's controls with their evidence paths; Product commits what it accepts | SPEC/00 §15 asks the page to link evidence for every control; the rows it can fill at M07 are filled |
| 2 | Act 6 (upgrade and retire) | M08 PR 4 (SPEC/00 §8 M07 cut 3) | A recording; S1 to S3's records stand without it |
| 3 | Act 4 (a model swap) and Act 3 (the reference agent, M06's cut 2) | M08 PR 4 | Recordings against M04's pull requests and refagent; nothing M07 measures reads them |
| 4 | `docs/developer/manifest.md`, `goldens.md`, `edges.md` (M06's cut 3) | M08 PR 4 | Guides; `docs/developer/upgrade.md` stays, since F7.1's pull requests are what it documents |
| 5 | `make upgrade` as a local command | the workflow alone | The pull request arrives from the platform; the local diff is a convenience |

Never cut, and never moved again without a SPEC/00 amendment: S0 and
its three bounds; SPEC/06's S3 with Act 1; S1 to S5 and their readers;
Act 2; the owner's test read by CI; the restatement of
`f6_3_quickstart.yaml` and SPEC/06 §7 before S3.

## 10. Not in M07, and the amendments to SPEC/00 this PR proposes

Each is a change to a claim, a falsifier, a seeded case or a cut, and is
**ruled by the human as Product before any seed is planted**
(`milestones/M07/feasibility.md` §2; `rulings/pr1.md`). None is in force
until ruled.

1. **SPEC/00 §8 M07, seeded cases**: gains **S0, the template's repair
   read by CI through the owner's test**, and receives **SPEC/06's S3**
   (the timed quickstart, with Act 1), both named as never cut. The
   seeded case "platform major bump opens a draft PR" reads **"a platform
   bump opens a draft PR; major when the platform check at the new
   version refuses the agent's head, recorded"**: the bump M07 can make
   inside its cap is the re-make of the template from PR 2's merge, and
   whether that is major is read, not promised.
2. **SPEC/00 §8 M07, falsifiers**: gains **F7.0**, "no agent from the
   template exists to upgrade" (the owner's test's fixed head refused or
   not live, or SPEC/06's S3 unread or over its bar). **F7.1** reads "an
   upgrade requires a manual edit: no pull request the platform opened
   arrives, or a workflow or a person's commit was needed to merge it".
   As written ("a manual workflow edit") it could not fire in an agent
   repository, which has no workflow to edit. **F7.4** reads "(read
   through Grafana's query API, as F6.4)" in place of "(Playwright
   asserts)": Managed Grafana authenticates through Identity Center, which
   a browser under test cannot pass with a service-account token, and the
   query API is the record F6.4 already reads. SPEC/00 §13's Playwright
   row is marked not used.
3. **SPEC/00 §8 M07, cut list**: §9's order, with cuts a to e taken at
   open. A code item cut from M07 is not built in this project (M08 adds
   no code path) and is recorded in SPEC/00 §12, each with the finding of
   how many times it moved. SPEC/00 §15's "at least seven GREEN" and "the
   compliance page links to evidence for every control it names" are not
   amended; whether they can still be met is read at M08.
4. **SPEC/00 §10.5**: "by the author, as the write-only account
   `floresinnovations` (one person, R1), at M07" stands as M06 PR 4 wrote
   it (`open.md` row 7). NOTE 23 of `milestones/M06/feasibility.md`
   extends to S3's attempt at M07: `andaro74` stays on GitHub Pro and
   `floresinnovations` stays as it is until then (`open.md` row 11).
5. **Row 6's claim keeps "governed"** (`open.md` row 8): a claim is not
   rewritten at its close. No M07 prose uses "governed", "secure" or
   "proven" of F6.1 to F6.3, F7.0 to F7.5, or the App's grant.

Also not in M07:

- Any change to `src/baseline/` (ADR-0002), to a bar, or to a golden id.
- The landing zone, SCPs, and `open.md` row 75 (deferred with the landing
  zone; re-ruled at M08 open).
- The rows dated M08 in `milestones/M07/open.md` (34, 68 to 75) stay M08's.

## 11. Read before PR 2

Each read is put to the human with a recommendation and ruled by the
human in the seat named before PR 2's first commit; the outputs of reads
are committed under `milestones/M07/runs/` (M06 PR 4, Unsure E). None is
a code change.

| # | Seat | Read | Then rule |
|---|---|---|---|
| R1 | Security | Row 20: the `platform-app` environment's branch policies (read 2026-10-02: one, `main`, type branch; `runs/platform_app_environment.json`); `platform-check.yml` dispatched from a branch, its `post` job refused by the environment (the seeded refusal) | that the key's environment limits deployments to `main`, read back, before any grant |
| R2 | Security | The installation as the App's JWT returns it: `repository_selection`, `repositories`, `permissions`; GitHub's documentation of which permission shows `bypass_actors` and whether a read-only form exists; which jobs can mint the token | row 2's bounds, one by one; then the grant, and its acceptance by the organisation |
| R3 | Security | Whether the App can be installed on `andaro74/agentkeel` with `contents: write` and `pull_requests: write` for `model-watch`'s pull requests, or a fine-grained token in the `platform-app` environment is the smaller grant; whether a pull request opened by an App installation token starts `evals.yml` | the token `model-watch` and `platform-upgrade` open pull requests with |
| R4 | Security; Engineering | Whether the observer on `main` can run from a job that checks out `main` only, with the key from the environment, inside `evals.yml`, or needs a workflow of its own whose observation `evals.yml`'s run picks up | row 3's design |
| R5 | Security | Whether the platform pushes the re-made template (`contents: write` on `agent-template` only) or the owner does, by hand, as at M06 | who re-makes the template, and when S1's trigger is recorded |
| R6 | Threshold Owner | `ListFoundationModels` and `GetFoundationModel` for refagent's pin and `pinned_roles`, their `modelLifecycle`; the candidate for `m07_watch_candidate` from the models the account can call (`scripts/check_model_access.py`); the cost of a swap run against `cost_cap` | the candidate, named before `model-watch` runs; `open.md` rows 65 to 67 |
| R7 | Security | `DeleteAgentRuntime`'s behaviour on a runtime with an endpoint; what `cdk destroy` through the deploy role needs that it does not have; the KMS key's deletion window | the retirement path's grants, as a diff for the Security seat's PR |
| R8 | Security | Where panel 2 reads envelopes: Athena over the audit bucket's `envelopes/` prefix in the security account (cross-account read for the workspace role), or a copy the deploy path writes in the agent account | panel 2's source |
| R9 | Product | `milestones/M06/runs/f6_3_quickstart.yaml`'s "after M06 PR 3" and "PR 4's run"; SPEC/06 §7's "five records" against four | the restatements, pushed before S3 |
| R10 | Product; Security | Which pull request carries the owner's test at M07: a new head on `owner-check` #1 (the template's content again, then the fix), or a new pull request | S0's run file names it before the attempt |
