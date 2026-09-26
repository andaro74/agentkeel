---
# M03 PR 3 (#21), the repair. Product's key.
# One seat per file: the Rule Owner's is pr3-rule-owner.md, Security's
# pr3-security.md, Engineering's pr3-engineering.md (with the cold review),
# the Threshold Owner's pr3-threshold-owner.md. No Data Owner or Tool Owner
# path. Drafted by the session; for the human to rule as Product.
ruling: pr3
seat: Product
authorises:
  - milestones/README.md
  - milestones/M03/README.md
  - milestones/M03/runs/**
evidence:
  - SPEC/00-overview.md#8-M03
  - SPEC/03-evals-regression-redteam-corpus.md
  - milestones/M03/rulings/pr2.md
  - milestones/M03/rulings/pr2-rule-owner.md
  - milestones/M03/runs/guardrail_probes.md
  - milestones/M03/runs/pr3_stop_a_cdk_diff.md
  - milestones/M03/runs/pr3_stop_a_read_back.md
  - milestones/M03/runs/pr3_stop_b_ingest.md
pr: 21
---

# Ruling: M03 PR 3, Product

DRAFT. For the human to rule as Product.

## What this PR is

PR 3 of M03, the repair. It repairs what PR 2's Unsure list carried here,
item C (`rule-owner` F1 on PR 2): the guardrail's own plants, `g-013` and
`g-015`, had no named rule, so dropping `sending-terms-to-a-competitor`
from `guardrail.yaml` silenced no plant (`g-015` is also blocked by two
other topics). Now `guardrail.yaml` names the rule for each of its plants
as `redteam.yaml` does, `build` scores a plant as fired only when its named
rule is among the trace's topics, `validate` requires every control to name
one, the synth refuses one it does not build, and `two-key` reads a change
to any `blocks` value as a relaxation.

Any byte of the rule files is a new guardrail version, so the repair needed
two stops in AWS, both run by the human: stop A cut version 5 of
`1088aw3ujhyd` (bootstrap) and stop B configured the ingest promoter with
it; the manifest pins 5. Row 3 moves to 3 / 4. Its Measured cell is not
written here: it is PR 4's, from this PR's envelope or a later one.

## Rulings (the human, 2026-09-26)

- **A. `g-021`.** `rulings/pr1.md` F6 said retire it with two keys and
  re-add it under a new id at PR 2; SPEC/03 §10 says retiring it is not in
  M03. SPEC/03 wins. It stays never passed and goes to **M04 PR 1** (Data
  Owner, Tool Owner).
- **B. `open.md` row 7, the Threshold Owner's re-ruling of the cap**, is
  done in this PR as a ruling file only (`pr3-threshold-owner.md`); no
  change to `thresholds.yaml`.
- **C. The ingest stack.** It reads the manifest's pin at synth, so moving
  the pin left the deployed promoter on version 4. Redeploy it (stop B)
  rather than record the drift: PR 2 Security F3 was ruled on the deployed
  stacks equalling the tree.

## The run records under `milestones/M03/runs/`

The human's outputs, transcribed by the session with headers:
`pr3_stop_a_cdk_diff.md` (the `--strict` diff whole),
`pr3_stop_a_read_back.md` (81 cases before and after, byte-identical, 0
mismatches, `open.md` row 8's two rows among them),
`guardrail_probes.md` (version 5: READY, description the digest of the rule
files at `0a90d52`, probe 0 mismatches), `pr3_stop_b_ingest.md` (one
change, in place; the promoter configured with 5; version 4 READY).

## Unsure, carried

| # | Item | Seat | When |
|---|---|---|---|
| A | `evals/goldens/v1/g-015.yaml` line 1: "deal terms requested for a third party"; "no guardrail exists before M03". Both stale since SPEC/00 §9's amendment at PR 2 and the guardrail. A comment; id and question unchanged | Data Owner | M04 PR 1 |
| B | The eval role applying version 5 is first read by this PR's CI run; the runtime's `GuardrailIdentifier` condition at `:5` by this PR's merge deploy's load check (a deploy log, not an envelope) | Security, Engineering | this PR's run; the merge |
| C | The first envelope in `mode: runtime` with version 5, if PR 4 cites one: a run after this PR's merge deploy | Product | PR 4 |
| D | Whether the deployed bootstrap template now reads `§` where it read `?` (metadata only) | Security | the next bootstrap `cdk diff --strict` |
| E | R10's N is not in `thresholds.yaml`; dated to PR 2 and slipped unrecorded (`threshold-owner` F7) | Threshold Owner | re-dated in `pr3-threshold-owner.md` |
| F | `g-021` (ruling A) | Data Owner, Tool Owner | M04 PR 1 |

## What a reader can run to falsify this PR

```
uv run pytest -q                                              # with no untracked files in the root
uv run pytest tests/test_build.py -k "named or blocks" -v    # g-015 fails once its rule leaves the trace
uv run pytest tests/test_validate_controls.py -v             # blocks required, each value a rule
uv run pytest tests/test_gates.py -k entry_5 -v              # a blocks value changed or nulled: two keys
make validate && make ledger && make plants
uv run python -m src.gates.two_key --base a423292 --pr 21    # no relaxation against the base
git diff --exit-code 0a90d52 HEAD -- agents/refagent/rules/  # the rules version 5 was built from
```

## The measurement

To be filled from this PR's CI run and its envelope: guardrail
`1088aw3ujhyd:5`, plants 7 of 7, `g-013` and `g-015` fired by their named
rules, every claim 3 check passing.
