---
# M02 PR 1 (#11), the plant. One seat per file (M01 PR 1, ruling B), and
# from M02 each seat's paths are in that seat's file, in the shape
# SPEC/02 §2 gives `ruling-cited` to read: Security's key is
# rulings/pr1-security.md, Engineering's is rulings/pr1-engineering.md.
ruling: pr1
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/02-seats-and-change-gates.md
  - CLAUDE.md
  - .claude/skills/cold-review/SKILL.md
  - docs/adr/ADR-0003-remaining-path-ownership.md
  - docs/adr/ADR-0006-gateway-endpoints-for-s3-and-dynamodb.md
  - docs/adr/ADR-0008-a-ruling-is-on-main-at-the-merge-commit.md
  - docs/milestones/M02.md
  - docs/milestones/README.md
  - milestones/README.md
  - milestones/M01/runs/f1_3_key_policy.yaml
  - milestones/M02/**
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md
  - milestones/M02/feasibility.md
  - milestones/M02/open.md
  - docs/adr/ADR-0003-remaining-path-ownership.md
  - docs/adr/ADR-0005-video-follows-the-tag.md
  - docs/adr/ADR-0008-a-ruling-is-on-main-at-the-merge-commit.md
pr: 11
---

# Ruling: M02 PR 1 (plant), Product

Cites `SPEC/00-overview.md#8-M02` for M02's build paths, and the rulings
in `milestones/M02/feasibility.md` §2 (the BLOCK, §2.1; the FINDINGs and
NOTEs, §2.2 and §2.3; the 23 carried rows, §6). Nothing here makes claim
2 pass: no `src/gates/`, no CODEOWNERS, no growth in `validate`, no
`scripts/observe_pr.py`.

## Seat per path

- **Product** (this file): SPEC/00 (§5's Security row, the
  `ruling-cited` line and R9, each amended by an ADR that names Security
  as the seat whose rule changes); SPEC/02; CLAUDE.md's tree line; the
  cold-review skill (open.md row 8); the three ADR files under
  `docs/adr/`, a Product folder whose rules belong to the seat each
  names; the explainer draft; the ledger and its three new header rows;
  the M02 folder; one comment in an M01 run file (row 22).
- **Security**: `rulings/pr1-security.md`. `infra/construct/`,
  `infra/bootstrap/README.md` (row 9); the rule changes in ADR-0006
  amendment 1 and ADR-0008, and ADR-0003 amendment 2's path.
- **Engineering**: `rulings/pr1-engineering.md`. `tests/**`,
  `src/verdict/plants.py`, `src/verdict/gate.py`, `.gitattributes`.

No two-key change: `thresholds.yaml`, every golden, every manifest and
`rules/` are untouched. The seed patches under `tests/fixtures/m02/`
change none of them on this branch.

## What was planted, and the order

SPEC/02 first (`bc35c39`), reviewed before it was committed; then the
five seeds, one commit each (`6ff333a`, `74a38be`, `d8fbdb1`, `9eb539c`,
`479abb9`), each with its test, none with a reader; then the listing
(`b3c6b3a`). Row 9's test (`25b2743`) precedes its fix (`9ea6405`).

## The PR shape, checked against CLAUDE.md

Held. This PR contains SPEC/02, the feasibility note with the report in
it, the ledger row on open, the explainer with "What happened" empty,
the seeds, and carried items from a closed milestone under their seats'
rulings. It contains nothing that reads a seed. The one thing it does
that a plant PR does not usually do is change a deployed construct (row
9); that change is a repair to M01's build path under a Security ruling,
neither seeds nor reads claim 2, and its test went in before it. The
template diff is one line, `SSEEnabled` true to false, in the PR body.

## To falsify this PR's own claims

```
git show 6ff333a --stat          # S1: two patches and the test file, nothing else
git show 74a38be --stat          # S2
git show d8fbdb1 --stat          # S3
git show 9eb539c --stat          # S4: three run files and the test
git show 479abb9 --stat          # S5
uv run pytest tests/test_m02_seeds.py    # 6 xfailed
make plants                      # S1-S5 listed, each reader "not in the tree yet"
git checkout 25b2743 && uv run pytest tests/test_bootstrap.py -k needs_an_action   # fails on the table
git checkout 9ea6405 && uv run pytest tests/test_bootstrap.py -k needs_an_action   # passes
ls src/gates .github/CODEOWNERS scripts/observe_pr.py     # none exists
make validate && make ledger     # both exit 0; row 2 Measured is empty
```
