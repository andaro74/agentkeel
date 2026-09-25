---
# M03 PR 1 (#19), the plant. Product's key. One seat per file: the Rule
# Owner's is pr1-rule-owner.md, Security's pr1-security.md, Engineering's
# pr1-engineering.md (with the cold review). The PR touches no Data
# Owner, Tool Owner or Threshold Owner path.
ruling: pr1
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/01-signed-bundle.md
  - SPEC/02-seats-and-change-gates.md
  - SPEC/03-evals-regression-redteam-corpus.md
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
  - docs/milestones/M01.md
  - docs/milestones/M02.md
  - docs/milestones/M03.md
  - docs/milestones/README.md
  - docs/video/README.md
  - docs/video/milestones/M02.mp4
  - milestones/README.md
  - milestones/M03/**
  - .claude/agents/docs-writer.md
evidence:
  - SPEC/00-overview.md#8-M03
  - SPEC/03-evals-regression-redteam-corpus.md
  - milestones/M03/feasibility.md
  - milestones/M03/open.md
  - docs/adr/ADR-0005-video-follows-the-tag.md
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
pr: 19
---

# Ruling: M03 PR 1, Product

Ruled by andaro74 as Product, 2026-09-25.
The rulings marked **ruled** in `feasibility.md` §2 were made by the
human on 2026-09-25 before the seeds, or before the PR opened; this file
carries them and the rest.

## What this PR is

PR 1 of M03, the plant. SPEC/03 first (`ac399c0`), reviewed by
`product-spec-reviewer` (3 BLOCK, 12 FINDING, 4 NOTE; `feasibility.md`
§1). Seven seeds, one commit each, before any reader: `61ac95a` S1,
`c5f5ca3` S2, `01876a7` S3, `2fd7128` S4, `149d352` S5, `d229601` S6,
`1e51666` S7; the two guards `92c7b2a`. Row 3 on open, 1 / 4. Nothing in
it makes claim 3 pass: `CONTROLS` is `{}`, and there is no overlap check,
fingerprint reader, table in the runtime match, ingest pipeline, or
ancestor-limited history.

## Rulings

1. **The BLOCKs on SPEC/03**: B1 a sixth seed, S6; B2 not seeded, M04;
   B3 the plant count stated before PR 2's run (`feasibility.md` §2.1).
2. **F2**: "the eval gate" is the whole `evals` job. **F9**: the
   knowledge base and retrieval are cut to M04 at open (cut 6).
3. **After the seat reports** (`feasibility.md` §2.5): the gate reads a
   subagent prompt's own `seat:` (`security-reviewer` BLOCK 1,
   `10452f9`); S7 (cold review F1); `g-014` not counted at M03, so the
   count is **7 of 7** (`g-013`, `g-015` to `g-020`); ADR-0009 gains
   entry 5 and no other addition.
4. **The drafts in `feasibility.md` §2.2 and §2.3** (F1, F3 to F8, F10
   to F12; N1 to N4) are ruled as drafted.
5. **ADR-0009** (`open.md` row 1; Threshold Owner proposed, Rule Owner
   added entry 5). Draft: entries 1 to 5, the `keys:` field and the
   `deletes:` field, and past globs matched at their own merge commit,
   are accepted. Its status becomes Accepted when this file is on
   `main`. The readers are Engineering's at M03 PR 2. **Not added**, and
   one key until a later ADR says otherwise: a boundary deny narrowed
   (Security, PR 2 narrows the `bedrock:*Guardrail*` deny under one key,
   with its `simulate-principal-policy` read-back in the PR); an Object
   Lock retention or mode weakened (Security picks the corpus bucket's
   mode and period at PR 2; M05's audit bucket is R5's and already
   two-key by SPEC/00 §5's words); the overlap bound raised (the Data
   Owner's file at PR 2 fixes 12); a rights-table row deleted (Data
   Owner; `validate` still refuses a golden whose row is gone).
6. **`open.md` row 9, the video ceiling.** Draft: **the ceiling stands
   and so do the two recordings.** A milestone video is at most five
   minutes from M03 on. M01's (6:09) and M02's (5:48) are committed as
   recorded and not re-recorded: SPEC/00 §10.2 commits a recording once
   and §10.5 allows no retake, and cutting a recording to fit a ceiling
   is an edit. Each row says by how much it is over. Raising the ceiling
   to fit two recordings after the fact is the move this repo refuses
   everywhere else.
7. **Every `open.md` row** is answered in `feasibility.md` §6 or moved
   with a seat and a date. Row 11: 0 of 11 done, each re-dated.

## Findings from the seat reports, and where each is held

Security, Rule Owner and Engineering findings on their own paths are in
their files. The rest, by source:

| Source | # | Held |
|---|---|---|
| `security-reviewer` | F1 the guardrail cannot be on the call under the `bedrock:*Guardrail*` deny | SPEC/03 §6 (`4d04332`): Security narrows it at PR 2 before the guardrail's commit; one key (ruling 5) |
| | F2 code can drop the guardrail | Security, PR 2: a `bedrock:GuardrailIdentifier` condition on the agent's invoke grant |
| | F3 the promoter, its trust, the deploying role, the bucket-policy route | Security, PR 2, named in SPEC/03 §6 in the commit before the ingest stack |
| | F4 Object Lock mode and period | Security, PR 2 (ruling 5) |
| | F5 the deploy role cannot delete rows | Security, PR 2: `DeleteItem` and `Scan` on the table, read back by `simulate-principal-policy` |
| | F6 where the runtime's table digest lives | Engineering with Security, PR 2: a marker the agent does not read, cleared before a load and set after; unreadable means runner mode |
| | F7 the S5 lookup can read absence too early or under the wrong key | Engineering, PR 2: `observe_ingest.py` finds the pipeline's record of this version first, and checks the production bucket by content. The run file is not edited |
| | NOTE 3 `src/gates/` judged by the PR's own code | SPEC/03 §8 (`4d04332`); Security, M05 |
| | NOTE 5, 6, 7 | ruling 5; M05 (S3 data events); PR 2 (cdk-nag) |
| `data-owner` | F1 an answer-side overlap rule | Data Owner, PR 2, before the corpus lands: no `r-NNN` token in `data/corpus/`, and no document pairs a golden's title, territory and platform with its date or exclusivity |
| | F2 the bound on an Engineering path | ruling 5: not on the list; the Data Owner's file at PR 2 fixes 12 |
| | F3 no Data Owner file | PR 2, the first PR that changes a Data Owner path; a ruling here could authorise nothing this PR changes |
| | F4 S3's seed path is the real schedule's | the seed is not edited; the real schedule takes another key (Data Owner, PR 2) |
| | F5 `g-014` | ruling 3 |
| | F6 `g-021` does not follow from its row | Data Owner and Tool Owner, PR 2 (`open.md` row 5): retired with two keys and re-added under a new id, never edited in place |
| | F7 `admitted.yaml` can drift from its bytes | Engineering, PR 2: `validate` checks each sha256, the file set, and the named ruling's seat |
| | N9, N12 | Data Owner, PR 2 |
| | N11 "a contract nobody signed" means "a document the Data Owner did not name" | recorded; the sentence stands, and SPEC/03 §2 says what refuses it |
| | N13 S1's two non-UTF-8 bytes | the seed is not edited; a PR 2 test that validates S1's tree reads it with `errors="replace"` or not at all |
| `rule-owner` | F3 the score does not tell which rule intervened | Engineering, PR 2: `score_one` reads the intervening policy from the trace, or SPEC/03 says it does not; `red-teamer.md` item 5 widened at PR 2 |
| | F4 `DRAFT` as a version | SPEC/03 §6 (`4d04332`); the schema at PR 2 |
| | F6 two files, one resource | SPEC/03 §6 (`4d04332`) |
| | N1 over-block | SPEC/03 §6: `red-teamer` checks before the guardrail's commit |
| | N2 SPEC/00 §9 lists three guardrail rules | Product, PR 2, with the guardrail |
| | N4, N5 the red-teamer prompt | Rule Owner: Promptfoo if cut 5 is not taken (PR 2); the open milestone's SPEC (M04 PR 1) |

## What a reader can run to falsify this PR

```
git show 61ac95a --stat   # a seed: fixture, test, fixtures README; no reader
uv run pytest tests/test_m03_seeds.py -rxX           # 7 xfailed, 2 passed
uv run pytest tests/test_m03_seeds.py --runxfail     # each fails for its planted reason
make plants                                           # S1 to S7 listed
make ledger                                           # exit 0; row 3 OPEN, 1 / 4
grep -n "CONTROLS: dict" -A1 src/verdict/plants.py    # still {}
```

A seed test that passes, a reader in the tree, or `make ledger` exiting
1 falsifies it.
