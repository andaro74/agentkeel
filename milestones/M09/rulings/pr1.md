---
# M09 PR 1 (#49), the plant. Product's key. One seat per file:
# Engineering's is pr1-engineering.md (the seeds, SEEDS_M09, the tests, the
# ledger test's count, the fixtures README). SPEC/00's amendment, SPEC/09,
# ADR-0014, the explainer, the ledger and milestones/M09/** are Product
# paths. The fixture's rules file and goldens are under tests/**,
# Engineering's, as M08's hostile copy was; the Rule Owner's and the Data
# Owner's readings of them are reports in the PR body, not keys.
ruling: pr1
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/09-per-agent-rules.md
  - docs/adr/ADR-0014-per-agent-rules-on-a-platform-baseline.md
  - docs/milestones/M09.md
  - docs/milestones/README.md
  - milestones/README.md
  - milestones/M09/**
evidence:
  - SPEC/00-overview.md#8-M09
  - SPEC/09-per-agent-rules.md
  - milestones/M09/feasibility.md
  - milestones/M08/open.md
  - docs/adr/ADR-0014-per-agent-rules-on-a-platform-baseline.md
  - docs/adr/ADR-0013-m08-builds-no-control.md
  - docs/adr/ADR-0005-video-follows-the-tag.md
pr: 49
---

# Ruling: M09 PR 1, Product

**DRAFT.** Drafted by the session on 2026-10-11 for andaro74 to rule as
Product. This file reads "Ruled by" only when the human has read it and
says so; until then nothing in this PR is ruled, and the PR does not
merge (`cold-review-ruling`; `milestones/M05/open.md` row 44).

Ruled by: *pending*.

## What this PR is

PR 1 of M09, the plant: 1 / 4. M08 is closed (RED, tag `m08` on
`0ba6d1d`, 2026-10-06). SPEC/00 had no M09 and called M08 the last
milestone; it is amended for a tenth (`d848ea9`, `2320218`), SPEC/09
written in the same commit and reviewed by `product-spec-reviewer` (0
BLOCK, 8 FINDING, 7 NOTE; `feasibility.md` §1), every finding taken on
the session's recommendation (`feasibility.md` §2), SPEC/09 revised once
(`2320218`), ADR-0014 proposed, the seeds planted (`02db54e`). It builds
no reader, no baseline, no merge, no guardrail, no workflow, no stack, no
bar, no golden under `evals/goldens/`, no rule under
`agents/refagent/rules/` and no manifest field of refagent's, and makes
no grant and no attempt.

## Rulings put to Product

1. **A tenth milestone.** M09 opens after M08's close by this ruling,
   not by a finding of M08, and reopens none of M08's rows; M08's five
   findings and three ruled Unsure items keep their homes. SPEC/00 §8's
   count becomes ten and at most 40 PRs (ADR-0014 decision 1).
2. **The claim and the plain sentence, as written** (SPEC/00 §7 row 9,
   §10.3 row 09), with the explainer's first section saying what "the
   platform's" rules are on day one and that their firing is not read at
   M09 (reviewer finding 1, note 14).
3. **M09 builds one control** (ADR-0014): the add-only merge and the
   per-agent guardrail. It is not described as working until it fires on
   the seeded case. The gate rules nothing on `agent_rules`; a silent
   plant in an agent repository stops no merge at M09.
4. **Expected GREEN, stated with its risks** (SPEC/09 §7): fired 1 of 1;
   the rule's wording unprobed, the baseline's content and the builder
   unruled, the split possibly two keys. The golden is never edited to
   make the rule fire.
5. **The fifteen dispositions in `feasibility.md` §2**, each a proposal
   with its seat: the placeholder pin and the three-pull-request sequence
   (finding 2), F9.2's live arm (3), S5 (4), the count (5), the two
   SPEC/00 lines (6, 13), M09's video at its own close (7), no CODEOWNERS
   edit owed (8), the independent digest (9), the registry row (10), R10
   (11), the cap risk recorded (12), where `rules/` goes (15).
6. **The public caller is M10**, proposed and not opened (SPEC/09 §11
   R6).

## Unsure, each with its seat and when

The PR body's Unsure list, repeated here so the ruling carries it.

| # | Item | Seat | By |
|---|---|---|---|
| A | The prompt-attack filter is off by ruling (`guardrail.yaml:33-36`) and the bootstrap refuses to build unless it is off. Does the baseline turn it on, and if so how does a plant still prove its named rule fired? Proposed: off; if on, the membership rule as it stands, the filter's own match recorded beside the topic and not counted | Rule Owner | before PR 2 opens (R1) |
| B | What the baseline holds on day one. Proposed: the two PII entities, no topic, the two messages. Their firing is not read at M09 (SPEC/09 §8) | Rule Owner | before PR 2 opens (R1) |
| C | The deploy role is denied guardrail create and update. Which role builds a guardrail for a new agent, and does each new agent need a bootstrap deploy? Proposed: the construct in the agent's own stack, the deny narrowed to a guardrail the stack tags; the alternative is a bootstrap deploy by hand per agent | Security | before PR 2 opens (R3) |
| D | Splitting the baseline changes refagent's guardrail. Whether ADR-0009 entry 4 or 5 makes that a two-key change. Proposed: the PII entries stay in refagent's file beside the baseline's and the id is kept, so neither fires; else PR 2 carries two keys | Rule Owner; Threshold Owner | before PR 2 opens (R2) |
| E | Bedrock's limit of 30 topics per guardrail, for baseline plus agent rules. Proposed: the merge refuses at the count and names the file that took it over | Engineering | PR 2 (R5) |
| F | Whether the public caller is M10 or stays inside this milestone. Proposed: M10, its own claim | Product | before PR 2 opens (R6) |
| G | The shape of a blocked observation that pharmadelta's scorer will read (pharmadelta M00 Unsure 10). Proposed: as `build` writes it today, `stop_reason: guardrail_intervened` and `guardrail_topics` naming the rules, `pass` true only when the named rule is among them; M09 adds no new shape | Data Owner | PR 2 (R7) |
| H | The observer's read-back of a built guardrail (`bedrock:GetGuardrail`); if not granted, SPEC/09 §9 cut 3 | Security | before PR 2 opens (R4) |
| I | The fixture repository's name and visibility: `agentkeel-studio/festival-desk`, public | Product | before PR 3's run (R8) |
| J | The fixture's three goldens and that `g-030`'s wording is not changed to make the rule fire; the Rule Owner rewords the rule if the first probe does not block | Data Owner; Rule Owner | before PR 3's run (R9) |
| K | Row 37 re-ruled: a template agent's pin may be its own (SPEC/00 §8 M09 item 3) | Rule Owner | PR 2 (R10) |

## What a reader can run

See `milestones/M09/README.md`, "What a reader can run".
