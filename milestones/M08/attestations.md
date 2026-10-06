# M08 — attestations

Four lines, signed before the close merges. Every seat is one human (R1),
so one person signs all four. Sign by writing your name and the date at the
end of the line, in a commit on the close PR's branch, pushed before the
merge. An unsigned line is not a failed attestation; it is a milestone that
is not closed. Nothing reads this file; the close checks it on the pushed
head before any merge command (`milestones/M05/open.md` row 44).

The ledger row is not waiting on these. Row 8's State is RED because the
ledger's reading of the envelope its Measured cell names says so, and
`make ledger` holds the cell to that line. What these four gate is the
merge, and `git tag m08`, which Product rules in `rulings/pr4.md`.

The Rule Owner's, the Data Owner's and the Tool Owner's files did not change
in M08 (`git diff --stat m07 HEAD` over `rules/`, `agents/refagent/rules/`,
`evals/goldens/`, `data/`, `tools/` and `agents/refagent/tools/` is empty),
so none of those seats signs a line. M08 built no control (ADR-0013).

---

**1. Engineering — the evidence is CI-written and unedited.**

The envelope `evals/history/e930e4da1e528fdfee77e62c52154970873add79.json`
and its control card were written by `src/verdict/build.py` and
`src/baseline/run.py` in this PR's evals run (37402273717), with `drill`
read from the security account's audit bucket by
`scripts/observe_drill.py` (as `agentkeel-audit-read`) in the same run, and
committed by `github-actions[bot]`. No human edited any of them after CI
wrote them. `src/baseline/` is unchanged since tag `m00`. No reader changed
in M08: nothing under `src/` or `scripts/` in this PR beyond the corrected
`observed:` blocks, which are data the observer reads, not the observer.

_Signed: andaro74, 2026-10-05_

**2. Security — the records are from the separate account, read by their own time.**

Every record row 8 rests on was read from the audit bucket in the security
account (`897698239547`), which the agent's role cannot write outside its own
prefix, by `agentkeel-audit-read`. The quarantine was attached and detached
by hand (`hector.flores`), and the egress rule added and removed for the
hostile copy's security group alone, each under a ruling that reads
"Ruled by" (`rulings/pr3-security.md`). No live control was left relaxed: the
egress rule was revoked (run 2) and the quarantine detached (run 1).

_Signed: andaro74, 2026-10-05_

**3. Product — the row is RED and the prose says what RED means.**

Row 8 is RED. The explainer's "What happened" carries the envelope's numbers,
not a rounded or softened version, and says in plain words what the drill did
and did not show — in particular that the recovery removed the hostile
behaviour but the "answers GREEN" arm was not measured (a fixture defect), and
that a4 and a6 were refused with no record. No "governed", "secure" or
"proven" is written about a control that did not fire on its seeded case.

_Signed: andaro74, 2026-10-05_

**4. Product — the recording is as recorded.**

`docs/video/milestones/M08.mp4` (sha256 `ac23d139dc18807fb7d3940ce6722b1794e48a8cbff7a8e7d2f3e4099b6599eb`,
41.98 MiB) is the game-day recording, captured during the retake's run 1 and
narrated as scripted, exported unedited. It is over the 40 MiB size ceiling by
~2 MiB (as M01 and M02 are over the time ceiling); it is not re-recorded to
fit (SPEC/00 §10.2). It shows the attempts firing, the quarantine attached and
detached, and the records in the security account's console.

_Signed: andaro74, 2026-10-05_
