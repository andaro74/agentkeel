---
# M03 PR 1 (#19), the Rule Owner's key. Product's file is rulings/pr1.md.
ruling: pr1-rule-owner
seat: Rule Owner
authorises:
  - .claude/agents/red-teamer.md
evidence:
  - SPEC/00-overview.md#8-M03
  - SPEC/03-evals-regression-redteam-corpus.md
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
pr: 19
---

# Ruling: M03 PR 1, Rule Owner

Ruled by andaro74 as the Rule Owner, 2026-09-25. The `rule-owner` report (0 BLOCK, 6 FINDING, 6 NOTE) is in the PR
body verbatim; it read the diff.

**`.claude/agents/red-teamer.md`** is the specialist R8 adds at M03,
`seat: rule-owner`, read-only (`Read, Grep, Glob`). It was exercised once
in this PR, on S2, through a general-purpose agent handed the file (it
was not yet registered as an agent type); its report is in the PR body.
Its front matter failed to parse once (`faed466` repaired a colon in
`description`), which `make validate` caught.

**No rule changes.** Nothing under `rules/` or `agents/*/rules/`; the
manifest's `guardrail` stays null. Nothing here is a relaxation.

**What the Rule Owner holds for PR 2:**

| # | Item | When |
|---|---|---|
| F2 | `g-014` not counted at M03; the control files name their plants by id | ruled (`pr1.md` ruling 3); PR 2 writes the files that way |
| F3 | a plant that fired by the wrong rule; `red-teamer.md` item 5 widened to "an intervention by a rule other than the one the attack names" | PR 2, with Engineering's `score_one` |
| F4 | the guardrail's `version` a number, never `DRAFT` | PR 2, the commit that sets `guardrail` |
| F5 | a rule dropped from a control file, or its action weakened, is a relaxation | ADR-0009 entry 5 (`ce8f9e7`); the reader is PR 2's |
| F6 | one Bedrock Guardrail built from both control files | SPEC/03 §6; PR 2 |
| N1 | `red-teamer` checks each new rule against `g-001` to `g-011` and `g-021` before the guardrail's commit | PR 2 |
| N3 | PR 2's `guardrail.yaml` is written from the `red-teamer` draft, not from S6's fixture | PR 2 |
| N4 | Promptfoo in the prompt if cut 5 is not taken | PR 2 |
| N5 | the prompt reads the open milestone's SPEC, not SPEC/03 only | M04 PR 1 |
