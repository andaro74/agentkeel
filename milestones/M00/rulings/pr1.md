---
ruling: m00-pr1
seat:
  - Product
  - Data Owner
  - Engineering
  - Security
  - Rule Owner
  - Tool Owner
  - Threshold Owner
authorises:
  # Product
  - milestones/README.md
  - milestones/M00/**
  - docs/milestones/M00.md
  - .claude/agents/product-spec-reviewer.md
  # Data Owner
  - evals/goldens/v1/**
  - data/clause_index.json
  - data/slate.json
  - data/rights_table.json
  - .claude/agents/data-owner.md
  # Engineering
  - src/baseline/**
  - src/validate/**
  - scripts/seed_slate.py
  - Makefile
  - .claude/agents/engineering-cold-reviewer.md
  # Security
  - .github/workflows/cold-review-ruling.yml
  - .claude/agents/security-reviewer.md
  # Rule Owner, Tool Owner, Threshold Owner: their own subagent file only
  - .claude/agents/rule-owner.md
  - .claude/agents/tool-owner.md
  - .claude/agents/threshold-owner.md
evidence:
  - SPEC/00-overview.md#8-M00
  - milestones/M00/feasibility.md
  - evals/local/m00-pr1-baseline.json
pr: 2
---

# Ruling: M00 PR 1 (plant)

Cites `SPEC/00-overview.md#8-M00` for `evals/goldens/`, `src/baseline/`,
`scripts/` and `data/`, and for the ledger, feasibility note, explainer
draft, seat subagents, `Makefile` and `cold-review-ruling` that §8 M00
lists as M00 build.

This PR plants. It holds nothing that reads the plant: no `src/verdict/`,
no gate tests, no skills. `cold-review-ruling` is in the tree and is not
yet a required check; Security enables it after this PR merges (R9: it
enforces from PR 2).

## Seat per path

| Seat | Paths | In §5? |
|---|---|---|
| Product | `milestones/README.md`, `milestones/M00/**`, `.claude/agents/product-spec-reviewer.md` | yes |
| Product | `docs/milestones/M00.md` | **no — proposed** |
| Data Owner | `evals/goldens/v1/**`, `data/clause_index.json`, `.claude/agents/data-owner.md` | yes |
| Data Owner | `data/slate.json`, `data/rights_table.json` | **no — proposed** |
| Engineering | `src/baseline/**`, `src/validate/**`, `Makefile`, `.claude/agents/engineering-cold-reviewer.md` | yes |
| Engineering | `scripts/seed_slate.py` | **no — proposed** |
| Security | `.github/workflows/cold-review-ruling.yml`, `.claude/agents/security-reviewer.md` | yes |
| Rule Owner, Tool Owner, Threshold Owner | `.claude/agents/rule-owner.md`, `tool-owner.md`, `threshold-owner.md` | yes |

The three proposed rows are BLOCK 7.1 of the `product-spec-reviewer`
report. Merging this PR with them unruled leaves three paths on `main`
with no seat in §5. Product settles it with a §5 amendment.

## What a reader can falsify

- `make validate` exits 0 at the head of this PR, and fails on each of:
  a `table_row` not in `data/rights_table.json`, a `kind` outside the
  enum, an `id` that differs from its file name, a duplicate id, an extra
  field, a guardrail `expected` outside `BLOCKED|MASKED`, a ruling with no
  `pr`, an `authorises` path that matches nothing. Break any one and run
  it.
- `python scripts/seed_slate.py` rewrites the three files under `data/`
  byte for byte. 12 titles, 40 rows, 14 clauses.
- Every ordinary and trap golden's `answer_fields` follow from its cited
  row on the date in its question (window, holdback, clearance, embargo at
  00:00 in the territory's reference time zone, exclusivity). Work any one
  by hand from `data/rights_table.json`.
- `src/baseline/` imports nothing from `data/` and opens no file but
  `src/baseline/prompt.txt`. `src/baseline/run.py` reads `id`, `kind` and
  `question` from a golden and never `expected`. Grep for `expected` and
  `data` under `src/baseline/`.
- `make evals`, `make plants`, `make ledger` print "not until M00 PR 2".
  The recipe exits 1; GNU make then exits 2, as it does for any failed
  recipe.
- The local run in feasibility.md §6: traps 0/3, no guardrail intervened
  on `g-013` to `g-015`, ordinary 0/9. Re-run `make evals-local` at
  `eb45fec` or later on this branch; temperature is 0.

## What this ruling does not settle

- `evals/local/m00-pr1-baseline.json` is named as evidence and is not in
  the tree: `.gitignore` excludes `evals/local/`, and P11 says a local run
  is not evidence. The trap and guardrail entries are pasted into
  feasibility.md §6 so the claim can be read without it. The measurement
  that decides row 0 is PR 2's.
- BLOCK 1.1: which `expected` fields score the baseline. Data Owner.
- What observable makes a guardrail golden BLOCKED, given `g-015` was
  declined by the model itself. Rule Owner and Data Owner, before M03.
- The baseline scored 0/9 on ordinary goldens and is close to a constant
  responder. Threshold Owner, before tag `m00`.
