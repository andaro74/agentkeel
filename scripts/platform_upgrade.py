"""A platform upgrade for an agent made from the template: computed here, opened by the platform (SPEC/07 §1, §2, §6).

    python scripts/platform_upgrade.py diff --agent DIR --platform DIR     # `make upgrade`: prints, opens nothing
    python scripts/platform_upgrade.py plan --template DIR --out PLAN.json  # no secret: what to open, as data
    python scripts/platform_upgrade.py open --plan PLAN.json                # agentkeel-upgrades' key: the drafts

Until M07 PR 2 nothing computed an upgrade: `platform_version` was written
once by `scripts/make_template.py` and read by nothing, and a team that
wanted a later platform version edited its own files by hand (seed S1).

**What an upgrade may change.** The platform-owned files of an agent
repository, and nothing else (SPEC/07 §2): `manifest.yaml`'s
`platform_version` and `guardrail`, `server.py` and `__init__.py`.
`diff(agent, platform)` reads those names from the platform side and no
other: a workflow or an `agent.py` that sits beside them is never read, so
it is never brought (F7.1). The manifest is edited as text, field by field,
so the team's comments and every other field stay byte for byte; the edit
is then parsed and refused if any other field moved.

**Behind** is ancestry in `agentkeel` (SPEC/07 §2): an agent's version is
behind when the commit it names is an ancestor of the template's and not
equal to it. A version is a milestone tag (`m07`) or a short commit.

**Major or minor** is read, not stated: major when the platform check at
`main` refuses the agent's default-branch head as it stands, minor
otherwise. The pull request's body records which, and the checks that
refused.

**Two halves, as `platform-check.yml` has** (rulings/pr2-security.md item
4). `plan` holds no secret: it reads each agent repository as data, at the
head the platform's App passed, and writes what to open. `open` holds
`agentkeel-upgrades`' key and runs on that artifact: it checks every entry
again (the paths, the fields, the version, the repository's owner) before
it mints a token for that repository, and opens one draft pull request
through `scripts/platform_pr.py`. Nothing from an agent repository is
imported or run in either.

**The bytes proposed are held to the template and to `main`** (M07 PR 3;
rulings/pr2-security.md item 13l; security-reviewer 4 and cold review N7
on M07 PR 2: until then `open` held the paths and the manifest's fields,
and took the content of `server.py` and `__init__.py`, and the guardrail's
value, from the plan). `plan` writes the template commit it read. `open`
asks git for the template repository's default-branch head, with no token,
refuses a plan made from any other commit, fetches the template as data at
that commit, and requires each proposed `server.py` and `__init__.py` to
equal the template's text (as UTF-8, with line endings read as one: the
plan carries text, not bytes), the proposed `platform_version` to be
the template's, and the proposed `guardrail` to be the one `main` pins
(`agents/refagent/manifest.yaml`). What it does not hold: who may push to
the template repository's default branch. That is the owner, by hand, at
M07 (SPEC/07 §11 R5).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PLATFORM_OWNED = ("manifest.yaml", "server.py", "__init__.py")
MANIFEST_FIELDS = ("platform_version", "guardrail")
COPIED = ("server.py", "__init__.py")
VERSION = re.compile(r"^(m[0-9]{2}|[0-9a-f]{7,40})$")
TEMPLATE_REPOSITORY = "agent-template"


class Refused(Exception):
    """Not an upgrade the platform computes or opens."""


# --- the manifest, edited as text ---------------------------------------------


def _scalar(value: Any) -> str:
    """A YAML scalar that parses back to `value`, quoted only when it must be ("5" is a string)."""
    plain = str(value)
    if isinstance(value, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9._-]*", plain) and yaml.safe_load(plain) == value:
        return plain
    return json.dumps(value)


def _block(lines: list[str], key: str) -> tuple[int, int] | None:
    """The lines of top-level `key`: its own line, then every indented line under it."""
    start = next((i for i, line in enumerate(lines) if re.match(rf"{re.escape(key)}\s*:", line)), None)
    if start is None:
        return None
    end = start + 1
    while end < len(lines) and lines[end][:1] in (" ", "\t") and lines[end].strip():
        end += 1
    return start, end


def set_fields(text: str, fields: dict[str, Any]) -> str:
    """`text`, a manifest, with each top-level field in `fields` set, and every other byte kept.

    A scalar's line and each line of a mapping are rewritten in place, so a comment above a field, or
    after a value, stays. A field that is not there, or changes shape (a null to a mapping), is
    written whole. The result is parsed: any other field that moved is a refusal, not a diff."""
    before = yaml.safe_load(text)
    if not isinstance(before, dict):
        raise Refused("manifest.yaml is not a mapping")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.replace("\r\n", "\n").split("\n")
    for key, value in fields.items():
        if before.get(key) == value:
            continue
        found = _block(lines, key)
        dumped = yaml.safe_dump({key: value}, sort_keys=False).rstrip("\n").split("\n")
        same_shape = isinstance(value, dict) and isinstance(before.get(key), dict) and set(value) == set(before[key])
        if found is None:
            while lines and not lines[-1].strip():
                lines.pop()
            lines += [*dumped, ""]
        elif isinstance(value, dict) and same_shape:
            start, end = found
            for i in range(start + 1, end):
                inner = re.match(r"(\s+)([\w-]+)(\s*:\s*)(.*?)(\s+#.*)?$", lines[i])
                if not inner or inner[2] not in value or isinstance(value[inner[2]], (dict, list)):
                    continue
                if before[key][inner[2]] == value[inner[2]]:
                    continue  # a line whose value does not move is not rewritten
                lines[i] = f"{inner[1]}{inner[2]}{inner[3]}{_scalar(value[inner[2]])}{inner[5] or ''}"
        elif not isinstance(value, (dict, list)) and not isinstance(before.get(key), (dict, list)):
            start, _end = found
            own = re.match(r"([\w-]+\s*:\s*)(.*?)(\s+#.*)?$", lines[start])
            lines[start] = f"{own[1]}{_scalar(value)}{own[3] or ''}"  # type: ignore[index]
        else:
            start, end = found
            lines[start:end] = dumped
    edited = newline.join(lines)
    after = yaml.safe_load(edited)
    if not isinstance(after, dict) or any(after.get(key) != value for key, value in fields.items()):
        raise Refused(f"manifest.yaml: the edit did not set {', '.join(fields)}")
    moved = sorted(k for k in set(before) | set(after) if k not in fields and before.get(k) != after.get(k))
    if moved:
        raise Refused(f"manifest.yaml: the edit moved {', '.join(moved)}, which is not the platform's to change")
    return edited


# --- the upgrade's diff (seed S1's reader) --------------------------------------


def platform_side(platform: Path) -> dict[str, Any]:
    """The platform's version and guardrail pin: `platform.json` where one is given, else the
    template's own `manifest.yaml`, which carries both."""
    stated = platform / "platform.json"
    if stated.is_file():
        doc = json.loads(stated.read_text(encoding="utf-8"))
    else:
        doc = yaml.safe_load((platform / "manifest.yaml").read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or not all(field in doc for field in MANIFEST_FIELDS):
        raise Refused(f"{platform}: the platform side names no {' and '.join(MANIFEST_FIELDS)}")
    if not isinstance(doc["platform_version"], str) or not VERSION.match(doc["platform_version"]):
        raise Refused(f"{platform}: platform_version {doc['platform_version']!r} is not a milestone tag or a commit")
    return {field: doc[field] for field in MANIFEST_FIELDS}


def diff(agent: Path, platform: Path) -> dict[str, str]:
    """The upgrade of the agent folder `agent` to the platform at `platform`: path to new content, for
    each platform-owned file that changes, and for no other path.

    Only the platform-owned names are read from `platform`; whatever else is there is not looked at."""
    target = platform_side(platform)
    changed: dict[str, str] = {}
    manifest = (agent / "manifest.yaml").read_text(encoding="utf-8")
    edited = set_fields(manifest, target)
    if edited != manifest:
        changed["manifest.yaml"] = edited
    for name in COPIED:
        source = platform / name
        if not source.is_file():
            continue
        new = source.read_text(encoding="utf-8")
        mine = agent / name
        if not mine.is_file() or mine.read_text(encoding="utf-8") != new:
            changed[name] = new
    outside = sorted(set(changed) - set(PLATFORM_OWNED))
    if outside:  # cannot happen from the lines above; said, so a later edit that widens them fails here
        raise Refused(f"the upgrade touches paths the platform does not own: {outside}")
    return changed


# --- behind, and major or minor -------------------------------------------------


def commit_of(version: Any, root: Path = ROOT) -> str | None:
    """The `agentkeel` commit a platform version names: a milestone tag, or a commit. None if neither."""
    if not isinstance(version, str) or not VERSION.match(version):
        return None
    for ref in (f"refs/tags/{version}^{{commit}}", f"{version}^{{commit}}"):
        done = subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref], cwd=root, capture_output=True,
                              text=True, check=False)  # fmt: skip
        if done.returncode == 0 and done.stdout.strip():
            return done.stdout.strip()
    return None


def behind(agent_version: Any, platform_version: Any, root: Path = ROOT) -> tuple[bool, str]:
    """(behind, why). Behind when the agent's version is an ancestor of the platform's and not it."""
    mine, theirs = commit_of(agent_version, root), commit_of(platform_version, root)
    if mine is None or theirs is None:
        unknown = agent_version if mine is None else platform_version
        return False, f"version {unknown!r} names no commit of agentkeel's: not read as behind"
    if mine == theirs:
        return False, f"at {platform_version}"
    done = subprocess.run(["git", "merge-base", "--is-ancestor", mine, theirs], cwd=root, capture_output=True, check=False)
    if done.returncode != 0:
        return False, f"{agent_version} is not an ancestor of {platform_version}: ahead, or on another line"
    return True, f"{agent_version} is behind {platform_version}"


def kind_of(agent: Path, repository: str) -> tuple[str, list[str]]:
    """major when the platform check at this checkout refuses the agent's head as it stands; the checks that refused."""
    from src.validate import agent as platform

    errors = platform.evaluate(agent, repository, lookup=lambda login: (True, "deferred: read by the App at the check"))
    refused = sorted(name for name, errs in errors.items() if errs)
    return ("major" if refused else "minor"), refused


# A check's name as the platform check posts it: words, no markup. What the keyed job will write in a body.
CHECK_NAME = re.compile(r"[A-Za-z0-9 ,.'/:_-]{1,160}")


def body_of(entry: dict[str, Any]) -> str:
    refused = "".join(f"\n- {name}" for name in entry["refused"]) or "\n- none"
    return (
        f"The platform moved from `{entry['from']}` to `{entry['to']}`. This draft brings the platform-owned "
        f"files of this repository to `{entry['to']}` and changes nothing else.\n\n"
        f"**Kind: {entry['kind']}.** Major means the platform check at `{entry['to']}` refuses this repository's "
        f"default branch as it stands; minor means it passes. Checks that refused the default branch at "
        f"`{entry['base'][:12]}`:{refused}\n\n"
        f"**Files:** {', '.join(f'`{path}`' for path in sorted(entry['files']))}. In `manifest.yaml`, only "
        "`platform_version` and `guardrail`.\n\n"
        "Opened by the platform (`agentkeel-upgrades`) from `agentkeel`'s `main`. It is checked like any change: "
        "it merges when the platform check passes it and one of this repository's seats merges it. Nobody needs "
        "to edit it. If you do, the platform's record will say a person's edit was needed.\n\n"
        "What this is and what to do: `docs/developer/upgrade.md` in `andaro74/agentkeel`."
    )


# --- plan: no secret ------------------------------------------------------------------


def fetch_as_data(repository: str, commit: str, into: Path) -> Path:
    """The agent repository's tree at `commit`, as files and nothing more: no hooks, no links followed,
    no credentials. A public repository; one that cannot be fetched is skipped with the reason."""
    target = into / repository.replace("/", "__")
    target.mkdir(parents=True)
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    env.pop("GITHUB_TOKEN", None)
    for command in (["git", "init", "--quiet"],
                    ["git", "-c", "core.hooksPath=" + os.devnull, "fetch", "--quiet", "--depth", "1",
                     f"https://github.com/{repository}.git", commit],
                    ["git", "-c", "core.symlinks=false", "-c", "core.hooksPath=" + os.devnull, "checkout", "--quiet",
                     "FETCH_HEAD"]):  # fmt: skip
        done = subprocess.run(command, cwd=target, capture_output=True, text=True, env=env, check=False)
        if done.returncode != 0:
            raise Refused(f"{repository}@{commit[:12]} could not be read as data: {done.stderr.strip()[-200:]}")
    return target


def checkout_commit(folder: Path) -> str | None:
    """The commit a checkout is at, as git gives it. None when `folder` is not the top of a checkout (a
    fixture, or `make upgrade`'s platform folder): then the plan names no template commit, and the
    keyed job opens nothing from it."""
    if not (folder / ".git").exists():
        return None
    done = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "HEAD^{commit}"], cwd=folder, capture_output=True,
                          text=True, check=False)  # fmt: skip
    found = done.stdout.strip()
    return found if done.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", found) else None


def plan_one(agent: dict[str, Any], template: Path, work: Path, fetch=fetch_as_data,
             template_commit: str | None = None) -> dict[str, Any]:  # fmt: skip
    """One agent's entry: what to open, or why nothing is. Never raises: a reason is a result."""
    from src.validate import agent as platform

    repository, commit = agent["repository"], agent["commit"]
    out: dict[str, Any] = {"repository": repository, "name": agent.get("name"), "base": commit, "open": False,
                           "template_commit": template_commit}  # fmt: skip
    try:
        target = platform_side(template)
        folder = fetch(repository, commit, work)
        if links := platform.links(folder):
            raise Refused(f"a symbolic link in the repository ({links[0]}); nothing is read from it")
        manifest = yaml.safe_load((folder / "manifest.yaml").read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise Refused("manifest.yaml is not a mapping")
        out |= {"from": manifest.get("platform_version"), "to": target["platform_version"]}
        if manifest.get("rollout") == "retired":
            raise Refused("the agent is retired: nothing is upgraded")
        is_behind, why = behind(manifest.get("platform_version"), target["platform_version"])
        if not is_behind:
            raise Refused(why)
        files = diff(folder, template)
        if not files:
            raise Refused("behind, and no platform-owned file differs")
        kind, refused = kind_of(folder, repository)
        out |= {"open": True, "why": why, "kind": kind, "refused": refused, "files": files,
                "branch": f"platform-upgrade/{target['platform_version']}",
                "title": f"Platform upgrade to {target['platform_version']} ({kind})"}  # fmt: skip
        out["body"] = body_of(out)
    except (Refused, OSError, yaml.YAMLError, ValueError) as exc:
        out["why"] = str(exc)
    return out


def plan(agents: list[dict[str, Any]], template: Path, work: Path | None = None, fetch=fetch_as_data) -> list[dict[str, Any]]:
    commit = checkout_commit(template)
    with tempfile.TemporaryDirectory(prefix="agentkeel-upgrade-") as scratch:
        return [plan_one(agent, template, Path(work or scratch), fetch, commit) for agent in agents]


# --- open: the key, on the artifact ---------------------------------------------------


def entry_errors(entry: Any, organisation: str, current_manifest: str | None, root: Path = ROOT) -> list[str]:
    """Why the keyed job will not open this entry; [] if nothing. The artifact is data from a job that
    read an agent repository: every bound the platform keeps is checked again here, on `main`'s code."""
    from src.validate.agent import NAME

    if not isinstance(entry, dict) or not isinstance(entry.get("files"), dict) or not entry.get("files"):
        return ["not an entry with files"]
    repository = str(entry.get("repository"))
    owner, _, name = repository.partition("/")
    errors = []
    if owner != organisation or not re.fullmatch(r"[A-Za-z0-9._-]+", name) or name == TEMPLATE_REPOSITORY:
        errors.append(f"{repository} is not an agent repository of {organisation}'s")
    if not isinstance(entry.get("name"), str) or not NAME.match(entry["name"]):
        errors.append(f"agent name {entry.get('name')!r} is not a name the platform deploys")
    if not re.fullmatch(r"[0-9a-f]{40}", str(entry.get("base"))):
        errors.append("base is not a commit")
    if not re.fullmatch(r"[0-9a-f]{40}", str(entry.get("template_commit"))):
        errors.append("the plan names no template commit, so its files cannot be held to the template")
    outside = sorted(set(entry["files"]) - set(PLATFORM_OWNED))
    if outside:
        errors.append(f"paths the platform does not own: {', '.join(outside)}")
    if not all(isinstance(content, str) for content in entry["files"].values()):
        errors.append("a file's content is not text")
    to = entry.get("to")
    done = None if commit_of(to, root) is None else subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit_of(to, root), "HEAD"], cwd=root, capture_output=True, check=False)  # type: ignore[list-item]
    if done is None or done.returncode != 0:
        errors.append(f"version {to!r} is not a commit of main's history")
    if entry.get("branch") != f"platform-upgrade/{to}":
        errors.append(f"branch {entry.get('branch')!r} is not platform-upgrade/{to}")
    if entry.get("kind") not in ("major", "minor"):
        errors.append(f"kind {entry.get('kind')!r} is neither major nor minor")
    refused = entry.get("refused")
    if not isinstance(refused, list) or not all(isinstance(r, str) and CHECK_NAME.fullmatch(r) for r in refused):
        errors.append("the checks that refused the default branch are not a list of check names")
    elif bool(refused) != (entry.get("kind") == "major"):
        errors.append(f"kind {entry.get('kind')!r} does not agree with {len(refused)} refusing checks")
    if "manifest.yaml" in entry["files"] and isinstance(entry["files"]["manifest.yaml"], str):
        try:
            before = yaml.safe_load(current_manifest or "")
            after = yaml.safe_load(entry["files"]["manifest.yaml"])
            if not isinstance(before, dict) or not isinstance(after, dict):
                errors.append("manifest.yaml, at the base or as proposed, is not a mapping")
            else:
                moved = sorted(k for k in set(before) | set(after) if k not in MANIFEST_FIELDS and before.get(k) != after.get(k))
                if moved:
                    errors.append(f"manifest.yaml: the proposal moves {', '.join(moved)}")
                if after.get("platform_version") != to:
                    errors.append(f"manifest.yaml: the proposal's platform_version is {after.get('platform_version')!r}, not {to!r}")
        except yaml.YAMLError:
            errors.append("manifest.yaml, at the base or as proposed, is not YAML")
    return errors


def template_head(organisation: str) -> str:
    """The template repository's default-branch head, as git's own protocol gives it: no token, no API."""
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    env.pop("GITHUB_TOKEN", None)
    url = f"https://github.com/{organisation}/{TEMPLATE_REPOSITORY}.git"
    done = subprocess.run(["git", "ls-remote", url, "HEAD"], capture_output=True, text=True, env=env, check=False)
    head = done.stdout.split()[0] if done.returncode == 0 and done.stdout.split() else ""
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise Refused(f"the template's default-branch head could not be read ({done.stderr.strip()[-200:] or 'no answer'})")
    return head


def read_template(organisation: str, into: Path) -> tuple[str, Path]:
    """The template's default-branch head, and its tree at that commit as data (`fetch_as_data`)."""
    from src.validate import agent as platform

    head = template_head(organisation)
    folder = fetch_as_data(f"{organisation}/{TEMPLATE_REPOSITORY}", head, into)
    if links := platform.links(folder):
        raise Refused(f"a symbolic link in the template ({links[0]}); nothing is read from it")
    return head, folder


def content_errors(entry: dict[str, Any], template: Path, platform_manifest: Any) -> list[str]:
    """Why the bytes this entry proposes are not the platform's; [] if they are (item 13l).

    `template` is the template repository's tree at the commit the entry names, fetched by the keyed job
    itself. `platform_manifest` is `main`'s own `agents/refagent/manifest.yaml`, whose `guardrail` is
    the one every agent from the template pins. The plan is not asked what either says."""
    at = str(entry.get("template_commit"))[:12]
    try:
        side = platform_side(template)
    except (Refused, OSError, yaml.YAMLError, ValueError) as exc:
        return [f"the template at {at} could not be read: {exc}"]
    errors = []
    if side["platform_version"] != entry.get("to"):
        errors.append(f"the template at {at} is at platform_version {side['platform_version']!r}, the plan says {entry.get('to')!r}")
    for name in COPIED:
        if name not in entry["files"]:
            continue
        source = template / name
        if not source.is_file():
            errors.append(f"{name}: the template at {at} has no such file")
            continue
        try:
            theirs = source.read_text(encoding="utf-8")
        except ValueError:  # not UTF-8: refused for this entry, never raised past the job's loop
            errors.append(f"{name}: the template's {name} at {at} is not UTF-8 text")
            continue
        if theirs != entry["files"][name]:
            errors.append(f"{name}: the proposal is not the template's {name} at {at}")
    if isinstance(entry["files"].get("manifest.yaml"), str):
        pinned = platform_manifest.get("guardrail") if isinstance(platform_manifest, dict) else None
        try:
            proposed = yaml.safe_load(entry["files"]["manifest.yaml"])
        except yaml.YAMLError:
            proposed = None
        guardrail = proposed.get("guardrail") if isinstance(proposed, dict) else None
        if not pinned or guardrail != pinned:
            errors.append(f"manifest.yaml: the proposal's guardrail {guardrail!r} is not the one main pins ({pinned!r})")
    return errors


def open_all(entries: list[Any], key: str, root: Path = ROOT, template_reader=read_template) -> list[dict[str, Any]]:
    """Open each entry that passes `entry_errors` and `content_errors`, each under a token minted for its
    repository alone."""
    from scripts import platform_check

    organisation, _platform_app = platform_check.identity()
    app_id = platform_check.load_grant()["agentkeel-upgrades"]["app_id"]
    wanted = [entry for entry in entries if isinstance(entry, dict) and entry.get("open")]
    with tempfile.TemporaryDirectory(prefix="agentkeel-template-") as scratch:
        # The template, read by this job itself, once, before any token: its head, and its tree as data.
        head, template, unread = None, None, "nothing to open"
        if wanted:
            try:
                head, template = template_reader(str(organisation), Path(scratch))
            except (Refused, OSError) as exc:
                unread = str(exc)
        platform_manifest = yaml.safe_load((root / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8"))
        return _open_each(wanted, key, str(organisation), app_id, head, template, unread, platform_manifest)


def _open_each(entries: list[dict[str, Any]], key: str, organisation: str, app_id: Any, head: str | None,
               template: Path | None, unread: str, platform_manifest: Any) -> list[dict[str, Any]]:  # fmt: skip
    from scripts import platform_check, platform_pr

    results = []
    for entry in entries:
        repository = str(entry.get("repository"))
        result: dict[str, Any] = {"repository": repository, "opened": False}
        try:
            # Checked once before any token, on what the artifact alone can show.
            if errors := [e for e in entry_errors(entry, str(organisation), None) if "manifest.yaml" not in e]:
                raise platform_pr.Refused("; ".join(errors))
            # Then the bytes, against the template this job fetched and main's own pin (item 13l).
            if template is None or head is None:
                raise platform_pr.Refused(f"the template could not be read as data ({unread}): nothing is opened")
            if entry["template_commit"] != head:
                raise platform_pr.Refused(f"the plan was made from the template at {entry['template_commit'][:12]}, and its "
                                          f"default branch is at {head[:12]}: the next run plans again")  # fmt: skip
            if errors := content_errors(entry, template, platform_manifest):
                raise platform_pr.Refused("; ".join(errors))
            with platform_check._As(platform_check.app_token(app_id, str(organisation), key, repository, "open")):
                default = platform_check.gh(f"/repos/{repository}")["default_branch"]
                manifest = platform_check.gh(f"/repos/{repository}/contents/manifest.yaml?ref={entry['base']}", raw=True)
                if errors := entry_errors(entry, str(organisation), manifest):
                    raise platform_pr.Refused("; ".join(errors))
                # The title and the body are written here, from the fields checked above and the manifest
                # this job read at the base: the artifact's own text is never posted as the App
                # (security-reviewer 4 on M07 PR 2).
                said = {"from": (yaml.safe_load(manifest) or {}).get("platform_version"), "to": entry["to"],
                        "kind": entry["kind"], "base": entry["base"], "refused": entry["refused"], "files": entry["files"]}  # fmt: skip
                result |= platform_pr.open_draft(
                    repository, default, entry["base"], entry["branch"], entry["files"],
                    title=f"Platform upgrade to {entry['to']} ({entry['kind']})", body=body_of(said),
                    message=f"Platform upgrade to {entry['to']} ({entry['kind']})")  # fmt: skip
                result["opened"] = True
        except (platform_pr.Refused, urllib.error.URLError, KeyError, TimeoutError, OSError) as exc:
            result["why"] = f"{type(exc).__name__}: {exc}"
        results.append(result)
        print(f"{repository}: {'opened #' + str(result.get('number')) if result['opened'] else 'not opened: ' + result['why']}")
    return results


# --- command line ------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="what", required=True)
    one = sub.add_parser("diff")
    one.add_argument("--agent", required=True, type=Path)
    one.add_argument("--platform", required=True, type=Path)
    two = sub.add_parser("plan")
    two.add_argument("--template", required=True, type=Path)
    two.add_argument("--agents", type=Path, help="platform_check.py deployable's output; read from GitHub if absent")
    two.add_argument("--out", required=True, type=Path)
    three = sub.add_parser("open")
    three.add_argument("--plan", required=True, type=Path)
    three.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    if args.what == "diff":
        try:
            changed = diff(args.agent, args.platform)
        except Refused as refusal:
            print(f"REFUSED: {refusal}", file=sys.stderr)
            return 3
        for path in sorted(changed):
            print(f"would change {path}")
        print(f"{len(changed)} platform-owned file(s) differ; nothing is opened from here")
        return 0

    from scripts import platform_check

    if args.what == "plan":
        organisation, app_id = platform_check.identity()
        if args.agents:
            agents = json.loads(args.agents.read_text(encoding="utf-8"))
        elif organisation and isinstance(app_id, int):
            agents = platform_check.deployable(organisation, app_id)
        else:
            agents = []
        entries = plan(agents, args.template)
        args.out.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
        for entry in entries:
            print(f"{entry['repository']}: {'open ' + entry['branch'] + ' (' + entry['kind'] + ')' if entry['open'] else entry['why']}")
        return 0

    key = os.environ.pop("AGENTKEEL_APP_PRIVATE_KEY", None)
    if not key:
        print("no AGENTKEEL_APP_PRIVATE_KEY: pull requests are opened in the platform-upgrades environment only")
        return 1
    try:
        results = open_all(json.loads(args.plan.read_text(encoding="utf-8")), key)
    except platform_check.NoGrant as refusal:
        print(f"REFUSED: {refusal}")
        return 1
    if args.out:
        args.out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
