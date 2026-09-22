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
  - src/manifest/schema.json
  - agents/refagent/manifest.yaml
  - src/verdict/schema.json
  - src/verdict/build.py
  - src/verdict/gate.py
  - src/agent/run.py
  - tests/conftest.py
  - tests/test_build.py
  - tests/test_gate.py
  - tests/test_m01_seeds.py
  - tests/test_adr0007.py
  - scripts/runtime_for_tree.py
  - tests/test_runtime_for_tree.py
  - src/ledger.py
  - scripts/read_back_grants.py
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

**Item 6 of `pr3.md`'s list closed the two routes these ten did not cover.**
The seven cases are below. The claim the file now supports is still exact and
narrow:

> the known ways to make the eval job stop failing on a RED gate, and the
> known ways to make the credential-free job stop running, are each refused.

It is **not** "the job cannot be made to pass a RED envelope". PR 2's cold
review found three checks written narrower than their own titles, all in
this file's ancestry; the line above is written so this one cannot join
them.

## Item 6: the two routes, `tests/test_evals_workflow.py` 10 to 17

| Test | What breaks it |
|---|---|
| `test_every_run_of_the_eval_job_is_either_measured_or_gated` | the `make evals` step's or the recorded-gate step's `if:` changed from exact complements on `measured_at` (`if: false`, a misspelt output); the recorded path no longer running the gate; an `if:` on the step that writes `measured_at` |
| `test_the_makefile_exits_with_the_gates_code` (6) | the rendered recipe turning the gate's 1 or 2 into anything else, in both chain variants |

The Makefile test reads behaviour, not text. `make -n` renders the recipe as
`make evals` would run it; the gate call is swapped for `(exit N)`, and the
line runs in `sh`, as make runs it. It skips where GNU make is absent, and
`ubuntu-latest` has it.

**Broken on purpose, in a worktree at `4095aa4`:**

| Mutation | Result |
|---|---|
| `exit $$code` → `true` | 4 cases fail (codes 1 and 2, both variants) |
| `exit $$code` → `exit 0` | 4 cases fail |
| the `make evals` step's `if:` → `false` | the complement test fails |
| the recorded gate's `if:` output name misspelt | the complement test fails |

**Still not covered:**
- a step added after `make evals` that removes or rewrites the envelope
  before `record` reads it is a different route, and nothing here reads it;
- the complement test holds these two steps, not every step a later edit
  could add;
- a PR that edits a test and the file it guards in one commit still passes
  (M02, `workflow-hash`'s own caveat).

## BLOCK F and item 7: `tests/test_bootstrap.py`, 17 cases to 38

The 21 added hold the grants in `pr3.md`'s BLOCK F section against two
things the tests read rather than remember: the construct's own template,
synthesised in the test, and `deploy.yml`'s own text.

| Test | What breaks it |
|---|---|
| `test_every_resource_type_the_construct_renders_is_one_the_grant_knows` | a resource type added to `GovernedAgent` with no row in the grant table, or a row for one it no longer renders |
| `test_the_execution_role_may_make_what_the_construct_renders` (7) | a create, read or rollback action missing for any one type |
| `test_the_execution_role_may_resolve_the_security_parameters` | a parameter the construct reads outside `/agentkeel/security/`, or `ssm:GetParameters` leaving that path |
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

## B1: ruling d amended — the schema, refagent's manifest, seven tests

Security amended ruling d in `pr3.md`: `ecr.api` and `ecr.dkr` join the
`endpoint_allowlist` enum. This key covers the three files in Engineering's
paths that carry the amendment:
- `src/manifest/schema.json`: the enum goes from 5 names to 7;
- `agents/refagent/manifest.yaml`: lists both;
- `tests/test_construct.py`: refagent's egress count goes from (3, 2) to
  (5, 2).

`tests/test_bootstrap.py`'s parameter test now checks that every SSM
parameter falls under `/agentkeel/security/`, instead of counting to eight.

The seven new tests, and what breaks each:

| Test | What breaks it |
|---|---|
| `test_the_agent_boundary_allows_the_pull_and_no_ecr_write` | the pull missing from the ceiling, or any other `ecr:` action in it |
| `test_the_vpc_has_the_two_endpoints_an_image_pull_needs` | either ECR endpoint gone |
| `test_both_are_published_for_the_construct` | either SSM parameter gone |
| `test_the_s3_endpoint_reaches_outside_the_account_for_the_image_layers_only` | a second unscoped statement, or this one wider than `GetObject` on the layer bucket |
| `test_a_manifest_without_the_image_pull_endpoints_is_refused_at_synth` | the construct's refusal dropped |
| `test_the_role_pulls_its_own_image_read_only` | the pull off this agent's repository, or an ECR write |
| `test_the_role_makes_its_log_group_under_agentcores_prefix_only` | the log-group grant widened |

All seven fail on the tree at `65ba8cc`. The S3, S5, S6 and S8 seed tests are
unchanged, and they still pass.

## ADR-0007: the envelope says where the agent ran (item 4, step 1)

**The code:**
- `schema.json`: an optional `schema_version: 2`. With it, `mode`,
  `runtime_arn`, `region` and `model_version` are required. Without it,
  none of the four may appear.
- `build.py` writes the four as the run reports them. The version comes
  from the manifest's pin (T1).
- `gate.py` refuses:
  - `runtime` without an ARN, or an ARN without `runtime`;
  - a mode that does not fit the envelope's shape;
  - a model, region or version off the pin at the envelope's commit (T3).
- `gate.measured()` adds `mode` for version 2 only.
- `run.py`'s raw file gains `mode`, `runtime_arn` and `bundle`.

**History is untouched.** All 23 envelopes in `evals/history/` are version
1. They still validate and replay, and `make ledger` still matches row 0
byte for byte.

**Tests changed, and why each:**
- `conftest.py`: the agent fixture uses refagent's real pin, not
  `agent-under-test`, which the gate now REJECTs.
- `test_build.py`'s F1.4 test and the S7 seed test build their own raw
  files; both overlay the same pin and mode. S7's seed file is untouched.
  Its `model_id` is Sonnet 5, the model planned when it was planted.
- `test_gate.py`: the ledger-cell literal gains `mode control` and
  `mode runner`.
- `test_adr0007.py`, 15 cases, including two where build writes and the gate
  refuses (P5).

## ADR-0007, step 2: the digest match

**`scripts/runtime_for_tree.py`** decides whether a run measures refagent in
the deployed runtime. It packs `agents/refagent` exactly as `deploy.yml`
does, then reads three things: the stack's `RuntimeArn`, the image digest
the runtime pins, and that image's tags. It writes the ARN only when the
tree's bundle digest is among the tags. It never fails the job. Any miss or
refused call is a reason, printed and written to the job summary.

Run against the account on 2026-09-21, before any deploy: `runner: the
deployed runtime could not be read (... Stack with id agentkeel-refagent does
not exist)`, exit 0. That is the correct answer today.

**Tests:**
- `tests/test_runtime_for_tree.py` (7): the digest equals what
  `python -m src.bundle.pack` prints, which is what `deploy.yml` tags the
  image with; a match, other bytes, and three failed lookups; the output and
  the summary.
- `test_the_runtime_arn_comes_only_from_the_digest_match`, in
  `test_evals_workflow.py`: the match runs before `make evals`, under the
  same condition. It writes to the summary. No other step sets
  `AGENTKEEL_RUNTIME_ARN`.
- `test_the_eval_role_may_read_which_bytes_the_runtime_runs_and_nothing_more`,
  in `test_bootstrap.py`.

**What they cannot say:** that the runtime answers. PR 4's run is where that
is first read.

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
uv run pytest tests/test_evals_workflow.py -q      # 17 passed

# Break it on purpose. Each of these must turn one test red.
# (Restore the file afterwards: `git checkout -- .github/workflows/evals.yml`)
#   - add `continue-on-error: true` to the `make evals` step, or to its job
#   - append `|| true` to that step's command
#   - delete `shell: bash` from it
#   - add `if: false` to the `checks` job
```
