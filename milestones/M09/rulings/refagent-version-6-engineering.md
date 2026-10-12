---
# Engineering's key over the one Engineering path pull request #51 touches:
# one test in tests/test_m07_readers.py, whose premise the Rule Owner's pin
# move made false. The pin itself is refagent-version-6.md (Rule Owner).
ruling: refagent-version-6-engineering
seat: Engineering
authorises:
  - tests/test_m07_readers.py
evidence:
  - SPEC/00-overview.md#8-M09
  - milestones/M09/rulings/refagent-version-6.md
  - milestones/M07/rulings/pr2.md
pr: 51
---

# Ruling: the M07 upgrade test's premise, after refagent pins version 6 (Engineering)

DRAFT until it reads "Ruled by". Drafted by the session 2026-10-12.

## What failed

Pull request #51's `checks` job, run 38193843689: one test,
`tests/test_m07_readers.py::test_the_guardrail_is_held_to_mains_pin_not_to_the_templates`,
on its first assertion:

    assert {'id': '1088aw3ujhyd', 'version': '6'} != {'id': '1088aw3ujhyd', 'version': '6'}

The `evals` job failed on "Fail if pytest failed" alone. 164 other tests in
the same files passed; nothing else in the run failed.

## Why

M07's seed S1 (`tests/fixtures/m07/s1-platform-upgrade/`,
`tests/fixtures/README.md` row S1) invented a platform at guardrail version
6 as "a pin `main` does not have", beside a fixture agent at version 5, so
the upgrade reader could be shown to hold a template's pin against `main`'s
and refuse it. The test took `main`'s pin from the live
`agents/refagent/manifest.yaml`. From #51 `main` pins version 6 itself, so
the fixture's invented pin is now the real one and the test's premise, not
the reader, is false. `scripts/platform_upgrade.content_errors` is
unchanged and still refuses a template pin that differs from `main`'s.

## What changes

The test keeps the live manifest's shape and takes the pin from the
fixture agent's own manifest (`agent/manifest.yaml`, version 5), which is
the pin `main` held when the seed was planted. Its assertions are
unchanged. No fixture file changes: `tests/fixtures/README.md` row S1 still
reads as written, and "invented for the fixture" now describes a version
that has since become real, which this file records.

## What a reader can run

```
git diff f5ecb25...HEAD -- tests/                       # one test's premise, nothing else under tests/
uv run pytest tests/test_m07_readers.py -q               # passes; the first assertion holds on version 5 vs 6
uv run pytest tests/test_m07_readers.py -q -k held_to_mains_pin
git diff f5ecb25...HEAD -- scripts/platform_upgrade.py   # empty: the reader is unchanged
```

A change to `scripts/platform_upgrade.py`, to a file under
`tests/fixtures/m07/`, or to any assertion of the test, in this pull
request, makes this ruling wrong.
