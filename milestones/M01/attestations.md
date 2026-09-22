# M01 — attestations

Four lines, signed before `git tag m01`. Every seat is one human (R1), so
one person signs all four. They are separate because they attest to
different things, and a later reader should be able to see which one was
wrong.

Sign by writing your name and the date at the end of the line, in a commit
on the close PR's branch or on `main` before the tag. An unsigned line is
not a failed attestation; it is a milestone that is not tagged.

The ledger row is not waiting on these. Row 1's State is RED because the
gate reads its cell as UNMEASURED and SPEC/00 §7 makes that close RED;
`make ledger` holds it there. What these four gate is `git tag m01`, and
what they add is a person's name against four sentences a file cannot
check.

---

**1. Engineering — the evidence is CI-written and unedited.**

The envelope `evals/history/e97125e970ccfc6d044612eb006cdbdbcdb99337.json`,
its baseline card and its raw observations were written by
`src/verdict/build.py`, `src/baseline/run.py` and `src/agent/run.py` inside
CI run 35680056132, and committed by `github-actions[bot]` in `ad7f161`.
No human edited any of them after CI wrote them. Every commit under
`evals/history/` in M01 is `github-actions[bot]`'s. `src/baseline/` is
unchanged since tag `m00` (ADR-0002, `tests/test_baseline_frozen.py`).

Signed: ____________________  Date: __________

---

**2. Security — what was deployed is what was read back, and the first
deploy failed where it says.**

The bootstrap stack was redeployed three times by the human, after reading
`cdk diff` each time (2026-09-21 14:06 and 14:41, 2026-09-22 00:45 UTC).
`scripts/read_back_grants.py` read the grants back after the last one: 50
of 50 rows as expected. The first deploy from `main`, run 35683865472,
failed at the rights table on `kms:CreateGrant`, refused by
`agentkeel-deploy-boundary`, and the stack was deleted from
`ROLLBACK_COMPLETE` by the human. S4 and S6 were refused by the account and
recorded by CloudTrail. The live ruleset requires `checks`,
`cold-review-ruling` and `evals`, and `infra/ruleset/main.json` says the
same.

Signed: ____________________  Date: __________

---

**3. Threshold Owner — the model is the pin, and no bar moved.**

refagent ran as `us.anthropic.claude-sonnet-4-6` in `us-west-2`, version
`null` (ruling p), and the envelope says so. The gate compares all three
with the manifest's pin (ADR-0007, T3). The control ran as
`us.amazon.nova-micro-v1:0`, frozen since `m00`. `thresholds.yaml`'s cap
is 150,000 tokens, unchanged in M01. The measured run spent 54,156. The
re-rule of the cap against that spend is `milestones/M02/open.md` row 18.

Signed: ____________________  Date: __________

---

**4. Product — the row is the gate's, the page says what RED means, and
every finding has a home.**

Row 1 is copied from the gate's reading of that envelope, and
`make ledger` exits 0 against it. The row is RED on the second half of the
claim alone: the first half held on every seeded case, and the second
was never read. `docs/milestones/M01.md` says both, in the reader's words,
with the envelope's numbers. Every Finding and Unsure item of M01 is
closed, ruled, or in `milestones/M02/open.md` with a seat and a date.
Nothing in this milestone is described as governed, secure or proven.

Signed: ____________________  Date: __________
