---
# M10 PR 4 (#57), the close. Product's key over the Product paths this PR
# touches: the ledger (row 10's Measured cell, PRs used and State; the
# `m10` header row), this milestone's README (the row and the close
# detail), the run file's observed block (14ab792, the owner's keys,
# carried here), the explainer, the generated ledger page, the video
# README's one row (ADR-0015 decision 6), the compliance map's two rows and
# one line, the two ADRs' status lines, the attestations and the four
# ruling files. Engineering's file is pr4-engineering.md (the run test's
# marker, the destination test, the cold review), Security's
# pr4-security.md (the destination policy, F3 standing), the Data Owner's
# pr4-data-owner.md (R5 on the first live records). The three seat files
# own no path in this diff but their own and, for Security, the one infra
# file; their paths are listed here for the gate and their keys are given in
# words there.
ruling: pr4
seat: Product
authorises:
  - milestones/README.md
  - milestones/M10/README.md
  - milestones/M10/runs/f10_x_caller_run.yaml
  - milestones/M10/attestations.md
  - milestones/M10/rulings/pr4.md
  - milestones/M10/rulings/pr4-engineering.md
  - milestones/M10/rulings/pr4-data-owner.md
  - milestones/M10/rulings/pr4-security.md
  - docs/milestones/M10.md
  - docs/milestones/README.md
  - docs/video/README.md
  - docs/compliance/map.md
  - docs/adr/ADR-0015-the-public-caller-an-eleventh-milestone.md
  - docs/adr/ADR-0016-two-keys-on-a-caller-admitted.md
evidence:
  - SPEC/00-overview.md#8-M10
  - SPEC/10-public-caller.md
  - docs/adr/ADR-0015-the-public-caller-an-eleventh-milestone.md
  - evals/history/14ab792156f585c9010275e6b6be3f687cee22c6.json
  - https://github.com/andaro74/agentkeel/actions/runs/39143365127
  - milestones/M10/rulings/pr1.md
  - milestones/M10/rulings/pr2.md
  - milestones/M10/rulings/pr3.md
pr: 57
---

# Ruling: M10 PR 4, the close, Product

DRAFT, written by the session on 2026-10-18 for the owner to rule as
Product.

## What this PR is

PR 4 of 4, the close, through `/close-milestone`. The run's reading and
the ledger's cell; one repair of the tree to what is deployed (the
destination policy, Security's `pr4-security.md`), no repair of a reader.
The code changes are the run test's marker (`14ab792`) and the destination
test following the policy (`e05095c`, `0ebfdbd`), Engineering's
`pr4-engineering.md`. The envelope the cell names was written by this PR's
own CI run on `14ab792`, from the owner's `observed` block in the same
commit, and committed by `github-actions[bot]` (`4de0fab`). The count is 4
of 4; no fifth pull request and no cap raise.

## What is ruled here

1. **Row 10 closes GREEN.** The Measured cell in `milestones/README.md` and
   `milestones/M10/README.md` is `make ledger`'s "as row M10 reads it" line
   for the envelope for `14ab792156f585c9010275e6b6be3f687cee22c6`,
   copied: `callers admitted 1 of 1, refused 3 of 3; F10_1 held; F10_2
   held; F10_3 held; F10_4 held; GREEN`, with refagent's `plants 7/7` and
   the M01 to M09 checks as row 9's cell has them. `make ledger` exits 0
   against it. As stated at open (SPEC/10 §7): admitted 1 of 1, refused 3
   of 3, F10.1 to F10.5 held. The envelope was written by CI run
   39143365127 on this PR's branch; a prose-only commit after it does not
   measure again, and no measured path changes after `14ab792` (the
   fixtures README under `tests/` was left as it stands for that reason,
   finding 17).
2. **The run moved to PR 4** (SPEC/10 §5.1's second exception, stated at
   open; `rulings/pr3.md`). PR 3 was the deploy path's repair; the four
   calls were made on 2026-10-18 after it merged, and PR 4's run read them.
   The row's "PR 3's run" at open reads as PR 4's by that clause, as M09's
   did.
3. **The explainer's "What happened"** carries the envelope's numbers (1 of
   1, 3 of 3, the four delays 78, 96, 107 and 235 s against 600, `g-030`
   1 of 1 through the door, refagent 7 of 7) and says what GREEN does not
   mean, first among them that a line from inside the platform's shared
   account could be filed under an agent's name (security F3, standing,
   `pr4-security.md`). No "governed", "secure" or "proven" is written. The
   `docs-writer` report on the page is in the PR body, its changes taken
   where taken and named there.
4. **The compliance map** gains E10 and row 36 for claim 10 and the claim-10
   line is rewritten; with no M11 there is no later PR to carry it to, as
   M09's finding 11 was carried to M10 PR 1. The framework lines in row 36
   are the map's convention, each marked unverified.
5. **ADR-0015 and ADR-0016 read `Accepted`**, dated the day their ruling
   files read "Ruled by" (2026-10-13 and 2026-10-15), each line naming that
   it read `Proposed` until this PR: M09's finding 14 again, corrected at
   the close rather than carried (finding 16).
6. **The video README's M10 row** reads "ruled not recorded", as ADR-0015
   decision 6 (ruled at PR 1) said the close would write it, in M09's row's
   shape. It plans, scripts and names no recording; nothing reads it.
   Product may strike the row before ruling if the standing instruction is
   read as "no row at all" (Unsure 1).
7. **No M11, no `open.md`.** SPEC/00 plans no milestone after M10 (ADR-0015);
   every finding and Unsure item stands in this milestone's close detail
   with a seat, as M08's and M09's did.
8. **The tag.** `git tag m10` on the merge commit of this PR, on `main`,
   after the merge, by the owner; never on the branch. Delete nothing in
   AWS (`pr4-security.md`, "What stands in AWS after the close").

## What was checked before this file was written

The three refusals of `/close-milestone`, each read: (1) `make ledger`
exits 0 with the cell in place; (2) every finding of this milestone has a
home in the close detail's table (`milestones/M10/README.md`); (3) every
Unsure item of every PR body (pr1 A to L, pr2 A to Q with the seat files'
own, pr3 A to J) is ruled in the close detail's Unsure table or stands
there with a seat. The explainer's "What happened" is filled with the
envelope's numbers; the State is the Measured cell's verdict; the
measurement exists; the count is four. `make validate` passes;
`uv run pytest -q` passes (the counts in the PR body).

## Unsure, each with its seat

| # | Item | Seat |
|---|---|---|
| 1 | Whether `docs/video/README.md` should carry the M10 row at all. ADR-0015 decision 6, ruled at PR 1, says it gets one at the close; the owner's standing instruction for this PR was to mention no recording. The row is written as ADR-0015 asks and says "ruled not recorded" only; strike it before ruling if the instruction wins | Product |
| 2 | The synthesised security template equals the deployed one: the owner's read in CloudShell on 2026-10-18, not in the tree. The deploy was not re-made; `pr4-security.md` records it as the owner's word | Security |
| 3 | The bypass role `m10-bypass` in the platform account and the stranger's throwaway pool `us-west-2_rXaZjWjO5`: whether each was deleted after the run, and when. No observer reads either (pr1 L); the owner's word, written here if given | Security; Product |
| 4 | The cell names `14ab792`, the envelope of the tree whose only difference from `main` was the run file, the marker and the destination policy with its test. If a later commit of this PR touches a measured path, a second envelope is written (M09 finding 20); the cell stays on `14ab792` unless Product says otherwise | Product |
| 5 | The compliance map's framework lines for row 36 are written by the session in the map's convention and marked unverified, as every row's are; `legal-compliance` did not run at this close | Product |
| 6 | The explainer says the door's records are told from a forgery by the request numbers the owner wrote down. That is the reading as built (the observer steps each record by `observed.<step>.request_id`); whether that sentence is enough for a director, or should say instead that the record's provenance is unproven, is Product's wording | Product |
| 7 | F10.5's agent-repository half stays unread (pr1 K; SPEC/10 §8): festival-desk's `callers` admission took one commit. Named in the row and the explainer; standing | Product |
| 8 | The three seat files list themselves under `authorises` while this file lists them too (cold review N4), as M09's close did; whether a seat file may key a `milestones/**` path of its own is Product's convention to state once | Product |
