M01 PR 2 of 4: **measure** (P3). Claim 1: *an unsigned or tampered bundle never loads; refagent runs inside the construct.* Opened as a **draft** right after the Security setup commit, so `sign-fixture.yml` runs on the `pull_request` event and the S2 signature is the bot's commit, before `src/bundle/` exists (`feasibility.md` §2.6, PR 2 mechanics and ruling n).

Rulings: `milestones/M01/rulings/pr2.md`, and `pr2-threshold-owner.md` when this PR's first agent envelope exists (rulings o, p). Build paths cite `SPEC/00-overview.md#8-M01`. The seats' rulings for this PR are `milestones/M01/feasibility.md` §2.6: SCOPE, Security a–k and q–r, Engineering l–n, Threshold Owner o–p.

**This PR is RED on this head, and for the right reason.** `pytest` fails on S4 and S6 — "the attempt has not been made". The two attempts are the human's, during this PR, against the deployed bootstrap stack. Nothing else fails.

## Scope at M01, as ruled at PR 2 open

Cuts 1, 3 and 4 of SPEC/01 §10 are taken: `ratings-helper` → M02, the knowledge base over `data/corpus/` → M03, the HITL branch → M07. Gateway and Identity are declared as props of `GovernedAgent` and wired to nothing; passing either is refused at synth. Identity's claim is M05's, Gateway's is M02's and M07's. refagent at M01 is Sonnet 5 through `us.anthropic.claude-sonnet-5`, the rights table, and `check_availability` with its strict schema, inside the construct.

## Step 1 — Security setup

- `infra/ruleset/main.json` re-exported: `required_status_checks` lists `cold-review-ruling` **and** `evals` (ruling k).
- `.github/workflows/sign-fixture.yml` (ruling n): keyless `cosign sign-blob` over S1's archive bytes, the bundle written into `tests/fixtures/bundles/altered/`, committed as `github-actions[bot]` in `2609d67`. `git show 2609d67 --stat` shows the signature and no `src/bundle/`.
- `infra/workflows.sha256` updated in the same push.

## Step 2 — the build

| What | Where | Ruling |
|---|---|---|
| Manifest schema, and `validate` checking every `agents/*/manifest.yaml` | `src/manifest/` | SPEC/01 §6, ruling d |
| `pack` (reproducible archive) and `verify` (every reason, exit 4) | `src/bundle/` | rulings g, h |
| Bootstrap stack: boundary, execution role, deploy role, developer role, `agentkeel-evals`, VPC, key, budget, tag-immutable ECR, the parameters the construct reads | `infra/bootstrap/` | a, b, d, e, f |
| `GovernedAgent`, Gateway and Identity declared and unwired | `infra/construct/governed_agent.py` | SCOPE, finding 17 |
| The checks that read S3 (both forms), S5 and S8, over the whole stack | `infra/construct/governed_agent.py` | SPEC/01 §5 |
| cdk-nag over both stacks, with the committed report held to that synth | `src/validate/checks.py` | q, r |
| Gateway endpoints for S3 and DynamoDB | `docs/adr/ADR-0006` | e |
| refagent at M01 scope: Sonnet 5, the rights table, `check_availability` | `agents/refagent/` | SCOPE |
| The agent runner; the Makefile writes the control card and refagent's envelope | `src/agent/run.py`, `Makefile` | l |
| The gate reads `thresholds.yaml` at the envelope's commit | `src/verdict/gate.py` | m |
| CloudTrail lookup of S4's and S6's request ids; the item 18 probe | `scripts/observe_attempt.py`, `evals.yml` | i, j |
| Pack, sign, verify, push, verify again, deploy, check at load | `.github/workflows/deploy.yml` | SPEC/01 §6 |

### Planted reasons

Each marker came off only when its test failed for the reason it was planted for. Verbatim:

```
S1  signature: no bundle.cosign.json beside tests/fixtures/bundles/unsigned
S2  digest: the bundle hashes to 3490a26a3c3a, signed 34275f772964
S3  [SeedS3ExtraEgress] SeedS3ExtraEgress/Refagent/Sg: egress to 0.0.0.0/0: a destination the
    manifest cannot name. The manifest lists AWS service names, and each is one endpoint of the
    platform's VPC (ruling d).
S3  [SeedS3ExtraEgressStandalone] SeedS3ExtraEgressStandalone/NotInTheManifest: egress to
    0.0.0.0/0: a destination the manifest cannot name. The manifest lists AWS service names, and
    each is one endpoint of the platform's VPC (ruling d). (added outside the construct)
S5  [SeedS5RoleWithoutBoundary] SeedS5RoleWithoutBoundary/NoBoundary: no permissions boundary.
    Every role the construct makes or is given carries the bootstrap stack's
    (/agentkeel/security/boundary-arn).
S8  [SeedS8OutsideConstruct] SeedS8OutsideConstruct/BareRuntime: an
    AWS::BedrockAgentCore::Runtime that is not a GovernedAgent's own runtime. An agent exists on
    this platform only as an instance of the construct (SPEC/01 §2).
S4  AssertionError: the attempt has not been made
S6  AssertionError: the attempt has not been made
```

S4's and S6's markers are **off**, because their reader landed in this PR (`scripts/observe_attempt.py` and `--check-attempt`). Both tests fail until the attempts are recorded. A strict `xfail` would have failed the measuring run the moment they were.

### The checks, and where each comes from

`F1_1` is read from two sources and passes only if both do: the S1, S2, S3 and S8 tests (`--check-cases`), and CloudTrail's record of S4's attempts (`--check-attempt`). `F1_2` is the S5 test. `F1_3` is CloudTrail's record of S6's attempt, and it requires the denial to name a resource-based policy. `F1_4` is the envelope's own goldens, worked out again by the gate. **An agent envelope missing any of the four is now refused by the gate**, because the Makefile builds those flags from variables and a missing one would otherwise read as a run that measured the claim.

### Counts, on this head

```
uv run pytest -q          149 passed, 2 failed, 1 skipped
                          the 2 are S4 and S6; the skip is the cosign test, on a machine
                          without cosign — CI installs it before pytest
uv run make validate      6 checks, all ok
uv run make plants        S1–S8 listed; every reader now in the tree
npx aws-cdk@2 synth       AgentkeelBootstrap: ok       AgentkeelRefagent: ok
```

cdk-nag, from the reports committed beside each `app.py`:

| Stack | Compliant | Suppressed | Non-Compliant | UNKNOWN |
|---|---|---|---|---|
| `AgentkeelBootstrap` | 21 | 16 | 0 | 0 |
| `AgentkeelRefagent` | 5 | 1 | 0 | 0 |

### Every suppression

Ruling r: a suppression on an IAM wildcard, a boundary rule or a key-policy rule names the seeded case it serves or the SPEC/01 §6 line that requires it. `make validate` fails on one that names neither, and it matches `seed S3`, not `S3` the service. Rows is the number of report rows the suppression covers.

| Rule | Resource | Rows | Reason |
|---|---|---|---|
| `AwsSolutions-IAM5` | `Boundary/Resource` | 4 | SPEC/01 §6: 'the permission boundary, on every role either stack synthesises, applied stack-wide'. This is that boundary, and it is what seed S5 reads: a role handed to GovernedAgent without it is refused at synth. A ceiling, not a grant: a Deny must cover every resource, including ones that do not exist yet, or a later attach slips past it. |
| `AwsSolutions-IAM5` | `ExecutionRole/DefaultPolicy/Resource` | 1 | SPEC/01 §6: 'the CloudFormation execution role the deploy passes, which carries the boundary and may create a role only with the boundary attached'. iam:CreateRole is scoped to /agentkeel/agents/ and conditioned on iam:PermissionsBoundary; the wildcard is in the Deny. It is half of what seed S4 reads. |
| `AwsSolutions-IAM5` | `DeployRole/DefaultPolicy/Resource` | 2 | SPEC/01 §6: 'the deploy role, trusted with StringEquals on aud, the immutable sub for refs/heads/main, and job_workflow_ref'. Seed S4 is an attempt to do from a laptop what only this role may do. cloudformation:* is scoped to stack/agentkeel-*; AWS appends the stack id suffix, which cannot be named in advance. |
| `AwsSolutions-IAM5` | `DeveloperRole/DefaultPolicy/Resource` | 5 | SPEC/01 §6: 'the developer role (§1), boundary on'. This is seed S4's principal. The Allow is read-only describe and list; the wildcard is in the Deny that refuses the deploy. |
| `AwsSolutions-IAM5` | `EvalRole/DefaultPolicy/Resource` | 1 | SPEC/01 §6: 'the eval role, absorbed from infra/eval-role/ under a new name, with its Deny statement (item 33) and trust conditions as they stand'. runtime/refagent* covers the versioned runtime name AgentCore assigns, which does not exist until the deploy. |
| `AwsSolutions-EC23` | `Vpc/EndpointBedrockRuntime/SecurityGroup/Resource` | 1 | SPEC/01 §6: 'a VPC with no internet gateway, endpoints with policies scoped to the account'. The rule cannot be resolved at synth: its source is the VPC's own CIDR, an intrinsic function. |
| `AwsSolutions-EC23` | `Vpc/EndpointKms/SecurityGroup/Resource` | 1 | as above |
| `AwsSolutions-EC23` | `Vpc/EndpointLogs/SecurityGroup/Resource` | 1 | as above |
| `AwsSolutions-IAM5` | `Refagent/Role/DefaultPolicy/Resource` | 1 | SPEC/01 §6, 'its own log group' and 'the agent's key': logs and kms actions are on `*` because the log stream does not exist until the runtime writes it and the key is reached through the grant. The boundary (S5) caps all four, and the key policy denies this role its own key policy (S6). |

Read those three `AwsSolutions-EC23` rows carefully: the rule did not evaluate and get waived, it **threw**, and a `CdkNagValidationFailure` suppression covered the throw. They are not evidence that inbound access was checked.

## Step 3 — the human's attempts, then the measurement

The human deploys `infra/bootstrap` with admin (`infra/bootstrap/README.md` has the commands), points `AWS_EVAL_ROLE_ARN` at `agentkeel-evals`, and attempts S4 and S6. Each attempt's request id, event name, timestamp and `AccessDenied` text go into `milestones/M01/runs/f1_1_laptop.yaml` and `f1_3_key_policy.yaml`; PR 2's CI run looks each id up in CloudTrail and writes `checks.F1_1` and `checks.F1_3`. A human-written file feeds no check by itself.

Row 1's measurement is the CI run on the head that is merged; earlier branch runs are recorded, not cited.

## What this PR does not show

- **No deploy has run.** `deploy.yml` is written and has never executed. The signature it would make, the image it would push and the load check it would run are untested, and `platform-architect` found that the deploy role and the execution role are, as written, too narrow to do what it asks (BLOCK B below). Row 1 does not rest on any of it.
- **The rights table is read from the file**, not DynamoDB, in this PR's measurement: refagent's stack deploys from `main` after this PR merges. Every observation records which source it read.
- **F1.4 reads existence, not correctness.** An answer passes the citation half if its `table_row` and `clause_id` exist in `data/`; neither is compared with the golden's expected pair. That is SPEC/01 §4 as written. Row 1's measured cell must not be read as "refagent cites correctly".
- **S8's check is installed by the stack under test.** A stack that never imports `infra.construct` is not checked (BLOCK D).

## The five seat reports, verbatim

### `security-reviewer`

## security-reviewer — M01 PR 2 (PR #8, `m01-pr2` → `main`), Security-owned paths

A report, not a ruling. Read: the tree at `m01-pr2`, `SPEC/00-overview.md` §3 §5 R3 R4 R5, `SPEC/01-signed-bundle.md` §5 §6 §9 §10, `milestones/M01/feasibility.md` §2.6 (a–r), `docs/adr/ADR-0006-gateway-endpoints-for-s3-and-dynamodb.md`, both committed NagReport CSVs. Nothing in this diff has been deployed or run against AWS, so no control below is described as working.

### BLOCK

**B1. The boundary denies `kms:GetKeyPolicy`, so seed S6 cannot show that the key policy is what refuses.** `infra\bootstrap\app.py:146` puts `"kms:GetKeyPolicy"` in the boundary's Deny; `milestones\M01\runs\f1_3_key_policy.yaml:17-20` says the attempting role is created "under the same path `/agentkeel/agents/`, **with the boundary attached** and `kms:GetKeyPolicy` on the key in its own policy … so a refusal can only come from the key policy". Both statements cannot be true: the boundary refuses the call on its own. `src\verdict\build.py:274` passes the check on `attempt.get("error_code") == "AccessDenied"` and never reads `error_message`, so `checks.F1_3` would read `pass` with the key policy's Deny (`infra\bootstrap\app.py:331-338`) deleted outright. F1.3 as wired cannot fail. What would settle it: take `kms:GetKeyPolicy` out of the boundary Deny (it is not in SPEC/01 §6's list and not in SPEC/00 §8 M05's five), or make S6's attempt with a role under the agent path and no boundary, and make `check_from_attempt` require the message to name an explicit deny in a resource-based policy. Security seat rules the boundary; SPEC/01 §5 S6 is the line.

**B2. A fork PR turns the only required measurement check green without running it.** `.github\workflows\evals.yml:68`: `if: github.event_name == 'push' || github.event.pull_request.head.repo.full_name == github.repository`. `infra\ruleset\main.json:1` makes `evals` a required status check. A job skipped by `if:` reports `skipped`, which branch protection counts as success. So a PR from a fork merges with no `make validate` (workflow hash, manifest schema, cdk-nag), no pytest, no envelope. The comment at `evals.yml:67` ("A fork gets no OIDC token. Skip it; do not fail it.") is right about the token and wrong about the consequence. What would settle it: a second job with no AWS step that runs `make validate` and `pytest` on fork PRs and is the required context, or a job that fails on a fork PR. `bypass_actors: []` (`infra/ruleset/main.json:1`) is doing its work; this path goes around it without a bypass. If Security rules it a carried finding instead, name M02 and say so in the PR body.

### FINDING

**F1. S4's three attempts are refused by the developer role's own Deny, not by the deploy role's trust policy.** `infra\bootstrap\app.py:269-276` denies `sts:AssumeRole`, `cloudformation:CreateStack` and `UpdateStack` on the developer role itself; `milestones\M01\runs\f1_1_laptop.yaml:20-31` makes exactly those three calls. `check_from_attempt` reads only `AccessDenied`, so the trust conditions at `app.py:238-239` (`sub`, `aud`, `job_workflow_ref` with `StringEquals`) are never the thing that refuses and could be relaxed without S4 noticing. SPEC/01 §5 S4 names three readers; only one of them fires. Settle: add a fourth attempt from a principal with no explicit Deny of its own, so the refusal is the trust policy's.

**F2. `GovernedAgent` reads two SSM parameter names that nothing writes.** `infra\construct\governed_agent.py:36` sets `ENDPOINT_PARAM = "/agentkeel/security/endpoint/{name}"` and line 114 uses it for every name in `endpoint_allowlist`, including `s3` and `dynamodb`. `infra\bootstrap\README.md:54` and `ADR-0006:63` write those two as `/agentkeel/security/prefix-list/s3` and `…/dynamodb`. `infra\bootstrap\app.py:454-460` publishes parameters for the three interface endpoints only. refagent's manifest lists all five (`agents\refagent\manifest.yaml:36-41`), so the refagent stack cannot deploy as written. Fail-closed, so nothing widens; but the deploy path is untested and the names disagree with the ADR. Settle: one name, in `governed_agent.py` or in the ADR and README, plus a synth test that names the parameter path.

**F3. The egress allowlist for the two gateway endpoints is whatever the SSM parameter says.** `governed_agent.py:113-120` builds `approved` from the same parameter values it builds the rules from, and `_egress_refusal` (`governed_agent.py:344-348`) then compares the rule's destination against that list. For a destination whose value is written by hand (F2), the S3 check cannot disagree with it. ADR-0006's "a wrong value there widens nothing" holds only because the endpoint policy and the boundary still apply — say that in the PR body rather than letting the synth check carry it.

**F4. `deploy.yml` writes an unbounded value into `$GITHUB_OUTPUT` and then interpolates it into a `run:` in the job that holds AWS credentials.** `.github\workflows\deploy.yml:80`: `echo "digest=$(awk '{print $1}' pack.out)" >> "$GITHUB_OUTPUT"` — `awk` prints field 1 of *every* line, and there is no heredoc delimiter, so more than one line of output sets more than one output. `.github\workflows\deploy.yml:150`: `tag="${{ needs.sign.outputs.digest }}"` is expanded by the runner before bash sees it. `src\bundle\pack.py:87` prints one line today; that is the only thing between this and command execution in the deploy job. Settle: `awk 'NR==1{print $1}'`, pass the value as an `env:` and use `"$TAG"`.

**F5. The CloudFormation execution role cannot create refagent's stack, and three deploy steps are outside the deploy role's policy.** `infra\bootstrap\app.py:196-209` grants the execution role `iam:CreateRole`, `PutRolePolicy`, `AttachRolePolicy` under `/agentkeel/agents/` and nothing else — no DynamoDB, EC2, Bedrock, AgentCore, SSM or CloudFormation. `deploy.yml:167` reads `describe-stacks --stack-name AgentkeelBootstrap`, which does not match the deploy role's `stack/agentkeel-*/*` (`app.py:247`, case-sensitive). `deploy.yml:172` calls `load_rights_table.py` and `deploy.yml:183` invokes the runtime; the deploy role has neither `dynamodb:*` nor `bedrock-agentcore:InvokeAgentRuntime` (that one is on the eval role, `app.py:302-306`). Fail-closed again. It means the deploy job's least-privilege story is a template, not a measurement. `infra\bootstrap\README.md:77-83` already says nothing here has been deployed; keep that sentence and add these four gaps to it.

**F6. "Only Security may change this key" names a principal the stack does not create.** `infra\bootstrap\app.py:345-348`: the Deny is `ArnNotLike` on `arn:aws:iam::<account>:role/agentkeel-security` and `…:root`. No `agentkeel-security` role exists in this stack or anywhere in `infra/`. In practice the only principal that can change the key policy is the account root, the break-glass admin SPEC/01 §1 puts out of scope. The deploy role and the execution role are denied, which is R4's first half — and SPEC/01 §9 already lists that as a control with no seeded case, so no document may call it proven. Settle: create the role, or rewrite the sid and the docstring at `app.py:322` to say "root only, until Security has a role".

**F7. Anyone with write can switch the eval role's gate off from inside, and nothing stops them yet.** `.github\workflows\evals.yml:44-46` says so; `infra\workflows.sha256:5` says so; both are right. The trust condition at `infra\bootstrap\app.py:79` is `StringLike` on `…/evals.yml@refs/pull/*/merge`, so the token a PR gets is the token for the `evals.yml` that PR just rewrote. `infra/workflows.sha256` is a file in the same PR. The deploy role is narrower — `StringEquals` on `deploy.yml@refs/heads/main` (`app.py:82`, `app.py:238-239`) — but the contents of `deploy.yml` on `main` are whatever the last merge made them. Answer to "who can edit the check and is that edit gated": anyone with write, and the only gate is the required `evals` check, which B2 shows a fork PR skips. M02 is where this is meant to close (`SPEC/01` §11); say it plainly in the PR body.

**F8. The bot authorship that makes an envelope evidence can be minted by the PR under test.** `.github\workflows\evals.yml:12-17` states the gap. Concretely: the `record` job (`evals.yml:238-276`) downloads the artifact the first job produced by running the PR's own `make evals`, copies it into `evals/history/` and commits it as `github-actions[bot]` (`evals.yml:272-275`). CLAUDE.md treats `github-actions[bot]` authorship under `evals/history/` as part of what makes an envelope evidence. Not new in this diff; new in that PR 2 is the first envelope that carries claim 1's checks. `two-key` on a human commit there is M02; this is not a human commit.

**F9. The check that enforces ruling r can be satisfied by the word "S3" meaning the AWS service.** `src\validate\checks.py:305`: `re.search(r"\bS[34568]\b", reason)`. A suppression whose reason reads "the S3 gateway endpoint" passes without naming seed S3. Settle: match `seed S3` / `S3 (`, or require an explicit `seeds:` field in the suppression reason. Engineering owns the file; the ruling it implements is Security's (feasibility §2.6 r).

### NOTE

**N1. Workflows, the mechanical part, are clean.** `permissions: {}` at the top of all three files (`deploy.yml:44`, `evals.yml:59`, `sign-fixture.yml:38`) with per-job grants: `deploy.yml:60-62` and `104-107` are `contents: read` + `id-token: write`; `evals.yml:71-75` adds `checks: read` and `pull-requests: read`, which `observe_pr_check.py` needs. Every third-party action is pinned to a 40-character SHA with the version in a trailing comment. No `pull_request_target` anywhere. No `secrets.*` reference anywhere; the two role ARNs come from `vars.` (`deploy.yml:133`, `evals.yml:158`), which a fork can read and cannot use without a token. `persist-credentials: false` on every checkout except the two that must push (`evals.yml:252`, `sign-fixture.yml:55`). The only untrusted-looking value in a `run:` is F4's.

**N2. Default-deny egress is in the code and has not fired in CI.** `governed_agent.py:107-110` builds the group with `allow_all_outbound=False`; `governed_agent.py:118` adds one rule per manifest name on tcp 443; `_egress_refusal` (`governed_agent.py:336-352`) refuses a CIDR, a missing destination (read as `0.0.0.0/0`, SPEC/01 §6), a destination outside the list and any port but 443, and `_egress` (`governed_agent.py:265-286`) walks the whole stack so a separate `CfnSecurityGroupEgress` naming the group is caught too. The VPC has `nat_gateways=0`, `PRIVATE_ISOLATED` only and flow logs (`infra\bootstrap\app.py:158-167`), and every endpoint policy is scoped to `aws:ResourceAccount` (`app.py:171-175`). None of this has run against S3's two fixtures in CI on this branch, so no sentence should call it proven.

**N3. The boundary's Allow is wider than the agent role needs.** `infra\bootstrap\app.py:136-139` allows `bedrock-agentcore:*` on `*`, so cross-agent `InvokeAgentRuntime` is inside the ceiling for every platform role. The construct's agent role does not grant it (`governed_agent.py:159-173`), so nothing reaches it today. "No shared surfaces" is M05's claim.

**N4. The agent role carries no explicit Deny; it is capped by omission.** SPEC/00 §8 M05 asks the agent role to deny `iam:*`, `bedrock:*Guardrail*`, `logs:Delete*`, `sts:AssumeRole`, `s3:PutBucketPolicy`. The boundary's Deny (`app.py:144-148`) names three IAM actions, not `iam:*`, and does not name `sts:AssumeRole`; both are excluded instead by not appearing in the Allow at `app.py:136-139`. The eval role's own Deny does carry all five (`app.py:77`, `app.py:307-310`). A later widening of the boundary's Allow would therefore hand an agent role `iam:*` with nothing else in the way. M05 is where this is claimed; worth writing down now.

**N5. `governed_agent.py:169-173` grants `logs:*` and `kms:Decrypt`/`GenerateDataKey` on `*`.** The suppression says why (log stream does not exist yet, key reached by grant) and the boundary caps both. Accurate. It also means the agent role can decrypt any key in the account that grants it — the key policy at `app.py:325-330` allows the agent path, and no other key exists yet.

**N6. R5 is not in this milestone and nothing here pretends otherwise.** No Object Lock, no compliance mode, no seven-year retention, no security account: cut 2, `SPEC/01` §10, and SPEC/00 §8 M05. `evals/history/` is a git path, not a write-once store. No retention value changes in this diff, so `two-key` is not engaged.

**N7. cdk-nag, every suppression, and whether its reason is specific.** All eight are `add_resource_suppressions_by_path`, one per resource; no stack-wide suppression. Every reason quotes a SPEC/01 §6 line, and five also name a seed. Ruling r is met on all eight.
- `infra\bootstrap\app.py:479-483` Boundary/Resource, IAM5 — §6 quote + S5. Specific.
- `app.py:484-490` ExecutionRole/DefaultPolicy, IAM5 — §6 quote + S4, names the scoping and the `iam:PermissionsBoundary` condition. Specific.
- `app.py:491-496` DeployRole/DefaultPolicy, IAM5 — §6 quote + S4, explains `stack/agentkeel-*`. Specific.
- `app.py:497-501` DeveloperRole/DefaultPolicy, IAM5 — §6 quote + S4. Specific.
- `app.py:502-507` EvalRole/DefaultPolicy, IAM5 — §6 quote, no seed, explains `runtime/refagent*`. Specific; the §6 line is the one it needs.
- `app.py:515-522` three endpoint security groups, `CdkNagValidationFailure` — §6 quote, explains that the rule cannot resolve an intrinsic. Specific.
- `infra\construct\app.py:60-68` Refagent/Role/DefaultPolicy, IAM5 — §6 quote + S5 + S6. Specific.

Read the CSV carefully: `infra\bootstrap\AwsSolutions--AgentkeelBootstrap-NagReport.csv:10,12,14` show Rule ID `AwsSolutions-EC23`, Compliance `Suppressed`. EC23 did not evaluate and get waived; it threw, and the `CdkNagValidationFailure` suppression covered the throw. Nobody should read those three rows as "inbound access checked".

**N8. "The committed CSV is the one the synth wrote" is mechanically enforced.** `src\validate\checks.py:274-282` re-synths both apps into `cdk.out`, byte-compares the rows (`_rows`, line 286) and fails with "not the report this synth wrote". So ruling q holds without my re-running it. Two gaps in the same function: `_nag_rows` (`checks.py:296-300`) fails only on `Non-Compliant` and inspects reasons only on `Suppressed`, so any other compliance value — an unsuppressed validation failure among them — passes silently; and `check_cdk_nag` synthesises with `AGENTKEEL_IMAGE_DIGEST` unset, so the report is always of the placeholder-digest stack (`governed_agent.py:45`), never of what deploys.

**N9. `src\bundle\verify.py:162` `--measure <identity>` accepts any identity given to it.** Not reachable from `deploy.yml` (lines 90, 129, 180 all call `verify` with no flag), which is what ruling g requires. It is one flag away from being reachable, and F7 is who could add it.

**N10. `sign-fixture.yml` keeps `contents: write` + `id-token: write` after its one job is done.** Its only guards are `head.ref == 'm01-pr2'` (line 45), same-repo (line 44) and the "Already signed?" step (line 59-66). Its certificate identity is refused for a deploy by `verify.py:48`. Consider deleting the file at PR 3 or 4 and taking its line out of `infra\workflows.sha256:10`.

**N11. `infra\bootstrap\app.py:412-413` is a stray comment block at column 0 inside the class body**, pasted from `infra\construct\app.py:48-49`. Python's tokenizer ignores comment-only lines, so `_image_repository` and `_parameters` are still methods and the stack synthesises; a reader scrolling past it will think they are module-level functions.

**N12. `infra\workflows.sha256:8-9` carries new hashes for `deploy.yml` and `evals.yml`,** and the header says the list and the workflows can be edited in one PR. Consistent with F7; I did not recompute the hashes (`make validate` does, `checks.py:209-213`).

BLOCK: 2 · FINDING: 9 · NOTE: 12

---

### `platform-architect` (on S3, S5 and S8)

## platform-architect report — M01 PR 2, construct and bootstrap (S3, S5, S8)

Read: `infra/construct/governed_agent.py`, `infra/construct/__init__.py`, `infra/construct/app.py`, `infra/bootstrap/app.py`, `infra/bootstrap/README.md`, the four fixtures under `tests/fixtures/construct/`, `tests/test_m01_seeds.py`, `tests/test_construct.py`, `src/validate/checks.py` (cdk-nag check), `.github/workflows/deploy.yml`, `Makefile`, `milestones/M01/runs/f1_1_laptop.yaml`, `f1_3_key_policy.yaml`, SPEC/00 §2 §3 §5 §6 §8-M01 §12 R3–R5, SPEC/01 §5 §6 §9 §10, `milestones/M01/feasibility.md` §2.6, `docs/adr/ADR-0006-gateway-endpoints-for-s3-and-dynamodb.md`. No file edited. This is a report, not a ruling.

### Short answer to the question asked

S3 form 1 and S5 are genuinely read: the construct installs the validation on its own stack, so a rule added to `agent.security_group` and a role handed in without a boundary are refused whether or not the caller cooperates. S3 form 2 is read only for the typed class `ec2.CfnSecurityGroupEgress`. S8 is read only because the seed asks to be read: `tests/fixtures/construct/outside_construct.py:25` `refuse_outside_construct(stack)`. Remove that line and the bare runtime synthesises.

### BLOCK

BLOCK 1 · The allow-list boundary is applied to the deploy-plane roles, so the deploy path as written cannot run. `infra/bootstrap/app.py:103` `iam.PermissionsBoundary.of(self).apply(boundary)` covers every role built after it. The boundary's only Allow is `infra/bootstrap/app.py:136-138` (`bedrock:Invoke*`, `bedrock-agentcore:*`, `dynamodb:GetItem`, `dynamodb:Query`, `kms:Decrypt`, `kms:GenerateDataKey`, `logs:CreateLogStream`, `logs:PutLogEvents`, `s3:GetObject`, `cloudformation:Describe*`, `sts:AssumeRoleWithWebIdentity`). Effective permission is the intersection, so: the deploy role's `cloudformation:CreateChangeSet`/`ExecuteChangeSet`/`CreateStack` and `iam:PassRole` (`app.py:244-252`) are capped to nothing; the execution role's `iam:CreateRole`, `PutRolePolicy`, `AttachRolePolicy` (`app.py:196-201`) are capped to nothing, and it has no Allow at all for `ec2:CreateSecurityGroup`, `dynamodb:CreateTable`, `bedrock:CreateApplicationInferenceProfile`, `bedrock-agentcore:CreateAgentRuntime`, `ssm:GetParameters`; the Budgets action role's `iam:AttachRolePolicy` (`app.py:376-377`) is capped, so the `daily_usd: 10` stop cannot attach; the VPC flow-log role created at `app.py:166` needs `logs:DescribeLogStreams` and `iam:PassRole`, neither in the boundary, so flow logs likely never deliver. SPEC/01 §6 says the execution role "may create a role only with the boundary attached" — with this boundary on itself it may create none. Settles it: either a deploy-plane boundary separate from the agent boundary, or the deploy-plane actions added to the Allow, plus one observed deploy or `simulate-principal-policy` table in the record. Seat: Security.

BLOCK 2 · The S8 check is opt-in, so what fired is "a stack that installs the checks refuses a bare runtime", not "an agent runtime cannot be synthesised without `GovernedAgent`". `tests/fixtures/construct/outside_construct.py:25` calls `refuse_outside_construct(stack)`; `infra/construct/governed_agent.py:365-372` installs on one stack only; `src/validate/checks.py:239-242` synthesises exactly two apps (`AgentkeelBootstrap`, `AgentkeelRefagent`) and nothing scans the tree or `cdk.out/*.template.json` for `AWS::BedrockAgentCore::Runtime`. A third app, a second stack in either app, a `Stage`, or a stack that omits the one line is not checked. False state 8 (SPEC/01 §3) is "an agent runtime is synthesised without `GovernedAgent`" — unqualified. Settles it: a check that does not depend on the stack cooperating (over every synthesised template in the repo, or a repo scan for the resource type and for CDK apps under `infra/**`), and a seeded case that is a stack which does **not** call `refuse_outside_construct` and is still caught. Until then `checks.F1_1` should not be read as covering S8's general form. Seat: Security.

BLOCK 3 · S3 form 2 is matched by Python class, not by CloudFormation type, so the same rule written as a raw resource is missed. `infra/construct/governed_agent.py:274` `if not isinstance(node, ec2.CfnSecurityGroupEgress): continue`. The seed uses that exact class (`tests/fixtures/construct/extra_egress_standalone.py:18`). `cdk.CfnResource(stack, "X", type="AWS::EC2::SecurityGroupEgress", properties={...})` — the same shape S8's own seed uses at `outside_construct.py:16-24` — is not an instance of it and is never examined. SPEC/01 §3 false state 3 says "however the rule is added". The S8 check next to it does this correctly: `governed_agent.py:319-326` matches on `cfn_resource_type`. Settles it: match on `_resource_type(node) == ec2.CfnSecurityGroupEgress.CFN_RESOURCE_TYPE_NAME` and read properties generically, plus a seed in that form. Seat: Security.

### FINDING

FINDING 1 · S5's second half has no seeded case. `infra/construct/governed_agent.py:304-306` refuses "a permissions boundary that is not the bootstrap stack's", but the only fixture is `role_without_boundary.py`, and SPEC/01 §3 false state 5 is "no permission boundary, **or has a different one**". No case shows that branch firing; SPEC/00 §10.5 forbids calling it working. Settles it: a second fixture handing a role with another managed policy as its boundary.

FINDING 2 · S6 has two explicit denies and the run file demands one of them by name. The key policy denies `kms:GetKeyPolicy` to the agent path (`infra/bootstrap/app.py:331-338`) and the boundary denies the same action to every platform role (`app.py:146` `"kms:GetKeyPolicy"`). `milestones/M01/runs/f1_3_key_policy.yaml:17` says the attempt is made with a role "with the boundary attached", and `:31` requires "AccessDenied with an explicit deny in a resource-based policy"; `tests/test_m01_seeds.py:84` asserts `"resource-based policy" in attempt["message"]`. If AWS names the permissions boundary instead, S6 fails on a working control. Settles it: drop `kms:GetKeyPolicy` from the boundary Deny (the key policy is the control under test, SPEC/01 §5 "the refusal can only be the key policy's explicit deny"), or re-rule `refused_when` and the assertion. Seat: Security.

FINDING 3 · The two gateway-endpoint parameters are written under one name and read under another. `infra/construct/governed_agent.py:36` `ENDPOINT_PARAM = "/agentkeel/security/endpoint/{name}"` is used for all five names at `:114-115`; `infra/bootstrap/README.md:54` writes `/agentkeel/security/prefix-list/$service`, and `ADR-0006:63-64` says the same. The agent stack will fail at deploy on a missing parameter. It fails closed, so it widens nothing; it does mean ADR-0006's "until they exist an agent stack does not deploy" is permanently true as written.

FINDING 4 · A runtime placed inside the construct's scope passes the S8 check with any properties. `infra/construct/governed_agent.py:319` `if not any(isinstance(scope, GovernedAgent) for scope in node.node.scopes)`. `agentcore.CfnRuntime(agent, "Extra", network_configuration=...PUBLIC..., role_arn=<any>)` is inside a `GovernedAgent` scope and is accepted — public network mode, any role, no boundary check, no security group. The check tests location in the tree, not that the resource is the construct's own `self.runtime`. Settles it: compare identity (`node is scope.runtime`), plus a seed in that form.

FINDING 5 · Every check reads CDK's typed properties, never the synthesised template. `governed_agent.py:270` `cfn.security_group_egress` and `:300` `cfn.permissions_boundary`. `node.default_child.add_property_override("SecurityGroupEgress", [...])` or `add_property_override("PermissionsBoundary", "<weak arn>")` changes the template at render time and leaves both getters as they were, so S3 form 1 and S5 both pass while the deployed template carries the rule. `tests/test_construct.py:62` shows the stronger reading (the template JSON) but only for the blessed stack and only in a test. Settles it: validate against `Template.from_stack`/the rendered resource, or state the limit in the construct's docstring.

FINDING 6 · The deploy role cannot do what `deploy.yml` asks of it, beyond BLOCK 1. `.github/workflows/deploy.yml:138-152` logs into ECR and pushes an image as the deploy role; `infra/bootstrap/app.py:242-253` grants it CloudFormation and `iam:PassRole` only — no `ecr:GetAuthorizationToken`, `ecr:PutImage`, `ecr:UploadLayerPart`, and no `ssm:GetParameters` for the `AWS::SSM::Parameter::Value<...>` parameters the template carries (`governed_agent.py:227`, `:202`). `aws cloudformation deploy` also calls `DescribeChangeSet` and `GetTemplateSummary`, neither granted.

FINDING 7 · The checks reach exactly `Stack.of(construct).node.find_all()`. `governed_agent.py:79-80`, `:273`. A `CfnSecurityGroupEgress` in a sibling stack naming the agent's group (cross-stack export) is out of reach, and so is a bare runtime in a parent or sibling stack. Nested stacks below the construct's stack are in reach. Worth one sentence in the docstring, which today claims the checks are "over the whole stack" without saying which stack.

FINDING 8 · The construct is the only way in at synth, and nothing in the account says so. There is no SCP, and the boundary's Allow includes `bedrock-agentcore:*` (`infra/bootstrap/app.py:137`), so a platform role whose own policy were widened could call `CreateAgentRuntime` directly, outside CloudFormation and outside the construct. Today no role's own policy grants it, and the developer role denies it explicitly (`app.py:274`). The account-level answer is landing-zone work (deferred, below). Settles it for M01: say so in `infra/construct/__init__.py`, which currently reads "An agent exists on this platform only as an instance of this construct" with no scope qualifier.

FINDING 9 · The key policy names a principal that exists nowhere. `infra/bootstrap/app.py:346` `arn:aws:iam::{account}:role/agentkeel-security`; `grep` finds it in no other file. In practice only account root is outside the `ArnNotLike` deny at `:345-348`, so the human with admin cannot change the key policy unless they are root. R4 is served either way; the reader of the template is misled.

FINDING 10 · Controls with no seeded case, carried. SPEC/01 §9 pre-declares seven; they are unchanged by this PR: the deploy role unable to alter a key policy (enforced in three places — key policy `app.py:339-349`, boundary Deny `app.py:146`, execution role Deny `app.py:205-206` — and fired in none), the boundary on roles the stacks create, no internet or NAT gateway, endpoint policies scoped to the account, the Budgets action, the eval role's two refusals, log delivery to the security account. Add to that list: the deploy path itself. `.github/workflows/deploy.yml:28-33` says it plainly — "**No deploy has run.**" Nothing in the deploy workflow, the deploy role's trust, the execution role, the ECR immutability or the image-digest pin has fired on anything. No prose may call any of them working (SPEC/00 §10.5). The construct's checks run at synth in CI; CloudFormation receives a template (`deploy.yml:163-169`) and re-runs nothing.

### NOTE

NOTE 1 · `governed_agent.py:349` compares `toPort` only: `tcp 1-443` to an approved endpoint is accepted. `fromPort` is read in the message but not in the test.

NOTE 2 · The endpoint security groups admit the whole VPC CIDR on 443 (suppression at `infra/bootstrap/app.py:515-522`), not the agent's group. The agent's egress list is the only thing scoping which endpoints it reaches, and that is a synth-time control.

NOTE 3 · Endpoint policies allow every action, scoped by account: `infra/bootstrap/app.py:171-175` `actions=["*"], resources=["*"]` with `aws:ResourceAccount`. That is what SPEC/01 §6 asks for; it means any workload in the VPC can reach any bucket or table in the account through the endpoint, subject to IAM.

NOTE 4 · The docstring's reason for the placement is wrong about the mechanism. `governed_agent.py:237-240` and `infra/construct/__init__.py:13-18` say the validation runs "after every aspect — after `PermissionsBoundary.of(stack).apply(...)` has written the boundary". In this `aws-cdk-lib`, `PermissionsBoundary.of().apply()` sets the context key `@aws-cdk/core:permissionsBoundary`, read by the `Role` constructor; it is not an aspect and does not reach a role built before the call. The placement still works. The sentence should not be relied on by the next reader.

NOTE 5 · Stray comment block inside the class body: `infra/bootstrap/app.py:412-414`, "A fixed output directory, so `make validate` reads the NagReport…" sits above `_image_repository`, duplicated at `:463`. Cosmetic.

NOTE 6 · `tests/test_construct.py:88` asserts every role in the refagent template is at `/agentkeel/agents/`. True today; it breaks the moment CDK adds any service role to that stack, which is a test failure rather than a finding.

NOTE 7 · `cdk.out/` is gitignored (`.gitignore:222`), and `tests/test_construct.py:62` reads `infra/construct/cdk.out/AgentkeelRefagent.template.json`. CI runs `make validate` first (`.github/workflows/evals.yml:123` before `:137`); a fresh local `pytest` fails on the missing file.

NOTE 8 · `infra/bootstrap/app.py:193` trusts `cloudformation.amazonaws.com` with no `aws:SourceArn`/`aws:SourceAccount` condition on the execution role. One account, and `iam:PassRole` on it is held only by the deploy role (`app.py:249-252`) plus admin, so the exposure is small.

NOTE 9 · Two accounts, with boundaries (R3): nothing here assumes more than two. M01 touches the agent account only (SPEC/01 §10 cut 2); the security account is named and not reached. Every role the platform creates carries the boundary — the bootstrap's five plus the flow-log role are covered because `app.py:103` precedes every `iam.Role` in the stack, and the construct's own role sets it explicitly at `governed_agent.py:154-155`. The one uncovered case is a role created in the agent stack by anything other than the construct; SPEC/01 §9 already carries that as a control with no seeded case, and the refagent stack has no such role today.

NOTE 10 · Who could create or update an agent stack, and whether the spec admits it: the deploy workflow on `main` over OIDC (`app.py:232-241`, admitted, never run); the human with admin who deploys the bootstrap stack (`infra/bootstrap/README.md:7-10`, admitted at `:15-18` and deferred to an SCP); account root (`app.py:347`, admitted only implicitly, by the key policy carve-out); the CloudFormation service through `agentkeel-cfn-exec`, reachable by anyone holding `iam:PassRole` on it (deploy role and admin). The developer role is denied by name (`app.py:269-276`) and by S4's three attempts (`milestones/M01/runs/f1_1_laptop.yaml:19-31`, `observed: null`). The eval role holds `bedrock-agentcore:InvokeAgentRuntime` only (`app.py:302-306`).

### Deferred items — landing zone, not defects

- **Service control policies** (stop the break-glass admin; forbid `bedrock-agentcore:CreateAgentRuntime` and `ec2:AuthorizeSecurityGroupEgress` outside CloudFormation). Out of scope: SPEC/00 §2 "Not a production landing zone", §12. The PoC instead makes the boundary an allow-list on every platform role, refuses at synth in the two apps in the repo, and names the admin as out of scope at `infra/bootstrap/README.md:15-18`.
- **Account vending, account-per-team, Control Tower.** Out of scope: SPEC/00 §2 and R3 ("agent account plus security account"), §12 first bullet. The PoC runs one agent account; containment numbers do not transfer, and SPEC/05 is required to say so.
- **Centralised networking** (transit gateway, shared VPC, egress inspection). Not in the two-account picture of §2. The PoC gives one isolated VPC, `nat_gateways=0`, `PRIVATE_ISOLATED` only (`infra/bootstrap/app.py:158-167`), three interface and two gateway endpoints (ADR-0006).
- **Org-wide CloudTrail and log archive in the security account.** SPEC/01 §10 cut 2, M05. The PoC keeps flow logs in the agent account (`app.py:166`) — see BLOCK 1 for whether they deliver.
- **`data_class` and residency enforcement; DSAR; multi-region and DR.** SPEC/00 §12. Informational fields only at M01.
- **Root account guard.** One account cannot deny root; `app.py:345-348` carves it out. An org SCP is the only bound, and that is landing-zone work.

`BLOCK: 3 · FINDING: 10 · NOTE: 10`

---

### `threshold-owner`

## Threshold Owner review — M01 PR 2 (branch `m01-pr2`)

No Bash tool in this seat, so I read the branch tree rather than a literal `git diff main...m01-pr2`. Everything below quotes a file and line as it stands on the branch. This is a report, not a ruling.

### The four answers asked for

**1. Should `thresholds.yaml` have changed in this PR? No — not yet.**
`thresholds.yaml:20` `tokens_per_run: 150000` is unchanged: direction **sideways**. That is what ruling o says (`milestones\M01\feasibility.md:325`: "stays 150,000 until PR 2's first agent envelope is recorded"). The last move (20000 → 150000, **upward = a relaxation**, per `thresholds.yaml:10` "Relaxes upward: a higher number needs two keys") happened at PR 1 and both keys are on `main`: `milestones\M01\rulings\pr1-threshold-owner.md:25` and `milestones\M01\rulings\pr1.md:179`. No bar in this PR moved down; R10's N is untouched. So no new two-key event — but see the BLOCK: the PR still owes the re-rule file.

**2. Ruling m in `gate.py` — the reasoning holds; the fallback is not fully silent-proof.**
`src\verdict\gate.py:87-101` reads `git show <commit>:thresholds.yaml`, `gate.py:103-111` turns it into the cap. Reading the cap at the envelope's commit is right: it is the cap `build` used when it wrote that envelope (`src\verdict\build.py:366-367`), so gate and build can still disagree without the bar moving under them. Keeping the pinned base hash on the tree (`gate.py:165`) is also right and for the stated reason: the base is frozen, so a change must reject every envelope naming the old one, loudly. The fallback is where it leaks — see FINDING 1 and 2.

**3. What the Threshold Owner needs before re-ruling the cap (ruling o).**
From the first agent envelope: `tokens_in + tokens_out`; the control's share (its card) against the agent's, so the two subjects can be separated; from `evals/history/<commit>.agent-raw.json`, the per-golden `usage` and the length of `tool_calls`, which says whether `MAX_TOOL_CALLS` is binding or slack; and whether any observation carries `error` (those count zero, so the total under-reads). Then a headroom factor stated as a number, and the file. If the re-rule moves the number **up**, that is a relaxation and needs a second key, as at PR 1.

**4. Can the cap be breached, and what happens?**
`agents\refagent\agent.py:40` `MAX_TOOL_CALLS = 2` with the loop `for _ in range(MAX_TOOL_CALLS + 1)` at `agent.py:139` — at most three Converse calls per golden, messages accumulating, system prompt ~750 tokens (`agents/refagent/prompt.txt`, 43 lines) plus the tool schema on every request, `maxTokens: 1024` (`agent.py:39`). Fifteen goldens. Typical two-call golden ≈ 2.5k tokens → ~38k; plus the control, measured at 5,644 (`evals\history\5b91750828c70f92e2cb41906d28ef1a63c56c85.json:14,144`) → ~44k, under a third of the cap. Pathological (three calls, output ceiling hit each time) ≈ 7.3k per golden → ~110k + control ≈ 116k, about 77% of 150000. So a breach is not expected and is not impossible: more than one `toolUse` block per turn (`agent.py:152-165` handles a list) or any re-run inside one `make evals` would close the gap. If breached, `build.py:366` writes RED, `gate.py:236-238` reads RED again, the job exits 1 and the record job still commits it (`.github\workflows\evals.yml:243`). Row 1 would then be RED for spend, not for the claim — and by ruling m that RED cannot be re-ruled later at that commit (FINDING 5).

### Findings

BLOCK · `milestones\M01\rulings\pr2-threshold-owner.md` does not exist; `milestones\M01\rulings\pr2.md:3-5` says the Threshold Owner "re-rules the cap and refagent's model version against this PR's first agent envelope, in rulings/pr2-threshold-owner.md, which carries the same `pr`", and rulings o and p (`feasibility.md:325-326`) promise the same. No agent envelope is in `evals/history/` yet, so the input does not exist either. Settled by: the first CI agent envelope, then that file, citing its `tokens_in + tokens_out` and either holding 150000 or moving it (a move up needs a second key). Threshold Owner rules.

FINDING · `src\verdict\gate.py:98` returns the working-tree cap when git cannot resolve the commit, and `gate.py:315` (`cap, _ = cap_at(...)`) drops `where`, so `measured_at`/`src\ledger.py:60` records a Measured cell that cannot say which cap ruled. Only `gate.py:386-387` prints it, and only in `main()`. The evidence path is safe today because `.github\workflows\evals.yml:85` checks out `fetch-depth: 0`; nothing holds it there. Settled by: refusing the fallback unless asked for it explicitly, or putting the cap and its provenance in the cell. Threshold Owner on what the cell must say; Engineering writes it.

FINDING · `src\verdict\gate.py:95` `git show <commit>:thresholds.yaml` resolves any object in the repo, including a commit that never landed on `main`. A branch that raises the cap, records an envelope at that commit, then reverts the cap before merge, leaves an envelope ruled forever under a cap that `main` never carried. The workflow does an ancestry check for reuse (`evals.yml:98` `git merge-base --is-ancestor`); the gate does not. Settled by: the same ancestry check in `cap_at`, or a stated ruling that an envelope is ruled under its own commit's cap whatever that was. Threshold Owner rules; Engineering writes it.

FINDING · `src\verdict\gate.py:236` gates on the cap only when `"tokens_in" in envelope`, and `gate.py:162-164` requires `tokens_in` on **agent** envelopes only. A control envelope with `tokens_in` omitted escapes the cap entirely at the gate. M00's envelopes are exactly that shape (`evals\history\55dadb2…json` has `tokens_out:2253` and no `tokens_in`), which is why it is written this way, but the gate is the reader that is not supposed to trust the writer. Settled by: requiring `tokens_in` on any envelope whose commit is at or after tag `m01`. Threshold Owner on the bar, Engineering on the reader.

FINDING · The cap under-counts exactly in the case it exists for. `src\cost_cap.py:32-33` skips any observation with `error`, and `src\verdict\build.py:335` reads `o.get("usage", {})`, which is empty for one; `src\agent\run.py:88-90` replaces the whole observation on an exception, discarding the usage `agents\refagent\agent.py:147-148` had already accumulated for that golden's earlier Converse calls. A run that spends and then fails reports less than it spent. Settled by: `agent.answer` returning usage alongside the error, and the counters adding it. Threshold Owner names the bar, Engineering counts.

FINDING · Rulings m and o together make 150000 unrepairable after the fact: if PR 2's first agent envelope lands over the cap it is RED at that commit forever, because the gate re-reads the cap at that commit (`gate.py:87-101`). A later raise fixes nothing; only a new run at a new commit does. The cap therefore has to be right **before** the run, not after it — which is the opposite of what ruling o's wording ("re-ruled against that envelope") suggests. Settled by: the Threshold Owner saying, before the run, that 150000 is the pre-run number and the re-rule is calibration only. Threshold Owner rules.

FINDING · `src\agent\run.py:68` takes `model_id` from the manifest and `run.py:99` writes it into the raw, including on the deployed path (`run.py:72-73, 84-85`), where the model that actually answered is whatever the deployed runtime holds. From `main` after the deploy the envelope's `model_id` is an assertion copied from the manifest, not an observation. A-vs-A at M04 compares the pair; this field cannot carry that weight. Settled by: the runtime returning its model id in the payload and the runner recording it, refusing on a mismatch. Threshold Owner owns the field; Engineering the runner.

FINDING · `.github\workflows\evals.yml:269` commits only `<commit>.json`, `.baseline-card.json` and `.baseline-raw.json`. `Makefile:60` writes `<commit>.agent-raw.json` into `evals/history/` and `evals.yml:227` uploads it, but it is never committed, so the agent's per-golden usage, its `region`, `inference_config` and `prompt_sha256` live only in a 90-day artifact. The envelope carries neither region nor model version. Settled by: adding `.agent-raw.json` to the record job's list, or naming in the ruling what evidence of the pinned triple is expected to survive. Engineering writes it; Threshold Owner says what must survive.

FINDING · `src\manifest\schema.json:26` `"region": {"type": "string", "minLength": 1}` — any non-empty string validates, while `profile` is held to `^us\.` (line 25). A region a `us.` profile cannot serve passes the schema. Settled by: an enum or a cross-check of region against the profile prefix in `check_manifests` (`src\validate\checks.py:217`). Threshold Owner owns the field; Engineering writes the check.

NOTE · No perfection gate. `src\verdict\build.py:370-378` goes RED only on `regressed`, a plant mismatch, a failed check or the cap, and comments it: "GREEN is the regression bar (P7, R2): nothing got worse. It is not a score." `gate.py:202-238` works out the same list independently. `passed`/`total` at `build.py:166-168` are card counts, reported and not gated. `SPEC\01-signed-bundle.md:249-251` says it in prose: "No count of refagent's passes is expected". R2 holds.

NOTE · One policy, not both. `thresholds.yaml:10` calls the cap "A budget, not a quality bar", and no absolute quality bar exists anywhere in the file; the quality policy at M01 is the regression bar, relative to history. `delta_max` (SPEC/00 §5 / `SPEC\00-overview.md:413`) arrives at M04; when it does, the cap sitting beside it is still a budget and should keep saying so in the same words.

NOTE · Judge: nothing changed and nothing exists to change. `agents\refagent\manifest.yaml:25` `judge_model_id: null`; `src\verdict\build.py:386` hardcodes `"judge_model_id": None`; no rubric file is in the tree; the candidates at `manifest.yaml:102-108` are M03's. R6 (pinned, never the model under test, reproduces its graded-examples set) is not engaged yet. `gate.judge()` is a function name, not the model — worth keeping in mind when M03 lands.

NOTE · Model ids: unchanged in this PR, as `milestones\M01\rulings\pr2.md:79-81` states. `manifest.yaml:17-21` pins id `anthropic.claude-sonnet-5`, `version: null` (ruling p), profile `us.anthropic.claude-sonnet-5`, region `us-west-2`; `manifest.yaml:13-14` reads lifecycle from the right place — "modelLifecycle for anthropic.claude-sonnet-5 in us-west-2: ACTIVE on 2026-09-19 (list-foundation-models)", not the inference profile status. No swap, so no A-vs-A to report; there has been no A-vs-A run in this repo and M04 is where the pair is first compared.

NOTE · Baseline: `src\baseline\agent.py:15-16` still `us.amazon.nova-micro-v1:0` / `us-west-2`, matching `manifest.yaml:87-89`, and `tests\test_baseline_frozen.py:1-17` holds `src/baseline/` to tag `m00` four ways including `git diff m00 HEAD`. Parameters unchanged. `thresholds.yaml:31-33` still pins the m00 card. Nothing in this PR touches the control.

NOTE · R10's N is not moved and is not in this PR. `scripts\observe_attempt.py:40` `WINDOW = timedelta(minutes=30)` is a CloudTrail search window either side of a hand-written timestamp, not a detection bar; R10's ten minutes belongs to claims 5 and 8. It should not later be read as N.

NOTE · The consequence of reading the pinned base hash from the tree (`gate.py:165-167`) is worth writing down once: if `baseline_card.sha256` ever changes, every prior agent envelope becomes REJECTED (exit 2), `make ledger` stops, and no agent row can be re-read. That is the loudness intended, and it means the base must never change — a stronger commitment than "two keys".

BLOCK: 1 · FINDING: 8 · NOTE: 6

---

### `tool-owner`

## Tool Owner report — M01 PR 2 (`main...m01-pr2`)

A report, never a ruling. Scope read: `SPEC/00-overview.md` §5, §6, §9, R7; `SPEC/01-signed-bundle.md` §6, §10; `milestones/M01/feasibility.md` §2.6 (SCOPE, ruling d); `milestones/M01/rulings/pr2.md`; `data/rights_table.json`; `data/clause_index.json`; `agents/refagent/tools/check_availability.json`; `agents/refagent/agent.py`; `agents/refagent/prompt.txt`; `agents/refagent/server.py`; `agents/refagent/manifest.yaml`; `src/manifest/schema.json`; `src/agent/run.py`; `tests/test_refagent.py`.

### Closed schemas (rule 1) — passes on the tool contract
`agents\refagent\tools\check_availability.json` sets `"additionalProperties": false` at every object level it has: line 9 (input), line 31 (output), line 44 (the `row` object). There is no fourth object level. `tests/test_refagent.py:74-75` asserts both, and `:66` proves the result side refuses a row with an extra field. No BLOCK here.

### BLOCK

1. **BLOCK — the output shape contradicts SPEC/00 §9, unamended.** `SPEC/00-overview.md:539-541`: "`check_availability(title_id, territory, platform, date) -> {available, exclusive, constraints[], table_row, clause_id, confidence}`". The contract returns `"required": ["found", "row", "clause_candidates", "source"]` (`check_availability.json:32`). The arguments match; the return does not. `SPEC/01` §6:200-202 and ruling SCOPE (`feasibility.md:282`) say only "with a strict schema both ways" — neither re-rules the return, and `rulings/pr2.md:76` cites exactly those two. Settled by **Product**: amend `SPEC/00-overview.md:539-541` (an ADR or a §9 edit), or return §9's fields. The tool-side argument for amending §9 rather than the file is in `agent.py:11-15` — "A tool that returned the verdict would make F1.4 a test of the tool" — and `confidence` lost its only consumer when cut 4 took the HITL branch. But SPEC/00 is the authority, and while §9 stands, the version on this file cannot be computed: 1.0.0 as a new file, or 2.0.0 as a breaking change to the contract §9 published (R7).

### FINDING

2. **The result schema accepts a row that is not a rights-table row (territory/platform).** `check_availability.json:50-51`: `"territory": {"type": "string", "minLength": 2}`, `"platform": {"type": "string", "minLength": 4}`. The input asserts the alphabet (`:19` `enum: [AU, BR, DE, FR, GB, JP, US]`, `:21` `enum: [AVOD, PVOD, SVOD, THEATRICAL]`); the output does not. `{"territory": "ZZ", "platform": "DISC"}` validates. Settled by the **Tool Owner**: re-use the same two enums on the row. That change is major (R7).

3. **The row's dates are unconstrained strings.** `check_availability.json:52-57`: `"window_start": {"type": "string"}`, `"window_end": {"type": "string"}`, and `holdback_until`, `clearance_expiry`, `embargo_lift_local` as `["string","null"]` with no pattern. `prompt.txt:35-39` tells the model to compare the asked date against these. A row carrying `"window_end": "whenever"` passes the contract and reaches the model. The input date has a pattern (`:25`); the output does not. **Tool Owner**, with the **Data Owner** for the table's own format.

4. **`clause_candidates` is not bound to the clause index.** `check_availability.json:67`: `"items": {"type": "string", "minLength": 2}`. Any two characters validate. `data/clause_index.json` has fifteen ids; `src/verdict/build.py:98,132` fails `cites` on a clause outside it, so a clause the tool invented would turn an ordinary golden red. `tests/test_refagent.py:39-42` covers today's constants in `agent.ALWAYS`/`agent.BY_FIELD`, not the schema. An enum or pattern drawn from the index would make the contract, not a test, the guarantee. **Tool Owner**, with the **Data Owner** owning the index.

5. **The tool hands the model a result field the output schema does not name (rule 5).** `agents/refagent/agent.py:161`: `result, status = {"error": str(exc)}, "error"`, sent at `:163-164` as `{"toolResult": {... "content": [{"json": result}], "status": status}}` and recorded at `:162` under `calls[].output`. `{"error": ...}` appears nowhere in `check_availability.json`'s output. Not a BLOCK: the Converse `status: "error"` channel marks it, and no credential is in it — the payload is a jsonschema message over the model's own arguments. Settled by the **Tool Owner**: name the error branch in the contract's output (`anyOf` with a closed `{"error": string}`), which computes to major (R7).

6. **`match[0]` decides which row governs when the key repeats.** `agent.py:80-89` filters on title/territory/platform and takes `row = match[0]`; the contract calls it "The governing row" (`check_availability.json:39`). I checked all forty rows of `data/rights_table.json`: `(title_id, territory, platform)` is unique today, so nothing is wrong now. Nothing in the contract, the code or a test holds it unique. A second row added by the Data Owner would be silently dropped and the tool would have chosen. Settled by the **Tool Owner**: refuse on more than one match, so the choice is never made quietly.

7. **`found: false` is the one place the tool states a conclusion.** `check_availability.json:35`: "There is then nothing to publish under", and `agent.py:88` hardcodes `"clause_candidates": ["ML-2.1"]` with no row to read it from. `prompt.txt:42` then instructs "If the tool returns found false, answer with `"available": false`". For unscheduled combinations the answer is settled before the model reads anything. It is defensible under ML-2.1 ("a title may be published only in the territories and on the platforms listed"), but it is the tool applying a clause. **Tool Owner** to rule whether `found` plus a fixed clause is a fact or a verdict.

8. **`date` is required and never read.** `check_availability.json:10` requires it; `agent.py:80-85` matches on title, territory and platform only. The model must supply a field the tool ignores, and a wrong date cannot be caught at the tool boundary. The intent reads as correct — the window question is the model's — but the input contract implies otherwise. **Tool Owner**: drop it from `required`, or document in the description that it is recorded and not matched on. Either is major (R7).

9. **The output contract is duplicated in prose with nothing binding the two.** `prompt.txt:30-41` names `table_row`, `clause_candidates`, `exclusive`, `holdback_until`, `clearance_expiry`, `embargo_lift_local`. `tests/test_refagent.py:69-75` binds the *input* schema to the toolSpec; nothing binds the prompt to the output schema. A major bump that renames a row field leaves the prompt citing a field that no longer exists. Settled by **Engineering** (`prompt.txt` is Engineering's path under `rulings/pr2.md:77`) with a test asserting every field the prompt names is in the contract's row properties.

10. **The Tool Owner's manifest fields are optional.** `src/manifest/schema.json:7`: `"required": ["name", "model", "judge_model_id", "guardrail", "endpoint_allowlist", "seats", "platform_version"]`. `may_call`, `may_be_called_by` and `ceilings` are absent from it, so a manifest declaring no edge fields at all validates. The M02 two-sided check then has no anchor — an absent `may_be_called_by` is indistinguishable from an empty one. Settled by the **Tool Owner**: require all three, `[]` being a declaration. (The file sits under `src/**`, Engineering's path per `rulings/pr2.md:77`, but these three subschemas are the Tool Owner's fields under `SPEC/00-overview.md:103`; the ruling names no Tool Owner for them.)

11. **The two ceilings that bound a runaway edge have no maximum.** `src/manifest/schema.json:75-76`: `"concurrency": {"type": "integer", "minimum": 1}`, `"rps_per_edge": {"type": "number", "minimum": 0}`. `depth` and `fan_out` carry SPEC/00 §6's numbers as maxima (`:77-78`). A manifest may declare `concurrency: 10000` and validate. SPEC/00 §6:220-221 gives numbers only for depth and fan-out, so the maximum has to come from somewhere: **Product** for a §6 number, or the **Tool Owner** for a ruling.

12. **A zero-edge agent cannot declare zero fan-out.** `src/manifest/schema.json:78`: `"fan_out": {"type": "integer", "minimum": 1, "maximum": 3}`. refagent has no edges and declares `fan_out: 3` (`manifest.yaml:65`) and `depth: 2` (`:64`) — the maxima — because 0 is not expressible. The declaration says the most the schema allows rather than what M01 uses. **Tool Owner**: allow 0.

13. **An open object in the manifest schema.** `src/manifest/schema.json:116`: `"pinned_roles": {"description": ..., "type": "object"}`, with no `additionalProperties: false` and no properties. Any key with any value validates, including a model id under a misspelled role. The block is the **Threshold Owner's** content; the closed-schema rule is mine (`SPEC/00-overview.md:191`). `seats` (`:52-57`) is closed in effect by `propertyNames` and is fine.

### NOTE

14. **Semver preview.** `check_availability.json:4`: `"version": "1.0.0"`. Read as a new file, 1.0.0 is the initial version and no bump is computed. Read against SPEC/00 §9's published shape it is 2.0.0 (see BLOCK 1). Whichever way §9 is settled, **the next change to `input` or `output` — including findings 2, 3, 4, 5 and 8 — computes to a major bump**: 2.0.0, or 3.0.0 if BLOCK 1 lands as 2.0.0 first. R7 (`SPEC/00-overview.md:718-719`): "Schema or edge change is major; the developer does not choose the bump." Nothing in this diff carries a version that disagrees with its computed bump, so no BLOCK on rule 2.

15. **No computed-semver reader exists yet, and that is scheduled.** `SPEC/00-overview.md:368-369` puts "computed semver (schema/edge change = major); edges declared both sides; cycle and ceiling check" in M02's build. `src/validate/` contains no reader of `tools/**`. So R7 is a convention here, not a gate, until M02. The version string is recorded as evidence: `src/agent/run.py:103` writes `"tools": [agent.CONTRACT["name"] + "@" + agent.CONTRACT["version"]]` into every raw observation — which means a schema change without a bump would put a stale `check_availability@1.0.0` into an envelope that measured a different contract.

16. **Both sides (rule 3): nothing to check, correctly.** `agents/refagent/manifest.yaml:56-57`: `may_call: []`, `may_be_called_by: []`. No edge is declared anywhere in `agents/`, so no one-sided edge exists and no cycle is possible. This matches ruling SCOPE (`feasibility.md:274-276`, `ratings-helper` → M02) and `SPEC/01-signed-bundle.md:210-213` ("edges two-sided, no cycles, ceilings within bounds: PR 2 ... M02 if `ratings-helper` is cut"). Rule 3 is vacuous at this diff; the first real test of it is M02.

17. **Ceilings (rule 4): within bounds.** `manifest.yaml:61-65` — `concurrency: 2`, `rps_per_edge: 1`, `depth: 2`, `fan_out: 3`. Depth 2 and fan-out 3 are exactly SPEC/00 §6's numbers (`:220-221`). Graph depth in this diff is 0. See findings 11 and 12 on what the schema does and does not bound.

18. **`manifest.yaml` is not in this diff.** `rulings/pr2.md:79`: "`agents/refagent/manifest.yaml` is not changed in this PR." Its Tool Owner fields landed at PR 1; `src/manifest/schema.json` is their first reader, which is why findings 10–12 are raised here.

19. **No credential in any result (rule 5, credential half).** The row's fields are `table_row, title_id, territory, platform, window_start, window_end, exclusive, holdback_until, clearance_expiry, embargo_lift_local` (`check_availability.json:45-46`), and `agent.py:97` returns the row as read. No key, token, ARN or account id can travel in a result. `source` (`:71`) is a two-value enum naming a table or a file. The deployed path's `"the deployed runtime reads its own table"` (`src/agent/run.py:74`) is an observation field, not a tool result, and never reaches `check_availability`.

20. **A stale description in the envelope schema.** `src/verdict/schema.json:183`: `"description": "null until ceilings exist (M01)."`, and `src/verdict/build.py:401` writes `"rejected_over_ceiling": None`. Ceilings exist in the manifest as of M01; no edge does, so nothing can be rejected. The honest wording is "null until an edge exists (M02)". Engineering's file, the Tool Owner's meaning.

BLOCK: 1 · FINDING: 12 · NOTE: 7

---

### `engineering-cold-reviewer`

Cold review of M01 PR 2 (#8), base `main`, branch `m01-pr2`. Draft ruling file text below — for `milestones\M01\rulings\pr2-cold-review.md`. I wrote nothing; this is text for the Engineering seat to rule and commit.

Note there is already an uncommitted `milestones\M01\rulings\pr2.md` (the seats' open ruling) — see BLOCK 1; this cold review is a separate file and does not replace it.

---

# M01 PR 2, cold review

Row 1's PR 2 line asks for: S1 and S2 refused by `verify`, each with its planted reason; S3 (both forms), S5 and S8 refused at synth; `checks.F1_1`, `F1_2`, `F1_4` in refagent's envelope; `F1_1` and `F1_3` written from CloudTrail's record of S4's and S6's attempts. The readers are in the tree and the five file-backed seeds fire for their planted reasons. Two things block, and eight weaken what the row will be able to say.

## BLOCK 1 — this PR has no ruling file

`git ls-files milestones/M01/rulings/` returns `pr1.md` and `pr1-threshold-owner.md` and nothing else. `git status --porcelain` returns `?? milestones/M01/rulings/pr2.md`: the file exists on disk, was never `git add`ed, and is not in `git diff --name-only main...m01-pr2` (57 paths, none under `milestones/M01/rulings/`).

So on the branch as it stands every seat-owned path in this PR — `.github/workflows/deploy.yml`, `.github/workflows/evals.yml`, `.github/workflows/sign-fixture.yml`, `infra/**`, `SPEC/00-overview.md`, `SPEC/01-signed-bundle.md`, `docs/adr/ADR-0006-*.md`, `milestones/README.md` — is changed with no ruling on `main` that names it. `cold-review-ruling` blocks the merge on exactly this. A local `make validate` does not catch it: `check_rulings` in `src/validate/checks.py` globs the working tree, where the untracked file is present and well-formed.

Falsify: `git ls-files milestones/M01/rulings/`.

## BLOCK 2 — two touched paths no ruling names, committed or not

Cross-checking the 57 changed paths against the `authorises:` list in the uncommitted `pr2.md` leaves six uncovered. Three are the bot-written envelope files under `evals/history/` (CI-written, correctly outside a ruling) and one is `uv.lock` (Engineering, a glob away from covered). Two are seat-owned:

- `agents/refagent/manifest.yaml`. The diff adds `may_call: []` and `may_be_called_by: []` (Tool Owner, SPEC/00 §5), `ceilings` (Tool Owner), `seats` and `endpoint_allowlist` (Security, feasibility ruling d), `max_tokens_per_session` and `daily_usd` (Threshold Owner). CLAUDE.md gives Engineering `agents/<name>/**` "but for the rows above and the manifest fields their seats own". No ruling in the tree names this path.
- `infra/bootstrap/cdk.json`, new, 4 lines. `infra/**` is Security's. `infra/construct/cdk.json` is on the list; its sibling is not.

Falsify: `git diff --name-only main...m01-pr2 | grep -E 'manifest.yaml|bootstrap/cdk.json'`, then search `milestones/M01/rulings/` for either path.

## FINDING 1 — an envelope may omit claim 1's checks and still go GREEN

`Makefile:43-46` makes every claim-1 check conditional on a variable: `$(if $(JUNIT),--check-cases F1_1 ...)`, `$(if $(S4_OBS),--check-attempt F1_1 ...)`, `$(if $(S6_OBS),--check-attempt F1_3 ...)`. `both()` in `src/verdict/build.py` inserts a lone source when the other was never passed:

    if falsifier not in checks:
        return checks | {falsifier: result}

so `F1_1` reads "pass" from the pytest half alone if `S4_OBS` is empty, and disappears entirely if `JUNIT` is empty too. `gate.judge` in `src/verdict/gate.py` requires only one of the four to be present — `"checks.F1_4 is missing from an agent envelope"` — and has no equivalent for `F1_1`, `F1_2` or `F1_3`; it only reads the checks that are there (`if check["status"] == "fail"`).

The evidence that this is not theoretical is in the diff: `evals/history/5b91750828c70f92e2cb41906d28ef1a63c56c85.json` is recorded GREEN with `checks` = `{F0_2, F0_3}` and nothing about claim 1. The gate that decides row 1 cannot tell a run that measured the claim from one that did not. `both()`'s own docstring says "Two sources pass only if both do"; that is true only when both flags are passed, and nothing checks that.

## FINDING 2 — F1_3 does not require the key policy to be what refused S6

`check_from_attempt` in `src/verdict/build.py` passes when every attempt has `found is True and error_code == "AccessDenied"`. It never reads `error_message`, which `scripts/observe_attempt.py` does record.

`milestones/M01/runs/f1_3_key_policy.yaml:3-5` says the opposite: "A refusal that names the role's own policy does not count: the message must say an explicit deny in a resource-based policy". `tests/test_m01_seeds.py:84` asserts exactly that (`assert all("resource-based policy" in attempt["message"] ...)`) — but that test is `xfail(strict=True)` and feeds no check. So the only thing that writes `checks.F1_3` will say "pass" on a denial that came from the role's own identity policy, which is the case the run file says does not count.

## FINDING 3 — S4's and S6's reader landed; their markers did not come off

`tests/test_m01_seeds.py:31` still defines `PR2 = "no reader until M01 PR 2"` and lines 61 and 77 still carry `reason=f"S4: {PR2} ..."` / `f"S6: {PR2} ..."`. The reader landed in this PR: `scripts/observe_attempt.py` plus `check_from_attempt` in `src/verdict/build.py`, wired at `Makefile:45-46` and `.github/workflows/evals.yml`. The reason string is now false.

The mechanical consequence: both tests read `observed` from the run files and assert `AccessDenied` on every attempt. Both files still say `observed: null`. The moment the human fills them in — which the ledger row requires before PR 2's CI run — both tests XPASS, `strict=True` turns that into a failure, and `.github/workflows/evals.yml`'s last step ("Fail if pytest failed") fails the run that is supposed to measure the row. The module docstring at lines 9-13 has been rewritten to say the markers come off "when the human has made them", which is the opposite of the rule stated three lines above it: "a failure the first time it passes, so the marker has to come off in the commit that lands the reader".

## FINDING 4 — the S2 assertion that decides F1_1 is the loose one

`Makefile:39` names `test_s2_a_bundle_changed_after_signing_is_refused` in `F1_1_CASES`. That test (`tests/test_m01_seeds.py:41`) is `pytest.raises(verify.Refused, match="digest")`. `Refused` joins every reason, and `src/bundle/verify.py` has a second reason containing the word: `"digest: the cosign bundle carries no signed digest"`, raised when `signed_digest()` returns None. So S2 would still be "refused for its planted reason" if the digest comparison never ran at all.

The test that cannot be satisfied that way — `tests/test_bundle.py:54-59`, which asserts exactly one `digest: ` reason and that it carries the signed digest's first twelve characters — is not in `F1_1_CASES`. The three construct seeds were tightened to exact phrases in this PR (`tests/test_m01_seeds.py:55`, `:74`, `:91`); S2 was not.

## FINDING 5 — `verify()` fails open on a certificate it cannot read

Three places in `src/bundle/verify.py`:

- `certificate_fields` returns `(None, None)` when the PEM is empty or will not parse;
- both identity checks are guarded by `if san is not None` / `if repository_id is not None`, so `(None, None)` produces no reason;
- `cosign_accepts` opens with `if not shutil.which("cosign"): return None`.

On a machine without cosign, a hand-written `bundle.cosign.json` carrying no `cert` and a `rekorBundle` whose hash is the archive's own verifies clean — an unsigned bundle that loads, which is F1.1's first clause. The module docstring says "Three things are checked, always, and every failing one is reported."

`.github/workflows/evals.yml` installs `sigstore/cosign-installer` before `pytest`, with a comment naming this gap, so the measuring run is covered and `deploy.yml` installs it too. What is not covered is any other caller, and `tests/test_bundle.py:105` — `assert shutil.which("cosign") or True` — is an assertion that cannot fail.

## FINDING 6 — S8's refusal is opt-in

`refuse_outside_construct(stack)` in `infra/construct/governed_agent.py` installs the stack validation, and the seed calls it on itself: `tests/fixtures/construct/outside_construct.py:17`. A stack that creates an `AWS::BedrockAgentCore::Runtime` and never imports `infra.construct` synthesises with nothing refused. F1.1 says "an agent built outside the construct ... synthesises"; what PR 2 measures is an agent built outside the construct in a stack that consented to be checked. The seed was shaped this way at PR 1 and PR 2 read it as planted, so this is not a plant defect — it is a limit on what the row may claim.

## FINDING 7 — "refused at synth" is not where an out-of-enum endpoint is refused

`agents/refagent/manifest.yaml:31-33`, `src/manifest/schema.json:46` and feasibility ruling d all say a hostname outside the five-name enum is "refused at synth". `_security_group` in `infra/construct/governed_agent.py:113-118` reads `/agentkeel/security/endpoint/<name>` through `ssm.StringParameter.value_for_string_parameter`, which is a token that resolves at deploy; an unknown name synthesises fine and fails later, at deploy, on a parameter that does not exist. `_StackRules` never reads the enum. The refusal that does exist is `check_manifests` under `make validate` — a different tool, at a different time, with a different consequence.

## FINDING 8 — two construct tests read a gitignored artifact

`tests/test_construct.py:20` points `TEMPLATE` at `infra/construct/cdk.out/AgentkeelRefagent.template.json`, written by the cdk-nag synth inside `make validate` and ignored by `.gitignore`. Lines 60 and 84 assert over it. Nothing ties the file to this commit: `pytest` run without a prior `make validate` errors on a missing file, and a stale `cdk.out` from an earlier synth lets both tests pass on an older template. The docstring at line 61 — "Read from the template `make validate` just wrote" — is an assumption pytest has no way to check.

## NOTE 1 — shape

PR 2 holds the readers for the plants it measures, and nothing in it makes a plant pass. No reader lands in a last PR. It also carries the whole build: `infra/bootstrap/app.py` (524 lines), the construct, refagent and `.github/workflows/deploy.yml` (185 lines). The deploy path measures nothing here and says so in its own header ("No deploy has run ... no prose may call it proven"), which is the honest form. Ledger row 1 moves 1/4 → 2/4.

## NOTE 2 — P5 holds in the new code

`src/agent/run.py`, `agents/refagent/agent.py` and `scripts/observe_attempt.py` write raw observations and read no envelope; a grep for `evals/history` across the new files returns one line, in a README. Envelopes are still written only by `src/verdict/build.py` and read only by `src/verdict/gate.py`. Both `evals/history/` and the S2 signature under `tests/fixtures/` were committed by `github-actions[bot]` (`6ec6d9c`, `2609d67`), so there is no human commit to `evals/history/**` and no hand-written envelope outside the `tests/fixtures/` exception.

## NOTE 3 — frozen paths

No path under `src/baseline/` appears in `git diff --name-only main...m01-pr2`.

## NOTE 4 — the five file-backed seeds fire for their planted reasons

S1: exactly one reason, the missing signature (`tests/test_bundle.py:51`). S3: both forms, `"egress to 0.0.0.0/0"` in each and `"added outside the construct"` in the standalone one only (`tests/test_m01_seeds.py:52-58`). S5: `"no permissions boundary"` (`:74`). S8: `"outside GovernedAgent"` (`:91`). These are real tightenings over PR 1's `is not None`, which would have passed on an ImportError. S2 is the exception; see FINDING 4.

## NOTE 5 — what F1.4 can and cannot catch

`score_one` in `src/verdict/build.py` sets `cites` from "the cited `table_row` is in the rights table and the cited `clause_id` is in the clause index" — existence, not correctness. `check_availability` hands the model its `clause_candidates`, and `tests/test_refagent.py:39-42` asserts every clause the tool can name is in `data/clause_index.json`, with the comment "the tool cannot cause that". So F1.4 fires on S7's "cites nothing" and cannot fire on a wrong citation that exists. Row 1's measured cell should not be read as "refagent cites correctly".

## NOTE 6 — the cap read at the envelope's commit

`thresholds_at` / `cap_at` in `src/verdict/gate.py` fall back to the working tree when `git show <commit>:thresholds.yaml` fails, and return where they read. `rule()` discards that with `cap, _ = cap_at(...)`; only `main()` prints it, so a caller of `rule()` cannot tell which cap ruled. `.github/workflows/evals.yml:85` sets `fetch-depth: 0`, so the fallback should not fire in CI, and `tests/test_gate.py` pins both branches.

## NOTE 7 — `milestones/M01/pr2-body-draft.md` is committed. Not read for this review.

## NOTE 8 — nothing on this branch measures claim 1 yet

The only envelope in the diff is `evals/history/5b91750828c70f92e2cb41906d28ef1a63c56c85.json`: all results `scope: control`, GREEN, `checks` = `{F0_2, F0_3}`. Both run files still say `observed: null`, so `check_from_attempt` would write `F1_3: fail` and `both()` would pull `F1_1` to fail today — RED, correctly, for the stated reason. Row 1's Measured cell cannot be filled from anything now on the branch.

BLOCK: 2 · FINDING: 8 · NOTE: 8

---

Two things worth acting on before anything else, both one-line fixes with large blast radius: `git add milestones/M01/rulings/pr2.md` (BLOCK 1), and adding `agents/refagent/manifest.yaml` and `infra/bootstrap/cdk.json` to its `authorises:` list (BLOCK 2). FINDING 1 and FINDING 3 are the two that decide whether PR 2's measuring run can be green and meaningful at the same time.

## Unsure

Five BLOCKs are **not** repaired here. Each names the seat whose ruling would settle it and the milestone by which it must be settled. The PR is not undrafted until they are ruled.

**A. The tool's return shape is not the one SPEC/00 §9 publishes.** §9 says `check_availability(title_id, territory, platform, date) -> {available, exclusive, constraints[], table_row, clause_id, confidence}`. The contract in this PR returns `{found, row, clause_candidates, source}`: the row and the clauses it can be read under, and no verdict. The argument for what is here is in `agents/refagent/agent.py` — a tool that returned the verdict would make F1.4 a test of the tool, and `confidence` lost its only consumer when cut 4 took the HITL branch. But CLAUDE.md says SPEC/00 is the authority and a disagreement gets a PR, not a shrug. Either §9 is amended (an ADR) or the tool returns §9's fields. Until it is settled the contract's version cannot be computed: 1.0.0 as a new file, 2.0.0 as a breaking change to a published contract (R7). **Product**, before this PR is undrafted.

**B. The boundary is an allow-list, and it is applied to the deploy-plane roles too.** `PermissionsBoundary.of(self).apply(boundary)` covers every role the bootstrap stack makes. The boundary's only Allow is the agent's ten actions. Effective permission is the intersection, so the CloudFormation execution role's `iam:CreateRole` is capped to nothing and it has no Allow at all for `ec2:CreateSecurityGroup`, `dynamodb:CreateTable` or `bedrock-agentcore:CreateAgentRuntime`; the deploy role's `cloudformation:CreateStack` is capped to nothing; the Budgets action role's `iam:AttachRolePolicy` is capped, so the `daily_usd: 10` stop cannot attach; the VPC flow-log role likely cannot deliver. **The stack as written can be deployed, and can then deploy nothing.** SPEC/01 §6 asks the execution role to "create a role only with the boundary attached" — with this boundary on itself it may create none. Either a separate deploy-plane boundary, or the deploy-plane actions in the Allow, plus one `simulate-principal-policy` table in the record. **Security**, before the first deploy from `main`; it does not block S4 or S6, which are refusals. This is the one to read first.

**C. A fork PR turns the only required measurement check green without running it.** The `evals` job is skipped on a fork (`head.repo.full_name != github.repository`), and GitHub counts a skipped required check as success. So a fork PR merges with no `make validate`, no pytest and no envelope. `bypass_actors: []` is doing its work; this path goes around it without a bypass. The fix needs a required context that runs on a fork (a second job with no AWS step), which is a ruleset PUT — the human's, not mine. **Security**, by M02 at the latest; say in the ruling whether it is repaired here or carried.

**D. S8's check is installed by the stack under test.** `refuse_outside_construct(stack)` is what puts the check on a stack with no `GovernedAgent` in it, and S8's fixture calls it on itself. A third app, a second stack, a `Stage`, or a stack that simply never imports `infra.construct` is not checked. What fired is "a stack that installs the checks refuses a bare runtime", which is narrower than false state 8, "an agent runtime is synthesised without `GovernedAgent`". A check that does not depend on the stack cooperating — over every synthesised template in the repo — plus a seeded case that is a stack which does *not* call it, is what would close it. **Security**; until then `checks.F1_1` should not be read as covering S8's general form.

**E. `pr2-threshold-owner.md` cannot be written yet.** Rulings o and p re-rule the cap and refagent's model `version` against this PR's first agent envelope, and no agent envelope exists. A related point the Threshold Owner raised, which matters *before* the run rather than after it: ruling m means an envelope written over the cap is RED at that commit forever, because the gate re-reads the cap at that commit. A later raise repairs nothing; only a new run at a new commit does. So 150,000 has to be right before the run, and the re-rule is calibration. The estimate from the code: about 44k tokens typical for control plus agent over fifteen goldens, about 116k in the pathological case — 77% of the cap. **Threshold Owner**, before the measuring run.

Five more, not BLOCKs, each with a seat and a date:

1. **What is signed is the bundle; what runs is the image.** `deploy.yml` verifies the bundle in the job's checkout, twice, and builds the image from that checkout. Nothing proves the pushed image holds those bytes. SPEC/01 §6's "the check runs outside the bundle's own code" is met; "the bytes that ran are the bytes that were signed" is not, end to end. **Security**, by M02.
2. **The two gateway-endpoint prefix lists are written by hand.** AWS gives no CloudFormation attribute for a managed prefix list id, so two SSM parameters are `put-parameter` calls in `infra/bootstrap/README.md`. A wrong value narrows egress rather than widening it, because the endpoint policy and the boundary still apply. **Security**, by M02: a custom resource, or ruled as it stands.
3. **The construct's checks read CDK's typed properties, not the rendered template.** `add_property_override("SecurityGroupEgress", …)` changes the template at render time and leaves the getters as they were, so S3 form 1 and S5 would both pass while the deployed template carried the rule. **Security**, by M02.
4. **The key policy names `agentkeel-security`, a role that exists nowhere.** In practice the only principal outside the Deny is the account root. The half that does hold — the deploy role and the execution role cannot change it — is already a control with no seeded case in SPEC/01 §9. **Security**, by M02: create the role, or say root.
5. **`infra` is now a default dependency group**, so `uv sync --frozen` installs `aws-cdk-lib` and `cdk-nag` in every job. Without it the S3, S5 and S8 tests would pass for the wrong reason: no `aws_cdk`, no synth, no refusal to read. It costs install time in jobs that do not synth. **Engineering**, by M02, if the cost matters.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
