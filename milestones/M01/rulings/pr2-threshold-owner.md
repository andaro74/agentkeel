---
# M01 PR 2 (#8), the Threshold Owner's key. Ruling B (M01 PR 1): one seat
# per ruling file. `milestones/M01/rulings/pr2.md` is Product's and carries
# the same `pr`; this file rules the fields that file names as this seat's.
ruling: pr2-threshold-owner
seat: Threshold Owner
authorises:
  - agents/refagent/manifest.yaml
  - scripts/check_model_access.py
evidence:
  - milestones/M01/feasibility.md
  - evals/history/96331342d12e16ac08781a2292923f595438fe95.json
  - https://github.com/andaro74/agentkeel/actions/runs/35529132275
pr: 8
---

# M01 PR 2 — the Threshold Owner's key

Two rulings were promised at PR 2 open and are given here: (o) the token
cap, and (p) refagent's model id and version. A third thing happened on
the way, and it is the reason (p) reads as it does.

## (p) refagent's model is Sonnet 4.6, and `version` stays null

`model.id` becomes `anthropic.claude-sonnet-4-6`, `model.profile`
`us.anthropic.claude-sonnet-4-6`, region `us-west-2` unchanged. `version`
stays null: Bedrock returns no version for this profile either.

It was `anthropic.claude-sonnet-5`, and **this account cannot call it**:

```
AccessDeniedException: anthropic.claude-sonnet-5 is not available for this account
```

fifteen times in one run, one per golden (run 35529132275, envelope
`96331342…`, UNMEASURED). The pin was made on `list-foundation-models`
reporting `modelLifecycle: ACTIVE` in us-west-2. **ACTIVE says the model
exists in the region. It does not say this account may call it**, and this
seat read the two as one. The same listing reports `us.anthropic.claude-sonnet-5`
as `ACTIVE` today, beside the refusal, so the listing was never going to
say otherwise.

**A pin is not pinned until something has called it.** From M01, this seat
pins a model only after `scripts/check_model_access.py` has called it
through the profile the manifest names, and the date and account of that
call go in the comment above the field. It is a script and not a check in
`make validate`, because it spends: a check that cost money on every
`validate` would be turned off, and a check that is turned off is not a
check.

Verified for this ruling on **2026-09-20**, account `581208540944`,
us-west-2, by `scripts/check_model_access.py`: ten of twelve pinned models
answered. Beyond the call, refagent's own path was run once against
`us.anthropic.claude-sonnet-4-6` on golden g-001 — one tool call, and the
answer cited `table_row: r-019` and `clause_id: ML-2.1`, which is the pair
the golden expects, at 3,533 tokens.

Two consequences this seat also rules, both recorded in the manifest:

- **`m04_equivalent_swap` moves** to `anthropic.claude-sonnet-4-5-20250929-v1:0`.
  It was Sonnet 4.6, which is now the model under test; an "equivalent
  swap" to the model already running measures nothing. Sonnet 4.5 answers.
- **`m04_deprecation_plant` is already refused**, and not for access:
  `ResourceNotFoundException`, "marked by provider as Legacy and you have
  not been actively using the model in the last 30 days". A deprecation
  plant that cannot be called even once cannot show a before, and M04
  cannot measure a deprecation it never saw working. M04 rules whether
  that is the plant it wants; this seat records that it does not answer
  today. `m03_judge_candidates[5]`, `openai.gpt-6-astra`, is likewise not
  available to this account, and M03 picks from the ones that answer.

## (o) the cap stays at 150,000, and it is a pre-run number

`cost_cap.tokens_per_run` does **not** move. Ruling o said it would be
re-ruled against PR 2's first agent envelope; that envelope
(`96331342…`) measured nothing, because every call was refused, so there
is no run to calibrate against yet.

This seat's own review raised the reason that matters more than the
number. Ruling m has the gate read `thresholds.yaml` **at the envelope's
commit**, so an envelope written over the cap is RED at that commit
forever — a later raise repairs nothing, and only a new run at a new
commit does. **The cap therefore has to be right before the run, not
after it.** So: 150,000 is the pre-run number, ruled now, and the re-rule
against the first measured envelope is calibration, not permission.

What the number is measured against, from the one real call above:
3,533 tokens for a two-turn golden with one tool call. Fifteen goldens is
about 53,000, plus the control at 5,534 (this run's own cost-cap line),
so about **58,500 against 150,000** — under 40%. The pathological case
this seat costed at PR 2 open, three Converse turns per golden with the
output ceiling hit each time, was about 116,000, or 77%. Both fit. A move
**up** from 150,000 would be a relaxation and would need a second key; no
such move is made here.

## What this ruling does not settle

Nothing here measures refagent. The envelope this file cites is
UNMEASURED and says so. The first measured agent envelope is the next CI
run after the model access lands, and if its `tokens_in + tokens_out`
falls outside the estimate above, this seat says so in M01's close and
names the difference.
