---
# M03 PR 2 (#20, expected), the Rule Owner's key. Drafted by the session from the
# rule-owner report; the human rules it as Rule Owner. Product's file is pr2.md.
ruling: pr2-rule-owner
seat: Rule Owner
authorises:
  - agents/refagent/rules/guardrail.yaml
  - agents/refagent/rules/redteam.yaml
  - agents/refagent/manifest.yaml
  - .claude/agents/red-teamer.md
evidence:
  - SPEC/00-overview.md#8-M03
  - SPEC/03-evals-regression-redteam-corpus.md
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
  - milestones/M03/rulings/pr1-rule-owner.md
  - milestones/M03/runs/guardrail_probes.md
  - milestones/M03/runs/guardrail_candidates_third_party.yaml
pr: 20
---

# Ruling: M03 PR 2, Rule Owner

**Draft.** The human rules it as Rule Owner. The `rule-owner` report on the
diff `d2d1e6d...5871122` (1 BLOCK, 5 FINDING, 8 NOTE) is in the PR body.
On `agents/refagent/manifest.yaml` this file covers the `guardrail` field
only; ruling-cited attributes the manifest field by field.

## Not a relaxation: one key (the human, 2026-09-26)

At the base refagent had no rule files and `guardrail: null`; null to a
value is not a relaxation (ADR-0009 entry 4), and nothing was removed from
a list on `main`. Three narrowings happened inside the PR, none ever on
`main` or on an envelope (`evals/history` holds no `1088aw3ujhyd`):

- the blocked intent renamed `third-party-deal-terms` to
  `sending-terms-to-a-competitor`, and narrowed from terms for any third
  party to terms for a competitor. Case: versions 1 and 2 and a trial of a
  rename blocked `g-006`, an ordinary golden; five of six wordings about a
  competitor as the recipient did not;
- `topics_apply_to: input` (version 4): the six topics no longer block on
  the answer. Case: version 3 blocked every ordinary and trap answer on the
  first of two local runs (`evals/local`, not evidence). At M03 refagent
  reads no document, so the answer side had nothing to catch; M04
  re-examines it with the knowledge base;
- the prompt-attack filter off, so each plant is blocked by the rule it names.

**One key**, as `rule-owner` read it and the human ruled. From this PR on,
each is a relaxation, two keys, because `two_key.py` now reads ADR-0009
entry 5 (`1c33876`): a rule, a PII type, a plant id or a `blocks` entry
removed (a rename is a removal), an action weakened, a `blocks` entry
re-pointed, `topics_apply_to` narrowed, a switch turned off (the
prompt-attack filter `on -> off`) or a filter level lowered (the second
cold read of PR 2, F2). A definition's wording is not read, while an
example's is (a list entry): Product, pr2.md Unsure B.

## The pin

`1088aw3ujhyd`, version **4**, built by the bootstrap stack from the two
rule files; a numbered version, never DRAFT (F4 at PR 1). The files at the
PR head hash to `rules sha256 9cbefa08…`, the digest version 4 was built
from (`ade6dcb`; unchanged since). Its `get-guardrail` description,
pasted by the human on 2026-09-26: `rules sha256 9cbefa08…`, the same. Probe of version 4: 0 mismatches,
transcribed whole in `guardrail_probes.md`.

## Plants

Seven: `g-013` and `g-015` (`guardrail.yaml`), `g-016` to `g-020`
(`redteam.yaml`, each with the rule that must block it in `blocks`, and
`build` scores an attack fired only by that rule, `484db7d`). `g-014` is
not counted until M04; the PII rule stays in the file and no page calls
it working.

## Findings, and where each is held

| # | Finding | Status |
|---|---|---|
| BLOCK | nothing read ADR-0009 entries 4 and 5 | **repaired** `1c33876` |
| F1 | `g-013`, `g-015` have no named rule; dropping the blocked intent silences no plant | **deferred to M03 PR 3** (the human, 2026-09-26): any byte of `guardrail.yaml` makes version 5 |
| F2 | the rule covers less than SPEC/00 §9 named | **repaired**: SPEC/00 §9 amended (pr2.md ruling 4) |
| F3 | version 4 not read back against the files | **done** `a9c8ff6`: the description and the files both 9cbefa08 |
| F4 | `topics_apply_to` and a narrowed definition outside entry 5 | the switch **read** by `1c33876`; definitions: Product, pr2.md Unsure B |
| F5 | no Rule Owner ruling | this file |
| NOTEs | wording in `guardrail.yaml` comments (first of two local runs; the stated reason looser than the data); g-015 matching two more topics than its words; the synth refusing prompt-attack on | recorded; the comment wording changes with F1 at PR 3, the same new version |
