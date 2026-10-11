---
# M09 PR 1 (#49), Engineering's key over the Engineering paths this PR
# touches: the seed fixtures, SEEDS_M09, the seed tests, the ledger test's
# row count, and the fixtures README. No reader is in this PR (that is
# PR 2). The cold review runs from PR 2 (R9); this is the open ruling for
# the Engineering paths, as M08 PR 1's pr1-engineering.md was.
ruling: pr1-engineering
seat: Engineering
authorises:
  - tests/fixtures/m09/**
  - tests/test_m09_seeds.py
  - tests/test_cost_cap_and_ledger.py
  - tests/fixtures/README.md
  - src/verdict/plants.py
evidence:
  - SPEC/09-per-agent-rules.md#5-the-seeded-cases
  - milestones/M09/feasibility.md
  - milestones/M09/rulings/pr1.md
pr: 49
---

# Ruling: M09 PR 1, Engineering

**DRAFT.** Drafted by the session on 2026-10-11 for andaro74 to rule as
Engineering. It reads "Ruled by" only when the human says so.

Ruled by: *pending*.

## What this covers

The seeds and their tests, planted in one commit before any reader
(`02db54e`):

- **S1, the fixture agent** (`tests/fixtures/m09/s1-festival-desk/`): the
  template's folder as `scripts/make_template.py` wrote it at `d848ea9`
  (refagent's code, tool, prompt and full data, so M08's fixture row
  defect is not repeated), with `rules/guardrail.yaml` of its own (one
  topic, `plants: [g-030]`, `blocks` naming it; no `pii` or
  `content_filters`, which the baseline supplies), `goldens/g-030.yaml`
  (guardrail, BLOCKED) beside `g-001` and `g-010`, every seat the author,
  and the placeholder pin `fest1va1desk:1`. `src/validate/agent.evaluate()`
  **refuses it** in a worktree through M06's stand-in lookup, on the pin
  and on `g-030`'s kind: the false state. Two planted tests (admitted;
  rules read) and one guard (the format). Its goldens carry the Data
  Owner's seat and its rules file the agent's Rule Owner's; the folder is
  under `tests/**`, Engineering's, as M08's hostile copy was.
- **S2** (`s2-weakened-baseline/`): `weakened.yaml` (EMAIL to NONE, to be
  refused naming EMAIL) and `empty_pii.yaml` (`pii: []`, to merge with
  PHONE and EMAIL kept). Readers: `rules/baseline.yaml` and
  `src/validate/agent_rules.py` `merge`, `merge_errors`, neither in the
  tree.
- **S3** (`s3-silent-plant/`): three answer records (blocked by another
  rule; answered; held). Reader: `src/verdict/agent_rules.py` `plants`,
  returning `{read, held, expected, fired, reasons}`.
- **S4**: a guard, no fixture: refagent's rules whole (six topics, two
  entities, seven plants); F9.5's witness after the split.
- **S5** (`s5-unnamed-plant/`): `no_blocks.yaml` and `unbuilt_rule.yaml`,
  to be refused by `rules_errors(agent, rules=...)` naming `g-030` and
  `festival-embargo`.
- **The run file** (`milestones/M09/runs/f9_3_plant_run.yaml`, Product's
  under `milestones/**`): `observed: null`, four steps named, read by
  `scripts/observe_rules.py` after PR 2 merges.
- **`SEEDS_M09`** in `src/verdict/plants.py`: six entries, listed by
  `make plants`; `CONTROLS` unchanged.
- **`tests/test_cost_cap_and_ledger.py`**: the ledger's row count, nine
  to ten, for row 9.

`tests/test_m09_seeds.py` shows 2 passed, 7 xfailed; `--runxfail` 2
passed, 7 failed, each with its planted message (`feasibility.md` §3).
The full suite passes with the row count bumped. `git show 02db54e
--stat` shows the seeds, the tests, the README rows and `SEEDS_M09`, and
no reader.

## For PR 2 (the names this PR fixes)

`src/validate/agent_rules.py` with `load`, `merge`, `merge_errors`,
`rules_errors(agent_dir, rules=None)`; `src/verdict/agent_rules.py` with
`plants(record, blocks)` and `guardrail(record, read_back, tree_digest)`;
`scripts/observe_rules.py` (matched by CODEOWNERS' `observe_*.py` line);
`agent_rules` in `src/verdict/schema.json`; `CLAIM_9_CHECKS` and
`READ_THE_RULES` in `gate.py`; row 9's reading in `src/ledger.py`;
`guardrail_errors` and `agent_goldens.KINDS` changed as SPEC/09 §6 says;
`rules/baseline.yaml` (Rule Owner); the registry row's guardrail fields;
the builder as Security rules. The cold review (`engineering-cold-reviewer`)
runs from PR 2 (R9); its report on this PR's diff is in the PR body.

## Unsure

- Whether `plants` should also return the per-golden topics it read, so
  the ledger cell can quote them; proposed: yes, in `reasons` for a miss
  and in a `fired_by` map for a hit. Engineering, PR 2.
- Whether `rules_errors` reads Bedrock's per-topic limits itself or
  leaves them to `guardrail_spec` at synth (SPEC/09 §9 cut 5); proposed:
  itself, so a team's pull request is refused before a deploy fails.
  Engineering, PR 2.
