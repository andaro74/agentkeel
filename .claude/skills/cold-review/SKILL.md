---
name: cold-review
description: The cold read of one PR before it opens. Runs engineering-cold-reviewer on the diff and the ledger row only, collects the other seat reports for the paths the PR touches, and produces the ruling file that cold-review-ruling requires on main.
---

# /cold-review

Arguments: the milestone id `MNN`, the PR number, and the base ref
(default `main`). If the PR number is not known yet, use the number the
PR will open as; the ruling file's `pr` must match it.

This skill is the transcript of the cold review of M00 PR 2
(`milestones/M00/rulings/pr2.md`, "Cold review"). It is run before a PR
opens, and again if the diff changes materially after a seat has read it.

## The rule that makes it cold

The reviewer reads **the diff and the milestone's ledger row, and nothing
else**. Not the PR description, not the feasibility note's argument, not
the commit message bodies. The diff has to stand up without the story
that came with it. If you have to explain the diff to the reviewer, the
diff is the problem.

## Run

1. `engineering-cold-reviewer`, given `MNN`, the PR number and the base
   ref. It returns BLOCK / FINDING / NOTE, each quoting file and line.
2. The seat subagent for every other path the diff touches:

   | Path | Subagent |
   |---|---|
   | `rules/**`, guardrail id or version | `rule-owner` |
   | `evals/goldens/**`, `data/**` | `data-owner` |
   | `tools/**`, `may_call`, `may_be_called_by` | `tool-owner` |
   | `thresholds.yaml`, judge rubric, judge or agent model id | `threshold-owner` |
   | `.github/workflows/**`, `infra/**`, key policy, cosign identity | `security-reviewer` |
   | `SPEC/NN` before PR 1 | `product-spec-reviewer` |

   Do not invoke a specialist that is not in the tree (R8).

   There is no subagent for Product's other paths — `milestones/**`,
   `docs/**`, `CLAUDE.md`, `.claude/skills/**`. A close PR is almost
   entirely those, and `engineering-cold-reviewer` reads them as part of
   the diff. That is the arrangement, not an oversight; if a milestone
   needs a Product reviewer beyond SPEC/NN, it is added at the milestone
   that first needs it (R8), not assumed here.

3. Paste every report into the PR body **verbatim**, with its counts.
   The `product-spec-reviewer` report goes into
   `milestones/MNN/feasibility.md` instead.

A report is a draft. It is never a ruling. A subagent does not decide
anything; it tells you what it saw.

## What to do with what comes back

- **BLOCK**: either repaired in this PR, or ruled by the named seat
  before the PR opens, and marked as one or the other in the ruling file.
  A BLOCK that is neither is a PR that does not open.
- **FINDING**: repaired, or recorded in the ruling file with the seat who
  owns it and when it is settled. A table of `# | Finding | Status` is
  enough.
- **NOTE**: in the ruling file if it will matter later, dropped if it
  will not. Say which.

Repairs go in as their own commits, before the measurement, never mixed
into the commit the reviewer read. If a repair touches a measured path,
the milestone measures again: the evidence has to be of the tree that
ships.

## The ruling file

`milestones/MNN/rulings/<slug>.md`. `cold-review-ruling` fails a PR on
`main` unless a file under `milestones/*/rulings/` has this PR's number
in its front matter, so this file is what lets the PR merge.

```yaml
---
ruling: <slug>
seat: <one seat (from M01 PR 1); name the seat per path in the body>
authorises:
  - <every path this PR changes, grouped by seat, with the ruling per group>
evidence:
  - <the CI run URL and the envelope, if this PR measured>
  - <SPEC/00-overview.md#8-MNN, or the ADR, for each authorised group>
pr: <number>
---
```

**Two keys, two files** (Product with the Threshold Owner, M01 PR 1). A
ruling file has one seat in `seat:`. A two-key change cites two ruling
files, each with one seat, both with the same `pr:`. The file of the seat
that owns the path authorises it; the other file names the path in its
body and says its key is given there. Name them
`<slug>.md` and `<slug>-<seat>.md` (e.g. `pr1.md` and
`pr1-threshold-owner.md`). M00's multi-seat ruling files stand as written.

Then the body: what the cold review found, what was repaired, what stands
for the seats, and what a reader can run to falsify the PR's own claims.
That last section is the point of the file. Write the commands.

`make validate` checks this front matter: the five fields, and that every
`authorises` path matches something in the tree.

## Refuse to open the PR if

- a BLOCK is neither repaired nor ruled;
- a path in the diff has no seat, or a seat that no ruling names;
- the PR shape is wrong for its position in the milestone (CLAUDE.md,
  "The PR shape"): a PR 1 that makes the plant pass, or a last PR that
  builds the thing that reads the plant;
- `authorises` names a path the diff does not touch, or misses one it
  does.

You write the diff and the ruling file. You do not merge.
