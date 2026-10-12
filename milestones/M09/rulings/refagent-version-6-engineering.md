---
# Engineering's key over the two Engineering paths pull request #51 touches:
# one test in tests/test_m07_readers.py, whose premise the Rule Owner's pin
# move made false, and the M08 hostile-copy fixture's manifest, whose pin
# was the platform's and is again. The pin itself is refagent-version-6.md
# (Rule Owner).
ruling: refagent-version-6-engineering
seat: Engineering
authorises:
  - tests/test_m07_readers.py
  - tests/fixtures/m08/s1-hostile-copy/manifest.yaml
evidence:
  - SPEC/00-overview.md#8-M09
  - milestones/M09/rulings/refagent-version-6.md
  - milestones/M07/rulings/pr2.md
pr: 51
---

# Ruling: two fixtures' premises after refagent pins version 6 (Engineering)

DRAFT until it reads "Ruled by". Drafted by the session 2026-10-12; the
first draft (the M07 test alone) was ruled at `a288e84` and is widened here
by the second failure below, so it is ruled again.

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

## The second failure, on the ruled head

Run 38201479296 on `a288e84`, one test:
`tests/test_m08_seeds.py::test_s1_the_platform_check_admits_the_hostile_copy`,
a guard with no marker. M08's seed S1 (`tests/fixtures/m08/s1-hostile-copy/`,
`tests/fixtures/README.md` row S1) is refagent's agent with six attempts in
its code; its manifest pinned the platform's guardrail as it was at M08,
version 5. The platform check requires an agent without `rules/` to pin
the platform's guardrail exactly, id and version
(`src/validate/agent.py`, "the platform's guardrail"), and from #51 that is
version 6, so the hostile copy was refused on its pin:

    manifest.yaml: guardrail {'id': '1088aw3ujhyd', 'version': '5'} is not the platform's {'id': '1088aw3ujhyd', 'version': '6'}

The seed's false state is the six attempts in `agent.py`, never the pin;
the pin has to be the platform's for the guard to read what it reads
(SPEC/08 §1: the check reads the manifest and never the code). Changed:
`version: "5"` to `version: "6"` in that manifest, one line, and nothing
else under `tests/fixtures/m08/`. The README row names no version and
stands. The M07 fixture agent's manifest also pins version 5
(`m07/s1-platform-upgrade/agent/manifest.yaml`) and stays: it is an agent
one platform version behind by design, and no test runs the platform check
over it.

The same reading applies outside the tree: `agentkeel-studio/drill-agent`,
retired at M08's close, pins version 5 and would be refused by the platform
check if it were ever checked again. Nothing deploys it. Recorded, not
changed.

## What a reader can run

```
git diff f5ecb25...HEAD -- tests/                       # one test's premise and one fixture pin, nothing else under tests/
uv run pytest tests/test_m08_seeds.py -q                 # the hostile copy admitted again
uv run pytest tests/test_m07_readers.py -q               # passes; the first assertion holds on version 5 vs 6
uv run pytest tests/test_m07_readers.py -q -k held_to_mains_pin
git diff f5ecb25...HEAD -- scripts/platform_upgrade.py   # empty: the reader is unchanged
```

A change to `scripts/platform_upgrade.py`, to a file under
`tests/fixtures/m07/`, to anything under `tests/fixtures/m08/` but that one
line, or to any assertion of either test, in this pull request, makes this
ruling wrong.
