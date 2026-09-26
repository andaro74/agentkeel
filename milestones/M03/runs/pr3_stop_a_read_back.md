# Stop A, read_back_grants.py before and after the bootstrap redeploy (M03 PR 3)

Run by the human as admin, 2026-09-26, from a clean checkout of `0a90d52`:
once before the deploy of `AgentkeelBootstrap` (`before.md`) and once after
it (`after.md`). The two outputs are byte-identical (`diff before.md
after.md` printed nothing; `cmp` read by the session), so one table stands
for both. 81 cases, every one the decision expected (mismatches: 0): PR 2's
79 and, first run here, the agent ceiling's two DynamoDB rows that
`5871122` added for `milestones/M03/open.md` row 8 (`dynamodb:Scan`
allowed, `dynamodb:PutItem` implicitDeny; the last two rows).

The deploy changed no IAM policy document (the `cdk diff`,
`pr3_stop_a_cdk_diff.md`), so nothing here was expected to move. What it
does not show: that the eval role may apply version 5. The simulated
`ApplyGuardrail` row names the unversioned ARN; the grant is on
`<arn>:*`, and the first read of version 5 as the eval role is PR 3's CI
run (security-reviewer on PR 3 before stop A). Written by the human; the
header added by the session, the table unchanged. It reads IAM at the
moment it ran and nothing more.

| Principal | Action | Resource | Context | Decision | Expected |
|---|---|---|---|---|---|
| `agentkeel-cfn-exec` | `iam:CreateRole` | `iam::<acct>:role/agentkeel/agents/refagent-x` | iam:PermissionsBoundary=policy/agentkeel-boundary | **allowed** | allowed |
| `agentkeel-cfn-exec` | `iam:CreateRole` | `iam::<acct>:role/agentkeel/agents/refagent-x` | — | implicitDeny | implicitDeny |
| `agentkeel-cfn-exec` | `iam:CreateRole` | `iam::<acct>:role/not-an-agent` | iam:PermissionsBoundary=policy/agentkeel-boundary | implicitDeny | implicitDeny |
| `agentkeel-cfn-exec` | `iam:ListRolePolicies` | `iam::<acct>:role/agentkeel/agents/refagent-x` | — | **allowed** | allowed |
| `agentkeel-cfn-exec` | `iam:PassRole` | `iam::<acct>:role/agentkeel/agents/refagent-x` | iam:PassedToService=bedrock-agentcore.amazonaws.com | **allowed** | allowed |
| `agentkeel-cfn-exec` | `iam:PassRole` | `iam::<acct>:role/agentkeel/agents/refagent-x` | iam:PassedToService=ec2.amazonaws.com | implicitDeny | implicitDeny |
| `agentkeel-cfn-exec` | `iam:CreateServiceLinkedRole` | `iam::<acct>:role/aws-service-role/network.bedrock-agentcore.amazonaws.com/AWSServiceRoleForBedrockAgentCoreNetwork` | iam:AWSServiceName=network.bedrock-agentcore.amazonaws.com | **allowed** | allowed |
| `agentkeel-cfn-exec` | `ssm:GetParameters` | `ssm:us-west-2:<acct>:parameter/agentkeel/security/vpc-id` | — | **allowed** | allowed |
| `agentkeel-cfn-exec` | `ssm:GetParameters` | `ssm:us-west-2:<acct>:parameter/other/secret` | — | implicitDeny | implicitDeny |
| `agentkeel-cfn-exec` | `ec2:CreateSecurityGroup` | `security-group/* + vpc/vpc-0638596d59ee8f1b9` | — | **allowed** | allowed |
| `agentkeel-cfn-exec` | `ec2:CreateSecurityGroup` | `security-group/* + vpc/vpc-other` | — | implicitDeny | implicitDeny |
| `agentkeel-cfn-exec` | `ec2:DeleteSecurityGroup` | `ec2:us-west-2:<acct>:security-group/sg-0` | ec2:Vpc=vpc/vpc-0638596d59ee8f1b9 | **allowed** | allowed |
| `agentkeel-cfn-exec` | `ec2:DeleteSecurityGroup` | `ec2:us-west-2:<acct>:security-group/sg-0` | ec2:Vpc=vpc/vpc-other | implicitDeny | implicitDeny |
| `agentkeel-cfn-exec` | `ec2:CreateNetworkInterface` | `network-interface/* + subnet/subnet-0 + security-group/sg-0` | ec2:Vpc=vpc/vpc-0638596d59ee8f1b9 | **allowed** | allowed |
| `agentkeel-cfn-exec` | `ec2:CreateNetworkInterface` | `network-interface/* + subnet/subnet-0 + security-group/sg-0` | ec2:Vpc=vpc/vpc-other | implicitDeny | implicitDeny |
| `agentkeel-cfn-exec` | `dynamodb:CreateTable` | `dynamodb:us-west-2:<acct>:table/agentkeel-refagent-rights` | — | **allowed** | allowed |
| `agentkeel-cfn-exec` | `dynamodb:DeleteTable` | `dynamodb:us-west-2:<acct>:table/agentkeel-refagent-rights` | — | implicitDeny | implicitDeny |
| `agentkeel-cfn-exec` | `bedrock:CreateInferenceProfile` | `bedrock:us-west-2:<acct>:application-inference-profile/abc123` | — | **allowed** | allowed |
| `agentkeel-cfn-exec` | `bedrock-agentcore:CreateAgentRuntime` | `*` | bedrock-agentcore:subnets=subnet-00008bbb7a11551a0/subnet-0f82c2f36bd203187 | **allowed** | allowed |
| `agentkeel-cfn-exec` | `bedrock-agentcore:CreateAgentRuntime` | `*` | bedrock-agentcore:subnets=subnet-00008bbb7a11551a0/subnet-elsewhere | implicitDeny | implicitDeny |
| `agentkeel-cfn-exec` | `bedrock-agentcore:CreateAgentRuntime` | `*` | — | implicitDeny | implicitDeny |
| `agentkeel-cfn-exec` | `bedrock-agentcore:GetAgentRuntime` | `bedrock-agentcore:us-west-2:<acct>:runtime/refagent-abc` | — | **allowed** | allowed |
| `agentkeel-cfn-exec` | `kms:PutKeyPolicy` | `*` | — | explicitDeny | explicitDeny |
| `agentkeel-cfn-exec` | `ec2:CreateInternetGateway` | `*` | — | explicitDeny | explicitDeny |
| `agentkeel-cfn-exec` | `bedrock:CreateGuardrail` | `*` | — | explicitDeny | explicitDeny |
| `agentkeel-cfn-exec` | `bedrock:ApplyGuardrail` | `bedrock:us-west-2:<acct>:guardrail/notrefagent0` | — | implicitDeny | implicitDeny |
| `agentkeel-cfn-exec` | `ssm:PutParameter` | `ssm:us-west-2:<acct>:parameter/agentkeel/marker/refagent/rights-table-digest` | — | implicitDeny | implicitDeny |
| `agentkeel-deploy` | `ecr:GetAuthorizationToken` | `*` | — | **allowed** | allowed |
| `agentkeel-deploy` | `ecr:PutImage` | `ecr:us-west-2:<acct>:repository/agentkeel-refagent` | — | **allowed** | allowed |
| `agentkeel-deploy` | `ecr:BatchDeleteImage` | `ecr:us-west-2:<acct>:repository/agentkeel-refagent` | — | implicitDeny | implicitDeny |
| `agentkeel-deploy` | `dynamodb:PutItem` | `dynamodb:us-west-2:<acct>:table/agentkeel-refagent-rights` | — | **allowed** | allowed |
| `agentkeel-deploy` | `dynamodb:DeleteItem` | `dynamodb:us-west-2:<acct>:table/agentkeel-refagent-rights` | — | **allowed** | allowed |
| `agentkeel-deploy` | `dynamodb:Scan` | `dynamodb:us-west-2:<acct>:table/agentkeel-refagent-rights` | — | **allowed** | allowed |
| `agentkeel-deploy` | `dynamodb:DeleteItem` | `dynamodb:us-west-2:<acct>:table/other` | — | implicitDeny | implicitDeny |
| `agentkeel-deploy` | `dynamodb:DeleteTable` | `dynamodb:us-west-2:<acct>:table/agentkeel-refagent-rights` | — | implicitDeny | implicitDeny |
| `agentkeel-deploy` | `dynamodb:BatchWriteItem` | `dynamodb:us-west-2:<acct>:table/agentkeel-refagent-rights` | — | implicitDeny | implicitDeny |
| `agentkeel-deploy` | `ssm:PutParameter` | `ssm:us-west-2:<acct>:parameter/agentkeel/marker/refagent/rights-table-digest` | — | **allowed** | allowed |
| `agentkeel-deploy` | `ssm:DeleteParameter` | `ssm:us-west-2:<acct>:parameter/agentkeel/marker/refagent/rights-table-digest` | — | implicitDeny | implicitDeny |
| `agentkeel-deploy` | `ssm:PutParameter` | `ssm:us-west-2:<acct>:parameter/agentkeel/security/boundary-arn` | — | implicitDeny | implicitDeny |
| `agentkeel-deploy` | `ssm:PutParameter` | `ssm:us-west-2:<acct>:parameter/agentkeel/security/guardrail/refagent` | — | implicitDeny | implicitDeny |
| `agentkeel-deploy` | `bedrock:CreateGuardrail` | `*` | — | explicitDeny | explicitDeny |
| `agentkeel-deploy` | `bedrock:ApplyGuardrail` | `bedrock:us-west-2:<acct>:guardrail/notrefagent0` | — | implicitDeny | implicitDeny |
| `agentkeel-deploy` | `bedrock-agentcore:InvokeAgentRuntime` | `bedrock-agentcore:us-west-2:<acct>:runtime/refagent-abc` | — | **allowed** | allowed |
| `agentkeel-deploy` | `bedrock-agentcore:InvokeAgentRuntime` | `bedrock-agentcore:us-west-2:<acct>:runtime/other-abc` | — | implicitDeny | implicitDeny |
| `agentkeel-deploy` | `cloudformation:CreateChangeSet` | `cloudformation:us-west-2:<acct>:stack/agentkeel-refagent/x` | — | **allowed** | allowed |
| `agentkeel-deploy` | `cloudformation:DescribeStacks` | `cloudformation:us-west-2:<acct>:stack/AgentkeelBootstrap/x` | — | implicitDeny | implicitDeny |
| `agentkeel-deploy` | `iam:PassRole` | `iam::<acct>:role/agentkeel-cfn-exec` | — | **allowed** | allowed |
| `agentkeel-evals` | `cloudformation:DescribeStacks` | `cloudformation:us-west-2:<acct>:stack/agentkeel-refagent/x` | — | **allowed** | allowed |
| `agentkeel-evals` | `cloudformation:DescribeStacks` | `cloudformation:us-west-2:<acct>:stack/AgentkeelBootstrap/x` | — | implicitDeny | implicitDeny |
| `agentkeel-evals` | `bedrock-agentcore:GetAgentRuntime` | `bedrock-agentcore:us-west-2:<acct>:runtime/refagent-abc` | — | **allowed** | allowed |
| `agentkeel-evals` | `bedrock-agentcore:GetAgentRuntime` | `bedrock-agentcore:us-west-2:<acct>:runtime/other-abc` | — | implicitDeny | implicitDeny |
| `agentkeel-evals` | `bedrock-agentcore:UpdateAgentRuntime` | `bedrock-agentcore:us-west-2:<acct>:runtime/refagent-abc` | — | implicitDeny | implicitDeny |
| `agentkeel-evals` | `ecr:DescribeImages` | `ecr:us-west-2:<acct>:repository/agentkeel-refagent` | — | **allowed** | allowed |
| `agentkeel-evals` | `ecr:PutImage` | `ecr:us-west-2:<acct>:repository/agentkeel-refagent` | — | implicitDeny | implicitDeny |
| `agentkeel-evals` | `bedrock-agentcore:InvokeAgentRuntime` | `bedrock-agentcore:us-west-2:<acct>:runtime/refagent-abc` | — | **allowed** | allowed |
| `agentkeel-evals` | `ssm:GetParameter` | `ssm:us-west-2:<acct>:parameter/agentkeel/marker/refagent/rights-table-digest` | — | **allowed** | allowed |
| `agentkeel-evals` | `ssm:PutParameter` | `ssm:us-west-2:<acct>:parameter/agentkeel/marker/refagent/rights-table-digest` | — | implicitDeny | implicitDeny |
| `agentkeel-evals` | `ssm:GetParameter` | `ssm:us-west-2:<acct>:parameter/agentkeel/security/vpc-id` | — | implicitDeny | implicitDeny |
| `agentkeel-evals` | `bedrock:CreateGuardrail` | `*` | — | explicitDeny | explicitDeny |
| `agentkeel-evals` | `bedrock:UpdateGuardrail` | `bedrock:us-west-2:<acct>:guardrail/notrefagent0` | — | explicitDeny | explicitDeny |
| `agentkeel-evals` | `bedrock:GetGuardrail` | `bedrock:us-west-2:<acct>:guardrail/notrefagent0` | — | explicitDeny | explicitDeny |
| `agentkeel-evals` | `bedrock:ListGuardrails` | `*` | — | explicitDeny | explicitDeny |
| `agentkeel-evals` | `bedrock:ApplyGuardrail` | `bedrock:us-west-2:<acct>:guardrail/1088aw3ujhyd` | — | **allowed** | allowed |
| `agentkeel-evals` | `bedrock:ApplyGuardrail` | `bedrock:us-west-2:<acct>:guardrail/notrefagent0` | — | implicitDeny | implicitDeny |
| `agentkeel-developer` | `bedrock:ListGuardrails` | `*` | — | explicitDeny | explicitDeny |
| `agentkeel-developer` | `bedrock:CreateGuardrail` | `*` | — | explicitDeny | explicitDeny |
| `agentkeel-developer` | `ssm:PutParameter` | `ssm:us-west-2:<acct>:parameter/agentkeel/marker/refagent/rights-table-digest` | — | implicitDeny | implicitDeny |
| `agentkeel-boundary (ceiling)` | `ecr:BatchGetImage` | `*` | — | **allowed** | allowed |
| `agentkeel-boundary (ceiling)` | `ecr:GetDownloadUrlForLayer` | `*` | — | **allowed** | allowed |
| `agentkeel-boundary (ceiling)` | `ecr:GetAuthorizationToken` | `*` | — | **allowed** | allowed |
| `agentkeel-boundary (ceiling)` | `logs:CreateLogGroup` | `*` | — | **allowed** | allowed |
| `agentkeel-boundary (ceiling)` | `ecr:PutImage` | `*` | — | implicitDeny | implicitDeny |
| `agentkeel-boundary (ceiling)` | `ecr:BatchDeleteImage` | `*` | — | implicitDeny | implicitDeny |
| `agentkeel-boundary (ceiling)` | `kms:GetKeyPolicy` | `*` | — | **allowed** | allowed |
| `agentkeel-boundary (ceiling)` | `kms:PutKeyPolicy` | `*` | — | explicitDeny | explicitDeny |
| `agentkeel-boundary (ceiling)` | `bedrock:ApplyGuardrail` | `*` | — | **allowed** | allowed |
| `agentkeel-boundary (ceiling)` | `bedrock:CreateGuardrail` | `*` | — | explicitDeny | explicitDeny |
| `agentkeel-boundary (ceiling)` | `bedrock:GetGuardrail` | `*` | — | explicitDeny | explicitDeny |
| `agentkeel-boundary (ceiling)` | `ssm:GetParameter` | `*` | — | implicitDeny | implicitDeny |
| `agentkeel-boundary (ceiling)` | `dynamodb:Scan` | `*` | — | **allowed** | allowed |
| `agentkeel-boundary (ceiling)` | `dynamodb:PutItem` | `*` | — | implicitDeny | implicitDeny |

mismatches: 0
