"""Read the deployed grants back from the account (M01 PR 3; ruling j's method).

    python scripts/read_back_grants.py        # admin credentials, agent account, us-west-2

What `milestones/M01/rulings/pr3.md` transcribes: `simulate-principal-policy`
on `agentkeel-cfn-exec`, `agentkeel-deploy` and `agentkeel-evals`, and
`simulate-custom-policy` on `agentkeel-boundary` as a ceiling, under an
allow-all identity policy, because no agent role exists before the first
deploy. From M03 PR 2 also `agentkeel-developer`, and the rows for the
narrowed guardrail deny and the rights table marker. Each grant has a negative beside it: the wrong VPC, the wrong subnet,
no boundary, the wrong service, a delete where only a write is granted. It
prints one markdown row per case and the count of mismatches, and exits 1 on
any mismatch.

Committed so that the tables in pr3.md can be re-run from the tree rather than
taken on trust (PR 3 cold review F5). It is not run in CI: it needs admin
credentials, and no CI role may read IAM this way. Its output is evidence of
the account at the moment it ran, and nothing more. A simulation reads IAM,
not the service: what CloudFormation and AgentCore actually call is read by
the first deploy.
"""
import json
import sys

import boto3


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    A = "581208540944"
    R = "us-west-2"
    iam = boto3.client("iam")
    ssm = boto3.client("ssm", region_name=R)
    vpc = ssm.get_parameter(Name="/agentkeel/security/vpc-id")["Parameter"]["Value"]
    boundary = ssm.get_parameter(Name="/agentkeel/security/boundary-arn")["Parameter"]["Value"]
    vpc_arn = f"arn:aws:ec2:{R}:{A}:vpc/{vpc}"
    agent_role = f"arn:aws:iam::{A}:role/agentkeel/agents/refagent-x"
    # M03 PR 2: the table marker, and a guardrail that is not refagent's.
    marker = f"arn:aws:ssm:{R}:{A}:parameter/agentkeel/marker/refagent/rights-table-digest"
    guardrail_any = f"arn:aws:bedrock:{R}:{A}:guardrail/notrefagent0"


    def ctx(**kv):
        return [{"ContextKeyName": k.replace("__", ":"), "ContextKeyValues": [v], "ContextKeyType": "string"}
                for k, v in kv.items()]


    def principal(role, rows):
        out = []
        for action, resource, context, expect in rows:
            r = iam.simulate_principal_policy(
                PolicySourceArn=f"arn:aws:iam::{A}:role/{role}", ActionNames=[action],
                ResourceArns=resource if isinstance(resource, list) else [resource],
                ContextEntries=context or [])["EvaluationResults"][0]
            out.append((role, action, resource if isinstance(resource, str) else " + ".join(x.split(":")[-1] for x in resource),
                        context, r["EvalDecision"], expect))
        return out


    platform_subnets = ssm.get_parameter(Name="/agentkeel/security/subnet-ids")["Parameter"]["Value"].split(",")


    def subnets(ids):
        return [{"ContextKeyName": "bedrock-agentcore:subnets", "ContextKeyValues": ids, "ContextKeyType": "stringList"}]


    cfn = principal("agentkeel-cfn-exec", [
        ("iam:CreateRole", agent_role, ctx(iam__PermissionsBoundary=boundary), "allowed"),
        ("iam:CreateRole", agent_role, None, "implicitDeny"),
        ("iam:CreateRole", f"arn:aws:iam::{A}:role/not-an-agent", ctx(iam__PermissionsBoundary=boundary), "implicitDeny"),
        ("iam:ListRolePolicies", agent_role, None, "allowed"),
        ("iam:PassRole", agent_role, ctx(iam__PassedToService="bedrock-agentcore.amazonaws.com"), "allowed"),
        ("iam:PassRole", agent_role, ctx(iam__PassedToService="ec2.amazonaws.com"), "implicitDeny"),
        ("iam:CreateServiceLinkedRole",
         f"arn:aws:iam::{A}:role/aws-service-role/network.bedrock-agentcore.amazonaws.com/AWSServiceRoleForBedrockAgentCoreNetwork",
         ctx(iam__AWSServiceName="network.bedrock-agentcore.amazonaws.com"), "allowed"),
        ("ssm:GetParameters", f"arn:aws:ssm:{R}:{A}:parameter/agentkeel/security/vpc-id", None, "allowed"),
        ("ssm:GetParameters", f"arn:aws:ssm:{R}:{A}:parameter/other/secret", None, "implicitDeny"),
        ("ec2:CreateSecurityGroup", [f"arn:aws:ec2:{R}:{A}:security-group/*", vpc_arn], None, "allowed"),
        ("ec2:CreateSecurityGroup", [f"arn:aws:ec2:{R}:{A}:security-group/*", f"arn:aws:ec2:{R}:{A}:vpc/vpc-other"],
         None, "implicitDeny"),
        ("ec2:DeleteSecurityGroup", f"arn:aws:ec2:{R}:{A}:security-group/sg-0", ctx(ec2__Vpc=vpc_arn), "allowed"),
        ("ec2:DeleteSecurityGroup", f"arn:aws:ec2:{R}:{A}:security-group/sg-0",
         ctx(ec2__Vpc=f"arn:aws:ec2:{R}:{A}:vpc/vpc-other"), "implicitDeny"),
        ("ec2:CreateNetworkInterface", [f"arn:aws:ec2:{R}:{A}:network-interface/*", f"arn:aws:ec2:{R}:{A}:subnet/subnet-0",
         f"arn:aws:ec2:{R}:{A}:security-group/sg-0"], ctx(ec2__Vpc=vpc_arn), "allowed"),
        ("ec2:CreateNetworkInterface", [f"arn:aws:ec2:{R}:{A}:network-interface/*", f"arn:aws:ec2:{R}:{A}:subnet/subnet-0",
         f"arn:aws:ec2:{R}:{A}:security-group/sg-0"], ctx(ec2__Vpc=f"arn:aws:ec2:{R}:{A}:vpc/vpc-other"), "implicitDeny"),
        ("dynamodb:CreateTable", f"arn:aws:dynamodb:{R}:{A}:table/agentkeel-refagent-rights", None, "allowed"),
        ("dynamodb:DeleteTable", f"arn:aws:dynamodb:{R}:{A}:table/agentkeel-refagent-rights", None, "implicitDeny"),
        ("bedrock:CreateInferenceProfile", f"arn:aws:bedrock:{R}:{A}:application-inference-profile/abc123", None, "allowed"),
        ("bedrock-agentcore:CreateAgentRuntime", "*", subnets(platform_subnets), "allowed"),
        ("bedrock-agentcore:CreateAgentRuntime", "*", subnets(platform_subnets[:1] + ["subnet-elsewhere"]), "implicitDeny"),
        ("bedrock-agentcore:CreateAgentRuntime", "*", None, "implicitDeny"),
        ("bedrock-agentcore:GetAgentRuntime", f"arn:aws:bedrock-agentcore:{R}:{A}:runtime/refagent-abc", None, "allowed"),
        ("kms:PutKeyPolicy", "*", None, "explicitDeny"),
        ("ec2:CreateInternetGateway", "*", None, "explicitDeny"),
        # M03 PR 2: the guardrail deny narrowed to everything but Apply (SPEC/03 §6).
        ("bedrock:CreateGuardrail", "*", None, "explicitDeny"),
        ("bedrock:ApplyGuardrail", guardrail_any, None, "implicitDeny"),
        ("ssm:PutParameter", marker, None, "implicitDeny"),
    ])
    deploy = principal("agentkeel-deploy", [
        ("ecr:GetAuthorizationToken", "*", None, "allowed"),
        ("ecr:PutImage", f"arn:aws:ecr:{R}:{A}:repository/agentkeel-refagent", None, "allowed"),
        ("ecr:BatchDeleteImage", f"arn:aws:ecr:{R}:{A}:repository/agentkeel-refagent", None, "implicitDeny"),
        ("dynamodb:PutItem", f"arn:aws:dynamodb:{R}:{A}:table/agentkeel-refagent-rights", None, "allowed"),
        # M03 PR 2 (S1's reader): the table is the file, so rows the file lacks are deleted.
        ("dynamodb:DeleteItem", f"arn:aws:dynamodb:{R}:{A}:table/agentkeel-refagent-rights", None, "allowed"),
        ("dynamodb:Scan", f"arn:aws:dynamodb:{R}:{A}:table/agentkeel-refagent-rights", None, "allowed"),
        ("dynamodb:DeleteItem", f"arn:aws:dynamodb:{R}:{A}:table/other", None, "implicitDeny"),
        ("dynamodb:DeleteTable", f"arn:aws:dynamodb:{R}:{A}:table/agentkeel-refagent-rights", None, "implicitDeny"),
        ("dynamodb:BatchWriteItem", f"arn:aws:dynamodb:{R}:{A}:table/agentkeel-refagent-rights", None, "implicitDeny"),
        ("ssm:PutParameter", marker, None, "allowed"),
        ("ssm:DeleteParameter", marker, None, "implicitDeny"),
        ("ssm:PutParameter", f"arn:aws:ssm:{R}:{A}:parameter/agentkeel/security/boundary-arn", None, "implicitDeny"),
        ("bedrock:CreateGuardrail", "*", None, "explicitDeny"),
        ("bedrock:ApplyGuardrail", guardrail_any, None, "implicitDeny"),
        ("bedrock-agentcore:InvokeAgentRuntime", f"arn:aws:bedrock-agentcore:{R}:{A}:runtime/refagent-abc", None, "allowed"),
        ("bedrock-agentcore:InvokeAgentRuntime", f"arn:aws:bedrock-agentcore:{R}:{A}:runtime/other-abc", None, "implicitDeny"),
        ("cloudformation:CreateChangeSet", f"arn:aws:cloudformation:{R}:{A}:stack/agentkeel-refagent/x", None, "allowed"),
        ("cloudformation:DescribeStacks", f"arn:aws:cloudformation:{R}:{A}:stack/AgentkeelBootstrap/x", None, "implicitDeny"),
        ("iam:PassRole", f"arn:aws:iam::{A}:role/agentkeel-cfn-exec", None, "allowed"),
    ])

    evals = principal("agentkeel-evals", [
        ("cloudformation:DescribeStacks", f"arn:aws:cloudformation:{R}:{A}:stack/agentkeel-refagent/x", None, "allowed"),
        ("cloudformation:DescribeStacks", f"arn:aws:cloudformation:{R}:{A}:stack/AgentkeelBootstrap/x", None, "implicitDeny"),
        ("bedrock-agentcore:GetAgentRuntime", f"arn:aws:bedrock-agentcore:{R}:{A}:runtime/refagent-abc", None, "allowed"),
        ("bedrock-agentcore:GetAgentRuntime", f"arn:aws:bedrock-agentcore:{R}:{A}:runtime/other-abc", None, "implicitDeny"),
        ("bedrock-agentcore:UpdateAgentRuntime", f"arn:aws:bedrock-agentcore:{R}:{A}:runtime/refagent-abc", None, "implicitDeny"),
        ("ecr:DescribeImages", f"arn:aws:ecr:{R}:{A}:repository/agentkeel-refagent", None, "allowed"),
        ("ecr:PutImage", f"arn:aws:ecr:{R}:{A}:repository/agentkeel-refagent", None, "implicitDeny"),
        ("bedrock-agentcore:InvokeAgentRuntime", f"arn:aws:bedrock-agentcore:{R}:{A}:runtime/refagent-abc", None, "allowed"),
        # M03 PR 2: the table marker, read only; the guardrail's admin actions still denied.
        ("ssm:GetParameter", marker, None, "allowed"),
        ("ssm:PutParameter", marker, None, "implicitDeny"),
        ("ssm:GetParameter", f"arn:aws:ssm:{R}:{A}:parameter/agentkeel/security/vpc-id", None, "implicitDeny"),
        ("bedrock:CreateGuardrail", "*", None, "explicitDeny"),
        ("bedrock:UpdateGuardrail", guardrail_any, None, "explicitDeny"),
        ("bedrock:GetGuardrail", guardrail_any, None, "explicitDeny"),
        ("bedrock:ListGuardrails", "*", None, "explicitDeny"),
    ])

    # M03 PR 2 (security-reviewer on e2839f2, FINDING 2): its bedrock:List* must not reach the guardrails.
    developer = principal("agentkeel-developer", [
        ("bedrock:ListGuardrails", "*", None, "explicitDeny"),
        ("bedrock:CreateGuardrail", "*", None, "explicitDeny"),
        ("ssm:PutParameter", marker, None, "implicitDeny"),
    ])

    # The agent boundary as a ceiling: an allow-all identity policy under it.
    doc = iam.get_policy_version(PolicyArn=boundary, VersionId=iam.get_policy(PolicyArn=boundary)["Policy"]["DefaultVersionId"])
    boundary_doc = json.dumps(doc["PolicyVersion"]["Document"])
    allow_all = json.dumps({"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]})
    ceiling = []
    for action, expect in [("ecr:BatchGetImage", "allowed"), ("ecr:GetDownloadUrlForLayer", "allowed"),
                           ("ecr:GetAuthorizationToken", "allowed"), ("logs:CreateLogGroup", "allowed"),
                           ("ecr:PutImage", "implicitDeny"), ("ecr:BatchDeleteImage", "implicitDeny"),
                           ("kms:GetKeyPolicy", "allowed"), ("kms:PutKeyPolicy", "explicitDeny"),
                           # M03 PR 2: Apply under the ceiling, nothing else on a guardrail, no ssm.
                           ("bedrock:ApplyGuardrail", "allowed"), ("bedrock:CreateGuardrail", "explicitDeny"),
                           ("bedrock:GetGuardrail", "explicitDeny"), ("ssm:GetParameter", "implicitDeny")]:
        r = iam.simulate_custom_policy(PolicyInputList=[allow_all], PermissionsBoundaryPolicyInputList=[boundary_doc],
                                       ActionNames=[action], ResourceArns=["*"])["EvaluationResults"][0]
        ceiling.append(("agentkeel-boundary (ceiling)", action, "*", None, r["EvalDecision"], expect))

    bad = 0
    print("| Principal | Action | Resource | Context | Decision | Expected |")
    print("|---|---|---|---|---|---|")
    for role, action, resource, context, got, expect in cfn + deploy + evals + developer + ceiling:
        c = ", ".join(f"{e['ContextKeyName']}={'/'.join(v.split(':')[-1] for v in e['ContextKeyValues'])}" for e in context or []) or "—"
        res = resource.replace(f"arn:aws:", "").replace(A, "<acct>")
        mark = "" if got == expect else " **MISMATCH**"
        bad += got != expect
        print(f"| `{role}` | `{action}` | `{res}` | {c} | {'**allowed**' if got == 'allowed' else got}{mark} | {expect} |")
    print(f"\nmismatches: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
