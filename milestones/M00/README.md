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

If a trap fails, fix the trap or the prompt, not the model.

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
| Falsifiers | F0.1 baseline passes a trap (record, do not tighten in this milestone). F0.2 an envelope validates without a baseline ref. F0.3 a PR merges without a ruling file after PR 2. |
| Seeded commit | `8a31e8d` on `m00-pr1`: goldens `g-001` to `g-015`, `src/baseline/`, `data/` |
| Expected gate output | Baseline traps 0/3. `g-013` to `g-015` fail and land in `never_passed`; `plants_expected = 0` under the plant rule. A run without a baseline card is rejected by `verdict.build`. |
| Measured | — (filled at close) |
| PRs used / cap | 1 / 4 |
| State | OPEN |

### Open detail (PR 1, 2026-09-18)

- Feasibility note: `milestones/M00/feasibility.md`. The
  `product-spec-reviewer` report in it has 2 BLOCK, 17 FINDING, 9 NOTE.
  Neither BLOCK is ruled; both are carried as stated assumptions for the
  Data Owner (which `expected` fields score the baseline) and Product
  (seats for paths §5 does not list).
- Planted: three traps (`g-010` holdback did not move with the theatrical
  date, `g-011` non-exclusive licence, `g-012` sequel does not inherit),
  three guardrail goldens (`g-013` to `g-015`) with no guardrail to
  enforce them, and the baseline that must lose.
- Not planted: the run without a baseline card. It needs the card format,
  which is `src/verdict/` in PR 2. PR 2 plants it before `build.py`.
- Baseline parameters, stated here because nothing else pins them:
  `us.amazon.nova-micro-v1:0`, us-west-2, Converse, temperature 0,
  `maxTokens` 512, one system prompt (`src/baseline/prompt.txt`), no
  tools, no guardrail, no retrieval. Threshold Owner confirms or changes
  them before tag `m00`; after the tag they are frozen with the code.
- PR 1 local run (not evidence): see feasibility.md §6.
- The reader lands in PR 2: `src/verdict/` (`verdict.schema.json`,
  `build.py`, `gate.py`), the P5 disagreement test, `make evals`,
  `make plants`, `make ledger`.

### Close detail

Written at the close PR.
