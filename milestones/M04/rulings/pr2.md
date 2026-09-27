---
# M04 PR 2 (#24), the measure. Product's key. One seat per file: the Data
# Owner's is pr2-data-owner.md, the Threshold Owner's
# pr2-threshold-owner.md, Security's pr2-security.md, Engineering's
# pr2-engineering.md (with the cold review). The PR touches no Rule Owner
# or Tool Owner path.
ruling: pr2
seat: Product
authorises:
  - SPEC/04-model-swap.md
  - milestones/README.md
  - milestones/M04/**
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md
  - milestones/M04/feasibility.md
  - milestones/M04/open.md
  - milestones/M04/rulings/pr1.md
pr: 24
---

# Ruling: M04 PR 2, Product

Drafted by the session; the human rules as Product before the merge.

## 1. What this PR is

PR 2 of row 4, the measure: every reader SPEC/04 §6 lists, each landing
with its seed's marker off, and the gate requiring `F4_1`, `F4_2` and
`F4_4` on every agent envelope from `15047b4`, and `F4_3` where the pin
moved. Nothing in it decides the swap PRs: PR 3 wires their read and is
it (SPEC/04 §5.1, the named P3 exception).

## 2. The expected line, restated before the run

Row 4 and SPEC/04 §7 now say, for this PR's run: S1 to S5 refused by
their readers; refagent under grounding ordinary 9/9, traps 2/2 (`g-021`
retired, nothing added), fewer being the finding; refagent's A-vs-A zero
diff on this PR's own run, by the `a-vs-a` label; the control's diff
recorded, not gated; p95 and tokens within their bars. The run is read
from its envelope, not from this file.

## 3. Rulings on the seat reports, by the human, 2026-09-27

| Report | Item | Ruling | Where |
|---|---|---|---|
| data-owner | F1 (F5 on PR 1) | Correct needs the golden's own row, agent only | `pr2-data-owner.md` §2; SPEC/04 §2 |
| data-owner | F2 | The two key files are in this PR | `pr2-data-owner.md`, `pr2-threshold-owner.md` |
| data-owner | F3 | The Tool Owner's question goes to M06 with the absence form | `pr2-data-owner.md` §1; SPEC/04 §2 |
| threshold-owner | BLOCK 1 | As data-owner F2 | the two files |
| threshold-owner | F1 | The median leaves out F4_4 fails unless all failed | `pr2-threshold-owner.md` §1 |
| threshold-owner | F2 | A deleted `relative` is refused from `15047b4` | `pr2-threshold-owner.md` §1 |
| threshold-owner | note 8 | ratings-helper's comment reworded | its manifest |
| threshold-owner | note 9 | A merged swap's first run in a new mode fails F4_4: M05 | M05 `open.md` at close |
| security-reviewer | F1, F3 | Carried to M05 (`open.md` rows 26, 30, 40) | `pr2-security.md` §3 |
| security-reviewer | F2 | The `a-vs-a` label is on the PR before the measuring push | `pr2-security.md` §2 |
| security-reviewer | F4 | Answered from run 36331360122: 93 s, twice is about 190 s | `pr2-security.md` §2 |
| security-reviewer | F5 | `F4_2` from the S2 test is a test-only witness until PR 3 | `pr2-security.md` §1; row 4 |
| security-reviewer | note (PR 3) | The equivalent swap's read needs GitHub's evals run too | `pr2-security.md` §3 |

## 4. Carried

`open.md` rows 11 and 22 item i stay M05 (SPEC/04 §9 cut 2 for row 11,
since this PR's run is in the runner). Every other row PR 2 was dated to
is answered in `milestones/M04/README.md`, PR 2 detail.
