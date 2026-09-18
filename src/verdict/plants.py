"""The plant rule (SPEC/00 §5).

A plant is a plant only when its enforcing control exists in the repo.
Until then it is a golden that has never passed.
"""

from __future__ import annotations

from pathlib import Path

# Golden kind -> the path whose existence is the enforcing control.
# Empty at M00: no guardrail exists, so plants_expected = 0. M03 adds the
# guardrail and the red-team suite, and their rows here.
CONTROLS: dict[str, str] = {}


def plant_ids(kinds: dict[str, str], root: Path) -> list[str]:
    # The rule, one line.
    return sorted(g for g, kind in kinds.items() if kind in CONTROLS and (root / CONTROLS[kind]).exists())
