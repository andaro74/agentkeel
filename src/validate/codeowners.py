"""`validate`: CODEOWNERS complete and single-owner over the tree, and its logins real (SPEC/02 §6).

Every tracked file matches an owner line; no file matches lines from two
seats (a file with two owners has none); every `.claude/agents/<name>.md`
is under the seat its own `seat:` front matter names (SPEC/00 §5, last
row); the seat names are SPEC/00 §5's seven, which are also the manifest
schema's `seats` keys; and each login is a real GitHub user, read from the
API (`GET /users/{login}`), with `GITHUB_TOKEN` when the environment has
one. A login that cannot be read is an error, not a skip: a table nobody
can check is not a table.

Cut-list item 4 of SPEC/02 §9 is the API half; it costs one request per
distinct login, which at M02 is one.
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from src.gates import CODEOWNERS, SEATS, Owners, canonical_seat, front_matter

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
AGENT_PROMPTS = ".claude/agents/"


def tracked(root: Path) -> list[str]:
    done = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True)
    return sorted(p for p in done.stdout.decode("utf-8").split("\0") if p)


def login_exists(login: str) -> tuple[bool, str]:
    """`GET /users/{login}` with the same token order as the ruleset read: GITHUB_TOKEN, then gh's.

    Unauthenticated, GitHub allows 60 calls an hour per address, and a day
    of local `make validate` runs spent them (403 on 2026-09-23); the
    status is reported with the token that was used.
    """
    from src.validate.ruleset import token

    request = urllib.request.Request(f"{API}/users/{login}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    value, which = token()
    if value:
        request.add_header("Authorization", f"Bearer {value}")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response).get("login", "").lower() == login.lower(), f"200 with {which}"
    except urllib.error.HTTPError as exc:
        return False, f"{exc.code} with {which}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, f"{type(exc).__name__}: {exc}"


def check(root: Path, *, lookup=login_exists) -> list[str]:
    path = root / CODEOWNERS
    if not path.is_file():
        return [f"{CODEOWNERS}: missing"]
    try:
        owners = Owners.parse(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [str(exc)]
    errors: list[str] = []
    for file in tracked(root):
        matched = owners.matching(file)
        if not matched:
            errors.append(f"{file}: matches no line of {CODEOWNERS}; a file no seat owns is deleted, not adopted (SPEC/00 section 5)")
            continue
        seats = sorted({line.seat for line in matched})
        if len(seats) > 1:
            where = ", ".join(f"line {line.number} ({line.seat})" for line in matched)
            errors.append(f"{file}: matches lines from {len(seats)} seats in {CODEOWNERS}: {where}")
        if file.startswith(AGENT_PROMPTS) and file.endswith(".md"):
            fm = front_matter((root / file).read_text(encoding="utf-8")) or {}
            own = canonical_seat(fm.get("seat"))
            if own is None:
                errors.append(f"{file}: front matter names no SPEC/00 section 5 seat")
            elif own != matched[-1].seat:
                errors.append(f"{file}: front matter says seat {own}, {CODEOWNERS} line {matched[-1].number} says {matched[-1].seat}")
    if missing := sorted(set(SEATS) - {line.seat for line in owners.lines}):
        errors.append(f"{CODEOWNERS}: no line for {missing}")
    for login in sorted(owners.logins()):
        real, status = lookup(login)
        if not real:
            errors.append(f"{CODEOWNERS}: @{login} is not a GitHub login the API answers for (GET /users/{login}: {status})")
    return errors
