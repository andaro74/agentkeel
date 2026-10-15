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
- the guardrail: an agent without `rules/` pins the platform's, refagent's,
  by id and version (SPEC/06 section 6, item 6, M06), and a null pin on
  either side is refused, so one key on refagent's pin cannot relax every
  agent at once (rule-owner on M06 PR 2). From M09 PR 2 an agent with
  `rules/guardrail.yaml` pins a guardrail of its own, not null and not
  refagent's, which the platform builds from its rules on the baseline in
  the agent's own stack (SPEC/09 section 2, section 6; R3, R10); given the
  registry row's pin (`--held-guardrail`, the deploy job), a pin that is not
  the held one is refused;
- an agent's rules (M09 PR 2, `agent_rules.py`): `rules/guardrail.yaml`
  merged onto `rules/baseline.yaml` add-only, every refusal named; each
  guardrail or red-team plant named for a rule the merged guardrail builds
  and a live golden of its kind;
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

from src.validate import agent_goldens, agent_rules, callers, edges, lifecycle, ruleset, seats
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
        # M09 PR 3 (security-reviewer F1 on #52): at deploy-agent the candidate itself sits at root/agents/<name>/,
        # so its manifest is not a platform agent's to copy here; copytree below would find the folder made for it
        # and raise. Skipped by identity, not by name: a platform agent that holds the name is still copied, and
        # name_errors has refused the candidate before this runs.
        if manifest.parent.resolve() == agent.resolve():
            continue
        target = tree / "agents" / manifest.parent.name / "manifest.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(manifest, target)
    shutil.copytree(agent, tree / "agents" / name, ignore=shutil.ignore_patterns(*NOT_COPIED), symlinks=True)
    return tree


def name_errors(name: Any, root: Path = ROOT, agent: Path | None = None) -> list[str]:
    """The name is well formed, not agentkeel's own, and not a folder agentkeel holds under agents/.

    `agent` is the folder being checked. M09 PR 3 (deploy run 38259465892, the first deploy of an agent
    with rules/): deploy.yml's held-pin check runs this over the bundle it has placed at agents/<name>/ in
    its own checkout, so the folder it finds there is the candidate itself, not a platform agent holding
    the name. That folder is not a collision. The pull-request check reads the head from `agent-src`
    beside a clean checkout of main (platform-check.yml), and that is where a name agentkeel holds is
    refused; a caller that gives no `agent` reads as before."""
    if not isinstance(name, str) or not NAME.match(name):
        return [f"manifest.yaml: name {name!r} is not lower-case letters, digits and hyphens, 3 to 31 long"]
    if name in agent_goldens.EXEMPT:
        return [f"manifest.yaml: name {name} is agentkeel's own agent; an agent repository may not take it"]
    held = root / "agents" / name
    if held.is_dir() and not (agent is not None and held.resolve() == agent.resolve()):
        return [f"manifest.yaml: name {name} is held by agents/{name}/ in agentkeel"]
    return []


# What infra/construct/agent.Dockerfile copies into the image; a folder without them cannot be built.
IMAGE_FILES = ("__init__.py", "agent.py", "server.py", "prompt.txt", "manifest.yaml")


def image_file_errors(agent: Path) -> list[str]:
    missing = [name for name in IMAGE_FILES if not (agent / name).is_file()]
    if not (agent / "tools").is_dir() or not any((agent / "tools").glob("*.json")):
        missing.append("tools/*.json")
    return [f"{name}: missing; the platform's image copies it (infra/construct/agent.Dockerfile)" for name in missing]


def has_own_rules(agent: Path) -> bool:
    """An agent repository with `rules/guardrail.yaml` is guarded by its own rules on the baseline (SPEC/09 §2)."""
    return (agent / "rules" / "guardrail.yaml").is_file()


def guardrail_errors(doc: dict[str, Any], root: Path = ROOT, *, own_rules: bool = False,
                     held: dict[str, Any] | None = None) -> list[str]:  # fmt: skip
    """The pin. Without `rules/`, the platform's (M06); with it, the agent's own (M09 PR 2, SPEC/09 §6; R10).

    `own_rules`: the folder carries `rules/guardrail.yaml`. Its pin must then be not null and not
    refagent's: the platform builds the guardrail from the merged rules in the agent's own stack
    and conditions the call on that resource, reading the pin only to refuse those two (R3). `held`
    is the registry row's guardrail for this agent, when the caller can read it (the deploy can,
    the check's job cannot): a pin that is not the held one is refused, so a placeholder is admitted
    only while the row holds no guardrail for the agent and refused once it does (R3, R10)."""
    platform = yaml.safe_load((root / "agents" / PLATFORM_AGENT / "manifest.yaml").read_text(encoding="utf-8"))
    pin = doc.get("guardrail")
    if not platform.get("guardrail") or not pin:
        return ["manifest.yaml: no guardrail pinned; an agent from the template pins the platform's "
                "(SPEC/06 section 6, item 6), and the platform's must be a pin" if not own_rules else
                "manifest.yaml: no guardrail pinned; an agent with rules/ pins a guardrail of its own, built by the "
                "platform from its rules on the baseline (SPEC/09 section 2; ADR-0014 decision 4)"]  # fmt: skip
    if not own_rules:
        if pin != platform.get("guardrail"):
            return [f"manifest.yaml: guardrail {pin!r} is not the platform's {platform.get('guardrail')!r} "
                    "(SPEC/06 section 6, item 6: one guardrail for every agent at M06; an agent with rules/ pins its own)"]  # fmt: skip
        return []
    if not isinstance(pin, dict) or not isinstance(pin.get("id"), str) or not isinstance(pin.get("version"), str) \
            or not pin["id"] or not pin["version"]:  # fmt: skip
        return [f"manifest.yaml: guardrail {pin!r} is not an id and a version, each a string"]
    if pin == platform.get("guardrail") or pin.get("id") == (platform.get("guardrail") or {}).get("id"):
        return [f"manifest.yaml: guardrail {pin!r} is refagent's; an agent with rules/ is guarded by its own, built from "
                "them on the baseline, not by refagent's six topics (SPEC/09 section 2; R10)"]  # fmt: skip
    if held and pin != held:
        return [f"manifest.yaml: guardrail {pin!r} is not the {held!r} the registry holds for this agent: a pin the "
                "registry does not hold is admitted only while the row holds no guardrail for the agent (R3)"]  # fmt: skip
    return []


def evaluate(agent: Path, repository: str, root: Path = ROOT, *, lookup=None,
             held_guardrail: dict[str, Any] | None = None) -> dict[str, list[str]]:  # fmt: skip
    """Each check's errors over the agent folder, by check name; every list empty means passed.

    `held_guardrail` is the registry row's pin for this agent, given by a caller that can read the
    registry (deploy.yml's deploy job); the check's own job holds no AWS credential and gives none."""
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
    errors: dict[str, list[str]] = {"the agent's name": name_errors(doc.get("name"), root, agent=agent)}
    if errors["the agent's name"]:
        return errors
    name = doc["name"]
    own_rules = has_own_rules(agent)
    errors["the platform's guardrail" if not own_rules else "the agent's own guardrail"] = guardrail_errors(
        doc, root, own_rules=own_rules, held=held_guardrail)
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
        # M09 PR 2 (SPEC/09 §2, §6; seeds S1, S2, S5): an agent's rules/guardrail.yaml merged onto the
        # baseline add-only, each plant named for a rule the merged guardrail builds. Read only for an agent
        # that carries rules/; one without is guarded by the platform's as at M06.
        errors["an agent's rules on the platform baseline, add-only, each plant naming a rule it builds"] = (
            agent_rules.rules_errors(tree / "agents" / name, root=root) if own_rules else [])
        # M10 PR 2 (SPEC/10 §2, §6; seed S2; F10.4): the manifest says who may call the agent, even if nobody.
        # Read for every agent: a manifest with no `callers` key is refused here, for this named reader.
        errors["an agent's manifest says who may call it, even if nobody (callers)"] = callers.callers_errors(doc)
    finally:
        seats.login_holds_seat.cache_clear()
        if previous is None:
            os.environ.pop("AGENTKEEL_SEAT_REPOSITORY", None)
        else:
            os.environ["AGENTKEEL_SEAT_REPOSITORY"] = previous
        shutil.rmtree(tree, ignore_errors=True)
    return errors


def _which(export: dict[str, Any], live: dict[str, Any], key: str) -> str:
    """For `rules`, which rule and which of its parameters differ: GitHub adding a field to a rule refused
    every agent repository once (M06 PR 3), and the next drift should cost a re-export, not a search."""
    if key != "rules" or not isinstance(export.get(key), list) or not isinstance(live.get(key), list):
        return ""
    ours = {r.get("type"): r.get("parameters") or {} for r in export[key] if isinstance(r, dict)}
    theirs = {r.get("type"): r.get("parameters") or {} for r in live[key] if isinstance(r, dict)}
    parts = []
    for kind in sorted(set(ours) | set(theirs), key=str):
        if kind not in ours or kind not in theirs:
            parts.append(f"{kind}: {'only in the export' if kind in ours else 'only live'}")
        elif ours[kind] != theirs[kind]:
            names = sorted(n for n in set(ours[kind]) | set(theirs[kind]) if ours[kind].get(n) != theirs[kind].get(n))
            parts.append(f"{kind}: {', '.join(names)}")
    return f" ({'; '.join(parts)})" if parts else ""


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
            found = [f"{EXPORT}: {key} differs from live ruleset {one.get('id')}{_which(export, one, key)}"
                     for key in ruleset.COMPARED if export.get(key) != one.get(key)]  # fmt: skip
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
    # M09 PR 2 (R3): the registry row's guardrail for this agent, `<id>:<version>`, given by deploy.yml's deploy
    # job, which can read the registry; empty when the row holds none. The check's own job gives none.
    one.add_argument("--held-guardrail", default="")
    two = sub.add_parser("ruleset")
    two.add_argument("--live", required=True, type=Path)
    two.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    if args.what == "evaluate":
        logins: list[str] = []

        def deferred(login: str) -> tuple[bool, str]:
            logins.append(login)
            return True, "deferred to the posting job"

        held = None
        if args.held_guardrail:
            held_id, _, held_version = args.held_guardrail.partition(":")
            held = {"id": held_id, "version": held_version}
        errors = evaluate(args.agent, args.repository, lookup=deferred if args.defer_seat_access else None,
                          held_guardrail=held)  # fmt: skip
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
