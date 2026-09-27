---
adr: ADR-0009
title: The closed list of relaxations, amended; how a second key names a path and a ruling names a deletion
status: Accepted
date: 2026-09-25
seat: Product
authorises:
  - Threshold Owner  # SPEC/00 §5 `two-key`: what counts as a relaxation (SPEC/02 §2, "Relaxation")
  - Rule Owner  # entries 4 and 5: a guardrail removed; a rule narrowed
amendments: 1
---

# ADR-0009 — The closed list of relaxations, amended

Proposed by the Threshold Owner at M03 PR 1 (`milestones/M03/open.md`
row 1; the `threshold-owner` report is in the PR body). Product rules
entry by entry in `milestones/M03/rulings/pr1.md`. Accepted by that ruling,
2026-09-25, on `main` at the merge commit of #19 (ADR-0008).

## Context

SPEC/02 §2 lists what `two-key` reads as a relaxation and says the list
is closed: adding to it is a SPEC/00 §5 amendment. M02's seat reports
and cold reviews found six gaps, and the Rule Owner's report on M03
PR 1 a seventh (`milestones/M03/open.md` row 1, with
its sources):

- a `relaxes:` direction flipped in one PR and the bar moved in the next
  takes one key each time (PR 2 threshold F2);
- a bar deleted from `thresholds.yaml` is not read at all:
  `threshold_moves` iterates the bars both sides share (PR 2 threshold
  F3);
- a manifest's `max_tokens_per_session` or `daily_usd` raised, or set to
  null, takes one key (PR 2 threshold F4);
- a manifest's `guardrail` set to null takes one key, while a version
  moved down takes two (PR 2 cold F5b);
- the second key "names" a path by substring anywhere in its body, so a
  ruling that argues against the change counts as a key for it (PR 2
  security F4);
- a rule dropped from a control file, with the version moved up, takes
  one key: the list reads a rules file deleted and a version moved down,
  and nothing inside the file (M03 PR 1 `rule-owner` F5);
- `validate` accepts an `authorises:` glob that matches a path deleted
  anywhere in history, so any new ruling may name any path ever deleted
  (M02 PR 3 `pr3.md` finding 3, cold N4).

## Decision

**The list** (SPEC/02 §2, "Relaxation"), entries added:

1. a `relaxes:` entry in `thresholds.yaml` whose value changes, or which
   is removed while its bar stays. Adding an entry for a new bar is not
   one;
2. a bar in `thresholds.yaml` deleted, or no longer a numeric leaf as
   `two-key` reads bars. A renamed bar is a deletion and an addition;
3. a manifest's `max_tokens_per_session` or `daily_usd` raised, set to
   null, or removed. The key that covers it is the field's seat
   (Threshold Owner), not the file's CODEOWNERS owner. The manifest's
   `ceilings` are not an entry: `validate` holds them under the ruled
   bars in `thresholds.yaml`, whose moves are already relaxations;
4. a manifest's `guardrail` set to null or removed from a value, or its
   `id` changed from one value to another. Null to a value is not one;
5. an entry removed from a list in a file under `rules/**` or
   `agents/*/rules/**` (a denied topic, a PII type, a blocked intent, a
   blocked attack), or its action weakened (BLOCK to MASK or NONE, MASK
   to NONE). Proposed by the Rule Owner on M03 PR 1 (`rule-owner` F5;
   the report is in the PR body), after the Threshold Owner's four: a
   version moved up with a rule dropped took one key, and a rule no
   golden reads would be caught by nothing. The key that covers it is
   the Rule Owner's.

**How the second key names a path** (SPEC/02 §2, "Two keys"): the
front-matter field `keys:`, a list of exact repo paths. `two-key` reads
it by equality. A body mention no longer counts, and neither does a
broad `authorises:` glob in the second key's file.

**How a ruling names a deletion** (SPEC/02 §2, "Covers"): the
front-matter field `deletes:`, a list of exact paths removed in the PR's
own diff; `ruling-cited` requires each deleted seat-owned path to be in
the owning seat's `deletes:`. `validate` stops matching past rulings'
globs against history at large: a glob in a ruling must match the tree
at its own PR's merge commit or that commit's first parent, found from
"Merge pull request #N" (merge commits only, ADR-0004 amendment 1). A
rename is a deletion of the old path and an addition of the new one;
`validate` reads git with `--no-renames`.

SPEC/02 §2's wording "`memory.retention` shortened" becomes
"`memory.retention_days` shortened, or `memory` removed", which is what
`two_key.py` reads.

## What reads it, and when

Nothing at M03 PR 1: this is the ruling. `src/gates/two_key.py`,
`src/gates/ruling_cited.py` and `src/validate/checks.py` read it from
M03 PR 2 (Engineering), before any commit of PR 2 that moves a bar.
Past rulings are not edited: the gates read only a PR's own rulings,
and `validate`'s new glob rule is checked against each past ruling's
own merge commit, where its paths existed.

## Consequences

- M03 PR 2's own work is not refused by it: the guardrail goes from null
  to a value; five goldens are added; `CONTROLS` is an Engineering path.
  A cap re-ruled upward was already a relaxation. If PR 2 raises
  `max_tokens_per_session`, entry 3 makes that two keys.
- One person still holds every seat (R1). The amendment makes a second
  key say which path it keys; it does not make it a second person.

## Amendment 1 (M04 PR 1, 2026-09-27): `deprecated_after` joins the list

Threshold Owner proposes (`threshold-owner` F6 on M04 PR 1, in the PR
body); Product rules (`milestones/M04/rulings/pr1.md`).

From M04 PR 2, `validate` fails a pin whose `deprecated_after` is within
30 days of the run, or past (SPEC/04 §5, seed S5). A one-key commit that
moved the date later, or cleared it, would switch that check off. ADR-0010
made the field the Threshold Owner's and left this open.

**Entry 6:** a manifest's `deprecated_after` moved to a later date, set
from a date to null, or removed, **with `model.id` unchanged**. Null to a
date is not one, nor is a date moved earlier. The key that covers it is
the Threshold Owner's. A swap changes the id, and its date describes
another model, so the two dates are not compared; a swap to a model
Bedrock marks `LEGACY` carries that model's `endOfLifeTime`, recorded in
the swap's Threshold Owner ruling (SPEC/04 §2; `threshold-owner` F4 on
the second read of M04 PR 1).

**What reads it, and when.** Nothing at M04 PR 1: this is the ruling.
`src/gates/two_key.py` reads it from M04 PR 2 (Engineering), in the same
PR as `src/validate/lifecycle.py` and no later.

Not changed here: a rule definition narrowed under the same name stays
one key **at the gate**. Until the Rule Owner's amendment, the Rule Owner
files a second key by hand for any change to a definition's wording
(`milestones/M04/feasibility.md` §6 row 2; `rule-owner` F1 on the second
read). This is ADR-0009's first amendment. One is left, and the Rule
Owner's is planned to be it; a change to the list after that is a new
ADR.
