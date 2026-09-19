# M00 — Baseline and ledger

## Model ids (Threshold Owner; region us-west-2 for everything; resolved 2026-09-18)

| Role | Model id | Pinned id | Status | Reason |
|---|---|---|---|---|
| baseline, frozen (M00) | `amazon.nova-micro-v1:0` | `us.amazon.nova-micro-v1:0` | ACTIVE; INFERENCE_PROFILE only | cheapest Amazon text model; the control is meant to lose. INFERENCE_PROFILE only; ON_DEMAND is not a requirement anywhere in SPEC/00. |
| refagent, model under test (M01) | `anthropic.claude-sonnet-5` | `us.anthropic.claude-sonnet-5` | ACTIVE | current Sonnet class, strongest tool discipline at reasonable cost; Opus and Fable exceed the task |
| M04 equivalent swap / cheaper swap | `anthropic.claude-sonnet-4-6` / `anthropic.claude-haiku-4-5-20251001-v1:0` | `us.anthropic.claude-sonnet-4-6` / `us.anthropic.claude-haiku-4-5-20251001-v1:0` | ACTIVE / ACTIVE | both recorded; M04 rules which runs |
| M04 deprecation plant | `anthropic.claude-sonnet-4-20250514-v1:0` | `us.anthropic.claude-sonnet-4-20250514-v1:0` | model LEGACY; profile ACTIVE | already LEGACY, so model-watch must flag it with no mock |
| M04 known-breaking swap | `meta.llama3-1-8b-instruct-v1:0` | `us.meta.llama3-1-8b-instruct-v1:0` | ACTIVE; ON_DEMAND and profile | smallest ACTIVE Meta or Mistral model that supports Converse tool use, so the break is a schema break, not a missing feature. Not Mistral 7B: a failure for a missing feature is not the RED M04 wants. |
| M03 judge candidates (pick at M03 PR 1 by scoring the graded-examples set, R6) | `meta.llama4-maverick-17b-instruct-v1:0`; `meta.llama3-3-70b-instruct-v1:0`; `mistral.mistral-large-2407-v1:0`; `openai.gpt-oss-120b-1:0`; `openai.gpt-6-astra`; `amazon.nova-pro-v1:0` | `us.meta.llama4-maverick-17b-instruct-v1:0`; `us.meta.llama3-3-70b-instruct-v1:0`; `mistral.mistral-large-2407-v1:0` (no profile; ON_DEMAND); `openai.gpt-oss-120b-1:0` (no profile; ON_DEMAND); `us.openai.gpt-6-astra`; `us.amazon.nova-pro-v1:0` | all ACTIVE | strongest ACTIVE non-Anthropic models from providers a studio would already have approved. Six candidates; a studio would have Amazon approved by default. `gpt-6-astra` is the one closed-weight entry: the listing's only GPT-6-generation model; the GPT-5.6 variants (sol, terra, luna) are the prior generation and the listing does not rank them. Nova Pro is the Amazon entry after Nova Premier was found end-of-life. |

From M01, if refagent fails a trap, fix the trap or the prompt, not the
model. This does not apply to the baseline: if the baseline passes a
trap, that is Finding F0.1; record it and change nothing in this
milestone.

## Findings

- **Profile status is not model status.** On 2026-09-18
  `list-inference-profiles` reported `us.amazon.nova-premier-v1:0` as
  ACTIVE while `get-foundation-model amazon.nova-premier-v1:0` returned
  end-of-life. The same held for Llama 3.2 1B and 3B. `model-watch` must
  read `modelLifecycle` from `list-foundation-models`, never
  `inferenceProfileSummaries.status`. Carry this sentence to SPEC/04 at
  M04 open.
- No Meta 405B-class model exists in us-west-2; Llama 3.3 70B is the
  largest Llama and stands as the Meta candidate.
- Present in the region but not recorded as judge candidates by ruling:
  OpenAI gpt-5.6 sol, terra and luna; xAI grok-4.6; Moonshot kimi-k3;
  DeepSeek R1.

## Ledger row

Written at M00 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 0 |
|---|---|
| Claim | Every later number is a delta against a frozen naive baseline |
| Falsifiers | F0.2 an envelope validates without a baseline ref. F0.3 a PR merges without a ruling file after PR 2. |
| Finding, not a falsifier | F0.1 baseline passes a trap (record, do not tighten in this milestone; ADR-0003). Recorded at open: `g-012` on the plant. F0.4 the control is non-deterministic at temperature 0 (ADR-0004, PR 2; feasibility.md §6.5). |
| Seeded commit | `22b5499` on `m00-pr1`: the plant. Goldens `g-001` to `g-015`, `data/` and the baseline code are from `8a31e8d`; the baseline prompt is as revised once in `22b5499`. |
| Expected gate output | Baseline card written; `score` and `cites` recorded per golden; traps expected 1/3 on the plant, F0.1 recorded as a finding. A 0/3 or 2/3 in PR 2's CI run is a non-determinism finding to record. `g-013` to `g-015` fail and land in `never_passed`; `plants_expected = 0` under the plant rule. A run without a baseline card is rejected by `verdict.build`. From ADR-0004 (PR 2): every result is `scope: control`, so `regressed` is 0 by construction and `checks.F0_2`, `checks.F0_3` decide the verdict. |
| Measured | control: traps 1/3 (g-012); ordinary 0/9; guardrail 0/3; never_passed 14; regressed 0; plants 0/0; F0_2 pass; F0_3 pass; GREEN; envelope `9407615dcde09308490f6699c21a18100bfedcd2`. Both check URLs are in the cell in `milestones/README.md`, which is the one `make ledger` reads. |
| PRs used / cap | 3 / 4 |
| State | GREEN |

### Open detail (PR 1, 2026-09-18)

- Feasibility note: `milestones/M00/feasibility.md`. The
  `product-spec-reviewer` report in it has 2 BLOCK, 17 FINDING, 9 NOTE.
  Both BLOCKs were ruled before the PR opened (feasibility.md §2): the
  Data Owner split scoring into `score` (answer fields; Finding F0.1 is
  read on it) and `cites` (row and clause exist; gates from M01); Product gave
  seats to the unlisted paths by ADR-0001 amendment 2.
- Planted: three traps (`g-010` holdback did not move with the theatrical
  date, `g-011` non-exclusive licence, `g-012` sequel does not inherit),
  three guardrail goldens (`g-013` to `g-015`) with no guardrail to
  enforce them, and the baseline, which is expected to lose.
- Not planted: the run without a baseline card. It needs the card format,
  which is `src/verdict/` in PR 2. PR 2 plants it before `build.py`.
- Baseline parameters, stated here because nothing else pins them:
  `us.amazon.nova-micro-v1:0`, us-west-2, Converse, temperature 0,
  `maxTokens` 512, one system prompt (`src/baseline/prompt.txt`), no
  tools, no guardrail, no retrieval. Threshold Owner confirms or changes
  them before tag `m00`; after the tag they are frozen with the code.
- The prompt was revised once in this PR, by ruling of the Threshold
  Owner and Product: the first prompt made the baseline a near-constant
  responder (0/15, eight identical replies). The revision asks the plain
  question for three fields. No further revision is permitted; if it
  collapses again it is frozen as is.
- PR 1 local runs (not evidence): both are in feasibility.md §6 with
  their commit hashes. Run 1 is the finding, run 2 is the plant.
- **Finding F0.1, recorded at open**: on run 2 the baseline passed trap
  `g-012` on `score` at `22b5499` (traps 1/3, ordinary 1/9). Work
  stopped and the seats ruled: the plant is run 2; F0.1 is a finding,
  not a falsifier (ADR-0003); `g-012` stays as is for M00; M00 is not
  RED on this. The trap and the prompt were not edited. Why it passed
  is in feasibility.md §6.4.
- Carried to M01 open (feasibility.md §7): the Data Owner may retire
  `g-012` and add a replacement; the Threshold Owner rules whether Nova
  Micro is still a fair control.
- The reader lands in PR 2: `src/verdict/` (`verdict.schema.json`,
  `build.py`, `gate.py`), the P5 disagreement test, `make evals`,
  `make plants`, `make ledger`.

### PR 2 detail (measure, 2026-09-18)

- The second seed went in first, before any reader:
  `tests/fixtures/hand_written_envelope_no_baseline_card_ref.json`, with
  a test that failed because `src/verdict/` did not exist (`f9f1342`).
- The reader: `src/verdict/schema.json`, `build.py`, `gate.py`,
  `plants.py`, `replay_history.py`. On the seed the gate exits 2,
  REJECTED, `'baseline_card_ref' is a required property`. A run with no
  baseline card makes `build` exit 3, REFUSED, and write nothing.
- The F0.3 seeded case is PR #4: no ruling file, `cold-review-ruling`
  failed on it, closed unmerged. `milestones/M00/runs/f0_3.yaml` points
  the observer at it.
- The rulings that bound this PR are in feasibility.md §2, third round.
  The file formats are in §8. What was found on the way is in §9; the
  first item there decides `checks.F0_3`.
- The seats then ruled on what PR 2 found (feasibility.md §2, fourth
  round; ADR-0004). The baseline is the control and is never gated:
  every result carries `scope`, and at M00 all fifteen are `control`.
  The first envelope, for `8fb4b80`, was written before `scope` existed;
  it is kept under `evals/history/pre-scope/` and the gate does not read
  it. The CI role now allows the baseline's profile only, to `evals.yml`
  only (Finding S-1).
- The measurement is the CI-written envelope under `evals/history/`.
  Nothing here states it. Read the envelope, or run `make ledger`.

### Close detail (PR 3, the close, 2026-09-18)

The milestone closes in three PRs, not four. Ruling F (feasibility.md §2,
fourth round): the cold review of PR 2 found two BLOCKs and both were
cured inside PR 2, so there is no repair PR and PR 3 is the close. The
cap was four and three were used.

**The measurement.** Row 0 is GREEN on the envelope for
`9407615dcde09308490f6699c21a18100bfedcd2`, written by the `record` job
of [run 35406351135](https://github.com/andaro74/agentkeel/actions/runs/35406351135)
as `github-actions[bot]` (`76fa683`). The Measured cell above is copied
from it; `make ledger` reads the cell, asks `verdict.gate` to rule on the
envelope it names, and exits 1 if the two differ. It exits 0.

The same envelope was ruled on again after the merge, with no tokens
spent: the `push` run on `0c39568`
([35408681217](https://github.com/andaro74/agentkeel/actions/runs/35408681217))
found nothing measured had changed since `9407615` and ran the gate on
that envelope. The measurement is the one on `main`, not only the one on
the branch.

**This PR measures again, and the row does not move.** The close PR adds
`tests/test_baseline_frozen.py` and edits `infra/eval-role/README.md`.
Neither is prose to `evals.yml`'s "already measured" step, which excludes
`docs/`, `SPEC/`, `.claude/` and `milestones/**/*.md` and nothing else,
so this PR spends tokens and writes its own envelope. That is wanted:
it is also the first run to assume the eval role as redeployed for S-1.

Row 0 stays on `9407615`, by ruling. That envelope is the measurement
PR 2 took of the tree that reads the plant; adding a test that reads
`src/baseline/` does not re-open the claim. The close PR's own run is
recorded in `feasibility.md` §6.5 as another reading of the control
(Finding F0.4), and in `rulings/pr3.md` with its id. If its trap count is
anything other than 1/3, that is an F0.4 entry, not a change to the row —
and if a check fails, this PR is RED and the row is rewritten before the
tag.

**What "the plant went RED" means.** Product, at this close. Two
sentences, in this order:

1. The gate's REJECTED on the seed. `verdict.gate` on
   `tests/fixtures/hand_written_envelope_no_baseline_card_ref.json`
   exits 2, REJECTED, `'baseline_card_ref' is a required property`. That
   is the plant firing. The seed is `f9f1342`, committed before
   `src/verdict/` existed.
2. `checks.F0_2: pass` in the envelope is the measurement that the
   rejection holds in CI. The six tests in `tests/test_f0_2.py` ran in
   run 35406351135 and their junit result is that field.

The first is the control firing; the second is the evidence that it fired
where it counts. This settles report 4.1, one of the six items PR 2 left
unruled.

**Baseline parameters: confirmed before tag `m00`.** Threshold Owner.
`us.amazon.nova-micro-v1:0`, us-west-2, Converse, temperature 0,
`maxTokens` 512, one system prompt with sha256 `2c3d9b75…` as in the
baseline card at `9407615`, no tools, no guardrail, no retrieval.
Confirmed as measured, not changed. They are frozen with the code by
ADR-0002 from the tag, and `tests/test_baseline_frozen.py` fails on any
diff to `src/baseline/` or to the prompt hash.

**Merge commits, not rebase.** Product, ADR-0004 amendment 1. Envelopes
are keyed to the commit they measured and the bot's authorship under
`evals/history/` is part of the evidence; a rebase or a squash breaks
both. The ruleset on `main` allows `merge` and has no linear-history
rule.

**What this PR carries.** ADR-0002 and its test; ADR-0004 amendment 1;
the Measured cell and this detail; `docs/milestones/M00.md` "What
happened"; the three skills (`/open-milestone`, `/close-milestone`,
`/cold-review`), written from PRs 1 to 3 by hand; `attestations.md`;
`milestones/M01/open.md`; `rulings/pr3.md`.

**What this PR does not carry.** The video. `docs/video/milestones/M00.mp4`
is recorded at the tag, after the merge; the explainer's Watch line says
"pending, tag `m00`". SPEC/00 §10.5 says a close is not ruled ready
without the page and the video, so this is a departure, ruled by Product
at this close and written down rather than quietly taken. The tag is the
human's, after the merge.

**Findings, and where each one lives now.**

| Finding | Home |
|---|---|
| F0.1 — the baseline passes trap `g-012` | ADR-0003; feasibility.md §6.4. Carried to the Data Owner at M01 PR 1 (`milestones/M01/open.md`) |
| F0.4 — the control is not deterministic at temperature 0 | ADR-0004; feasibility.md §6.5, run by run. Seeds SPEC/04's A-vs-A design at M04 open |
| S-1 — the CI eval role was wider than M00 needs | `infra/eval-role/README.md`. Fixed in `app.py` at PR 2, redeployed 2026-09-19T00:20:25Z, not yet assumed by any run at the time of writing; this PR's own run is the first, and is recorded in `rulings/pr3.md` when it finishes. Security signs S-1 on that observation, at M01 (`milestones/M01/open.md` item 12) |
| Profile status is not model status | Findings, above. Carried to SPEC/04 at M04 open |

**What a reader should not take from GREEN.** The control scored 1 of 15
on the measured run, and the one it got right is a trap it got right for
the wrong reason (§6.4). Three of the fifteen have passed on some run
(`g-001`, `g-006`, `g-012`) and no run has passed more than two;
`never_passed` is 14 because the gate's history holds `g-012` only.
GREEN says no check failed and nothing the gate reads regressed; at M00
the gate reads no golden at all, because every result is `scope: control`
and the control is never gated (ADR-0004).
