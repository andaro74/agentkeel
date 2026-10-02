---
# M07 PR 3 (to open as #40), the repair. Product's key. One seat per
# file: Engineering's is pr3-engineering.md (with the cold review);
# Security's is pr3-security.md; the Threshold Owner's is
# pr3-threshold-owner.md. The PR touches no Rule Owner, Data Owner or
# Tool Owner path.
ruling: pr3
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/07-upgrade-retire-surfaces.md
  - CLAUDE.md
  - docs/adr/ADR-0011-one-stated-second-run-after-a-p95-miss.md
  - docs/adr/ADR-0012-the-reader-of-the-apps-grant-is-securitys.md
  - docs/compliance/map.md
  - docs/developer/upgrade.md
  - milestones/README.md
  - milestones/M07/**
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - milestones/M07/runs/f7_0_owner_test.yaml
  - milestones/M07/runs/pr3_expected.md
  - milestones/M07/rulings/pr2.md
  - https://github.com/andaro74/agentkeel/actions/runs/37023118799
pr: 40
---

# Ruling: M07 PR 3, Product

DRAFT for andaro74 as Product. Not ruled until this line is replaced by one that starts with the two words the gate reads.

Four things in this file were ruled by the seat in the session, on
2026-10-02, before the code that depends on them. They are recorded
here as said; the line above still has to be changed by the seat.

## 1. What PR 3 is (ruled 2026-10-02)

Row 7 says PR 3 "carries every attempt's `observed` entry to `main`".
That cannot hold. The first deploy of an agent from the template failed
in the platform's own `deploy.yml` (run 37023118799); the deploy runs
from `main`; no attempt can be made until the fix is merged.

- **PR 3 is the workflow fix plus every repair owed before the next
  attempts, merged once.** It carries one `observed` entry, the owner's
  test's.
- **PR 4 carries every other attempt's observed entry and is the
  close.** A fifth pull request is a RED close. No cap raise is proposed.
- **Row 7's own words stay.** One dated amendment is added inside the
  row's Expected cell, after the sentence it corrects. The seat agreed
  that text on 2026-10-02 before it was committed. No claim, falsifier or
  seeded case changes, and none is cut or moved.

What that costs, and is accepted: PR 4's attempts are read from the
anonymous viewpoint alone (SPEC/07 §4), and none of PR 3's repairs has
run live, so a fault one of them shows during an attempt has no pull
request left (cold review F3).

## 2. The owner's test is not re-made (ruled 2026-10-02)

It was stated before, made once on 2026-10-02, and its deploy missed
`upgrade.deploy_max_seconds` because of the platform's own workflow.
F7.0 fired. Row 7 is RED if F7.0 fired, so **M07 is expected to close
RED on it**. The attempt is not re-made and not restated so that it
reads otherwise. `runs/f7_0_owner_test.yaml` carries its one entry. The
remaining attempts are still made and measured; what stays open goes to
M08's open list at the close.

## 3. SPEC/07 §2, "a person's edit" (wording agreed 2026-10-02)

Amended as the seat agreed the wording, before the reader changed
(`8725485`, then `7cf7431`): CI's own envelope commit on an `agentkeel`
pull request is not a person's edit, when its author and committer are
both `github-actions[bot]` and every file it touches is one of the three
envelope files for another commit of the same pull request. It changes
what F7.1 reads, and is the reason it was put to the seat first.

## 4. The seat table (diff agreed 2026-10-02)

ADR-0012: `scripts/platform_check.py` and `infra/platform_grant.yaml` are
Security's. SPEC/00 §5's two rows and `CLAUDE.md`'s table follow. The
CODEOWNERS diff was shown to the seat before it was committed
(`pr3-security.md`).

## What this authorises

- **SPEC/07**: §2's dated amendment; §12's two PR 3 sections (what PR 3
  is and what it repaired; after the seat reviews, what is still unheld).
- **SPEC/00 §5** and **`CLAUDE.md`**: the two rows; `infra/platform_grant.yaml`
  in "Where things are".
- **ADR-0011** (SPEC/04 §2's second-run rule; cold review F14 on PR 2)
  and **ADR-0012**.
- **`milestones/README.md`**: row 7's amendment and 3 / 4; what
  `validate` checks at M07 PR 3.
- **`milestones/M07/`**: the PR 3 detail in `README.md`; the owner's
  test's entry in `runs/f7_0_owner_test.yaml`; `runs/pr2_by_hand.md`
  corrected; `runs/pr3_expected.md`; the four ruling files.
- **`docs/developer/upgrade.md`**, **`docs/compliance/map.md`**.

## Findings from the reviews that are Product's

| # | Finding | Status |
|---|---|---|
| cold BLOCK 1 | This file and `pr3-security.md` were cited as ruled and were not in the tree | **Written as drafts.** Clears when the seats change each DRAFT line. `infra/platform_grant.yaml` names `pr3-security.md`, so until that file is ruled on `main` every keyed job stops at its first step; a test now holds that the file it names is there and is Security's |
| cold F3 | The amendment moves the measurement into the close; no repair room is left | **Accepted, and said** in §1 above, the M07 README and SPEC/07 §12. Not said inside the row: the row's text is as the seat agreed it |
| threshold-owner F1 | PR 3 touches `infra/construct/`, so ADR-0011 gives its own run no second run | **Stated before the run** in `runs/pr3_expected.md` and in ADR-0011 |
| threshold-owner F2, F4 | ADR-0011 named the bar by a key that is not in `thresholds.yaml`; its revert exception did not say which median | **Repaired** (`2c6031f`) |
| threshold-owner F5 | `two-key` reads the date in `agentkeel` only | **Said** in SPEC/07 §12 and the compliance note; to M08's open list |
| cold N7 | `docs/developer/upgrade.md` spoke of a retirement's check in the present tense | **Repaired** |
| platform-architect 1 | "ruled" for items 13a to 13n, against a heading in `pr2-security.md` that says "not ruled" | **Said on what it rests**: that file's first line rules it as written, which the seat confirmed in the session on 2026-10-02 ("item 13 (13a to 13n) ruled as written"). `pr3-security.md` rules the items PR 3 builds by item |

## What goes to M08's open list at the close

Named in SPEC/07 §12's last paragraph. Not written to
`milestones/M08/open.md` here: one milestone per session, and that file
is the close's.

## What a reader can run

```
make validate            # 20 checks
make ledger              # exit 0; row 7 OPEN, 3 / 4, Measured empty
git diff 3bfd074 -- milestones/README.md | grep "^[-+]| 7" | wc -l      # 2: one row out, one in
git diff 3bfd074 --word-diff=porcelain -- milestones/README.md | grep "^-" | grep -v "^---"   # only "2 / 4"
grep -n "Amended at M07 PR 3" SPEC/07-upgrade-retire-surfaces.md
gh api repos/agentkeel-studio/owner-check/pulls/1 --jq '[.merged_at,.merge_commit_sha]'
gh api repos/andaro74/agentkeel/actions/runs/37023118799/jobs --jq '.jobs[]|[.name,.conclusion]|@tsv'
```
