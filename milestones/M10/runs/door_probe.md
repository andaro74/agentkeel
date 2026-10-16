# The door probe (SPEC/10 §11 R2; §5.1 "The probe is before PR 2 opens")

Security's probe of door 1's three unknowns, run by hand on 2026-10-14 in
the platform account with throwaway names (`probe-door-*`, the runtime
`probe_door_agent`), outside the repository, and torn down on 2026-10-15
(the teardown's verification block read `GONE` on every line: the runtime,
the image repository, the two roles, the trail and its bucket, both pools,
the log groups). Nothing `agentkeel-*` was read, called or changed. The raw
outputs stayed in `~/probe-door/out/`; this file is the record PR 2 commits,
and the five data events are the raw fixture
`tests/fixtures/m10/s1-call-records/raw/data_events.json`, timestamps and
error messages byte for byte, every real id a placeholder (the table is in
`tests/fixtures/README.md`). The bypass call was made as an assumed role
(`probe-door-bypass`), never as the owner's IAM user; the owner's user
appears in the trail's management events only, and none of those is copied.

## What was built

One Cognito user pool (`probe-door-pool`) with one user, a callers client
(`USER_PASSWORD_AUTH`, no secret) and a machine client (`probe-door-platform`,
client credentials, a resource server scope `probe-door-api/invoke`); a
second pool (`probe-door-other`) with one user, the stranger; one AgentCore
runtime, `authorizerConfiguration.customJWTAuthorizer` on the first pool's
discovery URL with the two clients allowed; a role `probe-door-bypass`
holding `bedrock-agentcore:InvokeAgentRuntime` on that runtime; a trail with
a management-event selector and a data-event selector on
`AWS::BedrockAgentCore::Runtime`, delivering to a bucket of its own. Then a
third client, `probe-door-wrong`, not in `allowedClients`.

## The six calls (03-calls.py, 2026-10-14 14:21:47Z to 14:21:51Z)

| Call | How | HTTP | What the service said |
|---|---|---|---|
| admitted | the pool user's access token, bearer, on the invocations URL | 200 | the fixed reply |
| none | no `Authorization` header | 401 | `MissingAuthenticationTokenException`: "Missing Authentication Token" |
| stranger | the other pool's user's access token | 401 | `UnrecognizedClientException`: "Claim 'iss' value mismatch with configuration." |
| wrong-client | a token from the pool, from a client not in `allowedClients` | 401 | `UnrecognizedClientException`: "Claim 'client_id' value mismatch with configuration." |
| bypass | SigV4 `InvokeAgentRuntime` as the assumed role holding the grant | 403 | `AccessDeniedException`: "Authorization method mismatch. The agent is configured for a different authorization method than what was used in your request." |
| platform | the machine client's client-credentials token | 200 | the fixed reply |

## The answers, each with the file it is read from

**(a) YES.** A SigV4 call from an IAM principal holding the permission is
refused before IAM authorisation once the runtime is in JWT mode
(`call-bypass.json`; the data event `bypass` in the fixture, `errorCode:
AccessDenied`). The fallback SPEC/10 §11 R2 named for a no, the bootstrap's
grants narrowed by a runtime tag, is not needed.

**(b) PARTLY, not NO.** The brief that opened this session read the probe as
"the caller's identity is written nowhere the platform can read". The
records say less than that. The container receives an AWS-minted workload
access token and never the bearer token or its claims
(`records-logs-*`, the `PROBE-DOOR-REQUEST` lines: a `workloadaccesstoken`
header, no `Authorization` header); the runtime's log carries no claim; and
the `GetWorkloadAccessTokenForJWT` management event hides the token. But the
**data event of an admitted call carries the token's claims** under
`additionalEventData.jwt.claims`: `sub`, `iss`, `scope`, `token_use`,
`auth_time`, `exp`, `iat`, `jti` (and `version` for the machine client). It
drops `client_id` and `username`. So an admitted call's record names the
pool user's `sub` (a UUID, not the subject's name) and the pool's issuer,
and a machine-client call's record names the client id as `sub`. A refused
call's data event carries no claims at all: its `userIdentity` reads
`AWSAccount` with an empty principal and `accountId: anonymous`. The
fixture's `admitted` and `platform` events show the claims; `stranger` and
`wrong-client` show none.

**(c) PARTLY.** The stranger's and the wrong client's refusals each left a
data event (`eventTime 2026-10-14T14:21:49Z`) in an object the trail
delivered at `14:26:47Z`: 298 s after the event, under N (600 s). Each
names no caller. An `InboundAuthorizationFailure` metric
(`AWS/Bedrock-AgentCore`, `ExceptionType: UnauthorizedInboundTokenException`)
read 2 for the 14:21 minute, about 100 s after the calls
(`records-metrics-*`). **The no-token refusal left no record anywhere**: its
request id (`x-amzn-RequestId` on the 401) is in no data event, no log line
and no metric count; both reads (14:23Z and 14:43Z) agree
(`records-trail-s3-*`, `records-logs-*`, `records-metrics-*`). Event history
(`lookup-events`, management events) never shows `InvokeAgentRuntime`: a
data-event trail with a selector on `AWS::BedrockAgentCore::Runtime` is
required, and the probe's selector was accepted and delivered.

**(d)** Setting a new `allowedClients` list on a deployed runtime updates it
in place: version 1 to 2, the ARN unchanged, status `UPDATING` then `READY`
(`update.json`). Unsure H of PR 1 is answered: a redeploy with the door is
an update, not a replacement.

**(e)** The machine client's token: `POST` to the pool domain's
`/oauth2/token` with `Basic client_id:secret`, `grant_type=client_credentials`
and the resource-server scope; its `sub` is the client id, it has no
`username`, and the runtime admitted it (`call-platform.json`).

## The consequence (R2, ruled by Security at this PR)

Door 1 alone cannot meet claim 10. On the probe's own calls, F10.3 (the
caller named in each call's record) fails for the stranger's refusal, whose
record names no one, and F10.4's record arm fails for the no-token call,
which leaves nothing. The admitted call's record does name its caller, as a
`sub`; that is not enough for the two refused arms.

So R2 is **door 2 in the hybrid form**: an API Gateway in front of the
runtime with a Lambda authoriser and a small proxy Lambda. The runtime
**keeps** its JWT authoriser, so (a) stays: no SigV4 call reaches it; but
it admits **one client only**, the door's own machine client (the probe's
`platform` pattern), whose credential the proxy fetches; the agent's
callers' client is admitted by the API's authoriser alone. A caller's token
is checked against the manifest's `callers` by the authoriser; the API's
access log names the subject and the outcome, including the no-token case,
which the API refuses itself with a 401 and logs; the proxy exchanges to the
door's token and invokes the runtime; a call made straight at the runtime
(SigV4, a caller's own token, or no token) is refused by the runtime, the two
token cases recorded by the data event within N and the no-token-direct case
unrecorded, named in SPEC/10 §8. The raw record `from_raw` maps is the
access-log line; the data event is the second raw source, for the bypass
arm, and the platform account's trail has carried the runtime data-event
selector since M05 PR 2 (`infra/audit/app.py`, "AgentCore runtime
invocations"), so no trail changes.

## What the probe does not say

Whether the API's access log records a request its authoriser refused, with
the authoriser's context (the subject the stranger's token claimed), and a
request with no token at all; whether the Logs subscription reaches the
security account's bucket within N. Neither is a question door 1 could
answer, and neither is probed before PR 2: both are read at festival-desk's
deploy and PR 3's run, and SPEC/10 §7 names them as the risks first.
