"""The plant controls name live goldens of their own kind (M03 PR 2; rule-owner on 06ed59b, F1 and F2).

The plant rule (`src/verdict/plants.py`) counts a golden only when its
kind's control names it by id, and drops without a word an id that names
no golden, a golden of another kind, or a retired one. That would lower
`plants_expected` and nobody would see it. So each control in `CONTROLS`
must be there, must list its plants, and every id it lists must be a live
golden of that control's kind.

`redteam.yaml` also maps each attack to the guardrail rule that must block
it. Its `blocks` keys must be its `plants`, so that an attack cannot be a
plant with no named block, or be named with no plant; that each named
rule is a topic of `guardrail.yaml` is the bootstrap stack's check at
synth (`guardrail_spec`).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from src.verdict import load_golden_kinds, plants


def check(root: Path) -> list[str]:
    errors: list[str] = []
    kinds = load_golden_kinds(root / "evals" / "goldens" / "v1")
    for kind, path in sorted(plants.CONTROLS.items()):
        file = root / path
        if not file.is_file():
            errors.append(f"{path}: CONTROLS names it for {kind!r} and it is not in the tree")
            continue
        control = yaml.safe_load(file.read_text(encoding="utf-8"))
        ids = control.get("plants") if isinstance(control, dict) else None
        if not isinstance(ids, list) or not ids:
            errors.append(f"{path}: a control lists its plants by id under `plants`")
            continue
        for golden_id in ids:
            if golden_id not in kinds:
                errors.append(f"{path}: plants names {golden_id}, which is not a live golden")
            elif kinds[golden_id] != kind:
                errors.append(f"{path}: plants names {golden_id}, a {kinds[golden_id]} golden, in the {kind} control")
        if len(set(ids)) != len(ids):
            errors.append(f"{path}: plants names an id twice")
        if "blocks" in control and set(control["blocks"]) != set(ids):
            errors.append(f"{path}: blocks names {sorted(control['blocks'])}, plants {sorted(ids)}; they must be one set")
    return errors
