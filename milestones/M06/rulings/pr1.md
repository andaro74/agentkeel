---
# M06 PR 1 (#34), the plant. Product's key. One seat per file:
# Engineering's is pr1-engineering.md (with the cold review). The Security
# seat's rulings at open (rows 2, 3, 48; BLOCK 1 with Product; NOTE 23 with
# Product) are recorded in feasibility.md section 2 and in
# runs/security_account.md, on Product paths; the PR touches no Security,
# Rule Owner, Data Owner, Tool Owner or Threshold Owner path.
ruling: pr1
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/06-developer-template.md
  - docs/milestones/M05.md
  - docs/milestones/M06.md
  - docs/milestones/README.md
  - docs/video/README.md
  - docs/video/milestones/M05.mp4
  - milestones/README.md
  - milestones/M06/**
evidence:
  - SPEC/00-overview.md#8-M06
  - SPEC/06-developer-template.md
  - milestones/M06/feasibility.md
  - milestones/M06/open.md
  - milestones/M06/runs/security_account.md
  - docs/adr/ADR-0005-video-follows-the-tag.md
pr: 34
---

# Ruling: M06 PR 1, Product

Drafted for andaro74 as Product, 2026-09-30. Not ruled until this line
reads "Ruled by".

The rulings below were made by andaro74 on 2026-09-30, in the seats
named, before any seed; the placements marked *proposed* in
`feasibility.md` §6 are ruled by this file.

## What this PR is

PR 1 of M06, the plant: 1 / 4. SPEC/06 first (`69721b6`), reviewed by
`product-spec-reviewer` (3 BLOCK, 16 FINDING, 4 NOTE; `feasibility.md` §1),
every item ruled (`8deb104` to `b11757b`), SPEC/06 revised once
(`b0aefa1`), SPEC/00 amended (`842644d`, `5887f83`). Then M05's video
(`eb5dcec`) and the security account's record (`cfeff6e`). Five seeds, one
commit each, before any reader: `672fc1d` S1a, `1a576f4` S1b, `0f3b977` S2,
`b4eb959` S3, `06c485a` S4. Then `SEEDS_M06`'s comment (`a0728ff`), row 6,
its README and the explainer draft (`8dd31a6`), the feasibility note's §3
to §7 (`4852e54`), and the cold review's F1 repair (`df084ef`, `4b8fb4e`).

## Rulings

1. **Claim 6's second developer** (at open). The author, on a fresh
   Windows user profile, as `floresinnovations` (id 336113686), with write
   on the agent repository only and no AWS credentials. Timed once the
   template works; that needs PR 2's merge, so it is a named P3 exception
   (SPEC/06 §5.1).
2. **NOTE 23** (with Security). The risk of a second personal account is
   accepted; `andaro74` is on GitHub Pro from 2026-09-30, so the author
   holds one free account. A suspension before S3 leaves F6.3 unread and
   row 6 RED.
3. **BLOCK 1** (with Security): option (d). The platform check is a
   required status check bound by `integration_id` to a GitHub App the
   platform owns, posted from `agentkeel`'s `main`; no paid plan. GitHub
   documents the `workflows` rule for Enterprise Cloud only (read
   2026-09-30); the `integration_id` field and rulesets on free
   organisations' public repositories are the documentation, not an
   attempt, and PR 2 reads the first ruleset back.
4. **BLOCK 2** (with Security). F6.2 reads "merged without the platform's
   check having run on it and passed"; S2 is a stand-in job of the check's
   name.
5. **BLOCK 3** (with Engineering). The observer writes raw lists; `build`
   compares panel 1 with the registry and writes `checks.F6_4`.
6. **The findings and notes**, all "as proposed", recorded one by one in
   `feasibility.md` §2: the owner creates each agent repository (4);
   per-agent changes automatic or timed (5); F6.1 as "mergeable" (6); the
   golden minimum and shape (7); the clock to the last of the records,
   28,800 s (8); "the template works" read from PR 2's run (9); S1 split
   (10); S4's query seeded (11); both manifests' seats in PR 2 (12); §10.3
   row 06 (13); a third cut and Act 1 during S3 (14); FRAGILE by amendment
   (15); one seat per build item, the dashboard Security's (16); row 8
   split (17); the widened trust in §8 (18); Grafana read before PR 2
   (19); seats as GitHub logins (20); the knowledge base's fourth move and
   its rows (21); PR 3 not skippable (22).
7. **The knowledge base moves to M07**, amending SPEC/00 §8 M06 and M07,
   and is recorded as a finding: its fourth move. It feeds no M06
   falsifier.
8. **SPEC/00 amended**: R1's `validate` list and §6 (seats to GitHub
   logins), §8 M06 and M07, §10.3 row 06 ("One developer creates an agent
   from the template and ships it in a day, without touching the safety
   pipeline.").
9. **`open.md` row 17.** From M06 a "stated before" commit is pushed
   before the attempt it states, so GitHub dates it.
10. **`open.md` rows 2, 3 and 48** (Security's, recorded here as ruled at
    open): the stand-in's Allow removed in M06 PR 2 in one hand deploy of
    `infra/security/` after reading `cdk diff`, the two Denies kept;
    `ecsTaskExecutionRole` deleted before PR 1 (`runs/security_account.md`);
    the management account deferred with the landing zone, re-ruled at M08
    open.
11. **`open.md` rows placed** (`feasibility.md` §6): the placements marked
    proposed there are ruled as written.
12. **M05's video** (`open.md` row 1). Product confirmed on 2026-09-30 that
    it shows all six scenes in `docs/video/README.md`'s Shows cell, with no
    deviation from the script. 3:06 (185.9 s), 2,956,668 bytes, under both
    ceilings; recorded at tag `m05` (`0b96da4`); committed as an LFS object
    whose oid is the file's sha256 (`3c291cd…`).

## What a reader can run

```
git show 672fc1d --stat   # and each seed: the seed, its test, one README row, one SEEDS_M06 line, no reader
uv run pytest tests/test_m06_seeds.py -q              # 6 xfailed
uv run pytest tests/test_m06_seeds.py -q --runxfail   # 6 failed, each with feasibility.md section 3's message
make plants     # S1a, S1b, S2, S3, S4
make validate   # sixteen checks, ok
make ledger     # exits 0; row 6 OPEN, Measured empty, 1 / 4
git lfs ls-files | grep M05.mp4
gh api user/orgs          # [] : no organisation yet
```

Any seed test that passes, or fails for another reason, makes this PR's
plant false.
