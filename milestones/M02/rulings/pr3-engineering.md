---
# M02 PR 3 (#13), Engineering's key. Security's file is rulings/pr3-security.md,
# Product's rulings/pr3.md. Opened with the boundary test at the start of the
# branch; grew in the PR 3 session with the gate constant, the observer, the
# validate change and their tests. The cold review of this PR is
# rulings/pr3-cold-review.md, which names only itself.
ruling: pr3-engineering
seat: Engineering
authorises:
  - tests/test_bootstrap.py
  - src/validate/codeowners.py
  - src/validate/checks.py
  - src/verdict/gate.py
  - scripts/observe_pr.py
  - tests/conftest.py
  - tests/test_gate.py
  - tests/test_observe_pr.py
  - tests/test_evals_workflow.py
  - tests/test_m02_seeds.py
  - tests/test_validate_m02.py
  - tests/test_validate_rulings_name_deleted_paths.py
  - tests/fixtures/README.md
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#4-falsifiers
  - milestones/M02/rulings/pr2-cold-review.md
  - milestones/M02/runs/row10_first_deploy.yaml
  - https://github.com/andaro74/agentkeel/actions/runs/35817173042
  - https://github.com/andaro74/agentkeel/actions/runs/35874322479
pr: 13
---

# Ruling: M02 PR 3, Engineering (the boundary test; the constant; the observer; validate)

Drafted by the session; the human rules as Engineering before the merge.

## `tests/test_bootstrap.py`

`test_every_action_the_construct_grants_the_agent_role_is_under_the_agent_boundary`:
every action the construct grants the agent role must be in the agent
boundary's allow list. It fails at `0faf973` on `dynamodb:Scan` and
passes at `c34da39`, the commit that adds the action to the boundary.
The first deploy on which the runtime answered (run 35817173042) refused
all fifteen goldens on that action; nothing at synth had compared the
two lists.

```
git checkout 0faf973 && uv run pytest tests/test_bootstrap.py -k under_the_agent_boundary   # fails on dynamodb:Scan
git checkout c34da39 && uv run pytest tests/test_bootstrap.py -k under_the_agent_boundary   # passes
```

## `src/validate/codeowners.py`

The login check reads with the same token order as the ruleset read
(`GITHUB_TOKEN`, then the gh CLI's). Unauthenticated, the users endpoint
allows 60 calls an hour per address; a day of local `make validate`
runs spent them and the check failed 403 on the developer's machine
while CI, which has `GITHUB_TOKEN`, passed (`951d98e`).

## `src/verdict/gate.py`: `CLAIM_2_CHECKS` (`74624cb`)

The first item PR 2's cold review left for PR 3. `CLAIM_2_CHECKS =
("F2_1", "F2_2")` and `M02_PR2_MERGE = 97d3c76…`, #12's merge commit;
`required_checks(commit)` is claim 1's four for that commit and its
ancestors, and those plus claim 2's two for everything else, a commit
git cannot place included, so the gate fails closed as it does on the
cards. `rule` passes it to `judge`; `judge`'s default is still claim
1's, so every direct call in the tests reads as before. A control
envelope may carry no `F2_` check, as it may carry no `F1_` check.

Read now, not later: `12b4646`, `47258f2` and `6daf6c4` are agent
envelopes after the merge that carry `F2_1` alone, and the gate rules
each RED from this commit. `test_the_three_branch_envelopes_before_the_constant_are_red_under_it`
holds it. No Measured cell cites them; `make ledger` prints the latest
envelope's line as RED until this PR's run records one that carries both.
The fixture (`tests/conftest.py`) passes what CI passes from this PR:
the five seed cases in a junit file and the three observations in the
shape `build` reads as a pass. `test_measured_is_what_the_ledger_cell_must_say`
gains `F2_1 pass` and `F2_2 pass` in its expected line, which is what a
cell copied from a PR 3 envelope carries.

## `scripts/observe_pr.py`: the files, and the suite by id (`ab6219d`)

With `AGENTKEEL_RULE_SUITES` set, the rule-suites list is `list.json`
in that directory and the suite the human recorded (`rule_suite:` in
`f2_1_bypass.yaml`) is `<id>.json` there; with `AGENTKEEL_LIVE_RULESET`
set, the live ruleset is that file, the one `validate` reads. The
observation records `source: file` or `api` on each. A file that is set
and missing, empty or not JSON is unreadable, never the API and never
absent. The by-id read is what makes attempt 1's witness durable: the
list is `time_period=month`, and after a month it no longer holds the
suite, but `GET /rulesets/rule-suites/{id}` has no window. `rule_suite_fail_found`
is true on either. The recorded suite must be the actor's, on
`refs/heads/main`, with `result: fail`, and the observation names the
rule that refused (`required_status_checks`). `live_ruleset` refuses a
file whose `id` is not the export's.

The test that read the committed seed and asserted `observed: null`
(`test_observe_bypass_on_the_committed_seed_…`) failed the branch's run
35874322479 once the human filled the file. It reads a copy with
`observed` null now, with `GITHUB_API_URL` pointed at a closed port so a
call fails loudly.

## `tests/test_m02_seeds.py`: S4's marker (`939709d`)

`@pytest.mark.xfail(strict=True)` on `test_s4_the_owner_was_refused`
comes off in the commit that lands its reading, `evals.yml`'s observer
step. The marker refused the filled run file on run 35874322479
(`XPASS(strict)`), which is what strict is for; `tests/fixtures/README.md`
records that all six markers are off as of this PR.

## `src/validate/checks.py`: a ruling glob naming a deleted path (`c7a8242`)

Removing `infra/eval-role/` failed `ruling front matter` on four past
rulings that authorise files there. A past ruling is not edited to keep
a check green. A glob that matches nothing in the tree is now also
matched against every path deleted in HEAD's history (`git log
--diff-filter=D --name-only`, read once and only when needed); a glob
that never named anything is still refused, with a message that says
both. `tests/test_validate_rulings_name_deleted_paths.py` holds both in
a throwaway repository and in this tree.

## Recorded, not done here

- PR 2 cold N3 (`gate.rule` discards `where`) and N7 (`lines_naming`
  strips before the timestamp): unchanged, Engineering, M03 PR 1 with
  the regression bar. Neither turns on a seeded case at M02.
- `check_model_access` (PR 2 threshold N3): not needed at PR 3, the
  runtime answered on `12b4646`'s run; Threshold Owner at M04.

## What a reader can run

```
uv run pytest -q tests/test_gate.py tests/test_observe_pr.py tests/test_evals_workflow.py tests/test_m02_seeds.py tests/test_validate_rulings_name_deleted_paths.py
uv run python -m src.verdict.gate evals/history/6daf6c4f369bea52f80e210b6bf80d3029dc5af1.json   # RED: checks.F2_2 is missing
git show 6daf6c4:tests/test_m02_seeds.py | grep -c xfail                                         # 2 (marker and docstring); 1 at HEAD, the docstring
uv run python -m src.validate                                                                     # 12 ok, eval-role gone
```
