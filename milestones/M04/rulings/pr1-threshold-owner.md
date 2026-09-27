---
# M04 PR 1 (#23), the Threshold Owner's key. Product's file is
# rulings/pr1.md. This PR moves no bar and no pin: thresholds.yaml and
# agents/refagent/manifest.yaml are untouched. The paths below are where
# this seat's rulings are written: the two ADRs that authorise it, and the
# seed patches that move the pin in a copy of the tree.
ruling: pr1-threshold-owner
seat: Threshold Owner
authorises:
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
  - docs/adr/ADR-0010-the-pins-lifecycle-fields-are-the-threshold-owners.md
  - tests/fixtures/m04/s1-breaking-pin.patch
  - tests/fixtures/m04/s2-equivalent-pin.patch
  - tests/fixtures/m04/s5-deprecated-pin.patch
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md
  - milestones/M04/feasibility.md
  - milestones/M04/runs/model_access_2026-09-26.md
pr: 23
---

# Ruling: M04 PR 1, Threshold Owner

The rulings below were made by andaro74 as the Threshold Owner, on
2026-09-26 and 2026-09-27, each "as proposed". This file was drafted by
the session from them; the human signs it off before the PR opens. The
`threshold-owner` reports (0/8/11 on the tree at `74fb9ed`; 0/5/12 on the
diff at `688634c`) are in the PR body verbatim.

**No bar moves and no pin moves.** No two-key file is needed in this PR.

| # | Ruling | Where |
|---|---|---|
| 1 | "Promotes" means the equivalent swap PR is mergeable, every required check green, not merged | SPEC/04 §1 |
| 2 | `delta_max` applies to p95 and the agent's tokens, not to goldens; P7 stands | SPEC/04 §2; SPEC/00 §8 M04 |
| 3 | A model id change is not on ADR-0009's list; the measured gate is its control, and this seat's ruling on the swap PR its key | SPEC/04 §10; CLAUDE.md |
| 4 | The candidates: equivalent Sonnet 4.5, breaking Llama 3.1 8B, cheaper Haiku 4.5 (reported only), named before any run | SPEC/04 §2 |
| 5 | The deprecation plant is Sonnet 4 with Bedrock's `endOfLifeTime` 2026-10-14 (S5); it is nobody's swap | SPEC/04 §2, §5 |
| 6 | The bars: p95 ≤ 2.0× and the agent's tokens ≤ 1.5× the incumbent's median; the incumbent is the pin at the merge-base with `main`, matched on profile and region, in the same `mode`; envelopes with no `mode` not counted | SPEC/04 §2 |
| 7 | The run's side is its first refagent run, its tokens from a field of their own; no incumbent envelope in the mode writes `F4_4: fail`, RED | SPEC/04 §2 |
| 8 | The bars apply to every agent envelope, under `relative.*`; `cost_cap` is a budget beside them | SPEC/04 §2, §6 |
| 9 | ADR-0009 entry 6 (proposed here, ruled by Product): `deprecated_after` moved later, nulled or removed with `model.id` unchanged is a relaxation, this seat's key; a swap to a `LEGACY` model carries its `endOfLifeTime` | ADR-0009; SPEC/04 §2 |
| 10 | ADR-0010: `model.profile` and `deprecated_after` are this seat's | ADR-0010 |
| 11 | `version` records a versioned id's suffix; null only when the id has none | SPEC/04 §2 |
| 12 | `pinned_roles` completed at PR 2 before either swap PR opens | SPEC/04 §5.1 |
| 13 | The control stays Nova Micro at `m00`; a swap moves the agent only (`open.md` row 12) | SPEC/04 §10 |

**Held for PR 2 by this seat:** the two bars into `thresholds.yaml`; the
cap re-ruled against A-vs-A's measured spend (two keys if raised); the
stale `thresholds.yaml` and manifest judge comments; the p95 evidence
restated on the counted envelopes; the incumbent median's ratchet
(`threshold-owner` notes 12, 13).
