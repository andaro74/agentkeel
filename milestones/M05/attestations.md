# M05 — attestations

Four lines, signed before `git tag m05`. Every seat is one human (R1), so
one person signs all four. They are separate because they attest to
different things, and a later reader should be able to see which one was
wrong. The Rule Owner's, the Data Owner's and the Tool Owner's files did
not change in M05 (`git diff --stat 4206edf HEAD` over `rules/`,
`agents/refagent/rules/`, `evals/goldens/`, `data/`, `tools/` and
`agents/refagent/tools/` is empty), so none of those seats signs a line.

Sign by writing your name and the date at the end of the line, in a commit
on the close PR's branch, pushed before the merge. An unsigned line is not
a failed attestation; it is a milestone that is not tagged. M04's close
merged with five lines unsigned and needed a sign-off PR (#29); `cold-review-ruling`
now refuses a draft ruling, but nothing reads this file, so the close
checks it on the pushed head before any merge command.

The ledger row is not waiting on these. Row 5's State is RED because the
ledger's reading of the envelope for `28634e9` names S1 and S7 as not
shown refused and unrecorded, and `make ledger` holds the cell to that
line. What these four gate is `git tag m05`.

---

**1. Engineering — the evidence is CI-written and unedited.**

The envelope `evals/history/28634e9a1405b034a3efbe898cc7675ebfab3587.json`
and its control card were written by `src/verdict/build.py` and
`src/baseline/run.py` inside CI run 36666223908, with `containment` read
from the audit bucket by `scripts/observe_containment.py` in the same run,
and committed by `github-actions[bot]` in `ff012c8`. No human edited any of
them after CI wrote them. Every commit under `evals/history/` in M05 is
`github-actions[bot]`'s (five: `139bd16`, `f53ed25`, `e19a4c8`, `d5250a5`,
`ff012c8`); that authorship can still be claimed by anyone with write,
and the copy under `envelopes/` in the audit bucket, put by the `archive`
job on each merge to `main`, is the record no branch push can make.
`src/baseline/` is unchanged since tag `m00`. The readers were repaired
twice to the records AWS wrote (PR 2: `388dbcf`; PR 3: `17675d6`,
`f50e493`, `01b40f5`), each stated as a repair before the run that read
it, and none moved N or a falsifier. At the close the seed tests read 5
passed and 2 xfailed, S1 and S7, each with its finding as its reason.

Signed: ____________  Date: ________

---

**2. Security — what was deployed is what was read back, and the second
account is one the agent account cannot change.**

Only the human deployed by hand in M05, each time after reading
`cdk diff` (the times are the human's reading of each stack's events,
recorded in `milestones/M05/README.md`, PR 2 detail; only the stand-in's
are in a run file): `infra/security/` in 897698239547 (`CREATE_COMPLETE`), then
`OrganizationAccountAccessRole` deleted there (`NoSuchEntity`); the
bootstrap (12:23:47Z, 2026-09-29; 49,613 of 51,200 bytes); `infra/audit/`
(12:48:48Z), twice more for S1's Lambda and once to remove it (14:26:13Z),
and once on 2026-09-30 to remove the stand-in (03:58:11Z, `NoSuchEntity`
at 03:58:19Z). refagent's denies, depth ceiling and chain check reached the
runtime only through the deploy role, from `main` (run 36657429406). S6's
four actions from the agent account were refused, two of them by the lock.
Not attested: that the organization cannot reach the security account (it
is the management account's member; centralized root access was not
enabled when read on 2026-09-28, and nothing stops it being enabled); that
the bucket policy no longer names the stand-in (it does, `M06/open.md` row
2); and any control in SPEC/05 §8 that no seed attempted.

Signed: ____________  Date: ________

---

**3. Threshold Owner — N was set before its reader and not moved.**

`detection.max_seconds: 600`, `relaxes: up`, was added to
`thresholds.yaml` in `a4e8922`, alone and before any code read it, as R10
states it. It was not moved when S1 and S7 could not be recorded: the
standard was not bent to fit, and no other kind of record stood in for the
missing ones. The worst recorded latency at the reading was 307 s.
Whether 600 s holds for flow logs is unread (`M06/open.md` row 41).

Signed: ____________  Date: ________

---

**4. Product — the row is the ledger's reading, the page says what RED
does not mean, and every finding has a home.**

Row 5 is copied from `make ledger`'s reading of the envelope for
`28634e9`, and `make ledger` exits 0 against it. S1's and S7's findings
were each stated before the reading that decided them (`rulings/pr2.md`
ruling 9; `rulings/pr3.md` ruling 1, `e1a6bb2`). `docs/milestones/M05.md`
says what RED does not mean, with the envelope's numbers. Every Finding
and Unsure item of M05 is closed, ruled, or in `milestones/M06/open.md`
with a seat and a milestone. Nothing in this milestone is described as
governed, secure or proven.

Signed: ____________  Date: ________
