---
# M06 PR 3 (#36), the repair. Product's key. One seat per file: Security's
# is pr3-security.md, Engineering's pr3-engineering.md (with the cold review).
ruling: pr3
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/06-developer-template.md
  - milestones/README.md
  - milestones/M06/**
  - docs/milestones/M06.md
evidence:
  - SPEC/00-overview.md#8-M06
  - evals/history/822514aa1ade3b94debe1196913c5ad6e9faf074.json
  - milestones/M06/runs/f6_0_owner_test.yaml
  - milestones/M06/runs/owner_check_ruleset_24310403.json
pr: 36
---

# Ruling: M06 PR 3, Product

DRAFT for andaro74 as Product. Not ruled until this line reads "Ruled by".

## What this PR is

PR 3 of M06, the repair: 3 / 4. After PR 2's merge (`39031e7`; its
envelope `822514a`: GREEN, plants 7/7, `F6_4` held live, `F6_1` live,
`F6_2` and `F6_3` unread, so row 6 RED as stated), the owner's test of the
template (`runs/f6_0_owner_test.yaml`, pushed at 12:57:19Z) made
`agentkeel-studio/owner-check` at 13:05:37Z and applied the ruleset export.
Read back, the live ruleset differed from it: GitHub adds two fields to an
organisation repository's pull request rule. The App compares exactly, so
it would have refused every head of every agent repository. Step 1 missed;
it is recorded as missed. No pull request was opened.

## What this authorises (Product's paths)

- **Row 6 amended** (`milestones/README.md`, `milestones/M06/README.md`):
  the platform check runs from `main`, so the owner's test, S2 and S3 are
  made after PR 3's merge, and **PR 4's run records them**; PR 3 is the
  repair, and PR 4 is that read and the close. Option A, ruled by the human
  on 2026-10-01 over option B (close RED now). A miss at PR 4 is a RED close
  with the finding; there is no fifth PR.
- **SPEC/00 §10.5**: the quickstart is timed after PR 3's merge and read by
  PR 4's run, with the amendment noted in SPEC/00's header.
- **SPEC/06 §5.1, §6's table and §7**: the same move; the owner applies
  `agent.post.json` and the live ruleset must equal `agent.json`.
- **The run files**: S2's and S3's name PR 4's run and PR 3's merge, before
  either is attempted, so no expected value moved after an attempt. The
  owner test records step 1 as missed, says no reader takes the file (the
  owner reads it by hand; PR 4's ruling records it as S3's precondition,
  not as evidence for the cell), and step 3 now reads whether an approval
  is asked. GitHub's response for ruleset 24310403 is committed beside it.
- **The explainer** names the read at PR 4.
- **3 / 4** and the PR 3 detail.

## Stands, for later

- SPEC/00 §10.5 says the quickstart is timed "by the author"; row 6 says by
  `floresinnovations`. Older than this PR (cold review N3); PR 4's close
  says which.
- Row 6's claim says "governed agent"; the close does not repeat it in prose
  unless S2 and S3 read as stated (cold review N4).

## What a reader can run

```
git diff 39031e7...HEAD -- milestones/README.md SPEC/00-overview.md SPEC/06-developer-template.md
uv run python -m src.ledger                                   # exit 0, row 6 at 3 / 4
grep -n "PR 3's run" milestones/M06/runs/*.yaml SPEC/06-developer-template.md   # none but the amendment notes
```
