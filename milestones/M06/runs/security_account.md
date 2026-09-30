# The security account at M06 open (`open.md` rows 2 and 3)

Recorded at M06 PR 1. What the human did and read in the security
account (897698239547) before this PR; this file writes it down and reads
nothing. The account is M05's (`milestones/M05/runs/security_account.md`).

## Row 3: `ecsTaskExecutionRole`, deleted

Left in the account from before the cleanup of 2026-09-29, trusted by
`ecs-tasks` only and read by nothing (#31 and #32 Unsure N;
`milestones/M05/rulings/pr2-security.md` §7, platform F4). **Deleted by
the human as `hector.flores` on 2026-09-30, before M06 PR 1** (Security).

Read afterwards in the security account's CloudShell, as `hector.flores`:

```
aws iam get-role --role-name ecsTaskExecutionRole
  -> NoSuchEntity: The role with name ecsTaskExecutionRole cannot be found.

aws cloudtrail lookup-events --region us-east-1
    --lookup-attributes AttributeKey=ResourceName,AttributeValue=ecsTaskExecutionRole
  -> DetachRolePolicy  2026-09-30T13:18:06+00:00  hector.flores
  -> DeleteRole        2026-09-30T13:18:06+00:00  hector.flores
```

The two events are CloudTrail's record, in the security account's event
history (IAM is a global service; its events are recorded in us-east-1).
They are the human's paste of that record, not read by any reader in this
repository. The security account's trail is multi-region with IAM's
global events, so the same two events reach the audit bucket under
`AWSLogs/897698239547/`; no reader looks them up there.

What is left in the account that no stack of this platform makes: AWS
service-linked roles, and the four tagged leftovers named in M05's file.

## Row 2: the stand-in's Allow, ruled

`agentkeel-refagent-standin` was deleted on 2026-09-30 at 03:58:11Z
(M05's file), but the audit bucket's policy still allows its ARN a put
under `agents/refagent/standin/*`, matched by name. **Ruled by Security
at M06 open, 2026-09-30:** the Allow is removed in M06 PR 2, in one hand
deploy of `infra/security/` as `hector.flores`, after reading `cdk diff`;
the two Denies that name the stand-in stay. Until that deploy a role
recreated with that name and path in the agent account gets the grant
back, on that one prefix, where a write adds a version and modifies
nothing.

This PR touches AWS read-only and does not deploy.
