---
adr: ADR-0010
title: A pin's profile and its deprecated_after are the Threshold Owner's
status: Accepted
date: 2026-09-26
seat: Product
authorises:
  - Threshold Owner  # SPEC/00 §5: "agent model id + version + region" read as the whole pin, with profile and deprecated_after
amendments: 0
---

# ADR-0010 — A pin's profile and its `deprecated_after` are the Threshold Owner's

Raised by `product-spec-reviewer` on SPEC/04 (finding 10,
`milestones/M04/feasibility.md` §1). Ruled by Product at M04 PR 1
(`milestones/M04/rulings/pr1.md`), accepted on `main` at that PR's merge
commit (ADR-0008).

## Context

SPEC/00 §5 gives the Threshold Owner "agent model id + version +
region". ADR-0003 amendment 1 gives every other manifest field to the
file's owner, Engineering. Two fields sit between them:

- `model.profile`, the inference profile Converse is called through. It
  names the model a second time (ADR-0007: the gate refuses a pin whose
  `id` and `profile` disagree). `src/gates/__init__.py`'s
  `MANIFEST_FIELD_SEATS` already attributes the whole `model` mapping,
  `profile` with it, to the Threshold Owner. No text said so.
- `deprecated_after`, a top-level field. From M04 PR 2 `validate` fails
  a pin within 30 days of it (SPEC/04, seed S5). The gate attributes it
  to Engineering, so an Engineering commit could clear the date that
  makes `validate` fail. The date describes the model, not the code.

ADR-0003 has used both its amendments, so this is a new ADR.

## Decision

1. **`model.profile` is the Threshold Owner's**, as part of the pin.
   This records what the gate already does.
2. **`deprecated_after` is the Threshold Owner's.** It is set from
   Bedrock's `modelLifecycle.endOfLifeTime` for the pinned model, and is
   null while Bedrock announces none. Setting it from Bedrock by code is
   M07's (`model-watch`; SPEC/04 §9 cut g).
3. `MANIFEST_FIELD_SEATS` gains `deprecated_after: Threshold Owner` at
   M04 PR 2 (Engineering). Nothing reads this ADR before then.

## Consequences

- A diff that clears or moves `deprecated_after` needs a Threshold Owner
  ruling. Whether moving it later is a relaxation is not decided here;
  ADR-0009's list does not name it.
- One person holds every seat (R1). This names whose ruling a diff cites;
  it does not add a reviewer.
