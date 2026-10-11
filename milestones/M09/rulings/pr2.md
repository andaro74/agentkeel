---
# M09 PR 2 (#50), the measure. Product's key over the Product paths this PR
# touches: the two developer documents, the explainer's engineer rows, the
# ledger's header row, this milestone's README and run file, and the four
# ruling files. The Rule Owner's file is pr2-rule-owner.md (R1, R2, R10),
# Security's is pr2-security.md (R3, R4), Engineering's is
# pr2-engineering.md (the readers, with the cold review). R6 is ruled here.
ruling: pr2
seat: Product
authorises:
  - SPEC/09-per-agent-rules.md
  - docs/developer/template-README.md
  - docs/developer/quickstart.md
  - docs/milestones/M09.md
  - milestones/README.md
  - milestones/M09/**
evidence:
  - SPEC/00-overview.md#8-M09
  - SPEC/09-per-agent-rules.md
  - milestones/M09/feasibility.md
  - milestones/M09/rulings/pr1.md
  - docs/adr/ADR-0014-per-agent-rules-on-a-platform-baseline.md
pr: 50
---

# Ruling: M09 PR 2, Product

Ruled by: pending

## What this PR is

PR 2 of M09, the measure: 2 of 4. The gate that reads the plant. Every
reader SPEC/09 §6 names is in the tree, each landed in the commit that
took its seed's marker off (`milestones/M09/README.md`, "Measure
detail"), and on this PR's own envelope `agent_rules` reads not made, so
row 9's reading is RED: the plant going RED under the measurement, which
PR 2 is for. The rulings decided before it opened (R1, R2, R3, R4, R6,
R10, 2026-10-11, each as proposed in PR 1's Unsure table) are written as
this PR's four ruling files; each is a draft until it reads "Ruled by".

## Rulings put to Product

1. **R6: the public caller is M10, its own claim.** Nothing in M09's
   falsifiers reads a caller, and nothing in this PR builds one (SPEC/09
   §11 R6, §12). A tenth claim is opened, if at all, by a Product ruling
   as this one was (ADR-0014 decision 1), not folded into row 9.
2. **SPEC/09 §2's `content_filters` sentence** reads "that differs from
   the baseline's" from this PR, as the Rule Owner rules it (`rule-owner`
   finding 1 on PR 2); the quickstart says the same, and says no agent
   with `rules/` has been deployed yet (cold review note 4).
3. **The template README and the quickstart say what is now true**: a
   `rules/guardrail.yaml` is read and merged onto the platform's baseline
   add-only; every rule a team writes carries a planted question; the
   platform builds the agent's guardrail from the merged rules; the
   platform's own two rules have no planted question of their own
   (SPEC/09 §8; feasibility §2 finding 1). The sentence "A `rules/`
   folder here is not read", the false state, is corrected now that the
   reader exists (ADR-0014, Consequences), never before.
4. **The ledger's header row for M09 PR 2**: twenty-one checks, one new
   and two changed, with what `validate` still does not read. Put to
   Product as the brief asked; the row is written as proposed.
5. **The run file's `observed` keys**, stated as a comment above
   `observed: null` so the owner fills what the observer reads and nothing
   else (SPEC/09 §5.1). The file's prose feeds no reading.
6. **The explainer's engineer rows** say the check landed; "What happened"
   stays empty until the close.
7. **R7 and R11 are the Data Owner's and are not ruled here.** R7 is built
   as proposed (the answer record carries each golden's observation in the
   shape `build` writes for refagent's plants, `stop_reason` and
   `guardrail_topics`; `pass` true only when the named rule is among them);
   the Data Owner's ruling on the shape, and on whether a MASKED plant is
   counted (R11), is put in the PR body under Unsure.

## What a reader can run

```
uv run pytest tests/test_m09_seeds.py -q     # 8 passed, 1 xfailed
make ledger                                  # row 9 OPEN; as row M09 reads it: RED, agent_rules not read
make validate                                # twenty-one checks
git diff 460990b...HEAD -- docs/developer docs/milestones/M09.md milestones/README.md milestones/M09   # this key's paths
```
