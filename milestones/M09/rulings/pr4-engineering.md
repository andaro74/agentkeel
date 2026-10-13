---
# M09 PR 4 (#53), the close. Engineering's key over the one Engineering
# path this PR touches: the run test's marker in tests/test_m09_seeds.py,
# first and alone, so the branch's CI envelope reads agent_rules made. The
# cold review of the close is pasted below. Product's file is pr4.md, the
# Data Owner's pr4-data-owner.md, Security's pr4-security.md.
ruling: pr4-engineering
seat: Engineering
authorises:
  - tests/test_m09_seeds.py
evidence:
  - SPEC/09-per-agent-rules.md#5-the-seeded-cases
  - evals/history/c503324bac926e4a3295ee7e7f68a98cf254bc42.json
  - https://github.com/andaro74/agentkeel/actions/runs/38400685274
  - milestones/M09/rulings/pr2-engineering.md
  - milestones/M09/rulings/pr3-engineering.md
pr: 53
---

# Ruling: M09 PR 4, Engineering

DRAFT until it reads "Ruled by". Drafted by the session 2026-10-13.

## The marker

`test_the_plant_run_was_made` in `tests/test_m09_seeds.py` loses its
`xfail(strict=True)` marker (`c503324`): the run is made, `observed` is a
mapping (`bfa4c19`), and the test passes by its reader, the run file. The
file now shows 9 passed; `--runxfail` has nothing left to show. The
`expected_failure` marker object stays defined, unused, as the other
milestones' seed files leave theirs. No other line changes. The
pre-existing unused import `SeedBroken` (ruff F401; no workflow runs ruff)
stays: no code beyond the marker in a close (finding 17).

## The envelope's provenance

The marker was committed and pushed alone, and the PR opened, before any
document was written, so the CI bot's envelope is of a tree whose only
difference from `main` is the owner's `observed` block and the marker.
`evals.yml` (run 38400685274) ran `scripts/observe_rules.py` twice, as
`agentkeel-audit-read` for the bucket and as the eval role for GitHub, the
registry and `GetGuardrail` (`made True` both times), and `build` composed
`agent_rules` from the file; the gate ruled GREEN; `record` committed
`evals/history/c503324….json` as `github-actions[bot]` (`1ebd907`). The
`checks` job's pytest passed. Nothing under `src/`, `scripts/`,
`evals/history/` (but for the bot's commit) or `infra/` is in this PR.

## Read on the envelope, by the readers PR 2 built

- `F9_1`: `source: read_back`, so R4's grant was deployed and the eval
  role read the guardrail; `digest_read == digest_expected`
  (`1245e65b…a122`). The registry fallback (SPEC/09 §9 cut 3) was not
  needed.
- `F9_2`: `refused_on` is the rules check alone; `baseline_in_guardrail:
  true` from the read-back's PII entities.
- `F9_3`: `fired_by: {g-030: [unannounced-selection-leak]}`, one topic, the
  named one; membership, not "only", and here they coincide.
- `F9_4`: `heads: {first: admitted, second: refused, third: admitted}`,
  each the platform App's run (5144253) by `_check`'s app-id hold (cold
  review F2 on PR 2).
- `gate.rules_misses` returns `[]`; `rules_reading` prints the cell's
  tail.

## Cold review

Run before the documents were asked for ruling, on the diff
`79ba804...HEAD`. The report is pasted verbatim below with its
dispositions; the counts are in the PR body.

(The report and the table are added by the session after the review
runs; a draft ruling with this section empty is not ruled.)

## What a reader can run

```
git show c503324 --stat                                  # tests/test_m09_seeds.py, one deletion
git diff c503324^ c503324                                # the marker line and nothing else
uv run pytest tests/test_m09_seeds.py -q                 # 9 passed
git log --format='%h %an' 1ebd907 -1                     # github-actions[bot]
uv run python -m src.verdict.gate evals/history/c503324bac926e4a3295ee7e7f68a98cf254bc42.json   # exit 0
git diff 79ba804...HEAD --stat -- src scripts infra .github rules evals/goldens thresholds.yaml   # empty
```

A reader changed in this PR, an envelope committed by a person, a marker
left on, or a test that passes for a reason other than the run file's
`observed` block, makes this ruling wrong.
