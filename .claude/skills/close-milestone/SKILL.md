---
name: close-milestone
description: Close milestone MNN. Copies the measured cell from the CI-written envelope, fills the explainer's "What happened", moves every finding and every Unsure item to a named home, writes the attestations and the ruling file, and refuses to tag if any of that is missing.
---

# /close-milestone

Argument: the milestone id, `MNN`. If none was given, ask for it and
stop.

This skill is the transcript of M00 PR 3, done by hand
(`milestones/M00/rulings/pr3.md`, `milestones/M00/README.md` close
detail). From M01 on, a milestone closes only through it.

The close PR is PR 3 or PR 4 of the milestone, never PR 5. If the cold
review of PR 2 found nothing to repair, PR 3 is the close. A fifth PR is
a RED close with the finding as the result; do not propose a cap raise.

## What the close PR contains

1. The `Measured` cell in `milestones/README.md`, copied from the
   CI-written envelope, with the commit and the run URL in it.
2. `docs/milestones/MNN.md` — **What happened**, and the Watch line.
3. The video README entry.
4. `milestones/MNN/attestations.md` — the lines the seats sign.
5. `milestones/MNN/rulings/<slug>.md` with this PR's number.
6. `milestones/M<NN+1>/open.md` — everything carried forward.
7. `git tag mNN`, on `main`, **after** the merge. Never on the branch.

## Read the evidence, never the prose

```
make ledger
```

It prints each row and, at the end, what the latest CI-written envelope
reads. The `Measured` cell is that line, copied. Do not retype it, do not
round it, do not summarise it. `make ledger` exits 1 if the cell differs
from the envelope, and that is the first refusal below.

A local run (`evals/local/`) is not evidence. An envelope written by
anything but `verdict.build`, or committed by anything but CI, is not
evidence.

## Findings and Unsure items

Collect every **Finding** raised anywhere in this milestone: the
feasibility note, the ruling files, the seat reports, the cold review.
Each one gets a row in the close detail with its **home**: the file that
holds it and the seat and milestone that will act on it. A finding whose
home is "we should look at that" has no home.

Collect every **Unsure** item from every PR body in this milestone. Each
one is either ruled here, with the seat named, or moved to
`milestones/M<NN+1>/open.md` with a seat and a date of either
"before M<NN+1> PR 1" or "at M<NN+1> open".

## Then

- `make ledger-plain` rewrites `docs/milestones/README.md`. Never edit
  that file by hand.
- `make validate`, `uv run pytest -q`.
- Write the ruling file. Its `evidence` names the envelope, the run URL,
  and the milestone's rulings.
- Open the PR. Do not merge. The tag comes after the merge.

## Refuse to tag if

Check all three before you write anything, and report all three together.

1. **The measured cell and the envelope disagree.** `make ledger` exits
   1. The cell is wrong or the envelope is not the one the cell names.
   Fix the cell, never the envelope.
2. **A Finding has no home.** A finding raised in this milestone with no
   file holding it, or with no seat and milestone named to act on it.
   List each one.
3. **An Unsure item lacks a named seat and a milestone.** An item in any
   PR body of this milestone that is not ruled here and is not in
   `milestones/M<NN+1>/open.md` with both.

Also refuse if:

- the explainer's **What happened** is empty, or its numbers are not the
  envelope's;
- the State in the ledger is not the verdict in the Measured cell;
- a milestone that closes with no measurement is not RED. A close without
  a measurement is RED, never GREEN, never UNMEASURED-and-quiet;
- the PR count would be five.

Say which one it is, name the file, and stop. Do not tag, do not merge,
do not soften the row. A RED row that is true is worth more than a GREEN
row that is arranged.

## The words

No "governed", "secure" or "proven" about a control that has not fired on
its seeded case. Numbers over adjectives. If the milestone is GREEN,
write in the explainer what GREEN does **not** mean; at M00 that sentence
was "GREEN means nothing regressed against an empty history; it does not
mean 2 of 15 passing is good."
