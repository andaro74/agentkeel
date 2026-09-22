---
# M02 PR 2 (#12), the measurement. Product's key. One seat per file
# (M01 PR 1, ruling B); from M02 each seat's paths are in that seat's
# file, in the shape ruling-cited reads: Security's key is
# rulings/pr2-security.md, Engineering's rulings/pr2-engineering.md,
# the Threshold Owner's rulings/pr2-threshold-owner.md, the Data Owner's
# rulings/pr2-data-owner.md, the Tool Owner's rulings/pr2-tool-owner.md,
# and the cold review's rulings/pr2-cold-review.md.
ruling: pr2
seat: Product
authorises:
  - SPEC/02-seats-and-change-gates.md
  - CLAUDE.md
  - docs/milestones/M02.md
  - docs/milestones/README.md
  - docs/platform/overview.md
  - milestones/README.md
  - milestones/M02/**
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md
  - milestones/M02/feasibility.md
  - milestones/M02/runs/api_probes.yaml
  - milestones/M02/runs/row16_second_workflow.yaml
  - milestones/M02/runs/rehearsal_doors.json
  - milestones/M02/runs/rehearsal_seed_prs.json
pr: 12
---

# Ruling: M02 PR 2 (measure), Product

Drafted by the session; the human rules as Product before the merge.
Cites `SPEC/00-overview.md#8-M02` for M02's build paths. This is the PR
that reads the plant: the six seed tests lost their markers in the
commits that landed their readers, five pass on refusing, and S4's stays
until the attempts (below). Later PRs do not decide the row.

## What Product rules here

1. **`checks.F2_1` on PR 2's own envelope is its first source alone.**
   SPEC/02 §7 as written at PR 1 had `F2_1` failing on PR 2's run because
   S4's `observed` is null. That cannot be executed: `evals` is a required
   check whose job exits with the gate's code, so a RED envelope would
   have left this PR unable to merge through the ruleset it measures,
   with `bypass_actors` `[]`. SPEC/02 §4 and §7, the ledger row and
   `milestones/M02/README.md` are amended in place, with the reason. The
   second source and `checks.F2_2` are wired at PR 3; the readers land
   here. The gate is to require both on every agent envelope from this
   PR's merge commit on, a constant set at PR 3 as M01 PR 3 set
   `ADR_0007`. One more line of the P3 exception §5.1 names.
2. **S4's marker stays on.** Its reader (`scripts/observe_pr.py`) is in
   the tree; its input (`f2_1_bypass.yaml`, `observed:`) is the human's
   after the merge. A strict marker taken off now fails every run until
   then. `tests/fixtures/README.md` says so.
3. **The `ratings-helper` stub declares no edge.** SPEC/02 §6 said the
   stub would name refagent in `may_be_called_by`; on `main` that would
   itself be one-sided, and a two-sided edge would have made S3's patch
   stop applying. The seed is never edited; §6 is amended to say what was
   built and why.
4. **Door 2 is this PR's merge**, as ruled at PR 1 (finding 2): `g-012`
   retired and `g-021` added with the Data Owner's key
   (`pr2-data-owner.md`, covering) and the Threshold Owner's
   (`pr2-threshold-owner.md`, naming the path). `two-key` on this PR's
   head is Door 2's check run; the merge commit with both files is its
   record; PR 3's run reads them from `f2_2_three_doors.yaml`.
5. **Two things this PR was asked to do and does not.** `infra/eval-role/`
   stays: `AgentkeelM00EvalRole` was `UPDATE_COMPLETE` in the account on
   2026-09-22, and the directory is removed after the human destroys the
   stack (Unsure E). `observed_at_pr2_merge` in `runs/row10_first_deploy.yaml`
   stays null: the merge is the first arm64 deploy, and the run file now
   records that the reuse branch will not refuse `822fe2b5` by name at
   it, because the Dockerfile pin moved the bundle digest (Security).
6. **Cut list (SPEC/02 §9): nothing cut.** Ceilings, the cycle check,
   computed semver, the login check and `docs/platform/overview.md` are
   all in this PR, each in its smallest form; the cap is 2 of 4 after
   this PR.

## Seat per path

- **Product** (this file): SPEC/02 (§4, §5.1, §6, §7 amended in place);
  the ledger's header row for this PR and row 2's expected output and
  cap; the M02 folder (the PR 2 detail, the run files this PR adds, the
  six ruling files); the explainer's tense; `docs/platform/overview.md`;
  CLAUDE.md's tree and `validate` lines. `docs/milestones/README.md` is
  what `make ledger-plain` writes.
- **Security**: `pr2-security.md`.
- **Engineering**: `pr2-engineering.md`.
- **Threshold Owner**: `pr2-threshold-owner.md`.
- **Data Owner**: `pr2-data-owner.md`.
- **Tool Owner**: `pr2-tool-owner.md`.

## The PR shape, checked against CLAUDE.md

Held. PR 2 is the measurement: it builds every reader SPEC/02 §6 names
and nothing that a later PR would need to build to read the plant. It
re-plants nothing: all five patches still apply at the head (`git apply
--check`). It writes no envelope by hand; its own envelope is `evals.yml`'s.
It touches nothing under `src/baseline/`.

## To falsify this PR's own claims

```
uv run pytest tests/test_m02_seeds.py          # 5 passed, 1 xfailed (S4)
git log --format='%h %s' c77e872..HEAD          # the markers come off in cc6e568 (S1, S2) and 9068349 (S3, S5)
git show cc6e568 -- tests/test_m02_seeds.py     # two markers removed, nothing else in the test file
git show 9068349 -- tests/test_m02_seeds.py     # two markers removed
make plants                                     # S1-S5: every reader "in the tree"
make validate                                   # 12 ok
uv run python -m src.gates.ruling_cited --base origin/main --pr 12   # 0: every path covered
uv run python -m src.gates.two_key --base origin/main --pr 12        # 0: g-012 retired with two keys
git checkout 0e78ef8 && make validate           # FAIL workflow-hash on gates.yml (row 16)
git apply --check tests/fixtures/m02/*.patch    # every seed still applies
make ledger                                     # rows 0 and 1 still hold under the goldens at their commits
```
