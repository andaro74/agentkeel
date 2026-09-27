---
# M04 PR 1 (#23), the plant. Product's key. One seat per file: the
# Threshold Owner's is pr1-threshold-owner.md, the Data Owner's
# pr1-data-owner.md, the Rule Owner's pr1-rule-owner.md, Engineering's
# pr1-engineering.md (with the cold review). The PR touches no Tool Owner
# or Security path.
ruling: pr1
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/02-seats-and-change-gates.md
  - SPEC/04-model-swap.md
  - CLAUDE.md
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
  - docs/adr/ADR-0010-the-pins-lifecycle-fields-are-the-threshold-owners.md
  - docs/milestones/M03.md
  - docs/milestones/M04.md
  - docs/milestones/README.md
  - docs/video/README.md
  - docs/video/milestones/M03.mp4
  - milestones/README.md
  - milestones/M04/**
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md
  - milestones/M04/feasibility.md
  - milestones/M04/open.md
  - milestones/M04/runs/model_access_2026-09-26.md
  - docs/adr/ADR-0005-video-follows-the-tag.md
pr: 23
---

# Ruling: M04 PR 1, Product

The rulings below were made by andaro74 as Product, on 2026-09-26 and
2026-09-27, each "as proposed", before the seeds or before this PR
opened. This file was drafted by the session from them; the human signs
it off before the PR opens.

## What this PR is

PR 1 of M04, the plant: 1 / 4. SPEC/04 first (`78b042e`), reviewed by
`product-spec-reviewer` (1 BLOCK, 12 FINDING, 4 NOTE; `feasibility.md`
§1), revised once on the rulings. Five seeds, one commit each, before any
reader: `a16e2c7` S1, `c6b6cb8` S2, `6f18507` S3, `63033b7` S4, `8994dcb`
S5; S3's and S4's raw runs remade at `2dc81ae` and `e0ce2ce`, before any
reader. Six strict expected failures. Nothing that makes claim 4 pass.

## The rulings

1. **"Promotes" means mergeable, not merged.** The equivalent swap PR has
   every required check green and is closed unmerged. Product, with the
   Threshold Owner (`pr1-threshold-owner.md` ruling 1).
2. **The knowledge base and retrieval go to M06**, with the cached-answer
   seed, F3.5's second half and `g-014`; FRAGILE to M06. SPEC/00 §8 M06 and
   §9 amended. A third move is a SPEC/00 amendment, not a cut.
3. **`model-watch`, the judge (with its rubric, graded examples and
   `admitted_false_fails.json`), the Braintrust mirror and
   `deprecated_after` set from Bedrock go to M07**; k6 to M05. SPEC/00 §8
   M07 amended.
4. **BLOCK 1, M02's pattern.** From PR 2's merge, `F4_1` and `F4_2` come
   from the seed tests alone, test-only witnesses. The swap PRs are opened
   during PR 2 and read by PR 3's run, a named P3 exception; a swap PR's
   run never reads itself. PR 3 is both that read and the repair; if either
   misses, row 4 closes RED at PR 4. There is no fifth PR.
5. **The findings of `product-spec-reviewer`**, F2 to F13 and N14 to N17,
   as `feasibility.md` §2 rules them; the seat reports and the cold review
   as §2.4 and §2.5 rule them.
6. **SPEC/00 amended** in §3 (the poisoned corpus answered in the bucket
   at M03, in the answer at M06), §5 and §5.1 (the whole pin is the
   Threshold Owner's; `deprecated_after` in the two-key rule), §8 M04, M06
   and M07, §9 (seven documents; the knowledge base to M06; CORRECT
   includes grounding from PR 2) and §10.3 rows 03 and 04. `make
   ledger-plain` regenerated `docs/milestones/README.md`. CLAUDE.md's seat
   line follows SPEC/00.
7. **ADR-0009 amendment 1** (entry 6: `deprecated_after` moved later,
   nulled or removed, with the model id unchanged, is a relaxation) and
   **ADR-0010** (`profile` and `deprecated_after` are the Threshold
   Owner's) accepted; SPEC/02 §2 amended inline. Each authorises the
   Threshold Owner, whose key is `pr1-threshold-owner.md`.
8. **`open.md`**: all 38 rows and the two new items answered or moved with
   a seat and a date (`feasibility.md` §6). Row 2 stays one key at the
   gate, with a second key filed by hand for a definition change until the
   Rule Owner's amendment (M05 open, or the first `rules/**` change).
9. **The M03 video** (`31a026c`, row 24): committed at tag `m03`, 3:36,
   4,323,437 bytes, LFS. **Confirmed:** the row's Shows cell was the plan
   written at M03's close; andaro74, as Product, watched the recording on
   2026-09-27 and confirmed it shows what the cell lists.

## What a reader can run to falsify this PR

```
git show a16e2c7 c6b6cb8 6f18507 63033b7 8994dcb 2dc81ae e0ce2ce --stat   # no reader in any
uv run pytest tests/test_m04_seeds.py                                      # 6 xfailed
uv run pytest tests/test_m04_seeds.py --runxfail                           # each fails on its planted line
make plants                                                                # S1 to S5 listed
make validate                                                              # fifteen checks, as at m03
make ledger                                                                # exit 0; row 4 Measured empty
git diff 2addb95...HEAD -- thresholds.yaml agents/ infra/ src/baseline/ rules/ data/   # empty
```
