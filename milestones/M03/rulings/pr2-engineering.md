---
# M03 PR 2 (#20), Engineering's key and the cold review, one file. The
# cold review was drafted by engineering-cold-reviewer from the diff
# d2d1e6d...5871122 and row 3 only; its report is in the PR body verbatim.
# Drafted by the session; ruled by the human as Engineering, 2026-09-26.
ruling: pr2-engineering
seat: Engineering
authorises:
  - .gitattributes
  - Makefile
  - agents/refagent/agent.py
  - agents/refagent/server.py
  - scripts/**
  - src/**
  - tests/**
evidence:
  - SPEC/00-overview.md#8-M03
  - SPEC/03-evals-regression-redteam-corpus.md#6-the-code-that-reads-the-answer-pr-2
  - milestones/README.md
  - milestones/M03/rulings/pr1-engineering.md
  - https://github.com/andaro74/agentkeel/actions/runs/36252383220
  - evals/history/0225d84ee58dc34bb8a3031edcea5f07c19529ec.json
pr: 20
---

# Ruling: M03 PR 2, Engineering, with the cold review

Ruled by andaro74 as Engineering, 2026-09-26, as written.

## The cold review

`engineering-cold-reviewer` read `git diff d2d1e6d...5871122` (86 files,
40 commits) and row 3, not the PR body or the commit bodies, and ran
pytest (497 passed, 1 skipped, no xfail), `make validate` (15 of 15),
`make ledger` (exit 0) and `make plants` (7): **1 BLOCK, 7 FINDING, 9 NOTE**.
Its shape check: every seed's reader lands here, each marker off in the
commit that adds its reader; `src/baseline/` untouched; P5 holds (no new
writer of envelopes; build and gate read the fingerprint the same way and
can still disagree on verdict and cap). The repairs after `5871122` are
their own commits; the diff the reviewer read is unchanged beneath them.

| # | Finding | Status |
|---|---|---|
| B1 | no ruling for the Rule Owner, Security and Product paths | `pr2.md`, `pr2-rule-owner.md`, `pr2-security.md`, this file |
| F1 | S4's reader untested through `gate.rule` with a corpus admitted | **repaired** `dadf78e` |
| F2 | S5's test passes on the human's record alone | **named** `dadf78e` as the weaker witness it is; F3_5, CI's lookup, is the witness `CLAIM_3_CHECKS` requires |
| F3 | the readers' git fallbacks fail open in a shallow clone | **repaired** `dadf78e`: `gate.rule` refuses a shallow clone; the constant says it holds only with merge commits |
| F4 | F3_5 fails on every run once `admitted.yaml` changes | **repaired** `9ac4e2a`: compared at the run file's `admitted_at` |
| F5 | nothing ties the pinned version to the rule files | **read back** `a9c8ff6`: the description and the files both 9cbefa08; no check reads it in CI (no platform role may read a guardrail) |
| F6 | `make plants` said SILENT for an envelope ruled GREEN | **repaired** `dadf78e` |
| F7 | PR 2's measurement not on the branch | **measured**: run 36252383220, envelope `0225d84…`, GREEN, plants 7 of 7, every F3 check passing |
| N1 | S1's and S2's test bodies changed with their readers | recorded: the seeds' files are unchanged; S1's PR 1 assertion could never pass, the new one depends on the reader |
| N2 | claim 3 required from `f82a02a`, before PR 2's merge | recorded: stricter than row 3's words, with no envelope between |
| N3 | the runtime half of the guardrail not fired | recorded: PR 2's run is expected in `mode: runner` (the bundle changed); no prose says the runtime carries it before a runtime envelope shows it |
| N4 | `validate` loosened for ingest rows, `bars` tightened | recorded |
| N5 | schema.json's "M03 makes null a failure" | recorded: the gate fails a mismatch at the commit; null before `55c5b07` is right |
| N6 | the doors file needs Product's ruling | `pr2.md` ruling 1 |
| N7 | the promoter records assessment keys, `invocationMetrics` among them, as policies | recorded; changing it is an ingest redeploy |
| N8 | SPEC/00's deny wording; `pr: 20` expected | **repaired** `df975d2`; the PR opened as #20 |
| N9 | nothing keeps the guardrail's examples away from the attacks | recorded: at most 4 shared words today |

## Also repaired after the cold review, from the seat reports

- `1c33876`: ADR-0009's readers in `two_key`, `ruling_cited` and `validate`
  (the `rule-owner` BLOCK): entries 1 to 5, `keys:`, `deletes:`, a ruling's
  glob at its own merge commit.
- `72d52d1`: the runtime sends the guardrail's ARN (security F1).
- `9ac4e2a`: the positive half of admission read in CI (data-owner F2).

## Engineering's paths

`src/**`, `scripts/**`, `tests/**`, the `Makefile`, `.gitattributes`, and
refagent's `agent.py` and `server.py`: every seed's reader (S1 `606bece`,
S2 `6d49b79`, S3 `bbcf424`, S4 `5d4b7c8`, S5 `f82a02a`, S6 `9e82ea1`,
S7 `a9c11ca`), claim 3's checks (`ac24bfd`), a plant scored by its named
rule (`484db7d`), `open.md` rows 3, 4 and 8 (`5871122`), and the repairs
above.

## What a reader can run

```
uv run pytest -q                                              # no xfail left
uv run pytest tests/test_m03_seeds.py -v                      # S1..S7 and the guards
uv run pytest tests/test_gates.py -k "entry or keys or deletion" -v
uv run python -m src.gates.two_key --base d2d1e6d --pr 20     # not a relaxation against the base
make validate && make ledger && make plants
```
