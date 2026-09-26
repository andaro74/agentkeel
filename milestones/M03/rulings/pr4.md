---
# M03 PR 4 (#22), the close. Product's key. Every path this PR changes is
# Product's (milestones/**, docs/**). The cold review is Engineering's file,
# pr4-engineering.md, which names only itself. Drafted by the session; ruled
# by the human as Product.
ruling: pr4
seat: Product
authorises:
  - milestones/README.md
  - milestones/M03/README.md
  - milestones/M03/attestations.md
  - milestones/M03/rulings/pr4.md
  - milestones/M03/runs/pr3_merge_deploy_load_check.md
  - milestones/M04/open.md
  - docs/milestones/M03.md
  - docs/milestones/README.md
  - docs/video/README.md
evidence:
  - SPEC/00-overview.md#8-M03
  - SPEC/03-evals-regression-redteam-corpus.md
  - https://github.com/andaro74/agentkeel/actions/runs/36270471757
  - evals/history/cb06c0dbf0019088c664c6df1ce7d67cc64f7d58.json
  - milestones/M03/rulings/pr1.md
  - milestones/M03/rulings/pr2.md
  - milestones/M03/rulings/pr3.md
  - milestones/M03/runs/pr3_merge_deploy_load_check.md
pr: 22
---

# Ruling: M03 PR 4, Product

Drafted by the session through `/close-milestone M03`; to be ruled by
andaro74 as Product.

## What this PR is

PR 4 of M03, the close, and the last: 4 / 4. It writes row 3's Measured
cell from the gate's reading of the envelope, the explainer's "What
happened", the M03 video row (not recorded), the attestations, this file,
and `milestones/M04/open.md`; `make ledger-plain` wrote
`docs/milestones/README.md`. It builds no reader and touches no seat path
but Product's.

## The measurement

Row 3's Measured cell is the line `make ledger` prints for the latest
CI-written envelope, copied by a script from its output, not typed:
`evals/history/cb06c0dbf0019088c664c6df1ce7d67cc64f7d58.json`, run
[36270471757](https://github.com/andaro74/agentkeel/actions/runs/36270471757),
committed by `github-actions[bot]` (`013a1c5`). Its verdict is GREEN, so
row 3's State is GREEN. `make ledger` exits 0.

**Why this envelope.** It is PR 3's run on the tree that ships.
`main`'s run 36272077628 found nothing measured changed since `cb06c0d`
and ruled that envelope GREEN without spending; this PR changes only paths
`evals.yml` does not measure, so its run does the same. It is in
`mode: runner`. **No envelope reads the runtime at guardrail version 5.**
The merge deploy's load check (run 36272077619, transcribed in
`runs/pr3_merge_deploy_load_check.md`) is a log. Carried as M04 `open.md`
row 10. The session's first plan expected this PR's run to be the first
runtime envelope at version 5; the workflow's skip rule says it cannot be.

## Rulings

1. **SPEC/03 cuts 1 to 4 are recorded as taken here, not before.** The
   Braintrust mirror with its divergence check and redaction (cut 1), the
   Bedrock Evaluations judge pinned in the manifest (cut 2),
   `admitted_false_fails.json` (cut 3) and the FRAGILE state (cut 4) are in
   SPEC/00 §8's M03 build list. None was built, and no PR of M03 took one,
   though SPEC/03 §9 allowed each "only if the cap is threatened". The cap
   is now spent. Each goes where §9 names: M04 (M04 `open.md` row 19). Cut
   5, Promptfoo, goes to M05 (row 25), and with it `pr1-rule-owner.md` N4.
   This is found at the close and says so; it is not a relaxation of any
   bar, and no row-3 RED condition reads it.
2. **Unsure items closed here** (the rest are in M04 `open.md`):
   - #19 E: `red-teamer` was exercised twice more in PR 2 (#20's first
     comment); nothing depends on whether it ran as a registered type.
   - #20 D: read by PR 2's merge deploy's load check, a log.
   - #21 B: the eval role's use of version 5 is read by `cb06c0d`; the
     runtime's `GuardrailIdentifier` condition at `:5` by run 36272077619's
     load check (20 answers, 0 errors), a log. Nothing more is claimed.
   - #21 C: closed negatively. No `mode: runtime` envelope at `:5` exists
     at the close (M04 `open.md` row 10).
3. **Findings that had no seat or no date before this close** are given
   one in M04 `open.md`: rows 9 (`pr2-engineering` N7), 11
   (`security-reviewer` F1 on `606bece`), 17 (`topics_apply_to`), 18 (the
   uncited clauses), 19 (cuts 1 to 4), 21 (`pr2-engineering` N9), 23
   (SPEC/00 §3 and §10.3 wording).

## Numbers changed from a draft, and why

- The explainer's plain sentence "each blocked by the rule named for it"
  became "counted as blocked only when the rule named for it fired": the
  envelope carries the count, not the topics (cold review F4).
- "What M03 is to show" became "What M03 shows" only with the limits
  named: the table route refused in a test, the bucket's locks untried,
  the admin able to go around them (cold review F5).
- The seed claim "each reader switched off, its seed failed again" was
  removed: the tree records the markers coming off with their readers,
  not a switch-off run (cold review F1). For S1 and S2 the close detail
  says it is recorded, not measured (second read F3).
- "Four of the seven planted routes were refused only in a copy" became
  six: row 3 lists S1, S2, S3, S4, S6 and S7 as refused in a copy; only
  S5 was tried for real (second read N1).

## The cold review

`engineering-cold-reviewer` read `git diff c73eb9e...e20d3c9` (7 files)
and row 3: 0 BLOCK, 6 FINDING, 6 NOTE. The table is in
`pr4-engineering.md`; the report is in the PR body verbatim. Every finding
is repaired in `ae2debf` or `e240864`, or by this file (F2). A second
cold read of the repairs, `e20d3c9...bab1e0b` (8 files), found 0 BLOCK, 3
FINDING, 6 NOTE, repaired in the commit after it; its F3 is carried as
M04 `open.md` row 38. No other seat
subagent applies: the diff touches no Rule Owner, Data Owner, Tool Owner,
Threshold Owner or Security path.

## What a reader can run to falsify this PR

```
make ledger                                    # exit 0; row 3 GREEN, 4 / 4
make ledger-plain && git diff --exit-code docs/milestones/README.md
make validate                                  # fifteen checks
uv run pytest tests/test_m03_seeds.py -v       # seven seeds and two guards pass
make plants                                    # S1 to S7, each reader in the tree
git diff --stat c73eb9e HEAD                   # docs/** and milestones/** only
git log m02..HEAD --format=%an -- evals/history   # github-actions[bot] only
```

A Measured cell that differs from `make ledger`'s line, a State that is not
GREEN, a path outside Product's, or a row-3 RED condition holding
falsifies it. `git tag m03` is the human's, on `main`, after the merge and
after the attestations are signed.
