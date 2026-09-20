# SPEC/01 — Signed bundle, construct, first tenant

Status: DRAFT · Owner: Product seat · Milestone M01 · Opened at M01 PR 1
(`milestones/M01/rulings/pr1.md`) · Build list: SPEC/00 §8 M01, which is
the ruling for this milestone's build paths (`SPEC/00-overview.md#8-M01`)
· Revised once before PR 1 opened, on the `product-spec-reviewer` report
(3 BLOCK, ruled) and the `platform-architect` report
(`milestones/M01/feasibility.md` §1, §2).

## 1. The claim

**Claim 1.** An unsigned or tampered bundle never loads; refagent runs
inside the construct.

For a director: *an agent can only be deployed from a build the pipeline
signed; a changed byte, or a laptop, is refused* (SPEC/00 §10.3, M01).

Threat answered (SPEC/00 §3): the malicious developer who edits what
ships or deploys from a laptop.

**What "a laptop" means here** (ruling on BLOCK 2). A person using the
developer role that the bootstrap stack creates, which carries the
permission boundary, from any machine. It does not mean the admin who
deploys the bootstrap stack. That admin is break-glass: stopping them
takes a service control policy, which is landing-zone work (SPEC/00 §2,
§12). The explainer says so in plain words.

## 2. Words used here

- **Bundle.** One agent's `agents/<name>/{manifest.yaml, prompt.txt,
  tools/, rules/}` (ADR-0003 amendment 1), packed by CI into one archive.
  Its **digest** is the sha256 of that archive. Packing is reproducible:
  the same tree gives the same digest on any machine.
- **Signed.** CI signs the digest with cosign, keyless, over GitHub OIDC.
  For a deploy, the only identity accepted is `deploy.yml` on
  `refs/heads/main` in `andaro74/agentkeel`, pinned by issuer and by the
  certificate's source-repository id as well as by name.
- **Verify.** `src/bundle/verify.py` checks the signature, the signer's
  identity and the digest, and reports **every** reason a bundle fails,
  not the first (ruling on BLOCK 1). A seed is refused for the reason it
  was planted for, whatever else is also wrong with it.
- **Loads.** The agent starts in AgentCore Runtime with this bundle as its
  code and prompt. **Deploys** means CloudFormation creates or updates the
  agent's stack. Claim 1 is false if either happens to a seeded bundle.
- **The construct.** `GovernedAgent`, a CDK construct under
  `infra/construct/` (Security). An agent exists on this platform only as
  an instance of it.
- **The bootstrap stack.** `infra/bootstrap/` (Security). Deployed by a
  human with admin, in the agent account, and changed only that way.

## 3. The false state

Claim 1 is false if any of these is true. Each names something a reader
can look at.

1. A bundle with no signature from the deploy identity is deployed or
   loads.
2. A signed bundle with one byte changed after signing is deployed or
   loads.
3. An agent stack whose security groups allow egress to a destination not
   in the manifest's `endpoint_allowlist` synthesises or deploys, however
   the rule is added.
4. A deploy of refagent's stack succeeds from a laptop, as §1 defines it.
5. `GovernedAgent` accepts an agent role that has no permission boundary,
   or has a different one from the bootstrap stack's.
6. The agent's role can read the key policy of its own KMS key.
7. refagent answers an ordinary golden, and the answer lacks a `table_row`
   or a `clause_id` that exists in `data/`, and the run is not RED.
8. An agent runtime is synthesised without `GovernedAgent`.

## 4. Falsifiers

| Id | Fires when | What it looks like in the repo |
|---|---|---|
| F1.1 | any of the seeded bundles or deploys (false states 1–4, 8) loads, deploys or synthesises | `checks.F1_1: fail` in an agent envelope under `evals/history/`, or a seed's observation file under `milestones/M01/runs/` recording anything but the expected refusal |
| F1.2 | the construct accepts a role without the boundary | `checks.F1_2: fail`; `cdk synth` of `tests/fixtures/construct/role_without_boundary.py` exits 0 |
| F1.3 | the agent role can read its own KMS key policy | `checks.F1_3: fail`; `milestones/M01/runs/f1_3_key_policy.yaml` records anything but a denial by the key policy |
| F1.4 | refagent answers an ordinary golden without a `table_row` and a `clause_id` that both exist (missing either fires it) | `checks.F1_4: fail` in an agent envelope; an agent result with `kind: ordinary` and `cites: false` |

**F1.4 is read twice, separately (P5).** `verdict.build` writes, and
`verdict.gate` works out again from `goldens` and rejects any
disagreement:

- `pass = score and cites` for `scope: agent` results of kind `ordinary`
  and `trap`;
- `checks.F1_4 = fail` when any `scope: agent` result of kind `ordinary`
  has `cites: false` (ruling on BLOCK 3). A failed check is RED whatever
  the history, so an uncited answer turns row 1 RED on the first run.

The control is scored as it was at `m00`. Its card is the base, and its
composition must not change (ADR-0004 amendment 2).

**Where each check comes from (PR 2).** Engineering names the runner at
PR 2 open; the paths are fixed here. `F1_1`: the junit result of the S1,
S2, S3 and S8 tests in `tests/test_m01_seeds.py`, and the CloudTrail
lookup of S4's request ids. `F1_2`: the junit result of the S5 test.
`F1_3`: the CloudTrail lookup of S6's request id. `F1_4`: the envelope's
own `goldens`. A human-written observation file feeds no check by itself. As with `F0_2`, a check read
from junit carries the CI run URL.

**Domain rule (SPEC/00 §9).** The rights table is the truth; the corpus is
the evidence. An answer returns `table_row` and `clause_id` as typed
fields, and a missing one is a bug, not a matter of style. Dates, windows,
holdbacks and exclusivity are read from the table and never inferred from
vector search.

## 5. The seeded cases

SPEC/00 §8 M01 lists four seeds. F1.2, F1.3 and F1.4 get one each here,
and so does the second half of the claim (S8). A falsifier with no seeded
case is one that has never been shown to fire.

| Seed | Falsifier | Planted as | Read by (PR 2 unless said) |
|---|---|---|---|
| S1 unsigned bundle | F1.1 | `tests/fixtures/bundles/unsigned/`: a bundle directory with no signature | `verify`, in the deploy workflow and at load |
| S2 altered after signing | F1.1 | `tests/fixtures/bundles/altered/`: S1's bundle with one byte of `prompt.txt` changed. It carries S1's signature, which CI makes in PR 2's first commit, before the verifier. The PR run signs with its own identity; `verify` reports the digest mismatch whatever the identity (ruling on BLOCK 1) | the same |
| S3 egress not in the manifest | F1.1 | `tests/fixtures/construct/extra_egress.py` (a rule added through the construct's security group) and `extra_egress_standalone.py` (a separate egress resource that names the group) | a check over the whole synthesised stack, not inside the construct |
| S4 laptop deploy | F1.1 | `milestones/M01/runs/f1_1_laptop.yaml`: the principal (the developer role), the two attempts, what counts as refused | the deploy role's trust policy, the developer role's boundary, and the CDK bootstrap roles trusting only the deploy role |
| S5 role without boundary | F1.2 | `tests/fixtures/construct/role_without_boundary.py` | `GovernedAgent`, at synth |
| S6 key policy read | F1.3 | `milestones/M01/runs/f1_3_key_policy.yaml`: the call made with `kms:GetKeyPolicy` granted in the role's own policy for the attempt, so the refusal can only be the key policy's explicit deny | the key policy |
| S7 uncited answer | F1.4 | `tests/fixtures/refagent_raw_uncited.json`: fifteen raw replies that give every ordinary and trap golden's `answer_fields` right and cite nothing | `verdict.build` and `verdict.gate`, **in PR 1**, in the commit after the seed |
| S8 agent outside the construct | F1.1 | `tests/fixtures/construct/outside_construct.py`: an AgentCore runtime resource made directly, with no `GovernedAgent` | a check over the whole synthesised stack |

Each seed goes in as its own commit, with its test in
`tests/test_m01_seeds.py`, before any code that reads it. Each test is marked `xfail(strict=True)`: it reports
as an expected failure until its reader lands, and fails the first run
after that, until the marker comes off. A seed cannot start passing
without somebody saying so. S4 and S6 are attempts against AWS; their
tests read the observation files, which say `observed: null` until the
attempt is made.

**When each is measured (ruling on BLOCK 1; ruling 4 before PR #7
merged).** PR 2's run on the PR measures S1, S2, S3, S5, S7 and S8, with
the PR run's identity accepted for that measurement only. The bootstrap stack is deployed to the agent account by the human with admin during PR 2, before PR 2's first CI run, as infra/eval-role was at M00. S4 and S6 are attempted by the human against that stack during PR 2; each attempt's request id, timestamp and AccessDenied text are written to milestones/M01/runs/f1_1_laptop.yaml and f1_3_key_policy.yaml, and a CloudTrail lookup in PR 2's CI run (scripts/observe_attempt.py, the F0.3 observer's pattern) confirms each request id was denied and writes checks.F1_1 and checks.F1_3. A human-written file feeds no check by itself; the check is the CI lookup of the request id. Refagent's first agent envelope is PR 2's. Nothing about claim 1 is first measured after PR 2 merges (P3).
The deploy-from-`main` path is what PR 2's construct exercises for
refagent; it is not where a falsifier is first read.

These are seeded cases for claim 1, not plants under SPEC/00 §5's plant
rule. They do not enter `plants_expected`, which counts golden plants.
`make plants` lists them separately, with their reader's path and whether
it exists yet. `platform-architect` (R8, added in PR 1) is exercised on
S3, S5 and S8 at PR 2.

## 6. The code that reads the answer (PR 2, except F1.4)

None of it is in PR 1, except the F1.4 reading in `verdict.build` and
`verdict.gate`.

- **Manifest schema** (`src/manifest/schema.json`), and `validate`
  checking every `agents/*/manifest.yaml` against it.
- **Bundle** (`src/bundle/`): `pack` (reproducible archive and digest),
  `verify` (§2). Exit 0 or a refusal with every reason; no warnings.
- **Deploy workflow** (`.github/workflows/deploy.yml`, Security): on
  `main` only. Packs, signs, verifies, then deploys. Verify runs again at
  the start of the deploy job, on the bytes that job deploys.
- **At load** (repair on `platform-architect` BLOCK 3). The check runs
  outside the bundle's own code and verifies the cosign signature, not
  only a digest the deployer wrote. The runtime image is pinned by digest
  and its repository is tag-immutable. S1 and S2 are run through the load
  check as well as through the deploy workflow.
- **Bootstrap stack** (`infra/bootstrap/`):
  - the GitHub OIDC provider, imported (it exists in the account);
  - the deploy role, trusted with `StringEquals` on `aud`, the immutable
    `sub` for `refs/heads/main`, and `job_workflow_ref` =
    `…/deploy.yml@refs/heads/main`;
  - the CloudFormation execution role the deploy passes, which carries
    the boundary and may create a role only with the boundary attached
    (`iam:PermissionsBoundary` condition). The CDK bootstrap roles trust
    the deploy role only. This is the repair on `platform-architect`
    BLOCK 1: without it the deploy role acts as admin;
  - the developer role (§1), boundary on;
  - the eval role, absorbed from `infra/eval-role/` under a **new name**,
    with its Deny statement (item 33) and trust conditions as they stand;
  - **two permission boundaries**, one per plane (ruling s,
    `feasibility.md` §2.6). `agentkeel-boundary` is the agent plane's
    allow-list, attached to roles under `/agentkeel/agents/` and to no
    others; it is what S5 and S6 read, and it allows `kms:GetKeyPolicy`
    so that the key policy is what refuses S6 (ruling t).
    `agentkeel-deploy-boundary` is the deploy plane's deny-list, on every
    role the bootstrap stack makes, so the execution role can create what
    a deploy creates while R4 still holds. Every role either stack
    synthesises carries one of the two, and a synth test fails on a role
    with neither, on an agent-path role with the wrong one, and on a
    deploy-plane role carrying the agent allow-list;
  - a VPC with no internet gateway, endpoints with policies scoped to the
    account, and the boundary denying internet and NAT gateway creation;
  - one KMS key per agent. Its policy denies key-policy changes, grants,
    disabling and deletion to every role the platform creates, named one
    by one, and denies `kms:GetKeyPolicy` to agent roles, matched by role
    path. It does not deny them to the human with admin: KMS refuses to
    create a key whose policy locks its own creator out of
    `kms:PutKeyPolicy`, and SPEC/01 §1 already puts that principal in the
    landing zone;
  - two Budgets budgets on Bedrock spend (ruling a, amended at PR 2). The
    daily one at `daily_usd: 10` notifies and stops nothing; the monthly
    one carries the Deny action, because AWS Budgets Actions do not
    support a daily budget. Budgets data lags by hours and the action's
    own window is a month, so what is bounded is a month's spend plus one
    refresh interval at the account quota.
  - Order (Security, item 20; ruling 4): the human deploys the bootstrap
    stack with admin during PR 2, before PR 2's first CI run, points
    `AWS_EVAL_ROLE_ARN` at the new eval role, and PR 2's CI runs; then
    `AgentkeelM00EvalRole` is deleted after PR 2 merges.
- **`GovernedAgent`** (`infra/construct/`): AgentCore Runtime in VPC
  mode only, Gateway and Identity; the boundary on every role it makes,
  and required on any role it is given (imported roles refused); the
  bootstrap's VPC, not a caller's; security groups built from the
  manifest's `endpoint_allowlist`, with a check over the whole stack
  refusing any other egress (an absent egress list counts as
  `0.0.0.0/0`); a Bedrock application inference profile per agent, for
  cost tagging. The boundary ARN is read from a Security-owned parameter,
  not from CDK context.
- **refagent** (`agents/refagent/`): Sonnet 4.6 through
  `us.anthropic.claude-sonnet-4-6`, us-west-2; the rights table in DynamoDB,
  loaded from `data/rights_table.json`; the tool
  `check_availability(title_id, territory, platform, date)` with a strict
  schema both ways; the knowledge base over `data/corpus/` (Data Owner);
  the HITL branch (confidence under 0.7, or any first-window release,
  refuses and mints a resume token). `ratings-helper` as a stub, so the
  edge exists.
- **The agent runner** writes raw observations for refagent, as
  `src/baseline/run.py` does for the control. On a PR it runs refagent's
  code in the runner; on `main` after the deploy, it calls the deployed
  runtime. `verdict.build` writes one envelope, for refagent.
- **`validate` at M01.** Workflow file hash: PR 1. Manifest schema and
  cdk-nag: PR 2. Seats assigned to real groups, edges two-sided, no
  cycles, ceilings within bounds: PR 2, when refagent's and
  `ratings-helper`'s manifests carry them; M02 if `ratings-helper` is cut.
  CODEOWNERS ↔ manifest: M02, with CODEOWNERS.

## 7. What the gate reads, from M01 (ADR-0004 amendment 2)

- **One envelope per commit, one subject.** When an agent ran, its
  `goldens` hold `scope: agent` results only; the control is still run
  every time (P6), its card is `<commit>.baseline-card.json`, and the
  envelope names it in `control_card_ref`. When no agent ran, the
  envelope is the control's, in M00's form (`control_card_ref: null`,
  its own card as the base). A run always writes an envelope.
- **The base is fixed.** On an agent envelope, `baseline_card_ref` names the card at tag `m00`,
  the one row 0 cites. Its hash is in `thresholds.yaml` (Threshold Owner),
  and `build` refuses a different one.
- **Cost is a recorded RED** (Threshold Owner, item 22). `tokens_in` joins
  `tokens_out`. An envelope whose spend is over `thresholds.yaml`
  `cost_cap.tokens_per_run` is RED, read by `build` and again by `gate`.
- **The card's `region`** is the request region, the profile ARN's
  `us-west-2` (Threshold Owner with Security, item 23). Converse does not
  return the region that served the call, and nothing records it.
- **Agent history starts empty.** No `(agent, id)` row exists before
  refagent's first CI run.

## 8. Expected on the plant (row 1)

- **PR 1.** No agent under test, so `make evals` writes the control's
  envelope in M00's form, gated and recorded as at M00. It says nothing
  about claim 1. `make plants` lists S1–S8: S7's reader is in the tree,
  and the other seven are listed as having no reader yet. `pytest` shows
  seven expected failures and S7 passing.
- **On S7 (PR 1).** Every ordinary and trap result has `score: true`,
  `cites: false`, `pass: false`; `checks.F1_4` is `fail`; build and gate
  both say RED.
- **PR 2's run on the PR.** S1 and S2 refused by `verify`, each with its
  planted reason among the reasons; S3 (both), S5 and S8 refused at synth;
  refagent's envelope carries `checks.F1_1`, `F1_2` and `F1_4`, each
  `pass`. No count of refagent's passes is expected: agent history is
  empty, so its first numbers are reported and do not gate (P7). The
  checks decide the row.
- **During PR 2, before its first CI run** (ruling 4). The human deploys
  the bootstrap stack and attempts S4 and S6; PR 2's CI run looks up each
  request id in CloudTrail and writes `checks.F1_1` and `checks.F1_3`.
  Refagent's first agent envelope is PR 2's. Nothing about claim 1 is
  first measured after PR 2 merges (P3).

## 9. Controls with no seeded case at M01

SPEC/00 §10.5: no document describes these as working. Each is a
FINDING carried with a seat, not a claim.

- the deploy role unable to alter a key policy (R4, first half);
- the boundary on roles the stacks create, as opposed to a role handed to
  the construct (S5 covers only that);
- no internet or NAT gateway;
- endpoint policies scoped to the account;
- the Budgets action;
- the eval role refusing a direct foundation-model call, and a call
  through an unpinned profile (item 18, a step in `evals.yml` at PR 2);
- log and audit delivery to the security account;
- Gateway targets and Identity credential providers calling out with no
  security group over them (ruling c, `feasibility.md` §2.6). Neither is
  wired at M01, and both are deferred to M05.

## 10. Cut list

Cuts 1, 3 and 4 are **taken at open** (ruling SCOPE, `feasibility.md`
§2.6), not held against the cap. Cut 2 stands as a cut if the cap is
threatened. Cut 5 is not taken: the per-agent inference profile stays,
and only the Budgets filter that would use it is M05 (ruling a).

| # | Item | State at M01 open | Milestone |
|---|---|---|---|
| 1 | `ratings-helper` stub, and the two-sided edge | cut now | M02 |
| 2 | Log and audit delivery to the security account | cuttable, in order, if the cap is threatened; M01 then touches the agent account only | M05 |
| 3 | The knowledge base over `data/corpus/` | cut now; refagent answers from the table and the tool alone, and F1.4 does not read the corpus | M03 |
| 4 | The HITL branch | cut now; it becomes a Gateway tool there anyway | M07 |
| 5 | The application inference profile per agent | not cut; it stays at M01 | — (its Budgets filter: M05) |

Never cut: any seeded case; cosign sign and verify; the signature check
at load; the permission boundary; the deploy role's and the execution
role's policies; the KMS key policy; the egress refusal; refagent's tool
and the rights table (F1.4 reads them). Gateway and Identity are **not**
never-cut at M01 (`product-spec-reviewer` finding 17, ruled at PR 2
open): the construct declares both as props and wires neither. Identity's
claim is M05's, Gateway's is M02's and M07's.

## 11. Not in M01

- `ruling-cited`, `two-key`, CODEOWNERS routing, `bypass_actors: []`
  checked against the live ruleset: M02.
- Guardrail, judge, corpus fingerprint on the envelope: M03. `cost_usd`:
  M05 at the earliest, when a milestone first needs USD on the envelope (a
  price table in `thresholds.yaml`, keyed by pinned model id).
- Containment beyond the boundary and the egress refusal: M05.
- The admin, break-glass principal: landing zone (§1).
