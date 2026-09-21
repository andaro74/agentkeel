---
# M01 PR 2 (#8), the measurement. Ruling B: one seat per file; the seat
# per path is named in the body. The Threshold Owner re-rules the cap and
# refagent's model version against this PR's first agent envelope, in
# rulings/pr2-threshold-owner.md, which carries the same `pr`.
ruling: pr2
seat: Product
authorises:
  # Product
  - SPEC/00-overview.md
  - SPEC/01-signed-bundle.md
  - docs/adr/ADR-0006-gateway-endpoints-for-s3-and-dynamodb.md
  - milestones/README.md
  - milestones/M01/README.md
  - milestones/M01/feasibility.md
  # The explainer's draft. "What happened" stays empty until the close.
  - docs/milestones/M01.md
  - milestones/M01/pr2-body-draft.md
  - milestones/M01/rulings/pr2.md
  - milestones/M01/runs/f1_1_laptop.yaml
  - milestones/M01/runs/f1_3_key_policy.yaml
  # Security
  - .github/workflows/deploy.yml
  - .github/workflows/evals.yml
  - .github/workflows/sign-fixture.yml
  - infra/bootstrap/app.py
  - infra/bootstrap/README.md
  - infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv
  - infra/construct/__init__.py
  - infra/construct/governed_agent.py
  - infra/construct/app.py
  - infra/construct/cdk.json
  - infra/construct/AwsSolutions--AgentkeelRefagent-NagReport.csv
  - infra/bootstrap/cdk.json
  - infra/ruleset/main.json
  - infra/ruleset/README.md
  - infra/workflows.sha256
  # Tool Owner
  - agents/refagent/tools/check_availability.json
  # Threshold Owner and Tool Owner, in one file, one field at a time
  # (ADR-0003 amendment 1). The model fields are re-ruled in
  # pr2-threshold-owner.md against this PR's first agent envelope.
  - agents/refagent/manifest.yaml
  # Engineering
  - .gitignore
  - uv.lock
  - Makefile
  - pyproject.toml
  - agents/__init__.py
  - agents/refagent/__init__.py
  - agents/refagent/agent.py
  - agents/refagent/server.py
  - agents/refagent/prompt.txt
  - agents/refagent/Dockerfile
  - scripts/load_rights_table.py
  - scripts/observe_attempt.py
  - src/cost_cap.py
  # CI-written, never by hand (SPEC/00 §5). Listed because this PR's diff
  # carries them, not because anything here authorises writing one.
  - evals/history/**
  # Security. The M00 eval role was redeployed for Sonnet 4.6 (ruling j)
  # before it was absorbed; both files change in this PR.
  - infra/eval-role/app.py
  - infra/eval-role/README.md
  - src/agent/**
  - src/bundle/**
  - src/manifest/**
  - src/validate/checks.py
  - src/verdict/build.py
  - src/verdict/gate.py
  - tests/**
evidence:
  - SPEC/00-overview.md#8-M01
  - SPEC/01-signed-bundle.md
  - milestones/M01/feasibility.md
  - docs/adr/ADR-0006-gateway-endpoints-for-s3-and-dynamodb.md
pr: 8
---

# M01 PR 2 — the measurement

This is the PR that reads the plants (P3). Row 1 is decided by the CI run
on the head that merges; earlier runs on this branch are recorded and not
cited (PR 2 mechanics, `feasibility.md` §2.6).

## The seat for each group

| Paths | Seat | What authorises them |
|---|---|---|
| `SPEC/**`, `milestones/**`, `docs/adr/ADR-0006` | Product | `SPEC/00-overview.md#8-M01`; ADR-0006 is Security's rule and Product's folder |
| `.github/workflows/**`, `infra/**` | Security | `SPEC/00-overview.md#8-M01`, SPEC/01 §6, `feasibility.md` §2.6 a, b, d, e, f, g, k, n, q, r |
| `agents/refagent/tools/check_availability.json` | Tool Owner | SPEC/01 §6 (`check_availability` with a strict schema both ways), ruling SCOPE |
| `src/**`, `scripts/**`, `tests/**`, `Makefile`, `pyproject.toml`, `.gitignore`, `agents/refagent/**` but for the rows above | Engineering | `SPEC/00-overview.md#8-M01`, `feasibility.md` §2.6 l, m |

`agents/refagent/manifest.yaml` is changed in this PR, and each field it
gains has its own seat (ADR-0003 amendment 1): `endpoint_allowlist` and
`seats` are Security's (ruling d), `may_call`, `may_be_called_by` and
`ceilings` the Tool Owner's, `max_tokens_per_session` and `daily_usd` the
Threshold Owner's. The model id, version and region do not move; they are
re-ruled with the cap (rulings o and p) in `pr2-threshold-owner.md`.

S4 and S6 fail on this head, and that is the row RED for the stated
reason: the attempts have not been made. Their markers are off because
their reader — `scripts/observe_attempt.py` and `--check-attempt` — landed
in this PR, which is the rule (a marker comes off in the commit that lands
the reader). Leaving `xfail(strict=True)` on would have failed the
measuring run the moment the human recorded the attempts.

## What went in, and what reads what

| Seed | Planted | Read by | State at this PR |
|---|---|---|---|
| S1 | `tests/fixtures/bundles/unsigned/` | `src/bundle/verify.py` | marker off; refused for its missing signature |
| S2 | `tests/fixtures/bundles/altered/` | `src/bundle/verify.py` | marker off; refused for its digest |
| S3 | `tests/fixtures/construct/extra_egress*.py` | the stack validation in `infra/construct/` | marker off; both forms refused at synth |
| S4 | `milestones/M01/runs/f1_1_laptop.yaml` | the deploy role's trust policy, read through CloudTrail | marker off; **failing**, because the attempt has not been made |
| S5 | `tests/fixtures/construct/role_without_boundary.py` | the stack validation | marker off; refused at synth |
| S6 | `milestones/M01/runs/f1_3_key_policy.yaml` | the key policy, read through CloudTrail | marker off; **failing**, because the attempt has not been made |
| S7 | `tests/fixtures/refagent_raw_uncited.json` | `verdict.build` and `verdict.gate` | marker came off at PR 1 |
| S8 | `tests/fixtures/construct/outside_construct.py` | the stack validation | marker off; refused at synth |

## ADR-0006

SPEC/00 §8 M01 said "VPC with interface endpoints only". S3 and DynamoDB
are reached from a VPC through gateway endpoints, which have no security
group. The rule is amended, and the difference is carried into the
construct: three egress rules to security groups, two to prefix lists, and
the S3 check accepts both shapes and nothing else.

## What the cold review found, and what was done

Five seats read this PR before it was undrafted: `security-reviewer`,
`platform-architect` (on S3, S5 and S8), `threshold-owner`, `tool-owner`
and `engineering-cold-reviewer`. Every report is in the PR body verbatim.
Counts: 6 BLOCK, 39 FINDING, 43 NOTE. Two BLOCKs are ruled here (B, repaired; E, ruled in `pr2-threshold-owner.md`); three stand.

**Repaired in this PR.** Each of these was a control that could not fail,
or a check that could not see:

| # | What | Where |
|---|---|---|
| 1 | The boundary denied `kms:GetKeyPolicy`, so S6 could never show the **key policy** was what refused. F1.3 could not fail. | `infra/bootstrap/app.py` |
| 2 | S4's attempts were refused by the developer role's own Deny, so the deploy role's trust conditions were never the thing that refused. The assume is now allowed on the developer role, exactly as S6 grants itself `kms:GetKeyPolicy`. | `infra/bootstrap/app.py` |
| 3 | `F1_3` passed on any `AccessDenied`, including one from the role's own policy — the case the run file says does not count. It now reads CloudTrail's `errorMessage` against `message_must_contain`. | `src/verdict/build.py`, `runs/f1_3_key_policy.yaml` |
| 4 | An agent envelope could omit `F1_1`, `F1_2` and `F1_3` and still go GREEN: the Makefile builds the flags conditionally. The gate now refuses an agent envelope missing any of the four. | `src/verdict/gate.py` |
| 5 | `verify()` passed a bundle whose certificate it could not read, and skipped the signature silently when cosign was absent. Both are now reasons. A regression test forges exactly that bundle. | `src/bundle/verify.py` |
| 6 | S3's second form was matched by Python class, so the same rule written as a raw `CfnResource` was missed. Now matched by CloudFormation type. | `infra/construct/governed_agent.py` |
| 7 | A runtime added inside a `GovernedAgent`'s scope passed S8's check. Now the check is identity, not a place in the tree. | `infra/construct/governed_agent.py` |
| 8 | `fromPort` was in the message and not in the test: `tcp 1-443` to an approved endpoint was accepted. | `infra/construct/governed_agent.py` |
| 9 | S4's and S6's markers were still `xfail(strict=True)` although their reader landed here. The moment the attempts were recorded, strict xpass would have failed the measuring run. | `tests/test_m01_seeds.py` |
| 10 | S2's assertion matched `digest`, which also matches "carries no signed digest" — it would have passed with the comparison never run. | `tests/test_m01_seeds.py` |
| 11 | Two construct tests read a gitignored `cdk.out`, so they could pass on an older template. They synthesise their own now. | `tests/test_construct.py` |
| 12 | The tool chose silently between two rows on one key; `date` was required and never read; the prompt's field names were bound to nothing. | `agents/refagent/` |
| 13 | A run that spent and then failed reported less than it spent — the case the cap exists for. | `agents/refagent/agent.py`, `src/cost_cap.py` |
| 14 | `deploy.yml` set an output from every line of `pack`'s stdout and interpolated it into a shell in the credentialed job. | `.github/workflows/deploy.yml` |
| 15 | The construct read the two gateway endpoints under a parameter name nothing writes: refagent's stack could not have deployed. | `infra/construct/governed_agent.py` |
| 16 | `make validate`'s ruling-r check matched `S3` the AWS service as if it were seed S3. | `src/validate/checks.py` |
| 17 | **BLOCK B, ruled and repaired** (rulings s and t). One allow-list boundary was on every role the bootstrap stack makes, so the execution role could create nothing and the Budgets stop could not attach. Split per plane: the agent allow-list on agent-path roles only, a deploy-plane deny-list on the rest. The deny-list denies neither `iam:*` nor `sts:AssumeRole`, because either would be the wrong control firing. | `infra/bootstrap/app.py`, `tests/test_bootstrap.py` |
| 18 | The agent boundary did not **allow** `kms:GetKeyPolicy`. An allow-list caps by omission, so taking it out of the Deny at repair 1 was not enough: the boundary, not the key policy, would still have refused S6. | `infra/bootstrap/app.py` |
| 21 | **The instrument could not read the record it exists to read.** `scripts/observe_attempt.py` runs as `agentkeel-evals`, and that role had no `cloudtrail:LookupEvents`: `simulate-principal-policy` returns `implicitDeny`. In CI the lookup wrote "0 of 3 attempts recorded as AccessDenied" for attempts CloudTrail held, and `F1_1` and `F1_3` failed for want of a permission rather than for want of a refusal (run 35539363797). The same lookup run with admin credentials found 3 of 3 and 1 of 1. The role now holds `cloudtrail:LookupEvents` and no other cloudtrail action, so the instrument may read the record and may not change it. **The bootstrap stack must be redeployed before the next CI run.** | `infra/bootstrap/app.py`, `tests/test_bootstrap.py` |
| 20 | **The Budgets action would not deploy.** It hung off a daily budget, and AWS Budgets Actions do not support one. The daily figure notifies now and a monthly budget carries the stop, so the figure that was ruled and the figure that stops anything are no longer the same figure (ruling a, amended). | `infra/bootstrap/app.py`, `tests/test_bootstrap.py` |
| 19 | **The key policy could not be created.** It denied the four admin actions with `ArnNotLike` on `agentkeel-security` — a role nothing creates — plus root, so it covered the human running the deploy, and KMS refused: "The new key policy will not allow you to update the key policy in the future". It names the principals it refuses now: agent roles by path, and the deploy, execution, eval and developer roles. That is `security-reviewer` F6 and `platform-architect` finding 9 as well, which said the policy named a seat that does not exist. | `infra/bootstrap/app.py`, `tests/test_bootstrap.py` |

**Ruled here, repaired in PR 3.** Each of the three is ruled in its own
section below, with the seat that owns it. None is repaired in this PR:
PR 2 is the measurement, and PR 3 is the repair PR the cap allows.

| # | BLOCK | Seat | Ruled | Repair |
|---|---|---|---|---|
| A | The tool's return shape is not the one SPEC/00 §9 publishes. | Product | the tool stands; §9 is amended | **amended here** |
| C | A fork PR skips the `evals` job, and a skipped required check counts as success on GitHub. | Security | real; the skip is not the defect | PR 3, and M02 plants the case |
| D | S8's check is installed by the stack under test. | Security | what fired is narrower than false state 8, and the ledger says the narrower thing | PR 3 wording; M05 the control |
| F | Found after the cold review: the execution role cannot create refagent's stack. | Security | `deploy.yml` refuses at its first step and says why; `evals.yml` is untouched by F | the refusal is **here**, the grants in PR 3 |

## What refagent's first agent envelope found (run 35529132275)

`aadc735` records the first envelope of `scope: agent` this repo has ever
written. It is **UNMEASURED**, and the reason is not in the repo:

```
AccessDeniedException ... anthropic.claude-sonnet-5 is not available for this account
```

Fifteen goldens, fifteen identical refusals, and the control beside them
answering normally on Nova Micro. The account has never had model access
for Sonnet 5 enabled, and nothing before this run would have said so.

**Ruled, in `rulings/pr2-threshold-owner.md` (o and p).** The model was
pinned on `list-foundation-models` reporting `modelLifecycle: ACTIVE` in
us-west-2. ACTIVE says the model exists in the region; it does not say
this account may call it, and the two were read as one. refagent's model
is now `anthropic.claude-sonnet-4-6`, verified by a call rather than by a
listing, and `scripts/check_model_access.py` is what makes that check
repeatable. It is a script and not a `validate` check because it spends.
The cap stays at 150,000 as a **pre-run** number: ruling m makes an
over-cap envelope RED at its commit forever, so the cap has to be right
before the run, not calibrated after it.

What the envelope does show, and it is the first time any of it has been
in CI evidence: `F1_2` **pass** — S5's role without a boundary refused at
synth; `F1_1` and `F1_3` **fail** — S4's and S6's attempts have not been
made; `F1_4` **fail** — refagent cited nothing, because it answered
nothing. The cost-cap read 5,534 tokens against 150,000, all of it the
control's.

## The S4 and S6 attempts, and how their record was written

Both attempts were made on **2026-09-20** against account `581208540944`
in us-west-2, and AWS refused all four calls. Each was refused by the
control the seed names, which is the part a bare `AccessDenied` cannot
tell you:

| Seed | Call | What refused it |
|---|---|---|
| S4 | `sts:AssumeRole` on `agentkeel-deploy` | the **trust policy**. The developer role holds `sts:AssumeRole` on purpose (`AssumeIsAllowedHereSoTheTrustPolicyIsWhatRefusesIt`), and the message names no explicit deny, so the identity policy allowed it and the trust policy is what said no. |
| S4 | `sts:AssumeRole` on `agentkeel-cfn-exec` | the trust policy, same reading. It trusts `cloudformation.amazonaws.com` and nothing else. |
| S4 | `cloudformation:CreateStack` | `with an explicit deny in an identity-based policy` — the developer role's `NeverDeploy`. No stack was created. |
| S6 | `kms:GetKeyPolicy` | `with an explicit deny in a resource-based policy` — **the key policy**. The role's own policy granted the action and the agent boundary allows it (ruling t), so nothing else was left to refuse it. |

S6's attempt used a role created by hand for it, `agentkeel-seed-s6`, on
path `/agentkeel/agents/` with `agentkeel-boundary` attached, and deleted
after. refagent's runtime role does not exist until refagent's stack is
deployed from `main`.

**How the record was written, which is weaker than ruling i describes.**
Ruling i has the human write what they saw and CI confirm it independently
in CloudTrail, and `scripts/observe_attempt.py` puts the two side by side
under `human_said` with the note that they must agree. Here the human made
the attempts but did not keep the output, so the `observed:` entries were
reconstructed from CloudTrail by request id. **The two halves therefore
have one source, and the `human_said` comparison is vacuous for this
milestone.** The request ids are real and the events are AWS's own; what
is lost is the independence, not the refusal. Recorded rather than quietly
left as it stands. From M02 the human's own output is kept.

One further note for the record: the run file's command for S6 reads
`--key-id alias/agentkeel-refagent`, and KMS refuses an alias for this
operation (`InvalidArnException: Key Aliases are not supported for this
operation`). The attempt was made with the key id. The `command:` field is
documentation and feeds no check, but it is wrong as written and Product
carries the correction.

## BLOCK A — the tool returns the row; SPEC/00 §9 published the answer

**Seat: Product.** SPEC/00 §9 publishes

```
check_availability(title_id, territory, platform, date)
  -> {available, exclusive, constraints[], table_row, clause_id, confidence}
```

and `agents/refagent/tools/check_availability.json` returns
`{found, row, clause_candidates, source}`. SPEC/00 is the authority, so one
of the two is wrong.

**Ruled: the tool stands and §9 is amended.** Three reasons, heaviest first.

1. **The fields §9 lists are the answer's, and the answer has them.** Run
   35544267728, golden g-004: `{'table_row': 'r-029', 'clause_id': 'MC-4',
   'available': False, 'exclusive': False, 'constraints':
   ['clearance_expired', 'non_exclusive']}`. Five of the six named fields,
   produced one layer up from the tool. §9 drew one arrow where the design
   has two hops.
2. **A tool that returned them would decide, and F1.4 would stop measuring
   the agent.** F1.4 asks whether the agent cites a `table_row` and a
   `clause_id` that exist. Hand the model both, already chosen, and it
   relays them: F1.4 then measures a table lookup. The tool's own
   description says the same thing and has since it was written — "Returns
   the row; it does not decide the answer", and of `clause_candidates`,
   "Which one the question turns on is the agent's to say."
3. **`confidence` is not a naming difference. It does not exist anywhere in
   the repo.** `grep -rn confidence agents/ src/ evals/goldens/` returns
   nothing. §9 also keys HITL to it — "confidence below 0.7 ... refuses and
   mints a resume token". The HITL branch was **cut at M01 open** (cuts 1, 3
   and 4, recorded in `agents/refagent/agent.py`), and §9 was never updated
   to say so. A cut list that does not reach the spec it cuts from is how a
   spec starts describing something nobody built.

**Amended here, not in PR 3.** SPEC/00 §9 now gives the tool's return as
`{found, row, clause_candidates, source}` and the answer's shape as
`{available, exclusive, constraints[], table_row, clause_id}` in a bullet
of its own, with the sentence that makes the split matter: a tool that
returned `available` and `clause_id` would decide, and F1.4 would measure a
table lookup rather than the agent. `confidence` and the HITL rule stay in
§9, both marked **M07 (HITL cut from M01 at open)** — the rule is still the
rule; what changed is when it is built.

This is the only BLOCK whose repair edits SPEC/00, the authority. The
measurement is not affected: the workflow's already-measured check excludes
`SPEC`, and the envelope at `305da212` was written against the tool as it
stands, which is the half of the pair that did not move.

## BLOCK C — a fork PR skips `evals`, and a skipped required check passes

**Seat: Security.** `.github/workflows/evals.yml:67`:

```yaml
# A fork gets no OIDC token. Skip it; do not fail it.
if: github.event_name == 'push' || github.event.pull_request.head.repo.full_name == github.repository
```

GitHub counts a skipped required check as success, so a fork PR merges with
no `make validate` and no `pytest`.

**Ruled: real, and the skip is not the defect.** A fork has no OIDC token
and the measuring half genuinely cannot run; failing it would be a red
check that means "not applicable". The defect is that the half needing no
credentials was skipped along with it.

**Repair, in PR 3:** split the job. `make validate` and `uv run pytest`
move into a job with no `configure-aws-credentials` and no `if:`, required
on the branch, so they run on a fork. The measuring job keeps the skip.

**What that leaves, named rather than closed:** a fork PR would then merge
with no envelope at all. Whether it may is M02's, the milestone that
measures seat-owned files and the ruleset.

And the part worth saying plainly: **today the exposure is zero, and that
is not a control.** R1 is one human; this repo has no external
contributors, so no fork PR has ever been opened and none will be before
M02. A check that has never met the case it guards against is an absence of
a test, not a guarantee. M02 plants the case.

## BLOCK D — S8's check is installed by the stack it checks

**Seat: Security.** `refuse_outside_construct(stack)` is opt-in, and
`tests/fixtures/construct/outside_construct.py` calls it on its own last
line. A stack that never imports `infra.construct` is never checked.

**Ruled: what fired is narrower than false state 8, and the ledger says the
narrower thing.**

- **What S8 proves.** A stack that installs the platform's checks and then
  makes a bare `AWS::BedrockAgentCore::Runtime` is refused at synth, with
  "not a GovernedAgent's own runtime". That is a real refusal of a real
  false state, and it is what `checks.F1_1` carries.
- **What it does not prove.** That a stack which never imports the module is
  refused. Nothing at synth can bind code that does not call it. That is
  the ceiling of synth-time checking, not a bug in the check.

**What is closed today by something other than synth**, and it is more than
the cold review credited: the developer role — seed S4's own principal — is
denied both `bedrock-agentcore:CreateAgentRuntime` and
`cloudformation:CreateStack` by `NeverDeploy`, and CloudTrail recorded the
second being refused on 2026-09-20.

**What would bind an author who did not ask to be bound:** a CloudFormation
Hook on the resource type, or a service control policy. SPEC/01 §1 already
puts SCPs in the landing zone. **M05** — five hostile attempts — is where an
author who skips the import belongs, and this ruling names it as M05's.

**In PR 3:** SPEC/01 §5's wording for S8 takes the narrowing, and M01's
explainer does not say the construct is the only way to make an agent on
this platform. It says a stack that asks the platform to check it is
refused, which is what happened.

## BLOCK F — the execution role cannot create refagent's stack

**Seat: Security. Found after the cold review, while ruling D.**

`agentkeel-deploy` may create a stack and may `iam:PassRole` exactly one
role, `agentkeel-cfn-exec`; CloudFormation then acts as that role. Its
whole policy, read from the deployed account on 2026-09-20:

```
Allow CreateRolesOnlyInsideTheBoundary: iam:CreateRole, iam:PutRolePolicy,
      iam:AttachRolePolicy  ->  role/agentkeel/agents/*
Deny  NeverTouchTheBoundaryOrAKeyPolicy: iam:DeleteRolePermissionsBoundary,
      iam:CreatePolicyVersion, iam:DeletePolicy, kms:PutKeyPolicy,
      ec2:CreateInternetGateway, ec2:AttachInternetGateway,
      ec2:CreateNatGateway  ->  *
```

No `bedrock-agentcore`, no `ec2`, no `logs`, no `kms`, no `s3`, no
`dynamodb`. The construct makes all of those. **refagent's stack will fail
on its first non-IAM resource**, and `simulate-principal-policy` returns
`implicitDeny` for `bedrock-agentcore:CreateAgentRuntime`.

Nothing has told us because `deploy.yml` has never run — which this file
already said under "What this PR does not show", without knowing what was
waiting there.

### Ruled: `deploy.yml` refuses up front, and `evals.yml` is left alone

**`deploy.yml` refuses at its first step**, with the message

```
cfn-exec has no service grants: BLOCK F, repaired in M01 PR 3
```

A `refuse` job runs before everything; `sign` needs it and `deploy` needs
`sign`, so nothing signs, pushes or half-builds a stack. Without it the
first push to `main` after this PR merges would run a deploy that fails
partway and leaves a partial `AgentkeelRefagent` behind, and the failure it
printed would be a permissions error on whichever resource happened to come
first — true, and useless. It refuses in one line instead, and names the
block and the PR that lifts it. `infra/workflows.sha256` is rewritten.

**The grants themselves are PR 3**, and narrowly: cfn-exec gets what the
construct makes and nothing else, read back with the same
`simulate-principal-policy` table the eval role's deploy prints (ruling j)
before `deploy.yml` is trusted with anything.

### What runner mode means for claim 1, and what PR 3 owes

The runner's fallback to in-process mode is silent, and the envelope can't distinguish "refagent in the runner" from "refagent in the construct." PR 2 measures the first, and claim 1's second half is not measured until PR 3 deploys the runtime.

Claim 1 has two halves — "an unsigned or tampered bundle never loads" and
"refagent runs inside the construct". The first is measured here: S1 and S2
refused by `verify`, S3, S5 and S8 at synth, S4 and S6 against the deployed
bootstrap stack. The second is not. Every run so far, on a PR and on
`main`, has been runner mode, and nothing in the envelope says so — the
observation records `where`, but `where` is written by the runner that
chose the mode, and the gate never reads it.

**This is a P3 exception and is named as one.** P3 says claim 1 is measured
by PR 2. Half of it is; the half that needs a deployed runtime cannot be,
because BLOCK F means no runtime can be deployed until cfn-exec has its
grants. The ledger row's Expected cell and `docs/milestones/M01.md` both
carry the sentence, so a reader meets it before they meet the GREEN.

**Made loud, here:** `src/agent/run.py` prints `mode: runner
(AGENTKEEL_RUNTIME_ARN unset)` or `mode: runtime <arn>` as its first line,
and `evals.yml` on `main` echoes that line into the job summary. Neither is
a check. They stop the fallback being silent; they do not stop it.

**Carried to PR 3**, with the construct and not written here:

1. cfn-exec's service grants (BLOCK F), and the first real deploy.
2. The measurement of construct tenancy that the deploy makes possible.
3. **An envelope field recording the mode.** `src/verdict/schema.json` is
   `additionalProperties: false`, so this is a schema change, and ADR-0004
   (measurement fields) already carries its two amendments. It needs a new
   ADR. **The next free number is ADR-0007**, not ADR-0006: ADR-0006 is
   `gateway-endpoints-for-s3-and-dynamodb`, added in this PR.

### What `evals.yml` on `main` does, which is not what this seat assumed

This ruling was drafted on the premise that a failed deploy would leave
`evals.yml` with no runtime to call, so the merge commit would carry a RED
whose real cause was F — and that the answer was to write the control's
envelope in M00 form (`control_card_ref: null`), as PR 1's did, until
refagent is deployed.

**That premise does not hold, and the change it implied is not made.**
`AGENTKEEL_RUNTIME_ARN` is set nowhere: not in `.github/workflows/evals.yml`,
not in the `Makefile`. `src/agent/run.py` reads it and falls back to running
refagent's code **in the runner** when it is absent, which is the mode every
run so far has used, on a PR and on `main` alike. So after this PR merges,
`evals.yml` on `main` writes the same agent-scope envelope it writes on a
PR, with `control_card_ref` populated, and the verdict is **GREEN**. The
deploy is invisible to it.

Downgrading that to a control-only envelope would not protect the merge
commit from a RED it was never going to carry. It would throw away a real
measurement of refagent to do it, and P3 wants claim 1 measured by PR 2,
not deferred past it. So `evals.yml` is untouched.

**What this does cost, and it is worth naming.** The envelope on `main`
will say `where: refagent's code, in the runner` and
`source: data/rights_table.json`, exactly as on the PR. Nothing in M01
measures the deployed runtime or the DynamoDB read, and the ledger row
already says so. BLOCK F does not change that; it explains why it will
still be true after the merge.

**The instruction this seat gave, and what was done instead**, recorded
because a ruling that quietly became something else is worse than a ruling
that was wrong: the refusal in `deploy.yml` is implemented as ruled; the
`evals.yml` fallback to M00 form is not, on the finding above. If this seat
wants the fallback anyway, it is one `if:` on the agent step and this
section is the place to say so.

**One consequence for D.** Part of what makes S8's gap small today is that
the deploy plane cannot make a runtime either. That is this hole, not a
control, and it disappears the moment cfn-exec is given what it needs. D's
narrowing does not get to lean on it.

## Five failures this milestone's tests could not have caught

Sonnet 5 was not available to the account; the KMS key policy failed the
lockout safety check; the Budgets action refused a daily budget; the eval
role could not call CloudTrail; and the CloudFormation execution role
cannot create refagent's stack (BLOCK F, which has not fired yet because
nothing has asked it to). Synth passed, cdk-nag passed and 168
tests passed before each one. All four are service behaviour rather than
template shape, and the fourth is worse than the other three: the template
was right, the code was right, and the **permission the instrument needed
was never granted**, so the check failed silently in the direction of
"nothing was refused".

This milestone's infra was written against the API's shape and never
against the API. M01's close carries that as its own line, and the
remedies are already in the tree in two forms:
`scripts/check_model_access.py` (a pin is not pinned until something has
called it) and the `simulate-principal-policy` table the eval role's
deploy prints (ruling j). Neither would have caught the other's failure.
What is still missing is anything that runs an instrument as its own
principal before a measuring run depends on it.

## What a reader can run to falsify this PR's own claims

```bash
uv sync --frozen

# Each seed, refused for its own reason and no other.
uv run pytest tests/test_m01_seeds.py -q          # S4 and S6 read the attempts made on 2026-09-20
uv run python -m src.bundle.verify tests/fixtures/bundles/unsigned   # exit 4, signature
uv run python -m src.bundle.verify tests/fixtures/bundles/altered    # exit 4, digest
uv run python -c "from pathlib import Path; from infra.construct import synth_refusal; \
  print(synth_refusal(Path('tests/fixtures/construct/extra_egress.py')))"

# The archive recipe is the one CI signed: this re-packs S1 and compares
# the digest with the one inside the bot's signature.
uv run pytest tests/test_bundle.py -q

# Both stacks, cdk-nag, and the committed reports held to this synth.
uv run make validate

# The gate reads the cap that stood at the envelope's commit, not today's.
uv run python -c "from src.verdict import gate; \
  print(gate.cap_at('55dadb2f221e60036bdba0b01fdb6eff025d74bc'))"   # 20000, not 150000
```

To falsify the construct's claim, add an egress rule to
`infra/construct/app.py` — any destination, any port — and run
`uv run make validate`. If it synthesises, the S3 check does not read what
it says it reads.

## What this PR does not show

- **No deploy has run.** `deploy.yml` is written and has never executed.
  The signature it would make, the image it would push and the load check
  it would run are all untested. Row 1 does not rest on any of them.
- **The rights table is read from the file, not DynamoDB**, in this PR's
  measurement. refagent's stack is deployed from `main` after this PR
  merges, so on a PR run there is no table; every observation records
  which source it read (`agent.rights_rows`, `rights_table` in the raw).
- **F1.4 reads existence, not correctness.** An answer passes the citation
  half if its `table_row` and `clause_id` exist in `data/`; it is not
  compared with the golden's expected pair. That is SPEC/01 §4 as written,
  and it is the weaker of the two things a reader might assume it means.
