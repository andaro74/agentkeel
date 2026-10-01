---
# M06 PR 2 (#35), Security's key. Product's file is pr2.md.
ruling: pr2-security
seat: Security
authorises:
  - .github/workflows/platform-check.yml
  - .github/workflows/deploy.yml
  - .github/workflows/evals.yml
  - infra/workflows.sha256
  - infra/bootstrap/**
  - infra/construct/**
  - infra/security/**
  - infra/grafana/**
  - infra/ruleset/**
  - infra/platform_identity.json
  - agents/refagent/manifest.yaml
  - agents/ratings-helper/manifest.yaml
evidence:
  - SPEC/00-overview.md#8-M06
  - SPEC/06-developer-template.md
  - milestones/M06/feasibility.md
  - milestones/M06/open.md
pr: 35
---

# Ruling: M06 PR 2, Security

DRAFT for andaro74 as Security. Not ruled until this line reads "Ruled by".

## What this authorises

- **The platform check** (R2): `platform-check.yml` from `main` on a
  schedule; the agent repositories' ruleset export `infra/ruleset/agent.json`;
  `infra/platform_identity.json`, which carries verify's signer and repository
  id unchanged (moved from `src/bundle/verify.py`, finding 16) and the
  organisation `agentkeel-studio` (GitHub Free, so its repositories are
  public: a ruleset is enforced only there) and the App 5144253, made by the
  human on 2026-09-30.
- **The agent deploy** (R3): `deploy.yml`'s `find-agents`, `sign-agent` and
  `deploy-agent`, from `main`, with the platform's
  `infra/construct/agent.Dockerfile`; refagent's jobs unchanged but for its
  registry row. The deploy role's and the eval role's trust and verify's
  identity do not widen.
- **The per-agent changes** (R4, SPEC/06 §6): the registry and the ECR
  creation template (`agentkeel` namespace) in the bootstrap; each
  template agent's own key, tagged, used by its own role only, with R4's
  denies widened; runtime `agentkeel_<name>`; the role tag; the deploy
  role's grants named in its suppression; the execution role's runtimes
  narrowed to the platform's and its KMS grants held to tagged keys;
  refagent's key refusing another agent's role; logs scoped to the
  runtime's own group.
- **The security account** (`infra/security/`): `open.md` row 2, the
  stand-in's Allow removed and its two Denies kept; the tag-keyed audit
  prefix for template agents (`open.md` row 29); the read role on
  `envelopes/agents/`; `agentkeel-answer-put` for `deploy.yml` on `main`,
  under `envelopes/agents/` only.
- **Grafana** (R1): `infra/grafana/`, its roles under the deploy boundary,
  and `panel1.json`.
- **The seats** in both manifests: `andaro74`, every seat (finding 12).
- **`open.md` row 4** for every stack this PR edits: each suppression in the
  bootstrap, security and Grafana stacks names its findings (`appliesTo`);
  the construct's already did. The four NagReports are the synth's, 0
  non-compliant.

## The seat reports and what each changed

security-reviewer (0 BLOCK, 12 FINDING, 13 NOTE; read the tree at
`565dd04`, a weaker witness, each finding re-checked against the diff by
the caller) and platform-architect (1 BLOCK, 8 FINDING, 10 NOTE; read the
tree): verbatim in the PR body.

| Report, # | Status |
|---|---|
| platform-architect BLOCK 1 (no boundary on the Grafana roles) | Repaired (`6976a7d`) |
| security-reviewer F1 (a merged head is never evaluated, so never deployed) | Repaired: `find` reads default-branch heads (`1c8dba1`) |
| security-reviewer F2 (name takeover after a failed first deploy) | Repaired: the claim is a conditional write before the stack (`1c8dba1`, `6976a7d`) |
| security-reviewer F3 (one repository stops every deploy) | Repaired: `always()` on `deploy-agent`, and the image's files checked before merge |
| security-reviewer F4, platform-architect F5 (KMS grants and R4's denies) | Repaired |
| security-reviewer F5, platform-architect F2 (every agent role uses every agent's key) | Repaired, refagent's key included |
| security-reviewer F6 (who can tag a role) | Named in SPEC/06 §8; a seeded refusal is PR 3's to propose |
| security-reviewer F7 (deploy.yml could write evals.yml's envelope keys) | Repaired: `agentkeel-answer-put` |
| security-reviewer F8 (Grafana trust account-wide) | Boundary repaired; the workspace id is pinned after the workspace exists, named in SPEC/06 §8 |
| security-reviewer F9 (the Grafana token beside the PR's code) | Repaired: its own step, curl and jq only |
| security-reviewer F10, platform-architect F9 (suppressions) | Repaired: `appliesTo` and current reasons |
| security-reviewer F11 (seat logins) | Repaired (Engineering's path; `pr2-engineering.md`) |
| security-reviewer F12 (the App key's environment is unread) | Named in SPEC/06 §8 |
| platform-architect F3, F4 (logs; the execution role's `runtime/*`) | Repaired |
| platform-architect F6, F7, F8 (§8 stale or silent) | Repaired in SPEC/06 §8 (Product) |
| security-reviewer N5, N6 (Rekor every ten minutes; the App token unscoped) | Repaired: the registry is read before signing; the token is minted per repository with four permissions |
| platform-architect N13, N14, N15 (`agentkeel_` prefix unreserved; base image by tag; workspace trust) | Named in SPEC/06 §8 (N13, N15); N14 carried to M07 with refagent's own image pin |

## The post-review delta (`053dcb0...5ffc1f5`, read by security-reviewer as the diff)

Made while the human set up the platform, 2026-09-30 to 10-01: the
organisation and App ids; the connector's memory, 3008 MB (at 512 it ran
out of Metaspace on panel 1's first query); the registry's six columns as a
Glue table, `default`.`agentkeel-registry`, with `glue:GetTable` on that
table alone (with no row, the connector inferred only `name`). Panel 1's
query then returned HTTP 200 with its four fields, read with the observer's
token as `evals.yml` sends it.

| # | Status |
|---|---|
| F1 (nothing reads that an agent repository is public; GitHub Free enforces a ruleset nowhere else) | Repaired (`a22154d`): `post` refuses a private repository, `deployable` skips one; unseeded, named in SPEC/06 §8 |
| N2 (the Glue table sits in the shared `default` database; any Glue writer in the account can edit it, and CloudFormation restores it only at the next deploy) | Stands for Security's ruling: an edit can make panel 1 wrong or unread, which F6.4 reads as fired against a direct registry scan, never as held. A dedicated database would let a deny be scoped, at the cost of panel 1's query; named in SPEC/06 §8 |
| N3 (5144253 is the App's id only by the human's word) | Settled by the first `post`'s check run showing `app.id` 5144253 |
| N4 (the App key's environment) | Made 2026-10-01: `platform-app`, `main` only, the key there and not at repository level (read through the API) |
| N5 (the temporary Admin token's deletion) | The human deleted `setup-temp`; recorded in the close attestations from Grafana's list |
| N1, N6, N7, N8 | Recorded: the grant is minimal; cost only; no suppression added; the test is sound |

## What a reader can run

```
for s in bootstrap security grafana; do CDK_OUTDIR=$(mktemp -d) uv run python infra/$s/app.py; done   # 0 non-compliant each
uv run pytest tests/test_bootstrap.py tests/test_construct.py tests/test_containment_stacks.py -q
uv run python -c "from pathlib import Path; from src.validate import checks; print(checks.check_workflow_hashes(Path('.')))"   # []
```
