# Carried into M01

Written at the M00 close (PR 3). Every item that M00 raised and did not
settle is here, with the seat that rules it and when. Nothing is carried
without both. `/open-milestone` reads this file first: an item dated
"at M01 open" is answered in M01 PR 1's feasibility note, and an item
dated "before M01 PR 1" is answered before that PR's first commit.

An item that is neither ruled nor re-dated by the M01 close is a finding
about this project, not about M01.

## Left unruled by M00 PR 2 (four of the six; two were ruled at the close)

| # | Item | Seat | When |
|---|---|---|---|
| 1 | Is `tests/fixtures/` exempt from CLAUDE.md's "never write an envelope by hand"? The F0.2 seed is a hand-written envelope and has to be, because it is the thing the gate must refuse. The rule as written forbids the seed it depends on. | Product | before M01 PR 1 |
| 2 | The schema's file name (report 8.4). The file is `src/verdict/schema.json`, as CLAUDE.md has it; its `$id` is `verdict.schema.json`, as SPEC/00 §6 has it. Both are true and a reader has to know that. Rule one form or say in SPEC/00 §6 that the `$id` is not the path. | Product | at M01 open |
| 3 | Who owns a price table for `cost_usd`. The field is `null` in every envelope because no seat owns a price per token; the cap is in tokens. A price table is a seat-owned input, not a constant someone pastes. | Threshold Owner | at M01 open |
| 4 | Is `replay_history` a reader of envelopes under P5? SPEC/00 §8 names it, and `gate.py` is meant to be the only reader that rules on one. The seat rules once whether P5 admits a second reader that rules on nothing. | Engineering | before M01 PR 1 |

Ruled at the close, and listed here because they land in M01:

| # | Item | Seat | When |
|---|---|---|---|
| 5 | Which card a later envelope points at (report 1.4). Ruled in ADR-0004 amendment 1: the baseline card at tag `m00`, by content hash, recorded once as `baseline_card_sha` in `thresholds.yaml`; a card with a different hash is a build error. Not built at M00. `thresholds.yaml` is the Threshold Owner's file, so the line carries their key too. | Engineering, with Threshold Owner | at M01 PR 1 |

## From the cold review of M00 PR 2, still open

| # | Item | Seat | When |
|---|---|---|---|
| 6 | FINDING 3: `build` and `gate` share `plants.plant_ids` and `replay_history`, so they cannot disagree on either RED condition by logic. P5 wants them able to disagree. Split, or rule that the shared part is not what P5 is about. | Engineering | before M01 PR 1 |
| 7 | FINDING 7: the "already measured" skip key reads the tree, and `checks.F0_3` is read from GitHub, not from the tree. A ruleset change on `main` changes the measurement without changing a file. | Engineering, with Security | at M01 open |
| 8 | FINDING 10: "CI-written" is `GITHUB_ACTIONS == "true"`, an environment variable a runner sets and a laptop can set too. It becomes real when `two-key` lands at M02. | Engineering | at M01 open |
| 9 | A gate-REJECTED envelope is still committed to `evals/history/`. Rejected evidence in the evidence folder. Decide whether `record` refuses, or whether rejected envelopes get their own folder as `pre-scope/` did. | Engineering | at M01 open |
| 10 | Row 0's Seeded commit cell names `22b5499` only, not the second seed `f9f1342`. Either a row may name two seeded commits or the second seed belongs somewhere else. Do not edit row 0 to find out; rule the format first. | Product | at M01 open |
| 11 | History is keyed on (scope, golden id) with one envelope per commit. From M01 a run has two subjects, the control and refagent. Whether they share an envelope is M01's to settle before refagent's passes can become anyone's bar. | Engineering | at M01 PR 1 |

## Security (Finding S-1 and what PR 2 left)

| # | Item | Seat | When |
|---|---|---|---|
| 12 | S-1's last step: a run of `evals.yml` that assumes the **redeployed** role, showing STS evaluates the `job_workflow_ref` condition. The stack was redeployed 2026-09-19T00:20:25Z; the run is recorded in `milestones/M00/rulings/pr3.md`. Security signs it on the observation. | Security | before M01 PR 1 |
| 13 | Spend enforced outside the runner: a Budgets alarm per inference profile that disables the eval role. `cost-cap` reads only what the PR's own runner wrote down, after the spend. M01's bootstrap stack; carried to SPEC/01. | Security | at M01 open |
| 14 | M01 PR 1 adds refagent's profile ARN to `infra/eval-role/app.py`, with a Security ruling. The role allows the baseline's profile only until then. | Security | at M01 PR 1 |
| 15 | The F0.3 observer cannot read `bypass_actors`, so `checks.F0_3: pass` does not say the repository owner cannot bypass the required check. P9 asks for that. | Security | at M01 open |
| 16 | `evals.yml`'s header says a `record` push "starts no workflow". It does start runs of both workflows, which GitHub parks at `action_required` with no jobs. The effect is as described; the sentence is not. `evals.yml` is a measured path, so the edit rides with M01's first measurement. | Security | before M01 PR 1 |
| 17 | The five pinned action SHAs were resolved from each repo's latest release through the API, not checked with `git ls-remote`. Check them once against the tags they claim to be. | Security | before M01 PR 1 |
| 18 | Not observed: a direct call to a foundation model, and a call through an unpinned profile, both denied. Two `AccessDenied` results from the deployed role would show the policy is what the README says. | Security | at M01 open |
| 19 | `MaxSessionDuration` stays 3600. The ruling asked for 900; IAM's floor is one hour. Recorded, not fixable in IAM. Decide whether a shorter-lived credential is worth minting another way. | Security | at M01 open |
| 20 | `agentkeel-m00-evals` is a fixed role name and the M01 bootstrap stack absorbs this role. Delete the M00 stack, or the names collide. | Security | at M01 PR 1 |

## Threshold Owner

| # | Item | Seat | When |
|---|---|---|---|
| 21 | Is Nova Micro still a fair control? On the plant it is right on 2 of 12 scored replies and 5 of 12 are one self-contradictory object. Once refagent has numbers, rule whether a delta against this control says enough. | Threshold Owner | at M01 open |
| 22 | Is an over-cap run a recorded RED, or no record at all? `cost-cap` exits before `build` today, so an over-cap run writes nothing and leaves no trace in `evals/history/`. | Threshold Owner | before M01 PR 1 |
| 23 | The pin says `us-west-2` and the inference profile serves from three regions (us-east-1, us-east-2, us-west-2). The card records one region; the call can be served from another. Say which the card means. | Threshold Owner, with Security | at M01 open |

## Data Owner

| # | Item | Seat | When |
|---|---|---|---|
| 24 | Finding F0.1: `g-012` passed on every run, for the wrong reason (§6.4). The Data Owner may retire `g-012` — never rename (R11) — and add a replacement whose expected `constraints` the frozen prompt cannot produce. Retiring is a two-key change, and `two-key` is not built until M02. | Data Owner | at M01 open |
| 25 | The replacement's id. `g-016` to `g-020` are already promised to the first red-team goldens at M03 (feasibility.md §9). Rule the numbering before an id is used twice. | Data Owner | at M01 open |
| 26 | `sequel_no_inherit`, or any new constraint code, is not among the six the frozen prompt can emit, and `src/baseline/` is closed from tag `m00` (ADR-0002). How a frozen control meets a new code is a question for both seats. | Data Owner, with Threshold Owner | at M01 open |

## Product

| # | Item | Seat | When |
|---|---|---|---|
| 27 | `docs/video/milestones/M00.mp4`. SPEC/00 §10.5 says a close is not ruled ready without the explainer page and the video. The page is in the close PR; the video is recorded at the tag, after the merge. The departure is ruled at the M00 close and written in `milestones/M00/README.md`. Record the video, or amend §10.5 to say the video follows the tag. | Product | before M01 PR 1 |

## Not carried — already homed, named here so M04 does not have to go looking

These two are not open questions. Each has a file that holds it and a
milestone that acts on it, and neither needs anything from M01.

- **Finding F0.4**, the control is not deterministic at temperature 0:
  ADR-0004 and `milestones/M00/feasibility.md` §6.5, run by run. It is
  the seed for SPEC/04's A-vs-A design, which assumes a model compared
  with itself shows zero diff. SPEC/04 says what "zero diff" means for a
  control like this one — how many runs, which goldens, what spread —
  at M04 open. Product.
- **"Profile status is not model status"**: `milestones/M00/README.md`,
  Findings. `model-watch` reads `modelLifecycle` from
  `list-foundation-models`, never `inferenceProfileSummaries.status`.
  The sentence goes to SPEC/04 at M04 open. Product.
