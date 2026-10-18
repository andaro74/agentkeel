---
adr: ADR-0016
title: Two keys on a caller admitted; entry 7 of the closed list
status: Accepted  # 2026-10-15, when milestones/M10/rulings/pr2.md read "Ruled by"; this line read Proposed until M10 PR 4 (the close; M09's close finding 14, again)
date: 2026-10-15
seat: Product
authorises:
  - Tool Owner  # `callers` is its field (SPEC/00 §5); a subject added, or the key removed from a value, is two keys from M10 PR 2
amendments: 0
---

# ADR-0016 — Two keys on a caller admitted: entry 7 of the closed list

Proposed by the session at M10 PR 2 and put to Product
(`milestones/M10/rulings/pr2.md`), keyed at the same PR by the Tool Owner
(`pr2-tool-owner.md`). Accepted when that ruling reads "Ruled by", on `main`
at the merge commit of M10 PR 2 (ADR-0008). A new ADR, not ADR-0009's second
amendment: ADR-0009's last amendment is reserved for the Rule Owner by its own
closing words (`tool-owner` note 4 on M10 PR 1).

## Context

- **The closed list** (SPEC/02 §2; ADR-0009 entries 1 to 6) names what
  `two-key` reads as a relaxation: a bar moved in its `relaxes:` direction,
  a golden retired or its `expected` changed, a rule removed or weakened, a
  guardrail nulled or its id changed, a budget raised, memory shortened,
  `deprecated_after` moved later with the model unchanged. Adding to it is
  a SPEC/00 §5 amendment, not an edit to the gate.
- **`callers`** is a manifest field from M10 PR 2 (ADR-0015 decision 3;
  SPEC/10 §2): the outside subjects an agent admits through the door the
  platform controls, each with its issuer, `[]` the default. It is the Tool
  Owner's (SPEC/00 §5, amended at M10 PR 1). A subject on the list is a
  caller the door lets in.
- **The false state** (SPEC/10 §3 item 4, seed S3, `fba41ad`): a manifest
  key that admits a caller is on no entry, so a diff adding one passes
  `two-key` with one ruling. The agent repository's half is unread by
  design (SPEC/00 §12: an agent repository has no `two-key`).

## Decision

1. **Entry 7.** A subject added to a manifest's `callers`, or the key
   removed from a value, is a relaxation. Read against the base ref, on
   subjects: a subject in the PR's list that is not in the base's is
   admitted; a first write that names a subject admits one. A `callers`
   that stops being a list is read as removed, since a gate that cannot say
   does not pass it.
2. **Not one.** Absent to `[]`, and a subject removed: both admit no one
   new. The two manifests M10 PR 2 gives `callers: []` are exactly that
   diff, under the Tool Owner's one key (`pr2-tool-owner.md`); seed S3's
   second guard case plants it.
3. **The keys.** The Tool Owner's file covers the path, as the field's
   owner; the second is any other seat's, naming the path in its `keys:`,
   as the gate reads every entry (`tool-owner` note 5 on M10 PR 1). The
   refusal reads `<path>: callers: subject '<name>' admitted (ADR-0016 entry
   7)` or `<path>: callers removed from a value (ADR-0016 entry 7)`, with
   the gate's usual count of seats holding a key.
4. **What stays outside.** The construct's authoriser widened in
   `infra/construct/governed_agent.py` is Python no entry reads; it is
   Security's under `ruling-cited` and `security-reviewer`, named unread by
   `two-key` in SPEC/10 §4 F10.5 and §8. An agent repository's own `callers`
   pull request is admitted on the platform check alone (SPEC/00 §12). Both
   are named, not measured, at M10.

## Consequences

- `src/gates/two_key.py` gains entry 7 (`caller_relaxations`) at M10 PR 2,
  after its seeded case, which `tests/test_m10_seeds.py` S3 reads: a subject
  added and the key removed each refused with one key and passed with two;
  a subject removed and absent to `[]` each passed with one.
- F10.5 on every agent envelope from PR 2's merge is a test-only witness of
  this entry (SPEC/10 §4). The live reading at M10 is `two-key` on this
  PR's own diff and on the fixture's; nothing in an agent repository is
  read.
- SPEC/00 §5's Tool Owner row, amended at M10 PR 1 ("admit a caller with one
  key" under May not), is what this entry enforces from PR 2's merge.
