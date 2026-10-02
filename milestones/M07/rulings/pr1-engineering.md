---
# M07 PR 1 (#38), Engineering's key and the cold review, one file. Drafted
# from engineering-cold-reviewer's read of the diff 57b9bf6...01e8ff8 and
# row 7 only; the repairs after it (4240d9e) were not read cold again.
# Product's file is rulings/pr1.md; Security's is rulings/pr1-security.md.
ruling: pr1-engineering
seat: Engineering
authorises:
  - src/verdict/plants.py
  - tests/test_m07_seeds.py
  - tests/fixtures/README.md
  - tests/fixtures/m07/**
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - milestones/README.md
  - milestones/M07/README.md
  - milestones/M07/feasibility.md
pr: 38
---

# Ruling: M07 PR 1, Engineering, with the cold review

Ruled by andaro74 as Engineering, 2026-10-02, as written.

## What this authorises

- **`src/verdict/plants.py`**: `SEEDS_M07`, six lines, and its entry in
  `SEEDS_BY_MILESTONE`. A list `make plants` prints; nothing rules on it.
- **`tests/test_m07_seeds.py`**: thirteen tests, each
  `xfail(strict=True, raises=AssertionError)`, none calling AWS, a model
  or GitHub.
- **`tests/fixtures/m07/**` and `tests/fixtures/README.md`'s M07
  section**: the fixtures of S0 to S5. Each is a false state or a held
  case beside one; none is an envelope and none is copied to
  `evals/history/`.

## What was read

`engineering-cold-reviewer` read the diff `57b9bf6...01e8ff8` (39 files,
+2350 / -7), the commit subjects and row 7, not the PR body or commit
bodies. **It ran nothing** (its report says so), so each check it names
was run by the caller, on the head this file is committed in:

- `uv run pytest tests/test_m07_seeds.py -q`: 13 xfailed; with
  `--runxfail`, 13 failed, each an `AssertionError` with the message in
  `feasibility.md` §3;
- `uv run pytest tests/test_m06_seeds.py -q`: 7 passed, 1 xfailed (S3);
- `make plants`: S0 to S5, each reader "not in the tree yet";
- `make ledger`: exit 0; `make ledger-plain`: no diff;
- `make validate`: nineteen checks, ok;
- `uv run pytest -q`, the full suite: the counts are in the PR body.

BLOCK 1, FINDING 6, NOTE 6. Its second read, of the six M06 commits
`milestones/M07/open.md` row 15 owed: FINDING 5, NOTE 1. The report is
verbatim in the PR body.

## What holds (the reviewer's sections 1 to 4)

1. **Shape.** Only PR 1 material. Nothing makes the claim pass: no
   `scripts/observe_upgrade.py`, `platform_upgrade.py`, `retire_agent.py`,
   `model_watch.py`, `src/verdict/upgrade.py` or
   `infra/grafana/panel2.json`, and no `grant_errors`, `f7_2`, `f7_3`,
   `panel_verdict_mismatch`, `surface_plants` or `SURFACE_PLANTS` under
   `src`, `scripts`, `infra` or `.github`.
2. **One commit per seed, each after SPEC/07's revision and SPEC/00's
   amendment**: `c870bca`, `ef3d88a`, `3872c13`, `ea53ef4` (`a46c98f`),
   `e814efe`, `f36adee`. Thirteen markers, the row's count.
3. **P5.** No envelope written; nothing under `evals/` in the diff.
4. **Frozen and owned paths.** `src/baseline/` unchanged since `m00`.
   Nothing under `evals/`, `thresholds.yaml`, `rules/`, `data/`,
   `agents/`, `.github/workflows/` or `infra/`.

## Dispositions

| # | Finding | Status |
|---|---|---|
| BLOCK 1 | A Security path touched and no ruling in the tree | Lifted by this commit: `rulings/pr1.md`, this file and `rulings/pr1-security.md`, each a draft until its seat rules |
| F1 | S0's first test read a signature, not a refusal | Repaired (`4240d9e`): it calls `app_token()` with no repository against a stub and expects a refusal and no token asked for. Today it asks for one with scope `{}`. The permission set is not tested: its shape waits for Security's ruling (R2) |
| F2 | S1 could not fire F7.1's workflow arm | Repaired (`4240d9e`): the platform side carries a workflow and an `agent.py`; the dead assertion is gone and `PLATFORM_OWNED` is what the test reads (N3) |
| F3 | Four fixture tests had a refusing arm only | Repaired (`4240d9e`): a held case for S2, S3, S4 and S5; S2 also without its bundle and with an invocation refused for access (legal-compliance 7, security-reviewer 15) |
| F4 | `build.panel_verdict_mismatch` as a reader of `evals/history/` | Carried to PR 2: the reader goes through `src/verdict/replay_history.py`, and PR 2's ruling says so. The seed test opens two envelopes itself, as `tests/test_gate.py` does |
| F5, F6 | The video's confirmation; `legal-compliance`'s run | Product's (`rulings/pr1.md`; `feasibility.md` §8) |
| N1 | `make plants`' state line is a proxy for four seeds | Stands; `SEEDS_M07`'s comment says so, and the strict markers say whether a seed is read |
| N2, N4 | S3's falsifiers; the explainer's "keeps answering" | Repaired (`8337ad8`, `4240d9e` for the seed list) |
| N5 | The run-file tests pass on a file a human filled | Stands, as at M05 and M06: they write no check; the observer and `build` read the attempts |
| N6 | Nothing was run by the review | The caller's runs above |
| Re-read `69f8383` A | A merged S2 with state "unknown" reads as unread | M07 PR 2: `merged` read before the unread return, with a test |
| Re-read `69f8383` B | "Refused first" counts any failure from the App | M07 PR 2: the App's reasons are read; S0 needs "the seats and the goldens and nothing else" |
| Re-read `52ebd57` | On a 412 the registry row is written against a record the run did not write; untested | M07 PR 2 (Security's path, `deploy.yml`) |
| Re-read `9be344c` | The quickstart's stale line | Repaired (`8337ad8`, Product) |
| Re-read `b19db9a` | The test proved the reader on an administrator's view | M06's RED (`open.md` row 2); S0's fixtures say they are the shape of the reads, not the reads |

Also repaired in `4240d9e`, from `security-reviewer` 19: S0's uncovered
grants now include a level raised and a selection widened with no new
name, and a tag policy named `main`.

**What PR 2 inherits from the seed tests**: the names in `feasibility.md`
§4. If Security rules more than one App, `grant_errors`' shape and S0's
fixtures change in PR 2's first commit, before the reader, and PR 2 says
so.

## What a reader can run

```
uv run pytest tests/test_m07_seeds.py -q              # 13 xfailed
uv run pytest tests/test_m07_seeds.py -q --runxfail   # 13 failed, each on its planted reason
git show e814efe --stat                               # a seed: fixture, tests, README row, SEEDS_M07 line
git grep -n "grant_errors\|panel_verdict_mismatch\|surface_plants" -- src scripts   # nothing: no reader
uv run python -m src.verdict.gate --plants | tail -13
```
