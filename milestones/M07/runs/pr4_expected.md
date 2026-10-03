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

### Started

- Statement on GitHub: `a490d5d`, committed 2026-10-03T01:00:11Z.
- `agentkeel-studio/window-check` created 2026-10-03T01:01:33Z from
  `agent-template` (`main` at `8d2bfb4`); ruleset 24400101 `platform`,
  active; `floresinnovations` invited with write at 01:01:49Z.
