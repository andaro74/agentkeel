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
  - SPEC/00-overview.md
  - docs/adr/ADR-0001-spec00-adopted.md
  - docs/adr/ADR-0003-remaining-path-ownership.md
  - CLAUDE.md
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
  # §6: the pasted raw entries of both local runs, with commit hashes
  - milestones/M00/feasibility.md#6
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

This PR also carries ADR-0001 amendment 2 (SPEC/00 §5 and §5.1) and
ADR-0003 (§5 again, and §8 M00: F0.1 is a finding, not a falsifier).
`SPEC/**`, `docs/**` and `CLAUDE.md` are Product paths and this file is
the ruling that authorises the change.

## Seat per path

| Seat | Paths |
|---|---|
| Product | `SPEC/00-overview.md`, `docs/adr/ADR-0001-spec00-adopted.md`, `docs/adr/ADR-0003-remaining-path-ownership.md`, `CLAUDE.md`, `milestones/README.md`, `milestones/M00/**`, `docs/milestones/M00.md`, `.claude/agents/product-spec-reviewer.md` |
| Data Owner | `evals/goldens/v1/**`, `data/clause_index.json`, `data/slate.json`, `data/rights_table.json`, `.claude/agents/data-owner.md` |
| Engineering | `src/baseline/**`, `src/validate/**`, `scripts/seed_slate.py`, `Makefile`, `.claude/agents/engineering-cold-reviewer.md` |
| Security | `.github/workflows/cold-review-ruling.yml`, `.claude/agents/security-reviewer.md` |
| Rule Owner, Tool Owner, Threshold Owner | `.claude/agents/rule-owner.md`, `tool-owner.md`, `threshold-owner.md` |

Every path is in §5 as amended by ADR-0001 amendment 2 and ADR-0003.

## Rulings applied in this PR

Recorded in full in `milestones/M00/feasibility.md` §2.

1. Data Owner: `score` is the answer-fields match and F0.1 fires on it;
   `cites` is a deterministic check, reported always, gating from M01.
2. Product: seats for `scripts/**`, `data/**`, `docs/**` and root config
   (ADR-0001 amendment 2).
3. Rule Owner, Data Owner: only `guardrail_intervened` counts as BLOCKED
   or MASKED. `g-015` stays a fail. Becomes P12 at M03.
4. Threshold Owner, Product: one prompt revision for the baseline, the
   prompt a reasonable engineer would write first. ("Traps must still
   be 0/3" is superseded by R2-2 below.)
5. Product: the "fix the trap or the prompt" sentence applies to
   refagent from M01.
6. `evals/local/` is not evidence; this file cites feasibility.md §6.
7. The second seed is PR 2's first commit.
8. Product: the cold reviewer outputs `ruling: DRAFT`; Engineering
   commits it (§5.1, amendment 2).
9. Data Owner: `added:` and `retired:` are milestone ids.

Second round, after run 2 passed trap `g-012`:

- R2-1. Threshold Owner, Product: the plant is run 2 (`22b5499`); run 1
  is the finding; no third run.
- R2-2. Product, ADR-0003: F0.1 is a finding, not a falsifier. The
  falsifiers of claim 0 are F0.2 and F0.3. M00 is not RED on it.
- R2-3. Data Owner: `g-012` stays as is for M00; it may be retired at
  M01 PR 1 (feasibility.md §7).
- R2-4. Product: row 0 expects the baseline card written, `score` and
  `cites` per golden, traps 1/3 on the plant.
- R2-5. Product, ADR-0003: seats for `README.md`, `LICENSE`, `tests/**`,
  `evals/history/**`, `evals/local/**`.
- R2-6. Product: the `CLAUDE.md` seats-table edit stands.

## What a reader can falsify

- `make validate` exits 0 at the head of this PR, and fails on each of:
  a `table_row` not in `data/rights_table.json`, a `kind` outside the
  enum, an `id` that differs from its file name, a duplicate id, an extra
  field, a guardrail `expected` outside `BLOCKED|MASKED`, an `added` that
  is not a milestone id, a ruling with no `pr`, an `authorises` path that
  matches nothing. Break any one and run it.
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
- The revised prompt holds no title, territory, date, row id or clause id
  from the goldens or from `data/`. Read `src/baseline/prompt.txt`; diff
  it against `8a31e8d` to see the one revision.
- `make evals`, `make plants`, `make ledger` print "not until M00 PR 2".
  The recipe exits 1; GNU make then exits 2.
- The two local runs in feasibility.md §6, each with the commit it was
  made at. Check out that commit and run `make evals-local`; temperature
  is 0.

## What this ruling does not settle

- Whether Nova Micro remains a fair control once refagent has numbers.
  Threshold Owner, at M01 open (feasibility.md §7).
- The FINDINGs and NOTEs of the `product-spec-reviewer` report that the
  seats did not rule on. They are on the record in feasibility.md §1, not
  open questions for this PR. Several bind PR 2: 2.1 (what records the
  plant firing), 2.3 (no CI credential path to Bedrock at M00), 3.2 (how
  F0.2 is observed without a hand-written envelope), 4.2 (who writes the
  measured cell).
