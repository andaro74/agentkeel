# Stop A, `cdk diff --strict AgentkeelBootstrap` before the redeploy (M03 PR 3)

Run by the human as admin, 2026-09-26, from a clean checkout of `0a90d52`
(`cd infra/bootstrap && npx aws-cdk@2 diff --strict AgentkeelBootstrap`),
after the read-back before (`pr3_stop_a_read_back.md`) and before the
deploy. Pasted by the human, transcribed whole below by the session.

What it shows, read by the session before the deploy was run:

- **Two resources change.** `RefagentGuardrailVersion` is replaced: its
  description goes from `rules sha256 9cbefa08…` (version 4, `ade6dcb`) to
  `rules sha256 b2cff2a1…`, the digest of the two rule files at `0a90d52`.
  `ParamGuardrail`'s description is corrected (security-reviewer N9 on
  PR 2, `d02be78`).
- **`RefagentGuardrail` itself does not change.** Its topics, PII and
  messages are version 4's, so version 5 is a snapshot of the same
  guardrail with a new description. No IAM policy document, boundary
  statement, security-group rule or VPC resource changes.
- **Ten changes are metadata only.** Each is a `cdk_nag`
  `rules_to_suppress` reason, on the boundary, five endpoint security
  groups and four role policies. The only difference is `§` in the tree
  against `?` in the deployed template (the `[-]` side). These are the "10
  changes omitted because they are likely mangled non-ASCII characters"
  of PR 2's diff (`guardrail_probes.md`; security-reviewer F3 on PR 2),
  now printed by `--strict`. The earlier deploy stored `?` in place of `§`.
  Metadata grants and denies nothing. Whether this deploy stored `§` is
  read by the next `cdk diff`.

```
Stack AgentkeelBootstrap
Resources
[~] AWS::IAM::ManagedPolicy Boundary BoundaryEA298153
 └─ [~] Metadata
     └─ [~] .cdk_nag:
         └─ [~] .rules_to_suppress:
             └─ @@ -1,6 +1,6 @@
                [ ] [
                [ ]   {
                [-]     "reason": "SPEC/01 ?6: 'the permission boundary, on every role either stack synthesises, applied stack-wide'. This is that boundary, and it is what seed S5 reads: a role handed to GovernedAgent without it is refused at synth. A ceiling, not a grant: a Deny must cover every resource, including ones that do not exist yet, or a later attach slips past it.",
                [+]     "reason": "SPEC/01 §6: 'the permission boundary, on every role either stack synthesises, applied stack-wide'. This is that boundary, and it is what seed S5 reads: a role handed to GovernedAgent without it is refused at synth. A ceiling, not a grant: a Deny must cover every resource, including ones that do not exist yet, or a later attach slips past it.",
                [ ]     "id": "AwsSolutions-IAM5"
                [ ]   }
                [ ] ]
[~] AWS::EC2::SecurityGroup Vpc/EndpointBedrockRuntime/SecurityGroup VpcEndpointBedrockRuntimeSecurityGroupDC40BAF1
 └─ [~] Metadata
     └─ [~] .cdk_nag:
         └─ [~] .rules_to_suppress:
             └─ @@ -1,6 +1,6 @@
                [ ] [
                [ ]   {
                [-]     "reason": "SPEC/01 ?6: 'a VPC with no internet gateway, endpoints with policies scoped to the account'. AwsSolutions-EC23 cannot resolve this rule: the source is the VPC's own CIDR, an intrinsic function at synth. The rule allows 443 from inside this VPC and nothing else, and the VPC has no way out.",
                [+]     "reason": "SPEC/01 §6: 'a VPC with no internet gateway, endpoints with policies scoped to the account'. AwsSolutions-EC23 cannot resolve this rule: the source is the VPC's own CIDR, an intrinsic function at synth. The rule allows 443 from inside this VPC and nothing else, and the VPC has no way out.",
                [ ]     "id": "CdkNagValidationFailure"
                [ ]   }
                [ ] ]
[~] AWS::EC2::SecurityGroup Vpc/EndpointKms/SecurityGroup VpcEndpointKmsSecurityGroupBA52493D
 └─ [~] Metadata
     └─ [~] .cdk_nag:
         └─ [~] .rules_to_suppress:
             └─ @@ -1,6 +1,6 @@
                [ ] [
                [ ]   {
                [-]     "reason": "SPEC/01 ?6: 'a VPC with no internet gateway, endpoints with policies scoped to the account'. AwsSolutions-EC23 cannot resolve this rule: the source is the VPC's own CIDR, an intrinsic function at synth. The rule allows 443 from inside this VPC and nothing else, and the VPC has no way out.",
                [+]     "reason": "SPEC/01 §6: 'a VPC with no internet gateway, endpoints with policies scoped to the account'. AwsSolutions-EC23 cannot resolve this rule: the source is the VPC's own CIDR, an intrinsic function at synth. The rule allows 443 from inside this VPC and nothing else, and the VPC has no way out.",
                [ ]     "id": "CdkNagValidationFailure"
                [ ]   }
                [ ] ]
[~] AWS::EC2::SecurityGroup Vpc/EndpointLogs/SecurityGroup VpcEndpointLogsSecurityGroupA1EEEDC3
 └─ [~] Metadata
     └─ [~] .cdk_nag:
         └─ [~] .rules_to_suppress:
             └─ @@ -1,6 +1,6 @@
                [ ] [
                [ ]   {
                [-]     "reason": "SPEC/01 ?6: 'a VPC with no internet gateway, endpoints with policies scoped to the account'. AwsSolutions-EC23 cannot resolve this rule: the source is the VPC's own CIDR, an intrinsic function at synth. The rule allows 443 from inside this VPC and nothing else, and the VPC has no way out.",
                [+]     "reason": "SPEC/01 §6: 'a VPC with no internet gateway, endpoints with policies scoped to the account'. AwsSolutions-EC23 cannot resolve this rule: the source is the VPC's own CIDR, an intrinsic function at synth. The rule allows 443 from inside this VPC and nothing else, and the VPC has no way out.",
                [ ]     "id": "CdkNagValidationFailure"
                [ ]   }
                [ ] ]
[~] AWS::EC2::SecurityGroup Vpc/EndpointEcrApi/SecurityGroup VpcEndpointEcrApiSecurityGroup0E9BC945
 └─ [~] Metadata
     └─ [~] .cdk_nag:
         └─ [~] .rules_to_suppress:
             └─ @@ -1,6 +1,6 @@
                [ ] [
                [ ]   {
                [-]     "reason": "SPEC/01 ?6: 'a VPC with no internet gateway, endpoints with policies scoped to the account'. AwsSolutions-EC23 cannot resolve this rule: the source is the VPC's own CIDR, an intrinsic function at synth. The rule allows 443 from inside this VPC and nothing else, and the VPC has no way out.",
                [+]     "reason": "SPEC/01 §6: 'a VPC with no internet gateway, endpoints with policies scoped to the account'. AwsSolutions-EC23 cannot resolve this rule: the source is the VPC's own CIDR, an intrinsic function at synth. The rule allows 443 from inside this VPC and nothing else, and the VPC has no way out.",
                [ ]     "id": "CdkNagValidationFailure"
                [ ]   }
                [ ] ]
[~] AWS::EC2::SecurityGroup Vpc/EndpointEcrDkr/SecurityGroup VpcEndpointEcrDkrSecurityGroupF331C903
 └─ [~] Metadata
     └─ [~] .cdk_nag:
         └─ [~] .rules_to_suppress:
             └─ @@ -1,6 +1,6 @@
                [ ] [
                [ ]   {
                [-]     "reason": "SPEC/01 ?6: 'a VPC with no internet gateway, endpoints with policies scoped to the account'. AwsSolutions-EC23 cannot resolve this rule: the source is the VPC's own CIDR, an intrinsic function at synth. The rule allows 443 from inside this VPC and nothing else, and the VPC has no way out.",
                [+]     "reason": "SPEC/01 §6: 'a VPC with no internet gateway, endpoints with policies scoped to the account'. AwsSolutions-EC23 cannot resolve this rule: the source is the VPC's own CIDR, an intrinsic function at synth. The rule allows 443 from inside this VPC and nothing else, and the VPC has no way out.",
                [ ]     "id": "CdkNagValidationFailure"
                [ ]   }
                [ ] ]
[~] AWS::IAM::Policy ExecutionRole/DefaultPolicy ExecutionRoleDefaultPolicyA5B92313
 └─ [~] Metadata
     └─ [~] .cdk_nag:
         └─ [~] .rules_to_suppress:
             └─ @@ -1,6 +1,6 @@
                [ ] [
                [ ]   {
                [-]     "reason": "SPEC/01 ?6: 'the CloudFormation execution role the deploy passes, which carries the boundary and may create a role only with the boundary attached'. iam:CreateRole is scoped to /agentkeel/agents/ and conditioned on iam:PermissionsBoundary; the wildcard is in the Deny. It is half of what seed S4 reads: the laptop cannot reach CloudFormation, and CloudFormation cannot exceed this. BLOCK F's grants are what GovernedAgent renders, one statement per resource type: managing security-group/* is conditioned on ec2:Vpc being this stack's VPC, and creating one is held by the VPC resource, because a new group has no ec2:Vpc yet; a new network-interface/* likewise, held by its subnet and group; CreateAgentRuntime takes no resource-level permission and is held to this stack's subnets by bedrock-agentcore:subnets; runtime/*, application-inference-profile/* and the agent role path name resources whose ids AWS assigns at create; ec2:Describe* takes no resource-level permission; security-group-rule/* is the egress rule's own resource; the five vpc-lattice actions are the Runtime create handler's VPC-mode calls, which name no resource in advance. The action lists are CloudFormation's published handler permissions (describe-type). A ceiling, not a grant: a Deny must cover every resource, including ones that do not exist yet, or a later attach slips past it.",
                [+]     "reason": "SPEC/01 §6: 'the CloudFormation execution role the deploy passes, which carries the boundary and may create a role only with the boundary attached'. iam:CreateRole is scoped to /agentkeel/agents/ and conditioned on iam:PermissionsBoundary; the wildcard is in the Deny. It is half of what seed S4 reads: the laptop cannot reach CloudFormation, and CloudFormation cannot exceed this. BLOCK F's grants are what GovernedAgent renders, one statement per resource type: managing security-group/* is conditioned on ec2:Vpc being this stack's VPC, and creating one is held by the VPC resource, because a new group has no ec2:Vpc yet; a new network-interface/* likewise, held by its subnet and group; CreateAgentRuntime takes no resource-level permission and is held to this stack's subnets by bedrock-agentcore:subnets; runtime/*, application-inference-profile/* and the agent role path name resources whose ids AWS assigns at create; ec2:Describe* takes no resource-level permission; security-group-rule/* is the egress rule's own resource; the five vpc-lattice actions are the Runtime create handler's VPC-mode calls, which name no resource in advance. The action lists are CloudFormation's published handler permissions (describe-type). A ceiling, not a grant: a Deny must cover every resource, including ones that do not exist yet, or a later attach slips past it.",
                [ ]     "id": "AwsSolutions-IAM5"
                [ ]   }
                [ ] ]
[~] AWS::IAM::Policy DeployRole/DefaultPolicy DeployRoleDefaultPolicyDC930F96
 └─ [~] Metadata
     └─ [~] .cdk_nag:
         └─ [~] .rules_to_suppress:
             └─ @@ -1,6 +1,6 @@
                [ ] [
                [ ]   {
                [-]     "reason": "SPEC/01 ?6: 'the deploy role, trusted with StringEquals on aud, the immutable sub for refs/heads/main, and job_workflow_ref'. Seed S4 is an attempt to do from a laptop what only this role may do. cloudformation:* is scoped to stack/agentkeel-*, the set of stacks this platform deploys; AWS appends the stack id suffix, which cannot be named in advance. BLOCK F: ecr:GetAuthorizationToken takes no resource; the push is on repository/agentkeel-*, the table load (put, scan, and the delete of rows the file lacks, M03 PR 2) on table/agentkeel-*-rights, and the load check's InvokeAgentRuntime on runtime/refagent*, the versioned name AgentCore assigns at create.",
                [+]     "reason": "SPEC/01 §6: 'the deploy role, trusted with StringEquals on aud, the immutable sub for refs/heads/main, and job_workflow_ref'. Seed S4 is an attempt to do from a laptop what only this role may do. cloudformation:* is scoped to stack/agentkeel-*, the set of stacks this platform deploys; AWS appends the stack id suffix, which cannot be named in advance. BLOCK F: ecr:GetAuthorizationToken takes no resource; the push is on repository/agentkeel-*, the table load (put, scan, and the delete of rows the file lacks, M03 PR 2) on table/agentkeel-*-rights, and the load check's InvokeAgentRuntime on runtime/refagent*, the versioned name AgentCore assigns at create.",
                [ ]     "id": "AwsSolutions-IAM5"
                [ ]   }
                [ ] ]
[~] AWS::IAM::Policy DeveloperRole/DefaultPolicy DeveloperRoleDefaultPolicy6E63DC77
 └─ [~] Metadata
     └─ [~] .cdk_nag:
         └─ [~] .rules_to_suppress:
             └─ @@ -1,6 +1,6 @@
                [ ] [
                [ ]   {
                [-]     "reason": "SPEC/01 ?6: 'the developer role (?1), boundary on'. This is seed S4's principal. The Allow is read-only describe and list; the wildcard is in the Deny that refuses the deploy. A ceiling, not a grant: a Deny must cover every resource, including ones that do not exist yet, or a later attach slips past it.",
                [+]     "reason": "SPEC/01 §6: 'the developer role (§1), boundary on'. This is seed S4's principal. The Allow is read-only describe and list; the wildcard is in the Deny that refuses the deploy. A ceiling, not a grant: a Deny must cover every resource, including ones that do not exist yet, or a later attach slips past it.",
                [ ]     "id": "AwsSolutions-IAM5"
                [ ]   }
                [ ] ]
[~] AWS::IAM::Policy EvalRole/DefaultPolicy EvalRoleDefaultPolicy39B7B632
 └─ [~] Metadata
     └─ [~] .cdk_nag:
         └─ [~] .rules_to_suppress:
             └─ @@ -1,6 +1,6 @@
                [ ] [
                [ ]   {
                [-]     "reason": "SPEC/01 ?6: 'the eval role, absorbed from infra/eval-role/ under a new name, with its Deny statement (item 33) and trust conditions as they stand'. The two profiles and the foundation models are named by ARN; runtime/refagent* covers the versioned runtime name AgentCore assigns, which does not exist until the deploy. The Deny (DENY: escalation, evidence deletion, and every guardrail action but Apply, M03 PR 2) is the ceiling. ApplyGuardrail is on refagent's guardrail and <arn>:*, its numbered versions only (M03 PR 2). Seeds S4 and S6: cloudtrail:LookupEvents is on * because CloudTrail takes no resource-level condition for it, and ruling i has this role ask CloudTrail whether the human's attempts were refused. It is the only cloudtrail action granted, so the instrument may read the record and may not change it. ADR-0007 (P1): stack/agentkeel-refagent/* is the stack id suffix AWS appends, and runtime/refagent* the versioned name; DescribeStacks, GetAgentRuntime and ecr:DescribeImages are reads on refagent alone. A ceiling, not a grant: a Deny must cover every resource, including ones that do not exist yet, or a later attach slips past it.",
                [+]     "reason": "SPEC/01 §6: 'the eval role, absorbed from infra/eval-role/ under a new name, with its Deny statement (item 33) and trust conditions as they stand'. The two profiles and the foundation models are named by ARN; runtime/refagent* covers the versioned runtime name AgentCore assigns, which does not exist until the deploy. The Deny (DENY: escalation, evidence deletion, and every guardrail action but Apply, M03 PR 2) is the ceiling. ApplyGuardrail is on refagent's guardrail and <arn>:*, its numbered versions only (M03 PR 2). Seeds S4 and S6: cloudtrail:LookupEvents is on * because CloudTrail takes no resource-level condition for it, and ruling i has this role ask CloudTrail whether the human's attempts were refused. It is the only cloudtrail action granted, so the instrument may read the record and may not change it. ADR-0007 (P1): stack/agentkeel-refagent/* is the stack id suffix AWS appends, and runtime/refagent* the versioned name; DescribeStacks, GetAgentRuntime and ecr:DescribeImages are reads on refagent alone. A ceiling, not a grant: a Deny must cover every resource, including ones that do not exist yet, or a later attach slips past it.",
                [ ]     "id": "AwsSolutions-IAM5"
                [ ]   }
                [ ] ]
[~] AWS::Bedrock::GuardrailVersion RefagentGuardrailVersion RefagentGuardrailVersion replace
 └─ [~] Description (requires replacement)
     ├─ [-] rules sha256 9cbefa08166fa869a80a0a533431366458b5671f4fa501297bf6b61af0e4413f
     └─ [+] rules sha256 b2cff2a1fd13d3638d29f232824dea2a7b5e6ee48951872e1979c4d651e10315
[~] AWS::SSM::Parameter ParamGuardrail ParamGuardrail82D0B153
 └─ [~] Description
     ├─ [-] agentkeel: refagent's guardrail. For GovernedAgent's ApplyGuardrail grant (M03 PR 2, the construct's commit).
     └─ [+] agentkeel: refagent's guardrail ARN, read by the human's read-back. The construct and the ingest stack take the id and version from the manifest, not from here.



✨  Number of stacks with differences: 1
```
