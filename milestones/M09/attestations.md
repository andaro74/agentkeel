# M09 — attestations

Six lines, signed before the close merges. Every seat is one human (R1),
so one person signs all six. Sign by writing your name and the date at the
end of the line, in a commit on the close PR's branch, pushed before the
merge. An unsigned line is not a failed attestation; it is a milestone that
is not closed. Nothing reads this file; the close checks it on the pushed
head before any merge command (`milestones/M05/open.md` row 44).

The ledger row is not waiting on these. Row 9's State is GREEN because the
ledger's reading of the envelope its Measured cell names says so, and
`make ledger` holds the cell to that line. What these six gate is the
merge, and `git tag m09`, which Product rules in `rulings/pr4.md`.

The Tool Owner's and the Threshold Owner's files did not change in M09
(`git diff --stat m08 HEAD` over `tools/`, `agents/refagent/tools/` and
`thresholds.yaml` is empty), so neither seat signs a line. The Rule Owner's
did (`rules/baseline.yaml` added at PR 2; `agents/refagent/manifest.yaml`'s
guardrail version at `#51`), and the Data Owner's R9 was a live condition
of the run, so each signs one.

---

**1. Engineering — the evidence is CI-written and unedited.**

The envelope `evals/history/c503324bac926e4a3295ee7e7f68a98cf254bc42.json`
and its control card were written by `src/verdict/build.py` and
`src/baseline/run.py` in this PR's evals run (38400685274), with
`agent_rules` read by `scripts/observe_rules.py` in the same run from the
security account's audit bucket (as `agentkeel-audit-read`), from GitHub,
from the registry and from the built guardrail (as the eval role), and
committed by `github-actions[bot]` (`1ebd907`). No human edited any of them
after CI wrote them. `src/baseline/` is unchanged since tag `m00`. The one
code change in this PR is the run test's marker (`c503324`); no reader
changed in PR 4, and the run file was not changed after the owner's
`observed` block (`bfa4c19`).

_Signed: _

**2. Security — the grants fired as ruled, and the records are from the separate account.**

The guardrail `at8e36cosq1r:1` was created by the CloudFormation execution
role under the request-tag grant deployed at step 1 (`rulings/pr3-security.md`),
tagged at create, and read back by the eval role under R4's grant; refagent's
guardrail was neither tagged nor touched (its versions 1 to 6 stand, 6 the
baseline's). The answer record row 9 rests on was read from the audit
bucket in the security account (`897698239547`), which the agent's role
cannot write outside its own prefix. The bootstrap deploy of 2026-10-12
01:19Z was made on a draft ruling Security had read and not signed; it is
recorded as such and stands on the "Ruled by" that file carries. No live
control was left relaxed.

_Signed: _

**3. Rule Owner — the split did not relax refagent.**

`rules/baseline.yaml` holds PHONE and EMAIL as ANONYMIZE, no topic, the
prompt-attack filter off (R1); `agents/refagent/rules/` is unchanged since
tag `m08`; refagent's manifest moved from guardrail version 5 to 6 under
`rulings/refagent-version-6.md`, one key, the id unchanged (R2). refagent's
plants read 7 of 7 on every envelope since `#51` merged, this PR's among
them (F9.5).

_Signed: _

**4. Data Owner — the golden was never edited to make the rule fire.**

`tests/fixtures/m09/s1-festival-desk/goldens/g-030.yaml` is as `02db54e`
planted it, and the copy in `agentkeel-studio/festival-desk` at `cd0ad604`
is the same file; the rule blocked it on the first probe, so no rewording
was needed (R9). `g-001` and `g-010` cite rows and clauses that exist in the
full table the template ships. No golden under `evals/goldens/` changed in
M09.

_Signed: _

**5. Product — the row is GREEN and the prose says what GREEN does not mean.**

Row 9 is GREEN. The explainer's "What happened" carries the envelope's
numbers, not a rounded or softened version, and says in plain words what
GREEN does not mean: the platform's own two rules were read present, not
firing; a silent rule stops no merge at M09; one rule fired once. No
"governed", "secure" or "proven" is written about a control that has not
fired on its seeded case. Every finding and every Unsure item of this
milestone has a named home in the close detail.

_Signed: _

**6. Product — the recording's rule.**

M09's video is not yet recorded at the time this close is signed. It is
recorded on `main` at tag `m09` after the merge, as every video from M01
to M07 was, and committed in M09's video pull request, uncounted as `#29`
was (`rulings/pr4.md` ruling 3), where its duration, size and sha256 are
written in `docs/video/README.md`, the Shows cell confirmed, and this line
signed again with the hash.

_Signed: _
