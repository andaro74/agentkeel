---
# M04 PR 2 (#24), Engineering's key and the cold review, one file. Drafted
# by engineering-cold-reviewer from the diff 8e438d1...39f0e16 and row 4
# only; repaired and completed by the session. Product's file is
# rulings/pr2.md; the Data Owner's, the Threshold Owner's and Security's
# are beside it.
ruling: pr2-engineering
seat: Engineering
authorises:
  - Makefile
  - agents/ratings-helper/manifest.yaml
  - agents/refagent/server.py
  - scripts/observe_pr.py
  - src/validate/checks.py
  - src/validate/lifecycle.py
  - src/verdict/__init__.py
  - src/verdict/build.py
  - src/verdict/gate.py
  - src/verdict/plants.py
  - src/verdict/replay_history.py
  - src/verdict/schema.json
  - tests/conftest.py
  - tests/fixtures/README.md
  - tests/fixtures/m04/s1-breaking-pin.patch
  - tests/fixtures/m04/s2-equivalent-pin.patch
  - tests/fixtures/m04/s5-deprecated-pin.patch
  - tests/test_build.py
  - tests/test_cost_cap_and_ledger.py
  - tests/test_evals_workflow.py
  - tests/test_gate.py
  - tests/test_m01_seeds.py
  - tests/test_m04_seeds.py
  - tests/test_observe_pr.py
  - tests/test_p5_disagree.py
  - tests/test_refagent.py
  - tests/test_replay_history.py
  - tests/test_retired.py
  - tests/test_validate_lifecycle.py
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md#2-words-used-here
  - SPEC/04-model-swap.md#6-the-code-that-reads-the-answer-pr-2
  - SPEC/04-model-swap.md#51-when-each-is-measured
  - milestones/README.md
  - milestones/M04/README.md
pr: 24
---

# M04 PR 2, the measure: Engineering's cold review

Read cold by `engineering-cold-reviewer`: `git diff 8e438d1...39f0e16`
(42 files, +1710 -114) and ledger row 4. Not read: commit bodies, the PR
body, the feasibility argument. 1 BLOCK, 6 FINDING, 6 NOTE; the report
is in the PR body verbatim. The human rules as Engineering before the
merge.

The three seat reports on this PR (Data Owner, Threshold Owner,
Security) each say they read the tree at HEAD `89e57ec`, not the diff:
**weaker witnesses** (`/cold-review`, M02 PR 1 row 8). Each of their
findings was re-checked against the diff by the session while it was
repaired or ruled, and every one is about a line this PR added.

## Dispositions

| # | Item | Status |
|---|---|---|
| B1 | P5: `observe_pr` read a swap's envelope and `build` ruled on it | **Repaired** (`b3a693f`): the envelope reading, `swap_held`, `check_from_swaps` and `--check-swaps` are cut. `observe_pr` keeps GitHub's own record. PR 3 has the gate rule the swap's envelope at its commit (settlement (b), then (a) at PR 3) |
| F1 | PR 2's A-vs-A rests on the `a-vs-a` label | **Stands, as ruled** (`pr2-security.md` §2): the PR carries the label before its measuring push. Claim 4.3 on refagent is read from this PR's envelope only if `a_vs_a` is there with `agent: []`; absent is unmeasured, not zero diff |
| F2 | The cache refusal read the first run only | **Repaired** (`b3a693f`): every run |
| F3 | The control's second run could make the envelope UNMEASURED | **Repaired** (`b3a693f`): recorded in its diff, gates nothing |
| F4 | The swap's measured commit rests on a spoofable author | **Repaired with B1** for this PR: no envelope is read from the branch. PR 3 holds the named commit to GitHub's `evals` run on it |
| F5 | S4's token case could pass on `gate.spend`'s reason | **Repaired** (`b3a693f`): the reason starts `F4_4: ` and names `p95_ms` or `agent_tokens` |
| F6 | No test drove `--a-vs-a-control` | **Repaired** (`b3a693f`): `test_a_vs_a_through_builds_command_line_with_the_controls_second_run`. The Makefile's chain itself first runs on this PR's labelled run; `make -n` showed both second runs and both flags |
| N1 | A non-mapping tool call crashed `grounded` | **Repaired** (`b3a693f`) |
| N2 | The gate cannot re-check grounding | **Recorded**: it has no raw run, as it has no `expected`. For the explainer at close |
| N3 | `pin_moved` said "not moved" when git had no merge-base | **Repaired** (`b3a693f`) |
| N4 | The first run after a merged swap is RED for no incumbent | **Recorded**: as ruled (`pr2-threshold-owner.md` §1, note 9); M05's `open.md` |
| N5 | Row 4 moved from traps 2/3 to 2/2 | **Recorded**: the same passing set, announced at PR 1, authorised by `pr2.md`; not a lowered bar |
| N6 | PR 2's run is in the runner | **Recorded**: `server.py` and the manifest move the bundle digest; the runner median has 8 envelopes |

## What the session ran that the reviewer could not

Each seed's test with its reader switched off, before its marker came
off (S1 grounding, S2 the candidate list, S3 `differ`, S4 the bars, S5
`lifecycle.check`): each failed on its planted assertion, with its
planted message. With the reader on, each passes.

## The first labelled run, refused

The PR opened at `4f7757d`. The `opened` event fired before `gh` added
the `a-vs-a` label, so that run (36344929457) was cancelled during
pytest, before any model call, and the PR was closed and reopened. The
reopened run, 36345059724, read `LABELLED: true` and made both second
runs; `build` then refused: "A-vs-A: the control's second run was on a
dirty tree". No envelope was written. The cause was the Makefile's
chain, not the tree: `src/baseline/run.py`, frozen, calls any untracked
file dirty, and the control's second run started after the first had
written into `evals/history/`. Repaired in the Makefile: the control's
second run goes first, outside the tree, and its raw is moved in after
the first run. `test_both_control_runs_start_on_a_tree_with_nothing_untracked`
renders the chain with `make -n`; it fails on `4f7757d`'s Makefile and
passes on the repair. The cold review read neither; the refusal is
`build`'s own check in `a_vs_a_pair`.

## What this does not rule

The swap PRs (read at PR 3). This PR's own measuring run, which does not
exist yet: before the merge, this file gains that run's URL, the
envelope commit, and its `a_vs_a`, `p95_ms`, `agent_tokens`, `F4_1` to
`F4_4` and verdict, as `gate.measured_at` prints them.

## Falsify it

    git diff --stat 8e438d1...HEAD -- src/baseline/            # empty: the control untouched
    uv run pytest -q                                           # all pass on a clean tree
    uv run pytest -q tests/test_m04_seeds.py -rA               # S1..S5, six passed, none xfail
    uv run python -m src.validate                              # 16 ok
    uv run python -m src.gates.ruling_cited --base origin/main --pr 24
    uv run python -m src.gates.two_key --base origin/main --pr 24
    grep -rn "evals/history" scripts/ --include=*.py           # observe_pr reads no envelope (B1)
    grep -n "cacheReadInputTokens" src/verdict/build.py        # usage + more (F2)
    uv run python -c "from src.verdict import gate; print(gate.required_checks('HEAD'))"
    uv run python -m src.verdict.gate evals/history/<PR 2's envelope>.json   # once CI writes it
