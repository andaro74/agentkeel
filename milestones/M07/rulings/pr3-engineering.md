---
# M07 PR 3 (to open as #40), Engineering's key and the cold review, one
# file. Drafted from engineering-cold-reviewer's read of the diff
# 3bfd074...936eb17 and row 7 only. The repairs after it were not read
# cold again. Product's file is rulings/pr3.md; Security's is
# rulings/pr3-security.md; the Threshold Owner's is
# rulings/pr3-threshold-owner.md.
ruling: pr3-engineering
seat: Engineering
authorises:
  - src/**
  - scripts/**
  - tests/**
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - milestones/README.md
  - milestones/M07/README.md
  - milestones/M07/runs/pr3_expected.md
  - https://github.com/andaro74/agentkeel/actions/runs/37047341001
  - evals/history/af8835fad82709e2385bf4eff97a175e069bf855.json
pr: 40
---

# Ruling: M07 PR 3, Engineering, with the cold review

Ruled by andaro74 as Engineering, 2026-10-02, as written.

## What this authorises

- **`src/verdict/upgrade.py`**: `commit_by_the_app` (who made a commit,
  from GitHub's record of it); `ci_envelope_commit` (SPEC/07 §2 as
  amended); `relaxation` with every time comparison in it, and the
  restore read from the ruleset.
- **`src/gates/two_key.py`**: `date_relaxation`, ADR-0009 amendment 1's
  entry 6, after its seeded case.
- **`scripts/observe_upgrade.py`**: the relaxation written as records;
  tokens minted first and revoked after, the key not kept; no tree
  packed as the App; `download`.
- **`scripts/platform_check.py`**: the grant read from
  `infra/platform_grant.yaml`. Engineering's under the base ref's
  CODEOWNERS, which is what the gates read; Security's from the next
  pull request (ADR-0012).
- **`scripts/platform_upgrade.py`**: `content_errors` and the template
  read by the keyed job (13l). **`scripts/retire_agent.py`**: `same`
  (13i). **`scripts/model_watch.py`**: a docstring.
- **`tests/`**: the tests of each, the seeded case
  `tests/fixtures/m07/two-key-deprecated-after/`, and the fixtures given
  GitHub's record of an App's commit.

Nothing under `src/baseline/`, `evals/history/`, `evals/goldens/`,
`rules/`, `data/`, `agents/` or `thresholds.yaml`.

## The cold review

`engineering-cold-reviewer` read `git diff 3bfd074...936eb17` (38 files)
and row 7, ran seven M07 test files (357 passed, 4 expected failures),
`tests/test_gates.py` (54 passed) and the two key-policy tests. BLOCK 1,
FINDING 3, NOTE 7. Its report is in the pull request's body, verbatim.

It found the shape held: the fix, the repairs PR 2's reviews left open,
one `observed` entry, the row's amendment; the one new seeded case
planted before its reader; nothing under `evals/history/`; the observer
writing records and build comparing them.

### BLOCK

| # | Block | Status |
|---|---|---|
| B1 | The two rulings the diff rests on, `pr3.md` and `pr3-security.md`, were not in the tree; the Security edits cited items of `pr2-security.md` that its own heading calls "not ruled"; at that head `load_grant()` refused, so merged like that every keyed job on `main` would stop | **Written, as drafts. The seats'.** All four files are in the tree now. `pr3-security.md` rules 13h, 13i, 13j and 13l by item and authorises every Security path in the diff, the sign-agent fix among them. It clears when each DRAFT line is changed by its seat; `cold-review-ruling` holds the merge until then. A test now holds that the ruling the grant names is in the tree and is Security's |

### FINDING

| # | Finding | Status |
|---|---|---|
| F1 | "After the restore" could be the relaxing call itself: the App's accepted call sets `updated_at` after the run began | **Repaired** (`44a86eb`): a restore is a change after the platform check failed the new head for the ruleset. No detection, no restore. Two cases added |
| F2 | The by-hand file deployed B2 and B3 from the unmerged branch, and the diff deleted its guard sentence | **Security's.** The sentence is back; the choice is put to the seat in `pr3-security.md` item 4 |
| F3 | The row's amendment moves the measurement into the close; a fault a repair shows at PR 4 has no pull request left | **Product's; accepted and said** in `pr3.md`, the M07 README and SPEC/07 §12 |

### NOTE

- **N1:** repaired (`b5b3b5f`): `two-key` reads an unquoted timestamp by
  its day.
- **N2:** repaired (`ce2bf49`): one test more holds that `deploy-agent`
  reads no signed file from outside the staged folder. The fix has not
  run on `main`.
- **N3:** repaired (`4fd46f8`): "text", not "byte for byte".
- **N4:** repaired (`127d7fc`): the observer's docstring and
  `observe.yml` say what is still read from an agent repository beside
  the App's tokens.
- **N5, kept because it bears on this file's evidence:** the head that
  merges is not the head that was read. After `936eb17`: the review
  repairs, the four ruling files, `runs/pr3_expected.md`, CI's envelope
  commit, and, if the seat gives them before the merge, the two App ids
  in a commit of their own. The envelope this file cites is of the head
  CI measured, and is added to `evidence:` when CI has written it.
- **N7:** repaired: the developer's page says no retirement has run.
- N6 needs nothing.

## The other seats' reports that named this seat's paths

Each is in the pull request's body. What was done is in
`pr3-security.md` section 6 and `pr3-threshold-owner.md` section 5. In
`scripts/` and `src/`: the observer's tokens revoked and held to
GitHub's API host (security-reviewer 14, 15); a template file that is
not UTF-8 refused, not raised (10); `two-key`'s timestamp
(threshold-owner N3).

## Stands, and said

- **No commit by `agentkeel-upgrades` has been read.**
  `commit_by_the_app` takes the App's bot as author, the commit verified,
  and the bot or GitHub's signer as committer. If the App's first commit
  carries another record, S1 reads as a person's edit. That is the
  conservative reading the seat asked for, and it cannot be repaired
  after this pull request.
- **None of this pull request's repairs has run live.** Tests on
  fixtures and one seeded case hold them.
- **`ruff check` reports 99 findings across `scripts`, `src` and
  `tests`**, none in a rule this diff's files newly fail (`--select F`:
  3 before, 3 after). Not in CI. Not this pull request's.

## What a reader can run

```
uv run pytest -q                                                    # the whole suite
uv run pytest -q tests/test_m07_seeds.py                            # 9 passed, 4 xfailed
uv run pytest -q tests/test_m07_two_key_seed.py                     # 8 passed
uv run pytest -q tests/test_m07_upgrade.py -k "apps_only or envelope_commit or restore or relaxation"
uv run pytest -q tests/test_m07_observer.py -k "relaxation or mints_first or storage_host"
uv run pytest -q tests/test_m07_readers.py -k "template or proposed or grant"
uv run pytest -q tests/test_m07_platform.py -k "retired_head or deployed_commit"
uv run python -m src.gates.ruling_cited --base origin/main --pr 40
uv run python -m src.gates.two_key --base origin/main --pr 40
make validate && make ledger
```
