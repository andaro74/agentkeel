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

# Claim 4's seeded cases (SPEC/04 section 5), the same shape. Listed at M04
# PR 1, one seed per commit; the readers land at M04 PR 2. S1's, S3's and
# S4's readers are files already in the tree that change there (build's
# scoring, A-vs-A in build, the gate reading the bars), so `make plants`
# says "in the tree" beside them: the strict markers, not this list, say
# whether a seed is read. Listing them reads nothing and gates nothing.
# Read at M04 PR 2: every reader landed and every strict marker came off
# (cold review N1 on PR 1: "in the tree" is now also "reads its seed").
SEEDS_M04: dict[str, tuple[str, str, str]] = {
    "S1": ("F4.1", "tests/fixtures/m04/s1-breaking-pin.patch, s1-breaking-raw.json", "src/verdict/build.py"),
    "S2": ("F4.2", "tests/fixtures/m04/s2-equivalent-pin.patch", "infra/bootstrap/app.py"),
    "S3": ("F4.3", "tests/fixtures/m04/s3-a.json, s3-b.json", "src/verdict/build.py"),
    "S4": ("F4.4", "tests/fixtures/m04/s4-slow-raw.json, s4-heavy-raw.json", "src/verdict/gate.py"),
    "S5": ("none (SPEC/00 section 8 M04)", "tests/fixtures/m04/s5-deprecated-pin.patch", "src/validate/lifecycle.py"),
}

# Claim 5's seeded cases (SPEC/05 section 5), the same shape. Listed at M05
# PR 1, one seed per commit. The attempt seeds are run files the human fills
# (M01 S4's pattern); their reader is the observer that looks each up in the
# security account's audit bucket, which lands at M05 PR 2. S4's reader is a
# file already in the tree that changes there (server.py), and S5's (build),
# so `make plants` says "in the tree" beside them: the strict markers, not
# this list, say whether a seed is read. Listing them reads nothing and gates
# nothing. From M05 PR 2 every reader here is in the tree: S4's and S5's
# markers came off with their readers; the attempt seeds' come off as each
# attempt is recorded (S2, S6 during PR 2; S3, S7 at PR 3). S1's stays on: no flow record of it can exist in a
# VPC with no route out (milestones/M05/rulings/pr2.md ruling 9).
SEEDS_M05: dict[str, tuple[str, str, str]] = {
    "S1": ("F5.1, F5.2", "milestones/M05/runs/f5_1_curl.yaml", "scripts/observe_containment.py"),
    "S2": ("F5.1, F5.2", "milestones/M05/runs/f5_2_prefix.yaml", "scripts/observe_containment.py"),
    "S3": ("F5.1, F5.2", "milestones/M05/runs/f5_3_logs.yaml", "scripts/observe_containment.py"),
    "S4": ("F5.1, F5.2", "tests/fixtures/m05/s4-depth3-request.json, milestones/M05/runs/f5_4_chain.yaml", "agents/refagent/server.py"),
    "S5": ("F5.1", "tests/fixtures/m05/s5-credential-raw.json", "src/verdict/build.py"),
    "S6": ("F5.3", "milestones/M05/runs/f5_6_audit.yaml", "infra/security/"),
    "S7": ("F5.4", "milestones/M05/runs/f5_7_quarantine.yaml", "infra/audit/"),
}

# Claim 6's seeded cases (SPEC/06 section 5), the same shape. Listed at M06
# PR 1, one seed per commit. S1a, S1b and S4 are fixtures read in a worktree
# of HEAD by `validate` (S4 also by `build`); S2 and S3 are run files the
# human fills, read by the observer that lands at M06 PR 2 and made after its
# merge (SPEC/06 section 5.1). From M06 PR 2 each reader is named by its own
# file, and a seed with two readers names both, comma-separated: `make
# plants` says "in the tree" only when every one is (cold review F2 on PR 1).
# The strict markers, not this list, say whether a seed is read. Listing
# them reads nothing and gates nothing.
SEEDS_M06: dict[str, tuple[str, str, str]] = {
    "S1a": ("F6.1", "tests/fixtures/m06/s1a-unassigned-seat/", "src/validate/seats.py"),
    "S1b": ("F6.1", "tests/fixtures/m06/s1b-no-goldens/", "src/validate/agent_goldens.py"),
    "S2": ("F6.2", "milestones/M06/runs/f6_2_standin.yaml", "scripts/observe_template.py"),
    "S3": ("F6.1, F6.3", "milestones/M06/runs/f6_3_quickstart.yaml", "scripts/observe_template.py"),
    "S4": ("F6.4", "tests/fixtures/m06/s4-panel1/", "src/validate/panel.py, src/verdict/template.py"),
}

# Claim 7's seeded cases (SPEC/07 section 5), the same shape. Listed at M07
# PR 1, one seed per commit. Each of S0 to S3 is a fixture and a run file:
# the fixture is read by a function PR 2 adds (the name is fixed by
# tests/test_m07_seeds.py), the run file by the observer after PR 2 merges
# (SPEC/07 section 5.1). S4 and S5 are fixtures only. A reader that is a
# new function in a file already in the tree is named here by the new file
# PR 2 adds beside it, so `make plants` does not say "in the tree" early.
# The strict markers, not this list, say whether a seed is read. Listing
# them reads nothing and gates nothing.
SEEDS_M07: dict[str, tuple[str, str, str]] = {
    "S0": ("F7.0", "tests/fixtures/m07/s0-app-token/, milestones/M07/runs/f7_0_owner_test.yaml", "scripts/observe_upgrade.py"),
    "S1": ("F7.1", "tests/fixtures/m07/s1-platform-upgrade/, milestones/M07/runs/f7_1_platform_upgrade.yaml", "scripts/platform_upgrade.py"),
    "S2": ("F7.2", "tests/fixtures/m07/s2-retired-agent/, milestones/M07/runs/f7_2_retire.yaml", "scripts/retire_agent.py, src/verdict/upgrade.py"),
    "S3": ("F7.3", "tests/fixtures/m07/s3-rollback/, milestones/M07/runs/f7_3_rollback.yaml", "scripts/model_watch.py, src/verdict/upgrade.py"),
}

# Every milestone's seeded cases, in order, with the SPEC section that lists them.
SEEDS_BY_MILESTONE: list[tuple[str, dict[str, tuple[str, str, str]]]] = [
    ("SPEC/01 section 5", SEEDS),
    ("SPEC/02 section 5", SEEDS_M02),
    ("SPEC/03 section 5", SEEDS_M03),
    ("SPEC/04 section 5", SEEDS_M04),
    ("SPEC/05 section 5", SEEDS_M05),
    ("SPEC/06 section 5", SEEDS_M06),
    ("SPEC/07 section 5", SEEDS_M07),
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
