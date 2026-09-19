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


def plant_ids(kinds: dict[str, str], root: Path) -> list[str]:
    # The rule, one line.
    return sorted(g for g, kind in kinds.items() if kind in CONTROLS and (root / CONTROLS[kind]).exists())
