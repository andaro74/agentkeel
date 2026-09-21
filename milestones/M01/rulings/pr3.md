---
# M01 PR 3 (#9), the repair PR. Ruling B: one seat per file. This file is
# Security's; `pr3-engineering.md` carries Engineering's key for `tests/**`
# and has the same `pr`. Opened early and grown as PR 3 lands its items,
# rather than written at the end: `cold-review-ruling` is red without it,
# and a check that is red for a whole PR is a check nobody reads.
ruling: pr3
seat: Security
authorises:
  - .github/workflows/evals.yml
  - infra/workflows.sha256
  - infra/ruleset/main.json
  - infra/ruleset/README.md
  - infra/bootstrap/app.py
  - infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv
  - .github/workflows/deploy.yml
  - milestones/M01/rulings/pr3.md
evidence:
  - SPEC/00-overview.md#8-M01
  - milestones/M01/rulings/pr2-cold-review.md
  - https://github.com/andaro74/agentkeel/actions/runs/35555584127
pr: 9
---

# M01 PR 3 — the repair

PR 2's cold review left four BLOCKs. Three were cured inside PR 2 (M00's
precedent). **B2 was carried here**, with BLOCK F's grants, ADR-0007,
BLOCK D's wording and the first real deploy. This file grows as each lands.

## BLOCK C / B2 — a fork PR could merge with nothing run

**The defect.** `.github/workflows/evals.yml` skips the `evals` job on a
fork, because a fork gets no OIDC token and cannot measure anything. That
skip is right. What was wrong is that **GitHub counts a skipped required
check as satisfied**, and `evals` was one of only two required contexts
(`infra/ruleset/main.json`). So a fork pull request could merge into `main`
with no `make validate` and no pytest having run at all.

`security-reviewer` found it independently at PR 2 and named the half
`pr2.md`'s ruling had missed: the ruleset is what turns the skip into a
hole, not the `if:`.

**The repair.** A `checks` job that carries the half needing no credentials
— checkout, install, `make validate`, cosign, pytest. It has no `if:` on the
job or on any step, so it cannot be skipped, and it asks for
`contents: read` and nothing else, so it behaves the same on a fork as
anywhere else.

**pytest now runs twice, and that is a decision rather than an oversight.**
The copy inside `evals` carries `continue-on-error: true` so that a failing
test reaches the envelope as `checks.F0_2 = fail` (SPEC/01 §4). This copy
must do the opposite and fail the pull request. The two answer different
questions — *what did the tree measure* and *may this merge* — so neither
can be dropped for the other. About 40 seconds.

**Proved once before anything was required of it**: run 35555584127 on this
PR, job `checks`, success.

## The ruleset is not changed in this PR's first commit, and that is the point

`infra/ruleset/main.json` is an **export** — a record of what GitHub holds.
Editing it to name `checks` would make it assert a required context that
GitHub does not require, which is the prose-against-reality defect this
milestone has now caught five times.

Applying it live before the job had reported would also have been
dangerous. `bypass_actors` is `[]` and `current_user_can_bypass` is
`never`: a required context that never reports blocks every merge into
`main`, with no one able to override it.

**The order, which is a human step (R1):**

1. push, and let `checks` report green once on this pull request — done,
   run 35555584127;
2. `PUT` the context into the live ruleset — done;
3. re-export, so the file in the tree is a true export again — done,
   `5693447`.

**Splitting the job without step 2 would have left the hole exactly where
it was**, because the required context would still have been the one a
fork skips. Steps 2 and 3 are done: the live ruleset (id 23685206) requires
`checks`, `cold-review-ruling` and `evals`, and `infra/ruleset/main.json`
says the same three. B2 is closed mechanically, not only made available.
What it does not close is below.

## What B2 does not close

- **The check can still be switched off from inside.** A PR with write
  access can edit `evals.yml` and `infra/workflows.sha256` in one commit and
  `workflow-hash` still passes. Self-disclosed in both files; M02.
- **`workflow-hash` hashes workflow text only** — not the `Makefile`, not
  `src/`, not `scripts/`. M02.
- **The envelope the required check reads is written by the PR's own code.**
  M02, as the workflow's own header says.
- **No fork PR has ever been opened against this repo.** R1 is one human.
  The exposure is zero today, which is not the same as a control that has
  fired. **M02 plants the case**; until it does, no prose here calls this
  proven.

## BLOCK F and item 7 — written, not yet deployed

**The defect.** `agentkeel-cfn-exec` could create a role under
`/agentkeel/agents/` and nothing else, and the construct makes a security
group, two egress rules, a table, an inference profile and a runtime. The
deploy role could drive CloudFormation and pass cfn-exec, and could not log
in to ECR, push the image, load the table or call the runtime, all of which
`deploy.yml` does. Item 7 is the same shape: `deploy.yml` described
`AgentkeelBootstrap` with a grant on `stack/agentkeel-*/*`, and IAM ARN
matching is case-sensitive.

**The repair, in `infra/bootstrap/app.py`.** cfn-exec gets one statement
per resource type `GovernedAgent` renders, and nothing for a type it does
not render: security groups only in the platform VPC (`ec2:Vpc`), the table
with no `DeleteTable` (it is RETAIN), `iam:PassRole` on the agent path to
`bedrock-agentcore.amazonaws.com` only, `ssm:GetParameters` on
`/agentkeel/security/*` for the eight parameters CloudFormation resolves, and
AgentCore's network service-linked role by service name. The deploy role gets
what each step of `deploy.yml` calls: `ecr:GetAuthorizationToken`, the push
actions on `repository/agentkeel-*`, `dynamodb:PutItem` and `DescribeTable`
(the loader calls `put_item`, not `BatchWriteItem`), and
`InvokeAgentRuntime` on `runtime/refagent*`. No `ecr:Delete*`, no
`DeleteItem`, no service wildcard on either role.

**Where the action lists come from.** The first draft of cfn-exec's grant was
a reading of what CloudFormation calls, and `security-reviewer` found it
short (F1): a rollback would have left the agent role `DELETE_FAILED`,
because the IAM::Role delete handler calls `ListRolePolicies` and
`ListAttachedRolePolicies`. The lists are now the handler permissions AWS
publishes for each type (`aws cloudformation describe-type`, read
2026-09-21). Calls made only by features the template does not use are
left out: Kinesis streaming, table import, replicas, a customer key, S3
code artifacts and capacity providers.

**Item 7, in `deploy.yml`.** The step builds the execution role's ARN from
its fixed name and `sts get-caller-identity`, which needs no grant, rather
than widening the deploy role to a second stack pattern.
`infra/workflows.sha256` is rewritten.

**What holds it.** `tests/test_bootstrap.py` grew from 17 cases to 38 (Engineering's key,
`pr3-engineering.md`). The grant is tested against the construct's own
template in both directions: a resource type the construct renders with no
grant fails, and so does a grant for a type it no longer renders. 16 of the
new tests fail on the tree before this repair, and all pass after it.

**What has not happened.** None of this is in the account. The bootstrap
stack is redeployed by the human (R1), after reading `cdk diff`, and then
read back with `aws iam simulate-principal-policy`, as ruling j did for the
eval role. The table goes here. `deploy.yml`'s `refuse` job stays until both
are done. A template is what exists today, and a template is not a grant
AWS has honoured.

**Unsure, for the Security seat** (from `security-reviewer` on this diff:
2 BLOCK, 6 FINDING, 7 NOTE; the full report is in the PR body). None of
these is repaired here, because each changes the agent's ceiling or the
construct, not cfn-exec:

1. **B1: the runtime probably cannot pull its image.** Neither the agent
   role nor `agentkeel-boundary` allows `ecr:BatchGetImage`,
   `ecr:GetDownloadUrlForLayer` or `ecr:GetAuthorizationToken`. Adding them
   widens the boundary that seeds S5 and S6 read, so it needs a ruling that
   says both still fire. F6 is the same question on the network side: the
   VPC has no ECR endpoints, and it is not known whether AgentCore pulls
   through it.
2. **B2: the agent cannot call its model.** `governed_agent.py` grants invoke
   on `application-inference-profile/agentkeel-refagent`, but AWS gives an
   application profile a generated id, not its name. The runtime is also
   pointed at the system profile, which the role does not grant. The stack
   would deploy and the load check would fail.
3. **The five `vpc-lattice` actions are on `*`.** They are the Runtime
   create handler's VPC-mode calls, and the handler does not say which
   resources they name.
4. **F3: whether CloudFormation resolves the SSM parameters as cfn-exec or
   as the caller.** If it resolves them as the caller, the change set fails
   cleanly at create, and the deploy role needs `ssm:GetParameters` on
   `/agentkeel/security/*`. The first deploy settles it.
5. **F4: nothing constrains an agent-path role's trust policy.** A template
   merged to `main` could make one that something other than AgentCore can
   assume. The fix is for S5's synth check to also read the principal.

## Still to land in PR 3

| # | Item | Seat |
|---|---|---|
| 1 | ~~The live ruleset `PUT` and re-export~~ — done, `5693447` | Security |
| 2 | **BLOCK F**: grants written (above); redeploy, `simulate-principal-policy` table, then delete `deploy.yml`'s `refuse` job | Security |
| 3 | The first real deploy, and construct tenancy with it: claim 1's second half, the P3 exception named in ledger row 1 | Security |
| 4 | **ADR-0007**: the envelope's mode field, plus region and model version (`schema.json` is `additionalProperties: false`) | Product, with Threshold Owner |
| 5 | **BLOCK D**: SPEC/01 §5's wording for S8 takes the narrowing | Security |
| 6 | The two routes `tests/test_evals_workflow.py` does not cover: a step `if:` edited to never-true, and the `Makefile` losing `exit $code` | Engineering |
| 7 | ~~`deploy.yml:198` reads `--stack-name AgentkeelBootstrap`~~ — written (above); holds once `deploy.yml` runs | Security |

PR 4 must close the milestone. There is no fifth PR; if this list will not
fit, the cut is item 3, and claim 1's second half becomes a stated RED half
at the close rather than a missed one.

## What a reader can run to falsify this PR's own claims

```bash
uv sync --frozen

# The credential-free job exists, cannot be skipped, and asks for nothing.
uv run pytest tests/test_evals_workflow.py -q

# It really is unconditional: no `if:` on the job or any of its steps.
uv run python -c "
import yaml, pathlib
job = yaml.safe_load(pathlib.Path('.github/workflows/evals.yml').read_text())['jobs']['checks']
print('job if:', job.get('if'), '| permissions:', job['permissions'])
print('step ifs:', [s.get('if') for s in job['steps']])"

# The export still says what GitHub holds: checks, cold-review-ruling,
# evals, in both.
grep -o '"required_status_checks":\[[^]]*\]' infra/ruleset/main.json
gh api repos/andaro74/agentkeel/rulesets/23685206 \
  --jq '.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context'
```

The last two commands must agree. If they ever disagree, the export is
prose about a control rather than a record of one.
