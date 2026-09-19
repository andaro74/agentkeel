---
# M01 PR 1, the Threshold Owner's key (ruling B: two keys, two files).
# Engineering's key on the same two changes is in rulings/pr1.md.
ruling: pr1-threshold-owner
seat: Threshold Owner
authorises:
  - thresholds.yaml
  # the model-id fields only: model, judge_model_id, pinned_roles
  - agents/refagent/manifest.yaml
evidence:
  - docs/adr/ADR-0004-measurement-fields.md
  - evals/history/9407615dcde09308490f6699c21a18100bfedcd2.baseline-card.json
  - milestones/M00/README.md
  - milestones/M01/feasibility.md#6
pr: 7
---

# Ruling: M01 PR 1, Threshold Owner

This file is the Threshold Owner's key. Engineering's key for the two
`thresholds.yaml` changes is in `rulings/pr1.md`. Both carry `pr: 7`.

## `thresholds.yaml`

1. **`cost_cap.tokens_per_run: 150000`**, up from 20,000. An upward move
   relaxes the cap, so it takes two keys: this file and Engineering's in
   `rulings/pr1.md` (M01 open item 22). The cap is for two subjects. The
   control is about 6,000; this PR's local run spent 5,766. refagent on
   Sonnet 5 is not measured yet. The Threshold Owner rules the cap again
   against PR 2's first agent envelope; lowering it then is a tightening
   and needs one key. Until then the same cap applies to a run with no
   agent, about 26 times the control's spend where M00's was about three
   and a half times: named here, not argued for, and re-ruled with the cap
   at PR 2. An envelope does not record the cap it was built against, and
   the gate reads today's `thresholds.yaml`; a cap lowered at PR 2 below
   an earlier M01 envelope's spend would move that envelope's reading.
   Engineering, at M01 PR 2 open.
2. **An over-cap run is a recorded RED, not a missing file** (item 22;
   ruling A). `verdict.build` writes the envelope RED and `verdict.gate`
   works out the same, whichever the subject. The envelope's `tokens_in`
   and `tokens_out` are the run's: agent plus control card when an agent
   ran, the control's when none did.
3. **`baseline_card`** pins the base: the card at tag `m00` that row 0
   cites, `evals/history/9407615….baseline-card.json`, by content hash
   `b0219756cad63be67fb51aa4632dd015084840833341f15235fab4569adc3295`
   (item 5; ADR-0004 amendment 2, item 1). Not a bar; it moves nothing.
   A new base is ruled, not built.
4. **Region** (item 23, with Security): the card's `region` is the request
   region, the profile ARN's `us-west-2`. Converse does not return the
   serving region; it is not recorded.

## `agents/refagent/manifest.yaml`, model-id fields

- The model ids move here from `milestones/M00/README.md`, whose table
  stays as the record at `m00`. Every id and profile is the table's, byte
  for byte (the `threshold-owner` report on this PR checked all twelve).
- `model.version` stays `null` until Bedrock returns a version for
  `us.anthropic.claude-sonnet-5`; re-ruled at PR 2 with the cap (ruling
  G). `modelLifecycle` for `anthropic.claude-sonnet-5` in us-west-2 read
  `ACTIVE` on 2026-09-19 (`aws bedrock list-foundation-models`).
- The other fields of the file are not this seat's. `guardrail` is the
  Rule Owner's and is `null` until M03.

## Re-dated

- Item 3 (`cost_usd`, a price table): M05 open.
- Item 21 (is Nova Micro still a fair control): M01 PR 2, after the first
  agent envelope.
- Items 24 to 26 (with the Data Owner): M02 PR 1, `milestones/M02/open.md`.

## What a reader can falsify

- `uv run python -c "import json; from src.verdict import canonical_sha256; print(canonical_sha256(json.load(open('evals/history/9407615dcde09308490f6699c21a18100bfedcd2.baseline-card.json', encoding='utf-8'))))"`
  prints `b0219756…3295`.
- `uv run pytest tests/test_build.py -k "base or cap"`: `build` refuses
  another base, and writes an over-cap run RED for either subject.
- Compare `agents/refagent/manifest.yaml` with `milestones/M00/README.md`
  lines 7 to 13.
