---
# M03 PR 2 (#20, expected; corrected when the PR opens), the Data Owner's key.
# A draft by the session; the human rules as Data Owner before the merge.
ruling: pr2-data-owner
seat: Data Owner
authorises:
  - evals/goldens/v1/g-016.yaml
  - evals/goldens/v1/g-017.yaml
  - evals/goldens/v1/g-018.yaml
  - evals/goldens/v1/g-019.yaml
  - evals/goldens/v1/g-020.yaml
  - data/corpus/**
evidence:
  - SPEC/00-overview.md#8-M03
  - SPEC/03-evals-regression-redteam-corpus.md
  - milestones/M03/feasibility.md
  - milestones/M03/rulings/pr1.md
  - data/rights_table.json
  - data/clause_index.json
  - data/slate.json
pr: 20
---

# Ruling: M03 PR 2, Data Owner

**Draft.** Written by the session for the human, who rules each item below
as Data Owner. Nothing here is ruled until the human says so.

## The red-team goldens `g-016` to `g-020`

Added at `06ed59b`, `kind: redteam`, `expected: BLOCKED`, `added: M03`,
never passed. `g-016`'s fields are seed S2's fixture word for word; the
other four are the `red-teamer` draft's questions (#19's first comment).
The `data-owner` report on `06ed59b` (0 BLOCK, 3 FINDING, 14 NOTE) is in the
PR body.

## The corpus (`data/corpus/`, admitted in `admitted.yaml`)

Six invented documents, as SPEC/00 §9 lists them: the master license,
Amendment No. 1 (signed), the schedule of holdbacks, the music clearance
sheet, the embargo memo and the ratings letter. The unsigned Amendment No. 2
is seed S5 and is not admitted: no document under `data/corpus/` is it, and
`admitted.yaml` does not name its sha256.

- **The overlap bound stays 12** (feasibility F6; `data-owner` F2 at PR 1).
  `validate` refuses a run of 12 shared words or more between a live golden's
  question and a document. The longest run in these six is 5 words.
- **The answer-side rule** (`data-owner` F1 at PR 1, scoped on its report on
  `06ed59b`): no document names a rights-table row (`r-NNN`; `validate`
  refuses it), and no document pairs an ordinary or trap golden's title,
  territory and platform with its date or exclusivity. A red-team golden's
  answer is BLOCKED, which no document can supply. The documents keep per
  title dates, holdbacks, expiries and exclusivity in the Rights Schedule
  (the rights table), which they name and do not reproduce. The one dated
  pairing is Amendment No. 1's revised theatrical date for t-002 in DE, a
  platform no golden asks about; it says the holdback is unchanged.
- **The real holdback schedule** is `schedule-of-holdbacks.md`, not seed S3's
  path `holdback-schedule.md` (`data-owner` F4 at PR 1).
- **Talent contact details** in the master license (ML-12.3) are invented:
  `+1 212 555 0147` and `+44 20 7946 0321`, numbers in the ranges reserved
  for fiction, and `.example` addresses. They are there for `g-014` at M04,
  when refagent reads the corpus. At M03 the ingest pipeline's guardrail and
  PII scan reads them and flags PHONE and EMAIL: that hit is recorded and
  does not stop promotion, which rests on `admitted.yaml` alone (SPEC/03 §2,
  ruling on F7). Otherwise an admitted document would be refused and the
  fingerprint would name a document the production bucket does not hold.
- **The ratings letter** says a rating decides the version delivered and
  never availability, so the rights table stays the only source of
  `available` (SPEC/00 §9).
- **A gap, recorded:** SPEC/00 §9 asks for "8–10 invented documents, 1–3
  pages each". Its own list comes to seven with both amendments: six are
  admitted here and the seventh is seed S5, never admitted. Five of the six
  are under a page. SPEC/00's count is Product's to amend; what the corpus
  holds is this seat's.
- **Clauses outside the index.** The documents number clauses that are not
  in `data/clause_index.json` (ML-2.2, ML-4.1, ML-5.1, ML-6.1, ML-15.1,
  AM1-1, AM1-3, HS-1, HS-3, HS-5, MC-1, MC-2, MC-5, EM-3). They stay
  uncitable: an answer that cites one fails F1.4 until a ruling adds it to
  the index (M04, with retrieval).

`validate` holds `admitted.yaml` to the bytes of each document, to the set of
files under `data/corpus/`, and to a ruling of this seat that authorises the
path (`data-owner` F7 at PR 1).
