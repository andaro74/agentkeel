---
# M10 PR 1 (#54), the plant. Product's key. One seat per file:
# Engineering's is pr1-engineering.md (the seeds, SEEDS_M10, the tests, the
# ledger test's count, the fixtures README). SPEC/00's amendment, SPEC/10,
# SPEC/06's one row, ADR-0014's status line, ADR-0015, CLAUDE.md's seat
# table, the explainer, the quickstart, the compliance map, the ledger and
# milestones/M10/** are Product paths. The fixtures under tests/** are
# Engineering's, as M09's were; the Tool Owner's reading of the proposed
# field is a report in the PR body, not a key: no manifest and no schema
# changes in this PR.
ruling: pr1
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/06-developer-template.md
  - SPEC/10-public-caller.md
  - CLAUDE.md
  - docs/adr/ADR-0014-per-agent-rules-on-a-platform-baseline.md
  - docs/adr/ADR-0015-the-public-caller-an-eleventh-milestone.md
  - docs/compliance/map.md
  - docs/developer/quickstart.md
  - docs/milestones/M10.md
  - docs/milestones/README.md
  - milestones/README.md
  - milestones/M10/**
evidence:
  - SPEC/00-overview.md#8-M10
  - SPEC/10-public-caller.md
  - milestones/M10/feasibility.md
  - milestones/M09/README.md
  - milestones/M09/rulings/pr2.md
  - docs/adr/ADR-0015-the-public-caller-an-eleventh-milestone.md
  - docs/adr/ADR-0014-per-agent-rules-on-a-platform-baseline.md
  - docs/adr/ADR-0005-video-follows-the-tag.md
pr: 54
---

# Ruling: M10 PR 1, Product

DRAFT. Becomes a ruling when the line below reads "Ruled by".

## What this PR is

PR 1 of M10, the plant: 1 / 4. M09 is closed (GREEN, tag `m09` on
`833ab2b`, 2026-10-13). SPEC/00 planned no M10; it is amended for an
eleventh (`053ee19`, `841178f`), SPEC/10 written in the same commit and
reviewed by `product-spec-reviewer` (0 BLOCK, 9 FINDING, 3 NOTE;
`feasibility.md` §1), every finding taken on the session's recommendation
(`feasibility.md` §2), SPEC/10 revised once (`841178f`), ADR-0015
proposed, the seeds planted (`fba41ad`). It builds no reader, no door, no
pool, no workflow, no stack, no bar, no golden under `evals/goldens/`, no
rule, no manifest field and no schema change, and makes no grant, no
probe and no attempt.

## Rulings put to Product

1. **An eleventh milestone.** M10 opens after M09's close by this ruling,
   not by a finding of M09, and reopens none of M09's rows; M09's twenty
   findings and its Unsure items keep their homes. SPEC/00 §8's count
   becomes eleven and at most 44 PRs (ADR-0015 decision 1).
2. **The claim and the plain sentence, as written** (SPEC/00 §7 row 10,
   §10.3 row 10), ruled at the session's stop on 2026-10-13 before SPEC/10
   was written, with four changes from the brief's proposal
   (`feasibility.md` §2.4): a door the platform controls; an identity the
   manifest admits; each call's record; the bypass arm as a platform
   principal the construct does not name. The title reads "Outsiders"
   (reviewer finding 9).
3. **M10 builds one control** (ADR-0015): the door, with the identity it
   admits and the manifest field that says who, and the reading of each
   call's record. It is not described as working until it has refused its
   seeded case. The gate rules nothing on `caller`; a bypass, an answered
   stranger or an unrecorded refusal stops no merge at M10.
4. **Expected GREEN, stated with its risks** (SPEC/10 §7): admitted 1 of
   1, refused 3 of 3; the refusal's record at the service's edge the first
   risk and the item most likely to threaten the cap; the subject on the
   record, the runtime's authoriser update and the deploy step's token
   the others. The probe before PR 2 is what turns the first into a
   reading.
5. **The twelve dispositions in `feasibility.md` §2**, each a proposal
   with its seat: the record's two shapes and its mapper (1), no guardrail
   on a call record (2), the two timestamps (3), the fallback for (a) (4),
   two more S1 records (5), cut 4 struck (6), SPEC/00 §5's Tool Owner row
   (7), the pool in the agent's stack (8), the title (9), the three fields
   (10), ADR-0015 (11), cut 3's wording at the close (12).
6. **M10 records no video** (ADR-0015 decision 6; SPEC/00 §10.5 and §15
   as amended), ruled by Product on 2026-10-13 before this PR was written:
   no gate, no `validate` check, no envelope and no ledger cell reads a
   recording; the evidence for row 10 is the CI-written envelope its cell
   will name. ADR-0005 has no amendment left, so the rule lives in
   ADR-0015 and here. The explainer's Watch line reads "No recording" from
   its draft; `docs/video/README.md` gets its M10 row at the close.
7. **R7, M09's housekeeping, yes to all four** (ruled 2026-10-13 at the
   stop): SPEC/06 §6 row 2 and the quickstart's step 0 say the platform
   App is on "selected repositories" and the owner adds a new repository
   to it (M09 finding 3; Security's `pr4-security.md` rules it stays so);
   ADR-0014's `status:` reads Accepted with 2026-10-11 (finding 14);
   `docs/compliance/map.md` gains envelope E9 and row 35 for claim 9, and
   its "Claim 8 (M08): not opened" line is replaced by two that say where
   claims 7 to 10 stand (finding 11). `docs/story.md` and the M08 header
   rows stay standing.
8. **The seed test count corrected** in SPEC/10 §7 (4 passed, 6 xfailed;
   it said 2 and 5 before the tests were written and 3 and 6 before the
   cold review's F2 gave S3 two real guard cases), the earlier counts
   named there and the corrections recorded in `feasibility.md` §3.
9. **The two seat reads of PR 1 applied as drafts** (`feasibility.md`
   §2.5, §2.6): `tool-owner` 0 BLOCK, 6 FINDING, 9 NOTE, no schema or
   manifest change to rule on, the field's shape and ADR-0016 as its
   findings proposed; `engineering-cold-reviewer` 0 BLOCK, 3 FINDING, 8
   NOTE, applied in this PR's last commit. The reports are in the PR body
   verbatim. SPEC/00 §6's manifest list gains `callers` under this ruling
   (`tool-owner` F4).

## Unsure, each with its seat and when

The PR body's Unsure list, repeated here so the ruling carries it.

| # | Item | Seat | By |
|---|---|---|---|
| A | The door (SPEC/10 §11 R2). Proposed: door 1, the runtime's own JWT authoriser on a Cognito user pool per agent in the agent's stack; the three unknowns probed with throwaway names before PR 2 opens, outputs in `runs/door_probe.md` at PR 2; door 2 if (c) is no; the bootstrap's grants narrowed by a runtime tag if (a) is no, failing which door 2 | Security | before PR 2 opens (R2) |
| B | Who the outside caller is (R3). Proposed: a user in the agent's pool for the admitted arm; a user of a throwaway pool for the stranger; no token; the laptop's IAM principal for the bypass arm only, standing for a platform principal the construct does not name, never presented as outside; a security-account principal as the stranger if door 2 is ruled | Security; Product | before PR 2 opens (R3) |
| C | The manifest field (R4). Proposed: `callers`, in the shape SPEC/10 §2 fixes (`subject` a name, never `platform`, unique; `issuer` the symbol `self` at M10; both required; optional in the schema, required by `callers_errors`; no semver bump); not an edge, not a rule; `[]` the default and absent to `[]` not a relaxation; the `platform` client admitted by the construct and not listable; refagent's and `ratings-helper`'s gain `callers: []` at PR 2 under a Tool Owner ruling file | Tool Owner | before PR 2 opens (R4) |
| D | The call record's read shape (R5): `subject`, `issuer`, `agent`, `outcome`, `reason`, `request_id`, `time`, `delivered`; no guardrail; `build`'s `from_raw` maps the raw record onto it and refuses one that carries a credential; the raw record stays beside it | Data Owner | PR 2 (R5) |
| E | N (R6): `detection.max_seconds`, 600 s, reused and read as M05 read it (`LastModified` against `eventTime`); no bar added or moved | Threshold Owner | before PR 2 opens (R6) |
| F | ADR-0016, a new ADR (ADR-0009's last amendment is the Rule Owner's, `tool-owner` note 4): entry 7, a subject added to `callers` or the key removed from a value; absent to `[]` not one; keyed by the Tool Owner and any second seat. The construct's authoriser widened is Security's under `ruling-cited`, unread by `two-key` | Product (the ADR); Tool Owner | PR 2 |
| G | Where the raw record comes from (CloudTrail's data event for `InvokeAgentRuntime`, or the runtime's log by a subscription the bootstrap deploys) and under which bucket statement it lands (`calls/agents/<name>/`, proposed) | Security | before PR 2 opens (R2's probe, question (b)) |
| H | Whether setting `authorizerConfiguration` on a deployed runtime updates it in place or replaces it (a new ARN and registry row). Not a falsifier; the registry row says which | Security; Engineering | PR 2 (read at the first deploy after it) |
| I | The `platform` client's credential for `deploy.yml`'s goldens step: where it is held (Secrets Manager or SSM, proposed) and which role reads it | Security | before PR 2 opens (R2) |
| J | If cut 3 is taken (the record names the client, not the subject), the plain sentence's "who asked" is read as "which app asked" and the explainer says so | Product | the close |
| K | F10.5's agent-repository half is unread (no `two-key` there, SPEC/00 §12); named in SPEC/10 §8 and the ledger row, not measured | Product | recorded; standing |
| L | A throwaway pool for the stranger arm is made and deleted by the owner outside the repository; its creation and deletion are not recorded by any observer | Security; Product | before PR 3's run |

## What a reader can run

See `milestones/M10/README.md`, "What a reader can run".
