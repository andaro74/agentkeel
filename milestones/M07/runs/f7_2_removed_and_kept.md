# What a retirement removes, and what it keeps

For seed S2 (`f7_2_retire.yaml`), owed by SPEC/07 §11 R7 before the
dispatch. Read from the tree at `a2c5a61` and the account as listed on
2026-10-02 (`pr2_reads.md`, R7). Security ruled the path on 2026-10-02
(`rulings/pr2-security.md`, item 11): a retirement is an update of the
agent's stack to a template without the runtime. Nothing here has run:
the first retirement is S2's attempt on `owner-check`.

The agent below is one made from the template, stack
`agentkeel-<name>`. refagent is never retired by this path: the retire
job refuses the name.

## Removed

| Resource | By what | The record |
|---|---|---|
| The runtime `agentkeel_<name>` (`AWS::BedrockAgentCore::Runtime`) and the endpoint AgentCore made with it | CloudFormation, as `agentkeel-cfn-exec`, on a stack update from the deploy role on `main`. The execution role already may `DeleteAgentRuntime` on `runtime/agentkeel_*` | `DeleteAgentRuntime` in CloudTrail (`eventTime`) |
| The stack output `RuntimeArn` | the same update | the stack's outputs |

## Kept, by design

| Resource | Why it stays | Who could remove it |
|---|---|---|
| The stack `agentkeel-<name>` | the deploy role has no `cloudformation:DeleteStack` | an admin of the agent account, by hand |
| The agent's role, its security group, its inference profile | still in the template: the stack is updated, not deleted | the next update, or an admin |
| The agent's key and its alias `alias/agentkeel-<name>` | `RemovalPolicy.RETAIN` in the construct; the key policy denies `kms:ScheduleKeyDeletion` to every platform role and every agent role | an admin of the agent account |
| The rights table `agentkeel-<name>-rights` | `RemovalPolicy.RETAIN`; the deploy role has no `DeleteTable` | an admin |
| The image repository `agentkeel/<name>` and its images | not in the stack; tag-immutable; no role has `ecr:Delete*` | an admin |
| The runtime's log group | AgentCore made it at run time; it is in no stack | an admin; no platform role may `logs:Delete*` |
| The table marker `/agentkeel/marker/<name>/rights-table-digest` | written by the deploy, in no stack | an admin |
| The registry row, with `retired_at` | the row is the record that the agent existed; `scripts/registry.py retire` adds the field | the deploy role can rewrite a row; the table is not write-once |
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
`all-at-once` would be deployed as a new runtime by the next deploy run,
with a new ARN; the old ARN stays gone.

## Not read

- `DeleteAgentRuntime`'s behaviour on a runtime with an endpoint. It
  cannot be read without deleting one; S2 is the first.
- Whether an update that removes the runtime also removes the
  network interface AgentCore made in the VPC. Read at S2, by the
  security group's dependants after the update.
