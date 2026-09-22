"""`validate`: a golden id on `main` never disappears; it is retired (R11; SPEC/02 §6, seed S5).

`check(tree, base)`: every `evals/goldens/v*/g-NNN.yaml` in the base is in
the tree, or the base's copy already has `retired:` set. A deleted or
renamed id is refused, naming the id and the word that would have been
right. `g-099` is burned (`tests/fixtures/README.md`): no golden has that
id, on any branch.

In `make validate` the base is `origin/main` (the branch the PR targets,
`GITHUB_BASE_REF`, when CI sets it) and the tree is the repository; a base
that cannot be resolved is an error, since the check would then compare to
nothing. In `tests/test_m02_seeds.py` both are directories.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

from src.gates import Tree

GOLDEN = re.compile(r"^evals/goldens/v[0-9]+/(g-[0-9]{3})\.yaml$")
BURNED = {"g-099"}


def _goldens(tree: Tree) -> dict[str, tuple[str, dict[str, Any]]]:
    """id -> (path, document) for every golden file the tree holds."""
    out = {}
    for path in sorted(tree.files()):
        if not (match := GOLDEN.match(path)):
            continue
        try:
            doc = yaml.safe_load(tree.text(path) or "")
        except yaml.YAMLError:
            doc = None
        out[match[1]] = (path, doc if isinstance(doc, dict) else {})
    return out


def compare(tree: Tree, base: Tree) -> list[str]:
    before, after = _goldens(base), _goldens(tree)
    errors = []
    for golden_id, (path, doc) in sorted(before.items()):
        if golden_id in after:
            continue
        if doc.get("retired") is None:
            errors.append(
                f"{path}: {golden_id} is on {base.name} and not in this tree, and its retired is null: "
                "an id is retired (retired: MNN), never renamed or deleted (R11)"
            )
    for golden_id, (path, doc) in sorted(after.items()):
        if golden_id in BURNED or doc.get("id") in BURNED:
            errors.append(f"{path}: {golden_id} is a burned id (tests/fixtures/README.md); no golden ever gets it")
    return errors


def default_base(root: Path) -> str | None:
    """`origin/<GITHUB_BASE_REF>` on a pull request run, else `origin/main`; None if git cannot resolve it."""
    ref = f"origin/{os.environ.get('GITHUB_BASE_REF') or 'main'}"
    done = subprocess.run(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], cwd=root, capture_output=True, check=False)
    return ref if done.returncode == 0 else None


def check(tree: Path, base: str | Path | None = None) -> list[str]:
    if base is None:
        base = default_base(tree)
        if base is None:
            return ["evals/goldens/: no origin/main to compare the ids against (fetch it)"]
    return compare(Tree(tree), Tree(base, repo=Path(tree)))
