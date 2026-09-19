---
adr: ADR-0003
title: Remaining path ownership; F0.1 is a finding, not a falsifier
status: Accepted
date: 2026-09-18
seat: Product
authorises:
  - Product      # §5 Product row, §8 M00 seeded, expected and falsifier lines
  - Engineering  # §5 Engineering row; the `two-key` trigger on evals/history/**; amendment 1: .gitattributes, agents/<name>/**
  - Security     # amendment 1: infra/bootstrap/**, infra/construct/** as paths; seats -> groups in a manifest
  - Rule Owner   # amendment 1: agents/*/rules/**, guardrail id and version in a manifest
  - Tool Owner   # amendment 1: agents/*/tools/**, may_call and may_be_called_by in a manifest
  - Threshold Owner  # amendment 1: model and judge ids in a manifest
amendments: 1
---

# ADR-0003 — Remaining path ownership; F0.1 is a finding

ADR-0002 is reserved for the baseline freeze at the M00 close PR. This
ADR takes the next number because ADR-0001 has used both amendments.

## Context

M00 PR 1 ran the baseline locally twice (`milestones/M00/feasibility.md`
§6). On the second run, the plant, the baseline passed trap `g-012` on
`score`. SPEC/00 §8 M00 listed that as falsifier F0.1 of claim 0.

ADR-0001 amendment 2 gave seats to most paths §5 did not list and left
five without one.

## Decision

1. **F0.1 is a finding, not a falsifier.** Claim 0 is that every later
   number is a delta against a frozen naive baseline. It is not that the
   baseline loses every trap. A baseline that gets a trap right is a fact
   about the trap, which F0.1's own text already said: "record, do not
   tighten". The falsifiers of claim 0 are F0.2 and F0.3 only. F0.1 keeps
   its number and becomes Finding F0.1 in SPEC/00 §8 M00, in row 0 and in
   the feasibility note. M00 is not RED on it. Product.
2. **Expected on the baseline** in §8 M00 changes from "traps 0/3" to:
   the baseline card is written, `score` and `cites` are recorded per
   golden, traps 1/3 on the plant as opened. A different trap count in
   CI is a non-determinism finding to record; it becomes the A-vs-A
   control at M04. Product.
3. **Remaining paths.** Product. (§5, CLAUDE.md table)
   - `README.md` and `LICENSE` are Product's.
   - `tests/**` is Engineering's.
   - `evals/history/**` is Engineering's and is written by CI only. A
     human commit touching it is a `two-key` change. §5's `two-key` gate
     gains that trigger.
   - `evals/local/**` is Engineering's. It is gitignored and no gate
     reads it.

## Consequences

- Every path on `main`, and every path PR 2 will write, has a seat.
- `two-key` has a fourth trigger to implement at M02.
- A trap the baseline passes does not decide row 0. It is still written
  down every time it happens.
- Carried to M01 open: `g-012` passed on three guessable fields. The
  Data Owner may retire it there and add `g-016` (R11: retire, never
  rename). See feasibility.md §7.

## Amendment 1 (M01 PR 1, 2026-09-19): paths M01 adds

Product. M01 adds paths that §5 and CLAUDE.md's table do not name. Every
file on `main` has a seat (§5), so each gets one here, before the file
exists. Ruled for M01 PR 1 (`milestones/M01/rulings/pr1.md`).

- **`.gitattributes`** → Engineering. Root config, beside `.gitignore`.
  It holds one line: `docs/video/**/*.mp4 filter=lfs diff=lfs merge=lfs -text`.
  The line was first ruled as `docs/video/** …`; that made
  `docs/video/README.md` an LFS pointer (commit `fa21d9d`), so Engineering
  narrowed it to the recordings before the PR opened.
- **`agents/<name>/**`** → Engineering, except:
  - `agents/*/rules/**` → Rule Owner;
  - `agents/*/tools/**` → Tool Owner;
  - `agents/*/manifest.yaml` → each field by its §6 owner: model, judge
    and guardrail ids to the Threshold Owner and the Rule Owner as §5
    already divides them; `may_call` and `may_be_called_by` to the Tool
    Owner; seats → groups to Security. A diff to the file names the seat
    of every field it changes.

  §5's `rules/**` and `tools/**` mean these paths too: a rule or a tool
  schema is the Rule Owner's or the Tool Owner's wherever it sits.
- **Bundle layout:** `agents/<name>/{manifest.yaml, prompt.txt, tools/,
  rules/}`. `prompt.txt` is Engineering's, as the rest of the agent's code
  is. A change to it is a change to what ships, and from M01 PR 2 a
  change to the bundle's digest.
- **`infra/bootstrap/**` and `infra/construct/**`** → Security. §5 already
  gives Security the bootstrap stack and the construct in words; this
  names them as paths. `infra/**` was Security's already, so nothing
  moves.

This is ADR-0003's first amendment. One is left.
