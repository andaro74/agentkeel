---
name: open-milestone
description: Open milestone MNN. Writes SPEC/NN, the feasibility note with the product-spec-reviewer report in it, the ledger row, the explainer draft, and the seeded false state — and nothing that makes the claim pass. This is PR 1 of at most four.
---

# /open-milestone

Argument: the milestone id, `MNN`. If none was given, ask for it and
stop.

This skill is the transcript of M00 PR 1, done by hand
(`milestones/M00/rulings/pr1.md`, `milestones/M00/feasibility.md` §1–§6).
From M01 on, a milestone opens only through it.

## Before you write anything

1. Read `milestones/README.md` (the ledger) and `SPEC/00-overview.md` §7
   (the claims) and §8 (the milestone's build list).
2. Read the previous milestone's `milestones/M<NN-1>/README.md` close
   detail and `milestones/M<NN-1>/open.md` if it exists. Items carried
   forward with "at M<NN> open" are this PR's inbox. Every one of them is
   answered here or is moved on with a new date; none is dropped.
3. Check the previous milestone is closed: its ledger State is GREEN or
   RED, not OPEN, and its tag exists (`git tag -l m<NN-1>`). One
   milestone per session. If the previous one is open, say so and stop.
4. Say back, in two sentences: the claim, and the commit or input that
   makes it false. If you cannot, stop and say so. Do not touch code.

## The order the work goes in

The order matters more than the content. Each step exists to stop the
next one cheating.

### 1. SPEC/NN

From SPEC/00 §8's entry for this milestone. It must name, in plain
sentences:

- the claim, in one sentence a director can repeat;
- the **false state**: what would have to be true in the repo for the
  claim to be false, as something a reader can go and look at;
- the falsifiers, `FN.1`, `FN.2`, …, each with what it would look like
  in the repo;
- the cut list, in the order things get cut if the milestone runs long.

A claim whose false state is not already plantable is not a claim yet.
Rewrite it until it is.

### 2. `product-spec-reviewer`, before anything else is written

Run the `product-spec-reviewer` subagent against SPEC/NN. Paste its
report **verbatim** into `milestones/MNN/feasibility.md` §1. It is a
report, never a ruling.

Then §2: rule on every BLOCK before the PR opens, naming the seat for
each. A BLOCK that is not ruled is not a BLOCK that is ignored; the PR
does not open.

### 3. Call the seat subagent for every path this PR touches

`data-owner` for `evals/goldens/**` and `data/**`, `rule-owner` for
`rules/**`, `tool-owner` for `tools/**`, `threshold-owner` for
`thresholds.yaml` and model ids, `security-reviewer` for
`.github/workflows/**` and `infra/**`, `engineering-cold-reviewer` for
`src/**`, `tests/**` and the `Makefile`. Paste each report into the PR
body. Do not invoke a specialist that is not in the tree (R8).

### 4. Plant the false state, and commit it before the reader exists

This is the step that has failed before. The seed goes in as its own
commit, with a test or a file that fails **because the thing that reads
it does not exist yet**. `git show <seed> --stat` must show the seed and
no reader.

If the seed needs a format that this milestone's later PR defines, say so
in the feasibility note and plant it as PR 2's first commit instead —
still before the code that reads it.

### 5. The ledger row

Write row N in `milestones/README.md`: claim, falsifiers, seeded commit,
expected gate output, `Measured` as `—`, `PRs used / cap` as `1 / 4`,
State `OPEN`. Write the same row with the open detail in
`milestones/MNN/README.md`.

`make ledger` must exit 0 with the cell empty.

### 6. The explainer draft

`docs/milestones/MNN.md`, the fixed structure of SPEC/00 §10.3. Fill
every section except **What happened**, which stays empty until the
close. The plain sentence comes from the §10.3 table, not from you.

### 7. Run the milestone's own checks

```
make validate
make plants
make ledger
```

`plants` must list this milestone's plant and show it has not fired.

### 8. The ruling file

`milestones/MNN/rulings/<slug>.md`, front matter `ruling`, `seat`,
`authorises`, `evidence`, `pr`. `pr` is the GitHub PR number this will
open as. Every path in `authorises` must exist in the tree or
`make validate` fails.

### 9. Open the PR. Do not merge.

PR body: what was planted, the seat reports verbatim, and an **Unsure**
section. Every Unsure item names the seat whose ruling would settle it
and the milestone by which it must be settled. An item with neither is
not an Unsure item, it is a decision you are avoiding.

## Refuse to open if

- the false state is not in the repo, or is in the same commit as the
  code that reads it;
- SPEC/NN has a BLOCK from `product-spec-reviewer` that no seat ruled on;
- the previous milestone is still OPEN, or is untagged;
- the PR contains anything that makes the claim pass. That is PR 2.

Say which of these it is, and stop.
