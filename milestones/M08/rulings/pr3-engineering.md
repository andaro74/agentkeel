---
# M08 PR 3, Engineering's key. One tests/ change: the run1 xfail marker
# comes off, since run 1 was made at this PR. No code under src/ changed;
# the readers landed in PR 2 and the cold review's one FINDING was repaired
# inside PR 2 (64a550d). This ruling will carry the engineering-cold-reviewer
# report drafted on the final diff before the PR opens. DRAFT until the
# human rules.
#
# Product's file is rulings/pr3.md; Security's (run 2's egress rule) is
# rulings/pr3-security.md.
ruling: pr3-engineering
seat: Engineering
authorises:
  - tests/test_m08_seeds.py
evidence:
  - SPEC/00-overview.md#8-M08
  - SPEC/08-game-day-drill.md#5-the-seeded-cases
  - milestones/M08/rulings/pr2-engineering.md
pr: 47
---

# Ruling: M08 PR 3, Engineering — DRAFT

To be ruled by andaro74 as Engineering once the cold review is run.

## What this covers

- **`tests/test_m08_seeds.py`.** The xfail(strict) marker on
  `test_run1_was_made` comes off, since run 1 was made on 2026-10-05 and
  `milestones/M08/runs/drill_run1.yaml`'s `observed:` block is now filled
  (SPEC/08 §5.1). The markers on `test_run2_was_made` and
  `test_run3_was_made` stay xfail until each of those runs lands.

## What it does not do

- **No code change.** `src/verdict/drill.py`, `scripts/observe_drill.py`,
  `src/verdict/build.py`, `src/verdict/gate.py`, `src/ledger.py` and
  `src/verdict/__init__.py` are unchanged. The PR 2 cold review's one
  FINDING (dead `DRILL_RUNS`/`READERS` constants) was repaired inside
  PR 2 at `64a550d` (`rulings/pr2-engineering.md`), nothing is owed to
  PR 3.
- **No `evals/goldens/`, `thresholds.yaml`, `rules/`, `data/corpus/`,
  manifest ids or `src/baseline/` touched.** No `two-key` relaxation.

## The cold review

To be run on the final diff `228da43..HEAD` by `engineering-cold-reviewer`
before this PR opens, and pasted here. If run 2 or run 3 needs a repair
of the platform's own deploy path, PR 3 is that repair and this ruling's
`authorises` list grows to carry it; run 3 is read by PR 4's run (second
named P3 exception, SPEC/08 §5.1).

## Unsure

- **The after-answer attempts did not make it to CloudTrail as
  management events for a4, a5, a6** (run 1's finding, recorded in
  `drill_run1.yaml.observed.findings`): the sample `agent.py` the owner
  wrote places the five after-answer attempts inline, and the AgentCore
  runtime handler appears to have returned before boto3 shipped them.
  **Not a repair for PR 3** (M08 builds no control; the drill reads what
  happened). An Engineering follow-up for a hypothetical future milestone
  would move the attempts into a background thread fired before the
  handler returns; carried as a named gap in the explainer at PR 4. Seat:
  Engineering. Recorded under the M08 decision rule.
- **F8.5 fired on IAM propagation delay** (~12 s between attach at
  00:51:33Z and the first AccessDenied at 00:51:45Z, during which the
  role's ECR pulls, GetAuthorizationToken, BatchGetImage and one
  CreateLogStream were answered). A different finding than the one
  incident-responder's F2 named (the deny-all hazard); recorded in the
  run 1 YAML and in the explainer at PR 4. **Not a repair for PR 3**.
  Seat: Engineering + Security.
