---
# M03 PR 3 (#21), Engineering's key and the cold review, one file. The
# cold review was drafted by engineering-cold-reviewer from the diff
# a423292...62e7980 and row 3 only; its report is in the PR body verbatim.
# Drafted by the session; for the human to rule as Engineering.
ruling: pr3-engineering
seat: Engineering
authorises:
  - src/verdict/build.py
  - src/validate/controls.py
  - src/gates/two_key.py
  - scripts/probe_guardrail.py
  - scripts/try_guardrail_wording.py
  - tests/**
evidence:
  - SPEC/00-overview.md#8-M03
  - SPEC/03-evals-regression-redteam-corpus.md
  - milestones/README.md
  - milestones/M03/rulings/pr2-engineering.md
pr: 21
---

# Ruling: M03 PR 3, Engineering, with the cold review

DRAFT. For the human to rule as Engineering.

## The cold review

`engineering-cold-reviewer` read `git diff a423292...62e7980` (19 files, 11
commits) and row 3, not the PR body or the commit bodies, and ran pytest
(528 passed, 1 skipped, 1 failed: `test_m02_seeds.py::test_s1_one_key...`,
on the human's untracked `before.md` and `after.md`, which that test's copy
of the tree picks up; it passes with them moved aside), `make validate`
(15 of 15), `make ledger` (exit 0) and `make plants`: **0 BLOCK, 1 FINDING,
6 NOTE**. Its shape check: one repair (Unsure C) and the two redeploys it
forced; no Measured cell, tag, explainer or attestation; `src/baseline/`,
`evals/history/`, `evals/goldens/`, `data/`, `thresholds.yaml` and
`.github/` untouched. P5 holds: no new writer of envelopes, `gate.py`
unchanged, `blocks_at` read by `build` alone. The repairs after `62e7980`
are their own commits; the diff the reviewer read is unchanged beneath
them.

| # | Finding | Status |
|---|---|---|
| F1 | `g-015: null` unnamed the plant: `two-key` compared `blocks` values string to string, `controls.check` keys only, `score_one` skips a None rule; only the synth refused it | **repaired** `88577a5`: `two-key` reads any change to a `blocks` value; `validate` requires each value to name a rule; `build` refuses it (exit 3). Tests for each |
| N1 | the comment at `build`'s call named `redteam.yaml` alone | **repaired** `88577a5` |
| N2 | `blocks_at` returned `{}` for a control with no `blocks`; a list raised AttributeError | the list **repaired** `88577a5` (refused); a missing `blocks` is `validate`'s refusal (`f735f29`) and `two-key`'s (entry removed), not `build`'s: recorded |
| N3 | "dropping the rule now silences `g-015`" is witnessed by a unit test and the admin probe | recorded: the first envelope scoring it under version 5 is this PR's run; PR 4 cites the envelope, not the sentence |
| N4 | "clean checkout" with untracked files present | **repaired** `e88259c` |
| N5 | the guardrail version is the digest of both rule files, comments included; nothing mechanical compares the pin's digest with the tree | recorded (predates this PR); `pr3-rule-owner.md` F4 |
| N6 | no PR 3 ruling files | these five files |

## Engineering's paths

`build.blocks_at` reads every control's `blocks` at the commit and refuses
a clash or a `blocks` that names no rule (`c5ff91e`, `88577a5`);
`validate`'s controls check requires `blocks` in every control, its keys
the control's `plants` and each value a rule (`f735f29`, `88577a5`);
`two_key` reads any change to a `blocks` value as a relaxation
(`88577a5`); the probe and the wording trial read both controls and refuse
a clash (`c5ff91e`, `f735f29`); tests for each, and the bootstrap tests
for Security's synth check (`d02be78`).

## What a reader can run

```
git diff --stat a423292...HEAD                 # nothing under src/baseline, evals/, data/, thresholds.yaml, .github
uv run pytest -q                               # with no untracked files in the repo root
uv run pytest tests/test_build.py tests/test_validate_controls.py tests/test_gates.py -k "blocks or named or entry_5" -v
make validate && make ledger && make plants
uv run python -c "from src.verdict import build; print(build.blocks_at('HEAD'))"               # g-013, g-015 named
uv run python -c "from src.verdict import build; print('g-015' in build.blocks_at('a423292'))"  # False
```
