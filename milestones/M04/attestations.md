# M04 — attestations

Five lines, signed before `git tag m04`. Every seat is one human (R1), so
one person signs all five. They are separate because they attest to
different things, and a later reader should be able to see which one was
wrong. The Rule Owner's and the Tool Owner's files did not change in M04,
so neither seat signs a line.

Sign by writing your name and the date at the end of the line, in a commit
on the close PR's branch or on `main` before the tag. An unsigned line is
not a failed attestation; it is a milestone that is not tagged.

The ledger row is not waiting on these. Row 4's State is RED because the
gate's reading of the envelope for `05bd718`, under `READ_THE_SWAPS`,
names the equivalent swap as missed, and `make ledger` holds the cell to
that line. What these five gate is `git tag m04`.

---

**1. Engineering — the evidence is CI-written and unedited.**

The envelope `evals/history/05bd718feb0cc72ab78df13fccf47c3efb8a9314.json`,
its control card and the control's raw observations were written by
`src/verdict/build.py` and `src/baseline/run.py` inside CI run
36362949356, and committed by `github-actions[bot]` in `a3bae6b`. No human
edited any of them after CI wrote them. Every commit under
`evals/history/` in M04, on `main` and this branch, is
`github-actions[bot]`'s (four: `82dfd42`, `e6f01b9`, `f161053`,
`a3bae6b`); so are the four on the swap branches (`bc75a53`, `131dc22`,
`9b6c8dd`, `d1f27d7`). That authorship can be claimed by anyone with
write (M05 `open.md` row 18); `evals_on_measured` in each swap record is
GitHub's own. `src/baseline/` is unchanged since tag `m00`. Each seed's
strict marker came off in the commit that landed its reader
(`pr2-engineering.md`); at the close the six seed tests pass.

Signed: ________  Date: ________

---

**2. Security — what was deployed is what was read back.**

Only the human deployed the bootstrap stack in M04, once, on 2026-09-27,
after reading `cdk diff --strict`: only the eval role's policy changed in
its statements, and the read-back after the deploy (five profiles, fifteen
`foundation-model` ARNs, the Deny as before) matched the diff
(`pr3-security.md` §3). Sonnet 4.5 then answered every call on #26. The
template is 49,173 of 51,200 bytes; the 66 bytes over PR 1's measure are
not accounted for (M05 `open.md` row 20). A model call made without the
pinned guardrail has not been attempted in AWS, and this line does not
say it is refused (row 8).

Signed: ________  Date: ________

---

**3. Threshold Owner — the candidates and the bars were named before any run.**

The breaking (Llama 3.1 8B) and equivalent (Sonnet 4.5) candidates were
named in SPEC/04 §2 before any run, and their swap PRs changed only
`model` to their `pinned_roles` entry (`swap-breaking.md`,
`swap-equivalent.md`, `modelLifecycle` ACTIVE with no end-of-life date).
The label "equivalent" was not moved when #26 regressed `g-005`. The two
`delta_max` bars (2.0x p95, 1.5x agent tokens) were added, not relaxed
(`fb1e6e9`); the cap stayed 150,000 against PR 2's 97,635. Cut 1, the
Haiku 4.5 run, was taken without its condition and is recorded so
(`pr4.md` §4).

Signed: ________  Date: ________

---

**4. Data Owner — correct means grounded, and no golden was edited to fit.**

`g-021` was retired with two keys before grounding landed, and nothing
was added (`fe70686`). An ordinary or trap answer is correct only when
the tool grounded it and the cited `table_row` equals the golden's
(`pr2-data-owner.md`). `g-005` is unchanged: its expected answer is right,
and the equivalent model's is wrong.

Signed: ________  Date: ________

---

**5. Product — the row is the gate's, the page says what RED does not
mean, and every finding has a home.**

Row 4 is copied from the gate's reading of the envelope for `05bd718`,
and `make ledger` exits 0 against it. The reading lands in the close
PR, a named P3 exception (`pr4.md` §2). `docs/milestones/M04.md` says
what RED does not mean, with the envelopes' numbers. Every Finding and
Unsure item of M04 is closed, ruled, or in `milestones/M05/open.md` with a
seat and a milestone. Nothing in this milestone is described as governed,
secure or proven.

Signed: ________  Date: ________
