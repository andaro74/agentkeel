# M07 PR 2: what its run is expected to read, stated before the run

Written on 2026-10-02, before the pull request is opened, and pushed
first: the branch `m07-pr2` has no pull request as this is committed, and
`evals.yml` runs on a pull request, so GitHub dates this commit's push
before the run. SPEC/07 §7 asks for it ("PR 2's run, stated before it").

PR 2 is the measure of the seeds PR 1 planted. It measures nothing live:
no attempt is made in it, no App is granted anything, and no stack is
deployed by it.

## Expected

| What | Expected |
|---|---|
| `tests/test_m07_seeds.py` | 9 passed, 4 expected failures. The nine are the fixture tests, each passing by its reader. The four are the run-file tests (S0 to S3) |
| `tests/test_m06_seeds.py` | still 1 expected failure, SPEC/06's S3 |
| `checks.F7_0` to `checks.F7_5` | all six `pass`, each from its seed's fixture tests; `F7_5` joined by the run's own count of the surfaces' plants |
| every earlier check (`F0_2` to `F6_4`) | `pass`, as on `0f4b72a` |
| `upgrade.F7_0` | **unread**. Of its four parts, `dispatch` is read and held (S0's second attempt, made 2026-10-02, run 36963543726); `owner_test`, `relaxation` and `timed_run` are unread |
| `upgrade.F7_1`, `F7_2`, `F7_3` | **unread**: no attempt is made |
| `upgrade.F7_4` | **unread**: panel 2 is not deployed, so the workspace has no table to answer from |
| `upgrade.F7_5` | read and held. It has no live half: it is read from this run's own tests |
| `upgrade.surfaces` | `plants_expected` 2, `plants_fired` 2, nothing silent |
| `upgrade.taken` | **0 of 3**: platform, model and retirement each unread |
| `upgrade.app_observation` | null: `observe.yml` has not run, and the read role cannot list `observations/` until the security account's stack is redeployed |
| every `viewpoint` | `anonymous`, or none where nothing was read from GitHub |
| `template` | as on `245eb9b` and `0f4b72a`: `F6_1` unread, `F6_2` held, `F6_3` unread, `F6_4` held; `F6_2` now with `viewpoint: anonymous` and its raw `mergeable_state` |
| refagent | ordinary 9/9, traps 2/2, guardrail 2/3, red team 5/5; golden plants 7/7; `never_passed` 1 (`g-014`); `regressed` 0 |
| `mode` | `runtime`: the diff changes no file of `agents/refagent/` and no row of the rights table, so the deployed runtime still runs this tree's bytes |
| tokens | about 49,000 in all, under the cap of 150,000. No A-vs-A: the pin does not move |
| `p95_ms` | at or under 13,529 ms, which is 2.0 times the incumbent's median of 6,764.5 ms over 16 runtime envelopes |
| the envelope's verdict | **GREEN** |
| `make validate` | 20 checks, all passing |
| `make ledger` | exit 0. Row 7 stays OPEN with an empty Measured cell. Printed "as row M07 reads it", this envelope is RED: five falsifiers unread and `taken 0 of 3`. That is the expected reading of a PR that makes no attempt, not a result about claim 7 |

## What would make this statement wrong

- A fixture test passing for a reason other than its reader, or a
  run-file test passing: a marker is wrong.
- Any `upgrade` reading but `F7_5` read as held, or `taken` above 0:
  the observer or build is reading something that was not made.
- `F6_2` not held. M06 found GitHub's `mergeable_state` depends on who
  asks, and a pull request's own token has read S2 as `unstable` before.
  It read `blocked` on the last two envelopes. If it reads otherwise
  here, that is M06's second finding again, now recorded with its
  viewpoint, and not a change this PR made.
- `mode: runner`. The diff would then have changed what the bundle packs
  to, which it should not.
- **`F4_4` failing on p95.** M07 PR 1's first run did, at 14,281 ms, on a
  diff that changed nothing refagent runs. If this run does, **no second
  run is stated or made**: this diff touches `infra/construct/` (a
  retired agent's stack has no runtime), which is on the list of what
  the agent runs in the rule the Threshold Owner ruled on 2026-10-02
  (SPEC/04 §2). refagent's own synthesised stack is unchanged by it, and
  nothing in this PR deploys. The pull request would then be RED on
  `evals`, and what follows is the Threshold Owner's to rule.

## Added after the seat reviews, still before the pull request exists

The four reports read `a2c5a61...1b376a3`. Their repairs are commits on
this branch before the pull request is opened. Nothing in the table
above changes:

- `upgrade.F7_0`'s `dispatch` part is still expected read and held. It
  is now held on GitHub's own annotation on the `post` job of run
  36963543726 ("is not allowed to deploy to platform-app"), which the
  observer reads, not on the job having no steps.
- The envelope's `upgrade.F7_1.upgrades` entries now carry `deployed_s`,
  null on this run.
- `tests/test_m07_seeds.py` is still 9 passed, 4 expected failures.

Two things are stated now because the reviews found them:

- **`taken` cannot reach 3 as SPEC/07 §2 stands.** CI's own envelope
  commit on the swap pull request is a person's edit by that
  definition. Until Product amends it, the most the close can read is 2
  of 3. This run reads 0 of 3 either way.
- **Which envelope rules if the head moves.** `evals.yml` measures every
  head. If any head of this pull request is RED on `F4_4`, that is the
  finding and it is recorded, whatever a later head reads. A later head
  made for another reason is not the "one second run" of SPEC/04 §2,
  which this diff does not qualify for.

## What this run cannot read

The live grant, the three Apps, the environments' rules, a deploy, an
upgrade, a retirement, a rollback, panel 2's rows. Each is read after PR
2 merges (SPEC/07 §5.1), each stated before and pushed first.
