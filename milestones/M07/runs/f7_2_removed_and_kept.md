# What a retirement removes, and what it keeps

For seed S2 (`f7_2_retire.yaml`), owed by SPEC/07 §11 R7 before the
dispatch. Read from the tree at `a2c5a61` and the account as listed on
2026-10-02 (`pr2_reads.md`, R7). Security ruled the path on 2026-10-02
(`rulings/pr2-security.md`, item 11): a retirement is an update of the
agent's stack to a template without the runtime. Nothing here had run
when this was written. **The first retirement ran on 2026-10-03**
(`owner-check`, `runs/pr4_expected.md` attempt 6); what it showed is at
the end of this file.

The agent below is one made from the template, stack
`agentkeel-<name>`. refagent is never retired by this path: the retire
job refuses the name.

## Expected to be removed

Expected, not observed: no runtime has been deleted through this role
(see "Not read"). The retire job records a retirement only when one
invocation of the runtime's ARN after the update is refused with
`ResourceNotFoundException`; on any other result it fails, and the row
stays open (platform-architect B1 on M07 PR 2).

| Resource | By what | The record |
|---|---|---|
| The runtime `agentkeel_<name>` (`AWS::BedrockAgentCore::Runtime`) and the endpoint AgentCore made with it | CloudFormation, as `agentkeel-cfn-exec`, on a stack update from the deploy role on `main`. The execution role already may `DeleteAgentRuntime` on `runtime/agentkeel_*` | `DeleteAgentRuntime` in CloudTrail (`eventTime`) |
| The stack output `RuntimeArn` | the same update | the stack's outputs |

## Kept, by design

| Resource | Why it stays | Who could remove it |
|---|---|---|
| The stack `agentkeel-<name>` | the deploy role has no `cloudformation:DeleteStack` | an admin of the agent account, by hand |
| The agent's role, its security group, its inference profile | still in the template: the stack is updated, not deleted | the next update, or an admin |
| The agent's key and its alias `alias/agentkeel-<name>` | `RemovalPolicy.RETAIN` in the construct; the key policy denies `kms:ScheduleKeyDeletion` to every agent role and to four platform roles by name (`agentkeel-deploy`, `agentkeel-cfn-exec`, `agentkeel-evals`, `agentkeel-developer`). The two roles M07 PR 2 adds, `agentkeel-model-watch` and `agentkeel-envelope-row-put`, are not in that list: for them the deploy boundary's deny and the absence of any kms Allow hold it (platform-architect F2 on M07 PR 2; rulings/pr2-security.md item 13h) | an admin of the agent account |
| The rights table `agentkeel-<name>-rights` | `RemovalPolicy.RETAIN`; the deploy role has no `DeleteTable` | an admin |
| The image repository `agentkeel/<name>` and its images | not in the stack; tag-immutable; no role has `ecr:Delete*` | an admin |
| The runtime's log group | AgentCore made it at run time; it is in no stack | an admin; no platform role may `logs:Delete*` |
| The table marker `/agentkeel/marker/<name>/rights-table-digest` | written by the deploy, in no stack | an admin |
| The registry row, with `retired_at` | the row is the record that the agent existed; `scripts/registry.py retire` adds the field. `claim` and `write` refuse a name whose row says `retired_at`, so a later deploy does not replace the row | the deploy role holds `PutItem` on the table, which is not write-once: the refusal is the script's condition, not IAM's |
| AgentCore's network service-linked role | account-wide, made at the first runtime; not the agent's | an admin |
| `envelopes/agents/<name>/<commit>.json`, the answer records | the audit bucket, security account; put once; locked one day | the security account's admin, after the lock |
| `envelopes/agents/<name>/retired.json` | written once by the retire job, since the registry row is not write-once | the same |
| `bundles/<name>/<commit>.tar` and its signature | put once at each deploy from M07 PR 2 | the same |
| `agents/<name>/` in the audit bucket, the agent's own records | the agent's role put them at run time | the same |

## What the key encrypts

The agent's role may `Decrypt` and `GenerateDataKey` with its key. The
rights table uses DynamoDB's default encryption, not this key. The audit
bucket is in the security account under S3-managed encryption. So no
record a retirement keeps depends on the agent's key, and keeping the key
costs its monthly charge and nothing else.

## How long

The audit bucket's lock is one day (R5 as amended at M05). After that an
object is kept only by the security account's policies. Seven years is
M08's F8.4. M07 changes no retention.

## One-way

Nothing restores the runtime. A pull request that sets `rollout` back to
`all-at-once` is not deployed: `scripts/registry.py claim` refuses a name
whose row says `retired_at`, before the stack is touched, and the deploy
job fails there (security-reviewer 8 on M07 PR 2; until that repair it
would have been deployed as a new runtime and the row replaced). The
audit record's key is one per name, `retired.json`, which fits a name
that is retired once.

## Not read

- `DeleteAgentRuntime`'s behaviour on a runtime with an endpoint. It
  cannot be read without deleting one; S2 is the first.
- Whether an update that removes the runtime also removes the
  network interface AgentCore made in the VPC. Read at S2, by the
  security group's dependants after the update.
- Whether the delete removes the runtime's workload identity and the VPC
  Lattice association the create handler made. The delete handler names
  `DeleteWorkloadIdentity` and no lattice action (`pr2_reads.md`, R7,
  the read of 2026-10-02). Read at S2.
- Whether the delete succeeds at all. CloudFormation deletes a removed
  resource after the update has succeeded, so a failed delete leaves the
  stack `UPDATE_COMPLETE` and the runtime in the account outside any
  stack, where only an admin can delete it. The retire job's one
  invocation is what would show it.

## What the first retirement showed (2026-10-03, added at M07 PR 4)

`owner-check`, retire run 37129778736. The delete succeeded:
`DeleteAgentRuntime` in CloudTrail at 14:30:44Z as `agentkeel-cfn-exec`,
no error; the job's one invocation at 14:35:12Z answered
`ResourceNotFoundException`.

The three reads "Not read" promises "at S2" were not made at the
retirement (platform-architect F8 on PR 4). They were made at
2026-10-03T19:05Z, four and a half hours after the delete, by the
session as the agent account's admin user:

| Read | Result |
|---|---|
| The stack's resources | nine left: the key and its alias, the inference profile, the rights table, the role and its policy, the security group `sg-0657b2c0977659a8f` and its two egress rules. No runtime |
| The network interfaces behind that security group (`aws ec2 describe-network-interfaces --filters Name=group-id,...`) | **two, still `in-use`**: `eni-0186583e3b5e6180c` and `eni-06592620b867ef62a`, type `agentic_ai`, one in each platform subnet, attached, owner `amazon-aws`. `window-check`'s group, whose runtime is live, shows two of the same kind |
| The workload identity (`list-workload-identities`) | gone: `refagent-…` and `agentkeel_window_check-…` are listed, no `agentkeel_owner_check-…` |
| VPC Lattice (`list-service-network-vpc-associations` for the VPC; `list-resource-gateways`) | nothing listed |

**The finding:** a retirement removes the runtime and leaves its two
network interfaces in the platform VPC, behind a security group the
stack keeps. Whether AgentCore removes them later was not read; they
were still there after four and a half hours. The VPC has no route out,
and the group's egress is the platform endpoints'. Carried to M08 with
the kept role (platform-architect F9): what a retired agent's stack
should still hold is Security's.
