---
# M05 PR 2, Engineering's key and the cold review of the measure. Drafted by
# engineering-cold-reviewer from the diff 5a5720e...27f2678 and row 5 only;
# repaired and completed by the session. Product's file is rulings/pr2.md,
# Security's pr2-security.md, the Threshold Owner's pr2-threshold-owner.md.
ruling: pr2-engineering
seat: Engineering
authorises:
  - src/verdict/containment.py
  - src/verdict/build.py
  - src/verdict/gate.py
  - src/verdict/__init__.py
  - src/verdict/plants.py
  - src/verdict/schema.json
  - src/ledger.py
  - src/validate/checks.py
  - scripts/observe_containment.py
  - agents/refagent/server.py
  - Makefile
  - tests/**
evidence:
  - SPEC/00-overview.md#8-M05
  - SPEC/05-containment-and-evidence.md#6-the-code-that-reads-the-answer-pr-2
  - milestones/README.md
  - milestones/M05/README.md
pr: 31
---

# Ruling: M05 PR 2, Engineering, with the cold review

Drafted by the session; the human rules as Engineering before the merge,
after this PR's run has recorded S1, S2 and S6 (cold review F3).

## What was read

`engineering-cold-reviewer` read the diff `5a5720e...27f2678` (50 files,
18 commits) and row 5 only; two commit bodies were printed by `git show
--stat`, and nothing it found rests on them. It ran nine test files (192
passed, 5 xfailed), `validate` (16 ok), `ledger` (row 5 on `36a86b1` reads
"containment not read ... RED"), and S4's and S5's tests with their readers
monkeypatched off: each failed on its planted message. 0 BLOCK, 5 FINDING,
11 NOTE, verbatim in the PR body.

## What holds

- The shape is a measure: S4's reader (`server.py`, before any model or
  table call) and S5's (`build`, applied to the agent only), the observer,
  `containment` and row 5's reading, as row 5's Expected cell names them.
  No Measured cell is written; the gate's `rule` is unchanged.
- The fixtures under `tests/fixtures/m05/` are unchanged; only S4's and
  S5's markers came off (`27fd1e7`, `52b1051`).
- P5: the observer and `server.py` write raw; `build` writes `containment`
  and `alarm_latency_s`; the gate does not import `containment.py`, works
  each latency out again and holds it to N at the envelope's commit.
- `containment` is optional; no older envelope becomes invalid.

## Dispositions

| # | Finding | Status |
|---|---|---|
| F1 | S7's model-call window ran 30 min past the human's detach time | **Repaired** (`ec6747b`): up to the trail's own detach `eventTime`; no detach in the trail is a mismatch; a call after the detach is excluded (test) |
| F2 | Row 5's rules hold three record shapes no real record has shown (the role ARN with its path, `AccessDenied` exactly, the S3 message) | **Read by this PR's run**, stated before it: S2's and S6's `principal` and `error_message` in the envelope's `containment`. If a shape differs, PR 3 is the repair. The phrase itself was tightened (`ec6747b`, security-reviewer) |
| F3 | No attempt made at the head reviewed | **Ruled after the run**: this file is ruled only once the run on the head that fills S1's, S2's and S6's run files has recorded them; that head and run are written here before the ruling line |
| F4 | Nothing tested the two stacks, nor the stand-in's hand-copied denies | **Repaired** (`482eb61`): `tests/test_containment_stacks.py` synthesises both and holds what S2, S3 and S6 are refused by, and the stand-in's list equal to the construct's |
| F5 | `evals.yml` described the archive as if it had run | **Repaired** (`ca0d07d`, Security) |
| N1 | S4's last assert is also met by the no-ceiling refusal | Recorded; `test_m05_readers.py` pins depth 3 over 2, and fails F0_2 if it breaks |
| N2 | S4's "no model call" is vacuous if the trail carried no Bedrock events | Recorded; S7 is the positive control (a denied Converse must be recorded) |
| N3 | The observer is all or nothing, and reads the whole window | Recorded; fails closed. PR 3 narrows it if a run times out |
| N4 | `object_at` names S2's key, not the run file's | Recorded; the key is the run file's command |
| N5 | S6's `retain_until` is recorded, not compared | Recorded; the trail's refusal and the version still there decide |
| N6 | `LIVE_SEEDS` unused | **Repaired** (`ec6747b`) |
| N7 | The run-file test exercises nothing on `observed: null` | Recorded |
| N8 | F5_1 required from `2c88265`, before the merge; fails open if git cannot place it | Recorded; a squash would trip the test |
| N9 | The gate takes build's `made` and `refused` as given | Recorded; SPEC/05 §4 puts the reading in build, the latency and N in both |
| N10 | `FORTY` could match a real answer | Recorded; fails closed, and shows as a regressed golden |
| N11 | The rulings are drafts; the gate on them is this PR's | Recorded; the drafts are ruled before the merge |

From the Threshold Owner's report (Engineering's to rule): F7, N read at the
commit untested, **repaired** (`ec6747b`, `detection_at` at `5a5720e` and
`a4e8922`); F8, build's N never compared with the commit's, **repaired**
(a containment read against another N is a miss); N11, a negative latency,
**repaired** (a miss).

Found while repairing F4 (item k): the six IAM5 suppressions on refagent's
role passed `applies_to`, which cdk-nag's binding dropped, so each
suppressed every finding and the CSV printed one reason. Repaired with
`appliesTo` (`ca0d07d`); the test reads the six reasons in the template.

## The second read, of the repairs (`27f2678...a07d6ba`)

`engineering-cold-reviewer` read the repair diff and row 5: 0 BLOCK, 2
FINDING, 6 NOTE, verbatim in the PR body. Each repair closes what it
claims; every gap left fails closed. F1 (the phrase seen in no real
record) is F2 above, read by this PR's run. F2 (the run files' stated
tests looser than the reader): **repaired**, S2's and S6's lock-off
`refused_when` say the phrase, before the attempts (Product). N4 (a test
docstring) **repaired**; N5 (the stack's docstring) **repaired** (Security).
Recorded: N1, the refagent ARN is six literals, each divergence closed;
N2, build's N from another tree reads RED, never GREEN; N3, S7's window
opens at the call less a minute, not at the attach; N6, the write-once
Deny and the archive agree, and neither has run.

## The run that decides this ruling

Filled in before the ruling line: the head whose run records S1, S2 and
S6, its run URL, and row 5's reading of its envelope from `make ledger`.

## What a reader can run

```
uv run pytest -q tests/test_m05_seeds.py tests/test_m05_readers.py tests/test_observe_containment.py tests/test_containment_stacks.py
uv run pytest -q                                   # the suite; S1, S2, S3, S6, S7 xfailed until each is recorded
make validate                                      # sixteen; cdk-nag over the two new stacks
make ledger                                        # "as row M05 reads it" names each seed and each miss
git show 27fd1e7 52b1051 --stat                    # the two readers and the two markers
```
