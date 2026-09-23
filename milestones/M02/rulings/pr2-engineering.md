---
# M02 PR 2 (#12), Engineering's key. Product's file is rulings/pr2.md.
ruling: pr2-engineering
seat: Engineering
authorises:
  - src/**
  - scripts/**
  - tests/**
  - Makefile
  - agents/refagent/Dockerfile
  # every field but the ones the Tool Owner, the Threshold Owner and Security name in their files
  - agents/ratings-helper/manifest.yaml
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#6-the-code-that-reads-the-answer-pr-2
  - milestones/M02/runs/rehearsal_doors.json
  - milestones/M02/runs/rehearsal_seed_prs.json
  - milestones/M02/runs/row16_second_workflow.yaml
pr: 12
---

# Ruling: M02 PR 2, Engineering

Drafted by the session; the human rules as Engineering before the merge.
This file is Engineering's key on its own paths and takes no second key
over anything; the cold review's file is `pr2-cold-review.md`.

## `src/gates/` (SPEC/02 §6)

- `__init__.py`: what the two gates share. Two trees, a checkout or a
  revision; the changed paths by blob id, computed with
  `git hash-object --stdin-paths` and not the index's stat cache, which
  missed a same-size edit made in the same second as the checkout (the
  seeds are exactly that, and the first draft missed one); CODEOWNERS
  parsed with `# seat:` headers, last match wins as GitHub resolves it;
  rulings by `pr:` (`12`, `#12`, the URL); a manifest attributed field by
  field; the bot's exemption under `evals/history/`.
- `ruling_cited.py`: every uncovered path listed, the owner from the base
  (from the PR only when the base has no table, and the output says so),
  a ruling file with this PR's number covering itself.
- `two_key.py`: the closed list of SPEC/02 §2, no more; seats counted,
  not files; the owner's file must cover and a second seat must name.
- `tests/test_gates.py` builds a small repository per test and holds
  what the seeds do not reach.

## `src/validate/` (six checks)

`codeowners.py`, `edges.py` (two-sided, cycles, ceilings),
`golden_ids.py`, `semver.py`, `ruleset.py`, and `check_relaxes` in
`checks.py`. Two read `origin/main` through the same `Tree`; a revision
base resolves in the tree's own repository (the first draft resolved it
in this one and a test caught it). `ruleset.py` reads with a token and
refuses to read an absent bypass list as anybody's. The manifest schema
gains an optional `version` (Tool Owner's field).

## `scripts/observe_pr.py` and `build`'s readers

The instrument for S4 and F2.2, in `observe_attempt.py`'s pattern: it
reads the run file, asks the API, writes an observation, decides nothing.
`build.check_from_seed_prs`, `check_from_bypass`, `check_from_doors` read
it into `checks` through `both()`. Rehearsed once against PRs #10 and
#11 (row 17): both records read as expected. The Makefile wires F2_1's
first source now (`F2_1_CASES`, five tests; S4's is not among them) and
carries the three observation variables PR 3 sets.

## A retired golden (Door 2's reader)

`build.load_goldens` and `load_golden_kinds` skip a golden whose
`retired:` is set; the agent runner does not ask it; the frozen control
still does (ADR-0002) and `build` drops that answer with a note. The gate
reads the goldens **as they stood at the envelope's commit**
(`golden_kinds_at`, ruling m's pattern), so the M00 and M01 envelopes,
written over fifteen goldens that included `g-012`, still read as they
did: `make ledger` holds rows 0 and 1, and `tests/test_retired.py` holds
row 1's envelope GREEN. The tests that used `g-012` as a passing trap use
`g-010`; the S7 seed test overlays an uncited answer for `g-021`, and the
seed file is untouched.

## The markers

Off in the commits that landed the readers: `cc6e568` (S1 both forms,
S2; `two_key.py`) and `9068349` (S3, S5; `edges.py`, `golden_ids.py`).
S4's stays until the attempts (`tests/fixtures/README.md`).

## What Engineering does not do here

No change under `src/baseline/` (ADR-0002). No envelope written or read
by anything but `build` and `gate`. No seed edited: `git apply --check`
passes on all five patches at the head. `infra/eval-role/` not removed.

## What a reader can falsify

```
uv run pytest tests/test_gates.py tests/test_validate_m02.py tests/test_observe_pr.py tests/test_retired.py tests/test_m02_seeds.py
git show cc6e568 --stat; git show 9068349 --stat
uv run python -c "from src.verdict import golden_kinds_at, ROOT; print(len(golden_kinds_at('9407615dcde09308490f6699c21a18100bfedcd2', ROOT/'evals/goldens/v1')[0]))"   # 15, g-012 among them
make ledger
```
