---
# M09 PR 4 (#53), the close. Product's key over the Product paths this PR
# touches: the ledger (row 9's Measured cell, PRs used and State; the two
# header rows for PR 3 and the tag), this milestone's README (the row and
# the close detail), the run file's observed block (bfa4c19, written by the
# owner, carried here), the explainer, the generated ledger page, the video
# README, the quickstart's one sentence, the attestations and the four
# ruling files. Engineering's file is pr4-engineering.md (the run test's
# marker, the cold review), the Data Owner's pr4-data-owner.md (R7, R9, R11
# in words), Security's pr4-security.md (its Unsure dispositions). The
# three seat files own no path in this diff; their paths are listed here
# for the gate and their keys are given in words there.
ruling: pr4
seat: Product
authorises:
  - milestones/README.md
  - milestones/M09/README.md
  - milestones/M09/runs/f9_3_plant_run.yaml
  - milestones/M09/attestations.md
  - milestones/M09/rulings/pr4.md
  - milestones/M09/rulings/pr4-engineering.md
  - milestones/M09/rulings/pr4-data-owner.md
  - milestones/M09/rulings/pr4-security.md
  - docs/milestones/M09.md
  - docs/milestones/README.md
  - docs/video/README.md
  - docs/developer/quickstart.md
evidence:
  - SPEC/00-overview.md#8-M09
  - SPEC/09-per-agent-rules.md
  - evals/history/c503324bac926e4a3295ee7e7f68a98cf254bc42.json
  - https://github.com/andaro74/agentkeel/actions/runs/38400685274
  - milestones/M09/rulings/pr1.md
  - milestones/M09/rulings/pr2.md
  - milestones/M09/rulings/pr3.md
pr: 53
---

# Ruling: M09 PR 4, the close, Product

DRAFT until it reads "Ruled by". Drafted by the session 2026-10-13.

## What this PR is

PR 4 of 4, the close, through `/close-milestone`. The run's reading and
the ledger's cell; no repair. The one code change is the run test's marker
(`c503324`, Engineering, `pr4-engineering.md`). The envelope the cell
names was written by this PR's own CI run on that commit, from the owner's
`observed` block (`bfa4c19`), and committed by `github-actions[bot]`
(`1ebd907`). The count is 4 of 4; no fifth pull request and no cap raise.

## What is ruled here

1. **Row 9 closes GREEN.** The Measured cell in `milestones/README.md` and
   `milestones/M09/README.md` is `make ledger`'s "as row M09 reads it" line
   for the envelope for `c503324bac926e4a3295ee7e7f68a98cf254bc42`,
   copied, not retyped: planted rules fired 1 of 1; F9_1 held (read_back);
   F9_2 held; F9_3 held; F9_4 held; refagent `plants 7/7`; GREEN. `make
   ledger` exits 0. The reading matches what SPEC/09 §7 stated at open:
   fired 1 of 1, F9.1 to F9.5 held, row 9 GREEN. No number in the
   explainer differs from the envelope's; none was changed from a seat's
   wording, since none had been written.
2. **The ledger's header rows** for M09 PR 3 and for the tag `m09`:
   twenty-one checks, none new and none changed at either. Written as the
   close detail reads them.
3. **M09's video.** Not recorded at this close's opening. It is recorded
   on `main` at tag `m09` after this PR merges, as SPEC/00 §10.5 reads and
   as every video from M01 to M07 was, and committed in **M09's video
   pull request**, which carries the LFS object, the `docs/video/README.md`
   row's duration, size and sha256, the explainer's Watch line, the
   re-signed attestation 6, and the second amendment to ADR-0005 (finding
   10). That pull request is not counted against the cap, as the adoption
   PR (#1) and M04's sign-off PR (#29) are not (`milestones/README.md`,
   the note under the title; it adds its own line there). SPEC/00 §15's
   "ten videos" reads met when it merges. Why not on this branch before
   the merge: the tag does not exist yet, and the brief for this close
   says the owner records after the tag. The alternative, recording on
   this branch at `1ebd907` and committing before the merge as M08 did,
   is open to Product under Unsure 1 below; the video README row and
   attestation 6 are written for the first form.
4. **Every finding and every Unsure item has a named home.** The two
   tables in `milestones/M09/README.md`, close detail: 19 findings, each
   with a file and a seat, standing where M09 leaves them; every Unsure
   item of `#49`, `#50` and `#52`, each ruled by PR 2, PR 3, `#51` or one
   of this PR's four files, or standing with a seat. SPEC/00 plans no M10,
   so no `open.md` is written (SPEC/00 §10.5 as amended at M09 PR 1;
   SPEC/09 §11 R6: M10 is opened, if at all, by a Product ruling).
5. **SPEC/00 §15 re-read over rows 0 to 9**, the same way M08's close
   read it: four GREEN of ten; `docs-current` by hand; one act; ten
   explainers; nine videos until ruling 3's pull request; `docs/story.md`
   absent (finding 12, which M08's close did not read). Nothing moved to
   fit.
6. **The quickstart's one sentence** ("No agent with a `rules/` folder has
   been deployed yet") is corrected now that one has: the sentence was
   written at PR 2 to be true until this run, and `docs-current`'s rule
   (prose that drifts from the code) is why it is corrected here and not
   left.
7. **The run file.** `observed` as the owner wrote it in `bfa4c19`: the
   three pull request numbers, the deploy run id, the answer record's key.
   No result, no prose, nothing else; unchanged in this PR after it. The
   gate names it under this ruling because the commit is on this PR.

## What this PR does not do

No golden, no bar, no `src/baseline/`, no reader, no workflow, no
`infra/`, no `rules/`, no change to `agentkeel-studio/festival-desk` from
an agentkeel session, no deletion in AWS. The four pull requests of M09
are `#49`, `#50`, `#52` and `#53`; `#51` was the Rule Owner's version
bump, a by-hand step outside the count.

## Unsure, for Product

1. **Where M09's video lands** (ruling 3). Proposed: after the tag, in an
   uncounted video pull request. The alternative is M08's form: recorded
   on this branch now and committed before the merge, with the README row
   and attestation 6 rewritten to the hash. Product.
2. **ADR-0005's second amendment** (finding 10). Proposed text, for the
   video pull request:
   > ## Amendment 2 (M08 PR 4, 2026-10-05; written at M09's video pull request): the last milestone's video is committed at its own close
   > Product. A milestone with no next milestone has no PR 1 to carry its
   > video. M08's close committed `docs/video/milestones/M08.mp4` in M08
   > PR 4 (`milestones/M08/rulings/pr4.md`) and cited this amendment
   > without writing it. M09's video, recorded on `main` at tag `m09`, is
   > committed in an uncounted pull request after the close
   > (`milestones/M09/rulings/pr4.md` ruling 3). SPEC/00 §10.5 was amended
   > at M09 PR 1 to say so. This is ADR-0005's second amendment; none is
   > left.
   Product.
3. **ADR-0014's `status:`** (finding 14): `Proposed` to `Accepted`, one
   line, with the date `rulings/pr1.md` read "Ruled by" (2026-10-11) and
   `amendments: 0`. Proposed: in this PR before the rulings, if Product
   says so; else standing. Product.
4. **SPEC/06 §6 and the App's installation** (finding 3). If Security
   rules in `pr4-security.md` that the installation stays "selected",
   SPEC/06 §6 gains one sentence and the quickstart's first step one line
   ("ask the owner to add the repository to the platform App's
   installation"), at the next Product PR. Product.
5. **`docs/compliance/map.md`** (finding 11) and **`docs/story.md`**
   (finding 12): standing; neither written at this close. Product.

## What a reader can run

```
make ledger                                  # row 9 GREEN, 4 / 4; exit 0
make validate                                # twenty-one checks, ok
make ledger-plain && git diff --exit-code docs/milestones/README.md   # the generated page is as committed
uv run pytest -q                             # 1233 passed, 1 skipped, 2 xfailed at the close's head
git diff 79ba804...HEAD --stat               # the marker, the envelope, the documents and rulings; nothing else
git diff 79ba804...HEAD -- milestones/M09/runs   # bfa4c19 alone: the observed block
for f in milestones/M09/rulings/pr4*.md; do grep -l '^Ruled by ' "$f"; done   # all four before the merge
```

A Measured cell that is not the envelope's line, an explainer number that
is not the envelope's, a finding with no file and seat, an Unsure item with
no seat, or a fifth pull request, makes this ruling wrong.
