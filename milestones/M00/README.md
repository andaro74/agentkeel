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
| Finding, not a falsifier | F0.1 baseline passes a trap (record, do not tighten in this milestone; ADR-0003). Recorded at open: `g-012` on the plant. |
| Seeded commit | `22b5499` on `m00-pr1`: the plant. Goldens `g-001` to `g-015`, `data/` and the baseline code are from `8a31e8d`; the baseline prompt is as revised once in `22b5499`. |
| Expected gate output | Baseline card written; `score` and `cites` recorded per golden; traps expected 1/3 on the plant, F0.1 recorded as a finding. A 0/3 or 2/3 in PR 2's CI run is a non-determinism finding to record. `g-013` to `g-015` fail and land in `never_passed`; `plants_expected = 0` under the plant rule. A run without a baseline card is rejected by `verdict.build`. |
| Measured | — (filled at close) |
| PRs used / cap | 2 / 4 |
| State | OPEN |

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
- The measurement is the CI-written envelope under `evals/history/`.
  Nothing here states it. Read the envelope, or run `make ledger`.

### Close detail

Written at the close PR.
