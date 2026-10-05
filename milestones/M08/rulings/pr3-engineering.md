---
# M08 PR 3, Engineering's key. One tests/ change: the xfail markers on all
# three run-made tests come off, since all three runs were made at this PR.
# No code under src/ changed; the readers landed in PR 2 and that cold
# review's one FINDING was repaired inside PR 2 (64a550d). This ruling
# carries the engineering-cold-reviewer report run on the final diff. DRAFT
# until the human rules.
#
# Product's file is rulings/pr3.md; Security's (run 2's egress rule) is
# rulings/pr3-security.md.
ruling: pr3-engineering
seat: Engineering
authorises:
  - tests/test_m08_seeds.py
evidence:
  - SPEC/00-overview.md#8-M08
  - SPEC/08-game-day-drill.md#5-the-seeded-cases
  - milestones/M08/rulings/pr2-engineering.md
pr: 47
---

# Ruling: M08 PR 3, Engineering — DRAFT

To be ruled by andaro74 as Engineering.

## What this covers

- **`tests/test_m08_seeds.py`.** The `xfail(strict)` markers on
  `test_run1_was_made`, `test_run2_was_made` and `test_run3_was_made` are
  all off, since all three runs were made on 2026-10-05 and each run file's
  `observed:` block is now filled (SPEC/08 §5.1). `made()` still asserts
  `observed is not None`, so the tests are not vacuous; a run reverted to
  `observed: null` turns its marker back on. (run1/run2 came off earlier in
  PR 3; run3 comes off in this diff.)

## What it does not do

- **No code change.** `src/verdict/drill.py`, `scripts/observe_drill.py`,
  `src/verdict/build.py`, `src/verdict/gate.py`, `src/ledger.py` and
  `src/verdict/__init__.py` are unchanged. The PR 2 cold review's one
  FINDING (dead `DRILL_RUNS`/`READERS` constants) was repaired inside
  PR 2 at `64a550d`; nothing is owed to PR 3.
- **No `evals/goldens/`, `thresholds.yaml`, `rules/`, `data/corpus/`,
  manifest ids or `src/baseline/` touched.** No `two-key` relaxation.

## The cold review

`engineering-cold-reviewer` on the final diff `origin/main...eebcb7e`,
2026-10-05. Verbatim:

> Read: the diff origin/main...eebcb7e (8 files). I also read ledger row 8
> and tests/test_m08_seeds.py's `made()` helper (line 67, asserts observed
> is not None).
>
> Cold review of M08 PR 3 (PR #47, measure/repair). Shape is in bounds:
> fills the three run files' observed blocks, adds three DRAFT rulings + a
> README "During PR 3" section, fixes two expected.pushed_before pointers
> (run1→drill-agent#3, run3→#4), lifts three xfail markers. No src/, infra/,
> goldens, thresholds, baseline, or manifest ids touched; readers landed in
> PR 2. Row 8 stays OPEN/RED as expected; nothing flips the plant GREEN. The
> problems are internal contradictions in the diff.
>
> BLOCK 1 — the diff disagrees with itself on whether F8.5 held.
> pr3-engineering.md (Unsure) said "F8.5 fired on IAM propagation delay
> (~12 s between attach at 00:51:33Z and the first AccessDenied at
> 00:51:45Z …)". drill_run1.yaml says the opposite: attached 14:09:50Z,
> refused_call CreateLogStream AccessDenied at 14:10:45Z, f8_5: held, "no
> call by the role was answered after the attach." README prints "F8.5
> held." Three disagreements: timestamps (00:51 pair matches no run window
> 14:06–15:10Z), gap (~12 s vs 55 s), and whether calls were answered after
> attach. Cannot be ruled until run1 YAML, README, and pr3-engineering.md
> agree.
>
> BLOCK 2 — the Engineering ruling misdescribes the test change it
> authorises. pr3-engineering.md said only test_run1_was_made's marker comes
> off and test_run2/test_run3 "stay xfail". The diff removes @expected_failure
> from ALL THREE tests. The removals are functionally correct (all three
> observed blocks non-null; made() still asserts observed is not None) — but
> the ruling text must be corrected.
>
> FINDING 1 — run 2's invocation postdates the records it produced.
> drill_run2.yaml: invocation.at 14:28:32Z, but a1_iam ListKeys AccessDenied
> at 14:28:22Z and a1_flow ACCEPT at 14:28:06Z; the flow also precedes
> window.opened 14:28:08Z. Reconcile or explain the flow aggregation-window
> start.
>
> FINDING 2 — run 3's GREEN-answer arm (and a3's leak) is unmeasured, not
> demonstrated. Recovery is asserted only from absence of attempts/REJECT
> flows; claim 8's "recovers … answer GREEN" arm is never positively
> observed. Honestly disclosed (ADR-0013), row RED regardless — but PR 4's
> explainer must not read "recovers end to end" as demonstrated.
>
> NOTE 1 — pr3.md said "today is 2026-10-04" while runs were made 2026-10-05.
> NOTE 2 — pr3-security.md promises the 2>&1 console output of
> authorize/revoke-security-group-egress in drill_run2.yaml's observed block;
> the block carried structured fields only.
> NOTE 3 — stated "recorded 5 of 6"; the run reads a1/a3/a5 recorded, a4/a6
> not = 3 of 6, F8.1 firing on a4/a6. PR 4's Measured cell should carry 3.
>
> BLOCK: 2 · FINDING: 2 · NOTE: 3

### Resolution (repairs in this PR, before it opens)

| # | Item | Status |
|---|---|---|
| BLOCK 1 | F8.5 disagreement | **Repaired.** The 00:51/F8.5-fired text was the FIRST attempt's reading (that run crashed at import and is superseded). This file now reads the retake: **F8.5 HELD** (refused CreateLogStream by the role at 14:10:45Z, nothing answered after the 14:09:50Z attach), matching `drill_run1.yaml` and the README. |
| BLOCK 2 | test-change misdescription | **Repaired.** "What this covers" now says all three markers are off. |
| FINDING 1 | run 2 timestamp ordering | **Repaired** in `drill_run2.yaml`: `invocation.at` relabelled as the SDK return time; the attempt is timed by the IAM event (14:28:22Z, inside the 14:28:08–14:28:40 window); the flow record's time is the VPC flow-log capture-window boundary (±60 s aggregation), not the packet time, and is annotated as such. |
| FINDING 2 | run 3 GREEN arm unmeasured | **Recorded, not repaired** (ADR-0013). `drill_run3.yaml` and `pr3.md` now state the "answers GREEN" arm is **unmeasured** (RED by a fixture defect); PR 4's explainer must not claim "recovers end to end" — only "recovery removed the hostile behaviour." Seat: Product (the explainer). |
| NOTE 1 | stale date | Repaired in `pr3.md`. |
| NOTE 2 | run 2 console transcript | Repaired: the `authorize/revoke-security-group-egress` output (rule `sgr-071300307a9132ebe`, `Return: true`, timestamps) is transcribed into `drill_run2.yaml.observed`. |
| NOTE 3 | recorded count | `drill_run1.yaml` now states **recorded 3 of 6** (a1, a3, a5), a4/a6 not recorded, and **F8.1 fires on a4/a6**. PR 4's Measured cell carries 3, not 5. |

## Unsure

- **a4 and a6 refused but NOT recorded** (run 1's finding, in
  `drill_run1.yaml.observed`). In the retake all six attempts fired (the
  first attempt's "attempts never reached CloudTrail" was the import crash,
  superseded): **a5 reached the API and logged an explicit-deny
  AccessDenied**, but **a4 (`s3:PutObject`) and a6 (`s3:PutBucketPolicy`)
  produced no event in either account** — stopped below the API (the S3
  endpoint policy / SG), or PutObject data events are not logged. So they
  are refused but unrecorded, and **F8.1 fires** on the missing record.
  Not a repair for PR 3 (M08 builds no control; the drill reads what
  happened). Seat: Engineering. Recorded under the M08 decision rule.
- **F8.5 HELD** — after the deny-all attached (14:09:50Z) a call by the role
  was refused in the trail (CreateLogStream AccessDenied, 14:10:45Z) and no
  call was answered after the attach; the incident-responder F2 hazard (the
  deny-all refusing before any call reaches the trail, M05 S7) did not
  realize this time. Recorded in the run 1 YAML and carried to the explainer
  at PR 4. Seat: Engineering + Security.
- **The drill-agent fixture defect** (run 3's finding). The prompt slate
  maps the goldens' titles to t-005/t-002, but the goldens cite rows
  r-019/r-009 (t-012/t-004), so the agent finds no row and both goldens
  fail — RED identically in the hostile and clean runs. This makes **run 3
  RED not GREEN (F8.3 fires)** and leaves the recovery's GREEN arm (and
  a3's credential effect) **unmeasured**. ADR-0013: named, not repaired (the
  run was made; SPEC/08 §5.1 makes each run once). If a future milestone
  wants the GREEN arm demonstrated, the fixture is corrected there, not
  here. Seat: Product (the fixture lives in the drill-agent repo) and
  Engineering (the reader). Recorded under the M08 decision rule.
