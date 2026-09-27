---
# M04 PR 3 (#27), Security's key. Drafted by the session from the
# security-reviewer report on this PR; the human rules as Security before
# the merge. Product's file is rulings/pr3.md.
ruling: pr3-security
seat: Security
authorises:
  - .github/workflows/evals.yml
  - infra/workflows.sha256
evidence:
  - SPEC/04-model-swap.md#4-falsifiers
  - milestones/M04/rulings/pr2-security.md
pr: 27
---

# Ruling: M04 PR 3, Security

Drafted by the session; the human rules as Security before the merge.
`security-reviewer` read the diff at `fe31b6c`: 2 BLOCK, 4 FINDING,
6 NOTE, verbatim in the PR body.

## 1. The swap read in `evals.yml`

The observer step, which already runs `scripts/observe_pr.py` on M02's
three run files with `GITHUB_TOKEN`, runs it once more on
`milestones/M04/runs/f4_swaps.yaml`, and the measuring step passes the
result to `make evals` as `SWAPS_OBS`. No new permission, action, secret
or step. `infra/workflows.sha256` carries the new hash.

`scripts/rule_swaps.py` runs inside `make evals`, in the step that holds
the eval role's session. What reaches it from a swap PR, after the repair:

- **Two files, at fixed paths, from the bot's envelope commit:**
  `evals/history/<sha>.json` and `evals/history/<sha>.baseline-card.json`,
  where `<sha>` is a 40-hex commit GitHub's record names. Read with
  `git show`; never imported, never executed. The envelope is written
  outside the tree; the card only at its own path under `evals/history/`,
  and not over a file HEAD holds with other bytes.
- **The gate runs in a fresh worktree of HEAD per swap**, so the code
  that rules is this commit's `src/verdict/`, which no swap file can
  replace. Its environment is `PATH`, the temp and home variables and
  `PYTHONPATH`: **no `AWS_*`, no `GITHUB_TOKEN`**. It has 300 s.
- **Nothing on a swap branch stops the run**: any failure for one swap is
  that swap's `verdict: null` with a note.

## 2. The review's items

| # | Item | Status |
|---|---|---|
| B1 | The card path came from the envelope: a swap branch could write its own `src/verdict/gate.py` into the worktree, and it ran with the job's AWS session | **Repaired**: fixed paths, a worktree per swap, no credentials in the gate's environment. `test_an_envelope_naming_another_card_path_cannot_put_code_where_the_gate_imports` serves a hostile envelope and a hostile `gate.py`: only the two fixed paths are asked for, and the gate REJECTs. `test_the_gate_gets_no_credentials` |
| B2 | This ruling said what the diff did not do | **Repaired**: §1 rewritten after B1 |
| F1 | One bad file on a swap branch could fail every run | **Repaired**: per-swap `verdict: null`; the gate now REJECTs a file that is not UTF-8 instead of crashing. `test_nothing_on_a_swap_branch_stops_the_run` |
| F2 | The envelope was read at the head | **Repaired**: read at the bot's envelope commit, which `observe_pr` now records (`envelope_commit`). The author is still GitHub's attribution of an email a commit can claim; `evals_on_measured`, GitHub's own record, stands beside it. Carried as the known gap PR 2's cold review named (F4) |
| F3 | PR 4's run could reuse an envelope and read nothing | **Ruled** (`pr3.md` §4): PR 4 records the swaps' re-runs in `f4_swaps.yaml`, not prose, so its run measures |
| F4 | Scripts run under the eval role's session are Engineering's path, not Security's | **Carried** to M05's `open.md` at the close: whether such scripts need the Security seat is a SPEC/00 §5 amendment, not a workflow edit (Product). The swap branches are outside the ruleset; after B1 nothing from them runs |
| N3 | No timeout on the gate call | **Repaired**: 300 s |
| N1, N2, N4, N5, N6 | Workflow unchanged otherwise; no interpolation; hash; no IAM; the good parts not called working | Recorded |

## 3. The bootstrap redeploy (PR 2's `pr2-security.md` §1)

Carried here because PR 2 merged before it was recorded. Sonnet 4.5
answered every call on #26, so the eval role's candidate list is deployed.
**Still to record, from the human:** the `cdk diff --strict` read against
the checklist (only the EvalRole's policy changed), whether the deployed
side read `§` or `?` (`open.md` row 6), the template size at that head,
and `aws iam get-role-policy` on `agentkeel-evals` read back.
