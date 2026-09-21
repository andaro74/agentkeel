---
# M01 PR 3 (#9), the repair PR. Ruling B: one seat per file. This file is
# Security's; `pr3-engineering.md` carries Engineering's key for `tests/**`
# and has the same `pr`. Opened early and grown as PR 3 lands its items,
# rather than written at the end: `cold-review-ruling` is red without it,
# and a check that is red for a whole PR is a check nobody reads.
ruling: pr3
seat: Security
authorises:
  - .github/workflows/evals.yml
  - infra/workflows.sha256
  - infra/ruleset/main.json
  - infra/ruleset/README.md
  - milestones/M01/rulings/pr3.md
evidence:
  - SPEC/00-overview.md#8-M01
  - milestones/M01/rulings/pr2-cold-review.md
  - https://github.com/andaro74/agentkeel/actions/runs/35555584127
pr: 9
---

# M01 PR 3 — the repair

PR 2's cold review left four BLOCKs. Three were cured inside PR 2 (M00's
precedent). **B2 was carried here**, with BLOCK F's grants, ADR-0007,
BLOCK D's wording and the first real deploy. This file grows as each lands.

## BLOCK C / B2 — a fork PR could merge with nothing run

**The defect.** `.github/workflows/evals.yml` skips the `evals` job on a
fork, because a fork gets no OIDC token and cannot measure anything. That
skip is right. What was wrong is that **GitHub counts a skipped required
check as satisfied**, and `evals` was one of only two required contexts
(`infra/ruleset/main.json`). So a fork pull request could merge into `main`
with no `make validate` and no pytest having run at all.

`security-reviewer` found it independently at PR 2 and named the half
`pr2.md`'s ruling had missed: the ruleset is what turns the skip into a
hole, not the `if:`.

**The repair.** A `checks` job that carries the half needing no credentials
— checkout, install, `make validate`, cosign, pytest. It has no `if:` on the
job or on any step, so it cannot be skipped, and it asks for
`contents: read` and nothing else, so it behaves the same on a fork as
anywhere else.

**pytest now runs twice, and that is a decision rather than an oversight.**
The copy inside `evals` carries `continue-on-error: true` so that a failing
test reaches the envelope as `checks.F0_2 = fail` (SPEC/01 §4). This copy
must do the opposite and fail the pull request. The two answer different
questions — *what did the tree measure* and *may this merge* — so neither
can be dropped for the other. About 40 seconds.

**Proved once before anything was required of it**: run 35555584127 on this
PR, job `checks`, success.

## The ruleset is not changed in this PR's first commit, and that is the point

`infra/ruleset/main.json` is an **export** — a record of what GitHub holds.
Editing it to name `checks` would make it assert a required context that
GitHub does not require, which is the prose-against-reality defect this
milestone has now caught five times.

Applying it live before the job had reported would also have been
dangerous. `bypass_actors` is `[]` and `current_user_can_bypass` is
`never`: a required context that never reports blocks every merge into
`main`, with no one able to override it.

**The order, which is a human step (R1):**

1. push, and let `checks` report green once on this pull request — done,
   run 35555584127;
2. `PUT` the context into the live ruleset;
3. re-export, so the file in the tree is a true export again.

**Splitting the job without step 2 leaves the hole exactly where it was**,
because the required context would still be the one a fork skips. Until
step 2 is done this PR has improved nothing mechanically; it has only made
the improvement available. That sentence stays here until the re-export
lands in this PR.

## What B2 does not close

- **The check can still be switched off from inside.** A PR with write
  access can edit `evals.yml` and `infra/workflows.sha256` in one commit and
  `workflow-hash` still passes. Self-disclosed in both files; M02.
- **`workflow-hash` hashes workflow text only** — not the `Makefile`, not
  `src/`, not `scripts/`. M02.
- **The envelope the required check reads is written by the PR's own code.**
  M02, as the workflow's own header says.
- **No fork PR has ever been opened against this repo.** R1 is one human.
  The exposure is zero today, which is not the same as a control that has
  fired. **M02 plants the case**; until it does, no prose here calls this
  proven.

## Still to land in PR 3

| # | Item | Seat |
|---|---|---|
| 1 | The live ruleset `PUT` and re-export (above) | Security |
| 2 | **BLOCK F**: `agentkeel-cfn-exec`'s service grants, **and** the deploy role's — `ecr:*`, `dynamodb:*Item`, `bedrock-agentcore:InvokeAgentRuntime` — then delete `deploy.yml`'s `refuse` job | Security |
| 3 | The first real deploy, and construct tenancy with it: claim 1's second half, the P3 exception named in ledger row 1 | Security |
| 4 | **ADR-0007**: the envelope's mode field, plus region and model version (`schema.json` is `additionalProperties: false`) | Product, with Threshold Owner |
| 5 | **BLOCK D**: SPEC/01 §5's wording for S8 takes the narrowing | Security |
| 6 | The two routes `tests/test_evals_workflow.py` does not cover: a step `if:` edited to never-true, and the `Makefile` losing `exit $code` | Engineering |
| 7 | `deploy.yml:198` reads `--stack-name AgentkeelBootstrap`; the deploy role's grant is `stack/agentkeel-*/*` and IAM ARN matching is case-sensitive | Security |

PR 4 must close the milestone. There is no fifth PR; if this list will not
fit, the cut is item 3, and claim 1's second half becomes a stated RED half
at the close rather than a missed one.

## What a reader can run to falsify this PR's own claims

```bash
uv sync --frozen

# The credential-free job exists, cannot be skipped, and asks for nothing.
uv run pytest tests/test_evals_workflow.py -q

# It really is unconditional: no `if:` on the job or any of its steps.
uv run python -c "
import yaml, pathlib
job = yaml.safe_load(pathlib.Path('.github/workflows/evals.yml').read_text())['jobs']['checks']
print('job if:', job.get('if'), '| permissions:', job['permissions'])
print('step ifs:', [s.get('if') for s in job['steps']])"

# The export still says what GitHub holds. Until step 2 above, `checks`
# is NOT in this list, and that is the honest state.
grep -o '"required_status_checks":\[[^]]*\]' infra/ruleset/main.json
gh api repos/andaro74/agentkeel/rulesets/23685206 \
  --jq '.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context'
```

The last two commands must agree. If they ever disagree, the export is
prose about a control rather than a record of one.
