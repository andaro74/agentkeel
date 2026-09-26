# M03 — attestations

Six lines, signed before `git tag m03`. Every seat is one human (R1), so
one person signs all six. They are separate because they attest to
different things, and a later reader should be able to see which one was
wrong. M03 is the first milestone in which the Rule Owner's files change,
so that seat signs a line of its own.

Sign by writing your name and the date at the end of the line, in a commit
on the close PR's branch or on `main` before the tag. An unsigned line is
not a failed attestation; it is a milestone that is not tagged.

The ledger row is not waiting on these. Row 3's State is GREEN because the
gate read the envelope for `cb06c0d` as GREEN with `checks.F3_1`, `F3_2`,
`F3_3`, `F3_5` and `F3_6` passing and plants 7 of 7, and `make ledger`
holds the cell to that line. What these six gate is `git tag m03`.

---

**1. Engineering — the evidence is CI-written and unedited.**

The envelope `evals/history/cb06c0dbf0019088c664c6df1ce7d67cc64f7d58.json`,
its control card and the control's raw observations were written by
`src/verdict/build.py` and `src/baseline/run.py` inside CI run
36270471757, and committed by `github-actions[bot]` in `013a1c5`. No human
edited any of them after CI wrote them. The agent's raw observations,
from which `build` counted each plant by its named rule, are a CI
artifact of that run, not committed (M04 `open.md` row 34, item b). Every commit under
`evals/history/` in M03 is `github-actions[bot]`'s (three: `2b2229e`,
`506c8ed`, `013a1c5`). `src/baseline/` is unchanged since tag `m00`
(ADR-0002, `tests/test_baseline_frozen.py`). Each seed's strict marker came
off in the commit that landed its reader (`pr2-engineering.md`); S1's and
S2's test bodies changed with their readers (its N1). At the close the
seven seed tests and the two guards pass.

Signed: andaro74  Date: 2026-09-26

---

**2. Security — what was deployed is what was read back.**

Only the human deployed the bootstrap and ingest stacks in M03, after
reading `cdk diff`: at PR 2's stops A and B (guardrail versions 1 to 4,
and the ingest stack from `0ee873e`), and at PR 3's (version 5 from
`0a90d52`, the promoter's pin from `70e7d53`, each a checkout with no
tracked change). The read-backs matched the expected grants: 79 cases
after PR 2's stop A, 81 before and after PR 3's, 0 mismatches. The production bucket is configured with Object Lock in
COMPLIANCE mode for 1 day. The seed amendment was put in quarantine on 2026-09-26 at
03:34:52Z and is not in the production bucket, read by CI in run
36270471757. The merge deploy (run 36272077619) moved the runtime to
guardrail version 5; its load check wrote 20 observations with 0 errors
(`runs/pr3_merge_deploy_load_check.md`, a log, not an envelope).
None of the ingest stack's own refusals has been attempted in AWS, and
this line does not say they work.

Signed: andaro74  Date: 2026-09-26

---

**3. Rule Owner — each plant names the rule that must block it, and no
rule was relaxed on `main`.**

`agents/refagent/rules/guardrail.yaml` and `redteam.yaml` name, in
`blocks`, the rule for each of the seven plants. The manifest pins
`1088aw3ujhyd` version 5, whose `get-guardrail` description is
`rules sha256 b2cff2a1…`, the digest of the two files at `0a90d52` and at
the head. `two-key` found no relaxation against `d2d1e6d` (PR 2) or
`a423292` (PR 3). The three narrowings made inside PR 2 were never on
`main` or on an envelope. `g-014`'s PII rule is in the file and not
counted; no page calls it working.

Signed: andaro74  Date: 2026-09-26

---

**4. Data Owner — no golden was edited to green a build, and the corpus
is what `admitted.yaml` names.**

`g-016` to `g-020` were added at M03 and never edited. No golden id was
renamed or retired in M03. `data/corpus/admitted.yaml` names six documents
by sha256, and `validate` holds it to their bytes. It does not name the
unsigned amendment. The longest run of words shared by a live golden's
question and a document is 5, under the bound of 12. Every name in the
corpus is invented and was searched before the ruling.

Signed: andaro74  Date: 2026-09-26

---

**5. Threshold Owner — the model is the pin, and no bar moved.**

refagent ran as `us.anthropic.claude-sonnet-4-6` in `us-west-2`, version
`null`, and the envelope says so. The control is frozen since `m00`.
`thresholds.yaml` is unchanged in M03. The cap is 150,000 tokens; the
measured run spent 52,131 (47,034 in, 5,097 out), and the cap was
re-ruled against PR 2's 52,415 without moving (`pr3-threshold-owner.md`).

Signed: andaro74  Date: 2026-09-26

---

**6. Product — the row is the gate's, the page says what GREEN does not
mean, and every finding has a home.**

Row 3 is copied from the gate's reading of the envelope for `cb06c0d`, and
`make ledger` exits 0 against it. `docs/milestones/M03.md` says what GREEN
does not mean, with the envelope's numbers, including that no envelope
reads the deployed runtime at version 5. Every Finding and Unsure item of
M03 is closed, ruled, or in `milestones/M04/open.md` with a seat and a
date. SPEC/03 cuts 1 to 4 were not built and are recorded as taken at the
close, not before. Nothing in this milestone is described as governed,
secure or proven.

Signed: andaro74  Date: 2026-09-26
