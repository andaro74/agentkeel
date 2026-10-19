# M10 — attestations

Five lines, signed before the close merges. Every seat is one human (R1),
so one person signs all five. Sign by writing your name and the date at the
end of the line, in a commit on the close PR's branch, pushed before the
merge. An unsigned line is not a failed attestation; it is a milestone that
is not closed. Nothing reads this file; the close checks it on the pushed
head before any merge command (`milestones/M05/open.md` row 44).

The ledger row is not waiting on these. Row 10's State is what the
ledger's reading of the envelope its Measured cell names says, and `make
ledger` holds the cell to that line. What these five gate is the merge, and
`git tag m10`, which Product rules in `rulings/pr4.md`.

The Rule Owner's and the Threshold Owner's files did not change in M10
(`git diff --stat m09 HEAD` over `rules/`, `agents/*/rules/`, the guardrail
ids and versions, and `thresholds.yaml` is empty; N was reused, not moved,
R6), so neither seat signs a line. The Tool Owner's did (`callers` in the
manifest schema and in the two manifests at PR 2, under
`rulings/pr2-tool-owner.md`; festival-desk's `callers` pull request #4 is
the live arm), and the Data Owner's R5 (the record's shape and what a raw
record may carry onto an envelope) was a live condition of the run, so each
signs one.

---

**1. Engineering — the evidence is CI-written and unedited.**

The envelope `evals/history/14ab792156f585c9010275e6b6be3f687cee22c6.json` and its control card were written
by `src/verdict/build.py` and `src/baseline/run.py` in this PR's evals run
(39143365127), with `caller` read by `scripts/observe_caller.py` in the same
run from the security account's audit bucket (as `agentkeel-audit-read`:
the four call records under `calls/agents/festival-desk/`, the bypass's
data event in the platform account's trail objects, the answer record of
deploy run 39076739413) and from GitHub (as the eval role: festival-desk's
pull request #4 and its manifest at the merge commit), and committed by
`github-actions[bot]` (`4de0fab`). No human edited any of them after CI
wrote them. `src/baseline/` is unchanged since tag `m00`. The code changes
in this PR are the run test's marker (`14ab792`) and the destination
policy's test following the policy (`e05095c`, `0ebfdbd`); no reader
changed in PR 4, and the run file was not changed after the owner's
`observed` block (`14ab792`).

_Signed: andaro74, 2026-10-18_

**2. Security — the door and the records are as ruled, and the records are from the separate account.**

festival-desk's door was built by its own stack under the execution role's
door grants (`agentkeel-cfn-exec-door`, deployed by hand and ruled in
`rulings/pr3-security.md`) at deploy run 39076739413; the runtime admits
the door's client alone. The four call records row 10 rests on were read
from the audit bucket in the security account (`897698239547`), delivered
by the Logs subscription through the destination `agentkeel-calls`, which
no platform-account principal can edit; the bypass's refusal was read from
the platform account's trail objects in the same bucket. The calls
destination's policy is PR 2's, the platform account as principal and
nothing narrower, because CloudWatch Logs refused both narrower forms on
2026-10-18; security F3 on PR 3 stands as named in `rulings/pr4-security.md`,
with its routes, and no sentence here or in the explainer calls the record
forgery-proof. The two refused deploys were made on a draft of this PR's
ruling; each rolled back and is recorded as such. No live control was left
relaxed.

_Signed: andaro74, 2026-10-18_

**3. Tool Owner — the field admits what the two seats ruled and nothing else.**

`callers` is in the manifest schema in the shape SPEC/10 §2 fixes
(`rulings/pr2-tool-owner.md`); refagent's and `ratings-helper`'s read
`callers: []`, unchanged since PR 2; festival-desk's names one subject,
`lantern-desk`, `issuer: self`, admitted by the platform check on pull
request #4 and read back at its merge commit by the observer. No caller was
admitted in agentkeel with one key (`two-key` entry 7, ADR-0016, F10.5 on
every envelope since PR 2's merge). An agent repository has no `two-key`,
so festival-desk's own admission took one commit, as SPEC/10 §8 says; not
described otherwise.

_Signed: andaro74, 2026-10-18_

**4. Data Owner — the records on the envelope carry what R5 allows and nothing more.**

The four read records were mapped by `build`'s `from_raw` from what AWS
delivered, with the drop list applied (`DROPPED_KEYS`: the caller's address,
user agent, key id, principal id, session context and TLS details); the
first live records were re-read against that list at this close
(`rulings/pr4-data-owner.md`). No record carries a credential; the
observer and `build` refuse one that does. The stated caller of each step
has one source, the run file, and the bypass's principal is on the envelope
because the run file states it. No golden under `evals/goldens/` and
nothing under `data/` changed in M10; `g-030` is as `02db54e` planted it and
was blocked through the door on the deploy's answer record.

_Signed: andaro74, 2026-10-18_

**5. Product — the row's State is the envelope's, and the prose says what it does not mean.**

Row 10's Measured cell is `make ledger`'s "as row M10 reads it" line for
`14ab792156f585c9010275e6b6be3f687cee22c6`, copied, not retyped. The explainer's "What happened" carries the
envelope's numbers and says what the verdict does not mean. No "governed",
"secure" or "proven" is written about a control that has not fired on its
seeded case. Every finding and every Unsure item of this milestone has a
named home in the close detail; with no M11, each stands there. M10's
recording was ruled not recorded at PR 1 (ADR-0015 decision 6) and
`docs/video/README.md`'s M10 row says so and nothing more. The count is
4 of 4.

_Signed: andaro74, 2026-10-18_
