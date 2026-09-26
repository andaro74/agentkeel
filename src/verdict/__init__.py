"""The verdict chain (P5).

Runners write raw observations. `build` is the only writer of envelopes.
`gate` is the only reader that rules on one; `replay_history` reads past
envelopes for both, keyed on golden id. A test asserts they can disagree.

What build and the gate share: the schema, the hash, `plants.plant_ids`,
`replay_history` and `thresholds.yaml`. So they agree on the plant rule and
on "ever passed" by construction; a bug in either is a bug in both. They can
disagree on what they are given (the history, the tree) and on everything
the gate works out again from `goldens`: pass, F1.4, the lists, the cost
cap. Only build reads `expected`.

P5 separates judgment, not inputs. `replay_history` and `plants.plant_ids`
are inputs both build and gate read; neither rules on anything. P5 requires
that build's verdict and gate's verdict are computed separately from the
same inputs, which tests/test_p5_disagree.py shows. (Engineering, M01 open
items 4 and 6: no split.)
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


def where_at(commit: str, root: Path = ROOT) -> str:
    """Where a reading at `commit` is taken: the commit itself, or the working tree when git cannot resolve it."""
    import subprocess

    done = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}"], cwd=root,
                          capture_output=True, check=False)  # fmt: skip
    return f"{commit[:12]}, the envelope's own commit" if done.returncode == 0 else "the working tree"


def text_at(commit: str, path: str, root: Path = ROOT) -> tuple[str | None, str]:
    """The file at `path` as it stood at `commit`, None where it did not exist; and where it was read.

    Only a commit git cannot resolve (a test's made-up sha, a shallow clone)
    is read from the tree, and `where` says so. A file absent at a commit git
    knows is absent. Reading the tree for it is how a control added today
    makes plants of an envelope written before it (seed S6, SPEC/03 §5), and
    how a cap or a manifest deleted at an old commit was read from today's
    (M03 open.md row 11, items e and j).
    """
    import subprocess

    where = where_at(commit, root)
    if where == "the working tree":
        file = root / path
        return (file.read_text(encoding="utf-8") if file.is_file() else None), where
    shown = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=root, capture_output=True, check=False)
    return (shown.stdout.decode("utf-8") if shown.returncode == 0 else None), where


ADMITTED = "data/corpus/admitted.yaml"


def fingerprint_of(admitted: str | None) -> str | None:
    """The corpus fingerprint (SPEC/03 §2): sha256 over `key sha256` lines, sorted by key; None with no corpus.

    `admitted` is the text of `data/corpus/admitted.yaml`, or None where
    there is none. build writes this; the gate works it out again at the
    envelope's commit (seed S4's reader, M03 PR 2).
    """
    import yaml

    if admitted is None:
        return None
    entries = yaml.safe_load(admitted) or []
    lines = "".join(f"{e['key']} {e['sha256']}\n" for e in sorted(entries, key=lambda e: e["key"]))
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


def fingerprint_at(commit: str, root: Path = ROOT) -> tuple[str | None, str]:
    """The corpus fingerprint as `admitted.yaml` stood at `commit`, and where it was read."""
    text, where = text_at(commit, ADMITTED, root)
    return fingerprint_of(text), where


def load_golden_kinds(goldens_dir: Path) -> dict[str, str]:
    """Golden id -> kind, for the goldens that are not retired. Reads nothing else from a golden.

    From M02 PR 2 (Door 2, `g-012` retired): a retired golden is out of
    the run, the card, the envelope and the plant count. Its id is never
    reused (R11) and its file stays, so `replay_history` still keys on it.
    """
    import yaml

    kinds = {}
    for path in sorted(goldens_dir.glob("g-*.yaml")):
        golden = yaml.safe_load(path.read_text(encoding="utf-8"))
        if golden.get("retired") is None:
            kinds[golden["id"]] = golden["kind"]
    return kinds


def golden_kinds_at(commit: str, goldens_dir: Path, root: Path = ROOT) -> tuple[dict[str, str], str]:
    """Golden id -> kind as the goldens stood at `commit`, retired ones left out; and where it was read.

    The gate holds an envelope to the goldens of its own commit, as it
    holds it to the cap of its own commit (ruling m): a golden added or
    retired later must not re-rule an old envelope. When git cannot
    resolve the commit (a test, a shallow clone) the tree is used and the
    caller says so.
    """
    import subprocess

    import yaml

    try:
        rel = goldens_dir.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return load_golden_kinds(goldens_dir), "the working tree"
    listing = subprocess.run(["git", "ls-tree", "-r", "--name-only", commit, "--", rel], cwd=root,
                             capture_output=True, text=True, check=False)  # fmt: skip
    if listing.returncode != 0 or not listing.stdout.strip():
        return load_golden_kinds(goldens_dir), "the working tree"
    kinds = {}
    for path in sorted(listing.stdout.split()):
        if not path.rsplit("/", 1)[-1].startswith("g-") or not path.endswith(".yaml"):
            continue
        shown = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=root, capture_output=True, text=True, check=True)
        golden = yaml.safe_load(shown.stdout)
        if golden.get("retired") is None:
            kinds[golden["id"]] = golden["kind"]
    return kinds, f"{commit[:12]}, the envelope's own commit"
