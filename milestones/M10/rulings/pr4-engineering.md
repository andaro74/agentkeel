---
# M10 PR 4 (#57), the close. Engineering's key over the two Engineering
# paths this PR touches: the run test's marker in tests/test_m10_seeds.py,
# committed with the owner's observed block so the branch's CI envelope
# reads the run made; and tests/test_containment_stacks.py, following the
# destination policy back to PR 2's (Security's pr4-security.md). The cold
# review of the close is pasted below. Product's file is pr4.md, the Data
# Owner's pr4-data-owner.md, Security's pr4-security.md.
ruling: pr4-engineering
seat: Engineering
authorises:
  - tests/test_m10_seeds.py
  - tests/test_containment_stacks.py
evidence:
  - SPEC/10-public-caller.md#5-the-seeded-cases
  - evals/history/14ab792156f585c9010275e6b6be3f687cee22c6.json
  - https://github.com/andaro74/agentkeel/actions/runs/39143365127
  - milestones/M10/rulings/pr2-engineering.md
  - milestones/M10/rulings/pr3-engineering.md
pr: 57
---

# Ruling: M10 PR 4, Engineering

DRAFT, written by the session on 2026-10-18 for the owner to rule as
Engineering.

## The marker

`test_the_caller_run_was_made` in `tests/test_m10_seeds.py` loses its
`xfail(strict=True)` marker (`14ab792`): the run is made, `observed` is a
mapping in the same commit, and the test passes by its reader, the run
file. The file now shows 10 passed; `--runxfail` has nothing left to show.
The `expected_failure` marker object stays defined, unused, as the other
milestones' seed files leave theirs; the pre-existing `noqa: F401` import
stays. No other line of the test changes.

## The destination test

`tests/test_containment_stacks.py` asserts the destination policy's one
statement by equality (`Sid: ThePlatformAccountsDoorsSubscribe`, the
platform account as principal, `logs:PutSubscriptionFilter`, the one
destination ARN) and, on the real synth, the account and no condition
(`e05095c`, `0ebfdbd`), following `infra/security/app.py` back to PR 2's
policy for the reason Security gives. The test holds the template, not a
seeded case: no refused subscription from another account has been made,
and the comment says "stands", not "held" (security-reviewer N5).

## The envelope's provenance

The owner's `observed` block and the marker were committed and pushed
together, and the PR opened, before any document was written, so the CI
bot's envelope is of a tree whose only difference from `main` is that
commit and the destination policy with its test. `evals.yml` (run
39143365127) ran `scripts/observe_caller.py` twice, as `agentkeel-audit-read`
for the bucket (the five access-log and trail records, the answer record)
and as the eval role for GitHub (`#4` and the manifest at its merge), and
`build` composed `caller` from the file (`looked_up_at` 16:13:11Z); the
gate ruled GREEN on refagent's own run (`plants 7/7`); `record` committed
`evals/history/14ab792….json` as `github-actions[bot]` (`4de0fab`,
16:14:52Z). The `checks` job's pytest passed. Nothing under `src/`,
`scripts/`, `evals/goldens/`, `thresholds.yaml` or `src/baseline/` changed
in PR 4. No later commit of this PR touches a measured path; the fixtures
README under `tests/` was left unchanged for that reason (finding 17).

## Standing, this seat

| From | Item | Disposition |
|---|---|---|
| pr3 H | `time_epoch_ms` carries seconds on an HTTP API; the field keeps its name | Standing. The reader reads either unit by its size; the live lines read as 2026-10-18 on the envelope (the Data Owner's epoch check) |
| pr3 I | The quota test measures the template's rendered length; an intrinsic that renders longer could pass it and be refused | Standing. 1,106 characters of room in the execution role's default policy |
| pr3-engineering N4 | No test reads the observer's time window | Standing |
| pr3-engineering N5 | The action lists are the guide's; a deploy is the only reader of completeness | Standing; the door deployed |
| security-reviewer N4 (this PR) | Neither destination test asserts `RoleArn` is the subscriber role or `TargetArn` the stream | One line each at the next Engineering PR that touches the file; not in a close |
| data-owner D (this PR) | `_step_of`'s fallbacks pair a record to a step by its subject when no request id matches; a line with an unmatched request id and the right subject would hold F10.3 by construction. Not on this evidence: all five live records carried the observer's step | A test at the next Engineering PR: a line whose request id is in no `observed` entry is not held for the step its subject names |
| data-owner C (this PR) | The `PLATFORM` branch in `calls` is reached by a test only; `record()` filters the platform record by its null step first | Recorded; a comment at the next Engineering PR |
| pr2 F | `make plants` reads file presence; the run's marker, now off, was what said the run was not made | Closed by the marker |
| pr2-engineering (its two Unsure) | The observer imports three functions from `src/verdict/caller.py`; the M02 seed test fails on a dirty checkout | Standing, as at PR 2 and PR 3 |
| finding 17 | `tests/fixtures/README.md`'s run rows for M09 and M10 still read `observed: null` | The next Engineering PR; not changed at a close because `tests/` is a measured path and the change would write a second envelope for prose |

## Cold review of the close (verbatim)

@@COLD@@
