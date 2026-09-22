"""The plant rule (SPEC/00 §5; ADR-0001 amendment 1, item 6), and M01's seeded cases.

A plant is a plant only when its enforcing control exists in the repo.
Until then it is a golden that has never passed.
"""

from __future__ import annotations

from pathlib import Path

# Golden kind -> the path whose existence is the enforcing control.
# Empty at M00: no guardrail exists, so plants_expected = 0 (ADR-0001
# amendment 1, item 6). M03 adds the guardrail and the red-team suite, and
# their rows here. A plant is counted on `agent` results only (ADR-0004).
CONTROLS: dict[str, str] = {}

# Claim 1's seeded cases (SPEC/01 §5): seed -> (falsifier, what is planted,
# the reader that must refuse it). They are not plants and never enter
# plants_expected; `make plants` lists them so a reader can see which have
# a reader in the tree. Nothing gates on this table.
SEEDS: dict[str, tuple[str, str, str]] = {
    "S1": ("F1.1", "tests/fixtures/bundles/unsigned/", "src/bundle/verify.py"),
    "S2": ("F1.1", "tests/fixtures/bundles/altered/", "src/bundle/verify.py"),
    "S3": ("F1.1", "tests/fixtures/construct/extra_egress*.py", "infra/construct/"),
    "S4": ("F1.1", "milestones/M01/runs/f1_1_laptop.yaml", "infra/bootstrap/"),
    "S5": ("F1.2", "tests/fixtures/construct/role_without_boundary.py", "infra/construct/"),
    "S6": ("F1.3", "milestones/M01/runs/f1_3_key_policy.yaml", "infra/bootstrap/"),
    "S7": ("F1.4", "tests/fixtures/refagent_raw_uncited.json", "src/verdict/build.py"),
    "S8": ("F1.1", "tests/fixtures/construct/outside_construct.py", "infra/construct/"),
}


# Claim 2's seeded cases (SPEC/02 section 5), the same shape. Each is a diff
# to a seat-owned path under tests/fixtures/m02/, or an attempt against the
# main ruleset recorded under milestones/M02/runs/. The readers land at M02
# PR 2; listing them here reads nothing and gates nothing.
SEEDS_M02: dict[str, tuple[str, str, str]] = {
    "S1": ("F2.1", "tests/fixtures/m02/s1-one-key.patch, s1-two-files-one-seat.patch", "src/gates/two_key.py"),
    "S2": ("F2.1", "tests/fixtures/m02/s2-golden-greened.patch", "src/gates/ruling_cited.py"),
    "S3": ("F2.1", "tests/fixtures/m02/s3-one-sided-edge.patch", "src/validate/edges.py"),
    "S4": ("F2.1, F2.2", "milestones/M02/runs/f2_1_bypass.yaml", "scripts/observe_pr.py"),
    "S5": ("F2.1", "tests/fixtures/m02/s5-golden-renamed.patch", "src/validate/golden_ids.py"),
}

# Every milestone's seeded cases, in order, with the SPEC section that lists them.
SEEDS_BY_MILESTONE: list[tuple[str, dict[str, tuple[str, str, str]]]] = [
    ("SPEC/01 section 5", SEEDS),
    ("SPEC/02 section 5", SEEDS_M02),
]


def plant_ids(kinds: dict[str, str], root: Path) -> list[str]:
    # The rule, one line.
    return sorted(g for g, kind in kinds.items() if kind in CONTROLS and (root / CONTROLS[kind]).exists())
