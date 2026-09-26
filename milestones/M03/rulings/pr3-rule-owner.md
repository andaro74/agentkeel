---
# M03 PR 3 (#21), the Rule Owner's key. Drafted by the session from the
# rule-owner reports on this PR; for the human to rule as Rule Owner.
# Product's file is pr3.md.
ruling: pr3-rule-owner
seat: Rule Owner
authorises:
  - agents/refagent/rules/guardrail.yaml
  - agents/refagent/manifest.yaml
evidence:
  - SPEC/00-overview.md#8-M03
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
  - milestones/M03/rulings/pr2-rule-owner.md
  - milestones/M03/runs/guardrail_probes.md
  - milestones/M03/runs/pr3_stop_a_cdk_diff.md
pr: 21
---

# Ruling: M03 PR 3, Rule Owner

DRAFT. For the human to rule as Rule Owner. `rule-owner` read this PR three
times, each report in the PR body: before stop A, from the tree at
`9ff9f95` (0 BLOCK, 3 FINDING, 13 NOTE); before stop B, from the tree at
`47ee02d` (0 BLOCK, 3 FINDING, 5 NOTE); for the cold review, the diff
`a423292...62e7980` (0 BLOCK, 1 FINDING, 7 NOTE). On
`agents/refagent/manifest.yaml` this file covers the `guardrail` field only.

## Not a relaxation: one key

- `guardrail.yaml` gains `blocks: {g-013: embargoed-synopsis, g-015:
  sending-terms-to-a-competitor}` (`9ff9f95`), each the topic the probes of
  versions 3 to 5 show among that plant's matches. An addition: nothing in
  `plants`, `denied_topics`, `pii`, `content_filters`, `messages` or
  `topics_apply_to` changes. It tightens scoring. The other hunks are
  comments (`9ff9f95`, `0a90d52`).
- The manifest's pin moves from `"4"` to `"5"`, same id (`47ee02d`). ADR-0009
  entry 4 reads null, a removal or an id change; this is none. Version 5
  blocks what version 4 blocked: same topics, PII and messages (the stop A
  diff), and the probe matches version 4's row for row.
- `two_key --base a423292` finds no relaxation.

From this PR on, removing or re-pointing either `blocks` entry, or setting
one to null, is a relaxation (`88577a5`), and deleting `blocks` whole is
refused by `validate` (`f735f29`).

## The pin

`1088aw3ujhyd`, version **5**, read from `GuardrailVersionForTheManifest`,
not assumed. `get-guardrail` version 5: READY, description `rules sha256
b2cff2a1fd13d3638d29f232824dea2a7b5e6ee48951872e1979c4d651e10315`. The rule
files hash to that at `0a90d52` and at the head: `git diff --exit-code
0a90d52 HEAD -- agents/refagent/rules/` exits 0 (the session, on
`rule-owner`'s F3 before stop B). Probe of version 5 as admin: 0
mismatches, `g-013` and `g-015` each blocked with their named rule among
the topics. Version 4 retained and READY (stop B), which PR 2's envelope
names.

## Plants

Seven, as at PR 2: `g-013` and `g-015` (`guardrail.yaml`), `g-016` to
`g-020` (`redteam.yaml`), each now with a named rule. `g-014` is still not
counted (M04).

## Findings, and where each is held

| # | Finding | Status |
|---|---|---|
| PR 2 F1 | the guardrail's plants had no named rule | **repaired** `9ff9f95`, read by `c5ff91e` and `d02be78` |
| F3 (c), before stop A | `blocks` deleted whole passed `validate` | **repaired** `f735f29` |
| NOTE, before stop A | the probe merged two controls' `blocks` without refusing a clash | **repaired** `f735f29` |
| NOTEs, before stop A | the wrapping of two comment lines; the competitor wording's stated reason; "first of two local runs" | **repaired** `9ff9f95`, `0a90d52`, before stop A, so version 5 carries them |
| F4, before stop A | nothing mechanical ties the pin's description to the tree's digest | recorded: read by hand at each deploy; a mechanical check is a proposal for Security or Engineering (M05) |
| F3, before stop B | rules unchanged since `0a90d52` not verified | **read** by the session: exit 0, digest at the head `b2cff2a1…` |
| F4, before stop B | the manifest comment said, in the present tense, that the deployed stacks carry the pin | **repaired** `d294826` |
| FINDING, cold review | no envelope shows version 5 applied by the eval role | open until this PR's run; this file is to cite its envelope before the human rules |
| NOTE | `g-015.yaml`'s stale comment (Data Owner path) | `pr3.md` Unsure A, M04 PR 1 |
| NOTE | the drop of `sending-terms-to-a-competitor` is witnessed by a unit test, not a seed | recorded: enough for Unsure C |
