"""A retirement: the pull request the platform opens, and the record of the runtime gone (SPEC/07 §1, §2, §6).

    python scripts/retire_agent.py plan --name NAME --out PLAN.json      # no secret: the pull request, as data
    python scripts/retire_agent.py plan --deprecating --out PLAN.json    # every agent whose pin is within 30 days of its end
    python scripts/retire_agent.py open --plan PLAN.json                 # agentkeel-upgrades' key: the draft
    python scripts/retire_agent.py invoke --arn ARN --out RESULT.json    # the deploy role: one call, after the deletion
    python scripts/retire_agent.py record --name NAME ... --out RETIRED.json   # what is put once in the audit bucket

Until M07 PR 2 nothing retired an agent: the manifest's `rollout` took one
value, no job removed a runtime, and an archived repository was skipped by
the platform check while its runtime kept answering (seed S2).

**A retirement arrives as a pull request** (BLOCK 1). `plan` and `open` are
the two halves, as `scripts/platform_upgrade.py` has them: `plan` holds no
secret, reads the agent's manifest at the head the platform's App passed and
writes the one change, `rollout: retired`; `open` holds the key of the App
that opens pull requests, checks the entry again on `main`'s code (one file,
one field, an agent repository of the organisation's, never `refagent`) and
opens one draft through `scripts/platform_pr.py`. The agent's seats merge it.

Triggers: the owner's dispatch for one agent, which is the seeded one; and a
pin whose `deprecated_after` is 30 days away or fewer. The third SPEC/07 §1
names, a registry row idle for 90 days, is not built: nothing writes
`idle_since`, and no seed can wait (SPEC/07 §8).

**Then the deploy path retires instead of deploying** (`deploy.yml`'s
`retire-agent` job): at a merged head the App passed whose manifest says
`rollout: retired`, the agent's stack is updated to the construct's
template without the runtime (`infra/construct/`, no new IAM), and then:

- `invoke`: one invocation of the runtime's ARN, after the deletion, written
  raw: answered or not, and the error's code. Only
  `ResourceNotFoundException` says the runtime is gone; a refusal for access
  does not, and `build.f7_2` reads it that way. It exits 0 on that error
  and 5 on anything else, an answer included: the job then fails, nothing
  is recorded and the row stays open, so the next run asks again
  (platform-architect B1 on M07 PR 2: CloudFormation deletes a removed
  resource after the update has succeeded, and a delete that fails there
  leaves the runtime answering under an update that exited 0).
- `record`: the retirement as one JSON document, put once under
  `envelopes/agents/<name>/retired.json` in the security account's audit
  bucket, because the registry row is in the agent account and is not
  write-once (rulings/pr2-security.md item 11). It refuses an invocation
  that does not say the runtime is gone: a record put once must not be
  the record of a runtime that still answered.

Nothing from an agent repository is imported or run. `refagent` is refused
by name at every step.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import platform_upgrade  # noqa: E402

BRANCH = "platform-retire"
PLATFORM_AGENT = "refagent"
DEPRECATION_DAYS = 30  # as `validate`'s lifecycle check (src/validate/lifecycle.py)
REGION = "us-west-2"
GONE = "ResourceNotFoundException"


DISPATCHED = "the owner dispatched the retire workflow for this agent"


class Refused(Exception):
    """Not a retirement the platform opens."""


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def body_of(entry: dict[str, Any]) -> str:
    return (
        f"This draft retires the agent `{entry['name']}`. It changes one line: `rollout: retired` in "
        f"`manifest.yaml`.\n\n**Why:** {entry['why']}.\n\n"
        "**What merging it does.** At the next deploy run the platform removes this agent's runtime and deploys "
        "nothing in its place. The agent stops answering. Its registry row stays and says when it was retired. "
        "Its answer records and its signed bundle stay in the audit bucket. Its key, its table and its logs are "
        "kept. **It is one-way: nothing restores the runtime.**\n\n"
        "**What to do.** If the agent should be retired, mark this ready and merge it when the platform check "
        "passes. If it should not, close it: the platform does not open it again.\n\n"
        "Opened by the platform (`agentkeel-upgrades`) from `agentkeel`'s `main`"
        + (f", run {entry['run']}" if entry.get("run") else "") + ". Nobody needs to edit it.\n\n"
        "What this is: `docs/developer/upgrade.md` in `andaro74/agentkeel`."
    )


def plan_one(agent: dict[str, Any], why: str, read_manifest) -> dict[str, Any]:
    """One agent's retirement pull request, or why none. `read_manifest(repository, commit)` gives the text."""
    repository, commit, name = agent["repository"], agent["commit"], agent.get("name")
    out: dict[str, Any] = {"repository": repository, "name": name, "base": commit, "open": False}
    try:
        if name == PLATFORM_AGENT:
            raise Refused(f"{PLATFORM_AGENT} is the platform's own agent and is never retired by this path")
        text = read_manifest(repository, commit)
        manifest = yaml.safe_load(text)
        if not isinstance(manifest, dict) or manifest.get("name") != name:
            raise Refused("manifest.yaml at the passed head does not name this agent")
        if manifest.get("rollout") == "retired":
            raise Refused("already says rollout: retired")
        out |= {"open": True, "why": why, "files": {"manifest.yaml": platform_upgrade.set_fields(text, {"rollout": "retired"})},
                "branch": BRANCH, "title": f"Retire {name}", "run": os.environ.get("GITHUB_RUN_ID")}  # fmt: skip
        out["body"] = body_of(out)
    except (Refused, platform_upgrade.Refused, urllib.error.URLError, yaml.YAMLError, OSError, KeyError) as exc:
        out["why"] = f"{type(exc).__name__}: {exc}" if not isinstance(exc, Refused) else str(exc)
    return out


def deprecating(manifest: Any, today: date) -> str | None:
    """Why this agent is due to retire for its pin, or None: `deprecated_after` 30 days away or fewer."""
    stated = manifest.get("deprecated_after") if isinstance(manifest, dict) else None
    if isinstance(stated, date):  # YAML reads an unquoted date as one
        end = stated
    elif isinstance(stated, str):
        try:
            end = date.fromisoformat(stated)
        except ValueError:
            return None
    else:
        return None
    if end - today > timedelta(days=DEPRECATION_DAYS):
        return None
    return f"its model pin's `deprecated_after` is {stated}, {DEPRECATION_DAYS} days away or fewer, and it has not moved to another"


def plan(agents: list[dict[str, Any]], name: str | None, read_manifest, today: date | None = None) -> list[dict[str, Any]]:
    """Dispatched for `name`: that agent's entry, or a refusal that says why. Otherwise each agent due for its pin."""
    live = [a for a in agents if a.get("rollout") != "retired"]
    if name is not None:
        found = [a for a in live if a.get("name") == name]
        if not found:
            return [{"repository": None, "name": name, "base": None, "open": False,
                     "why": f"no agent named {name} has a head the platform's App passed, or it is already retired"}]  # fmt: skip
        return [plan_one(found[0], DISPATCHED, read_manifest)]
    entries = []
    for agent in live:
        try:
            why = deprecating(yaml.safe_load(read_manifest(agent["repository"], agent["commit"])), today or date.today())
        except (urllib.error.URLError, yaml.YAMLError, OSError):
            why = None
        if why:
            entries.append(plan_one(agent, why, read_manifest))
    return entries


def entry_errors(entry: Any, organisation: str, current_manifest: str | None) -> list[str]:
    """Why the keyed job will not open this entry; [] if nothing. One file, one field, one branch."""
    from src.validate.agent import NAME

    if not isinstance(entry, dict) or not isinstance(entry.get("files"), dict):
        return ["not an entry with files"]
    repository = str(entry.get("repository"))
    owner, _, repo = repository.partition("/")
    errors = []
    if owner != organisation or not re.fullmatch(r"[A-Za-z0-9._-]+", repo) or repo == platform_upgrade.TEMPLATE_REPOSITORY:
        errors.append(f"{repository} is not an agent repository of {organisation}'s")
    name = entry.get("name")
    if not isinstance(name, str) or not NAME.match(name) or name == PLATFORM_AGENT:
        errors.append(f"agent name {name!r} is not one the platform retires")
    if sorted(entry["files"]) != ["manifest.yaml"] or not isinstance(entry["files"].get("manifest.yaml"), str):
        errors.append(f"a retirement changes manifest.yaml and nothing else, not {sorted(entry['files'])}")
        return errors
    if entry.get("branch") != BRANCH:
        errors.append(f"branch {entry.get('branch')!r} is not {BRANCH}")
    if current_manifest is not None:
        try:
            before, after = yaml.safe_load(current_manifest), yaml.safe_load(entry["files"]["manifest.yaml"])
        except yaml.YAMLError:
            return [*errors, "manifest.yaml, at the base or as proposed, is not YAML"]
        if not isinstance(before, dict) or not isinstance(after, dict):
            return [*errors, "manifest.yaml, at the base or as proposed, is not a mapping"]
        moved = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        if moved != ["rollout"] or after.get("rollout") != "retired":
            errors.append(f"manifest.yaml: a retirement sets rollout to retired and nothing else; this moves {', '.join(moved) or 'nothing'}")
        if before.get("name") != name:
            errors.append("manifest.yaml at the base does not name this agent")
    return errors


def open_all(entries: list[Any], key: str) -> list[dict[str, Any]]:
    from scripts import platform_check, platform_pr

    organisation, _platform_app = platform_check.identity()
    app_id = platform_check.load_grant()["agentkeel-upgrades"]["app_id"]
    results = []
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("open"):
            continue
        repository = str(entry.get("repository"))
        result: dict[str, Any] = {"repository": repository, "opened": False}
        try:
            if errors := entry_errors(entry, str(organisation), None):
                raise platform_pr.Refused("; ".join(errors))
            with platform_check._As(platform_check.app_token(app_id, str(organisation), key, repository, "open")):
                default = platform_check.gh(f"/repos/{repository}")["default_branch"]
                manifest = platform_check.gh(f"/repos/{repository}/contents/manifest.yaml?ref={entry['base']}", raw=True)
                if errors := entry_errors(entry, str(organisation), manifest):
                    raise platform_pr.Refused("; ".join(errors))
                # The title and the body are written here, from the name checked above and the manifest
                # this job read at the base: the artifact's own text is never posted as the App
                # (security-reviewer 4 on M07 PR 2). Why: the pin's date when the manifest gives one that
                # is due, and the dispatch otherwise.
                why = deprecating(yaml.safe_load(manifest), date.today()) or DISPATCHED
                run = os.environ.get("GITHUB_RUN_ID", "")
                said = {"name": entry["name"], "why": why, "run": run if run.isdigit() else None}
                result |= platform_pr.open_draft(repository, default, entry["base"], BRANCH, entry["files"],
                                                 title=f"Retire {entry['name']}", body=body_of(said),
                                                 message=f"Retire {entry['name']}: rollout: retired")  # fmt: skip
                result["opened"] = True
        except (platform_pr.Refused, urllib.error.URLError, KeyError, TimeoutError, OSError) as exc:
            result["why"] = f"{type(exc).__name__}: {exc}"
        results.append(result)
        print(f"{repository}: {'opened #' + str(result.get('number')) if result['opened'] else 'not opened: ' + result['why']}")
    return results


# --- after the deletion ---------------------------------------------------------------------


def invoke(arn: str, client: Any = None) -> dict[str, Any]:
    """One invocation of `arn`, and what came back, raw. Never raises: an error is the result."""
    result: dict[str, Any] = {"arn": arn, "at": now(), "answered": False, "error": None, "message": None}
    try:
        if client is None:
            import boto3

            client = boto3.client("bedrock-agentcore", region_name=REGION)
        response = client.invoke_agent_runtime(agentRuntimeArn=arn, payload=json.dumps({"question": "Are you there?"}).encode("utf-8"))
        body = response["response"].read() if hasattr(response["response"], "read") else response["response"]
        result |= {"answered": True, "bytes": len(body) if body is not None else 0}
    except Exception as exc:  # noqa: BLE001 - whatever the call raised is the observation
        code = getattr(exc, "response", {}).get("Error", {}).get("Code") if hasattr(exc, "response") else None
        result |= {"error": code or type(exc).__name__, "message": str(exc)[:300]}
    return result


def record(name: str, repository: str, commit: str, arn: str, run_url: str, invocation: dict[str, Any]) -> dict[str, Any]:
    """The retirement as the job saw it. A record, not a ruling: `build.f7_2` reads CloudTrail, the
    bucket and the registry against it."""
    if name == PLATFORM_AGENT:
        raise Refused(f"{PLATFORM_AGENT} is never retired by this path")
    if not isinstance(invocation, dict) or invocation.get("answered") is not False or invocation.get("error") != GONE:
        raise Refused(f"the invocation does not say the runtime is gone ({GONE}): nothing is recorded as retired")
    if invocation.get("arn") != arn:
        raise Refused("the invocation is of another ARN: nothing is recorded as retired")
    return {"what": "agent retired", "agent": name, "repository": repository, "commit": commit, "runtime_arn": arn,
            "recorded_at": now(), "run_url": run_url, "invocation": invocation,
            "kept": ["the stack", "the agent's role", "its key and alias", "its rights table", "its image repository",
                     "its log group", "its registry row", "its answer records and its signed bundle"]}  # fmt: skip


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="what", required=True)
    one = sub.add_parser("plan")
    one.add_argument("--name")
    one.add_argument("--deprecating", action="store_true")
    one.add_argument("--agents", type=Path, help="platform_check.py deployable's output; read from GitHub if absent")
    one.add_argument("--out", required=True, type=Path)
    two = sub.add_parser("open")
    two.add_argument("--plan", required=True, type=Path)
    three = sub.add_parser("invoke")
    three.add_argument("--arn", required=True)
    three.add_argument("--out", required=True, type=Path)
    four = sub.add_parser("record")
    for flag in ("--name", "--repository", "--commit", "--arn", "--run-url"):
        four.add_argument(flag, required=True)
    four.add_argument("--invocation", required=True, type=Path)
    four.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    if args.what == "invoke":
        result = invoke(args.arn)
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        gone = result["error"] == GONE
        print(f"{args.arn}: {'answered' if result['answered'] else 'refused: ' + str(result['error'])}"
              f"{'' if gone or result['answered'] else ' (not the deletion: ' + GONE + ' is)'}")  # fmt: skip
        return 0 if gone else 5
    if args.what == "record":
        try:
            document = record(args.name, args.repository, args.commit, args.arn, args.run_url,
                              json.loads(args.invocation.read_text(encoding="utf-8")))  # fmt: skip
        except Refused as refusal:
            print(f"REFUSED: {refusal}", file=sys.stderr)
            return 3
        args.out.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        return 0

    from scripts import platform_check
    from src.validate.agent import NAME

    if args.what == "plan":
        if bool(args.name) == bool(args.deprecating):
            print("plan takes --name NAME or --deprecating, one of them", file=sys.stderr)
            return 2
        if args.name and (not NAME.match(args.name) or args.name == PLATFORM_AGENT):
            print(f"REFUSED: {args.name!r} is not an agent the platform retires", file=sys.stderr)
            args.out.write_text("[]\n", encoding="utf-8")
            return 3
        organisation, app_id = platform_check.identity()
        if args.agents:
            agents = json.loads(args.agents.read_text(encoding="utf-8"))
        elif organisation and isinstance(app_id, int):
            agents = platform_check.deployable(organisation, app_id)
        else:
            agents = []
        entries = plan(agents, args.name, lambda repository, commit: platform_check.gh(
            f"/repos/{repository}/contents/manifest.yaml?ref={commit}", raw=True))  # fmt: skip
        args.out.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
        for entry in entries:
            print(f"{entry['repository'] or entry['name']}: {'open ' + BRANCH if entry['open'] else entry['why']}")
        return 0

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
