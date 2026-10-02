# M07 PR 3: what its run is expected to read, stated before the run

Written on 2026-10-02, before the pull request is opened, and pushed
first: the branch `m07-pr3` has no pull request as this is committed, and
`evals.yml` runs on a pull request, so GitHub dates this commit's push
before the run.

PR 3 is the repair. It makes no attempt. It records one that was made
before it, the owner's test, and this is the first run that can read it.

## Expected

| What | Expected |
|---|---|
| `tests/test_m07_seeds.py` | 9 passed, 4 expected failures (the run-file tests, S0 to S3). S0's run file now holds two entries of three, so its test is still an expected failure |
| `tests/test_m07_two_key_seed.py` | 8 passed, no expected failure: the four seeded cases pass by `two_key.date_relaxation` |
| `tests/test_m06_seeds.py` | still 1 expected failure, SPEC/06's S3 |
| every check, `F0_2` to `F7_5` | `pass`, 25 of them, as on `f57e1a5` |
| `upgrade.F7_0` | **unread as a whole** (`read: false`, `held: null`): `relaxation` and `timed_run` are not made. Its parts: `dispatch` read and held, as before. **`owner_test` read and not held**, with one reason: no deploy and answer record, over `upgrade.deploy_max_seconds` 3600. Not a reason about the seats, the goldens, the fixed head, the merge or the merge commit: GitHub's record holds each of those |
| `upgrade.F7_1`, `F7_2`, `F7_3` | **unread**: no attempt is made |
| `upgrade.F7_4` | **unread**: panel 2's table is not deployed, or is empty |
| `upgrade.F7_5`, `upgrade.surfaces` | read and held; 2 expected, 2 fired |
| `upgrade.taken` | **0 of 3** |
| `upgrade.app_observation` | null, or naming no stored observation: `observe.yml` stops at its first step until the observer App's id is on `main` |
| every `viewpoint` | `anonymous`, or none where nothing was read from GitHub |
| `template` | as on `f57e1a5`: `F6_1` unread, `F6_2` held, `F6_3` unread, `F6_4` held |
| refagent | ordinary 9/9, traps 2/2, guardrail 2/3, red team 5/5; golden plants 7/7; `never_passed` 1 (`g-014`); `regressed` 0 |
| `mode` | `runtime`: the diff changes no file of `agents/refagent/` and no row of the rights table |
| tokens | about 49,000 in all, under the cap of 150,000. No A-vs-A: the pin does not move |
| `p95_ms` | at or under 2.0 times the incumbent's median in `runtime` mode, as the gate computes it (13,529 ms at PR 2) |
| the envelope's verdict | **GREEN** |
| `make validate` | 20 checks, all passing |
| `make ledger` | exit 0. Row 7 stays OPEN, 3 / 4, with an empty Measured cell. Printed "as row M07 reads it", this envelope is RED |
| `ruling-cited`, `two-key` | green: every path has its seat's ruling file with `pr: 40`; no relaxation is in the diff |
| `cold-review-ruling` | **red until the seats rule**: the four ruling files read DRAFT. That is the gate working |

## Stated so that nobody reads it otherwise afterwards

- **If `F4_4` fails on p95, this run is RED and there is no second
  run.** The diff touches `infra/construct/`, and ADR-0011, which this
  pull request carries, allows a second run only on a diff that touches
  nothing the agent runs (threshold-owner F1 on PR 3).
- **`owner_test` read and not held is the expected reading, and it is
  F7.0 firing.** It is not re-made and not restated (Product,
  `rulings/pr3.md`). After the merge the deploy is expected to complete;
  the reading then says "deployed N s after the merge, over
  upgrade.deploy_max_seconds", and stays a miss.
- **A local run read the same thing on 2026-10-02** (`upgrade.owner_test`
  on the observer's GitHub records: read, not held, "no deploy and answer
  record 10306 s after the merge"). A local run is not evidence; it is
  why this statement is not a guess.

## What would make this statement wrong

- `owner_test` unread: the run could not read `agentkeel-studio/owner-check`
  with its own token, or the bucket's answer records. The prose that says
  "F7.0 fired" would then rest on GitHub's record read by hand and on no
  envelope, and the pull request's body says so.
- `owner_test` held: a deploy and an answer record inside the hour. No
  deploy run has succeeded since the merge.
- Any other reason on `owner_test`: the observer or `build` reads the
  attempt otherwise than GitHub's record shows.
- A seed test passing but by its reader, or a run-file test passing.
- `mode: runner`: the deployed runtime no longer runs this tree's bytes.

## Which envelope rules if the head moves

The envelope CI writes for the head it measured. If a commit that
changes a measured path lands after it (the two App ids in
`infra/platform_grant.yaml` do not: `infra/` is not a measured path of
`evals.yml`, and if that is wrong the new run's envelope rules), the
latest envelope of the pull request's head rules, and both stay.
