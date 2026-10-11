---
# M09 PR 2 (#50), Engineering's key over the Engineering paths this PR
# touches: the two readers, the platform check's three changed readings,
# validate's new check, build, the gate, the schema, the answer record's
# schema, the ledger, the Makefile, the registry script, the observer, the
# tests and the fixtures README. The cold review (engineering-cold-reviewer)
# ran on this PR's diff before it opened (R9); its report is below.
# src/validate/agent.py's pin reading is Engineering's code under the Rule
# Owner's rule R10 (pr2-rule-owner.md).
ruling: pr2-engineering
seat: Engineering
authorises:
  - src/validate/agent_rules.py
  - src/validate/agent.py
  - src/validate/agent_goldens.py
  - src/validate/checks.py
  - src/verdict/agent_rules.py
  - src/verdict/build.py
  - src/verdict/gate.py
  - src/verdict/schema.json
  - src/verdict/answer.schema.json
  - src/verdict/__init__.py
  - src/ledger.py
  - Makefile
  - scripts/observe_rules.py
  - scripts/registry.py
  - tests/test_m09_seeds.py
  - tests/test_m09_readers.py
  - tests/test_m09_platform.py
  - tests/test_p5_disagree.py
  - tests/test_gate.py
  - tests/test_m07_readers.py
  - tests/fixtures/README.md
evidence:
  - SPEC/09-per-agent-rules.md#6-the-code-that-reads-the-answer-pr-2
  - milestones/M09/feasibility.md
  - milestones/M09/rulings/pr1-engineering.md
  - milestones/M09/rulings/pr2.md
pr: 50
---

# Ruling: M09 PR 2, Engineering

Ruled by: pending

## What this covers

The readers SPEC/09 §6 names, by the names the seed tests fixed:

- **`src/validate/agent_rules.py`**: `load`, `merge`, `merge_errors`,
  `rules_errors(agent_dir, rules=None)`, `digest`, `baseline_errors` and
  `check` (validate's twenty-first check). Add-only as SPEC/09 §2 and the
  rule-owner report's list; the thirty-topic limit refuses at the count
  naming the file that took it over (R5, this seat); Bedrock's per-topic
  limits are read here, before a deploy fails (cut 5 not taken, PR 1's
  Unsure). S1, S2 and S5 read.
- **`src/validate/agent.py`**: `guardrail_errors` admits, for an agent with
  `rules/`, a pin that is not null and not refagent's, and refuses one the
  registry does not hold when the deploy gives it (`--held-guardrail`);
  `evaluate` calls `rules_errors`. **`agent_goldens.py`**: the four kinds,
  `expected` shaped per kind, a plant named by its control (F9.4).
- **`src/verdict/agent_rules.py`**: `plants(record, blocks)` returning
  `{read, held, expected, fired, reasons, fired_by}` by the membership
  rule; `guardrail(record, read_back, tree_digest)` for F9.1 (the registry
  row stands in when the read-back is not granted, named `source:
  registry`); `heads` and `weakened` for F9.4 and F9.2; `record` for build.
  S3 read.
- **`src/verdict/build.py`**: `--rules` into `agent_rules`, recorded,
  never gated; `F9_5` joined with build's own count of refagent's plants;
  `build answer` writes each golden's observation (`stop_reason`,
  `guardrail_topics`, `parsed`: R7's shape) and the stack's pin
  (`--guardrail`), and scores an agent's plant by its own controls'
  `blocks`. **`gate.py`**: `CLAIM_9_CHECKS`, held from `M09_READERS`
  (`9d2f3a7`, named in `2608711`); `F9_5` held again to the gate's own
  count (P5); `READ_THE_RULES`, `rules_misses`, `rules_reading`;
  `measured(rules=...)`. **`ledger.py`** prints row 9's reading.
- **`scripts/observe_rules.py`**: raw records only; the digest computed
  from bytes it fetched by the merge commit and `git show` of main's
  baseline (cold review N7 on PR 1); a run file with `observed: null`
  written not made. **`scripts/registry.py`**: `write --guardrail
  --rules-digest`, `guardrail --name`.
- **Tests**: `test_m09_seeds.py` (six markers off, the run's on),
  `test_m09_readers.py`, `test_m09_platform.py`, five P5 cases, the
  required-checks list and the check count in two older tests.

`tests/test_m09_seeds.py`: 8 passed, 1 xfailed; `--runxfail` 8 passed, 1
failed (the run not made). The full suite passes on the committed tree.
`make validate` twenty-one ok; `make ledger` exit 0 and row 9's reading of
the latest envelope RED on `agent_rules not read`.

## Unsure, for this seat

- The M02 seed test (`test_s1_one_key_on_a_relaxation_is_refused`) diffs
  the working tree against a worktree of HEAD, so it fails locally while
  seat-owned files are uncommitted and passes on the committed tree; CI
  checks out a commit. Not changed here.
- `plants` returns `fired_by` (the topics read per hit) as PR 1's
  Engineering Unsure proposed; the reasons carry the miss. The cell quotes
  neither at M09: `rules_reading` prints n of m and each falsifier's state.

## Cold review

The `engineering-cold-reviewer` report, verbatim, with each finding's
disposition, is in the section below.
