"""model-watch: Bedrock's lifecycle for the pinned models, and the pull requests it sets off (SPEC/07 §1, §6; SPEC/04 §9 cut a).

    python scripts/model_watch.py read --out LIFECYCLE.json                       # as the model-watch role: Bedrock, read only
    python scripts/model_watch.py plan --lifecycle LIFECYCLE.json --out PLAN.json  # no key: which pull requests, as data
    python scripts/model_watch.py open --plan PLAN.json                           # agentkeel-upgrades' key: the drafts

Until M07 PR 2 a swap was opened by a person (M04's two were), refagent's
`deprecated_after` was null and nothing asked Bedrock for it:
`src/validate/lifecycle.py` reads the date the manifest carries and nothing
in AWS.

**What it opens.** At most two draft pull requests on `agentkeel`, each one
change to `agents/refagent/manifest.yaml` with a drafted Threshold Owner
ruling beside it:

- **`deprecated_after`**, written from Bedrock's `modelLifecycle.endOfLifeTime`
  for refagent's pin, when Bedrock gives a date and it differs from the
  manifest's. It opens nothing to set a null to null, and nothing to clear
  or delay a date the manifest holds: moving it later, or clearing it, with
  the model unchanged is a relaxation with two keys (ADR-0009 amendment 1),
  and is a person's to propose.
- **the swap**: refagent's pin moved to the candidate the Threshold Owner
  named. A person names the candidate; the platform opens the pull request
  (SPEC/07 §8). The name is read from the run file the Threshold Owner
  ruled it in (`CANDIDATE_FILE`, its `candidate:`), a role under the
  manifest's `pinned_roles`, whose whole pin the swap copies into `model`.
  A candidate Bedrock does not call ACTIVE is not proposed.

Its shadow run is the pull request's own `evals` run, which M04's gate
rules (F4.1, F4.2, F4.4): a pull request opened by an App starts
`evals.yml`, which one opened with `GITHUB_TOKEN` would not.

**One pull request per branch, ever** (`scripts/platform_pr.py`). The swap's
branch is `model-watch/<role>`. After it merged and was reverted the pin
differs from the candidate again, and nothing is opened a second time: a
new attempt is a new candidate, named by a person.

**The ruling file is a draft, and is written by the keyed job itself**,
never taken from the plan: it names the pull request's own number, so it is
a second commit, and it carries no line that starts with the two words
`cold-review-ruling` reads as a seat's ruling (rulings/pr2-security.md item
10; security-reviewer 8 on M07 PR 1). A seat rules it by replacing its
"Drafted" line. A ruling file is not a person's edit (BLOCK 2).

Two halves (item 4): `read` and `plan` run with no App key, the first as a
role that may ask Bedrock for a model's lifecycle and nothing else; `open`
holds the key and checks the plan again against `main`'s own manifest
before it mints a token for this repository alone.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import platform_upgrade  # noqa: E402

REPOSITORY = "andaro74/agentkeel"
MANIFEST = "agents/refagent/manifest.yaml"
CANDIDATE_FILE = "milestones/M07/runs/f7_3_rollback.yaml"  # where the Threshold Owner named the candidate
RULINGS = "milestones/M07/rulings"
REGION = "us-west-2"
PIN_FIELDS = ("id", "version", "profile", "region")
ROLE = re.compile(r"^[a-z0-9][a-z0-9_]{1,40}$")
DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
RULED_WORDS = "Ruled by"  # never at the start of a line this writes


class Refused(Exception):
    """Not a pull request model-watch opens."""


# --- read: Bedrock, as the model-watch role ---------------------------------------


def pinned_ids(manifest: dict[str, Any]) -> list[str]:
    """refagent's pin and every role's that carries an id, once each, in the manifest's order."""
    ids = [manifest["model"]["id"]]
    for role in (manifest.get("pinned_roles") or {}).values():
        for pin in role if isinstance(role, list) else [role]:
            if isinstance(pin, dict) and isinstance(pin.get("id"), str) and pin["id"] not in ids:
                ids.append(pin["id"])
    return ids


def read_lifecycle(ids: list[str], client: Any = None) -> dict[str, Any]:
    """Each model's `modelLifecycle` as Bedrock returns it; an id that could not be read carries its error."""
    from datetime import UTC, datetime

    if client is None:
        import boto3

        client = boto3.client("bedrock", region_name=REGION)
    models: dict[str, Any] = {}
    for model_id in ids:
        try:
            details = client.get_foundation_model(modelIdentifier=model_id)["modelDetails"]
            lifecycle = details.get("modelLifecycle") or {}
            end = lifecycle.get("endOfLifeTime")
            models[model_id] = {"status": lifecycle.get("status"),
                                "endOfLifeTime": end.isoformat() if hasattr(end, "isoformat") else end, "error": None}  # fmt: skip
        except Exception as exc:  # noqa: BLE001 - an unread model is an observation, never a guess
            models[model_id] = {"status": None, "endOfLifeTime": None, "error": f"{type(exc).__name__}: {exc}"[:300]}
    return {"read_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"), "region": REGION,
            "models": models}  # fmt: skip


# --- plan: no key -------------------------------------------------------------------------


def candidate_role(root: Path = ROOT) -> str | None:
    """The role the Threshold Owner named, from the run file: `candidate: pinned_roles.<role>`. None if none."""
    path = root / CANDIDATE_FILE
    if not path.is_file():
        return None
    named = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("candidate")
    role = named.removeprefix("pinned_roles.") if isinstance(named, str) else None
    return role if isinstance(role, str) and ROLE.match(role) else None


def end_date(lifecycle: dict[str, Any] | None) -> str | None:
    """Bedrock's end-of-life as the manifest's date, YYYY-MM-DD; None when Bedrock gives none."""
    end = (lifecycle or {}).get("endOfLifeTime")
    return end[:10] if isinstance(end, str) and DATE.match(end[:10]) else None


def plan(manifest_text: str, lifecycle: dict[str, Any], role: str | None, base: str, run_url: str | None) -> list[dict[str, Any]]:
    """What model-watch would open at `base`, and for anything it would not, why."""
    manifest = yaml.safe_load(manifest_text)
    models = lifecycle.get("models") or {}
    pin = manifest["model"]
    entries: list[dict[str, Any]] = []

    def entry(kind: str, branch: str, **more: Any) -> dict[str, Any]:
        return {"kind": kind, "repository": REPOSITORY, "base": base, "branch": branch, "run_url": run_url, "open": False, **more}

    # deprecated_after, from Bedrock's own date for the pin.
    mine = models.get(pin["id"]) or {}
    stated, read = manifest.get("deprecated_after"), end_date(mine)
    dated = entry("deprecated_after", f"model-watch/deprecated-after-{read or 'none'}", model=pin["id"], date=read)
    if mine.get("error") or not mine:
        dated["why"] = f"Bedrock's lifecycle for {pin['id']} was not read ({mine.get('error') or 'not asked'})"
    elif read is None:
        dated["why"] = (f"Bedrock gives {pin['id']} no end-of-life date; nothing is written"
                        + ("" if stated is None else f", and the manifest's {stated} is a person's to clear, with two keys"))  # fmt: skip
    elif read == stated:
        dated["why"] = f"the manifest already says {stated}"
    elif isinstance(stated, str) and read > stated:
        dated["why"] = f"Bedrock's date {read} is later than the manifest's {stated}: moving it later is two keys, a person's to propose"
    else:
        dated |= {"open": True, "why": f"Bedrock's end-of-life for {pin['id']} is {read}; the manifest says {stated}",
                  "files": {MANIFEST: platform_upgrade.set_fields(manifest_text, {"deprecated_after": read})}}  # fmt: skip
    entries.append(dated)

    # The swap, to the candidate a person named.
    swap = entry("swap", f"model-watch/{role}", role=role)
    candidate = (manifest.get("pinned_roles") or {}).get(role) if role else None
    if role is None:
        swap["why"] = f"{CANDIDATE_FILE} names no candidate: a person names it, the platform opens the pull request"
    elif not isinstance(candidate, dict) or not all(field in candidate for field in PIN_FIELDS):
        swap["why"] = f"pinned_roles.{role} is not a whole pin ({', '.join(PIN_FIELDS)})"
    elif all(candidate[field] == pin.get(field) for field in PIN_FIELDS):
        swap["why"] = f"refagent's pin is already pinned_roles.{role}"
    elif (models.get(candidate["id"]) or {}).get("status") != "ACTIVE":
        seen = models.get(candidate["id"]) or {}
        swap["why"] = (f"Bedrock does not call {candidate['id']} ACTIVE "
                       f"({seen.get('status') or seen.get('error') or 'not read'}): not proposed")  # fmt: skip
    else:
        new = {field: candidate[field] for field in PIN_FIELDS}
        swap |= {"open": True, "why": f"the Threshold Owner named pinned_roles.{role}, and refagent's pin is {pin['id']}",
                 "from": {field: pin.get(field) for field in PIN_FIELDS}, "to": new,
                 "files": {MANIFEST: platform_upgrade.set_fields(manifest_text, {"model": new})}}  # fmt: skip
    entries.append(swap)
    return entries


# --- open: the key, on the plan ------------------------------------------------------------


def entry_errors(entry: Any, manifest_text: str, role: str | None) -> list[str]:
    """Why the keyed job will not open this entry; [] if nothing. Held to `main`'s own manifest and to
    the candidate `main`'s own run file names, not to what the plan says they are."""
    if not isinstance(entry, dict) or not isinstance(entry.get("files"), dict):
        return ["not an entry with files"]
    errors = []
    if entry.get("repository") != REPOSITORY:
        errors.append(f"{entry.get('repository')} is not {REPOSITORY}")
    if sorted(entry["files"]) != [MANIFEST] or not isinstance(entry["files"].get(MANIFEST), str):
        return [*errors, f"model-watch changes {MANIFEST} and nothing else, not {sorted(entry['files'])}"]
    try:
        before, after = yaml.safe_load(manifest_text), yaml.safe_load(entry["files"][MANIFEST])
    except yaml.YAMLError:
        return [*errors, "the manifest, on main or as proposed, is not YAML"]
    if not isinstance(before, dict) or not isinstance(after, dict):
        return [*errors, "the manifest, on main or as proposed, is not a mapping"]
    moved = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    if entry.get("kind") == "swap":
        named = (before.get("pinned_roles") or {}).get(role) if role else None
        if role is None or entry.get("role") != role or entry.get("branch") != f"model-watch/{role}":
            errors.append(f"the plan's candidate {entry.get('role')!r} is not the one {CANDIDATE_FILE} names on main ({role!r})")
        elif moved != ["model"] or not isinstance(named, dict) or after["model"] != {f: named.get(f) for f in PIN_FIELDS}:
            errors.append(f"a swap sets `model` to pinned_roles.{role}'s pin and nothing else; this moves {', '.join(moved) or 'nothing'}")
    elif entry.get("kind") == "deprecated_after":
        new = after.get("deprecated_after")
        if moved != ["deprecated_after"] or not isinstance(new, str) or not DATE.match(new):
            errors.append(f"this sets deprecated_after to a date and nothing else; it moves {', '.join(moved) or 'nothing'}")
        elif isinstance(before.get("deprecated_after"), str) and new > before["deprecated_after"]:
            errors.append("this moves deprecated_after later, which is two keys and a person's to propose")
        if entry.get("branch") != f"model-watch/deprecated-after-{new}":
            errors.append(f"branch {entry.get('branch')!r} does not name the date")
    else:
        errors.append(f"kind {entry.get('kind')!r} is not one model-watch opens")
    return errors


def ruling_slug(entry: dict[str, Any]) -> str:
    return "model-watch-" + str(entry["branch"]).split("/", 1)[1].replace("_", "-")


def draft_ruling(entry: dict[str, Any], number: int) -> str:
    """The Threshold Owner's ruling for this pull request, as a draft. Written here, from fields this job
    checked, and with no line a gate would read as a seat's ruling."""
    slug = ruling_slug(entry)
    if entry["kind"] == "swap":
        change = (f"refagent's pin moves from `{entry['from']['id']}` to `{entry['to']['id']}` "
                  f"(`pinned_roles.{entry['role']}`, the candidate named in `{CANDIDATE_FILE}`). "
                  "The whole pin is copied: id, version, profile, region.")  # fmt: skip
        asks = ("A model id change is measured by the gate, not two-keyed (SPEC/04 section 10): this pull request's own "
                "`evals` run is the shadow run, with A-vs-A, and M04's gate rules it (F4.1, F4.2, F4.4). Its verdict is "
                "not stated here. It is merged only if that envelope is GREEN and every required check is green. "
                "A swap never gets a second run.")  # fmt: skip
        title = f"model-watch, the swap to pinned_roles.{entry['role']}"
    else:
        change = (f"`deprecated_after` is set to `{entry['date']}`, Bedrock's `modelLifecycle.endOfLifeTime` for "
                  f"`{entry['model']}`, read by model-watch.")  # fmt: skip
        asks = ("Writing the date Bedrock gives is not a relaxation. `validate` fails a pin 30 days from its date or "
                "fewer, so a date this close blocks every pull request until the pin moves.")  # fmt: skip
        title = "model-watch, deprecated_after from Bedrock"
    text = f"""---
# Drafted by model-watch on agentkeel's main, as the App agentkeel-upgrades.
# A seat rules it; the platform does not.
ruling: {slug}
seat: Threshold Owner
authorises:
  - {MANIFEST}
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - {CANDIDATE_FILE}
pr: {number}
---

# Ruling: {title}

Drafted by model-watch for the Threshold Owner ({entry.get('run_url') or 'run not recorded'}). Not ruled: a seat replaces this line with its own.

## What this pull request changes

{change}

Nothing else: no workflow, no bar, no golden, no other field of the manifest.

## What the seat is asked to rule

{asks}

This file is not a person's edit of the upgrade (SPEC/07 section 1, item 3): a seat ruling a change is the gate working.
"""
    if any(line.startswith(RULED_WORDS) for line in text.splitlines()):
        raise Refused("the drafted ruling would carry a line a gate reads as ruled")
    return text


def body_of(entry: dict[str, Any]) -> str:
    what = (f"moves refagent's pin to `{entry['to']['id']}` (`pinned_roles.{entry['role']}`)" if entry["kind"] == "swap"
            else f"sets `deprecated_after` to `{entry['date']}`, Bedrock's end-of-life for `{entry['model']}`")  # fmt: skip
    return (
        f"model-watch {what}.\n\n**Why:** {entry.get('why')}.\n\n"
        f"One file changes, `{MANIFEST}`, and a drafted Threshold Owner ruling is added beside it for the seat to rule. "
        "This pull request's own `evals` run measures the change; nothing is skipped for it.\n\n"
        f"Opened by run {entry.get('run_url') or 'not recorded'}, as `agentkeel-upgrades`, from `main`. "
        "Nobody needs to edit it; a seat rules the ruling file."
    )


def open_all(entries: list[Any], key: str, root: Path = ROOT) -> list[dict[str, Any]]:
    from scripts import platform_check, platform_pr

    app_id = platform_check.load_grant(root)["agentkeel-upgrades"]["app_id"]
    owner = REPOSITORY.split("/")[0]
    manifest_text = (root / MANIFEST).read_text(encoding="utf-8")
    role = candidate_role(root)
    results = []
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("open"):
            continue
        result: dict[str, Any] = {"kind": entry.get("kind"), "opened": False}
        try:
            if errors := entry_errors(entry, manifest_text, role):
                raise platform_pr.Refused("; ".join(errors))
            with platform_check._As(platform_check.app_token(app_id, owner, key, REPOSITORY, "open")):
                default = platform_check.gh(f"/repos/{REPOSITORY}")["default_branch"]
                what = f"refagent's pin to pinned_roles.{entry['role']}" if entry["kind"] == "swap" else f"deprecated_after {entry['date']}"
                result |= platform_pr.open_draft(REPOSITORY, default, str(entry.get("base")), entry["branch"], entry["files"],
                                                 title=f"model-watch: {what}", body=body_of(entry),
                                                 message=f"model-watch: {what}")  # fmt: skip
                result["opened"] = True
                path = f"{RULINGS}/{ruling_slug(entry)}.md"
                result["ruling"] = platform_pr.add_commit(
                    REPOSITORY, entry["branch"], {path: draft_ruling(entry, result["number"])},
                    f"model-watch: {path}, drafted for the Threshold Owner (pr {result['number']})")  # fmt: skip
        except (platform_pr.Refused, Refused, urllib.error.URLError, KeyError, TimeoutError, OSError) as exc:
            result["why"] = f"{type(exc).__name__}: {exc}"
        results.append(result)
        print(f"{entry.get('kind')}: {'opened #' + str(result.get('number')) if result['opened'] else 'not opened: ' + result.get('why', '')}"
              + (f" (the pull request is open and its ruling draft is not: {result['why']})" if result["opened"] and "why" in result else ""))  # fmt: skip
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="what", required=True)
    one = sub.add_parser("read")
    one.add_argument("--out", required=True, type=Path)
    two = sub.add_parser("plan")
    two.add_argument("--lifecycle", required=True, type=Path)
    two.add_argument("--base", required=True, help="the commit of main this was planned at")
    two.add_argument("--run-url")
    two.add_argument("--out", required=True, type=Path)
    three = sub.add_parser("open")
    three.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args(argv)

    manifest_text = (ROOT / MANIFEST).read_text(encoding="utf-8")
    if args.what == "read":
        lifecycle = read_lifecycle(pinned_ids(yaml.safe_load(manifest_text)))
        args.out.write_text(json.dumps(lifecycle, indent=2) + "\n", encoding="utf-8")
        for model_id, seen in lifecycle["models"].items():
            print(f"{model_id}: {seen['status'] or seen['error']}" + (f", end of life {seen['endOfLifeTime']}" if seen["endOfLifeTime"] else ""))
        return 0
    if args.what == "plan":
        entries = plan(manifest_text, json.loads(args.lifecycle.read_text(encoding="utf-8")), candidate_role(), args.base, args.run_url)
        args.out.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
        for entry in entries:
            print(f"{entry['kind']}: {'open ' + entry['branch'] if entry['open'] else 'nothing'}: {entry['why']}")
        return 0

    from scripts import platform_check

    key = os.environ.pop("AGENTKEEL_APP_PRIVATE_KEY", None)
    if not key:
        print("no AGENTKEEL_APP_PRIVATE_KEY: pull requests are opened in the platform-upgrades environment only")
        return 1
    try:
        open_all(json.loads(args.plan.read_text(encoding="utf-8")), key)
    except platform_check.NoGrant as refusal:
        print(f"REFUSED: {refusal}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
