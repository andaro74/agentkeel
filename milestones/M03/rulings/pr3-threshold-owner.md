---
# M03 PR 3 (#21), the Threshold Owner's key. Drafted by the session from
# the threshold-owner report on this PR; for the human to rule as Threshold
# Owner. It changes no bar: `thresholds.yaml` is named because this file
# rules on its cap (Product, pr3.md ruling B: a ruling file only).
ruling: pr3-threshold-owner
seat: Threshold Owner
authorises:
  - thresholds.yaml
evidence:
  - SPEC/03-evals-regression-redteam-corpus.md
  - milestones/M03/open.md
  - milestones/M02/rulings/pr2-threshold-owner.md
  - evals/history/0225d84ee58dc34bb8a3031edcea5f07c19529ec.json
  - evals/history/0225d84ee58dc34bb8a3031edcea5f07c19529ec.baseline-card.json
  - evals/history/0225d84ee58dc34bb8a3031edcea5f07c19529ec.baseline-raw.json
pr: 21
---

# Ruling: M03 PR 3, Threshold Owner

DRAFT. For the human to rule as Threshold Owner. `milestones/M03/open.md`
row 7, dated PR 2 in `feasibility.md` §6 and not done there, done here as a
ruling file (`pr3.md` ruling B). `threshold-owner`'s report (0 BLOCK, 1
FINDING, 11 NOTE) is in the PR body; it read the tree and the envelopes.

## 1. The cap against 52,415 measured

`cost_cap.tokens_per_run` **stays 150,000**. PR 2's envelope (`0225d84`)
spent 46,991 in and 5,424 out, 52,415 tokens, both subjects: **34.9% of the
cap**. The control's share is 7,887 (its card), so refagent spent 44,528
over 20 goldens, about 2,226 each; at M02 (`8033c2a`) it spent 47,896 over
15. The guardrail blocking seven plants on the question, with no tool
call, is the likely cause; the agent's raw is not committed, so the saving
cannot be split per golden. Runner (`e97125e`, 54,156) and runtime
(`8033c2a`, 54,009) spent within 0.3% of each other, so a runtime run at the
close should not move the number much.

Neither direction is justified: up is a relaxation (ADR-0009, two keys)
with no need behind it; down is one key, and M04's knowledge base would
likely force it back up, with two. This PR's run and PR 4's are read
against the same cap; `build` and `gate` already rule an envelope over it
RED.

## 2. The control answers the retired `g-012` every run

Accepted while ADR-0002 freezes the control: 373 tokens a run (255 in, 118
out), 4.7% of the control's spend, 0.25% of the cap. It is reported and
never scored. It ends only with an amendment to ADR-0002 (Product).

## 3. One cap for two run shapes

Stands. The control is frozen (prompt, temperature 0, `maxTokens` 512), so
its spend grows only with the number of goldens: at 21 calls, at most 21 ×
(263 + 512) = 16,275, 10.8% of the cap. A bar for a control-only run would
only bound the number of goldens, which the Data Owner governs.

## 4. Next re-ruled

**M04 PR 1**, against the first envelope with retrieval (the knowledge
base, SPEC/03 cut 6), with the model swaps and A-vs-A runs, the control's
fairness (M02 §8) and `check_model_access` (`open.md` row 12). The comment
in `thresholds.yaml` that says the control is "about 6,000" and refagent
"with retrieval" is "not measured yet" is stale; it is rewritten with that
re-ruling, not here.

## 5. R10's N (the report's FINDING)

`feasibility.md` §6 row 4 dated R10's N to "PR 2, with its `relaxes:`
entry". It is not in `thresholds.yaml`, and `two_key.py` defers it ("R10's
N and M04's `delta_max` land as bars when their milestones write them").
The date slipped without a record. Nothing moves, since no N exists.
**Re-dated to M05**, where claim 5 first reads it (proposed; the human
rules), and carried in `pr3.md` Unsure E.

`delta_max`, the relative regression bar, is M04's (ruling on F11). Today
the regression bar is P7 and R2 as `judge` holds them: any regressed golden
blocks.

## What a reader can run

```
uv run python -c "import json; e=json.load(open('evals/history/0225d84ee58dc34bb8a3031edcea5f07c19529ec.json')); print(e['tokens_in']+e['tokens_out'])"                 # 52415
uv run python -c "import json; c=json.load(open('evals/history/0225d84ee58dc34bb8a3031edcea5f07c19529ec.baseline-card.json')); print(c['tokens_in']+c['tokens_out'])"  # 7887
git diff --exit-code a423292 HEAD -- thresholds.yaml                                                                                                                    # unchanged
```
