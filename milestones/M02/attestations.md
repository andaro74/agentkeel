# M02 — attestations

Five lines, signed before `git tag m02`. Every seat is one human (R1), so
one person signs all five. They are separate because they attest to
different things, and a later reader should be able to see which one was
wrong.

Sign by writing your name and the date at the end of the line, in a commit
on the close PR's branch or on `main` before the tag. An unsigned line is
not a failed attestation; it is a milestone that is not tagged.

The ledger row is not waiting on these. Row 2's State is GREEN because the
gate read the envelope for `8033c2a` as GREEN with `checks.F2_1` and
`checks.F2_2` passing, and `make ledger` holds the cell to that line. What
these five gate is `git tag m02`, and what they add is a person's name
against five sentences a file cannot check.

---

**1. Engineering — the evidence is CI-written and unedited.**

The envelope `evals/history/8033c2a7a0588e557df577464c190e64a435e88a.json`,
its control card and its raw observations were written by
`src/verdict/build.py`, `src/baseline/run.py` and `src/agent/run.py` inside
CI run 35951008874, and committed by `github-actions[bot]` in `905f438`.
No human edited any of them after CI wrote them. Every commit under
`evals/history/` in M02 is `github-actions[bot]`'s. `src/baseline/` is
unchanged since tag `m00` (ADR-0002, `tests/test_baseline_frozen.py`).
The three earlier envelopes on this branch (`12b4646`, `47258f2`,
`6daf6c4`) were not edited either; they rule RED under the gate from
`74624cb` and nothing cites them.

Signed: ____________________  Date: __________

---

**2. Security — the live ruleset is the export, nobody bypasses it, and
what was deployed is what was read back.**

The live `main` ruleset requires `checks`, `cold-review-ruling`, `evals`,
`ruling-cited` and `two-key`, with `bypass_actors` `[]`, and
`infra/ruleset/main.json` says the same; `validate` compared them on
every run of this PR. The owner's `gh pr merge 14 --admin` was refused by
GitHub on 2026-09-23 at 13:34:13Z (rule suite 4192991324), and the owner
listed as a bypass actor made `validate` RED (job 107206831180) until the
list was emptied at 13:45:29Z. The bootstrap stack was redeployed once by
the human after reading `cdk diff` (`UPDATE_COMPLETE` 2026-09-23T04:45:35Z,
one resource, the agent boundary, `dynamodb:Scan` added). The M00 stack
`AgentkeelM00EvalRole` was destroyed (`DELETE_COMPLETE` 13:48:15Z) before
`infra/eval-role/` was removed. The `RULESET_TOKEN` reaches no step that
runs code from a pull request.

Signed: ____________________  Date: __________

---

**3. Threshold Owner — the model is the pin, and every bar moved with two
keys or not at all.**

refagent ran as `us.anthropic.claude-sonnet-4-6` in `us-west-2`, version
`null` (ruling p), inside the deployed runtime, and the envelope says so;
the gate compares all three with the manifest's pin (ADR-0007, T3). The
control ran as `us.amazon.nova-micro-v1:0`, frozen since `m00`.
`thresholds.yaml`'s cap is 150,000 tokens, unchanged in M02; the measured
run spent 54,009. Every bar carries `relaxes:`. The one relaxation
planted, the cap raised to 300,000 with one key, was refused on PR 14 and,
with two files from this seat, on PR 15. `g-012` was retired with this
seat's key beside the Data Owner's (PR 12).

Signed: ____________________  Date: __________

---

**4. Data Owner — no golden was edited to green a build, and no id was
renamed.**

`g-010`'s expected answer, edited to reward the answer it was written to
catch, was refused on PR 16 with no ruling. `g-005` renamed to `g-099` was
refused on PR 18; `g-099` is burned. `g-012` was retired, never renamed,
with two keys (PR 12), and `g-021` was added and has never passed. Every
golden id on `main` at `97d3c76` is present or retired at the close.

Signed: ____________________  Date: __________

---

**5. Product — the row is the gate's, the page says what GREEN does not
mean, and every finding has a home.**

Row 2 is copied from the gate's reading of that envelope, and
`make ledger` exits 0 against it. `docs/milestones/M02.md` says what
GREEN does not mean, in the reader's words, with the envelope's numbers.
Every Finding and Unsure item of M02 is closed, ruled, or in
`milestones/M03/open.md` with a seat and a date. Nothing in this
milestone is described as governed, secure or proven; the ceiling's one
refusal is recorded as unplanned.

Signed: ____________________  Date: __________
