---
# M03 PR 2 (#20, expected; corrected when the PR opens), the measure. Product's key.
# One seat per file: the Rule Owner's is pr2-rule-owner.md, Security's
# pr2-security.md, Engineering's pr2-engineering.md (with the cold review), the
# Data Owner's pr2-data-owner.md (ruled). No Tool Owner or Threshold Owner path.
# Drafted by the session; the human rules it as Product.
ruling: pr2
seat: Product
authorises:
  - CLAUDE.md
  - SPEC/00-overview.md
  - SPEC/02-seats-and-change-gates.md
  - SPEC/03-evals-regression-redteam-corpus.md
  - milestones/README.md
  - milestones/M02/runs/f2_2_three_doors.yaml
  - milestones/M03/runs/**
evidence:
  - SPEC/00-overview.md#8-M03
  - SPEC/02-seats-and-change-gates.md
  - SPEC/03-evals-regression-redteam-corpus.md
  - milestones/M03/rulings/pr1.md
  - milestones/M03/feasibility.md
  - milestones/M03/runs/guardrail_probes.md
  - milestones/M03/runs/f3_5_amendment.yaml
  - https://github.com/andaro74/agentkeel/actions/runs/36252383220
  - evals/history/0225d84ee58dc34bb8a3031edcea5f07c19529ec.json
pr: 20
---

# Ruling: M03 PR 2, Product

**Draft.** Written by the session for the human, who rules it as Product.

## What this PR is

PR 2 of M03, the measure: every seed's reader, the guardrail on the call,
the red-team suite, the corpus and its ingest pipeline, and claim 3's
checks required on every agent envelope from the commit that landed the
last reader (`f82a02a`). Row 3 moves to 2 / 4. Its Measured cell is not
written here: PR 2's CI run and its envelope are the measurement, and the
cold review, not this file, decides whether the PR shape holds.

## Rulings (the human, 2026-09-25 and 26)

1. **Unsure C** (`open.md` row 10): image `822fe2b5` deleted by the human
   (`row10_image_822fe2b5.yaml`); the two `doors:` blocks collapsed to the
   filled one, lines 5 to 17 (`f2_2_three_doors.yaml`; the reading
   unchanged, the first block kept at tag `m02`).
2. **The commit order** of SPEC/03 §6, thirteen commits, two AWS stops.
3. **SPEC/03 §6's ingest bullet** named the stack before it was built
   (`ad4ab14`, repaired `fa985cb`): a separate stack deployed by the
   human, Object Lock COMPLIANCE for 1 day (the human as Security, a demo
   setting), and §8's list of what is not attempted.
4. **SPEC/00 §9 amended** (on `rule-owner`'s F2 on PR 2): the blocked
   intent is deal terms requested for **a competitor**. Every wording about
   deal terms in general blocked `g-006`; the rule built and measured is
   `sending-terms-to-a-competitor`.
5. **SPEC/00 §8 M05** says what the narrowed deny denies (cold N8).
6. **CLAUDE.md**: golden/corpus overlap, named and described (`open.md` row 6).
7. **The run records** under `milestones/M03/runs/` are the human's
   outputs, transcribed by the session with headers: the read-back before
   (8 mismatches, each a row the deploy was to change) and after (0 of
   79), the guardrail probes of versions 1 to 4, the wording trials, seed
   S5's attempt with `admitted_at`, the image record.

## Unsure, carried

| # | Item | Seat | When |
|---|---|---|---|
| A | SPEC/00 §9's "8-10 invented documents": seven with S5, six admitted | Product | M04 PR 1, with the knowledge base |
| B | ADR-0009 does not read a narrowed definition under the same name | Product | M04 PR 1 (an ADR-0009 amendment, or a line that says it stays one key) |
| C | The guardrail's own plants (`g-013`, `g-015`) have no named rule, so dropping `sending-terms-to-a-competitor` silences no plant (`rule-owner` F1) | Rule Owner | M03 PR 3 (the human deferred it: any byte of `guardrail.yaml` is a new version) |
| D | The runtime half of the guardrail on the call: first read by the merge deploy's load check (security F1, repaired as far as the tree can) | Security | the merge |
| E | `g-010`'s answer is mostly in the corpus at M04 (`data-owner` F1) | Data Owner | M04 PR 1 |
| F | Version 4's `get-guardrail` description | Rule Owner, Security | **done** `a9c8ff6` |

## What a reader can run to falsify this PR

```
uv run pytest -q                                   # no xfail left: every seed read by its reader
uv run pytest tests/test_m03_seeds.py -v           # S1 to S7 and the two guards
make validate                                      # fifteen checks
make ledger                                        # exit 0: rows 0 to 2 unchanged
make plants                                        # 0 in the last run, 7 in the next
uv run python -m src.gates.ruling_cited --base d2d1e6d --pr 20
```

## The measurement

PR 2's CI run [36252383220](https://github.com/andaro74/agentkeel/actions/runs/36252383220),
envelope `evals/history/0225d84ee58dc34bb8a3031edcea5f07c19529ec.json`
(the bot's commit `506c8ed`), ruled **GREEN** by the gate at its own
commit: **plants 7 of 7** (`g-013`, `g-015` to `g-020`; `guardrail_hits`
7); `corpus_fingerprint` `e12988c5…`, equal to the gate's reading; F3_1,
F3_2, F3_3, F3_5 and F3_6 pass, F3_5 from CI's own lookup of seed S5 in
AWS; no regression; `g-014` and `g-021` never passed; `mode: runner`,
guardrail `1088aw3ujhyd:4`; 46,991 + 5,424 tokens against the cap of
150,000. `make ledger` still matches rows 0 to 2. The row's Measured cell
is PR 4's to write from this envelope, or from a later one if the tree
that ships changes.
