---
# M10 PR 2 (#55), Security's key over the Security paths this PR touches:
# the construct and its app (the door), the door's two functions, the
# bootstrap stack and its regenerated NagReport, the security stack (the call
# records' delivery) and its regenerated NagReport, deploy.yml, evals.yml and
# infra/workflows.sha256. The two rulings SPEC/10 §11 puts to this seat
# before PR 2: R2 (the door) and R3 (the outside caller). Product's file is
# rulings/pr2.md; the Tool Owner's is pr2-tool-owner.md; the Data Owner's is
# pr2-data-owner.md; Engineering's (with the cold review) is
# pr2-engineering.md.
ruling: pr2-security
seat: Security
authorises:
  - .github/workflows/deploy.yml
  - .github/workflows/evals.yml
  - infra/bootstrap/app.py
  - infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv
  - infra/construct/governed_agent.py
  - infra/construct/door.py
  - infra/construct/app.py
  - infra/security/app.py
  - infra/security/AwsSolutions--AgentkeelSecurity-NagReport.csv
  - infra/workflows.sha256
evidence:
  - SPEC/00-overview.md#8-M10
  - SPEC/10-public-caller.md
  - milestones/M10/runs/door_probe.md
  - milestones/M10/README.md
  - milestones/M10/feasibility.md
  - docs/adr/ADR-0015-the-public-caller-an-eleventh-milestone.md
pr: 55
---

# Ruling: M10 PR 2, Security

Ruled by andaro74 as Security, 2026-10-15, as written.

## R2. The door is door 2 in the hybrid form

Security's probe of door 1 (2026-10-14, throwaway names, torn down
2026-10-15; `runs/door_probe.md`) answered its three unknowns: (a) yes, a
SigV4 call is refused in JWT mode before IAM; (b) partly, an admitted call's
data event names the token's `sub` and a refused call's names no one; (c)
partly, the stranger's refusal is recorded in 298 s naming no caller and the
no-token refusal is recorded nowhere. Door 1 alone fails F10.3 on the
stranger and F10.4's record arm on the no-token call.

So the door is **door 2 in the hybrid form** (SPEC/10 §2, row 2), in
`infra/construct/governed_agent.py` for an agent whose manifest has
`callers`: the agent's own Cognito user pool (one user per subject, a
callers client with `USER_PASSWORD_AUTH`, a door client with client
credentials on a resource-server scope), the runtime's `authorizerConfiguration`
on the pool's issuer admitting **the door client only** (door 1's (a)
stays: no SigV4 reaches a doored runtime, and a caller's own token is
refused there too), an HTTP API in front with a Lambda authoriser that
checks a caller's token against the manifest's `callers` baked into the
stack at synth and a proxy Lambda that exchanges to the door's token and
invokes the runtime's bearer endpoint. The API's access log, one line per
call naming the subject, the issuer, the outcome and the reason (or the
API's own 401 for no token), is the call record; it goes to a log group in
the agent's stack and, by a subscription, to the security account's
destination (`infra/security/`, below). The bypass arm's record is the
`InvokeAgentRuntime` data event the platform account's trail has carried
since M05 PR 2 (`infra/audit/`); no trail changes.

**Grants.** No `InvokeAgentRuntime` grant is widened: the proxy carries the
door client's token, not SigV4. The execution role gains a policy of its
own (`agentkeel-cfn-exec-door`) for the door's resource types, each on the
platform's names where the service takes a resource, the pool's on
`userpool/*` held to the agent tag, the API's on `/apis` and `/apis/*`
(an API's sub-resources carry no tag of their own, said in the suppression),
`CreateUserPool` on `*` held to the request tag, and PassRole to Lambda on
the agent path; the three log groups and the subscription are retained,
since the deploy boundary denies `logs:Delete*` flat. The deploy role gains
one read, `cognito-idp:DescribeUserPoolClient` on a tagged agent's pool.
The agent ceiling gains that one action, so the proxy may read the door
client's secret on its own pool (a ceiling widened, as M05's put was); the
construct grants it on that pool alone. The secret is stored nowhere else
(Unsure I of PR 1). The door's two roles are agent-path roles under the
boundary, each with its own log group and nothing more.

**The delivery** (`infra/security/`): a Logs destination
(`agentkeel-calls`) whose policy admits the platform account's
`PutSubscriptionFilter` and nothing else; a Firehose (`agentkeel-calls`)
that decompresses CloudWatch Logs' batches, extracts each line, partitions
by the line's `agent` and writes newline-delimited JSON under
`calls/agents/<name>/` within a minute, encrypted with an AWS-owned key;
the stream's role writes under `calls/*` only, and the bucket's policy
admits it there and denies every other principal; the subscriber role's
trust is held to this account; the read role lists and reads `calls/`; the
trail logs it.

**What has not fired.** The runtime's one-client refusal fired in the
probe on a throwaway runtime; the authoriser and the proxy ran under test
with a key made for the test; the delivery, the subscription and the
deploy's door step have never run. None is described as working until
festival-desk's deploy and PR 3's run read it.

## R3. The outside caller

As proposed at PR 1: a user in the agent's pool for the admitted arm, named
in `callers`; a user of a throwaway pool the owner makes for the run and
deletes after for the stranger; no token for the no-identity arm; and the
bypass arm made **as an assumed role holding the grant, never the owner's
IAM user**, straight at the runtime, as the probe made it. The hybrid's API
takes tokens, not IAM, so the fallback (a security-account principal as the
stranger) is not needed.

## From this seat's read of the PR (0 BLOCK, 7 FINDING, 10 NOTE)

| # | Disposition | Seat |
|---|---|---|
| F1 | **Repaired.** The authoriser clips what it writes into its context: a claimed subject to the subject pattern (or a client id's shape), an issuer to a URL's charset with a length cap, else `-`; the format writes `$context.routeKey`, not the request path; the observer copies no line whose `agent` is not the prefix it was read under, and `build` names one as not this agent's record (F10.3). The probe with `%22` and `%0A` in a claimed username is on PR 3's list, at festival-desk's deploy | Security; Engineering |
| F2 | **Repaired.** A payload that is not an object is `no identity`; the `exp` compare is inside the try and a non-number is `not admitted`; tests for `[]`, a string `exp` and a null | Security; Engineering (the test) |
| F3 | **Repaired for the pool**: its management statement is held to `aws:ResourceTag/agentkeel:agent`. **Not for the API**, and the DoorGrants reason says why: an API's routes, integrations, authorisers and stages are made under `/apis/<id>/` and carry no tag of their own | Security |
| F4 | **Repaired.** `tests/test_m10_platform.py` reads the doored fixture's own NagReport and asserts no `Non-Compliant` row, and that the two Cognito suppressions applied | Security; Engineering |
| F5 | **Repaired.** The KDF1 suppression is deleted: the rule accepts an AWS-owned key | Security |
| F6 | **Repaired.** This file | Security |
| F7 | **Accepted by name.** The door's two functions run outside the platform VPC: the pool's hosted token endpoint (`*.auth.<region>.amazoncognito.com`) has no interface endpoint, and the runtime's bearer endpoint is a public service endpoint. The functions hold the door client's token in memory for its life and reach those two hosts and the pool's JWKS; the construct's egress check reads security groups and does not read them. Stated in SPEC/10 §2 and the construct. A VPC with endpoints for what has one is a later milestone's, if any | Security |
| N (ReadRole reason) | **Repaired**: names `calls/*` | Security |
| N (subscriber trust) | **Repaired**: `aws:SourceAccount` and `aws:SourceArn` on the role the destination assumes | Security |
| N (curl argv) | **Repaired**: the secret goes to curl through a netrc file in the runner's temp, removed after | Security |
| N (Cognito ResourceTag on the deploy role's read) | Recorded. If Cognito does not evaluate the tag on `DescribeUserPoolClient`, the step fails closed at the first doored deploy; PR 3's repair then | Security |
| N (Firehose into an Object Lock bucket) | Recorded. Whether Firehose's put carries the integrity header the lock requires is read at the security stack's deploy; the stream has no error log group, since the boundary's allow-list carries no `logs:*`. A silent refusal reads as `calls/` empty and row 10 unread | Security |
| N (jwks never refetched on a kid miss) | Recorded; Cognito does not rotate pool signing keys on its own | Security |
| N (calls/ under the one-day lock) | Pre-existing (R5 as amended at M05 PR 1); a change is two keys | Security |
| N (switched off from inside) | Recorded, as SPEC/10 §8 says: the authoriser's one client and the door are Python under `ruling-cited` and this review, unread by `two-key`; said in the PR body | Security; Product |
| N (nothing fired live) | Recorded, as above | Security |
| N (the hash file) | `make validate` reads it: twenty-one ok | Security |
| cold review F2 | **Repaired.** The deploy step's comment says the token is written to the step's output on the runner, masked, and nowhere else | Security |

### The report, verbatim

> Read: the diff a67de63...afd7f31 (Security paths) — C:\Users\andar\AppData\Local\Temp\claude\c--Users-andar-code-agentkeel\c5b42cd7-b1be-41a7-a9b3-e826e9ab0179\scratchpad\security.patch (deploy.yml, evals.yml, bootstrap/app.py + NagReport, construct/app.py, construct/door.py, construct/governed_agent.py, security/app.py + NagReport, workflows.sha256). Also read: SPEC/00 §3, §5, R3–R5; SPEC/10 §2, §6, §8, §11 R2; milestones/M10/runs/door_probe.md; tests/test_m10_platform.py; tests/test_containment_stacks.py (lines 235–297); src/verdict/caller.py (from_raw, _read_access_log); scripts/observe_caller.py (the calls/ listing); .github/workflows/*.yml (`permissions`, `uses:`, `on:`).
>
> ## What is as the brief says (each quoted)
>
> - Runtime admits the door client only: governed_agent.py `allowed_clients=[self.door_client.ref]` (patch l.636); without a pool `authoriser = None` (l.631). No InvokeAgentRuntime grant changes anywhere in the diff; the deploy role's new statement is `actions=["cognito-idp:DescribeUserPoolClient"]` only (l.296). Held by `test_the_runtime_admits_the_door_client_only_and_the_invoke_is_still_conditioned_on_the_guardrail` and `test_the_deploy_role_reads_a_door_clients_secret_on_a_tagged_pool...` (`assert len(deploy) == 1`, condition `Null aws:ResourceTag/agentkeel:agent: false`).
> - Door roles: `path=AGENT_ROLE_PATH`, `permissions_boundary=...self.boundary_arn` (l.714–716), one statement `ItsOwnLogStreams` on `log-group:/aws/lambda/<function>:*` (l.720–721); the proxy's one extra `ReadTheDoorClientsSecret` on `self.pool.attr_arn` (l.756–758). No VpcConfig on either CfnFunction (l.768–775): outside the VPC, stated in the module comment (l.586–587). Secret: no `ClientSecret` GetAtt, no output of it (construct/app.py outputs are Url, PoolId, ClientId, TokenEndpoint, Scope, l.378–382); the proxy caches the token in memory only (`_door.update(...)`, l.530).
> - Execution role: a policy of its own `agentkeel-cfn-exec-door` (l.282); PassRole held to `lambda.amazonaws.com` on the agent path (l.229–234); functions on `function:agentkeel-*-door-*`, log groups on `/agentkeel/doors/*` and `/aws/lambda/agentkeel-*-door-*`, no `logs:Delete*` and RETAIN on the three log groups and the subscription (l.742, 747, 761). `test_the_execution_role_may_make_each_resource_type_the_door_adds` holds the handler calls against the grants and the flat denies.
> - Deploy step: `echo "::add-mask::$secret"` before any use (l.30), `echo "::add-mask::$token"` (l.34); both go to `$GITHUB_OUTPUT` only, never to the summary; `$url/$endpoint/$scope` are the stack's outputs, not caller input. The goldens step receives `AGENTKEEL_DOOR_URL`/`AGENTKEEL_DOOR_TOKEN` as env (l.50–51).
> - Security account: destination policy `Principal: {AWS: AGENT_ACCOUNT}`, `logs:PutSubscriptionFilter`, the one destination ARN (l.1003–1006); subscriber role puts to `stream.attr_arn` only (l.995–997); delivery role `WriteUnderCallsOnly` on `calls/*` put+abort (l.960–961); bucket Allow by `ArnEquals aws:PrincipalArn` = delivery role, Deny `s3:PutObject` under `calls/*` for `ArnNotEquals` (l.925–934); read role `READ_PREFIXES += "calls/"` (l.860); trail `LOGGED_PREFIXES += "calls/"` (l.865). All held by the three tests in test_containment_stacks.py.
> - Access-log format (l.463–469): requestId, time, status, method, path, sourceIp, error.message, authorizer.error/subject/issuer/outcome/reason, integration.status. No header, no token field; `from_raw` refuses a record with a credential key anyway (caller.py `refuse_credential`).
> - Workflows: top-level `permissions: {}` in deploy.yml (l.150) and evals.yml (l.202); every job `contents: read` (+ `id-token: write` where it assumes a role); every `uses:` across .github/workflows pinned to a 40-char SHA; no `pull_request_target`; no PR title/body/branch in any `run:`; the new `run:` lines use `$NAME` and stack outputs.
>
> ## Findings
>
> FINDING — Unverified strings reach the evidence record unescaped. The authoriser copies the token's *claimed* `username`/`client_id`/`sub` and `iss` into its context on a refusal (door.py l.500–507), and the stage writes `$context.authorizer.subject`, `$context.authorizer.issuer` and `$context.path` into a JSON line (l.464–468) that Firehose partitions by `.agent` (security/app.py l.973, 983) with jq-1.6 (last duplicate key wins). A stranger with no credential can put `"` or a newline in a claimed username or the request path. If API Gateway does not JSON-escape these values, the line can carry a second `agent` key or split into a second, wholly forged line (`outcome: admitted`, any subject) under `calls/agents/<any name>/`, and `_read_access_log` (caller.py l.145–162) checks none of `agent`, `subject` or `issuer` against anything. Settle: the authoriser clips `claimed` to SPEC/10 §2's subject pattern and `iss` to a URL charset with a length cap before it enters the context; the format uses `$context.routeKey` not `$context.path`; `from_raw`/the observer refuse a line whose `agent` is not the prefix it was read under; one probe at festival-desk's deploy with `%22` and `%0A` in a claimed username, read back from `calls/`. Security (door.py, the format); Engineering (from_raw).
>
> FINDING — The authoriser crashes on a token whose payload is not an object or whose `exp` is not a number. `header, claims = json.loads(...)` is inside the `try` (l.496–499) but `claims.get("username")` (l.500) and `claims.get("exp", 0) < time.time()` (l.506) are outside it; a payload `[]` or `exp: "x"` raises, API Gateway answers 500, and the record names nobody (subject `-`, reason `-`), which is the F10.3 shape. Not covered by `test_the_authoriser_reads_a_header_that_is_not_a_token_as_no_identity` (its inputs are `not-a-token`, `Bearer x.y`, `Bearer`, ``). Settle: `isinstance(claims, dict)` and the exp compare inside a try returning `not admitted`; one test with a `[]` payload and a string `exp`. Security (door.py); Engineering (the test).
>
> FINDING — The execution role's pool and API statements are not held to the agent tag. `ManageAnAgentsPoolItsUsersClientsServerAndDomain` grants `DescribeUserPoolClient` (reads any client's secret), `AdminCreateUser`, `AdminDeleteUser`, `DeleteUserPool`, `UpdateUserPoolClient` on `userpool/*` with no condition (l.241–254); `MakeADoorApiOnly` grants POST/PATCH/PUT/DELETE on `/apis/*` with none (l.264–270). The guardrail statement two screens up uses `conditions={"Null": {"aws:ResourceTag/agentkeel:agent": "false"}}` (bootstrap/app.py l.825) and the deploy role's new read does too (l.298); the pool is tagged (`user_pool_tags={AGENT_TAG: ...}`, l.672) and so is the API (l.780). The DoorGrants suppression reason says only "the pool's id is the service's" (l.320), which explains the `*` in the ARN, not the missing tag condition. Settle: the resource-tag condition on both (CreateUserPool stays on the request tag), or a sentence in the reason saying why Cognito/API Gateway v2 cannot take it. Security.
>
> FINDING — The door's cdk-nag rows are read by nothing. The committed construct NagReport is refagent's, whose stack has no door, so it is unchanged in this diff; the COG2, COG8 and two IAM5 suppressions are under `if stack.agent.door_api is not None` (construct/app.py l.392) and only ever apply to a template no report of which is committed. `door_template` asserts `code == 0` on the synth (test_m10_platform.py l.80–81); `app.synth()` does not fail on cdk-nag error annotations, and nothing opens the fixture's `AwsSolutions--AgentkeelAgent-NagReport.csv`. A Non-Compliant row on the doored template (APIG, COG1, L1 or an unsuppressed IAM5) would be unseen. Settle: the test reads the fixture synth's NagReport and asserts no `Non-Compliant` row, as `check_cdk_nag` does for the committed apps. Security.
>
> FINDING — A dead KDF1 suppression with a wrong reason. security/app.py adds `"CallsStream/Resource": ("AwsSolutions-KDF1", "... which this rule reads only as a customer-managed key ...")` (l.1025–1030), but the regenerated report reads `"AwsSolutions-KDF1","AgentkeelSecurity/CallsStream","Compliant"` (l.830): the rule accepts `AWS_OWNED_CMK`, and the L1 stream's path has no `/Resource`, so the suppression matches nothing. Settle: delete the entry. Security.
>
> FINDING — The ruling the diff cites is not in the tree. `milestones/M10/rulings/pr2-security.md` is named by deploy.yml (l.9), bootstrap/app.py (l.204, 217, 293), governed_agent.py (l.580), workflows.sha256 (l.1050, 1054) and SPEC/10 §11 R2 ("Ruled at PR 2 (`pr2-security.md`)"). `milestones/M10/rulings/` holds pr1.md, pr1-engineering.md, pr2.md and pr2-tool-owner.md; pr2.md's header says "the five ruling files. Security's file is pr2-security.md". Settle: the DRAFT with `pr: 55` committed before #55 opens (R2 the hybrid, R3 the bypass arm as an assumed role, the Unsure items below named in it). Security writes it; Product's `ruling-cited` reads it.
>
> FINDING — The door functions' egress is open and no reader sees it. Neither CfnFunction has a `vpc_config` (l.768–775), so SPEC/00 §4's default-deny egress and the construct's S3 egress check (`_egress`, which reads security groups) do not apply to the one process that holds the door client's secret in memory. The module comment states it "under Unsure, Security" (l.586–587); SPEC/10 §2 row 2 says the same. Settle: pr2-security.md accepts it by name (the hosted token endpoint has no interface endpoint; `cognito-idp` and the runtime's bearer endpoint may), or the functions take the platform VPC with the endpoints they need. Security.
>
> ## Notes
>
> NOTE — Nothing here has fired live. The runtime's one-client refusal fired in the probe on throwaway names (door_probe.md, `wrong-client` 401), not on a platform runtime; the authoriser and proxy ran under test with a test key (`sign(...)`), not against Cognito; the delivery, the subscription and "The door the stack built" have never run (the first doored deploy is festival-desk's, PR 3). None of these is "secure" or "proven" yet, and the PR body should not say so.
>
> NOTE — The deploy role's read is held to `aws:ResourceTag/agentkeel:agent` (l.298). Whether Cognito evaluates a resource tag on `DescribeUserPoolClient` is unverified by anything in the tree; if it does not, the step fails closed (AccessDenied, `set -e`). Read at the first doored deploy.
>
> NOTE — Firehose into an Object Lock bucket is unverified. The bucket has `object_lock_default_retention` (security/app.py l.241); S3 requires an integrity header on puts under default retention, and whether Firehose's S3 delivery sends one is not read anywhere. The stream has no `cloud_watch_logging_options`, so a refused delivery is silent; the observer would read `calls/agents/<name>/` as empty and row 10 as unread. Settle at PR 3's run; a stream log group in the security account would make a failure visible. Security.
>
> NOTE — The subscriber role trusts `logs.us-west-2.amazonaws.com` with no `aws:SourceArn`/`aws:SourceAccount` condition (l.990–994); the delivery role's trust does carry `sts:ExternalId` (l.955–956). AWS's destination guidance names the condition against the confused deputy; one line. Security.
>
> NOTE — The ReadRole IAM5 suppression now covers `calls/*` (report l.819) with a reason that names AWSLogs/*, agents/*, test/*, envelopes/agents/* and observations/* and not calls/. Add "M10 PR 2 (SPEC/10 §6): calls/*" to the reason. Security.
>
> NOTE — `jwks()` fills once and never refetches on a `kid` miss (l.478–482, 503); a rotated pool key would refuse valid tokens until the container recycles. Cognito does not rotate pool signing keys on its own; fine for M10, named here.
>
> NOTE — `calls/` inherits the bucket's lock as it stands: `LOCK_DAYS = 1` COMPLIANCE (security/app.py l.108; R5 as amended at M05 PR 1), not seven years. Pre-existing, not this PR's; a change is two keys.
>
> NOTE — Can it be switched off from inside? Yes, by anyone with write: `allowed_clients=[self.door_client.ref]` and `_door()` are Python in governed_agent.py, Security's under `ruling-cited` and this review, which SPEC/10 §8 says `two-key` does not read. The one mechanical reader is `test_the_runtime_admits_the_door_client_only...` on the fixture, which the same PR may edit under Engineering's cold review. An agent repository's `callers` list is one commit with no two-key (SPEC/10 §8). Nothing in this diff changes that; say it in the PR body.
>
> NOTE — workflows.sha256's two new hashes (l.1058–1059) are not verified here; `make validate` reads them. The hash file's comment cites the absent ruling (the FINDING above).
>
> NOTE — The deploy step passes the secret to curl on the command line (`-u "$client:$secret"`, l.31): visible to processes in the same job for the call's duration on an ephemeral runner. `--netrc-file` from `$RUNNER_TEMP` would keep it off the argv. Minor. Security.
>
> BLOCK: 0 · FINDING: 7 · NOTE: 10

## Unsure, for this seat

| # | Item | By |
|---|---|---|
| A | Whether the API's access log records an authoriser's refusal with its context and a no-token request with its request id (pr2.md A) | festival-desk's deploy |
| B | Whether the subscription's delivery lands under `calls/agents/<name>/` within N, and whether Firehose's put passes the bucket's lock (pr2.md B) | the security stack's deploy |
| C | Whether Cognito evaluates the agent tag on the deploy role's and the execution role's pool actions; a refusal there is a PR 3 repair | festival-desk's deploy |
| D | The probe with a quote and a newline in a claimed username, read back from `calls/`, on PR 3's list | PR 3 |
