---
# M04 PR 2 (#24), Security's key. Drafted by the session from the
# security-reviewer report on this PR; the human rules as Security before
# the merge. Product's file is rulings/pr2.md.
ruling: pr2-security
seat: Security
authorises:
  - .github/workflows/evals.yml
  - infra/bootstrap/app.py
  - infra/workflows.sha256
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md#51-when-each-is-measured
  - milestones/M04/feasibility.md
  - milestones/M04/open.md
  - milestones/M03/rulings/pr3-security.md
  - https://github.com/andaro74/agentkeel/actions/runs/36331360122
pr: 24
---

# Ruling: M04 PR 2, Security

Drafted by the session; the human rules as Security before the merge.

## 1. The eval role's swap candidates (S2's reader; note 15 on PR 1)

`EVAL_CANDIDATES` (Sonnet 4.5, Llama 3.1 8B, Haiku 4.5) is added to the
eval role's two invoke statements and to nothing else. `MODELS` is
unchanged, so the agent boundary, the deploy role and
`CopyFromThePinnedProfilesOnly` are unchanged: no candidate can become an
application profile or reach the runtime. The template synthesises to
49,107 of 51,200 bytes (`open.md` row 7). Sonnet 4, LEGACY, is not on
the list.

**The redeploy, by the human, during this PR.** Read `cdk diff --strict`
on `AgentkeelBootstrap` and deploy only if:

1. only the EvalRole's `AWS::IAM::Policy` changes: `InvokePinnedProfiles`
   gains 3 `inference-profile/us.<candidate>` ARNs;
   `InvokePinnedModelsThroughProfilesOnly` gains 9 `foundation-model` ARNs
   and its `bedrock:InferenceProfileArn` condition the same 3 profiles;
2. nothing changes in the boundary, the deploy role, its boundary,
   `CopyFromThePinnedProfilesOnly`, the trust policy or any key policy;
3. any metadata change is the `§` suppression text only: record whether
   the deployed side read `§` or `?` (`open.md` row 6);
4. the template is measured again at this head;
5. after the deploy, `aws iam get-role-policy` on the eval role is read
   back and recorded.

Anything else in the diff stops the deploy. Until the equivalent swap
PR's run shows no `AccessDeniedException` (PR 3), the candidate list is
read by the S2 test on the synthesised template only: `F4_2` from it is
a test-only witness, and nothing calls the list working.

## 2. A-vs-A in `evals.yml`

A new step decides A-vs-A: where `pin_moved` (the function the gate
requires `F4_3` by) says the pin is not the incumbent's, or where the
pull request carries the `a-vs-a` label. The label comes in through
`env:` as `true` or `false`; it can only add a run, and a present `F4_3`
that fails still fails the envelope. `on: pull_request` has no
`labeled` type, so **the label is on this PR before the push that
measures it**, or that run is one run of each (`security-reviewer` F2).
`infra/workflows.sha256` carries the new hash.

**Timing** (`security-reviewer` F4), from the record: on M04 PR 1's run
(36331360122) `make evals` took 93 s and started 8 s after the
credentials were issued. Twice the runs is about 190 s, inside the
900-second session and the 15-minute job. No change to
`role-duration-seconds`. This PR's step times are recorded with its
envelope.

## 3. Findings carried, not fixed here

- The eval role's invoke is not conditioned on the guardrail, now for
  three more models (`security-reviewer` F1): `open.md` rows 26 and 40,
  M05.
- `pin_moved` and the gate are the PR's own code, so a swap PR that also
  edits `src/verdict/` can switch off its own A-vs-A (`security-reviewer`
  F3): the header's known gap, `open.md` row 30, M05. The swap PRs change
  `model` only, and their rulings say so.
- `observe_pr` found a swap's measured commit by a commit that claims the
  bot's name, and read its envelope from the branch. The envelope reading
  is cut from this PR (cold review B1: only the gate rules on an
  envelope). What stays is GitHub's own record: the pull, the checks on
  its head, and the `evals` run on the named commit. At PR 3 the gate
  rules the swap's envelope at its commit, and the named commit is held
  to the `evals` run GitHub recorded on it.
