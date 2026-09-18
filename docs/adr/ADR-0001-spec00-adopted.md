---
adr: ADR-0001
title: SPEC/00 adopted; rulings R1–R11 recorded
status: Accepted
date: 2026-09-18
seat: Product
authorises:
  - Product        # §5 ownership rows, §6 artifacts, §8 PR shape, §10.3 ledger pages
  - Threshold Owner  # agent model id + version + region ownership (§5)
  - Data Owner     # goldens path, golden schema, golden count, data/ paths (§5, §6, §9)
  - Engineering    # Makefile ownership and PR 1 / PR 2 targets (§5, §8 M00)
amendments: 2
---

# ADR-0001 — SPEC/00 adopted

## Context

SPEC/00-overview.md was written before the repo had anything else in it.
A read of SPEC/00 against CLAUDE.md (session of 2026-09-18) found twelve
things neither file specified and eight places the two files disagreed.
Product ruled on all twenty, and on three more raised by the re-report
against the amended files. This ADR records the adoption of SPEC/00 as
the authority, records rulings R1–R11 as recorded in SPEC/00 §11, and
carries the twenty-three rulings as amendment 1.

## Decision

SPEC/00-overview.md is adopted as the authority for this repo. CLAUDE.md
is the working summary; where they disagree SPEC/00 wins and CLAUDE.md
gets a PR.

Rulings R1–R11 (SPEC/00 §11) are recorded here and get no ruling files:

- R1 one human; the mechanical gates in §5 are exhaustive.
- R2 `passed == total` is not a gate anywhere.
- R3 two accounts with boundaries; account-per-team is a follow-on.
- R4 keys, bootstrap and cosign identity belong to Security.
- R5 evidence retention seven years, Object Lock, security account.
- R6 the judge is a model too: pinned, watched, never the model under test.
- R7 computed semver; schema or edge change is major.
- R8 subagents by need; seven seat subagents at M00 PR 1.
- R9 cold review from the start; amended below.
- R10 N is ten minutes.
- R11 golden ids are immutable.

## Amendment 1 (applied at adoption, same PR)

Rulings on what neither file specified:

1. Feasibility note lives at `milestones/MNN/feasibility.md`, every
   milestone. (§6, §8 preamble)
2. Ruling files: one per ruling at `milestones/MNN/rulings/<slug>.md`
   with front matter `ruling`, `seat`, `authorises` (paths), `evidence`
   (paths or PR links), `pr`. `ruling-cited` matches a touched path
   against `authorises:` of any ruling on `main`. R1–R11 get no files.
   SPEC/00 §8 MNN is itself the ruling for that milestone's build paths,
   cited as `SPEC/00-overview.md#8-MNN`. (§5, §6)
3. Agent model id, version and region are owned by the Threshold Owner,
   the seat that owns the judge id; A-vs-A compares the pair. (§5)
4. Golden schema: `evals/goldens/v1/g-NNN.yaml` with `id`, `kind` in
   `ordinary|trap|guardrail|redteam`, `question`, `expected`
   (ordinary and trap: `table_row`, `clause_id`, `answer_fields`;
   guardrail: `BLOCKED|MASKED`; redteam: `BLOCKED`), `seat`, `added`,
   `retired`. `replay_history` keys on id. (§6)
5. Golden count at M00 is 15: 9 ordinary, 3 traps, 3 guardrail. The five
   red-team goldens are `kind: redteam`, ids `g-016` to `g-020`, added at
   M03. §9 "Ordinary (4)" corrected to "(9)". (§8 M00, §9)
6. Plant rule: a plant is a plant only when its enforcing control exists
   in the repo; until then it is a golden that has never passed.
   `plants_expected` counts only plants whose control exists, so before
   M03 `kind: guardrail` goldens grade `never_passed` and
   `plants_expected = 0`. One line in `gate.py` at M00 PR 2. (§5, §8 M00)
7. `scripts/seed_slate.py` writes `data/slate.json` and
   `data/rights_table.json`. M01 loads DynamoDB from them. The baseline
   reads nothing. (§8 M00, §9)
8. Corpus documents are M01 under `data/corpus/`. At M00
   `data/clause_index.json` maps `clause_id` to a one-line description so
   goldens are checkable. Data Owner. §5 `corpus/**` becomes
   `data/corpus/**`. (§5, §8 M00, §9)
9. `.claude/agents/<name>.md` is owned by the seat in its front matter;
   `.claude/skills/**` and `CLAUDE.md` are owned by Product; gate
   `ruling-cited`. (§5, CLAUDE.md table)
10. M00 PR 1 cites `SPEC/00-overview.md#8-M00` for `evals/goldens/`,
    `src/baseline/`, `scripts/` and `data/`, and names the seat per path
    in the PR body. (§8 M00)
11. `docs/adr/` is owned by Product; each ADR's `authorises:` names the
    seat whose rule it changes. ADR-0001 lands in the adoption PR.
    ADR-0002 (baseline frozen, with the diff-test) lands in M00 PR 4 at
    tag `m00`, not before. (§5, §6, §8 M00)
12. `Makefile` is owned by Engineering. At M00 PR 1 all five targets
    exist; `evals-local` and `validate` run; `evals`, `plants`, `ledger`
    exit 1 with "not until M00 PR 2". At PR 2 all five run and `plants`
    returns an empty list so the F0.2 test can read `plants_expected = 0`.
    (§5, §8 M00)

Rulings on where the two files disagreed (SPEC/00 wins unless stated):

1. One ledger, `milestones/README.md`, machine-read by `make ledger` and
   `docs-current`. `milestones/MNN/README.md` holds that milestone's row
   plus open/close detail. `docs/milestones/README.md` is the
   plain-language index, generated by `make ledger --plain`, never
   hand-edited. (§6, §10.3, §10.4, CLAUDE.md tree)
2. Explainer "What happened" and the video land in the close PR (SPEC
   wins). CLAUDE.md PR 3 becomes: repair what the cold review of PR 2
   found; if nothing, PR 3 is skipped and the milestone closes at PR 3 as
   the close PR. A milestone may close in three PRs, never in five.
   (P10, §8 preamble, CLAUDE.md)
3. The `product-spec-reviewer` report goes into `feasibility.md`; every
   other seat report goes into the PR body. M00 PR 1 is exempt from
   "call before opening" for the six subagents it creates;
   `product-spec-reviewer` is written first and run against SPEC/00
   before the rest of PR 1. (§5.1, CLAUDE.md)
4. Every PR ends with a ruling file (CLAUDE.md's bar stands). R9 amended:
   the ruling file is written for every PR; the required check enforces
   it from M00 PR 2. (§5, §11)
5. P11 corrected: `make evals-local` is the local run; `agent evals
   --local` becomes an alias at M07 when the CLI exists. (P11)
6. Goldens path is `evals/goldens/**` (CLAUDE.md was right). (§5, §5.1)
7. `make evals` runs the baseline only at M00, baseline plus refagent
   from M01, baseline re-run every time (P6). CLAUDE.md line corrected.
8. M00 PR 4 also writes the three skills from by-hand PRs 1–3 (SPEC
   wins); added to CLAUDE.md's PR 4 list. Later milestones close through
   `/close-milestone`.

Rulings on what the re-report against the amended files still left open:

21. Judge candidates are six: Llama 4 Maverick, Llama 3.3 70B, Mistral
    Large 2407, gpt-oss-120b, gpt-6-astra, Nova Pro. Nova Pro stays as
    the Amazon entry; a studio would have Amazon approved by default.
    Threshold Owner. (`milestones/M00/README.md`)
22. `make validate` at M00 PR 1 validates golden front matter (schema,
    immutable id format, `kind` enum) and ruling front matter (fields
    present, `authorises` paths exist in the tree). Manifest, seats,
    edges and cdk-nag are added at M01 PR 1 when their inputs exist. The
    header of `milestones/README.md` records what `validate` checked at
    each tag. Engineering, Product on scope. `seat:` is the front matter
    field naming the owning seat in subagents and rulings. (§5, §6,
    §8 M00, CLAUDE.md)
23. `main.py` is deleted. Nothing in SPEC/00 names it, and an unowned
    file on `main` is a path with no seat. Rule recorded in §5: every
    file on `main` has a seat; a file no seat owns is deleted, not
    adopted. (§5, CLAUDE.md)

Also changed to match: §15 done-when names the ledger file and the ruling
file per PR; §8 M00 build list names every artifact above.

## Amendment 2 (M00 PR 1, 2026-09-18)

Rulings on two points the `product-spec-reviewer` report raised against
SPEC/00 at M00 open (`milestones/M00/feasibility.md`, BLOCK 7.1 and
FINDING 8.2). Carried by M00 PR 1 under `milestones/M00/rulings/pr1.md`.

1. Seats for paths §5 did not list. Product. (§5, CLAUDE.md table)
   - `scripts/**` is Engineering's.
   - `data/**` is the Data Owner's. This takes in `data/slate.json` and
     `data/rights_table.json`, and replaces the two narrower entries
     `data/corpus/**` and `data/clause_index.json`.
   - `docs/**` is Product's. This takes in `docs/milestones/**` and
     replaces the narrower entry `docs/adr/**`.
   - Root config is Engineering's: `pyproject.toml`, `uv.lock`,
     `.python-version`, `.gitignore`, with `Makefile` as before.
2. `engineering-cold-reviewer` outputs the ruling text with
   `ruling: DRAFT`; the Engineering seat commits it as the ruling. A
   subagent still never rules and never writes to a seat-owned path.
   Product. (§5.1)

Not settled by this amendment: `README.md` and `LICENSE` at the root,
`tests/**`, `evals/history/**` and `evals/local/**` still have no seat in
§5.

## Consequences

- `ruling-cited` has a concrete matching rule to implement at M02.
- The Threshold Owner pins model ids from M00, not M01; the manifest
  inherits them.
- Before M03 the envelope's `plants_expected` is 0 by rule, not by
  accident; the F0.2 test reads it.
- This ADR has used both of its amendments. The next change to these
  rulings is a new ADR.
