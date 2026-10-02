---
# M07 PR 2 (to open as #39), the measure. Product's key. One seat per
# file: Engineering's is pr2-engineering.md (with the cold review);
# Security's is pr2-security.md (the grant, the workflows, the stacks);
# the Threshold Owner's is pr2-threshold-owner.md (three bars). The PR
# touches no Rule Owner, Data Owner or Tool Owner path.
ruling: pr2
seat: Product
authorises:
  - SPEC/04-model-swap.md
  - SPEC/07-upgrade-retire-surfaces.md
  - CLAUDE.md
  - docs/compliance/map.md
  - docs/developer/quickstart.md
  - docs/developer/template-README.md
  - docs/developer/upgrade.md
  - docs/platform/surfaces.md
  - milestones/README.md
  - milestones/M07/**
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - milestones/M07/feasibility.md
  - milestones/M07/open.md
  - milestones/M07/runs/pr2_reads.md
  - milestones/M07/runs/pr2_expected.md
  - milestones/M07/runs/pr2_by_hand.md
  - milestones/M07/rulings/pr1.md
pr: 39
---

# Ruling: M07 PR 2, Product

DRAFT for andaro74 as Product. Not ruled until this line reads "Ruled by".

## What this pull request is

PR 2 of 4: the measure. The readers for the seeds PR 1 planted, and
nothing live. No attempt is made in it, no App is granted anything, and
no stack is deployed by it. Row 7's wording is untouched; its ledger
cell is at 2 / 4 and its Measured cell is empty.

## What this authorises

- **`SPEC/07` §12**: how §11's reads were ruled on 2026-10-02, where the
  build differs from §6's words, and, after the seat reviews, the
  controls with no seeded case that §8 did not name. No claim, falsifier
  or seeded case changes.
- **`SPEC/04` §2**: the rule for a p95 miss, as the Threshold Owner ruled
  it (`pr2-threshold-owner.md` item 2). The bar stays at 2.0.
- **`milestones/README.md`**: row 7 at 2 / 4; `validate`'s M07 PR 2 line.
- **`milestones/M07/`**: the PR 2 detail in `README.md`; the run files
  restated for three Apps; `runs/pr2_reads.md`, `pr2_by_hand.md`,
  `pr2_expected.md`, `f7_2_removed_and_kept.md`; the four ruling files.
- **`docs/`**: `developer/upgrade.md`, `platform/surfaces.md`,
  `compliance/map.md` (drafted by `legal-compliance`, its first run
  under its own name), and corrections to the quickstart and the
  template's README.
- **`CLAUDE.md`**: `scripts/` and `make upgrade`.

## Stated before the run

`runs/pr2_expected.md`, committed and pushed before the pull request
exists: nine fixture tests pass, four run-file tests stay expected
failures, `F7_0` to `F7_5` pass, every live reading in `upgrade` unread
but `F7_5`, `taken` 0 of 3, refagent as at M06, GREEN. If `F4_4` fails
on p95, no second run: the diff touches `infra/construct/`.

## The seat reviews

Four reports read `a2c5a61...1b376a3` before the pull request was
opened, and `legal-compliance` drafted the map from `9fdbfe2`. Counts:
engineering-cold-reviewer 2 BLOCK, 15 FINDING, 8 NOTE; security-reviewer
1, 7, 12; platform-architect 1, 5, 9; threshold-owner 0, 6, 13;
legal-compliance 0, 3, 17. Each is in the pull request's body, verbatim.
Three BLOCKs were code and are repaired. The fourth is the seats' own:
the ruling files are drafts, and `pr2-security.md` item 13 is not ruled.

What each finding came to: `pr2-engineering.md`, `pr2-security.md`
section 14, `pr2-threshold-owner.md` section 5.

## What is Product's to rule, found by the reviews

| # | What | Recommended |
|---|---|---|
| P1 | **SPEC/07 §2's "a person's edit" includes CI's own envelope commit** (cold review F1). `evals.yml` pushes `evals/history/<commit>.json` to every `agentkeel` pull request as `github-actions[bot]`. As defined, the model upgrade cannot read as held and `taken` is at most 2 of 3 | Amend §2 in PR 3, before the swap is opened: a commit by `github-actions[bot]` that adds only `evals/history/<its own commit>*.json` is not a person's edit, in `agentkeel` only. It is a change to what F7.1 reads, so it is not made here. Alternative: leave it, and row 7 closes RED on `taken` by definition |
| P2 | **SPEC/04 §2's second-run rule has no ADR** (cold review F14) | An ADR in PR 3, with the Threshold Owner. The rule is not used before then |
| P3 | **`two-key` does not read `deprecated_after`** (threshold-owner F1), and CLAUDE.md's seat table and ADR-0009 amendment 1 say it does | The reader and a seeded case in PR 3. Until then SPEC/07 §12 says no gate reads it |
| P4 | **What PR 3 now carries**, beside every attempt's `observed` entry: P1 to P3; Security's 13h, 13i, 13j, 13l, 13n as ruled; the rule on a commit's committer and verification (cold review F5); the relaxation's comparisons moved into build (F6) | PR 3 is the repair, and these are what the cold review of PR 2 found. A fifth PR is a RED close |

## What a reader can run

```
make validate            # 20 checks
make ledger              # exit 0; row 7 OPEN, 2 / 4, Measured empty
git diff a2c5a61 -- milestones/README.md | grep "^[-+]| 7"      # the row's wording: only "1 / 4" to "2 / 4"
grep -n "person's edit" SPEC/07-upgrade-retire-surfaces.md
```
