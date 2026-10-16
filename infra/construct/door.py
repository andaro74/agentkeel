"""The door's two functions and its access-log line (M10 PR 2; SPEC/10 §2, §6; R2 door 2 hybrid; Security seat).

What `GovernedAgent._door` deploys for an agent whose manifest has `callers`
(`governed_agent.py`): the code of the API's Lambda authoriser and of the
proxy that calls the runtime, as inline source (the account is not
CDK-bootstrapped, so no asset bucket: each must stay under CloudFormation's
4 KiB `ZipFile` limit, which `tests/test_m10_platform.py` holds), and the
format of the access-log line the API's stage writes, which
`src/verdict/caller.from_raw` reads.

**The authoriser** admits two token shapes and refuses everything else, and
says in its context who asked and why, so the access log names the subject
and the outcome for a refusal too:

- the pool's callers client's access token whose `username` is one of the
  manifest's `callers` (the subject is the username);
- the pool's door client's client-credentials token, the deploy's own
  goldens caller, admitted as `platform` (SPEC/10 §2).

It verifies the signature itself (RS256: the JWKS of the pool's issuer, cached
across invocations, and `pow` over the modulus; no library the runtime lacks),
then `exp`, `iss`, `token_use` and `client_id`. A token the pool did not issue
is refused `not admitted` with the subject and issuer it *claimed*, unverified,
so the stranger's record names the stranger (SPEC/10 §4 F10.3). A header that
is not a token, or a token whose header or payload is not an object, is `no
identity`. What it writes into its context is clipped: a claimed subject to
the subject pattern (or a client id's shape), an issuer to a URL's charset
with a length cap, so no quote, newline or second key a stranger puts in a
token can reach the access-log line (security-reviewer F1 on PR 2). A
missing header is expected never to reach this code: API Gateway refuses it
first and logs the 401, which is read at festival-desk's deploy
(door_probe.md, "What the probe does not say").

**The proxy** exchanges to the door's own token (the door client's secret read
from Cognito with `DescribeUserPoolClient`, never stored anywhere else;
cached until expiry) and invokes the runtime over its bearer endpoint with
the caller's body, returning the runtime's answer. The runtime admits that
client only, so a call that does not come through here is refused by the
runtime whatever credential it carries (door_probe.md (a)).

Neither function logs a token, a secret or a header.
"""

from __future__ import annotations

# `$context` is API Gateway's. A value it has none of is written as "-"; from_raw reads "-" as absent.
ACCESS_LOG_FORMAT = (
    '{"source":"access-log","agent":"%s","request_id":"$context.requestId","time_epoch_ms":"$context.requestTimeEpoch",'
    '"status":"$context.status","method":"$context.httpMethod","path":"$context.routeKey","ip":"$context.identity.sourceIp",'
    '"error":"$context.error.message","auth_error":"$context.authorizer.error","subject":"$context.authorizer.subject",'
    '"issuer":"$context.authorizer.issuer","outcome":"$context.authorizer.outcome","reason":"$context.authorizer.reason",'
    '"integration_status":"$context.integration.status"}'
)

AUTHORISER_SOURCE = r'''import base64, hashlib, json, os, re, time, urllib.request
E = os.environ
ISS = "https://cognito-idp.%s.amazonaws.com/%s" % (E["REGION"], E["POOL_ID"])
CALLERS = set(E["CALLERS"].split(","))
NAME = re.compile(r"^[a-z][a-z0-9-]{2,30}$|^[a-z0-9]{10,40}$")
URL = re.compile(r"^https://[a-z0-9.\-]{3,80}/[A-Za-z0-9_\-]{1,60}$")
_jwks = {}
def clip(value, pattern):
    return value if isinstance(value, str) and pattern.match(value) else "-"
def b64(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
def jwks():
    if not _jwks:
        with urllib.request.urlopen(ISS + "/.well-known/jwks.json", timeout=5) as r:
            _jwks.update({k["kid"]: k for k in json.load(r)["keys"]})
    return _jwks
def verified(h, p, s, key):
    n, e = (int.from_bytes(b64(key[x]), "big") for x in ("n", "e"))
    k = (n.bit_length() + 7) // 8
    em = pow(int.from_bytes(b64(s), "big"), e, n).to_bytes(k, "big")
    t = bytes.fromhex("3031300d060960864801650304020105000420") + hashlib.sha256((h + "." + p).encode()).digest()
    return em == b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t
def answer(ok, subject, issuer, reason):
    return {"isAuthorized": ok, "context": {"subject": subject or "-", "issuer": issuer or "-",
            "outcome": "admitted" if ok else "refused", "reason": reason or "-"}}
def handler(event, context):
    raw = (event.get("headers") or {}).get("authorization") or event.get("identitySource", [""])[0] or ""
    token = raw.split(" ", 1)[1] if raw.lower().startswith("bearer ") else raw
    try:
        h, p, s = token.split(".")
        header, claims = json.loads(b64(h)), json.loads(b64(p))
        assert isinstance(header, dict) and isinstance(claims, dict)
    except Exception:
        return answer(False, None, None, "no identity")
    claimed = clip(claims.get("username") or claims.get("client_id") or claims.get("sub"), NAME)
    iss = clip(claims.get("iss"), URL)
    try:
        ok = header.get("alg") == "RS256" and claims.get("iss") == ISS and verified(h, p, s, jwks()[header.get("kid")])
        ok = ok and claims.get("token_use") == "access" and float(claims.get("exp", 0)) >= time.time()
    except Exception:
        ok = False
    if not ok:
        return answer(False, claimed, iss, "not admitted")
    if claims.get("client_id") == E["DOOR_CLIENT_ID"] and "username" not in claims:
        return answer(True, "platform", iss, None)
    if claims.get("client_id") == E["CALLERS_CLIENT_ID"] and claims.get("username") in CALLERS:
        return answer(True, claims["username"], iss, None)
    return answer(False, claimed, iss, "not admitted")
'''

PROXY_SOURCE = r'''import base64, json, os, time, urllib.error, urllib.parse, urllib.request, uuid
import boto3
E = os.environ
_door = {}
def door_token():
    if _door.get("exp", 0) > time.time() + 60:
        return _door["t"]
    client = boto3.client("cognito-idp", region_name=E["REGION"]).describe_user_pool_client(
        UserPoolId=E["POOL_ID"], ClientId=E["DOOR_CLIENT_ID"])["UserPoolClient"]
    basic = base64.b64encode((E["DOOR_CLIENT_ID"] + ":" + client["ClientSecret"]).encode()).decode()
    body = urllib.parse.urlencode({"grant_type": "client_credentials", "scope": E["SCOPE"]}).encode()
    q = urllib.request.Request(E["TOKEN_ENDPOINT"], data=body, headers={
        "Authorization": "Basic " + basic, "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(q, timeout=10) as r:
        got = json.load(r)
    _door.update(t=got["access_token"], exp=time.time() + int(got.get("expires_in", 3600)))
    return _door["t"]
def handler(event, context):
    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode()
    url = "https://bedrock-agentcore.%s.amazonaws.com/runtimes/%s/invocations?qualifier=DEFAULT" % (
        E["REGION"], urllib.parse.quote(E["RUNTIME_ARN"], safe=""))
    session = uuid.uuid4().hex + uuid.uuid4().hex
    q = urllib.request.Request(url, data=body.encode(), headers={
        "Authorization": "Bearer " + door_token(), "Content-Type": "application/json",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session})
    try:
        with urllib.request.urlopen(q, timeout=28) as r:
            return {"statusCode": r.status, "headers": {"Content-Type": "application/json"}, "body": r.read().decode()}
    except urllib.error.HTTPError as e:
        return {"statusCode": e.code, "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": e.read().decode()[:2000]})}
'''

ZIPFILE_LIMIT = 4096  # CloudFormation's inline code ceiling, bytes
