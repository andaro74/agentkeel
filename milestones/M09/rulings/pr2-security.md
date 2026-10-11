---
# M09 PR 2 (#50), Security's key over the Security paths this PR touches:
# the construct and its app, the bootstrap stack and its regenerated
# NagReport, the construct's regenerated NagReport, deploy.yml, evals.yml
# and infra/workflows.sha256. The two rulings SPEC/09 §11 puts to this seat
# before PR 2: R3 (which role builds a guardrail for a new agent) and R4
# (the observer's read-back). Product's file is rulings/pr2.md; the Rule
# Owner's is pr2-rule-owner.md; Engineering's (with the cold review) is
# pr2-engineering.md.
ruling: pr2-security
seat: Security
authorises:
  - .github/workflows/deploy.yml
  - .github/workflows/evals.yml
  - infra/bootstrap/app.py
  - infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv
  - infra/construct/governed_agent.py
  - infra/construct/app.py
  - infra/construct/AwsSolutions--AgentkeelRefagent-NagReport.csv
  - infra/workflows.sha256
evidence:
  - SPEC/00-overview.md#8-M09
  - SPEC/09-per-agent-rules.md
  - milestones/M09/README.md
  - milestones/M09/feasibility.md
  - docs/adr/ADR-0014-per-agent-rules-on-a-platform-baseline.md
pr: 50
---

# Ruling: M09 PR 2, Security

Ruled by: pending

## R3. The construct builds an agent's guardrail in the agent's own stack

For an agent whose repository carries `rules/guardrail.yaml`,
`infra/construct/governed_agent.py` builds one Bedrock Guardrail,
`agentkeel-<name>`, from the agent's rules merged onto
`rules/baseline.yaml` at synth (the platform check's own merge,
`src/validate/agent_rules.py`; a file it would refuse is refused at synth),
tagged `agentkeel:agent=<name>`, with a numbered version whose description
carries the digest of the baseline and the agent's files, retained. The
role's invoke and the runtime's converse are conditioned on **the stack's
own resource** (`bedrock:GuardrailIdentifier` is the built ARN at the built
version; `AGENTKEEL_GUARDRAIL_ARN` is the built ARN), and the manifest's
pin is read only to refuse null and refagent's. The bootstrap keeps
refagent's guardrail, untagged. An agent without `rules/` is as at M06.

**The deploy plane's deny, narrowed** (`infra/bootstrap/app.py`,
`agentkeel-deploy-boundary`): every guardrail action but Apply and List
was denied outright since M03 PR 2. It is now denied on a guardrail that
is not tagged as an agent's own, read as both `aws:RequestTag/agentkeel:agent`
and `aws:ResourceTag/agentkeel:agent` null: a create with the tag in the
request passes, every action on a guardrail carrying the tag passes, and
refagent's and any other guardrail in the shared account stay out of
reach. `ListGuardrails` stays denied outright. The verbs stay patterns.
The execution role gains two statements: `CreateGuardrail` and
`TagResource` held to a tagged request; Get, Update, Delete,
CreateGuardrailVersion, the tags and `ListTagsForResource` held to a tagged
resource. The agent plane's deny is unchanged: no agent role may touch any
guardrail but Apply.

**The deploy writes the registry row** (`deploy.yml` `deploy-agent`): the
stack's `GuardrailId`, `GuardrailVersion` and `GuardrailDigest` outputs go
to `build answer` (`--guardrail`, so the answer record names the guardrail
the call carried) and to `scripts/registry.py write`. Before the stack is
touched, the platform check runs once more with the pin the row holds
(`--held-guardrail`), so a head whose manifest pins anything but the built
guardrail is refused and a placeholder is admitted only while the row holds
none (the placeholder's life, with R10). The check's own job
(`platform-check.yml`) holds no AWS credential and cannot read the row:
that refusal fires at the deploy, after a merge, not at the check. Stated
under Unsure.

**Nothing new runs.** The deploy role's trust, the eval role's and
`verify`'s identity are unchanged; no agent repository can assume or sign
anything. The first deploy of an agent with `rules/` is PR 3's run.

## R4. The observer's role may read a built guardrail back

The eval role gains `bedrock:GetGuardrail` on a guardrail tagged as an
agent's own (`Null aws:ResourceTag/agentkeel:agent: false`), read only;
its deny on `GetGuardrail` is kept for an untagged one (refagent's), and
its other guardrail denies are unchanged. `scripts/observe_rules.py` reads
the version's description, the topic names and the PII entities as the
eval role, in `evals.yml`'s eval-role block. Until the stack is deployed
the read is refused and written as such, and F9.1 reads the registry row's
digest instead (SPEC/09 §9 cut 3), named `source: registry` on the
envelope.

## What this PR does not do

- **No grant is deployed by it.** The bootstrap stack is deployed by hand
  (this seat, `infra/bootstrap/README.md`), a by-hand step before PR 3's
  run (`milestones/M09/README.md`). Until then: the execution role is
  refused on `CreateGuardrail` at the first deploy of an agent with
  `rules/` (a PR 3 repair, not a finding of the claim), and the read-back
  is refused.
- No bucket policy, key policy, security group, VPC or trust policy
  changes. `agentkeel-audit-read` already reads `envelopes/agents/*`.
- `evals.yml` gains two steps and one Makefile variable; both observer
  steps never fail the job. `infra/workflows.sha256` recomputed for
  `evals.yml` and `deploy.yml`.
- cdk-nag: both committed reports regenerated and held by `validate`; the
  new rows are the execution role's and the eval role's `guardrail/*`,
  each with its reason naming SPEC/01 §6 and the tag that holds it.

## Unsure, for this seat

- Whether Bedrock evaluates `aws:RequestTag` on `CreateGuardrail` and
  `aws:ResourceTag` on the other guardrail actions as the IAM reference
  lists them. The build follows the reference; the first deploy of the
  fixture agent (PR 3's run) is the reading. If the create is refused on
  the condition, the fallback is the deny narrowed by resource ARN after
  the create, or the bootstrap alternative R3 named.
- The placeholder's refusal fires at the deploy, not at the check (above).

## The KMS keys from M08

`ce2d6f46` and `fcd9e973` (`milestones/M08/open.md` row 6, tagged
owner-check, scheduled for deletion 2026-10-09) read as gone by andaro74
in the KMS console, agent account, us-west-2, on 2026-10-11. Noted here;
no file in the repository reads it.

## What a reader can run

```
uv run pytest tests/test_m09_platform.py tests/test_bootstrap.py tests/test_construct.py -q   # the builder, the grants, the denies
make validate                                                                                   # cdk-nag, every stack: ok, reports equal
git diff 460990b...HEAD --stat -- .github/workflows infra                                       # this key's paths and nothing else under them
```
