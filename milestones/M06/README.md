# M06 — Developer template

## Ledger row

Written at M06 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 6 |
|---|---|
| Claim | A developer ships a governed agent from the template in under one day |
| Falsifiers | F6.1 a first pull request in an agent repository is mergeable while a seat is unassigned (not a real GitHub login with access) or its goldens are under the minimum (one ordinary, one trap). F6.2 a pull request in an agent repository merges without the platform's check (a required status check bound to the platform's GitHub App by `integration_id`) having run on it and passed. F6.3 the timed quickstart, from the agent repository's `created_at` to the last of its four records (the first pull request refused then merged, the platform's deploy, the agent's answer to one of its own goldens, the registry and panel 1 listing it), exceeds `quickstart.max_seconds` (28,800 s wall clock, from PR 2), or a record is unread (the measured value for claim 6). F6.4 Grafana panel 1 shows an agent the registry does not. |
| Seeded commit | `672fc1d` (S1a an unassigned seat); `1a576f4` (S1b goldens under the minimum); `0f3b977` (S2 a stand-in for the platform check); `b4eb959` (S3 the timed quickstart); `06c485a` (S4 panel 1 against the registry, two tests, one per reader), each its own commit before any reader (SPEC/06 §5). S2 and S3 are attempts to make, `observed: null`; S1a, S1b and S4 are fixtures |
| Expected gate output | PR 1: refagent's envelope as at M05; it says nothing about claim 6. `make plants` lists S1a, S1b, S2, S3 and S4 (seeded cases, not golden plants); `tests/test_m06_seeds.py` shows 6 expected failures. PR 2, on the PR: S1a, S1b and S4 refused by their readers for their planted reasons (`validate` refuses the null seats, the missing goldens and a panel 1 query with a second source; `build.panel_not_in_registry` finds `ghost-agent`); both manifests' seats assigned. From PR 2's merge the gate requires `F6_1` and `F6_4` on every agent envelope, **from the seed tests alone: test-only witnesses**. F6.1's and F6.4's live halves, F6.2 and F6.3 are **recorded in the envelope's `template` and read by this row's cell, not gated** (SPEC/06 §4, ruled at open): the observer writes raw observations only and `build` rules on them. **A named P3 exception (SPEC/06 §5.1):** the platform check posts from `agentkeel`'s `main`, the deploy role trusts `main` only and the template is published from what PR 2 merges, so after PR 3's merge the owner reads that the template works from a test repository, S2 is attempted, S3 is timed once by the second developer (`floresinnovations`, write only), and **PR 4's run records them** (amended at PR 3: the platform check's ruleset reader refused every agent repository until a repair reached `main`, so the attempts wait for PR 3's merge); PR 3 is the repair and cannot be skipped, and PR 4 is that read and the close. Stated before, and pushed before each attempt: the first pull request not mergeable on its planted reasons; S2 not mergeable, the stand-in's check run a success on its head and none from the App (amended at PR 2: the App reaches S2 too, so S2 carries one null seat); S3 under 28,800 s with all four records read; panel 1's rows equal to the registry's. refagent otherwise as at M05: ordinary 9/9, traps 2/2, guardrail 2/3, red team 5/5, golden plants 7/7. RED if a first pull request is mergeable with a seat unassigned or goldens under the minimum; if S2 can merge; if S3 is over the bar or a record is unread; if panel 1 shows an agent the registry does not; if a seed's test passes but by its reader; if PR 4's run cannot read S2 and S3; or if `make ledger` stops matching rows 0 to 5 |
| Measured | agent: traps 2/2 (g-010, g-011); ordinary 9/9; guardrail 2/3; redteam 5/5; control: traps 0/2; ordinary 0/9; guardrail 0/3; redteam 0/5; mode runtime; never_passed 1; regressed 0; plants 7/7; F0_2 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F0_3 pass https://github.com/andaro74/agentkeel/actions/runs/35401176820/job/105781176255; F1_1 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F1_2 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F1_3 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F1_4 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F2_1 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F2_2 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F3_1 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F3_2 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F3_3 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F3_5 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F3_6 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F4_1 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F4_2 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F4_4 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F5_1 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F6_1 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F6_4 pass https://github.com/andaro74/agentkeel/actions/runs/36886530498; F6_1 unread; F6_2 held; F6_3 unread; F6_4 held; F6_1 unread: unread: no S3 observation or no platform App id; F6_3 unread: unread: no S3 observation; RED; envelope `245eb9baf796cd9ceed652abe3805825208358c9`; base b0219756 |
| PRs used / cap | 4 / 4 |
| State | RED |

### Open detail (PR 1, 2026-09-30)

- **Opened through `/open-milestone`.** SPEC/06 was written first
  (`69721b6`) and `product-spec-reviewer` run on it (3 BLOCK, 16 FINDING,
  4 NOTE), pasted verbatim in `feasibility.md` §1. The human ruled every
  item before any seed, BLOCK 1 as option (d) after two reads of GitHub's
  documentation and the rest "as proposed", and SPEC/06 was revised once
  on the rulings (`b0aefa1`, before the first seed `672fc1d`).
- **BLOCK 1 changed what "required workflow" means here.** GitHub
  documents the organisation ruleset's `workflows` rule for Enterprise
  Cloud only (read 2026-09-30); the account has no organisation, and the
  human ruled against a paid plan. The platform check is a required status
  check bound to a GitHub App the platform owns (`integration_id`), posted
  from `agentkeel`'s `main`: a job of the same name in a pull request's own
  workflow does not satisfy it (BLOCK 2's attack, S2). The documentation,
  not an attempt: the first ruleset was read back at PR 3, and differed
  from the export (the PR 3 detail).
- **M01's, M03's, M04's and M05's P3 exception again.** The platform check,
  the deploy role and the template all run from `main`, so S2 and S3 are
  made after PR 3 merges and read by PR 4's run (amended at PR 3: the
  ruleset reader's repair had to reach `main` first). PR 3 is the repair
  and cannot be skipped.
- **M05's lesson, planned at open.** The live readings are recorded in the
  envelope's `template` and read by row 6's cell; they gate no pull
  request. `F6_1` and `F6_4` on every envelope come from the seed tests, as
  test-only witnesses. The observer writes raw lists; `build` compares
  (BLOCK 3).
- **Planted** in five commits, one per seed, `672fc1d` to `06c485a`, each
  with its test in `tests/test_m06_seeds.py`, before any code that reads
  them: 6 expected failures (S4 has one test per reader), each run once
  with `--runxfail` and its message read (`feasibility.md` §3). S1 was split
  in two so a reader that catches one fault cannot pass the other (finding
  10).
- **What is live today, in the repo:** no template and no organisation;
  required checks that are names any workflow can answer to; every seat in
  both manifests null with `validate` green; one folder of goldens, all
  refagent's; a deploy role, an eval role and a `verify` that trust one
  repository; no registry, no Grafana, no quickstart.
- **The second developer** is the author as `floresinnovations` (id
  336113686), write only, on a fresh Windows profile with no AWS
  credentials; set up and ruled at open (`feasibility.md` §2, NOTE 23), with
  `andaro74` on GitHub Pro so that the author holds one free account.
- **Moved at open** by SPEC/00 amendment, not cut: the knowledge base, with
  the cached-answer seed, F3.5's second half and `g-014`, to M07, **its
  fourth move, a finding**; FRAGILE to M07. SPEC/00 R1, §6 (seats to GitHub
  logins), §8 M06 and M07 and §10.3 row 06 are amended.
- **Also in this PR:** M05's video (`open.md` row 1, `eb5dcec`); rows 2, 3,
  17 and 48 ruled at open (`runs/security_account.md`, `rulings/pr1.md`);
  every `open.md` row placed in `feasibility.md` §6.

### PR 2 detail (the measure, 2026-09-30)

- **The reads SPEC/06 §11 owed, then the rulings** (`feasibility.md` §8,
  R1 to R9), before the first commit (`86eb01a`): Managed Grafana over
  Athena (Identity Center was already on in the agent account); the
  platform check from `agentkeel`'s `main` on a schedule, with nothing to
  forge; `agentkeel`'s own deploy for every agent, so no trust widened.
- **The readers, each marker off in its own commit:** S1a (`4d961cd`,
  after the seats in `1dc781b`), S1b (`95e3824`), S4's query (`2a9e793`,
  after `panel1.json` in `9eff4bc`), S4's comparison (`6435f5c`). Cold
  review F4's cross-assertions land with S1a's and S1b's; F2's reader
  field with S4's. `F6_1` and `F6_4` from the seed tests, required from
  `c2a15d0`; `template` and row 6's reading of it in the same commit.
- **Built for PR 3's read:** the observer, `build answer`, the platform
  check (`platform-check.yml`, `src/validate/agent.py`,
  `scripts/platform_check.py`), the agent deploy (`deploy.yml`'s three new
  jobs, `infra/construct/agent.Dockerfile`, `scripts/registry.py`), the
  bootstrap's registry and image template, the security account's answer
  role and tag-keyed prefix, the Grafana stack, the template's source
  (`scripts/make_template.py`), the quickstart and `docs/refagent/`.
- **Changed from the plan, and said so:** S2 carries one null seat (the
  App reaches it too); a seat needs admin; template images are
  `agentkeel/<name>`; F6.3 times GitHub's and AWS's records only, and reads
  the registry row and panel 1's row untimed; cut 3 taken.
- **Reviewed:** five seat reports and two cold reads, every BLOCK and
  FINDING repaired in this PR or named in SPEC/06 §8 (`rulings/pr2-*.md`).
- **Still the human's, during this PR, before the merge:** the
  organisation, the App and its key, `platform_identity.json` and
  `agent.json` filled with them, the `platform-app` environment, the
  bootstrap, security and Grafana deploys after reading each `cdk diff`,
  the workspace and its data source, and the repository variables. After
  the merge: the template from `scripts/make_template.py`, the owner's
  test repository, then S2, then S3, read by PR 4's run (amended at PR 3).

### PR 3 detail (the repair, 2026-10-01)

- **After PR 2's merge (`39031e7`):** refagent redeployed with its role
  tag and wrote the registry's first row (deploy run 36860365548); panel 1
  listed it; the template `agentkeel-studio/agent-template` was made from
  `39031e7` (`a4c3788`). The App's first live check, on the template's own
  `main` before it was marked a template, refused its null seats, its
  missing goldens and its missing ruleset, from app 5144253.
- **The finding:** the owner's test repository (`f6_0_owner_test.yaml`,
  pushed at 12:57:19Z before the repository's `created_at`, 13:05:37Z) had
  its ruleset applied from `infra/ruleset/agent.json`, and read back it
  differed: GitHub adds `dismissal_restriction` and
  `require_extra_approval_for_unattributed_changes` to an organisation
  repository's pull request rule. The App compares exactly, so it would
  have refused every head of every agent repository. Found before the
  first pull request, so no attempt was spent on it.
- **The repair** (`fcc7187`): the export in GitHub's form, and a test that
  holds it equal to the live ruleset as read.
- **Row 6 amended (Product):** the platform check runs from `main`, so the
  owner's test, S2 and S3 are made after PR 3 merges and read by PR 4's
  run, the close. A miss there is a RED close with the finding.


### Close detail (PR 4, the close, 2026-10-01)

**Row 6 is RED.** The cap was four and four were used. `F6_1` and `F6_3`
are unread: S3 was not attempted. The reason is finding 1, below. Product
ruled option 1 on 2026-10-01: M06 closes RED at PR 4, and
`floresinnovations`' one clean attempt at S3 is kept for M07.

**The measurement.** The Measured cell is copied from `make ledger`'s "as
row M06 reads it" line for the envelope for
`245eb9baf796cd9ceed652abe3805825208358c9`, written by CI run 36886530498
and committed by `github-actions[bot]` (`3ca05dd`). That is PR 4's first
run, on the commit that recorded S2 and stated its reading before the run.
`make ledger` exits 0 against it. As numbers: refagent GREEN in
`mode: runtime`, ordinary 9/9, traps 2/2, guardrail 2/3, red team 5/5;
plants 7/7; `regressed` 0; `never_passed` 1 (`g-014`); every check passes,
`F6_1` and `F6_4` among them (from the seed tests, test-only witnesses);
p95 12,277 ms. `template`, looked up at 15:48:23Z:

| Falsifier | Read | Held | Why |
|---|---|---|---|
| F6.1 (live half) | no | — | no S3 observation |
| F6.2 | yes | yes, no reasons | owner-check #2 not mergeable ("blocked", the only state `template.py` holds on); the stand-in's `platform-check` a success (github-actions, app 15368, 15:23:10Z); the App's a failure (app 5144253, 15:24:56Z); the required check bound to 5144253 |
| F6.3 | no | — | no S3 observation; no elapsed time |
| F6.4 (live half) | yes | yes | panel 1's rows equal the registry's: refagent |

**The owner's test** (`runs/f6_0_owner_test.yaml`), S3's precondition and
not evidence for the cell. Step 1 missed at PR 3 (the ruleset as made
differed from PR 2's export; repaired in PR 3). **Step 2 missed at PR 4.**
owner-check #1 (head `0c596c1`, the manifest's name only) was failed by the
App at 14:24:31Z on the seats and the goldens, as expected, and on a third
reason step 2 excludes: "ruleset 24310403's bypass_actors is not shown to
the App's token". Steps 3 and 4 were never possible. #1 is left open.

**Finding 1, the RED.** GitHub returns a ruleset's `bypass_actors` only to
a caller that can administer it. The App has Administration: read and
`scripts/platform_check.py` asks for read (`POST_PERMISSIONS`), so
`src/validate/agent.py` reads the field as missing and refuses every head
of every agent repository, a fixed one too. The repair is the App granted
Administration: write (a Security ruling and a GitHub settings change)
with the token and reader changed to match: `milestones/M07/open.md` row 2.
It is reading machinery, so not in PR 4.

**S2**, made by `floresinnovations` (write only, browser only) as
owner-check #2: branch `s2-standin` from `main` (`68df4b5`), one commit
`e3a8083` adding `.github/workflows/standin.yml`, opened 15:22:53Z, seen by
the owner at 15:25Z. Recorded in `runs/f6_2_standin.yaml` and pushed
(`245eb9b`) before the run. The run file said "sets one seat to null"; the
branch came from `main`, where all seven seats were already null, so S2
set none. F6.2 held, but the App's failure carried the reason that refuses
every head. So it shows that a stand-in's success does not satisfy a check
bound to the App. It does not show the App refusing S2 for S2's own fault
(`milestones/M07/open.md` row 5). S2's test now passes because the run file
is filled; that is not F6.2 (`rulings/pr1-engineering.md` NOTE 1). #2 is
left open.

**Finding 2, and a statement that was wrong.** Read without a token, #2's
`mergeable_state` was "unstable" at 15:40Z; with the owner's token,
"blocked". `evals.yml`'s observer reads with agentkeel's own
`GITHUB_TOKEN`, which has no rights in `agentkeel-studio`. So the run file
stated, before the run, that it would read "unstable" and that F6.2 would
read as not held. **It read "blocked", and F6.2 held.** The statement was
wrong. Product ruled (a) on 2026-10-01: no reader changes in PR 4. What
GitHub says here depends on the token, and the envelope keeps the ruling
but not the raw state or the token. Carried as `milestones/M07/open.md`
row 3.

**Row 6's RED conditions, each checked at the close:** a first pull
request mergeable with a seat unassigned or goldens under the minimum
(none was: #1 and #2 are blocked; live F6.1 unread); S2 can merge (no:
F6.2 held); S3 over the bar or a record unread (**fires**: S3 not
attempted, `F6_3` unread); panel 1 showing an agent the registry does not
(no: `F6_4` held); a seed's test passing but by its reader
(`uv run pytest tests/test_m06_seeds.py`, 7 passed and 1 xfailed, S3's;
S2's marker came off when its run file was filled, `245eb9b`); PR 4's run
unable to read S2 and S3 (**fires** for S3: nothing to read); `make ledger`
matching rows 0 to 5 (holds).

**Also at the close.** SPEC/00 amended (§8 M06, §10.1 cut 3, §10.2 Acts 1
to 3, §10.5): S3 and Acts 1 and 2 move to M07, not cut. Act 2 was due at
this close and was not recorded: a finding (`milestones/M07/open.md` row
30). Cuts 1 and 2 (panel 2, Act 3) were taken. SPEC/00 §10.5's "by the
author" and row 6's `floresinnovations` are one person; §10.5 now says
both. Row 6's claim keeps its wording, "governed agent"; the close does not
repeat the word (`milestones/M07/open.md` row 8).

**Findings and Unsure items.** Every one is closed in M06 or carried to
`milestones/M07/open.md` with a seat and a milestone, 75 rows
(`rulings/pr4.md`). No video was recorded during M06; none is committed
here and no row is written in `docs/video/README.md`.

**After the merge:** `git tag m06` on `main`, by the human; the M06 video
recorded at the tag and committed in M07 PR 1 (`milestones/M07/open.md`
row 1).
