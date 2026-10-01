"""The platform check: `validate`'s checks over an agent repository's head (SPEC/06 §6, R2, R6).

    python -m src.validate.agent evaluate --agent DIR --repository ORG/NAME --head SHA --out RESULT.json
    python -m src.validate.agent ruleset --live RULESETS.json --out RESULT.json [--result RESULT.json]

`evaluate` runs in `.github/workflows/platform-check.yml`'s first job, which
holds no secret. DIR is the agent repository checked out **as data** at the
pull request's head; nothing in it is imported or run, only parsed, and a
symbolic link anywhere in it is refused before anything is read. The agent
folder is placed at `agents/<name>/` in a scratch tree beside `agentkeel`'s
own manifests and `thresholds.yaml`, as the seed tests place their fixtures,
and these run over it:

- the agent's name: lower-case letters, digits and hyphens, not `refagent`
  or `ratings-helper` (whose exemptions are agentkeel's), not a name another
  agent in `agentkeel` holds. A name the registry holds for another
  repository is refused at deploy (SPEC/06 §6, item 9);
- the guardrail: at M06 every agent from the template pins the platform's,
  refagent's, by id and version (SPEC/06 section 6, item 6), and a null pin
  on either side is refused, so one key on refagent's pin cannot relax every
  agent at once (rule-owner on M06 PR 2);
- the files `infra/construct/agent.Dockerfile` copies are there, so a merged
  repository cannot stop the deploy of every other agent
  (security-reviewer F3 on M06 PR 2);
- manifest schema; edges two-sided, no cycle, ceilings within bounds;
  `deprecated_after`;
- seats assigned, each a login that administers the repository to **this** repository (S1a's
  reader, `seats.py`, with `AGENTKEEL_SEAT_REPOSITORY` set to it);
- an agent's goldens (S1b's reader, `agent_goldens.py`).

`ruleset` runs in the second job, which holds the App's key: the agent
repository's live rulesets (read with the App's token) must hold one equal
to `infra/ruleset/agent.json` in the fields that say what it does, with
`bypass_actors: []`. A repository whose ruleset differs gets a failed check,
since without it the check binds nothing.

Exit 0 when everything passed, 1 when anything refused; the result file is
written either way, and the posting job reads it, not the exit code alone.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

from src.validate import agent_goldens, edges, lifecycle, ruleset, seats
from src.validate.checks import check_manifests

ROOT = Path(__file__).resolve().parents[2]
EXPORT = "infra/ruleset/agent.json"
NAME = re.compile(r"^[a-z][a-z0-9-]{2,30}$")
PLATFORM_AGENT = "refagent"  # whose guardrail an agent from the template pins at M06
NOT_COPIED = {".git", ".github"}


def links(agent: Path) -> list[str]:
    """Every symbolic link under `agent`, relative: refused, since a link can point a reader anywhere."""
    found = []
    for path in agent.rglob("*"):
        if any(part in NOT_COPIED for part in path.relative_to(agent).parts):
            continue
        if path.is_symlink():
            found.append(path.relative_to(agent).as_posix())
    return sorted(found)


def scratch_tree(agent: Path, name: str, root: Path = ROOT) -> Path:
    """agentkeel's manifests and thresholds.yaml, with the agent folder at agents/<name>/."""
    tree = Path(tempfile.mkdtemp(prefix="agentkeel-agent-"))
    shutil.copy2(root / "thresholds.yaml", tree / "thresholds.yaml")
    for manifest in sorted((root / "agents").glob("*/manifest.yaml")):
        target = tree / "agents" / manifest.parent.name / "manifest.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(manifest, target)
    shutil.copytree(agent, tree / "agents" / name, ignore=shutil.ignore_patterns(*NOT_COPIED), symlinks=True)
    return tree


def name_errors(name: Any, root: Path = ROOT) -> list[str]:
    if not isinstance(name, str) or not NAME.match(name):
        return [f"manifest.yaml: name {name!r} is not lower-case letters, digits and hyphens, 3 to 31 long"]
    if name in agent_goldens.EXEMPT:
        return [f"manifest.yaml: name {name} is agentkeel's own agent; an agent repository may not take it"]
    if (root / "agents" / name).is_dir():
        return [f"manifest.yaml: name {name} is held by agents/{name}/ in agentkeel"]
    return []


# What infra/construct/agent.Dockerfile copies into the image; a folder without them cannot be built.
IMAGE_FILES = ("__init__.py", "agent.py", "server.py", "prompt.txt", "manifest.yaml")


def image_file_errors(agent: Path) -> list[str]:
    missing = [name for name in IMAGE_FILES if not (agent / name).is_file()]
    if not (agent / "tools").is_dir() or not any((agent / "tools").glob("*.json")):
        missing.append("tools/*.json")
    return [f"{name}: missing; the platform's image copies it (infra/construct/agent.Dockerfile)" for name in missing]


def guardrail_errors(doc: dict[str, Any], root: Path = ROOT) -> list[str]:
    platform = yaml.safe_load((root / "agents" / PLATFORM_AGENT / "manifest.yaml").read_text(encoding="utf-8"))
    if not platform.get("guardrail") or not doc.get("guardrail"):
        return ["manifest.yaml: no guardrail pinned; an agent from the template pins the platform's "
                "(SPEC/06 section 6, item 6), and the platform's must be a pin"]  # fmt: skip
    if doc.get("guardrail") != platform.get("guardrail"):
        return [f"manifest.yaml: guardrail {doc.get('guardrail')!r} is not the platform's {platform.get('guardrail')!r} "
                "(SPEC/06 section 6, item 6: one guardrail for every agent at M06)"]  # fmt: skip
    return []


def evaluate(agent: Path, repository: str, root: Path = ROOT, *, lookup=None) -> dict[str, list[str]]:
    """Each check's errors over the agent folder, by check name; every list empty means passed."""
    if bad := links(agent):
        return {"no symbolic links": [f"{p}: a symbolic link; refused before anything is read" for p in bad]}
    path = agent / "manifest.yaml"
    if not path.is_file():
        return {"the agent's name": ["manifest.yaml: missing at the repository's root"]}
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return {"the agent's name": [f"manifest.yaml: not YAML ({exc.__class__.__name__})"]}
    if not isinstance(doc, dict):
        return {"the agent's name": ["manifest.yaml: not a mapping"]}
    errors: dict[str, list[str]] = {"the agent's name": name_errors(doc.get("name"), root)}
    if errors["the agent's name"]:
        return errors
    name = doc["name"]
    errors["the platform's guardrail"] = guardrail_errors(doc, root)
    errors["the files the platform's image copies"] = image_file_errors(agent)
    tree = scratch_tree(agent, name, root)
    previous = os.environ.get("AGENTKEEL_SEAT_REPOSITORY")
    os.environ["AGENTKEEL_SEAT_REPOSITORY"] = repository
    seats.login_holds_seat.cache_clear()
    try:
        mine = f"agents/{name}/"
        errors["manifest schema"] = [e for e in check_manifests(tree) if e.startswith(mine)]
        errors["edges two-sided, no cycle, ceilings within bounds"] = edges.check(tree)
        errors["deprecated_after more than 30 days away, or null"] = [e for e in lifecycle.check(tree) if e.startswith(mine)]
        seat_errors = seats.check(tree, lookup=lookup) if lookup else seats.check(tree)
        errors["seats assigned, each a login that administers the repository"] = [e for e in seat_errors if e.startswith(mine)]
        errors["an agent's goldens: one ordinary and one trap at least, citing its own data"] = [
            e for e in agent_goldens.check(tree) if e.startswith(mine)]
    finally:
        seats.login_holds_seat.cache_clear()
        if previous is None:
            os.environ.pop("AGENTKEEL_SEAT_REPOSITORY", None)
        else:
            os.environ["AGENTKEEL_SEAT_REPOSITORY"] = previous
        shutil.rmtree(tree, ignore_errors=True)
    return errors


def ruleset_errors(live: list[dict[str, Any]], root: Path = ROOT) -> list[str]:
    """One of the repository's live rulesets equals the export in what it does, with no bypass."""
    export = json.loads((root / EXPORT).read_text(encoding="utf-8"))
    if not live:
        return [f"{EXPORT}: the repository has no ruleset; the platform check binds nothing without it"]
    best: list[str] | None = None
    for one in live:
        if one.get("bypass_actors") is None:
            found = [f"{EXPORT}: ruleset {one.get('id')}'s bypass_actors is not shown to the App's token"]
        else:
            found = [f"{EXPORT}: {key} differs from live ruleset {one.get('id')}" for key in ruleset.COMPARED
                     if export.get(key) != one.get(key)]  # fmt: skip
        if not found:
            return []
        best = found if best is None or len(found) < len(best) else best
    return best or []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="what", required=True)
    one = sub.add_parser("evaluate")
    one.add_argument("--agent", required=True, type=Path)
    one.add_argument("--repository", required=True)
    one.add_argument("--head", required=True)
    one.add_argument("--out", required=True, type=Path)
    # The evaluating job holds no token that may ask an organisation repository about its collaborators:
    # a seat that names a login passes here, and the posting job checks each login's access with the App's.
    one.add_argument("--defer-seat-access", action="store_true")
    two = sub.add_parser("ruleset")
    two.add_argument("--live", required=True, type=Path)
    two.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    if args.what == "evaluate":
        logins: list[str] = []

        def deferred(login: str) -> tuple[bool, str]:
            logins.append(login)
            return True, "deferred to the posting job"

        errors = evaluate(args.agent, args.repository, lookup=deferred if args.defer_seat_access else None)
        result = {"repository": args.repository, "head": args.head, "errors": errors,
                  "seat_logins": sorted(set(logins)), "passed": not any(errors.values())}  # fmt: skip
    else:
        live = json.loads(args.live.read_text(encoding="utf-8"))
        problems = ruleset_errors(live if isinstance(live, list) else [])
        result = {"errors": {"the repository's ruleset is the export": problems}, "passed": not problems}
    for name, errs in result["errors"].items():
        print(f"{'FAIL' if errs else 'ok  '} {name}")
        for error in errs:
            print(f"     {error}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
