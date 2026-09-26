"""The plant rule (SPEC/00 §5; ADR-0001 amendment 1, item 6), and M01's seeded cases.

A plant is a plant only when its enforcing control exists in the repo.
Until then it is a golden that has never passed.

From M03 PR 2 the rule reads each control **at the envelope's commit**
(`git show`, as `gate.thresholds_at` reads the cap), and counts a golden
only when the control names it by id (SPEC/03 §5.1 and §6). A control
added today does not make plants of an envelope written before it (seed
S6), and a golden of a control's kind that the control does not name is
not a plant (`g-014`, MASKED, waits for the knowledge base at M04).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from src.verdict import text_at

# Golden kind -> the path of its enforcing control. The control is a YAML
# mapping whose `plants` lists, by id, the goldens it answers for.
# Empty from M00 to M03 PR 2: no guardrail existed, so plants_expected = 0
# (ADR-0001 amendment 1, item 6). Filled at M03 PR 2 in the commit after
# the guardrail is on the runner's and the runtime's converse (SPEC/03
# §5.1; 366104c): 7 plants, g-013 and g-015 in the guardrail's control,
# g-016 to g-020 in the red-team suite's. Read at the envelope's commit, so
# no envelope before this commit counts one. `validate` holds each id to a
# live golden of the control's kind. A plant is counted on `agent` results
# only (ADR-0004).
CONTROLS: dict[str, str] = {
    "guardrail": "agents/refagent/rules/guardrail.yaml",
    "redteam": "agents/refagent/rules/redteam.yaml",
}

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

# Claim 3's seeded cases (SPEC/03 section 5), the same shape. Listed at M03
# PR 1; the readers land at M03 PR 2. Every reader but S3's and S5's is a
# file already in the tree that changes there (the runtime match, CONTROLS,
# the fingerprint in the gate, the plant rule, history at the ancestors),
# so `make plants` says "in the tree" beside them, as it did for M01's S7:
# the strict markers, not this list, say whether a seed is read.
# S4 plants no file: row 2's envelope is the false state. Listing them reads nothing
# and gates nothing, and CONTROLS above stays empty until the guardrail is
# on the call (SPEC/03 section 5.1).
SEEDS_M03: dict[str, tuple[str, str, str]] = {
    "S1": ("F3.1", "tests/fixtures/m03/s1-table-regresses.patch", "scripts/runtime_for_tree.py"),
    "S2": ("F3.2", "tests/fixtures/m03/s2-g-016.yaml, s2-g-016-result.json", "src/verdict/plants.py"),
    "S3": ("F3.3", "tests/fixtures/m03/s3-overlap.patch", "src/validate/overlap.py"),
    "S4": ("F3.4", "evals/history/8033c2a7a0588e557df577464c190e64a435e88a.json", "src/verdict/gate.py"),
    "S5": ("F3.5", "tests/fixtures/m03/s5-unsigned-amendment.md, milestones/M03/runs/f3_5_amendment.yaml",
           "scripts/observe_ingest.py"),
    "S6": ("F3.6", "tests/fixtures/m03/s6-guardrail.yaml", "src/verdict/plants.py"),
    "S7": ("F3.6", "tests/fixtures/m03/s7-later-pass.json", "src/verdict/replay_history.py"),
}

# Every milestone's seeded cases, in order, with the SPEC section that lists them.
SEEDS_BY_MILESTONE: list[tuple[str, dict[str, tuple[str, str, str]]]] = [
    ("SPEC/01 section 5", SEEDS),
    ("SPEC/02 section 5", SEEDS_M02),
    ("SPEC/03 section 5", SEEDS_M03),
]


def named_by(kind: str, commit: str, root: Path) -> list[str] | None:
    """The ids the control for `kind` names at `commit`; None when the control is not there.

    A control that is there and names no plant list is refused, not read
    as naming none: that would be a control with no plants, and a silent
    plant nobody could see.
    """
    text, where = text_at(commit, CONTROLS[kind], root)
    if text is None:
        return None
    control = yaml.safe_load(text)
    ids = control.get("plants") if isinstance(control, dict) else None
    if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
        raise ValueError(f"{CONTROLS[kind]} at {where}: a control must list its plants by id under `plants`")
    return ids


def plant_ids(kinds: dict[str, str], root: Path, commit: str) -> list[str]:
    """The goldens that are plants at `commit`: of a kind whose control is there, and named by it."""
    named = {kind: named_by(kind, commit, root) for kind in CONTROLS}
    return sorted(g for g, kind in kinds.items() if g in (named.get(kind) or []))
