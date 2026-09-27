# AgentCore Gateway as an LLM gateway: probe record, 2026-09-26

**A record, not evidence** (P11). The human made these calls before M04
PR 1 opened, with their own credentials, in account 581208540944,
us-west-2, against throwaway resources named `probe-llmgw*`, all torn
down afterwards. The raw files are outside the repo, under
`~/probe-llmgw/out/` (round 1) and `~/probe-llmgw/out2/` (round 2), and
are transcribed here by M04 PR 1. No envelope reads this file, and no
gate. The human's IAM user name, which the files print, is written here
as "the human's admin user".

The question was whether an AgentCore Gateway could stand between
refagent and Bedrock as its model gateway, carrying Converse unchanged
and holding the guardrail pin as a gateway policy. The decision is M04
`feasibility.md` §6 item 39: Product, Security and Threshold Owner, at
M05 open. The probe leaned M05, not M04.

## Round 1: an inference target (`out/`)

- Gateway `probe-llmgw-oqyq4ki67j`, `authorizerType: AWS_IAM`, role
  `probe-llmgw-role` (`02-gateway.json`, `01-role.txt`). The role's policy
  allows `bedrock-mantle:CreateInference` and its reads.
- Target `KBP49A8GNU`: `targetConfiguration.inference.connector.source.connectorId:
  bedrock-mantle`, credentials `GATEWAY_IAM_ROLE` (`03-target.json`).
- The target's model list (`04-models.txt`, HTTP 200) names models as
  `bedrock-mantle/<id>`. It includes `bedrock-mantle/anthropic.claude-haiku-4-5`
  and no Sonnet 4.6.
- Three calls on `bedrock-mantle/anthropic.claude-sonnet-4-6`, for
  `g-001` with the guardrail headers and `g-016` with and without them
  (`q12-*.txt`): each **HTTP 404**, `"The model 'anthropic.claude-sonnet-4-6'
  does not exist"`, and no field naming a guardrail or a trace.
- For comparison, direct Converse on `us.anthropic.claude-sonnet-4-6`
  with guardrail `1088aw3ujhyd` (`ref-converse-*.txt`): `g-001`
  `end_turn`, no topics fired; `g-016` `guardrail_intervened`, topics
  `embargoed-synopsis` and `claimed-authority-override`.
- Teardown (`99-teardown.txt`): `GetGateway` ResourceNotFoundException;
  `GetRole probe-llmgw-role` NoSuchEntity.

**Finding (a).** An inference target, in the formats the probe tried,
cannot reach Sonnet 4.6. Sonnet 4.6 is served by `bedrock-runtime` through
Converse and InvokeModel, which that connector does not speak.

## Round 2: an HTTP passthrough target to `bedrock-runtime` (`out2/`)

- Gateway `probe-llmgw2-ce0mq3j8v1`, `AWS_IAM`, role
  `probe-llmgw2-gw-role`; a caller role `probe-llmgw2-caller`, assumed as
  `probe2` (`01-roles.txt`, `02-gateway.json`, `04-caller.txt`).
- The caller's policy (`caller-policy.json`) allows `bedrock:InvokeModel`
  on refagent's profile and its three foundation-model ARNs only with
  `bedrock:GuardrailIdentifier` equal to `guardrail/1088aw3ujhyd:5`, the
  model only through the profile, `ApplyGuardrail` on that guardrail, and
  `InvokeGateway` on the probe's gateway.
- Direct, as the caller: `g-001` with the guardrail answered, `end_turn`
  (`D1`); `g-001` without it refused, `AccessDeniedException`, "no
  identity-based policy allows the bedrock:InvokeModel action" (`D2`).

**Target A, `CALLER_IAM_CREDENTIALS`** (`03-target.json`, target
`Y60IPL3ZZN`, passthrough to `https://bedrock-runtime.us-west-2.amazonaws.com`,
`protocolType: INFERENCE`). Four calls to
`/bedrock/model/us.anthropic.claude-sonnet-4-6/converse`: as the caller,
`g-016` and `g-001` with the guardrail and `g-001` without (`P1` to `P3`);
as the human's admin user, `g-001` without (`P4`). Each **HTTP 403**,
`UnrecognizedClientException`, "The security token included in the
request is invalid". A call to a target name that does not exist
answered 404 "No Target found" (`05-inbound-check.txt`), so the
gateway's inbound IAM check passed and the refusal is the forwarded
call's.

**Finding (c).** `CALLER_IAM_CREDENTIALS` fails against
`bedrock-runtime`: 403, invalid security token, for the caller and for
the admin alike.

**Target B, `GATEWAY_IAM_ROLE`** (`06-target-b.json`, target
`UTKGXRCAFY`, the same passthrough). Three calls as the caller:

- `g-016` with the guardrail (`B1`): **HTTP 200**, `guardrail_intervened`,
  topics `embargoed-synopsis` and `claimed-authority-override`, the same
  as direct Converse;
- `g-001` with the guardrail (`B2`): **HTTP 200**, `end_turn`, no topics;
- `g-001` without the guardrail (`B3`): **HTTP 403**,
  `AccessDeniedException`, and the principal refused is
  `assumed-role/probe-llmgw2-gw-role/gateway-session-…`, **the gateway's
  role, not the caller's**.

**Finding (b).** A passthrough target to `bedrock-runtime`, signed as the
gateway's role, carries Converse unchanged: the guardrail's trace and
topics come back as they do directly, and a call without the guardrail
is refused. The refusal is on the gateway's role, so the pin is held in
one place for every caller, and CloudTrail names the gateway, not the
agent. The policy the gateway's role held for target B is not among the
probe's files: `gw2-role-policy.json` as saved grants only
`InvokeGateway`. What the record shows is the refusal naming that role,
not the statement that made it.

## The endpoint

`q3-endpoint.txt`: the VPC endpoint service
`com.amazonaws.us-west-2.bedrock-agentcore.gateway` exists (Interface,
`*.gateway.bedrock-agentcore.us-west-2.amazonaws.com`).

**Finding (d).** A gateway could be reached from the platform VPC
through an interface endpoint, as `bedrock-runtime` is today.

## Also in the folder, not read by any call above

`deny-without-guardrail.json`: a deny on `bedrock-mantle:*`,
`bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` unless
the guardrail identifier names `1088aw3ujhyd`. The files do not record
which role it was attached to, or whether any call ran under it.

## Teardown

`out2/99-teardown.txt`: `GetGateway` ResourceNotFoundException;
`GetRole` NoSuchEntity for `probe-llmgw2-caller` and
`probe-llmgw2-gw-role`. With round 1's, every probe resource the files
name is gone.
