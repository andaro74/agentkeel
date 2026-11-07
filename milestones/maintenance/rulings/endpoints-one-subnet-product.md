---
# Maintenance PR #58. Product's key over milestones/maintenance/README.md,
# the folder that holds rulings for pull requests after the m10 close.
ruling: endpoints-one-subnet-product
seat: Product
authorises:
  - milestones/maintenance/README.md
  - milestones/maintenance/rulings/endpoints-one-subnet-product.md
evidence:
  - CLAUDE.md
  - SPEC/00-overview.md#5
  - https://github.com/andaro74/agentkeel/pull/58
pr: 58
---

# Ruling: maintenance PR #58, Product

Ruled by andaro74 as Product, 2026-11-07, as written.

A folder `milestones/maintenance/` for the rulings of pull requests after
the `m10` close. `RULING_GLOB` accepts any folder under `milestones/`;
CLAUDE.md names `MNN`, and a maintenance PR has no milestone, no ledger
row and no PR 1 to 4. Unsure: whether Product would rather these rulings
live under `milestones/M10/rulings/` after the tag, or that CLAUDE.md's
"Where things are" gain a line for this folder (a Product PR). This ruling
takes the folder; the CLAUDE.md line is not in this PR.
