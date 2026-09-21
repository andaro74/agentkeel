---
# M01 PR 3 (#9), Engineering's key. Ruling B: one seat per ruling file.
# `pr3.md` is Security's and carries the same `pr`; it rules the workflow,
# the hash list and the ruleset. This file rules the tests that hold them.
#
# Two files rather than one because of PR 2's cold review, finding 10 and
# finding D4: one ruling file with one `seat:` had authorised five seats'
# paths, and the file that owns a path is the one that should key it.
ruling: pr3-engineering
seat: Engineering
authorises:
  - tests/test_evals_workflow.py
  - tests/test_bootstrap.py
  - tests/test_construct.py
  - milestones/M01/rulings/pr3-engineering.md
evidence:
  - milestones/M01/rulings/pr3.md
  - milestones/M01/rulings/pr2-cold-review.md
  - https://github.com/andaro74/agentkeel/actions/runs/35555584127
pr: 9
---

# M01 PR 3 — Engineering's key

## What these tests hold, and what they do not

`tests/test_evals_workflow.py` grew from 6 to 10. The four added ones hold
BLOCK C/B2's repair — that the `checks` job cannot be skipped and cannot
quietly stop failing:

| Test | What breaks it |
|---|---|
| `test_the_credential_free_job_cannot_be_skipped` | an `if:` on the job or on any of its steps |
| `test_the_credential_free_job_asks_for_no_credentials` | `configure-aws-credentials`, `id-token`, or any `secrets.` reference — each would stop it running on a fork, which is the one case it exists for |
| `test_the_credential_free_job_runs_validate_and_pytest` | dropping either command |
| `test_its_pytest_fails_the_job_unlike_the_one_in_evals` | `continue-on-error: true`, which is correct in `evals` and wrong here |

The six that were already there hold B1: the step that runs `make evals`
declares `shell: bash`, neither it nor its job carries `continue-on-error`,
its command does not end in `|| true` or its kin, there is exactly one such
step, the `record` job still refuses a REJECTED envelope, and one test
*runs* both bash invocations rather than asserting the claim from memory.

**Two routes are still not covered, and are item 6 of `pr3.md`'s list.** A
step whose `if:` is edited to something never true is skipped, and a skipped
step fails nothing; these tests do not read the step's `if:`. And the
`Makefile` could lose `exit $code`, which lives in another file. The claim
these ten tests support is exact and narrow:

> the known ways to make the eval job stop failing on a RED gate, and the
> known ways to make the credential-free job stop running, are each refused.

It is **not** "the job cannot be made to pass a RED envelope". PR 2's cold
review found three checks written narrower than their own titles, all in
this file's ancestry; the line above is written so this one cannot join
them.

## BLOCK F and item 7: `tests/test_bootstrap.py`, 17 cases to 38

The 21 added hold the grants in `pr3.md`'s BLOCK F section against two
things the tests read rather than remember: the construct's own template,
synthesised in the test, and `deploy.yml`'s own text.

| Test | What breaks it |
|---|---|
| `test_every_resource_type_the_construct_renders_is_one_the_grant_knows` | a resource type added to `GovernedAgent` with no row in the grant table, or a row for one it no longer renders |
| `test_the_execution_role_may_make_what_the_construct_renders` (7) | a create, read or rollback action missing for any one type |
| `test_the_execution_role_may_resolve_the_security_parameters` | the construct's SSM parameter count changing, or `ssm:GetParameters` leaving `/agentkeel/security/*` |
| `test_the_execution_role_grants_no_service_wildcard_and_no_delete_of_the_table` | any `svc:*`, `DeleteTable`, or a write to the table's items |
| `test_the_execution_role_makes_security_groups_in_the_platform_vpc_only` | the `ec2:Vpc` condition dropped |
| `test_the_execution_role_passes_an_agent_role_to_agentcore_only` | `iam:PassedToService` dropped, or PassRole off the agent path |
| `test_every_iam_write_on_the_execution_role_is_on_the_agent_path` | an IAM write off `/agentkeel/agents/`, or role creation without the boundary condition |
| `test_the_deploy_role_may_do_what_each_step_of_deploy_yml_calls` (5) | a step's action missing |
| `test_the_deploy_role_may_not_delete_or_batch_write` | `ecr:Delete*`, `DeleteItem`, `BatchWriteItem`, a service wildcard |
| `test_the_deploy_role_calls_refagents_runtime_and_no_other` | `InvokeAgentRuntime` widened past `runtime/refagent*` |
| `test_every_stack_deploy_yml_names_is_one_the_deploy_role_may_touch` | any `--stack-name` in a command that `stack/agentkeel-*` does not match, case-sensitively (item 7) |

16 of the 21 fail on the tree before the repair: run in a worktree at
`60fee1a` with this test file copied in. The other 5 pass there too. Three
are ceilings the old grant met by granting nothing. One reads only the
construct. One is `cloudformation deploy`, which the old grant already
covered.

**What they cannot say.** They read the template, not the account. A
grant that the template holds and AWS does not honour for this action on
this resource shape is invisible here. The `simulate-principal-policy`
table and the first deploy are what read that (`pr3.md`). The action lists
per resource type are AWS's published handler permissions
(`aws cloudformation describe-type`, read 2026-09-21), less the calls made
only by features the template does not use. They are copied into the test,
not fetched by it (`security-reviewer` F2). So a change on AWS's side, or a
feature added to the construct, shows up as a failed deploy and not as a
red test until someone re-reads `describe-type`.

## B2: `tests/test_construct.py`, four added

These tests read the rendered template:
- the role's invoke is on the profile's `InferenceProfileArn`, not on an ARN
  built from its name;
- the runtime's `AGENTKEEL_MODEL_PROFILE` is that same ARN;
- the foundation model is reachable only with `bedrock:InferenceProfileArn`
  equal to it;
- no `bedrock:Converse`.

All four fail on the construct at `cb94995`. They cannot say whether Bedrock
honours the grant; only a call from the runtime can.

## One thing a reader should know about these tests

They are invisible from the envelope. `Makefile:41` passes
`--check-junit F0_2 tests.test_f0_2`, so a failure here fails the job
through `evals.yml`'s "Fail if pytest failed" step and through the `checks`
job, but leaves `checks.F0_2` pass and the verdict GREEN. The guard blocks
the merge; it never appears in the ledger row or in `make plants`. That is a
choice, not a defect — said once so that nobody later reads a GREEN envelope
as evidence that this guard held.

## What a reader can run

```bash
uv run pytest tests/test_evals_workflow.py -q      # 10 passed

# Break it on purpose. Each of these must turn one test red.
# (Restore the file afterwards: `git checkout -- .github/workflows/evals.yml`)
#   - add `continue-on-error: true` to the `make evals` step, or to its job
#   - append `|| true` to that step's command
#   - delete `shell: bash` from it
#   - add `if: false` to the `checks` job
```
