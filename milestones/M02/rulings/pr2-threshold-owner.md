---
# M02 PR 2 (#12), the Threshold Owner's key. Product's file is
# rulings/pr2.md. This file is also the second key on g-012's retirement
# (Door 2): the Data Owner's file, rulings/pr2-data-owner.md, covers the
# path; this one names it, as ruling B (M01 PR 1) shaped two keys.
ruling: pr2-threshold-owner
seat: Threshold Owner
authorises:
  - thresholds.yaml
  # the model, max_tokens_per_session and daily_usd fields only
  - agents/ratings-helper/manifest.yaml
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#2-words-used-here
  - milestones/M02/open.md
  - evals/history/e97125e970ccfc6d044612eb006cdbdbcdb99337.json
pr: 12
---

# Ruling: M02 PR 2, Threshold Owner

Drafted by the session; the human rules as Threshold Owner before the
merge. Numbers over adjectives.

## 1. The second key on `evals/goldens/v1/g-012.yaml` (Door 2)

`g-012` is retired (`retired: M02`) and `g-021` added. A retirement is a
relaxation (SPEC/02 §2) and takes two keys. The Data Owner's file covers
the path; **this file is the second key, and its seat is distinct.** The
bar this seat holds is the regression bar: retiring the trap the frozen
control passes by luck (Finding F0.1: `traps 1/3 (g-012)` on every
control card since `m00`) takes one pass out of the control's tally and
none out of the agent's history, since history is keyed on the id and the
file stays. `g-021` never passes (P7) and is a reason for RED for nobody.

## 2. `relaxes:` on every bar (`thresholds.yaml`)

One entry per bar, read by `two-key` instead of a comment; `validate`
fails a bar without one. Five entries: `cost_cap.tokens_per_run: up` and
the four ceilings, each `up`. Adding the map moves no bar: one key.

## 3. The cap against 54,156 measured (open.md row 18)

`cost_cap.tokens_per_run` stays 150,000. The last agent envelope
(`e97125e`, M01 PR 4) spent 54,156 tokens, both subjects, 36 percent of
the cap. A move now would re-plant S1 (its patch is 150000 to 300000).
Re-ruled when refagent grows a knowledge base at M03.

## 4. `max_tokens_per_session` and `daily_usd` (row 18)

Ruled as they stand in refagent's manifest, 20,000 and 10: a session is
one golden's question, the largest observed answer is under 4,000 tokens
in, and ten dollars a day is more than a month of `evals` runs at the
measured spend. `daily_usd` keeps its name: SPEC/00 §6 names it, and the
eval role's monthly figure is Security's Budgets alarm (ruling a), a
different thing under a different seat; the manifest's comment says so.
The stub's values, 4,000 and 1, are placeholders until M07 measures a
call.

## 5. Five seed PRs, five `evals` runs (Unsure D)

Accepted. Each seed PR changes a measured path, so each spends one run:
five times about 54,000 tokens is about 270,000, against a monthly USD
300 ruled at M01 (ruling a′), of which September has spent a fraction.
The seed PRs are opened with `evals` running, so that their `checks`
context is the real one.

## 6. The platform's ceilings (`thresholds.yaml` `ceilings:`)

`concurrency 2`, `rps_per_edge 1`, `depth 2`, `fan_out 3`: SPEC/00 §6's
depth and fan-out, and refagent's M01 values for the other two, the only
tenant that has run. Both manifests sit at the bounds. Each relaxes
upward.

## 7. The stub's model fields

`agents/ratings-helper/manifest.yaml`: the same pin as refagent's, so
that M04's swap moves both or neither. Nothing calls it before M07.

## 8. `check_model_access` (row 18)

Not run in this PR: it spends against the human's credentials, and the
session runs no Bedrock call. The human runs it and commits its stdout
under `runs/` in PR 3, or rules it unneeded.

## What a reader can falsify

```
uv run python -c "import json; e=json.load(open('evals/history/e97125e970ccfc6d044612eb006cdbdbcdb99337.json')); print(e['tokens_in']+e['tokens_out'])"   # 54156
uv run pytest tests/test_validate_m02.py -k relaxes
uv run python -m src.gates.two_key --base origin/main --pr 12   # two keys found on g-012
```
