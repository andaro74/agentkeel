---
# M04 PR 2 (#24), the Threshold Owner's key. This file is also the second
# key on g-021's retirement: the Data Owner's file,
# rulings/pr2-data-owner.md, covers the path; this one names it, as at
# g-012 (M02 PR 2). Product's file is rulings/pr2.md.
ruling: pr2-threshold-owner
seat: Threshold Owner
authorises:
  - thresholds.yaml
  # pinned_roles, and the judge_model_id comment; the pin itself is unchanged
  - agents/refagent/manifest.yaml
# The second key on g-021's retirement names the path exactly (ADR-0009; src/gates Ruling.names).
keys:
  - evals/goldens/v1/g-021.yaml
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md#2-words-used-here
  - SPEC/04-model-swap.md#6-the-code-that-reads-the-answer-pr-2
  - milestones/M04/feasibility.md
  - milestones/M04/rulings/pr1-threshold-owner.md
  - milestones/M04/runs/model_access_2026-09-26.md
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
  - docs/adr/ADR-0010-the-pins-lifecycle-fields-are-the-threshold-owners.md
  - evals/history/cb06c0dbf0019088c664c6df1ce7d67cc64f7d58.json
  - evals/history/e51892775b6b36236755f0f9a94e6d98d7628206.json
pr: 24
---

# Ruling: M04 PR 2, Threshold Owner

Drafted by the session; the human rules as Threshold Owner before the
merge.

## 1. The `delta_max` bars land (`open.md` row 13; ruling 2, finding 3)

`relative.p95_ratio_max: 2.0` and `relative.agent_tokens_ratio_max:
1.5`, each `relaxes: up`, as ruled at M04 PR 1. Adding a bar is not a
relaxation (ADR-0009); `two-key` reads none here. They apply to every
agent envelope at a commit that carries them, not only to swaps
(threshold-owner F4): the incumbent is the pin at the merge-base with
`main`, its number the median of its envelopes in the same mode, the
run's side its first agent run, and no incumbent envelope in the mode is
a fail. On the counted set today the slowest runner envelope is 1.48x
the runner median, and the slowest runtime one 1.30x.

Ruled on this PR's report, by the human on 2026-09-27:

- **The ratchet (F1, your N13).** The median leaves out envelopes whose
  `checks.F4_4` failed, so a run over the bar that merged does not lift
  the next run's bar. Unless every counted envelope on the pin and mode
  failed it: a pin's first runs fail for having no incumbent, the
  envelope does not say which, and leaving them all out would leave the
  pin no median, ever. Then all are counted. No envelope in history
  carries `F4_4`, so today's medians are unchanged.
- **A deleted bar (F2).** From `15047b4`, which wired the checks, a
  `thresholds.yaml` with no `relative` is refused by `build` and
  REJECTED by the gate, as a deleted cap is. Before it, no bar, as
  before.
- **After a swap merges (note 9)**, its first envelope in a mode the
  swap never ran in fails `F4_4` for having no incumbent there, as ruled
  ("a mode the incumbent never ran in is not a way past the bar"). No
  swap merges at M04; recorded for M05's `open.md`.

## 2. The cap stays 150,000 until PR 2's own run is read (row 12)

The comment now gives the measured spend by subject. A-vs-A runs both
subjects twice on this PR's own run; a pre-read of M04 PR 1's raws
doubled came to 105,304. The cap is re-ruled against this PR's A-vs-A
envelope once it is on the branch: kept if that envelope is under it,
and a raise, two keys, only if it is not.

**Read, 2026-09-27.** PR 2's A-vs-A envelope
(`evals/history/9e4b559bf7ff8241482ed89bb350a2f6249e8c5c.json`, run
36345661354) spent 87,344 in + 10,291 out = 97,635 tokens, both
subjects twice. That is under 150,000, so by the rule above the cap is
kept: 52,365 of headroom, 65% used. `thresholds.yaml` is not changed.

## 3. `pinned_roles` carry the whole pin (row 14; F5, F8 on PR 1)

Every swap role has `version`, the suffix its id carries (null only
where an id has none, ruling G), and `region: us-west-2`, the request
region. A swap PR copies its role into `model` and decides nothing else.
Done before either swap PR is opened. The deprecation plant's open
question is answered: it is S5's pin. The judge comment says the judge is
M07's (note 13). ratings-helper's pin does not move at M04, because no
swap merges; its comment says so.

## 4. `g-021`: the second key

This file is the second seat's key on the retirement the Data Owner
rules in `pr2-data-owner.md`. The Threshold Owner's reason: a golden
that cannot pass under the correctness the Data Owner ruled is not a bar
anyone meets; retiring it lowers no bar that any run has cleared.

## 5. For the swap PRs (to be filed in this PR once they are opened)

Each swap PR's Threshold Owner ruling names its `pr:` and records the
`modelLifecycle` read on the day it is opened (threshold-owner F4,
second read on PR 1). Stated before their runs, as ruled on finding 2:
the breaking swap RED with at least one citing golden regressed, and not
UNMEASURED, over the cap or REJECTED; the equivalent swap GREEN, A-vs-A
zero diff, every required check green on its head. Neither merges.
