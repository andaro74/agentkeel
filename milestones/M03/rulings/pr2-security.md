---
# M03 PR 2 (#20, expected), Security's key. Drafted by the session from the
# security-reviewer reports in this PR; the human rules it as Security.
ruling: pr2-security
seat: Security
authorises:
  - .github/workflows/deploy.yml
  - .github/workflows/evals.yml
  - infra/workflows.sha256
  - infra/bootstrap/**
  - infra/construct/**
  - infra/ingest/**
evidence:
  - SPEC/00-overview.md#8-M03
  - SPEC/03-evals-regression-redteam-corpus.md
  - milestones/M03/rulings/pr1-security.md
  - milestones/M03/runs/stop_a_read_back_before.md
  - milestones/M03/runs/stop_a_read_back_after.md
  - milestones/M03/runs/guardrail_probes.md
  - milestones/M03/runs/f3_5_amendment.yaml
pr: 20
---

# Ruling: M03 PR 2, Security

**Draft.** The human rules it as Security. `security-reviewer` read this PR
six times (e2839f2; before stop A; 606bece; ad4ab14 and 2e93d27, with
`platform-architect`; the whole diff `d2d1e6d...5871122`: 0 BLOCK,
4 FINDING, 14 NOTE). Every report is in the PR body.

## What the human ruled and did (2026-09-25 and 26)

1. **The guardrail deny narrowed**, one key (pr1.md ruling 5): any Create,
   Update, Delete or Put on a guardrail and Get and List by name, in the
   agent boundary, the deploy boundary and the eval role; `ApplyGuardrail`
   allowed. Read back after stop A: 79 cases, 0 mismatches.
2. **The guardrail resource in the bootstrap stack** (CreateGuardrail stays
   denied to the deploy role), versions retained; the prompt-attack filter
   off (the Rule Owner's). Stop A deployed it; versions 1 to 4 exist.
3. **The rights table**: the deploy role may Scan and DeleteItem on
   `agentkeel-*-rights`; the marker parameter, put by the deploy role, read
   by the eval role; `deploy.yml` runs on `data/rights_table.json`.
4. **The ingest stack**, `AgentkeelIngest`, deployed by hand: quarantine,
   the promoter, production with Object Lock **COMPLIANCE, 1 day** (a demo
   setting; shorter or GOVERNANCE is a relaxation, one key), the record.
   Stop B deployed it from `0ee873e`; six documents promoted, seed S5 kept.
5. **The runtime's invoke conditioned on `bedrock:GuardrailIdentifier`** at
   version 4, and the runtime sends the guardrail's ARN (`72d52d1`).

## Findings on the whole diff, and where each is held

| # | Finding | Status |
|---|---|---|
| F1 | the runtime sent the bare id; the condition names the ARN | **repaired** `72d52d1`; the merge deploy's load check is still the condition's first read in AWS. If it refuses, main's runtime answers nothing and runs go to the runner or UNMEASURED; the repair is M03 PR 3 |
| F2 | version 4's `get-guardrail` description not pasted | **before the merge** (the human) |
| F3 | nothing shows the deployed stacks equal the tree | **before the merge**: `cdk diff` of AgentkeelBootstrap and AgentkeelIngest at the PR head, "no differences", pasted into `milestones/M03/runs/` |
| F4 | the promoter's open egress outside the platform VPC | **deferred to M05, by name** (SPEC/03 §8): it is not an agent and M05's per-agent egress does not cover it |
| N6 | a rights-table-only merge redeploys all; the marker is set before the load check | recorded |
| N7 | the gate and the Makefile that read F3_5 are Engineering paths | SPEC/03 §8's known gap; M05 takes the reader from `main` |
| N8 | the eval role's invoke is not conditioned on the guardrail | recorded: the plants catch a dropped guardrailConfig (F3_2), IAM does not |
| N9 | the Security parameter's description says GovernedAgent reads it; the construct reads the manifest | recorded; corrected with the next bootstrap change (a redeploy) |
| N10 | `<arn>:*` lets DRAFT and versions 1 to 3 be applied by the eval role, the agent role and the promoter; only the runtime's invoke is pinned to 4 | recorded |
| N11 | the record is write-once by code, not IAM | recorded; not R5 evidence (M05) |
| N13 | none of the ingest stack's own refusals attempted in AWS | SPEC/03 §8; no page calls them working |
| N14 | `s3:DeleteBucketPolicy` not denied; the admin can bypass | recorded; an SCP, deferred with the landing zone |
| N16 | the bootstrap template is ~46.7 KB of CloudFormation's 51.2 KB inline limit | recorded |

The earlier reports' findings are repaired or recorded in the commits named
in each report's reply in the PR body; the whole-diff report lists them.
