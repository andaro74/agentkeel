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
`security-reviewer` read the diff at `fe31b6c` (2 BLOCK, 4 FINDING,
6 NOTE) and the repair `fe31b6c..e8ab126` (0 BLOCK, 4 FINDING, 6 NOTE);
both verbatim in the PR body.

## 1. The swap read in `evals.yml`

The observer step, which already runs `scripts/observe_pr.py` on M02's
three run files with `GITHUB_TOKEN`, runs it once more on
`milestones/M04/runs/f4_swaps.yaml`, and the measuring step passes the
result to `make evals` as `SWAPS_OBS`. No new permission, action, secret
or step. `infra/workflows.sha256` carries the new hash.

`scripts/rule_swaps.py` runs inside `make evals`, in the step that holds
the eval role's session. What reaches it, and the gate, from a swap PR:

- **Two files, at fixed paths, from the bot's envelope commit:**
  `evals/history/<sha>.json` and `evals/history/<sha>.baseline-card.json`,
  where `<sha>` and the bot's commit are 40-hex commits GitHub's record
  names. Read with `git show` (no LFS smudge, 60 s per call); never
  imported, never executed. The envelope is written outside the tree; the
  card only at its own path under `evals/history/`, and not over a file
  HEAD holds with other bytes.
- **What the gate itself reads at the swap's commit**, as for any
  envelope, through `git show` and `yaml.safe_load` or `json.loads`:
  `thresholds.yaml` (the cap and the bars), the goldens, the plant
  controls, `agents/refagent/manifest.yaml` (the pin and the incumbent),
  `data/corpus/admitted.yaml`. Data, parsed; nothing from it is run.
- **The card is opened only at its fixed path**: the gate is run with
  `--strict-cards` and REJECTs an envelope naming any other card path
  before opening anything; a card that is not UTF-8 or not a mapping is
  REJECTED.
- **The gate runs in a fresh worktree of HEAD per swap**, so the code
  that rules is this commit's `src/verdict/`, which no swap file can
  replace. Its environment is `PATH`, `HOME`, `USERPROFILE`,
  `SYSTEMROOT`, `TEMP`, `TMP`, `TMPDIR`, `LANG` and `PYTHONPATH`, where
  set: **no `AWS_*`, no `GITHUB_*`, no `ACTIONS_*`**. All swaps together
  have 240 s.
- **Nothing on a swap branch stops the run**: any failure for one swap is
  that swap's `verdict: null` with a note. What comes back is cut: at
  most 50 reasons of 300 characters, one line each, with no `::`.
- **What remains:** a commit that claims the bot's email is attributed
  to the bot, so whoever can push to a swap branch (anyone with write:
  the ruleset covers `main` only) can hand-make an envelope, and the gate
  rules it like any other. `evals_on_measured`, GitHub's own record of
  the `evals` check on the named commit, is kept beside it; bot commits
  pushed by the workflow are not signed, so `verification.verified`
  cannot be required. The close reads both (`pr3.md` §3: the first run
  decides F4.2).

## 2. The review's items

| # | Item | Status |
|---|---|---|
| B1 | The card path came from the envelope: a swap branch could write its own `src/verdict/gate.py` into the worktree, and it ran with the job's AWS session | **Repaired**: fixed paths, a worktree per swap, no credentials in the gate's environment. `test_an_envelope_naming_another_card_path_cannot_put_code_where_the_gate_imports` serves a hostile envelope and a hostile `gate.py`: only the two fixed paths are asked for, and the gate REJECTs. `test_the_gate_gets_no_credentials` |
| B2 | This ruling said what the diff did not do | **Repaired**: §1 rewritten after B1 |
| F1 | One bad file on a swap branch could fail every run | **Repaired**: per-swap `verdict: null`; the gate now REJECTs a file that is not UTF-8 instead of crashing. `test_nothing_on_a_swap_branch_stops_the_run` |
| F2 | The envelope was read at the head | **Repaired**: read at the bot's envelope commit, which `observe_pr` now records (`envelope_commit`). The author is still GitHub's attribution of an email a commit can claim; `evals_on_measured`, GitHub's own record, stands beside it. Carried as the known gap PR 2's cold review named (F4) |
| F3 | PR 4's run could reuse an envelope and read nothing | **Ruled** (`pr3.md` §4): PR 4 records the swaps' re-runs in `f4_swaps.yaml`, not prose, so its run measures |
| F4 | Scripts run under the eval role's session are Engineering's path, not Security's | **Carried** to M05's `open.md` at the close: whether such scripts need the Security seat is a SPEC/00 §5 amendment, not a workflow edit (Product). The swap branches are outside the ruleset; after B1 nothing from them runs |
| N3 | No timeout on the gate call | **Repaired**: 240 s for all swaps, 60 s per git call; `test_the_gate_runs_without_credentials_strictly_in_a_worktree_per_swap_and_in_time` |
| N1, N2, N4, N5, N6 | Workflow unchanged otherwise; no interpolation; hash; no IAM; the good parts not called working | Recorded |

### The second read (`fe31b6c..e8ab126`)

| # | Item | Status |
|---|---|---|
| F1 | The gate opened any card path an envelope named, absolute ones too; a binary card crashed it | **Repaired**: `--strict-cards`; `card_at` REJECTs a card that is not UTF-8 or not a mapping. `test_strict_cards_open_a_card_only_at_its_fixed_path` |
| F2 | Swap-controlled text reached this run's envelope uncut | **Repaired**: 50 reasons of 300 characters. `test_the_gates_reasons_are_cut_before_they_reach_the_envelope` |
| F3 | No total time budget; git calls had none | **Repaired**: 240 s in all, 60 s per git call, seeded as a timeout |
| F4 | §1 did not name every read, the environment exactly, or the forged-bot-commit gap | **Repaired**: §1 above |
| N1 | The `evals.yml` header said "from its head" | **Repaired**; `infra/workflows.sha256` rewritten |
| N2 | A note printed to the log could carry `::` | **Repaired**: notes and reasons are one line with no `::` |
| N3 | One page of 100 commits | **Recorded**: a swap branch with more than 100 commits reads an older bot commit; the first run decides F4.2 |
| N4 | The joined line in `observe_pr.py` | **Repaired** |
| N5 | LFS smudge in the worktree | **Repaired**: `GIT_LFS_SKIP_SMUDGE=1` |
| N6 | The credentials test stopped at `gate_env` | **Repaired**: the test now reads the call site |

## 3. The bootstrap redeploy (PR 2's `pr2-security.md` §1)

Carried here because PR 2 merged before it was recorded. The human ran
`cdk diff --strict` on `AgentkeelBootstrap` and deployed on 2026-09-27
(output kept at 13:12 local, read here by the session). Against the
checklist in `pr2-security.md` §1:

1. **Only the EvalRole's `AWS::IAM::Policy` changed in its statements.**
   `InvokePinnedProfiles` gained the three candidate profiles;
   `InvokePinnedModelsThroughProfilesOnly` gained nine `foundation-model`
   ARNs (three models in three regions) and the same three profiles in
   its `bedrock:InferenceProfileArn` condition.
2. **Nothing else changed in a statement:** no change to the boundary,
   the deploy role or its boundary, `CopyFromThePinnedProfilesOnly`, the
   trust policy or any key policy.
3. **Every other difference is cdk-nag suppression text,** on the
   boundary, five endpoint security groups and the execution, deploy,
   developer and eval roles' policies: `§` in the tree against **`?` on
   the deployed side**. That answers `open.md` row 6: the deployed
   template read `?`; after this deploy it reads `§`. The diff was a
   template diff (CDK could not create a change set), not a change set.
4. **The template at this PR's head:** 49,173 of 51,200 bytes, compact
   JSON, from a local synth (PR 1 measured 49,107 by the same method in a
   scratch worktree; the 66 bytes between are not accounted for here).
5. **Read back after the deploy:** `aws iam get-role-policy` on
   `agentkeel-evals`, `EvalRoleDefaultPolicy39B7B632`: five profiles in
   `InvokePinnedProfiles`; fifteen `foundation-model` ARNs and the same
   five profiles in `InvokePinnedModelsThroughProfilesOnly`'s condition;
   the Deny (`DenyEscalationAndEvidenceDeletion`) and every other
   statement as before. It matches the diff.

Sonnet 4.5 then answered every call on #26: the candidate list is
deployed, and S2's reader has fired on a real run.
