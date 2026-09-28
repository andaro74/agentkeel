---
# M05 PR 1 (#30), the plant. Product's key. One seat per file: Security's
# is pr1-security.md (the workflow, and R5's second key), Engineering's
# pr1-engineering.md (with the cold review). The PR touches no Rule Owner,
# Data Owner, Tool Owner or Threshold Owner path.
ruling: pr1
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/05-containment-and-evidence.md
  - .claude/skills/close-milestone/SKILL.md
  - .claude/skills/open-milestone/SKILL.md
  - docs/milestones/M04.md
  - docs/milestones/M05.md
  - docs/milestones/README.md
  - docs/video/README.md
  - docs/video/milestones/M04.mp4
  - milestones/README.md
  - milestones/M05/**
evidence:
  - SPEC/00-overview.md#8-M05
  - SPEC/05-containment-and-evidence.md
  - milestones/M05/feasibility.md
  - milestones/M05/open.md
  - milestones/M04/rulings/signoff.md
  - docs/adr/ADR-0005-video-follows-the-tag.md
pr: 30
---

# Ruling: M05 PR 1, Product

Drafted by the session; the human rules as Product before the merge.

The rulings below were made by andaro74 as Product on 2026-09-28, before
the draft or "as proposed" on `product-spec-reviewer`'s report, and all
before the first seed.

## What this PR is

PR 1 of M05, the plant: 1 / 4. `open.md` row 44 first (`5206214`), then
M04's video (`38bf3a0`, `f74a823`), then SPEC/05 (`11490e0`), reviewed by
`product-spec-reviewer` (1 BLOCK, 17 FINDING, 4 NOTE; `feasibility.md`
§1) and revised once on the rulings. Seven seeds, one commit each, before
any reader: `142a2a9` S1, `962ea72` S2, `bfd17c4` S3, `d1c1b0f` S4,
`f8601c3` S5, `b1dc6c4` S6, `06f95d9` S7. Then row 5, its README and the
explainer draft (`c8c21eb`), `open.md` row 1 (`47f386d`), row 44's skill
step (`601fc8b`), and the feasibility note's §3 to §7 (`cc36e31`). Then
the repairs on the cold review and `security-reviewer`, before any
reader (`feasibility.md` §2.5): the seed tests and run files (`e38747b`),
`F5_1` alone on every envelope with the prose corrected (`f8b3e04`), and
the workflow comment (`457e04b`).

## Rulings

1. **The security account** (before the draft). The human creates and
   provides a second AWS account as the security account during PR 2.
   R3's two accounts are the agent account and this one.
2. **Retention** (before the draft; finding 1). The audit bucket's lock is
   COMPLIANCE with one day of retention through M05; seven years is M08's.
   Moving from R5's seven years is a retention change: this file is
   Product's key, and `pr1-security.md` is Security's. SPEC/00 R5 is
   amended.
3. **BLOCK 1, a named P3 exception.** S1, S2 and S6 are attempted during
   PR 2 and recorded by its run; S3, S4 and S7 need refagent's stack or
   image, deployed only from `main`, and are attempted after PR 2's merge
   deploy and recorded by PR 3's run. PR 3 is the repair and that read. A
   miss closes row 5 RED at PR 4; there is no fifth PR.
4. **Finding 16, planned at open.** The live attempts are recorded in the
   envelope's optional `containment` and read by row 5's cell, as row 4's
   cell read `swaps`; they gate no pull request. Amended before the PR
   opened (cold review F2): the check on every agent envelope is `F5_1`
   alone, from S4's and S5's seed tests, a test-only witness, and the
   ledger says so; F5.2, F5.3 and F5.4 are live only, read by the row.
5. **Finding 3.** "Modify" is deleting a version, shortening a retention,
   turning the lock off, or a policy that allows one of those; a new
   version is not a modification. S6's object is under a day old.
6. **Finding 7.** Cuts a to f and cut 1 are taken at open (SPEC/05 §9);
   cut 2, envelopes to the audit bucket, is taken only if the cap is
   threatened.
7. **Finding 9.** S4's refusal is self-reported, beside the trail's record
   of the call; the row says so.
8. **Finding 12.** SPEC/00 §10.3 row 05 reads: "An agent is stopped from
   reaching the internet, writing to another agent's files, or deleting
   its own logs, and each attempt is recorded in a separate account it
   cannot change."
9. **Finding 13.** SPEC/00 §8 M05 amended: the quarantine is a deny-all on
   the agent's role; F5.4 reads "the quarantine leaves the agent's role
   able to call its model"; Identity and the per-agent Budgets filter to
   M07.
10. **Finding 14.** Every `open.md` row placed (`feasibility.md` §6), row 19
    ruled with no SPEC/00 §5 amendment, row 22 as ruled on 2026-09-27.
11. **The M04 video** (`open.md` row 42). Product watched it on 2026-09-28:
    it shows everything `docs/video/README.md`'s Shows cell lists, with no
    deviation from the script. 3:13 (193.4 s), 3,547,769 bytes, under both
    ceilings.
12. **`open.md` row 44** is added before anything else in this PR, and the
    skills now read every ruling with the PR's number on the pushed head
    before any merge command.

The other seats' rulings on the report (findings 2, 4, 5, 6, 15 and 17,
Security; 8, Engineering; 10, the Data Owner and Engineering; 11, the
Threshold Owner) are recorded in `feasibility.md` §2 with their seats,
and are carried into PR 2's files by the seats that own the paths.

## What a reader can run

```
git show 142a2a9 --stat   # and each seed: the seed, its test, one README row, one SEEDS_M05 line, no reader
uv run pytest tests/test_m05_seeds.py -q              # 7 xfailed
uv run pytest tests/test_m05_seeds.py -q --runxfail   # 7 failed, each for feasibility.md section 3's message
make plants     # S1 to S7; the observer and the two stacks "not in the tree yet"
make validate   # sixteen checks, ok
make ledger     # exits 0; row 5 OPEN, Measured empty, 1 / 4
git lfs ls-files | grep M04.mp4
```

Any seed test that passes, or fails for another reason, makes this PR's
plant false.
