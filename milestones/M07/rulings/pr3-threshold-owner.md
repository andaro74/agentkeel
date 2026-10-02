---
# M07 PR 3 (to open as #40), the Threshold Owner's key. It moves no bar
# and no pin: thresholds.yaml and both manifests are not in the diff.
# The one path named is Product's; the rule in it is this seat's
# (the ADR's own `authorises:` names the Threshold Owner).
ruling: pr3-threshold-owner
seat: Threshold Owner
authorises:
  - docs/adr/ADR-0011-one-stated-second-run-after-a-p95-miss.md
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/04-model-swap.md
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
  - milestones/M07/rulings/pr2-threshold-owner.md
  - milestones/M07/runs/pr3_expected.md
  - tests/fixtures/m07/two-key-deprecated-after/cases.json
  - https://github.com/andaro74/agentkeel/actions/runs/37047341001
  - evals/history/af8835fad82709e2385bf4eff97a175e069bf855.json
pr: 40
---

# Ruling: M07 PR 3, Threshold Owner

DRAFT for andaro74 as Threshold Owner. Not ruled until this line is replaced by one that starts with the two words the gate reads.

No relaxation is in this pull request, so no second key is owed and this
file gives none.

## 1. `two-key` reads a pin's `deprecated_after`

ADR-0009 amendment 1, entry 6 (M04 PR 1) said `two-key` reads it from
M04 PR 2. Nothing did (this seat's F1 on PR 2). At PR 3 the seeded case
was planted first (`f9dc98a`: four cases expected to fail, three
guards), then the reader (`4462d29`, `two_key.date_relaxation`), and the
marker came off. Run once at the plant without its marker: four
failures, each "two-key passed it". No CI run of `f9dc98a` exists; the
strict marker in that commit is the record.

- With `model.id` unchanged: a date moved later, set to null or removed
  needs this seat's key and one more. Null to a date, a date moved
  earlier, and a swap are not read as relaxations.
- A value that is not a date, and changed, is read as relaxed.
- **In `agentkeel` only** (F5 below).

## 2. ADR-0011, the second-run rule

As this seat ruled it on 2026-10-02 (`pr2-threshold-owner.md` item 2),
now with its ADR. The bar, `relative.p95_ratio_max`, stays 2.0.

## 3. Restated: what a revert is held to

Item 3 of `pr2-threshold-owner.md` says the revert's median is read
"over Sonnet 4.6's envelopes". That is wrong (F2 on PR 2). The revert is
a pin move ruled against the incumbent at its merge-base, which is then
Haiku 4.5: its p95 on Sonnet 4.6 is held to 2.0 times the median of
Haiku 4.5's one or two envelopes in that mode. Its verdict is not
stated. ADR-0011 decision 4 now says so. The ruled file is not edited.

## 4. The owner's test and `upgrade.deploy_max_seconds`

The bar is 3,600 s and is not moved. The merge was at 14:39:32Z; the bar
passed at 15:39:32Z with no deploy. `build` reads a miss before the fix
deploys ("no deploy and answer record") and after ("deployed N s after
the merge, over"). The attempt is not re-made (Product, `pr3.md`).

## 5. The threshold-owner review, and what was done

Read on the diff `3bfd074...936eb17`: BLOCK 0, FINDING 5, NOTE 9. The
report is in the pull request's body, verbatim.

| # | Finding | Status |
|---|---|---|
| F1 | PR 3's diff touches `infra/construct/`, so ADR-0011 gives its own run no second run | **Stated before the run** (`runs/pr3_expected.md`; ADR-0011's consequences). A p95 miss on #40 is RED |
| F2 | ADR-0011 named the bar `delta_max.p95_ratio_max`; the key is `relative.p95_ratio_max` | **Repaired** (`2c6031f`) |
| F3 | `rulings/pr3.md` cited and not in the tree | Written; Product's line clears it |
| F4 | The revert exception did not say which median; F2 and N9 of PR 2 not carried | **Repaired**: ADR-0011 decision 4, and item 3 above. N9 (the manifest's stale judge comment) is not changed here: the manifest is not in this diff. To M08's open list, by name |
| F5 | Entry 6 is read in `agentkeel` only; an agent repository's date has no key | **Open, the seat's.** Said in SPEC/07 §12 and the compliance note. Whether the platform check should read it: to M08's open list |
| N3 | A YAML timestamp raised `TypeError` in the reader | **Repaired** (`b5b3b5f`): read by its day |
| N4 | The plant's failing run is not shown by the cumulative diff | Said in item 1 |
| N6 | ADR-0011 loosens what a RED on `F4_4` means without moving the bar; `build` could count second runs | To M08's open list |
| N7 | "Both now refuse it" | Left: `two-key` refuses it with one key; `model-watch` never opens it |
| N8 | A swap may set or clear the date with one key; a stale date then needs two | F5 of PR 2, still open; to be ruled before any pin carries a date. To M08's open list |
| N1, N2, N5, N9 | Notes | Need nothing |

## What a reader can run

```
uv run pytest -q tests/test_m07_two_key_seed.py                     # 8 passed
git show f9dc98a --stat | tail -4                                   # the plant: a fixture, a test, the README; nothing under src/
git show f9dc98a:tests/test_m07_two_key_seed.py | grep -n xfail     # the strict marker
grep -rn deprecated src/gates | head -3                             # now found
git diff 3bfd074 --stat -- thresholds.yaml agents/                  # nothing
python -c "import yaml;print(yaml.safe_load(open('thresholds.yaml'))['relative']['p95_ratio_max'], yaml.safe_load(open('thresholds.yaml'))['upgrade'])"
```
