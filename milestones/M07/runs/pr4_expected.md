# M07 PR 4: each attempt stated before it is made, and what PR 4's run is expected to read

Each section is pushed before the attempt it states (SPEC/06 §2 "stated
before"; `milestones/M06/open.md` row 17). The run that reads them all is
PR 4's, on the close PR, after the last attempt. What the run read is
written beside each statement afterwards, not edited into it.

## Attempt 1: the timed run (SPEC/06's S3; SPEC/07 §5 step 4)

Stated 2026-10-03, before the repository exists. Product ruled the same
day that the owner's test's miss on time does not stop this attempt
(SPEC/07 §12). `milestones/M06/runs/f6_3_quickstart.yaml` names the agent
`window-check` and holds `observed: null` until the attempt is made.

### Who does what

- **andaro74**, the owner, not timed until the first command: creates
  `agentkeel-studio/window-check` from `agentkeel-studio/agent-template`
  (at `a4c3788`), applies the ruleset from `infra/ruleset/agent.post.json`,
  gives `floresinnovations` write. The repository's `created_at` is the
  start of the clock.
- **floresinnovations** (id 336113686), on the fresh Windows profile with
  no AWS credential, follows `docs/developer/quickstart.md` steps 1 to 8
  as written: clone, branch, name the agent `window-check`, open the
  pull request **before** touching seats or goldens, wait for the App's
  failure, fill the seven seats with `andaro74`, write one ordinary and
  one trap golden citing rows and clauses in the repository's own `data/`,
  push, wait for the App's success, merge as a merge commit, watch the
  deploy, find the row in panel 1. The screen is captured throughout
  (Act 1).
- **The platform**, by itself: `platform-check.yml` every five minutes
  posts the App's check on each head; `deploy.yml` every ten minutes
  deploys the merged head, asks the agent its goldens, puts the bundle
  and the answer record in the security account, writes the registry row.
- **Nobody** touches `owner-check`, its pull request 2, the platform's
  workflows or any AWS resource during the run.

### Expected reading, PR 4's run (`template` and `upgrade` on its envelope)

| Reading | Expected |
|---|---|
| `template.F6_1` | read, held: the first pull request's first commit carries the template's seven null seats and no golden; the App (5144253) failed it with reasons naming both `seats assigned...` and `an agent's goldens...`; no faulty commit passed; merged at a head the App passed; the ruleset requires `platform-check` from the App |
| `template.F6_3` | read, held: `created_at`, `merged_at`, `deployed_at` (the deploy run's completion, success), `answered_at` (the answer record, one golden passed) all read; the registry row `window-check` and panel 1's row read; elapsed under `quickstart.max_seconds` 28,800 |
| `template.F6_4` | read, held: panel 1's rows equal the registry's (`refagent`, `owner-check`, `window-check`) |
| `template.F6_2` | as at PR 3: read, not held, "behind" (owner-check #2 is not touched) |
| `upgrade.F7_0.timed_run` | read, held: the timed run's agent listed |
| `upgrade.F7_0.owner_test` | read, not held: "deployed 32260 s after the merge, over upgrade.deploy_max_seconds 3600" (the sentence changes from PR 3's; the miss does not) |
| `upgrade.taken` | 0 of 3 until the later attempts |

Expected elapsed, if nothing fails: under 3,600 s. The App's check comes
within about five minutes of a push; the deploy within about ten minutes
of the merge and takes about seven. The bar is eight hours.

### What makes it a miss, and what is done then

- The first pull request mergeable before the App's failure, or the App
  passing a commit with a null seat or no golden: F6.1 fired. Nothing is
  retried; the run file records it.
- The deploy refused at the runtime again: a third IAM action nobody has
  seen. The stack rolls back; the clock keeps running; the repair is a
  grant, and whether the attempt is continued after it is Product's.
  F6.3 reads elapsed from `created_at` whatever happens in between.
- Over 28,800 s: F6.3 fired. Recorded as the measured value; a second
  timing is a second attempt beside the first and not the measured one.
- The repository deleted or renamed during the run: recorded, never
  replaced.

### What is installed on the profile

The run file asks for this list in a commit pushed before the repository
is created. **It was not**: the repository was created at 01:01:33Z
before the list was sent. The list is added below when it arrives, dated,
and stands as listed after the start. Nothing reads it.

### What happened (written after; the statement above is not edited)

Times are GitHub's and AWS's.

| When (UTC) | What |
|---|---|
| 01:00:11 | statement pushed (`a490d5d`) |
| 01:01:33 | `agentkeel-studio/window-check` created; ruleset 24400101; floresinnovations invited (01:01:49) |
| 01:13:02 | first commit `c83fa6f`, "Name the agent": the manifest also carried a stray `i` at the start of line 2 (the developer's editor), so it was not YAML |
| 01:21:49 | the scheduled check ran (the previous was 00:53:45: GitHub's five-minute schedule skipped 28 minutes); the App failed `c83fa6f` at 01:22:49 with **one** reason, `the agent's name: manifest.yaml: not YAML (ParserError)`. Not the planted fault's two reasons: F6.1 is expected to read **not held** on this commit, "refused, and not for its planted fault" |
| 01:26:06 | second commit `74e7feb`, the stray character removed, seats still null, no golden (Product chose to continue #1 rather than open a second pull request, so that the record keeps the first) |
| 01:34:41 | the owner dispatched `platform-check.yml` from `main` (37086621844) after eight minutes with no scheduled run; the App failed `74e7feb` at 01:35:39 for exactly the two planted reasons: seven seats unassigned, 0 ordinary and 0 trap goldens |
| 01:42:14 | third commit `7e27a03`: seats `andaro74`, `g-001` (ordinary, `r-038`, `ML-2.1`), `g-002` (trap, `r-016`, `HS-2`) |
| 01:43:30 | the owner dispatched the check again; the schedule fired the same minute, the dispatch was cancelled by the concurrency group, and the scheduled run (37087187702) passed `7e27a03` at 01:44:46 |
| 01:47:40 | merged by floresinnovations, merge commit `1c5b6ff` |
| 01:49 | the owner dispatched `deploy.yml` (37087589740): nothing to deploy, the App had not yet checked the merge commit |
| 01:51:45 | the owner dispatched the check (37087696839); the App passed `1c5b6ff` at 01:53:17 |
| 01:54:22 | **scheduled** deploy run 37087860298 started; stack `agentkeel-window-check` created, runtime `agentkeel_window_check-YBt5st7kMX`; `g-001` and `g-002` answered in it, 2 observations, 0 errors, GREEN; `bundles/window-check/1c5b6ff….tar` and `.cosign.json` put, first; the answer record put, first; registry row at **02:01:44**; the run completed 02:01:48 |
| 01:56:03 | the owner's second deploy dispatch (37087964107) found nothing left: already deployed |

Elapsed as the reader will take it: `created_at` 01:01:33 to the last
timed record (the deploy run's completion, 02:01:48) is **3,615 s**,
under 28,800. Panel 1's row is read by the observer at PR 4's run, not
here. The two IAM actions granted on 2026-10-02 were exercised a second
time by this create, and no third was asked for.

The observed entry is in `milestones/M06/runs/f6_3_quickstart.yaml`
(repository, pull request 1, `window-check`, 02:01:44Z); its seed test's
marker is off in the same commit.

### Started

- Statement on GitHub: `a490d5d`, committed 2026-10-03T01:00:11Z.
- `agentkeel-studio/window-check` created 2026-10-03T01:01:33Z from
  `agent-template` (`main` at `8d2bfb4`); ruleset 24400101 `platform`,
  active; `floresinnovations` invited with write at 01:01:49Z.
