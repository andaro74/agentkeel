"""Observe one check on one pull request and write what GitHub says (P5).

This is an instrument. It reads the pointer file, asks the GitHub API, and
writes a raw observation. It decides nothing; src/verdict/build.py reads the
observation into `checks`.

    python scripts/observe_pr_check.py milestones/M00/runs/f0_3.yaml --out f0_3.json

Pointer file: `pr` (number), `check` (check-run name), `base` (branch).
Environment: GITHUB_REPOSITORY, GITHUB_TOKEN (optional on a public repo).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")


def get(path: str) -> Any:
    request = urllib.request.Request(f"{API}{path}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token := os.environ.get("GITHUB_TOKEN"):
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def required_on(repo: str, base: str, check: str) -> bool | None:
    """Is `check` a required status check on `base`? None if neither source could be read."""
    answers: list[bool] = []
    try:
        rules = get(f"/repos/{repo}/rules/branches/{base}")
        answers.append(
            any(
                status.get("context") == check
                for rule in rules
                if rule.get("type") == "required_status_checks"
                for status in rule.get("parameters", {}).get(
                    "required_status_checks", []
                )
            )
        )
    except urllib.error.HTTPError:
        pass
    try:
        protection = get(f"/repos/{repo}/branches/{base}").get("protection")
        if protection is not None:
            required = protection.get("required_status_checks") or {}
            answers.append(
                protection.get("enabled", False)
                and required.get("enforcement_level", "off") != "off"
                and check in required.get("contexts", [])
            )
    except urllib.error.HTTPError:
        pass
    return any(answers) if answers else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pointer", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    pointer = yaml.safe_load(args.pointer.read_text(encoding="utf-8"))
    repo = os.environ["GITHUB_REPOSITORY"]
    number, check, base = int(pointer["pr"]), str(pointer["check"]), str(pointer["base"])

    pull = get(f"/repos/{repo}/pulls/{number}")
    head = pull["head"]["sha"]
    runs = get(f"/repos/{repo}/commits/{head}/check-runs?check_name={check}")[
        "check_runs"
    ]
    latest = max(runs, key=lambda run: run["id"]) if runs else None

    observation = {
        "what": "raw observation of one check run on one pull request; decides nothing",
        "repo": repo,
        "pr": number,
        "pr_url": pull["html_url"],
        "state": pull["state"],
        "merged": pull["merged"],
        "base": pull["base"]["ref"],
        "head_sha": head,
        "check": check,
        "check_run": None
        if latest is None
        else {
            "status": latest["status"],
            "conclusion": latest["conclusion"],
            "html_url": latest["html_url"],
        },
        "required_on_base": required_on(repo, base, check),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(observation, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(observation, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
