# SPEC/10 — The public caller

Status: DRAFT · Owner: Product seat · Written at M10 PR 1, the plant,
from SPEC/00 §8 M10 (added at this PR; ADR-0015) · Reviewed by
`product-spec-reviewer` before anything else of PR 1 was written
(`milestones/M10/feasibility.md` §1: 0 BLOCK, 9 FINDING, 3 NOTE) and
revised once on its findings (§2 the record's mapper and its two
timestamps, no `guardrail` on a call record; §4 F10.2 and F10.4; §5 S1's
two more records; §9 cut 4 struck; §11 R2's fallback for (a)).

M10 opens after M09 closed GREEN and was tagged (`m09` on `833ab2b`,
2026-10-13). It is opened by a Product ruling
(`milestones/M10/rulings/pr1.md`), as M09 was (ADR-0014 decision 1), not
by a finding of M09, and it reopens none of M09's rows and repairs
nothing M09 found. It takes one item and nothing else: "the public
caller", which SPEC/05 named (S4, "a caller lying about its depth:
Identity, M07"), SPEC/00 §12 shelved ("credentials only via Identity"),
and SPEC/09 §11 R6 ruled at M09 PR 2 as "M10, its own claim, opened only
by a Product ruling". The record names it and never defines it. Defining
it is this spec's first job (§2).

## 1. The claim

**Claim 10.** A caller outside the platform reaches an agent only through
a door the platform controls, under an identity the agent's manifest
admits, with the agent's pinned guardrail on every answer and the caller
named in each call's record in the security account; a caller with no
identity, or one the manifest does not admit, is refused and the refusal
is in the security account within N.

For a director: *someone outside the team can only ask an agent a
question through the platform's front door, under a name the agent's
owners agreed to; every answer still carries the agent's rules, every
question is recorded with who asked, and a stranger is turned away and
the attempt written down* (SPEC/00 §10.3 row 10).

Threat answered (SPEC/00 §3): an outside caller who reaches an agent
around the platform's door, or under an identity the agent's manifest
does not admit, or leaves no name on the call's record.

**Four parts, and the claim needs all four.**

- *Only through a door the platform controls.* Today there is no door:
  the runtime answers any IAM principal in the platform account that
  holds `bedrock-agentcore:InvokeAgentRuntime` on it, and nothing else
  decides (§3). After M10 the only way to an agent that has callers is
  the door, and a call that does not pass it is refused whoever makes
  it.
- *Under an identity the agent's manifest admits.* The agent's manifest
  says who may call it, in a field a seat owns (`callers`, Tool Owner),
  and the door admits those and no one else. A manifest that does not
  say is refused by the platform check.
- *With the agent's pinned guardrail on every answer.* The guardrail is
  on the agent role's model call inside the runtime (M03 PR 2, M09 PR 2:
  `infra/construct/governed_agent.py`, the `bedrock:GuardrailIdentifier`
  condition on `InvokeItsOwnProfileOnly`). The door is in front of the
  runtime and cannot take it off. This part is a guard, read on the
  answer record of the deploy that put the door on (the goldens asked
  through the door as `platform`, `g-030` still blocked by its rule) and
  on refagent's envelope, as M09's F9.5 was a guard that the split
  relaxed nothing. A call record cannot see the model call, so it does
  not carry the guardrail (reviewer finding 2).
- *The caller named in each call's record, and the refusal recorded
  within N.* Each call, admitted or refused, leaves one record in the
  security account's audit bucket that names the subject, the issuer,
  the agent, the outcome and the time, written by the door's log
  delivery and never by the agent (P5). A refused call's record arrives
  within `detection.max_seconds`, 600 s, the bar M05's attempts were
  read against. Today no record of any call names who called (§3).

**What this milestone builds: one control and the reading of it.** The
control is the door, with the identity it admits and the manifest field
that says who. The reading is the call record, read by the observer and
ruled on by `build` into the envelope's `caller` field. The control is
not described as working until it has refused its seeded case (SPEC/00
§10.5), and no reading of a call stops a merge at M10 (§4).

**The measured value for claim 10** is the live run's calls, **admitted n
of n and refused m of m, each on the record within N**, read from the
call records after the door is deployed, with F10.1 to F10.5 held. At the
run, n is 1 and m is 3. **Expected: admitted 1 of 1, refused 3 of 3**
(§7), with the risk §7 names first: whether a call refused at the
service's edge, before anything the platform runs sees it, leaves a
record the security account can hold. That is the item most likely to
threaten the cap, and §11 R2's probe answers it before PR 2 opens.

## 2. Words used here

- **The public caller.** A principal that is not the platform: not the
  eval role, not the deploy role, not the owner's IAM user or any role
  in the platform account (581208540944), and not an agent. At M10 it is
  an identity the door issues: a user in an identity pool the platform
  deploys for the agent, holding no AWS credential at all. The owner
  makes the calls from a laptop as that user, with the user's token;
  the laptop's own IAM principal is never presented as the caller and
  is used only for the bypass arm, where it stands for a platform
  principal the door does not admit (§5, the run). A second IAM
  principal in the platform account is not outside and is not the
  caller.
- **The door.** The one path by which a call reaches an agent's runtime.
  Which door is Security's ruling (§11 R2). The three candidates, their
  costs and the proposal:

  | # | Door | What admits a caller | Record of a refusal | Cost | Unknowns |
  |---|---|---|---|---|---|
  | 1 | **The runtime's own JWT authoriser** (AgentCore Runtime `authorizerConfiguration`, `customJWTAuthorizer`): the construct sets the agent's identity pool as the issuer and the agent's app client as the allowed client; a Cognito user pool per agent in the agent's own stack, its users made from `callers`. **Proposed.** | the pool's issuer and client at the service edge; a token for another pool or client is refused before the container; no token is refused the same way. A call signed as an IAM principal is refused once the runtime is in JWT mode, so the platform's own goldens caller (`deploy.yml`, "The agent answers its own goldens") presents a token too, as a `platform` client the construct makes | the service's own record of the refused `InvokeAgentRuntime`, delivered to the audit bucket as M05's attempts were (CloudTrail), or the runtime's log delivered by a subscription the bootstrap deploys | smallest diff: one construct property, one pool and two clients per agent, one deploy step changed to fetch a token; no new code path the platform must defend | (a) JWT mode refuses SigV4 outright; (b) the admitted call's subject is readable where the record is written; (c) a refusal at the edge leaves a record the security account can hold within N. Each is a yes-or-no the probe answers (§11 R2). If (a) answers no, the bootstrap's `InvokeAgentRuntime` grants are narrowed by a condition on a runtime tag the construct sets for an agent with `callers` (`agentkeel:door=jwt`, proposed), so no platform principal holds the grant on a doored runtime; failing that, door 2 (finding 4) |
  | 2 | **API Gateway with a Lambda authoriser** in front of `InvokeAgentRuntime`: the authoriser reads the token and the registry row's `callers`, a second Lambda holds `InvokeAgentRuntime` on the agent's runtime; the runtime's own grant narrows to that Lambda's role | the authoriser, by subject against `callers` | the API's access log, with the authoriser's `principalId`, delivered to the audit bucket | two Lambdas and a role holding `InvokeAgentRuntime`, all code Engineering and Security own and must defend; the runtime still answers any IAM principal with the grant, so F10.1's bypass arm needs the runtime's grants narrowed too | none in AWS; the record is certain. **The fallback** if door 1's probe answers no on (c) |
  | 3 | **The AgentCore Gateway** with an HTTP passthrough target to the runtime and admission by policy | the gateway's inbound authoriser and its policy | the gateway's own log | the gateway, a target per agent, a gateway role holding `InvokeAgentRuntime`; SPEC/00 §12 names the gateway as not built and would need amending | whether a target can be the runtime's invocations endpoint; whether policy admits by subject; whether the record names the caller. The most unknowns. Not proposed |

  Probe 2 of 2026-09-27 (the memory note `agentcore-gateway-llm-assessment`,
  `~/probe-llmgw/out2/`) showed Converse, the trace and the guardrail
  surviving a gateway between the agent and the model. That gateway sat
  between agent and model, not between caller and agent, so it picks no
  door for M10; it is cited because it is the only probe of a door this
  project has made.
- **The identity pool.** A Cognito user pool per agent, in the agent's
  own stack, made by the construct for an agent whose manifest has
  `callers`: one user per subject in `callers`, one app client for
  callers, one `platform` client with client credentials for the deploy
  step's goldens run. Its issuer URL is what the door admits. The pool
  is Security's (the construct); the subjects in it are the Tool Owner's
  (the manifest field). A user's first credential is set by the owner by
  hand, outside the repository, before the run (§5.1).
- **`callers`.** A manifest field (Tool Owner; `src/manifest/schema.json`
  grows it at PR 2): a list of `{subject, issuer}` entries, `issuer` the
  agent's own pool at M10. `callers: []` means no outside caller and no
  pool. A manifest with no `callers` key is refused by the platform check
  from PR 2 ("an agent's manifest says who may call it, even if nobody"),
  so refagent's and `ratings-helper`'s gain `callers: []` at PR 2 (Tool
  Owner, one key: an empty list admits no one and relaxes nothing).
  Not an edge: a caller is not an agent, so `may_be_called_by`'s
  two-sided check does not apply. Not a rule: it says who, not what may
  be said. The platform's own goldens caller is admitted by the construct
  as the `platform` client and is named `platform` on the record; it is
  not in `callers` and is not an outside caller.
- **The call record.** One object per call in the audit bucket of the
  security account (897698239547), under a prefix the bucket policy
  gives the delivery and no agent role (`calls/agents/<name>/`,
  proposed; Security). **Two shapes, and who writes each** (reviewer
  finding 1). The *raw* record is what AWS delivered, byte for byte
  (CloudTrail's data event for `InvokeAgentRuntime`, or the runtime's log
  line, as the probe's question (b) and R2 decide); it is written by the
  delivery and by nothing the platform runs. The observer
  (`scripts/observe_caller.py`) copies each raw record with the object's
  `LastModified` (its arrival) and the time it was read, and writes
  nothing else. The *read* record is `build`'s reading of a raw one
  (`src/verdict/caller.py` `from_raw(event)`): `subject`, `issuer`,
  `agent`, `outcome` (`admitted` or `refused`), `reason` for a refusal
  (`no identity`, `not admitted`, `not the door`), `request_id`, `time`
  (AWS's `eventTime` of the call) and `delivered` (the object's
  `LastModified`). The read shape is fixed here so the seeds and PR 2
  agree (§5); the raw shape is known only after the probe, so S1's
  fixtures are read records and PR 2 plants one raw record from the
  probe's output as its own first commit, before `from_raw` exists
  (`/open-milestone` step 4's allowance). A call record carries no
  guardrail: the delivery cannot see the agent role's model call
  (finding 2).
- **Admitted.** A call whose read record has `outcome: admitted` and
  whose `subject` is in the agent's `callers` (or is `platform`).
- **Refused.** A call whose read record has `outcome: refused` with its
  reason, and `delivered` minus `time` at most N (the same two
  timestamps M05's `alarm_latency_s` read: AWS's event time against the
  object's arrival, never the observer's read time; finding 3). A call
  that was refused and has no record with `delivered` within N of its
  `time` is **unrecorded**, which is F10.4's second arm, and a call that
  reached the agent without passing the door is **a bypass**, F10.1.
- **N.** `detection.max_seconds` in `thresholds.yaml`, 600 s (Threshold
  Owner, M05 PR 2). Reused, not added (§11 R6); no bar moves at M10.
- **The fixture agent.** `festival-desk`, M09's agent, public at
  `agentkeel-studio/festival-desk`, deployed at `19864419` with guardrail
  `at8e36cosq1r:1`, its first answer record at
  `envelopes/agents/festival-desk/cd0ad604….json` (row 9's close detail).
  It is reused as the agent the caller reaches: its manifest gains
  `callers` in a pull request of its own repository after PR 2 merges,
  its stack gains the pool and the authoriser at the deploy that
  follows, and its plant `g-030` is what F10.2 reads through the door.
  Nothing in it is changed from an agentkeel session; the owner opens
  its pull request by hand (§5.1).
- **The run file.** `milestones/M10/runs/f10_x_caller_run.yaml`: the
  four calls to make after PR 2 merges and the door is deployed, each
  stated first with its expected outcome; `observed: null` until the
  owner fills the keys (M05's pattern).
- **Recorded, not gated.** The live reading goes into the envelope's
  `caller` field and is read by row 10's Measured cell. The gate rules
  nothing on it at M10: a bypass, an answered stranger or an unrecorded
  refusal makes row 10's cell RED whatever refagent's own verdict, and
  stops no merge.
- **P5.** `scripts/observe_caller.py` writes raw observations (the call
  records as the bucket holds them, with the time each was read);
  `src/verdict/build.py` rules on them into `caller`; `src/verdict/gate.py`
  reads the envelope; `src/ledger.py` reads the gate. No reader writes
  its own verdict, and the agent writes nothing about its callers.

## 3. The false state

Claim 10 is false if any of these is on `main`. Each names something a
reader can open. **Live today, at `833ab2b` (tag `m09`).**

1. **The runtime answers any IAM principal with the grant, and there is
   no door** (F10.1). `src/agent/run.py:81-88` (`invoke_deployed`) calls
   `invoke_agent_runtime` with an ARN and a payload and nothing about
   who is calling; the bootstrap grants `InvokeAgentRuntime` to the
   deploy role on `runtime/refagent*` and `runtime/agentkeel_*`
   (`infra/bootstrap/app.py`, `CallTheRuntimeItJustDeployed`) and to the
   eval role on refagent's (`InvokeRefagentRuntimeOnly`); the owner
   called drill-agent's runtime by hand at M08 with the Python SDK. The
   construct sets no `authorizerConfiguration` on the runtime
   (`governed_agent.py`: the runtime resource carries the image, the
   role, the network and the environment, and no authoriser), so IAM is
   the only check and any principal the account grants is in. No
   principal outside the account is granted anything, so an outsider is
   refused today by IAM's default, with no record anywhere the platform
   reads: the platform has no outside caller, admitted or refused.
2. **No record of a call names who called** (F10.3). The answer record
   `build.compose_answer` writes (`src/verdict/build.py:1005-1020`) has
   `repository`, `agent`, `commit`, `platform_commit`, `runtime_arn`,
   `model_id`, `region`, `guardrail`, `goldens`, `observations`,
   `errors`, `tokens_in`, `tokens_out`, `run_url`, `verdict` and `what`,
   and no caller; it is written once
   per deploy by the goldens step, not once per call. M05's attempt
   records in the audit bucket are CloudTrail's events for IAM
   principals; a call by an identity that is not an IAM principal has no
   record there. No module under `src/` or `scripts/` has the word
   `caller` in a field it writes.
3. **No manifest field says who may call** (F10.4). `src/manifest/schema.json`
   has `may_call` and `may_be_called_by`, both lists of `<agent>@<major>`
   for agents, both empty in every manifest in the tree; it has
   `additionalProperties: false`, so a `callers` key is refused by the
   `manifest schema` check today. The platform check (`src/validate/agent.py`)
   reads no such field. So no agent's manifest can admit or refuse a
   caller, and nothing can refuse a manifest that does not say.
4. **A caller admitted with one key** (F10.5). `src/gates/two_key.py`'s
   closed list (SPEC/02 §2; ADR-0009 entries 1 to 6) reads thresholds,
   goldens, rule files, a manifest's guardrail, budgets, `deprecated_after`
   and memory; a manifest key that admits a caller is on no entry, so a
   diff adding one passes `two-key` with one ruling. The construct is
   Security's under `ruling-cited` and `security-reviewer`, not `two-key`,
   and an agent repository has no `two-key` at all (SPEC/00 §12).
5. **Nothing reads a call** (F10.1 to F10.4). There is no
   `scripts/observe_caller.py`, no `src/verdict/caller.py`, no `caller`
   field in `src/verdict/schema.json`, and `gate.py`'s per-milestone
   readers stop at `READ_THE_RULES`.

**Expected to hold today, named so nobody plants it as open.**

6. **The guardrail is on the model call, not on the door** (F10.2). The
   construct conditions the agent role's invoke on the pinned guardrail
   at its version (`governed_agent.py`, `InvokeItsOwnProfileOnly`), and
   the server passes it to converse; festival-desk's answer record names
   `at8e36cosq1r:1` and `g-030` blocked by its rule (row 9's cell);
   refagent's envelopes read `plants 7/7`. F10.2 is the falsifier that the
   door's construct change breaks any of this: it holds today and must
   hold after the door.

## 4. Falsifiers

| Id | Fires when | What it looks like in the repo |
|---|---|---|
| F10.1 | a call that does not pass the door reaches the agent: the outside caller directly on `InvokeAgentRuntime` with an IAM credential, or a platform principal the construct does not name (the eval role, the deploy role or the owner's role signing a call, where the runtime is in JWT mode and only the `platform` client is admitted) | `checks.F10_1: fail` from S1's fixture test (a record of a call that reached the agent with `reason: not the door` read as not held); live, the run file's `bypass` step: the owner's laptop principal, holding the grant, calls the runtime directly after the door is deployed and must be refused, the refusal on the record |
| F10.2 | a call through the door loses the guardrail: festival-desk's answer record from the deploy that put the door on (its goldens asked through the door as `platform`) names a guardrail other than its pin or reads `g-030` other than 1 of 1, or refagent's plants read under 7 of 7 on the first envelope after the construct change. A call record carries no guardrail (finding 2); the live reading is the answer record's and refagent's envelope's only | `checks.F10_2: fail` from S4's guards (the construct's invoke condition on the fixture agent's synthesised stack; refagent's latest envelope `plants 7/7`); live, `caller.F10_2` on festival-desk's answer record after the deploy, and `plants_fired` on refagent's envelope |
| F10.3 | a call's record names no caller, or a caller other than the one that called: the admitted call's read record carries no `subject`, or a `subject` that is not the user the owner called as; a refused call's record names a subject other than the stranger's (or other than none, for the no-identity call) | `checks.F10_3: fail` from S1's fixture test (today's answer record, with no caller, read as not held; a record whose `subject` is not the stated caller read as not held); live, `caller.records` on the envelope, each record's `subject` against the run file's stated caller |
| F10.4 | a caller with no identity, or one the manifest does not admit, is answered; or is refused with no record in the security account within N: `delivered` (the object's `LastModified`) minus `time` (AWS's `eventTime` of the call) over 600 s, or no record at all | `checks.F10_4: fail` from S1's fixture test (a record of a stranger answered; a refusal delivered later than N) and S2's (a manifest with no `callers` admitted by the platform check); live, the run file's `none` and `stranger` steps, each `outcome: refused` on a record with `delivered` within 600 s of its `time` |
| F10.5 | a caller is admitted with one key: a subject added to a manifest's `callers`, the key removed, or the construct's authoriser widened (a second issuer or client admitted) merges without two seats' rulings | `checks.F10_5: fail` from S3's seed (refagent's manifest gaining a `callers` entry with the Tool Owner's ruling alone, in a copy of the tree, which `two-key` must refuse under ADR-0009 amendment 2); live, `two-key` on PR 2's own diff and on the fixture's. **The agent repository's half is unread** (§8): an agent repository has no `two-key`, so festival-desk's `callers` pull request is admitted on the platform check alone; named, not measured |

**Where each reading comes from** (M04's to M09's lesson, planned at
open).

- **On every agent envelope, from PR 2's merge: `F10_1` to `F10_5`**,
  from the seed tests: each reader refusing its fixture, and S4's
  guards. **Test-only witnesses**, and the ledger says so.
  `CLAIM_10_CHECKS` in the gate is those five.
- **The live reading is recorded, not gated.** It lives in the security
  account and in the fixture agent's repository, after PR 2 merges and
  the door is deployed (§5.1). `scripts/observe_caller.py` (Engineering)
  writes raw observations only: each call record as the bucket holds it,
  the answer record of the deploy that put the door on, refagent's
  envelope's plant count, and the time each was read. `build` rules on
  them into an optional envelope field `caller`; the gate rules nothing
  on it. **Row 10's Measured cell reads `caller`**, as row 9's read
  `agent_rules`: a bypass, an answered stranger, a record with no
  caller, an unrecorded or late refusal, or a lost guardrail makes row
  10's cell RED whatever refagent's own verdict. A RED measurement never
  blocks a pull request.
- **Which run the cell cites.** PR 3's run's envelope: the door is
  deployed and the calls made after PR 2 merges (§5.1, a named P3
  exception as M07's, M08's and M09's). If the platform's own deploy
  path needs a repair, the run is read by PR 4's run and the cell cites
  that (M08's second exception, which M09 used).
- **A human-written file feeds no reading by itself.** The run file
  names the agent, the four calls and their stated outcomes; the reading
  is of the records in the bucket, never of the file's prose.
- **P5.** `tests/test_p5_disagree.py` gains a case for each new check.

## 5. The seeded cases

Planted at PR 1, in one commit before any reader, each with its tests in
`tests/test_m10_seeds.py`, marked `xfail(strict=True,
raises=AssertionError)`, run once with `--runxfail` so the message is
read; preconditions raise `SeedBroken`. Each is named in
`tests/fixtures/README.md` and in `src/verdict/plants.py` as
`SEEDS_M10`; none is copied to `evals/history/`.

| Seed | Falsifier | Planted as | Fails today because | Read by (PR 2) |
|---|---|---|---|---|
| S1 the call records | F10.1, F10.3, F10.4 | `tests/fixtures/m10/s1-call-records/`: six files for festival-desk, each in the **read** shape of §2 but the first. `record_no_caller.json` is **today's answer record shape**, as `build.compose_answer` writes it (the fields §3.2 lists, no `subject`, no `outcome`): the reader must read it as not held, "names no caller". `call_stranger_answered.json` has `subject: stranger`, not in `callers`, and `outcome: admitted`: not held, "a caller the manifest does not admit was answered". `call_bypass.json` has `outcome: admitted` with `reason: not the door` and no `issuer`: not held, "reached the agent without the door". `call_wrong_subject.json` has `outcome: admitted` with a `subject` that is in `callers` but is not the caller the run stated: not held, "names a caller other than the one that called" (finding 5). `call_refused_late.json` is the stranger's refusal with `delivered` 601 s after `time`: not held, "recorded later than N" (finding 5). `calls_held.json` is the admitted user's call, `outcome: admitted`, beside three refused records (`none`, `stranger`, `bypass`) each with `delivered` within N: held, admitted 1 of 1, refused 3 of 3 | nothing reads a call record (§3.5) | `src/verdict/caller.py`: `calls(records, stated, callers, max_seconds)` returning `{read, held, admitted, refused, expected_admitted, expected_refused, reasons}`, `stated` the run file's callers per step; and `from_raw(event)`, whose raw fixture is PR 2's first commit (§2) |
| S2 a manifest with no `callers` | F10.4 | `tests/fixtures/m10/s2-manifest-no-callers/manifest.yaml`: festival-desk's manifest as its repository holds it at `19864419` (pin `at8e36cosq1r:1`, every seat the author, `may_be_called_by: []`, no `callers`). Two planted tests: `src.validate.callers.callers_errors(manifest)` must refuse it naming the field; and `with_callers.yaml`, the same manifest with `callers: [{subject: lantern-desk, issuer: <the pool>}]`, must pass the manifest schema | `src/validate/callers.py` is not in the tree; the schema's `additionalProperties: false` refuses `callers` (§3.3) | `src/validate/callers.py`: `callers_errors(manifest)`; `src/manifest/schema.json`; `src/validate/agent.py` `evaluate()` calling it |
| S3 a caller admitted with one key | F10.5 | `tests/fixtures/m10/s3-caller-added/cases.json`: refagent's manifest, as this tree holds it, gaining `callers: [{subject: …, issuer: …}]` with the Tool Owner's ruling alone, in a repository whose base holds `callers: []`; and the key removed the same way. `two-key` must refuse each naming the path and ADR-0009 amendment 2; with Security's second key the same diff passes (M07's two-key seed pattern, `tests/test_m07_two_key_seed.py`) | `two_key.relaxations` has no entry for `callers` (§3.4) | `src/gates/two_key.py` (entry 7, ADR-0009 amendment 2) |
| S4 the guardrail stays on the call | F10.2 | two **guards**, no fixture: the fixture agent's stack as the construct synthesises it today (`tests/fixtures/m09/s1-festival-desk/`, through `tests/test_m09_platform.synth`) conditions the agent role's invoke on the stack's own guardrail at its version; and the latest CI-written envelope under `evals/history/` reads refagent's `plants_fired` equal to `plants_expected`, 7 of 7. Both pass today and must pass after the door is added to the construct | nothing: they pass, and that is the point | `infra/construct/governed_agent.py` (changed at PR 2) and `src/verdict/gate.py` (in the tree) |
| The run | F10.1 to F10.4, live | `milestones/M10/runs/f10_x_caller_run.yaml`: the agent, the four calls (`admitted` as the pool user named in `callers`; `none` with no token; `stranger` with a token from a pool the construct did not make; `bypass` as an IAM principal directly on the runtime) with each stated outcome, the record each must leave, and `observed: null` | the run is not made: no door exists, and nothing would read it | `scripts/observe_caller.py`, after PR 2 merges and the door is deployed |

**The fixture is fictional.** The agent is M09's festival desk; the
subjects are made-up names of a made-up festival's staff; no real
person, festival, title, contract or studio workflow detail, and nothing
pharmaceutical (SPEC/00 §9).

### 5.1 When each is measured

- **S1, S2, S3 and S4 are read on every run from PR 2**, in the tree, by
  their readers: test-only witnesses for `F10_1` to `F10_5`.
- **The live reading is after PR 2 merges, a named P3 exception.** The
  door is a construct change and a bootstrap change (§6), which only
  `deploy.yml` on `main` deploys for an agent repository (SPEC/06 §6),
  and the identity pool's first credential is set by hand. So, after PR
  2 merges and in this order, each stated in the run file first: the
  owner opens a pull request in `agentkeel-studio/festival-desk` adding
  `callers` with one subject (the platform check must admit it); it
  merges; the scheduled deploy puts the pool, the clients and the
  authoriser on festival-desk's stack and asks its three goldens through
  the door as `platform` (F10.2's answer-record arm is that record); the
  owner sets the admitted user's credential by hand, outside the
  repository; the owner makes the four calls from a laptop in the order
  the run file states, as the pool user, with no token, as a user of a
  throwaway pool the owner makes for the run and deletes after, and as
  the laptop's IAM principal directly on the runtime; the observer reads
  the four records, the answer record and refagent's envelope. PR 3's
  run carries the reading; the cell cites it.
- **Which run PR 3 reads if the deploy fails.** As M07, M08 and M09: if
  the platform's own deploy path needs a repair, PR 3 is that repair and
  the run is read by PR 4's run, which the cell cites. Stated here so it
  is not found at PR 3.
- **The probe is before PR 2 opens, not a step of the run.** Door 1's
  three unknowns (§2) are answered by Security with throwaway names
  outside the repository, as the two gateway probes were (`probe-*`,
  never `agentkeel-*`), torn down after, their outputs committed as
  `milestones/M10/runs/door_probe.md` in PR 2. If (c) answers no, R2
  rules door 2 before PR 2 opens, and the plant is unchanged: the seeds
  read records, not a door.

## 6. The code that reads the answer (PR 2)

One seat and one path each. The seed tests fix the names, so PR 2 does
not choose them.

| What | Path | Seat |
|---|---|---|
| The manifest field | `src/manifest/schema.json` grows `callers` (a list of `{subject, issuer}`, `additionalProperties: false`); `agents/refagent/manifest.yaml` and `agents/ratings-helper/manifest.yaml` gain `callers: []` | Engineering (the schema); Tool Owner (the field and its two empty lists) |
| The platform check's reading | `src/validate/callers.py`: `callers_errors(manifest)`; `src/validate/agent.py` `evaluate()` calls it | Engineering |
| The door | the construct (`infra/construct/governed_agent.py`): for an agent with `callers`, a Cognito user pool, one user per subject, a callers client and a `platform` client, and the runtime's `authorizerConfiguration` set to the pool's issuer and the two clients; the deploy boundary and the eval role as Security rules (R2) | Security |
| The platform's own call through the door | `.github/workflows/deploy.yml`, "The agent answers its own goldens": a token for the `platform` client fetched from the pool, passed to `src/agent/run.py`, which sends it on the invoke; `run.py` gains the header | Security (the step); Engineering (`run.py`) |
| The call record's delivery | `infra/security/` and `infra/bootstrap/`: the records reach `calls/agents/<name>/` in the audit bucket, by CloudTrail's data event or the runtime's log subscription as the probe decides, under a bucket statement no agent role can use | Security |
| The relaxation | `src/gates/two_key.py`: entry 7, a subject added to `callers`, the key removed, or the construct's authoriser widened; `docs/adr/ADR-0009-…` amendment 2, its last | Engineering (the gate); Product (the ADR, naming the Tool Owner's and Security's keys) |
| The reading | `src/verdict/caller.py`: `from_raw(event)` (the raw record to the read shape, §2) and `calls(records, stated, callers, max_seconds)` | Engineering (the module); Data Owner (the read shape, §11 R5) |
| The observer | `scripts/observe_caller.py`, in `evals.yml` on `main` (as `observe_rules.py`); `.github/CODEOWNERS` already takes `scripts/observe_*.py` as Engineering's with no edit (M09 feasibility §2 item 8) | Engineering (the script); Security (the workflow step and the read grant on `calls/`) |
| The envelope | `caller` in `src/verdict/schema.json`; `build` composes it; `CLAIM_10_CHECKS` and `READ_THE_CALLER` in `gate.py`; row 10's reading in `src/ledger.py` | Engineering |
| The documents | `docs/developer/quickstart.md` and `template-README.md` say what `callers` is, that an empty list is the default, and how a caller gets in | Product |

Not in PR 2: the fixture agent's `callers` pull request (PR 3, by the
owner), the probe itself (by hand, before PR 2 opens), any change to a
bar, a golden under `evals/goldens/`, `src/baseline/`, or refagent's
rules.

## 7. Expected on the plant (row 10)

**PR 1.** refagent's envelope as at M09: `plants 7/7`, the M01 to M09
checks as row 9's cell has them; it says nothing about claim 10.
`make plants` lists S1 to S4 and the run (seeded cases, not golden
plants); `tests/test_m10_seeds.py` shows **2 passed** (S4's two guards)
and **5 xfailed** (S1, S2 refused, S2 admitted by the schema, S3, the
run); `--runxfail` shows 2 passed, 5 failed, each with its planted
message. `make validate`'s twenty-one checks pass: none reads a fixture,
a run file or a call.

**PR 2, on the PR.** S1, S2 and S3 refused or read by their readers, each
with its planted reason; S4 still passing; from PR 2's merge the gate
requires `F10_1` to `F10_5` on every agent envelope, test-only witnesses.
On PR 2's own envelope `caller` reads **unread: no door is deployed and
no call has been made**, so row 10's cell would read RED at PR 2. That is
the plant going RED under the measurement, which PR 2 is for. refagent's
`plants_fired` must stay 7 of 7 across the construct change (F10.2).

**PR 3's run, stated at open.** festival-desk's `callers` pull request
admitted and merged; its stack redeployed with the pool and the
authoriser, its three goldens answered through the door as `platform`
with `g-030` still blocked by its rule, 1 of 1, and the answer record
naming its pin; the admitted user's call answered, its record naming the
user; the no-token call, the stranger's call and the bypass each refused,
each on a record delivered within 600 s of its event time.
**Expected: admitted 1 of 1, refused 3 of 3**, F10.1 to F10.5 held, row
10 GREEN. Stated risks, each a reading and not a reason to change the
plant:

- **The refusal's record.** A call refused at the service's edge is
  refused before anything the platform runs sees it. Whether AWS leaves
  a record of it that the security account can hold, and within N, is
  unknown today; it is the probe's question (c), answered before PR 2
  opens. If no, door 2 is ruled and the record is the API's access log.
  If neither door leaves a record within N, F10.4 fires on the record arm
  and row 10 closes RED on it. This is the item most likely to threaten
  the cap.
- **The subject on the admitted record.** Whether the record names the
  token's subject or only its client is the probe's question (b). If
  only the client, F10.3 reads the client against the user's and is
  named as reading the client, not the subject, in the cell; that is a
  weaker reading, recorded, not a miss.
- **The runtime's authoriser change.** Whether setting
  `authorizerConfiguration` on a deployed runtime updates it in place or
  replaces it (a new ARN, a new registry row) is unknown. A replacement
  is a deploy-path reading, not a falsifier; the registry row says which.
- **The platform's own goldens caller.** `deploy.yml` must present a
  token once the runtime is in JWT mode, or every deploy's goldens step
  fails with the runtime refusing SigV4. That is PR 2's work and is
  stated here so it is not found at the first deploy.
- **refagent is not behind a door at M10** (§8). Its envelope's 7 of 7 is
  the guard that the construct change relaxed nothing for an agent with
  `callers: []`.

RED if a call that did not pass the door is answered; if the answer
record through the door lacks the pin, `g-030` reads other than 1 of 1
through the door, or refagent's plants fall under 7 of 7; if a record names no caller
or the wrong one; if the no-token call or the stranger is answered, or
refused with no record within N; if a caller is admitted with one key in
agentkeel; if a seed's test passes for a reason other than its reader; if
PR 3's run cannot read the records; or if `make ledger` stops matching
rows 0 to 9.

## 8. Controls with no seeded case at M10

SPEC/00 §10.5: no document describes these as working.

- **Two keys on an agent repository's `callers`.** An agent repository
  has no `two-key` (SPEC/00 §12); festival-desk's `callers` pull request
  is admitted on the platform check alone, and a second subject added
  there later takes one commit. F10.5 is measured in agentkeel only.
- **refagent behind the door.** refagent's `callers` is `[]`; its
  runtime keeps IAM authorisation and the eval role's grant, so `make
  evals` and the swap runs are unchanged. The door on refagent is a
  later milestone's if any; at M10 one agent has a door.
- **Per-caller limits, a rate limit, a budget per caller.** The door
  admits or refuses; it counts nothing. `ceilings` is unchanged.
- **A caller that is an agent.** `may_call` and `may_be_called_by` stay
  empty and unread for callers; an agent calling an agent through the
  door is not planted (no edge exists, SPEC/00 §12).
- **The subject's credential.** How a pool user's first credential is
  set and rotated is by hand; not planted. A credential that leaks is
  M05's S5 shape and is not re-planted here.
- **A token replayed or forged.** The authoriser's own verification of
  the signature and expiry is AWS's; not planted.
- **The record's integrity after N.** The audit bucket's lock is one day
  (M05, two keys); M08's F8.4 read a record's single version; M10 reads
  arrival within N and does not re-read the lock.
- **A door removed from a deployed stack.** The construct change that
  takes the authoriser off an agent that has `callers` is Security's
  under `ruling-cited` and the proposed entry 7; its live half (a redeploy
  without the door) is not planted.
- **The AgentCore Gateway, AgentCore Identity's vault, a policy engine,
  Cedar, per-tool limits, log-only mode:** not built at M10 (§12).
- **The security account's own admin acting on `calls/`:** not stopped
  by this platform (SPEC/05 §8). The landing zone's.

## 9. Cut list

In order, if the cap is threatened. **Never cut:** the door, the
`callers` field and its refusal, the call record, the four live calls
with the bypass refused, the platform's own goldens caller through the
door (the `platform` client: without it the bypass arm has nothing to
refuse, reviewer finding 6), S1 to S4 or their readers, row 10's reading
of `caller`, or the measured value.

| # | Item | Then | Why |
|---|---|---|---|
| 1 | The quickstart's and template README's sections on callers | one paragraph each naming the field and that an empty list is the default; the rewrite at the close by `docs-writer` | documents, not readings |
| 2 | `ratings-helper`'s `callers: []` | refagent's manifest alone gains the field; `callers_errors` refuses a manifest with no field only for an agent the platform check reads in an agent repository, and `ratings-helper`'s stub is read as before | the stub has no code and no runtime (SPEC/00 §12); one less Tool Owner diff |
| 3 | The subject on the record (F10.3's second half) | F10.3 reads the record's client against the admitted user's client and names it as reading the client; the subject is read from the answer the owner received, by hand, and recorded in the run file's `observed` as a note the observer does not read. The plain sentence's "who asked" then reads as "which app asked", and the explainer's "What happened" says so (reviewer note 12) | the probe's question (b) may answer no; the record still names a caller, less finely |
| 4 | `src/validate/callers.py`'s issuer check (that `issuer` is the agent's own pool) | the construct refuses an issuer it did not make at synth; the platform check reads the field's shape only | the refusal moves from the platform check to the build; the reading is the same |

A fifth item, the `platform` client replaced by a mixed mode admitting
IAM beside tokens, was in the first draft and is struck: it would change
the door and remove the bypass call's refusal, both never cut (finding
6).

## 10. The amendments to SPEC/00 made at this PR

Put to Product in `milestones/M10/rulings/pr1.md`. SPEC/00 had no M10
and said "SPEC/00 plans no M10".

- **Status line:** amended at M10 PR 1, naming the sections below.
- **§3:** a new row, "An outside caller", answered by M10.
- **§7:** row 10, claim 10, OPEN.
- **§8 preamble:** eleven milestones, at most 44 PRs; M10 opened by a
  Product ruling after M09 closed GREEN and was tagged; reopens none of
  M09's rows and repairs nothing M09 found.
- **§5:** the Tool Owner's row gains `callers` (reviewer finding 7);
  CLAUDE.md's seat table follows it.
- **§8 M10:** the entry this SPEC is written from; item 2 corrected to
  the agent's own stack (finding 8).
- **§10.3:** row 10, title "Outsiders come in by the front door"
  (finding 9: the sentence's stranger is the one turned away) and plain
  sentence.
- **§10.5:** M10 has no recording, by Product's ruling at M10 PR 1
  (ADR-0015 carries the rule; ADR-0005 has no amendment left); §15's
  video clause reads nine videos, M09's and M10's ruled not recorded,
  not moved to fit; SPEC/00 plans no M11.
- **§15:** rows 0–10, eleven explainers, nine videos, tag `m10`; the
  clauses M09's close read stay as read, and M10's close re-reads them
  over eleven rows and moves none to fit.
- **§12** is not amended at PR 1: the gateway, Identity's vault and the
  rest stay not built, and this SPEC's §12 repeats them for M10. If
  Security rules door 3 at R2, §12's "the gateway" line is amended at PR
  2 under that ruling; door 1 and door 2 touch nothing on the list.

## 11. Read before PR 2

Each is a ruling or a reading, not a grant, and each is named in
`milestones/M10/README.md` with the pull request whose merge it must
precede. Each is also an **Unsure** item in PR 1's body, with its seat.
R1 was ruled before this SPEC was written; the rest were proposed at
the same stop and go in as proposals until each seat's ruling file reads
"Ruled by".

- **R1 (Product).** The claim's wording and the plain sentence. **Ruled
  2026-10-13, before this SPEC was written:** as §1 reads them, with the
  four changes from the brief's proposal recorded in
  `milestones/M10/rulings/pr1.md` (a door the platform controls, not
  "the platform's one door"; an identity the manifest admits, not one
  "the platform issued"; each call's record, not "the answer's record";
  the bypass arm as a platform principal the construct does not name).
- **R2 (Security).** The door. Proposed: door 1 (§2), the runtime's own
  JWT authoriser on a Cognito user pool per agent in the agent's stack
  (the construct, not the bootstrap: SPEC/00 §8 M10 item 2 says so,
  corrected at this PR, reviewer finding 8), with the three unknowns
  probed by Security with throwaway names before PR 2 opens and the
  outputs committed in PR 2 as `milestones/M10/runs/door_probe.md`. If
  (c) answers no, door 2. If (a) answers no, the bootstrap's grants are
  narrowed by a runtime tag the construct sets, failing which door 2
  (finding 4). Door 3 is not proposed. **This is the item most likely to threaten the cap**,
  as R3 was at M09: a door whose refusals leave no record within N has
  no reading for F10.4, and a RED close on the record arm is the stated
  result of that.
- **R3 (Security, Product).** Who the outside caller is. Proposed: a user
  in the agent's pool for the admitted arm, named in `callers`; a user of
  a throwaway pool the owner makes for the run for the stranger arm; no
  token for the no-identity arm; the owner's laptop IAM principal for the
  bypass arm, standing for a platform principal the construct does not
  name, and never presented as outside. A principal in the security
  account (897698239547) is the fallback for the stranger arm if door 2
  is ruled, since door 2 takes IAM.
- **R4 (Tool Owner).** The manifest field. Proposed: `callers`, a list of
  `{subject, issuer}`, `additionalProperties: false`, beside
  `may_be_called_by`; not an edge (a caller is not an agent) and not a
  rule (it says who, not what may be said); `callers: []` the default and
  not a relaxation; the `platform` client admitted by the construct and
  not listed. refagent's and `ratings-helper`'s manifests gain `callers:
  []` at PR 2 under the Tool Owner's key.
- **R5 (Data Owner).** The call record's read shape. Proposed (§2):
  `subject`, `issuer`, `agent`, `outcome`, `reason`, `request_id`,
  `time`, `delivered`; no guardrail (finding 2); `build`'s `from_raw`
  maps the raw record AWS delivered onto it (finding 1), and the raw
  record stays beside it on the envelope. One raw object per call under
  `calls/agents/<name>/`, written by the door's delivery and never by
  the agent; pharmadelta's scorer reads the answer record, which is
  unchanged but for the `platform` caller the deploy's goldens run now
  presents (M09 R7's shape stands).
- **R6 (Threshold Owner).** N. Proposed: `detection.max_seconds`, 600 s,
  reused; no bar added and none moved, so no Threshold Owner diff at PR
  1 or PR 2. Read as M05 read it: the object's `LastModified` against
  AWS's `eventTime` (finding 3).
- **R7 (Product).** M09's standing items carried as housekeeping in this
  PR, each named in `rulings/pr1.md`: SPEC/06 §6's "installed on all
  repositories" corrected to "selected repositories" with the
  quickstart's step 0 saying the owner adds the repository to the
  platform App (M09 finding 3); ADR-0014's `status:` to Accepted with
  2026-10-11 (finding 14); `docs/compliance/map.md`'s M09 row and its
  stale "Claim 8 (M08): not opened" line (finding 11). `docs/story.md`
  and the M08 header rows stay standing. **Ruled 2026-10-13, yes to all
  four**, at the same stop as R1.
- **No recording (Product, ruled 2026-10-13).** M10 records no video
  (SPEC/00 §10.5 as amended; ADR-0015). Not an Unsure item.

## 12. Not in M10

- The AgentCore Gateway (door 3, not proposed); AgentCore Identity's
  credential vault; a policy engine; Cedar; per-tool or per-caller
  limits; a rate limit; a budget per caller; log-only mode (SPEC/00
  §12).
- refagent behind the door; `make evals` through a door; the swap runs
  through a door.
- Two-key on an agent repository's own pull requests (SPEC/00 §12); a
  merge stop on a bypass, an answered stranger or an unrecorded refusal
  (the result is recorded after the fact and read by row 10's cell).
- A second person as the caller (R1: one human holds every seat; the
  caller is an identity, not a person).
- A filter on tool results; the judge; the knowledge base; Braintrust;
  GuardDuty (SPEC/00 §12).
- Any change to `src/baseline/` (ADR-0002), to a bar, to a golden under
  `evals/goldens/`, or to any rule file.
- An account-per-team landing zone, an SCP (R3); the security account's
  own admin.
- A recording (SPEC/00 §10.5, ruled at this PR).
- A fifth pull request. The cap is four; a fifth would be a RED close
  with the finding as the result, and this SPEC proposes no raise.
