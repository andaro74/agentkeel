---
adr: ADR-0008
title: A ruling is on main at the merge commit; the gates read the merge ref
status: Accepted
date: 2026-09-22
seat: Product
authorises:
  - Security  # SPEC/00 §5, the `ruling-cited` gate's "on `main`"; R9's last sentence
amendments: 0
---

# ADR-0008 — A ruling is on `main` at the merge commit

## Context

SPEC/00 §5 says `ruling-cited` requires "a ruling on `main` whose
`authorises:` matches that path", and R9 says "No PR in this repo merges
before its ruling file is on `main`." Since M00 PR 2 the required check
`cold-review-ruling` has checked out the PR's merge ref, so a ruling the
PR carries counts. `milestones/M02/open.md` row 1 carried the gap between
the words and the check to M02 PR 1, Security; `product-spec-reviewer`
finding 8 on SPEC/02 said SPEC/02 could not settle it by reinterpreting
SPEC/00, because SPEC/00 wins.

Read literally, "on `main` before the PR merges" means every PR needs a
ruling PR before it. With a cap of four PRs per milestone that is two
milestones' worth of PRs for one, and the ruling PR would itself touch a
seat-owned path, `milestones/**`, and need a ruling before it.

## Decision

1. **A ruling file is on `main` at the merge commit of the PR that
   carries it.** That is the first moment anything in the PR is on
   `main`, and it is what R9's sentence means: the merge commit that puts
   the diff on `main` puts the ruling there in the same commit, and no
   diff reaches `main` by any other commit (`allowed_merge_methods:
   ["merge"]`, `infra/ruleset/main.json`).
2. **`cold-review-ruling`, `ruling-cited` and `two-key` read the PR's
   merge ref.** A ruling the PR carries counts. At this ADR's date only
   `cold-review-ruling` exists and it checks `pr:` alone; from M02 PR 2
   what the gates check is what makes it a ruling and not a note: `seat:` is the
   CODEOWNERS owner of every path it authorises; `authorises:` covers
   every seat-owned path in the diff; a relaxation has a second file from
   a distinct seat with the same `pr:`; the file is under `milestones/**`
   and stays on `main` keyed by PR number (SPEC/02 §1, §2).
3. SPEC/00 §5's `ruling-cited` line is amended to read "cites a ruling in
   the PR's merge ref, on `main` at the merge commit". R9's last sentence
   is amended to "No PR in this repo merges without its ruling file in
   the merge commit."

## Consequences

- One person can write the diff and the ruling. R1 already says every
  seat is one person and no gate waits for a human. The control is that
  the change is **named** under the seat that owns the path, in a file
  that outlives the PR; not that someone else agreed.
- `milestones/M02/open.md` row 1 closes on this ADR. The workflow
  header's "by design at M00" line was right and is now the rule.
- `SPEC/00-overview.md#8-MNN` is still a ruling that is on `main` before
  the PR: the build paths of a milestone are authorised by the SPEC, and
  a PR cites the anchor. Nothing here changes that.
