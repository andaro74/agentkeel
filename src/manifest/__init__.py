"""Agent manifests: the schema, and reading one (SPEC/00 §6).

`validate` checks every `agents/*/manifest.yaml` against `schema.json`
(`additionalProperties: false`). The construct reads the same file for the
model, the endpoint allowlist and the seats; nothing else parses it.

A manifest has several owners, one field at a time (ADR-0003 amendment 1).
This module rules on none of them: it loads and validates, and the seats own
what the fields say.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = Path(__file__).parent / "schema.json"
AGENTS = ROOT / "agents"
ENDPOINTS = ("bedrock-runtime", "dynamodb", "kms", "logs", "s3")


def schema_errors(manifest: Any) -> list[str]:
    """Every way `manifest` differs from manifest.schema.json. Empty means valid."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return sorted(
        f"{'/'.join(str(p) for p in error.absolute_path) or '<manifest>'}: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(manifest)
    )


def load(path: Path) -> dict[str, Any]:
    """Read one manifest. Raises ValueError if it does not validate."""
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    if errors := schema_errors(manifest):
        raise ValueError(f"{path}: does not validate: " + "; ".join(errors))
    return manifest


def paths(root: Path = ROOT) -> list[Path]:
    return sorted((root / "agents").glob("*/manifest.yaml"))
