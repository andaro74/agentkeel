"""`validate`: every agent's seats assigned, each to a GitHub login with access (SPEC/06 §2, S1a's reader).

SPEC/00 R1 listed "seats assigned to real groups" among `validate`'s checks
from M01, and nothing ever read a seat (SPEC/06 §3.3, NOTE 20). Amended at
M06 PR 1: a seat is a GitHub login. Here, for every `agents/*/manifest.yaml`:
all seven of SPEC/00 §5's seats are named, and each is a login that has
access to the repository the manifest is in. Null, empty, a missing seat, or
a login GitHub does not answer for is unassigned, and refused with the
manifest's path.

Access is read from GitHub, as M02's CODEOWNERS logins are (`codeowners.py`):
the repository's owner has it (`GET /repos/{repo}`, public), anyone else is
asked of the collaborators endpoint (`GET /repos/{repo}/collaborators/{login}`,
204 or 404), which needs a token with push access. A lookup that cannot be
made is an error, not a skip: a seat nobody can check is not assigned. Under
R1 every seat is the author, who owns `agentkeel` and the organisation, so
CI reaches the answer with the token it already has.

The repository is `AGENTKEEL_SEAT_REPOSITORY`, else `GITHUB_REPOSITORY`, else
`andaro74/agentkeel`. The platform check sets it to the agent repository it
evaluates (`src/validate/agent.py`).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable
from functools import cache
from pathlib import Path

import yaml

from src.gates import SEATS

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
DEFAULT_REPOSITORY = "andaro74/agentkeel"
SLUGS = tuple(SEATS.values())  # the manifest's seat keys, SPEC/00 §5's seven


def repository() -> str:
    return os.environ.get("AGENTKEEL_SEAT_REPOSITORY") or os.environ.get("GITHUB_REPOSITORY") or DEFAULT_REPOSITORY


def _get(path: str) -> tuple[int, dict | None, str]:
    """(status, body or None, which token) for `GET {API}{path}`."""
    from src.validate.ruleset import token

    request = urllib.request.Request(f"{API}{path}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    value, which = token()
    if value:
        request.add_header("Authorization", f"Bearer {value}")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read()
            return response.status, (json.loads(raw) if raw else None), which
    except urllib.error.HTTPError as exc:
        return exc.code, None, which


@cache
def login_has_access(login: str) -> tuple[bool, str]:
    """True when `login` owns the repository or GitHub says it is a collaborator on it."""
    repo = repository()
    try:
        status, body, which = _get(f"/repos/{repo}")
        if status != 200 or body is None:
            return False, f"GET /repos/{repo}: {status} with {which}"
        if (body.get("owner") or {}).get("login", "").lower() == login.lower():
            return True, f"owner of {repo}"
        status, _, which = _get(f"/repos/{repo}/collaborators/{login}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    if status == 204:
        return True, f"collaborator on {repo}"
    if status == 404:
        return False, f"not a collaborator on {repo} (404 with {which})"
    return False, f"GET /repos/{repo}/collaborators/{login}: {status} with {which}, so access is unread"


def manifests(root: Path) -> list[Path]:
    return sorted((root / "agents").glob("*/manifest.yaml"))


def check(root: Path, *, lookup: Callable[[str], tuple[bool, str]] = login_has_access) -> list[str]:
    errors: list[str] = []
    for path in manifests(root):
        rel = path.relative_to(root).as_posix()
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: not YAML, so its seats are unread ({exc.__class__.__name__})")
            continue
        seats = doc.get("seats") if isinstance(doc, dict) else None
        if not isinstance(seats, dict):
            errors.append(f"{rel}: no `seats`: all seven are unassigned (SPEC/06 section 2)")
            continue
        for slug in SLUGS:
            login = seats.get(slug)
            if not isinstance(login, str) or not login.strip():
                errors.append(f"{rel}: seat {slug} is {login!r}: unassigned (SPEC/06 section 2)")
                continue
            real, status = lookup(login.strip())
            if not real:
                errors.append(f"{rel}: seat {slug} is {login}, not a login with access ({status})")
    return errors
