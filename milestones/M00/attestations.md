# M00 — attestations

Three lines, signed before `git tag m00`. Every seat is one human (R1),
so one person signs all three; the three are separate because they
attest to different things, and a later reader should be able to see
which one was wrong.

Sign by writing your name and the date at the end of the line, in a
commit on the close PR's branch or on `main` before the tag. An unsigned
line is not a failed attestation; it is a milestone that has not closed.

---

**1. Engineering — the evidence is CI-written and unedited.**

The envelope `evals/history/9407615dcde09308490f6699c21a18100bfedcd2.json`,
its baseline card and its raw observations were written by
`src/verdict/build.py` and `src/baseline/run.py` inside
[run 35406351135](https://github.com/andaro74/agentkeel/actions/runs/35406351135)
and committed by `github-actions[bot]` in `76fa683`. No human edited any
of the three after CI wrote them. The one human commit under
`evals/history/` moved the pre-scope envelope for `8fb4b80` into
`evals/history/pre-scope/` and changed no byte of its content
(ADR-0004, schema compatibility).

Signed: ______________________  Date: ____________

---

**2. Threshold Owner — the control is what the card says it is.**

The baseline ran as `us.amazon.nova-micro-v1:0` in `us-west-2` over
Converse, temperature 0, `maxTokens` 512, one system prompt with sha256
`2c3d9b754f8c285e95c3590cea61cafb1f59e5c5af64a1ea7b776c6c383684ab`, no
tools, no guardrail, no retrieval. These are the parameters as measured;
they were confirmed, not changed, before this tag. From the tag they are
frozen with the code by ADR-0002, and `tests/test_baseline_frozen.py`
fails on any diff to `src/baseline/` or to that prompt hash.

Signed: ______________________  Date: ____________

---

**3. Product — the row is the envelope's, and the page says what GREEN
does not mean.**

Row 0 in `milestones/README.md` is copied from that envelope and
`make ledger` exits 0 against it. The state is GREEN because no check
failed and nothing the gate reads regressed; at M00 the gate reads no
golden, because every result is `scope: control` and the control is never
gated (ADR-0004). `docs/milestones/M00.md` says so in the reader's own
words, and records Findings F0.1, F0.4 and S-1. The control scored 1 of
15 on the measured run and no more than 2 of 15 on any run. Nothing in
this milestone is described as governed, secure or proven.

Signed: ______________________  Date: ____________

---

Not attested here, and deliberately: that the narrowed eval role is
enforced by STS. The stack was redeployed on 2026-09-19T00:20:25Z, and
the first run that assumes the redeployed role is recorded in
`milestones/M00/rulings/pr3.md`. Security signs that in M01, on an
observation, not here on a deploy.
