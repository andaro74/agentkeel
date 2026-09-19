M01 PR 2 of 4: **measure** (P3). Claim 1: *an unsigned or tampered bundle never loads; refagent runs inside the construct.* Opened as a **draft** right after the Security setup commit, so `sign-fixture.yml` runs on the `pull_request` event and the S2 signature is the bot's commit, before `src/bundle/` exists (`feasibility.md` §2.6, PR 2 mechanics and ruling n).

Rulings: `milestones/M01/rulings/pr2.md` and `pr2-threshold-owner.md` (written at the cold review, both `pr: 8`). Build paths cite `SPEC/00-overview.md#8-M01`. The seats' rulings for this PR are `milestones/M01/feasibility.md` §2.6: SCOPE, Security a–k, Engineering l–n, Threshold Owner o–p.

## Scope at M01, as ruled at PR 2 open

Cuts 1, 3 and 4 of SPEC/01 §10 are taken: `ratings-helper` → M02, the knowledge base over `data/corpus/` → M03, the HITL branch → M07. Gateway and Identity are declared as props of `GovernedAgent` and wired to nothing; Identity's claim is M05's, Gateway's is M02's and M07's. refagent at M01 is Sonnet 5 through `us.anthropic.claude-sonnet-5`, the rights table in DynamoDB, and `check_availability` with its strict schema, inside the construct. F1.4 reads the table and the tool.

## Step 1 — Security setup (this push)

- `infra/ruleset/main.json` re-exported: `required_status_checks` now lists `cold-review-ruling` **and** `evals` (ruling k; the human's PUT landed before the PR 1 merge). The README carries the date and both contexts.
- `.github/workflows/sign-fixture.yml` (Security, ruling n): `pull_request` on this branch's paths only, keyless `cosign sign-blob` over S1's archive bytes, the bundle written into `tests/fixtures/bundles/altered/`, committed as `github-actions[bot]`. It runs once and never signs anything that deploys.
- `infra/workflows.sha256` updated in the same push, so `validate`'s `workflow-hash` covers the new file.

The bot's signature commit and its `git show --stat` go here when it lands, with `src/bundle/` shown absent at that commit.

## Step 2 — the build

Filled in with the build push: the manifest schema and `validate`'s manifest check; `src/bundle/` pack and verify (rulings g and h); `infra/bootstrap/` (a, b, d, e, f) and `infra/construct/`; the stack-wide checks that read S3, S5 and S8; cdk-nag in `make validate`; ADR-0006 (e); refagent at M01 scope; `src/agent/run.py` (l); the Makefile writing the control card and refagent's envelope; the gate reading `thresholds.yaml` at the envelope's commit (m); `scripts/observe_attempt.py`; the item 18 probe step; `deploy.yml`.

Each seed's xfail comes off only when its test fails for the reason it was planted for, and those reasons are pasted here.

## Step 3 — the human's attempts, then the measurement

The human deploys `infra/bootstrap` with admin, points `AWS_EVAL_ROLE_ARN` at `agentkeel-evals`, and attempts S4 and S6. Each attempt's request id, timestamp and `AccessDenied` text go into `milestones/M01/runs/f1_1_laptop.yaml` and `f1_3_key_policy.yaml`; PR 2's CI run looks each id up in CloudTrail (`scripts/observe_attempt.py`) and writes `checks.F1_1` and `checks.F1_3`. A human-written file feeds no check by itself.

Row 1's measurement is the CI run on the head that is merged; earlier branch runs are recorded, not cited.

## Seat reports

Pasted verbatim at the build push: `security-reviewer`, `platform-architect` (on S3, S5 and S8), `threshold-owner`, `tool-owner`, `engineering-cold-reviewer`.

## Unsure

Filled in before the PR is undrafted. Every item names a seat and a PR.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
