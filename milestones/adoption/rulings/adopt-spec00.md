---
ruling: adopt-spec00
seat: Product
authorises:
  - SPEC/**
  - CLAUDE.md
  - docs/adr/**
  - milestones/adoption/**
  - milestones/M00/README.md
evidence:
  - SPEC/00-overview.md
  - docs/adr/ADR-0001-spec00-adopted.md
  - milestones/M00/README.md
pr: https://github.com/andaro74/agentkeel/pull/1
---

# Ruling: adopt SPEC/00

SPEC/00-overview.md is adopted as the authority of this repo, with
amendment 1 applied in the same PR and recorded in
`docs/adr/ADR-0001-spec00-adopted.md`.

This PR carries its ruling in-PR. The `cold-review-ruling` check does not
exist yet (R9: required from M00 PR 2). This PR is not counted against
M00's cap of four.

What a reader can falsify:

- Every numbered item in ADR-0001 amendment 1 appears in the SPEC/00 or
  CLAUDE.md diff of this PR. Diff the two files against the untracked
  originals from the initial commit's working tree; there is no earlier
  committed version.
- The model ids at the top of `milestones/M00/README.md` were resolved on
  2026-09-18 from `aws bedrock list-inference-profiles` and
  `list-foundation-models` in us-west-2. Re-running those commands
  reproduces the status column.

Paths this ruling authorises beyond the three the seat named
(`SPEC/**`, `CLAUDE.md`, `docs/adr/**`): `milestones/adoption/**` for
this file, and `milestones/M00/README.md` for the Threshold Owner's model
table, which Product ruled should ride in this PR rather than in a
separate commit.
