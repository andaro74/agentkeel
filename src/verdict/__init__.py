"""The verdict chain (P5).

Runners write raw observations. `build` is the only writer of envelopes.
`gate` is the only reader that rules on one; `replay_history` reads past
envelopes for both, keyed on golden id. A test asserts they can disagree.

What build and the gate share: the schema, the hash, `plants.plant_ids` and
`replay_history`. So they agree on the plant rule and on "ever passed" by
construction; a bug in either is a bug in both. They can disagree on what
they are given (the history, the tree) and on everything the gate works out
again from `goldens`. Only build reads `expected`.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = Path(__file__).parent / "schema.json"


def schema_errors(envelope: Any) -> list[str]:
    """Every way `envelope` differs from verdict.schema.json. Empty means valid."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return sorted(
        f"{'/'.join(str(p) for p in error.absolute_path) or '<envelope>'}: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(envelope)
    )


def canonical_sha256(document: Any) -> str:
    """sha256 of the document's content, not its bytes: line endings do not change it."""
    canonical = json.dumps(
        document, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_golden_kinds(goldens_dir: Path) -> dict[str, str]:
    """Golden id -> kind. Reads nothing else from a golden."""
    import yaml

    kinds = {}
    for path in sorted(goldens_dir.glob("g-*.yaml")):
        golden = yaml.safe_load(path.read_text(encoding="utf-8"))
        kinds[golden["id"]] = golden["kind"]
    return kinds
