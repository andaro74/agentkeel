---
# M02 PR 3 (#13), Security's key: the ruleset export, the boundary, the
# evals.yml wiring of claim 2's reading, and the removal of infra/eval-role/.
ruling: pr3-security
seat: Security
authorises:
  - infra/ruleset/main.json
  - infra/bootstrap/app.py
  - infra/bootstrap/README.md
  - infra/workflows.sha256
  - infra/eval-role/**
  - .github/workflows/evals.yml
  - .claude/agents/platform-architect.md
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#51-when-each-is-measured
  - milestones/M02/rulings/pr2-security.md
  - milestones/M02/runs/row10_first_deploy.yaml
  - milestones/M02/runs/f2_1_bypass.yaml
  - https://github.com/andaro74/agentkeel/actions/runs/35817173042
  - https://github.com/andaro74/agentkeel/actions/runs/35951008874
pr: 13
---

# Ruling: M02 PR 3, Security (the export, the boundary, the reading's wiring)

Ruled by andaro74 as Security, 2026-09-24.

`ruling-cited` and `two-key` were made required on the live `main`
ruleset after PR 2 merged (the ruleset's `updated_at`
`2026-09-23T05:30:52-07:00`), and the export is `12b4646`, the fifth
commit on the branch after the boundary repair and row 10, committed the
same morning and before any seed PR was opened (13:10Z), which is the
window pr2-security.md item 4 bounded; "first commit" in an earlier
draft of this file was wrong (security-reviewer on PR 3, F5).
`bypass_actors` is `[]`.

## `infra/bootstrap/app.py`: the agent boundary allows `dynamodb:Scan`

The first deploy on which refagent's runtime answered (run 35817173042,
PR 2's merge) refused all fifteen goldens: the construct grants `Scan`
on the rights table (M01 PR 3) and the boundary, the ceiling on every
platform role (R4), listed `GetItem` and `Query` only. One action added
(`c34da39`); the boundary stays an allow list; `cdk diff` is that one
line. `tests/test_bootstrap.py` now holds the construct's grants under
the boundary (`0faf973`, failing first). The human deployed the
bootstrap stack by hand after reading the diff.

This PR's own `ruling-cited` run refused the three paths of that repair
until this file and `pr3.md`, `pr3-engineering.md` named them: the first
refusal of a real pull request by the gate, and on PR 3 itself, not a
seed. The record: `ruling-cited` failure on `12b4646`,
https://github.com/andaro74/agentkeel/actions/runs/35861180683/job/107181506184,
and success on `89819e2`, the commit that added the three files (run
35861631881).

**The redeploy, recorded** (security-reviewer F3, platform-architect F1):
`AgentkeelBootstrap` `UPDATE_COMPLETE`, `LastUpdatedTime`
2026-09-23T04:45:35Z; the stack events of that update name one resource,
`BoundaryEA298153` (`UPDATE_IN_PROGRESS` 04:45:39Z, `UPDATE_COMPLETE`
04:45:57Z). `infra/bootstrap/README.md` carries the same paragraph and
no longer says no agent stack has deployed. The ceiling refusing a call
on run 35817173042 is an unplanned observation of a control SPEC/01 §9
lists as having no seeded case (platform-architect F2): Product records
it against that bullet at M03 PR 1; a seeded case for the ceiling is
M05's, Security.

## `.github/workflows/evals.yml`: the reading (`939709d`)

Three changes to the `evals` job, and none to `checks` or `record`:

1. `permissions` gains `actions: read`. `scripts/observe_pr.py` reads
   the job log of each seed PR's failed check, in which the gate named
   the seed's path; a red check that names no path proves nothing
   (SPEC/02 §4). `checks: read` and `pull-requests: read` were already
   there for the F0.3 observer.
2. One new step on the measuring path, "Look up the seed PRs, the
   owner's attempts and the three doors", runs the observer on the
   three run files with `GITHUB_TOKEN` and hands `make evals`
   `SEED_PRS_OBS`, `BYPASS_OBS` and `DOORS_OBS`. From `74624cb` the gate
   requires `F2_1` and `F2_2` on every agent envelope after `97d3c76`,
   so a later edit that dropped this step makes the run RED, not GREEN
   by omission.
3. The step that holds `RULESET_TOKEN` fetches two more things with the
   same curl: the failed rule-suite evaluations on `main` for the last
   month, and each rule suite the human recorded by id in
   `f2_1_bypass.yaml`. Both go to files under `$RUNNER_TEMP/rule-suites/`
   beside the live ruleset, and the observer reads the files
   (`AGENTKEEL_RULE_SUITES`, `AGENTKEEL_LIVE_RULESET`). The secret is in
   that one step, which runs no code from the PR, as item 2 of
   pr2-security.md required for `validate`; `tests/test_evals_workflow.py`
   holds that no step with the token runs `uv`, `make` or a Python
   script, and that the observer's step carries neither the token nor
   `secrets.`. A read that fails leaves no file, and the observer
   records the source as unreadable, never as absent; `--remove-on-error`
   makes a transfer that drops mid-body leave no file either (N8). The
   live-ruleset read still fails the step; the two new reads warn. When
   both are unreadable, `rule_suite_fail_found` is false and
   `build.check_from_bypass` passes attempt 1 on the human's own output
   alone, the weaker witness SPEC/02 §5.1 names, with the observation
   saying so (`witness`); a run that reads the record and a run that
   could not are told apart in the observation, not in the check (F4).

`infra/workflows.sha256` lists the new hash; the line above it says why.

What this does not change: the `checks` job still carries no secret and
runs on a fork; the reading is still made by the PR's own code, the
header's first gap, M05's.

## `infra/eval-role/` removed (`b7311b3`; row 16, Unsure E)

`AgentkeelM00EvalRole` was `UPDATE_COMPLETE` on 2026-09-22 (PR 2). The
human destroyed it on 2026-09-23; `cloudformation list-stacks` read
`DELETE_COMPLETE` at 13:48:15Z before the directory was removed, and
`AWS_EVAL_ROLE_ARN` names `agentkeel-evals`, a resource of
`AgentkeelBootstrap` (`EvalRole3F02F524`), which `describe-stack-resources`
confirmed. The bootstrap README records the destroy where it asked for
it; `.claude/agents/platform-architect.md` no longer lists the path.
Four past rulings authorise files under the directory and are not
edited; `validate`'s front-matter check reads deleted paths from history
instead (Engineering, `c7a8242`; Product's finding 3 in `pr3.md`).

## The run that read it (security-reviewer F1, PR 13 Unsure F)

Run 35951008874 on `8033c2a`: the token step fetched the live ruleset,
the rule-suites list and suite 4192991324 with no warning; the observer
step wrote the three observations from those files; `build` wrote
`checks.F2_1` pass (both sources) and `checks.F2_2` pass; the gate ruled
GREEN and the `record` job committed the envelope as `905f438`. The run
on that commit (35951237584) gated the recorded envelope GREEN on the
skip path. The wiring has fired in CI.

## Security's items, standing

- The `security-reviewer` report on this PR's diff is in the PR body
  verbatim; its items are triaged in `pr3-cold-review.md`.
- Attempt 1's record in the rule-suites API: read at the attempt, and
  it is there (suite 4192991324, `required_status_checks` fail). Unsure
  B of PR 1 and PR 2 closes yes.
- The `checks` job on the five seed PRs is red on the export line too,
  the window pr2-security.md item 4 accepted; it closes when this PR
  merges. Their `evals` jobs failed at `validate` before any spend.
- The bot exemption reads `%an` (PR 2 cold F4): M05.

## What a reader can run

```
git diff 97d3c76...HEAD -- .github/workflows/evals.yml       # the three changes, nothing else
uv run pytest -q tests/test_evals_workflow.py                # the token reaches no PR code
uv run python -m src.validate                                # workflow-hash ok on the new hash
aws cloudformation list-stacks --region us-west-2 --stack-status-filter DELETE_COMPLETE \
  --query "StackSummaries[?StackName=='AgentkeelM00EvalRole'].DeletionTime"
```
