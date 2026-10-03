---
# M07 PR 4 (#44), the close, Security's key. Three changes to live IAM
# were deployed by hand from this pull request's branch BEFORE this file
# existed. It names them and rules each after the fact. It makes no grant.
ruling: pr4-security
seat: Security
authorises:
  - .github/workflows/platform-check.yml
  - infra/workflows.sha256
  - infra/bootstrap/app.py
  - infra/bootstrap/README.md
  - infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv
  - infra/security/app.py
  - scripts/platform_check.py
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - docs/adr/ADR-0012-the-reader-of-the-apps-grant-is-securitys.md
  - milestones/M07/rulings/pr2-security.md
  - milestones/M07/rulings/pr3-security.md
  - milestones/M07/runs/pr2_by_hand.md
  - milestones/M07/runs/b2_cdk_diff.md
  - milestones/M07/runs/pr4_expected.md
  - milestones/M07/runs/f7_2_removed_and_kept.md
  - https://github.com/andaro74/agentkeel/actions/runs/37066321605
  - https://github.com/andaro74/agentkeel/actions/runs/37074759767
  - https://github.com/andaro74/agentkeel/actions/runs/37077850271
  - https://github.com/andaro74/agentkeel/actions/runs/37119509159
  - https://github.com/andaro74/agentkeel/actions/runs/37123531195
  - https://github.com/andaro74/agentkeel/actions/runs/37123843294
  - https://github.com/andaro74/agentkeel/actions/runs/37149475766
  - evals/history/dee74c3cf4102bfb6d4315faafb161c154618ed9.json
pr: 44
---

# Ruling: M07 PR 4, Security

Ruled by andaro74 as Security, 2026-10-03, as written.

Dates and times are UTC. Each item is a recommendation with its
alternative. The seat rules it by the line above; a different ruling on
an item is written beside it.

## 1. Three deploys were made before this ruling, from an unmerged branch

`runs/pr2_by_hand.md` opens: "no stack is deployed from a commit whose
Security ruling still reads DRAFT". That did not hold at PR 4. No ruling
file for PR 4 existed when these were made (cold review B1,
platform-architect B1, security-reviewer F4 on this pull request):

| Stack | Commit, on `m07-pr4` | Deployed | By | What it changed | On what word |
|---|---|---|---|---|---|
| `AgentkeelBootstrap` (agent account) | `7a9032d` | 2026-10-02 22:49:50 | andaro74, as the account's admin user | the execution role's new statement with `CreateAgentRuntimeEndpoint` on `runtime/*`; and, owed since PR 2 and PR 3, the eval role's three reads, the roles `agentkeel-model-watch` and `agentkeel-envelope-row-put`, the table `agentkeel-envelopes`, refagent's key policy with two more principals in its Deny | "go ahead with your recommendation", to the session |
| `AgentkeelBootstrap` | `81508ab` | 2026-10-02 23:16:52 | the same | `TagResource` added to that statement, and its Sid renamed | "go" |
| `AgentkeelSecurity` (security account) | `e68ec46` | 2026-10-03 12:15:47 | `hector.flores`, in the console | `agentkeel-observation-put`'s trust: `sub` from the ref's to the environment's | "yes on 1" |

Each followed a failure a live attempt had just met, and each was said
to the session as a go-ahead, which is not a ruling file. The first
deploy's `cdk diff` was read by the human and not kept (the session's
command lost it). The first deploy carried refagent's key policy change,
made as the admin user and not the deploy role. A session synthesised
the template `hector.flores` uploaded.

**Recommended, for each of the three: keep as deployed.** The first two
are what let any agent from the template get a runtime; the third is
what let the observer put at all. Reverting any of them breaks the path
that the close's run reads. **Alternative:** narrow the first two now
(item 2); it costs a create that may be refused, with no pull request
left to repair it.

## 2. The execution role: two actions on `runtime/*`

`WhatCreateAgentRuntimeChecksOnTheRuntimeItHasNotNamedYet`:
`bedrock-agentcore:CreateAgentRuntimeEndpoint` and
`bedrock-agentcore:TagResource` on `runtime/*`, no condition.
`CreateAgentRuntime` checks both against a runtime with no id, one at a
time; runs 37066321605 and 37074759767 were refused without them, and
with both the third create passed (37077850271), then `window-check`'s
(37087860298).

What it reaches (security-reviewer N9): only CloudFormation assumes the
role, and only `deploy.yml` on `main` passes it. On a runtime that is not
the platform's, in this shared account, it could add an endpoint and set
tags. It cannot update, delete or untag: those stay on the two prefixes,
in the template. No create and no refusal has shown the prefixes hold
(platform-architect F2): that is a reading of the synth.

Two narrower forms were found by the reviews and not tried
(security-reviewer F1, F2; platform-architect F1): the Resource
`runtime/${*}`, IAM's literal asterisk; and `aws:TagKeys` held to
`aws:cloudformation:*` on `TagResource`. **Recommended: carried to M08**
(`milestones/M08/open.md` row 5), tried with `simulate-custom-policy`
and one throwaway create, under the rule now in
`infra/bootstrap/README.md`. **Alternative:** in this pull request,
before the merge; a miss leaves a rolled-back stack and a red close's
run.

The cdk-nag reason for the execution role's wildcards now names these
two actions and says they reach every runtime in the account
(security-reviewer F3, platform-architect F5, cold review F8). That
changes `Metadata` in the template: **the stack is not redeployed for
it**, so the stored reason is the old text until the next bootstrap
deploy (`runs/b2_cdk_diff.md`, last section).

## 3. The observer's put role trusts the environment's subject

`agentkeel-observation-put`: `sub` is
`repo:andaro74@3157440/agentkeel@1376369685:environment:platform-observer`;
`job_workflow_ref` exact, `observe.yml@refs/heads/main`, as before.
Fifteen keyed runs were refused under the old subject (37094837939 to
37119509159); 37123531195 assumed the role and made the first put.

It is not wider in who can assume it (security-reviewer N1,
platform-architect N1). What changed in kind: "main only" was two token
claims and is now one claim and one GitHub setting, the environment's
branch policy, which a repository admin can change with no gate and
which the grant's reader reads back on each keyed run. **It has one
positive case and no refusal** (N2, F10): nothing here may say the role
refuses a branch as an observed fact. **Recommended: as deployed**, with
a third condition on the token's `ref` claim tried at M08 (row 10).

## 4. Item 13n: the seeded relaxation's input and step are removed

`platform-check.yml` has no dispatch input and no `relax` step;
`infra/workflows.sha256` is regenerated; a test holds it. `relax_seed()`
and its `relax` subcommand stay in `scripts/platform_check.py`, with no
caller, held by the tests of their refusals; the key they need is in
`platform-app` alone. **Until this pull request merges, `main` still
carries the input**, and nothing on `main` records that the attempt was
made: a second dispatch would be accepted by GitHub again
(security-reviewer F7). **Recommended: as written; the function removed
or kept is M08's** (row 8).

## 5. What the relaxation showed about the grant

GitHub accepted the App's call (200) and the ruleset required no
platform check for 7 min 21 s, until the owner restored it by hand
(run 37123843294; `runs/pr4_expected.md` attempt 3). The grant block is
accurate: `agentkeel-platform` holds Administration: write on every
repository of the organisation, and that is the power to remove the rule
that requires its own check. It cannot drop to read: M06 showed read
does not return `bypass_actors`, and the observer App, which holds read,
does not see the field either (security-reviewer F8; the two sentences
that said otherwise are corrected in SPEC/07 §12 and the README).
**Detection, not refusal; no document may say the App cannot relax a
ruleset.** Detection needed a new head and the restore was manual (N4).
`milestones/M08/open.md` rows 8 and 9.

## 6. The retirement, and what it kept

The first retirement deleted the runtime with no IAM refusal
(`DeleteAgentRuntime`, 14:30:44, as `agentkeel-cfn-exec`). The stack
keeps the agent's role, key, table, inference profile and security
group, as designed; **two network interfaces were still in use behind
that group four and a half hours later**, and the kept role's trust
names the AgentCore service with no source condition
(platform-architect F8, F9). **Recommended: carried to M08** (row 7).

## 7. For a deploy by hand, from M08 (security-reviewer N7, N8; platform-architect N2)

- It waits for a ruling file that reads "Ruled by", or the file that
  records it says in its first line that it did not.
- The diff is read from the commit that is deployed, and its whole
  output kept (`2>&1`). `--require-approval never` is used only after
  that read.
- Each hand step and each session read names its principal
  (`aws sts get-caller-identity`).

## 8. Still owed, by hand

- The stored template of `AgentkeelSecurity`, hashed by `hector.flores`
  (`runs/pr2_by_hand.md`, "Still owed"; security-reviewer F6,
  platform-architect F7). Owed for the first B1 deploy since PR 3.
- A read that the two orphan keys are gone after 2026-10-09
  (`milestones/M08/open.md` row 6).
- The Grafana observer token, before 2026-10-31 (row 27).

## 9. The reviews of `origin/main...b310735`, and what was done

**security-reviewer: BLOCK 0, FINDING 8, NOTE 11.**

| # | Finding | Status |
|---|---|---|
| F1, F2 | `runtime/*` wider than the string refused; no condition tried | **Carried**: item 2; M08 row 5. Said in the code's comment and the bootstrap README |
| F3 | The cdk-nag reason contradicts what it suppresses | **Repaired** (`e0345b0`); NagReport regenerated |
| F4 | A ruling cited that is not in the tree; deploys before it | **Repaired**: this file, item 1; the four sentences no longer say "ruled" |
| F5 | Two stale rows in the by-hand table | **Repaired** (`b81dced`) |
| F6 | The security account's deploy on the human's word; the stored hash missing | **Open**: item 8; the command and the expected hash are in the by-hand file |
| F7 | The relaxation can be dispatched again | **Repaired for `main` after the merge**: item 4. Open until the merge |
| F8 | Who sees `bypass_actors` | **Repaired**: the two sentences were wrong and are corrected; item 5 |
| N1, N2 | The environment subject; no negative case | Item 3; the docstring says it |
| N3, N4 | What the accepted call means; detection needed a head | Item 5; M08 row 8 |
| N5 | Identifiers committed: an account id, two key ids of keys pending deletion, four secret names, a template hash | Accepted as committed; no secret among them |
| N6 | The observer App held two write permissions for under an hour | Whether its key existed in that hour is not recorded. Its id was not on `main` then, so no keyed job could use it |
| N7, N8 | Approval switched off; the first diff not kept | Item 7 |
| N9, N10, N11 | Reach; nothing else changed; the trust test | Need nothing |

**platform-architect: BLOCK 1, FINDING 10, NOTE 7.**

| # | Finding | Status |
|---|---|---|
| B1 | The ruling three files cite is not in the tree; the account changed before it | **Repaired**: this file exists and says so (item 1). It is ruled by the line above, not by this table |
| F1 | A narrower form not read | **Carried**: item 2; M08 row 5 |
| F2 | The runtime statements have no create seed | **Repaired as a rule**, in `infra/bootstrap/README.md`: one throwaway create after any change to them. Nothing holds the rule but the sentence (M08 row 4) |
| F3 | No runbook for a failed create | **Repaired**: the steps are in `infra/bootstrap/README.md`. Who cleans up: M08 row 6 |
| F4 | Keys written as "gone" | **Repaired**: "scheduled for deletion" in the four places; a row per key in the by-hand file, from CloudTrail |
| F5 | The cdk-nag reason | **Repaired**, as security-reviewer F3 |
| F6 | The checklist contradicts itself; the bootstrap README stale | **Repaired** (`e0345b0`, `b81dced`) |
| F7 | Template hashes owed | **Part**: B2's comparison is a script with both hashes (`runs/b2_cdk_diff.md`). The security account's: item 8 |
| F8 | Three reads owed at the retirement | **Made late**, 2026-10-03T19:05; one is a finding (item 6) |
| F9 | The retired agent's kept role | **Carried**: M08 row 7 |
| F10 | "Held twice" has no seeded refusal | **Said** in the docstring and item 3; M08 row 10 |
| N1 to N7 | The trust not wider; two synths; the rollback is the agent's bytes; the sign in the source; boundaries; the admin user as the default profile; where key rules are enforced | N2, N4: M08 row 13. N6: item 7. The rest need nothing |
| Deferred items 1 to 7 | An account of the platform's own; control of the admin; a deploy path into the security account; other tenants' resources; the OIDC providers; key lifecycle; alerting on admin use | Landing zone, SPEC/00 §12; `milestones/M08/open.md` row 62 |

## To falsify

```
git diff origin/main...HEAD -- infra/ .github/ scripts/platform_check.py     # three changes and 13n, nothing else
uv run pytest -q tests/test_bootstrap.py tests/test_containment_stacks.py tests/test_m07_workflows.py
aws iam get-role-policy --role-name agentkeel-cfn-exec --policy-name <its default policy> \
  --query 'PolicyDocument.Statement[?Sid==`WhatCreateAgentRuntimeChecksOnTheRuntimeItHasNotNamedYet`]'
gh run view 37123531195 --json jobs --jq '.jobs[].steps[]|select(.name|test("Put the observation"))|.conclusion'
gh api repos/andaro74/agentkeel/contents/.github/workflows/platform-check.yml --jq .content | base64 -d | grep -c relax_seed   # 0 once this merges
```

If the deployed statement carries a third action, if a run assumed the
observer's put role from anything but `observe.yml` on `main`, or if a
relaxation was dispatched a second time, this ruling is wrong.
