"""M10 PR 2's door, read from the construct's own template (SPEC/10 §2, §6; R2 door 2 hybrid).

The fixture agent with callers (`tests/fixtures/m10/s4-festival-desk-door/`, M09's agent with two subjects
added) synthesised through the construct: the pool with one user per subject, a callers client and the door
client; the runtime's authoriser admitting the door client only; the HTTP API with its Lambda authoriser, its
proxy and its access log, subscribed to the security account's destination; every role under the agent boundary;
the bootstrap's execution role able to make each resource type the door adds, with the deploy boundary denying
none of it. And the door's two functions, run here as Python with a key made for the test: the authoriser admits
the callers client's token for a listed subject and the door client's token as `platform`, refuses a stranger's
pool, a wrong client, an unlisted subject, a bad signature and an expired token, each with the subject it claimed;
the proxy exchanges to the door's token and invokes the runtime's bearer endpoint, copying the body and no header.
Nothing here calls AWS.
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
from pathlib import Path
from typing import Any

import pytest

from infra.construct import door

from .test_bootstrap import actions, denies_by_pattern, named, of_type, statements
from .test_bootstrap import template as bootstrap_template  # noqa: F401  (the fixture, by its name)
from .test_m09_platform import synth, the_one

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "m10" / "s4-festival-desk-door"
SUBJECTS = ["lantern-desk", "box-office"]
DESTINATION = "arn:aws:logs:us-west-2:897698239547:destination:agentkeel-calls"

# What CloudFormation's handlers call for the door's resource types (describe-type, read 2026-10-15), held against
# the execution role's grants as test_bootstrap.NEEDED_BY_TYPE holds the construct's other types.
DOOR_NEEDED_BY_TYPE = {
    "AWS::Cognito::UserPool": {"cognito-idp:CreateUserPool", "cognito-idp:DescribeUserPool", "cognito-idp:UpdateUserPool",
                               "cognito-idp:DeleteUserPool", "cognito-idp:TagResource", "cognito-idp:UntagResource",
                               "cognito-idp:ListTagsForResource", "cognito-idp:GetUserPoolMfaConfig", "cognito-idp:SetUserPoolMfaConfig"},
    "AWS::Cognito::UserPoolUser": {"cognito-idp:AdminCreateUser", "cognito-idp:AdminGetUser", "cognito-idp:AdminDeleteUser"},
    "AWS::Cognito::UserPoolClient": {"cognito-idp:CreateUserPoolClient", "cognito-idp:DescribeUserPoolClient",
                                     "cognito-idp:UpdateUserPoolClient", "cognito-idp:DeleteUserPoolClient"},
    "AWS::Cognito::UserPoolResourceServer": {"cognito-idp:CreateResourceServer", "cognito-idp:DescribeResourceServer",
                                             "cognito-idp:UpdateResourceServer", "cognito-idp:DeleteResourceServer"},
    "AWS::Cognito::UserPoolDomain": {"cognito-idp:CreateUserPoolDomain", "cognito-idp:DescribeUserPoolDomain",
                                     "cognito-idp:UpdateUserPoolDomain", "cognito-idp:DeleteUserPoolDomain"},
    "AWS::Lambda::Function": {"lambda:CreateFunction", "lambda:GetFunction", "lambda:UpdateFunctionCode",
                              "lambda:UpdateFunctionConfiguration", "lambda:DeleteFunction", "lambda:TagResource",
                              "lambda:UntagResource", "lambda:ListTags", "iam:PassRole"},
    "AWS::Lambda::Permission": {"lambda:AddPermission", "lambda:RemovePermission", "lambda:GetPolicy"},
    "AWS::ApiGatewayV2::Api": {"apigateway:POST", "apigateway:GET", "apigateway:PATCH", "apigateway:DELETE"},
    "AWS::ApiGatewayV2::Authorizer": {"apigateway:POST", "apigateway:GET", "apigateway:PATCH", "apigateway:DELETE"},
    "AWS::ApiGatewayV2::Integration": {"apigateway:POST", "apigateway:GET", "apigateway:PATCH", "apigateway:DELETE"},
    "AWS::ApiGatewayV2::Route": {"apigateway:POST", "apigateway:GET", "apigateway:PATCH", "apigateway:DELETE"},
    # M10 PR 3 (run 39052047504): a stage with access logging needs vended log delivery from its creator.
    "AWS::ApiGatewayV2::Stage": {"apigateway:POST", "apigateway:GET", "apigateway:PATCH", "apigateway:DELETE",
                                 "logs:CreateLogDelivery", "logs:GetLogDelivery", "logs:UpdateLogDelivery",
                                 "logs:ListLogDeliveries", "logs:PutResourcePolicy", "logs:DescribeResourcePolicies"},
    # No logs:Delete*: the deploy boundary denies them flat, so these four are retained and never deleted by a stack.
    "AWS::Logs::LogGroup": {"logs:CreateLogGroup", "logs:PutRetentionPolicy",
                            "logs:DescribeLogGroups", "logs:TagResource", "logs:UntagResource", "logs:ListTagsForResource"},
    "AWS::Logs::SubscriptionFilter": {"logs:PutSubscriptionFilter", "logs:DescribeSubscriptionFilters"},
}  # fmt: skip

# M10 PR 3, from festival-desk's first door deploy (run 38997315544, 2026-10-17T03:05Z): an action that takes no
# resource-level permission is granted on * or not at all, and a cross-account subscription is authorised against the
# destination's ARN as well as the log group's. PR 2 held neither, and the test above read the action names only.
ON_STAR_ONLY = {"logs:DescribeLogGroups", "cognito-idp:CreateUserPool", "logs:CreateLogDelivery", "logs:GetLogDelivery",
                "logs:UpdateLogDelivery", "logs:ListLogDeliveries", "logs:PutResourcePolicy", "logs:DescribeResourcePolicies"}
CALLS_DESTINATION = "arn:aws:logs:us-west-2:897698239547:destination:agentkeel-calls"


def synth_refagent(out: Path) -> dict[str, Any]:
    """refagent's own stack (AgentkeelRefagent), as deploy.yml synthesises it with no AGENTKEEL_BUNDLE."""
    import os
    import subprocess
    import sys

    done = subprocess.run([sys.executable, str(ROOT / "infra" / "construct" / "app.py")], cwd=ROOT, capture_output=True,
                          text=True, check=False, env={**os.environ, "PYTHONPATH": str(ROOT), "CDK_OUTDIR": str(out)})  # fmt: skip
    assert done.returncode == 0, done.stderr
    return json.loads((out / "AgentkeelRefagent.template.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def door_template(tmp_path_factory) -> dict[str, Any]:
    code, said, template = synth(FIXTURE.relative_to(ROOT), tmp_path_factory.mktemp("festival-desk-door"))
    assert code == 0, said
    return template


def props(template: dict[str, Any], kind: str) -> dict[str, dict[str, Any]]:
    return {logical: r["Properties"] for logical, r in of_type(template, kind).items()}


# --- the door's shape -------------------------------------------------------------------------------


def test_the_pool_has_one_user_per_subject_a_callers_client_and_the_door_client(door_template):
    pool_id, pool = the_one(door_template, "AWS::Cognito::UserPool")
    assert pool["UserPoolName"] == "agentkeel-festival-desk" and pool["MfaConfiguration"] == "OFF"
    assert pool["AdminCreateUserConfig"] == {"AllowAdminCreateUserOnly": True}
    assert pool["Policies"]["PasswordPolicy"]["MinimumLength"] == 12
    assert pool["UserPoolTags"] == {"agentkeel:agent": "festival-desk"}
    (resource,) = of_type(door_template, "AWS::Cognito::UserPool").values()
    assert resource.get("DeletionPolicy") == "RetainExceptOnCreate"
    users = props(door_template, "AWS::Cognito::UserPoolUser")
    assert sorted(u["Username"] for u in users.values()) == sorted(SUBJECTS)
    assert all(u["MessageAction"] == "SUPPRESS" and u["UserPoolId"] == {"Ref": pool_id} for u in users.values())
    clients = {c["ClientName"]: c for c in props(door_template, "AWS::Cognito::UserPoolClient").values()}
    assert set(clients) == {"callers", "door"}
    assert clients["callers"]["GenerateSecret"] is False
    assert clients["callers"]["ExplicitAuthFlows"] == ["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]
    assert clients["door"]["GenerateSecret"] is True and clients["door"]["AllowedOAuthFlows"] == ["client_credentials"]
    assert clients["door"]["AllowedOAuthScopes"] == ["agentkeel-festival-desk/invoke"]
    _, server = the_one(door_template, "AWS::Cognito::UserPoolResourceServer")
    assert server["Identifier"] == "agentkeel-festival-desk" and server["Scopes"][0]["ScopeName"] == "invoke"
    _, domain = the_one(door_template, "AWS::Cognito::UserPoolDomain")
    assert domain["Domain"] == {"Fn::Join": ["", ["agentkeel-festival-desk-", {"Ref": "AWS::AccountId"}]]}


def test_the_pool_and_its_users_are_retained_except_by_the_operation_that_made_them_and_the_log_groups_always(door_template):
    """M10 PR 3: 55 orphan pools from failed first deploys (2026-10-16, 17). The log groups stay Retain: the deploy
    boundary denies the delete a rollback would need, so a failed first door deploy is cleaned by hand."""
    for kind in ("AWS::Cognito::UserPool", "AWS::Cognito::UserPoolUser"):
        for logical, resource in of_type(door_template, kind).items():
            assert resource.get("DeletionPolicy") == "RetainExceptOnCreate", (logical, resource.get("DeletionPolicy"))
    for kind in ("AWS::Logs::LogGroup", "AWS::Logs::SubscriptionFilter"):
        for logical, resource in of_type(door_template, kind).items():
            assert resource.get("DeletionPolicy") == "Retain", (logical, resource.get("DeletionPolicy"))


def test_the_runtime_admits_the_door_client_only_and_the_invoke_is_still_conditioned_on_the_guardrail(door_template):
    """door_probe.md (a): in JWT mode a SigV4 call is refused whatever grant it holds; with the door client alone
    admitted, so is a caller's own token. The guardrail condition is M09's, untouched (F10.2)."""
    _, runtime = the_one(door_template, "AWS::BedrockAgentCore::Runtime")
    door_client = next(logical for logical, c in props(door_template, "AWS::Cognito::UserPoolClient").items()
                       if c["ClientName"] == "door")  # fmt: skip
    pool_id, _ = the_one(door_template, "AWS::Cognito::UserPool")
    authoriser = runtime["AuthorizerConfiguration"]["CustomJWTAuthorizer"]
    assert authoriser["AllowedClients"] == [{"Ref": door_client}]
    assert authoriser["DiscoveryUrl"] == {"Fn::Join": ["", ["https://cognito-idp.us-west-2.amazonaws.com/", {"Ref": pool_id},
                                                           "/.well-known/openid-configuration"]]}  # fmt: skip
    assert "AllowedAudience" not in authoriser
    guardrail, _ = the_one(door_template, "AWS::Bedrock::Guardrail")
    version, _ = the_one(door_template, "AWS::Bedrock::GuardrailVersion")
    invokes = [s for policy in of_type(door_template, "AWS::IAM::Policy").values()
               for s in policy["Properties"]["PolicyDocument"]["Statement"]
               if s["Effect"] == "Allow" and "bedrock:InvokeModel" in actions(s)]  # fmt: skip
    assert len(invokes) == 2
    for statement in invokes:
        assert statement["Condition"]["StringEquals"]["bedrock:GuardrailIdentifier"] == {
            "Fn::Join": ["", [{"Fn::GetAtt": [guardrail, "GuardrailArn"]}, ":", {"Fn::GetAtt": [version, "Version"]}]]}


def test_the_api_has_the_authoriser_on_its_one_route_the_proxy_behind_it_and_an_access_log_subscribed_to_the_security_account(door_template):
    _, api = the_one(door_template, "AWS::ApiGatewayV2::Api")
    assert api["ProtocolType"] == "HTTP" and api["Name"] == "agentkeel-festival-desk-door"
    _, authoriser = the_one(door_template, "AWS::ApiGatewayV2::Authorizer")
    assert authoriser["AuthorizerType"] == "REQUEST" and authoriser["EnableSimpleResponses"] is True
    assert authoriser["IdentitySource"] == ["$request.header.Authorization"] and authoriser["AuthorizerResultTtlInSeconds"] == 0
    _, route = the_one(door_template, "AWS::ApiGatewayV2::Route")
    assert route["RouteKey"] == "POST /invocations" and route["AuthorizationType"] == "CUSTOM" and "AuthorizerId" in route
    _, integration = the_one(door_template, "AWS::ApiGatewayV2::Integration")
    assert integration["IntegrationType"] == "AWS_PROXY" and integration["TimeoutInMillis"] == 29000
    _, stage = the_one(door_template, "AWS::ApiGatewayV2::Stage")
    assert stage["StageName"] == "$default" and stage["AutoDeploy"] is True
    assert stage["AccessLogSettings"]["Format"] == door.ACCESS_LOG_FORMAT % "festival-desk"
    log_groups = {g["LogGroupName"]: g for g in props(door_template, "AWS::Logs::LogGroup").values()}
    assert set(log_groups) == {"/agentkeel/doors/festival-desk/access", "/aws/lambda/agentkeel-festival-desk-door-authoriser",
                               "/aws/lambda/agentkeel-festival-desk-door-proxy"}  # fmt: skip
    assert all(g["RetentionInDays"] == 30 for g in log_groups.values())
    _, subscription = the_one(door_template, "AWS::Logs::SubscriptionFilter")
    assert subscription["DestinationArn"] == DESTINATION and subscription["FilterPattern"] == "" and "RoleArn" not in subscription
    for kind in ("AWS::Logs::LogGroup", "AWS::Logs::SubscriptionFilter"):
        for resource in of_type(door_template, kind).values():
            assert resource.get("DeletionPolicy") == "Retain", kind  # the deploy boundary denies logs:Delete*
    functions = {f["FunctionName"]: f for f in props(door_template, "AWS::Lambda::Function").values()}
    assert set(functions) == {"agentkeel-festival-desk-door-authoriser", "agentkeel-festival-desk-door-proxy"}
    for function in functions.values():
        assert function["Runtime"] == "python3.14" and "VpcConfig" not in function
        assert len(function["Code"]["ZipFile"].encode("utf-8")) <= door.ZIPFILE_LIMIT
    env = functions["agentkeel-festival-desk-door-authoriser"]["Environment"]["Variables"]
    assert env["CALLERS"] == "lantern-desk,box-office" and "DOOR_CLIENT_ID" in env and "CALLERS_CLIENT_ID" in env
    proxy_env = functions["agentkeel-festival-desk-door-proxy"]["Environment"]["Variables"]
    assert proxy_env["SCOPE"] == "agentkeel-festival-desk/invoke" and "RUNTIME_ARN" in proxy_env and "TOKEN_ENDPOINT" in proxy_env
    assert not any(k.lower().endswith("secret") for k in proxy_env)
    permissions = props(door_template, "AWS::Lambda::Permission")
    assert len(permissions) == 2 and all(p["Principal"] == "apigateway.amazonaws.com" and "SourceArn" in p for p in permissions.values())


def test_every_role_the_door_adds_is_under_the_agent_path_with_the_boundary_and_reads_only_its_own(door_template):
    boundary_param = [logical for logical, parameter in door_template.get("Parameters", {}).items()
                      if parameter.get("Default") == "/agentkeel/security/boundary-arn"]  # fmt: skip
    roles = of_type(door_template, "AWS::IAM::Role")
    assert len(roles) == 3
    for role in roles.values():
        assert role["Properties"]["PermissionsBoundary"] == {"Ref": boundary_param[0]}
        assert role["Properties"]["Path"] == "/agentkeel/agents/"
    pool_id, _ = the_one(door_template, "AWS::Cognito::UserPool")
    policies = {logical: p["Properties"]["PolicyDocument"]["Statement"] for logical, p in of_type(door_template, "AWS::IAM::Policy").items()}
    proxy = next(s for logical, s in policies.items() if "DoorProxyRole" in logical)
    assert [s["Sid"] for s in proxy] == ["ItsOwnLogStreams", "ReadTheDoorClientsSecret"]
    assert proxy[1]["Action"] == "cognito-idp:DescribeUserPoolClient" and proxy[1]["Resource"] == {"Fn::GetAtt": [pool_id, "Arn"]}
    authoriser = next(s for logical, s in policies.items() if "DoorAuthoriserRole" in logical)
    assert [s["Sid"] for s in authoriser] == ["ItsOwnLogStreams"]
    # the door's roles hold no InvokeAgentRuntime: the proxy carries the door client's token, not SigV4
    assert not any("bedrock-agentcore:InvokeAgentRuntime" in actions(s) for ss in policies.values() for s in ss)


def test_an_agent_without_callers_gets_no_door_and_no_authoriser(tmp_path):
    """refagent's stack, and the M09 fixture's (no callers key): the runtime keeps IAM authorisation (SPEC/10 §8)."""
    code, said, template = synth(Path("tests/fixtures/m09/s1-festival-desk"), tmp_path / "m09")
    assert code == 0, said
    _, runtime = the_one(template, "AWS::BedrockAgentCore::Runtime")
    assert "AuthorizerConfiguration" not in runtime
    assert not of_type(template, "AWS::Cognito::UserPool") and not of_type(template, "AWS::ApiGatewayV2::Api")
    refagent = synth_refagent(tmp_path / "refagent")
    _, runtime = the_one(refagent, "AWS::BedrockAgentCore::Runtime")
    assert "AuthorizerConfiguration" not in runtime and not of_type(refagent, "AWS::Cognito::UserPool")


def test_refagent_with_a_caller_is_refused_at_synth(tmp_path):
    from infra.construct import synth_refusal

    bundle = tmp_path / "agents" / "refagent"
    bundle.mkdir(parents=True)
    text = (ROOT / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8").replace("\r\n", "\n")
    (bundle / "manifest.yaml").write_text(text.replace("callers: []\n", "callers:\n  - subject: lantern-desk\n    issuer: self\n"),
                                          encoding="utf-8")  # fmt: skip
    app = tmp_path / "app.py"
    app.write_text("\n".join([
        "import sys", f"sys.path.insert(0, {str(ROOT)!r})", "import aws_cdk as cdk",
        "from infra.construct.governed_agent import GovernedAgent, ROOT as CONSTRUCT_ROOT",
        "import infra.construct.governed_agent as g", f"g.ROOT = __import__('pathlib').Path({str(tmp_path)!r})",
        "app = cdk.App()", "stack = cdk.Stack(app, 'S', env=cdk.Environment(region='us-west-2'))",
        "GovernedAgent(stack, 'R', bundle='agents/refagent')", "app.synth()", ""]), encoding="utf-8")
    refusal = synth_refusal(app)
    assert refusal is not None and "not behind a door at M10" in refusal


# --- the execution role may make the door, and the deploy boundary denies none of it -------------------------


def execution_role_policies(bootstrap_template: dict[str, Any]) -> list[dict[str, Any]]:
    """The execution role's inline default policy and its managed DoorGrants (M10 PR 3: a managed policy, since IAM
    holds a role's inline policies to 10,240 characters in all; `test_bootstrap.test_every_role_fits_iams_policy_quotas`)."""
    return [policy for kind in ("AWS::IAM::Policy", "AWS::IAM::ManagedPolicy")
            for policy in of_type(bootstrap_template, kind).values()
            if "ExecutionRole" in json.dumps(policy["Properties"].get("Roles", []))]  # fmt: skip


def test_the_execution_role_may_make_each_resource_type_the_door_adds(bootstrap_template, door_template):
    granted = {a for policy in execution_role_policies(bootstrap_template)
               for s in policy["Properties"]["PolicyDocument"]["Statement"] if s["Effect"] == "Allow" for a in actions(s)}  # fmt: skip
    flat = {a for s in statements(named(bootstrap_template, "agentkeel-deploy-boundary"), "Deny")
            if not s.get("Condition") and s["Resource"] == "*" for a in actions(s)}  # fmt: skip
    rendered = {r["Type"] for r in door_template["Resources"].values()}
    assert set(DOOR_NEEDED_BY_TYPE) <= rendered, sorted(set(DOOR_NEEDED_BY_TYPE) - rendered)
    for kind, needs in DOOR_NEEDED_BY_TYPE.items():
        assert needs <= granted, (kind, sorted(needs - granted))
        assert not [a for a in needs if denies_by_pattern(flat, a)], kind
    # PassRole to Lambda is on the agent path and held to the service, as the pass to AgentCore is
    passes = [s for policy in execution_role_policies(bootstrap_template)
              for s in policy["Properties"]["PolicyDocument"]["Statement"] if "iam:PassRole" in actions(s)]  # fmt: skip
    assert {s["Condition"]["StringEquals"]["iam:PassedToService"] for s in passes} == {"bedrock-agentcore.amazonaws.com", "lambda.amazonaws.com"}
    assert all("role/agentkeel/agents/" in json.dumps(s["Resource"]) for s in passes)


def granted_on(bootstrap_template: dict[str, Any], action: str) -> set[str]:
    """The resources the execution role holds this action on, as the template writes them."""
    found: set[str] = set()
    for policy in execution_role_policies(bootstrap_template):
        for s in policy["Properties"]["PolicyDocument"]["Statement"]:
            if s["Effect"] == "Allow" and action in actions(s):
                resource = s["Resource"]
                found |= {json.dumps(r) for r in (resource if isinstance(resource, list) else [resource])}
    return found


def test_an_action_that_takes_no_resource_is_granted_on_star_and_the_subscription_reaches_the_destination(bootstrap_template):
    for action in ON_STAR_ONLY:
        assert json.dumps("*") in granted_on(bootstrap_template, action), action
    on = granted_on(bootstrap_template, "logs:PutSubscriptionFilter")
    assert any(CALLS_DESTINATION in r for r in on), on
    assert any("log-group:/agentkeel/doors/*" in r for r in on), on


def test_the_doors_grants_are_a_managed_policy_on_the_execution_role_and_nothing_of_the_door_is_inline(bootstrap_template):
    """M10 PR 3: the bootstrap deploy of 2026-10-16 was refused with DoorGrants inline ("Maximum policy size of 10240
    bytes exceeded for role agentkeel-cfn-exec"). The door's grants are the one managed policy, attached to the
    execution role alone, carrying PR 2's six statements and PR 3's two; the role's inline policy names no door action."""
    door = named(bootstrap_template, "agentkeel-cfn-exec-door")
    assert [list(r.values())[0] for r in door["Roles"]] == [next(l for l in of_type(bootstrap_template, "AWS::IAM::Role") if l.startswith("ExecutionRole"))]
    assert [s["Sid"] for s in door["PolicyDocument"]["Statement"]] == [
        "PassADoorRoleToLambdaOnly", "MakeAnAgentsPoolOnlyWithItsTag", "ManageAnAgentsPoolItsUsersClientsServerAndDomain",
        "MakeADoorFunctionOnly", "MakeADoorApiOnly", "MakeTheDoorsLogGroupsAndItsSubscriptionOnly",
        "ListLogGroupsWhichTakesNoResource", "LetTheDoorsStageDeliverItsAccessLog",
        "SubscribeToTheSecurityAccountsCallsDestinationOnly"]  # fmt: skip
    inline = {a for policy in of_type(bootstrap_template, "AWS::IAM::Policy").values()
              if "ExecutionRole" in json.dumps(policy["Properties"]["Roles"])
              for s in policy["Properties"]["PolicyDocument"]["Statement"] for a in actions(s)}  # fmt: skip
    assert not {a for a in inline if a.startswith(("cognito-idp:", "lambda:", "apigateway:", "logs:"))}


def test_the_deploy_role_reads_a_door_clients_secret_on_a_tagged_pool_and_the_agent_ceiling_allows_the_proxys_read(bootstrap_template):
    deploy = [s for policy in of_type(bootstrap_template, "AWS::IAM::Policy").values()
              if "DeployRole" in json.dumps(policy["Properties"]["Roles"])
              for s in policy["Properties"]["PolicyDocument"]["Statement"] if "cognito-idp:DescribeUserPoolClient" in actions(s)]  # fmt: skip
    assert len(deploy) == 1 and deploy[0]["Condition"] == {"Null": {"aws:ResourceTag/agentkeel:agent": "false"}}
    assert actions(deploy[0]) == {"cognito-idp:DescribeUserPoolClient"}
    ceiling = {a for s in statements(named(bootstrap_template, "agentkeel-boundary"), "Allow") for a in actions(s)}
    assert "cognito-idp:DescribeUserPoolClient" in ceiling
    assert not any(a.startswith("cognito-idp:") and a != "cognito-idp:DescribeUserPoolClient" for a in ceiling)
    assert not any(a.startswith(("secretsmanager:", "ssm:GetParameter")) for a in ceiling)


# --- the door's code, run here (SPEC/10 §2: who is admitted, who is refused, and how each is named) -------------

# A 2048-bit RSA key made for this test and nothing else (a throwaway; its private exponent is here so the test
# can sign). The authoriser verifies RS256 with the public half as a JWKS entry.
KEY = {
    "n": "oq8E5X5Z40U7tQXswFuilTW6R29pdO9qBsPoQVtgMW7Q8INh3ooM9XfpK52iHpWeet4oX6-ql5O0VW3Ibd7Y1AzlhWMeeGQ0w1MzuAi61-NnlyfWG1dqObERFa4ezz_PIo8siPlPehLWOOEDBmT0hkfttG6uHiqIUr7jAtjv0tMQAXMzBknAwTmi8CkO3NXCN0pZov8eHNAh1MhpT96szNZzwHglJs9BdSD52M9VPWxBIL454Rn_f1RKnTS6EB1Ig05QIFzdnxV7r08ezuuDTcXUVzrdfEypIargQHRiLDlhRbLHP10BMvrf_A-8m2Zq1c7oExo53XL20DihF1On-Q",
    "e": "AQAB",
    "d": "VNA4Fkk8JZ93lFWla1eauH2NQybTbPJQbXx_PmucB8mFRo7IXFPOk77TIjkJRzarq9TcaZ5UqreHoa4deyJeGpcqpdLaFNvxIg_je8OZXWoiHIzZM-Hr8G3ewVXInDXhEFxiVHrds3_UjUzJ3fCOBt_DDnlRb0qvTaxU_6wHw_oOpKghND4KR9oLbW6u_0feA51L4l4PHe2SMNtbixWzCemBeYVJ7YerhL-AAvFWIFCXHT8xxKDP7CZlvcu6yD6qvitfiq49RfQqQJX4JxtBXUbSCKEHp6CfITzC5Y2iN5O-uf6NvqZG27c4q90BwWap6M0AN8bkrHns2aAjbWFWMQ",
}
REGION, POOL, OTHER_POOL = "us-west-2", "us-west-2_f1xture0", "us-west-2_0ther000"
ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{POOL}"
CALLERS_CLIENT, DOOR_CLIENT, WRONG_CLIENT = "ca11ersc1ient", "d00rc1ient", "wr0ngc1ient"
ENV = {"REGION": REGION, "POOL_ID": POOL, "CALLERS_CLIENT_ID": CALLERS_CLIENT, "DOOR_CLIENT_ID": DOOR_CLIENT,
       "CALLERS": ",".join(SUBJECTS), "TOKEN_ENDPOINT": "https://agentkeel-festival-desk-000000000000.auth.us-west-2.amazoncognito.com/oauth2/token",
       "SCOPE": "agentkeel-festival-desk/invoke",
       "RUNTIME_ARN": "arn:aws:bedrock-agentcore:us-west-2:000000000000:runtime/agentkeel_festival_desk-f1xture"}  # fmt: skip


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64int(value: str) -> int:
    return int.from_bytes(base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)), "big")


def sign(claims: dict[str, Any], kid: str = "k1", key: dict[str, str] = KEY, alg: str = "RS256") -> str:
    header = b64url(json.dumps({"alg": alg, "kid": kid}).encode())
    payload = b64url(json.dumps(claims).encode())
    n, d = b64int(key["n"]), b64int(key["d"])
    k = (n.bit_length() + 7) // 8
    digest = hashlib.sha256(f"{header}.{payload}".encode()).digest()
    t = bytes.fromhex("3031300d060960864801650304020105000420") + digest
    em = b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t
    signature = pow(int.from_bytes(em, "big"), d, n).to_bytes(k, "big")
    return f"{header}.{payload}.{b64url(signature)}"


def claims(**override: Any) -> dict[str, Any]:
    base = {"sub": "00000000-0000-4000-8000-00000000a0a1", "iss": ISSUER, "client_id": CALLERS_CLIENT, "token_use": "access",
            "scope": "aws.cognito.signin.user.admin", "exp": int(time.time()) + 600, "iat": int(time.time()), "username": "lantern-desk"}
    return {**base, **override}


def load(source: str, environ: dict[str, str], monkeypatch, jwks: dict[str, Any] | None = None, boto: Any = None,
         http: Any = None) -> dict[str, Any]:
    """The inline source as a module, with os.environ, urllib and boto3 standing in."""
    import io
    import types
    import urllib.request

    monkeypatch.setattr("os.environ", {**environ})

    class Response(io.BytesIO):
        status = 200

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *exc: Any) -> None:
            pass

    def urlopen(request: Any, timeout: float = 0) -> Response:
        url = request if isinstance(request, str) else request.full_url
        if url.endswith("/.well-known/jwks.json"):
            return Response(json.dumps(jwks or {"keys": [{"kid": "k1", "kty": "RSA", "n": KEY["n"], "e": KEY["e"]}]}).encode())
        assert http is not None, url
        return http(request)

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    if boto is not None:
        monkeypatch.setitem(__import__("sys").modules, "boto3", types.SimpleNamespace(client=lambda *a, **k: boto))
    namespace: dict[str, Any] = {}
    exec(compile(source, "<door>", "exec"), namespace)  # noqa: S102 - the door's own source, under test
    return namespace


def authorise(monkeypatch, token: str | None, **kwargs: Any) -> dict[str, Any]:
    module = load(door.AUTHORISER_SOURCE, ENV, monkeypatch, **kwargs)
    headers = {"authorization": f"Bearer {token}"} if token is not None else {}
    return module["handler"]({"headers": headers, "identitySource": [headers.get("authorization", "")]}, None)


def test_the_authoriser_admits_a_listed_subject_and_the_door_client_as_platform(monkeypatch):
    admitted = authorise(monkeypatch, sign(claims()))
    assert admitted == {"isAuthorized": True, "context": {"subject": "lantern-desk", "issuer": ISSUER, "outcome": "admitted", "reason": "-"}}
    platform = authorise(monkeypatch, sign({"sub": DOOR_CLIENT, "iss": ISSUER, "client_id": DOOR_CLIENT, "token_use": "access",
                                            "scope": "agentkeel-festival-desk/invoke", "exp": int(time.time()) + 600, "version": 2}))  # fmt: skip
    assert platform["isAuthorized"] is True and platform["context"]["subject"] == "platform"


def test_the_authoriser_refuses_a_strangers_pool_a_wrong_client_an_unlisted_subject_a_bad_signature_and_an_expired_token(monkeypatch):
    stranger = authorise(monkeypatch, sign(claims(iss=f"https://cognito-idp.{REGION}.amazonaws.com/{OTHER_POOL}", username="stranger")))
    assert stranger == {"isAuthorized": False, "context": {"subject": "stranger", "issuer": f"https://cognito-idp.{REGION}.amazonaws.com/{OTHER_POOL}",
                                                           "outcome": "refused", "reason": "not admitted"}}  # fmt: skip
    wrong_client = authorise(monkeypatch, sign(claims(client_id=WRONG_CLIENT)))
    assert wrong_client["isAuthorized"] is False and wrong_client["context"]["subject"] == "lantern-desk"
    unlisted = authorise(monkeypatch, sign(claims(username="usher")))
    assert unlisted["isAuthorized"] is False and unlisted["context"] == {"subject": "usher", "issuer": ISSUER, "outcome": "refused", "reason": "not admitted"}
    forged = sign(claims(username="box-office"))
    forged = forged[:-6] + ("AAAAAA" if not forged.endswith("AAAAAA") else "BBBBBB")
    assert authorise(monkeypatch, forged)["isAuthorized"] is False
    expired = authorise(monkeypatch, sign(claims(exp=int(time.time()) - 5)))
    assert expired["isAuthorized"] is False and expired["context"]["reason"] == "not admitted"
    id_token = authorise(monkeypatch, sign(claims(token_use="id")))
    assert id_token["isAuthorized"] is False
    # a door-client token that also carries a username is nobody's: not the platform, not a listed user
    assert authorise(monkeypatch, sign(claims(client_id=DOOR_CLIENT)))["isAuthorized"] is False
    unknown_key = authorise(monkeypatch, sign(claims(), kid="k9"))
    assert unknown_key["isAuthorized"] is False


def test_the_authoriser_reads_a_header_that_is_not_a_token_as_no_identity(monkeypatch):
    for raw in ("not-a-token", "Bearer x.y", "Bearer", ""):
        module = load(door.AUTHORISER_SOURCE, ENV, monkeypatch)
        out = module["handler"]({"headers": {"authorization": raw}, "identitySource": [raw]}, None)
        assert out == {"isAuthorized": False, "context": {"subject": "-", "issuer": "-", "outcome": "refused", "reason": "no identity"}}, raw


def test_the_proxy_exchanges_to_the_door_token_and_invokes_the_runtimes_bearer_endpoint_with_the_body_only(monkeypatch):
    import io
    import types
    import urllib.parse

    calls: list[Any] = []

    class Boto:
        def describe_user_pool_client(self, **kwargs: Any) -> dict[str, Any]:
            calls.append(("describe", kwargs))
            return {"UserPoolClient": {"ClientSecret": "s3cret"}}

    class Response(io.BytesIO):
        status = 200

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *exc: Any) -> None:
            pass

    def http(request: Any) -> Response:
        calls.append(("http", request.full_url, dict(request.header_items()), request.data))
        if request.full_url == ENV["TOKEN_ENDPOINT"]:
            return Response(json.dumps({"access_token": "d00r-t0ken", "expires_in": 3600}).encode())
        return Response(json.dumps({"answer": "fixed-reply"}).encode())

    module = load(door.PROXY_SOURCE, ENV, monkeypatch, boto=Boto(), http=http)
    out = module["handler"]({"body": json.dumps({"question": "g-001"}), "headers": {"authorization": "Bearer caller-token"}}, None)
    assert out["statusCode"] == 200 and json.loads(out["body"]) == {"answer": "fixed-reply"}
    assert calls[0] == ("describe", {"UserPoolId": POOL, "ClientId": DOOR_CLIENT})
    token_call = calls[1]
    assert token_call[1] == ENV["TOKEN_ENDPOINT"]
    assert token_call[2]["Authorization"] == "Basic " + base64.b64encode(f"{DOOR_CLIENT}:s3cret".encode()).decode()
    assert urllib.parse.parse_qs(token_call[3].decode()) == {"grant_type": ["client_credentials"], "scope": [ENV["SCOPE"]]}
    invoke = calls[2]
    assert invoke[1] == ("https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/"
                         + urllib.parse.quote(ENV["RUNTIME_ARN"], safe="") + "/invocations?qualifier=DEFAULT")
    assert invoke[2]["Authorization"] == "Bearer d00r-t0ken" and len(invoke[2]["X-amzn-bedrock-agentcore-runtime-session-id"]) >= 33
    assert json.loads(invoke[3]) == {"question": "g-001"}
    assert "caller-token" not in json.dumps(invoke[2])  # the caller's token never reaches the runtime
    # a second call reuses the cached door token: no second DescribeUserPoolClient, no second token call
    module["handler"]({"body": "{}", "headers": {}}, None)
    assert [c[0] for c in calls].count("describe") == 1 and sum(1 for c in calls if c[0] == "http" and c[1] == ENV["TOKEN_ENDPOINT"]) == 1
    assert isinstance(types, object)


# --- the seat reads on PR 2: what they found, held here -------------------------------------------------------


def test_the_doored_stacks_nag_report_has_no_non_compliant_row(tmp_path):
    """security-reviewer F4 on PR 2: the committed construct report is refagent's, whose stack has no door, so the
    door's cdk-nag rows are read here, from the fixture's own synth, as check_cdk_nag reads the committed apps."""
    import csv
    import os
    import subprocess
    import sys

    out = tmp_path / "door"
    done = subprocess.run([sys.executable, str(ROOT / "infra" / "construct" / "app.py")], cwd=ROOT, capture_output=True,
                          text=True, check=False, env={**os.environ, "PYTHONPATH": str(ROOT), "CDK_OUTDIR": str(out),
                                                       "AGENTKEEL_BUNDLE": FIXTURE.relative_to(ROOT).as_posix()})  # fmt: skip
    assert done.returncode == 0, done.stderr
    with (out / "AwsSolutions--AgentkeelAgent-NagReport.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows, "no cdk-nag report was written"
    non_compliant = [(r["Rule ID"], r["Resource ID"]) for r in rows if r["Compliance"] == "Non-Compliant"]
    assert non_compliant == [], non_compliant
    suppressed = {(r["Rule ID"], r["Resource ID"]) for r in rows if r["Compliance"] == "Suppressed"}
    assert ("AwsSolutions-COG2", "AgentkeelAgent/Agent/Pool") in suppressed
    assert ("AwsSolutions-COG8", "AgentkeelAgent/Agent/Pool") in suppressed


def test_the_authoriser_clips_what_it_writes_and_survives_a_malformed_payload(monkeypatch):
    """security-reviewer F1 and F2 on PR 2: a claimed subject or issuer that is not a name or a URL reaches the
    access-log line as `-`, never with a quote or a newline; a payload that is not an object, or an exp that is
    not a number, is refused, not crashed on."""
    quoted = authorise(monkeypatch, sign(claims(username='box"office\n,"agent":"other', iss="https://evil/\"x")))
    assert quoted["isAuthorized"] is False and quoted["context"] == {"subject": "-", "issuer": "-", "outcome": "refused", "reason": "not admitted"}
    long_name = authorise(monkeypatch, sign(claims(username="Box Office " * 4)))  # not a name, not a client id
    assert long_name["context"]["subject"] == "-"
    # the context never carries anything but the four keys, each a clipped string
    for out in (quoted, long_name):
        assert set(out["context"]) == {"subject", "issuer", "outcome", "reason"}
        assert all(isinstance(v, str) and '"' not in v and "\n" not in v for v in out["context"].values())
    header = b64url(json.dumps({"alg": "RS256", "kid": "k1"}).encode())
    not_an_object = f"{header}.{b64url(b'[]')}.{b64url(b'sig')}"
    assert authorise(monkeypatch, not_an_object)["context"]["reason"] == "no identity"
    string_exp = authorise(monkeypatch, sign(claims(exp="never")))
    assert string_exp["isAuthorized"] is False and string_exp["context"]["reason"] == "not admitted"
    assert authorise(monkeypatch, sign(claims(exp=None)))["isAuthorized"] is False
    # the route key, not the request path, is what the format writes
    assert "$context.routeKey" in door.ACCESS_LOG_FORMAT and "$context.path" not in door.ACCESS_LOG_FORMAT


def test_the_doored_stack_writes_no_logs_resource_policy_of_its_own(door_template):
    """security-reviewer F1 on M10 PR 3: the execution role holds logs:PutResourcePolicy on * for the stage's vended
    delivery, uncapped. The construct must never declare one; a template that did would be honoured."""
    assert not of_type(door_template, "AWS::Logs::ResourcePolicy")
