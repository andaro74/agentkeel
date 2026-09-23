"""`validate`: the live `main` ruleset equals its export, and nobody bypasses it (SPEC/02 §6; open.md row 5).

Reads `infra/ruleset/main.json` (Security's export) and the live ruleset
from the API, `GET /repos/{owner}/{repo}/rulesets/{id}`, and compares the
fields that say what the ruleset does: `name`, `target`, `enforcement`,
`conditions`, `rules` and `bypass_actors`. Not `updated_at`, `node_id`,
`created_at`, `current_user_can_bypass` or `_links`, which say when and by
whom it was read (Security, M02 PR 2 ruling, Unsure H). Both must say
`bypass_actors: []`.

This is Door 3's second gate (SPEC/02 §5.1, S4 attempt 2): the owner who
adds themselves to `bypass_actors` on the live ruleset turns `checks` RED
on every branch until it is removed, and a required check removed from
the live ruleset differs from the export in the same way.

The endpoint answers without a token on a public repository (200 on
2026-09-22, `milestones/M02/runs/api_probes.yaml`), **but the answer
then carries `bypass_actors: null`**: GitHub shows the bypass list only
to a caller it can name. So the read is made with `GITHUB_TOKEN` when the
environment has one, else with `gh auth token` on a developer's machine,
and a live ruleset whose `bypass_actors` is null is an error naming the
token, never a pass and never "somebody can bypass". Whether a workflow's
`GITHUB_TOKEN` is shown the list is read on M02 PR 2's first run, not
assumed (Security, Unsure H). A ruleset that cannot be read is an error,
not a skip: a setting nobody can read is not known to be unchanged.
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
EXPORT = "infra/ruleset/main.json"
COMPARED = ("name", "target", "enforcement", "conditions", "rules", "bypass_actors")


def repository(root: Path) -> str | None:
    """`owner/repo`, from the environment in CI or from `origin` locally."""
    if slug := os.environ.get("GITHUB_REPOSITORY"):
        return slug
    done = subprocess.run(["git", "remote", "get-url", "origin"], cwd=root, capture_output=True, text=True, check=False)
    url = done.stdout.strip()
    for prefix in ("https://github.com/", "git@github.com:"):
        if url.startswith(prefix):
            return url.removeprefix(prefix).removesuffix(".git").rstrip("/")
    return None


def token() -> tuple[str | None, str]:
    """The token that reads the ruleset, and which it was.

    `RULESET_TOKEN` first: a fine-grained token with Administration: read on
    this repository, kept as a repository secret. Read by the call on M02
    PR 2's first run (35809406890): an Actions `GITHUB_TOKEN` answers 200
    and is **not** shown `bypass_actors`, so the compare cannot rest on it.
    Then `GITHUB_TOKEN`, which still spares the rate limit and reads the
    rest; then the gh CLI's token on a developer's machine, which is shown
    the list.
    """
    if value := os.environ.get("RULESET_TOKEN"):
        return value, "RULESET_TOKEN"
    if value := os.environ.get("GITHUB_TOKEN"):
        return value, "GITHUB_TOKEN"
    done = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=False)
    if done.returncode == 0 and done.stdout.strip():
        return done.stdout.strip(), "gh auth token"
    return None, "no token"


def fetch(repo: str, ruleset_id: int) -> tuple[dict[str, Any] | None, str]:
    request = urllib.request.Request(f"{API}/repos/{repo}/rulesets/{ruleset_id}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    value, which = token()
    if value:
        request.add_header("Authorization", f"Bearer {value}")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response), f"200 with {which}"
    except urllib.error.HTTPError as exc:
        return None, f"{exc.code} with {which}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def compare(export: dict[str, Any], live: dict[str, Any], status: str = "") -> list[str]:
    if live.get("bypass_actors") is None:
        return [
            (f"{EXPORT}: the live ruleset's bypass_actors is not shown to this caller ({status}); GitHub shows the "
             "bypass list only to a token it can name, so the compare needs one (Security, M02 PR 2 Unsure H)")
        ]  # fmt: skip
    errors = []
    for key in COMPARED:
        if export.get(key) != live.get(key):
            errors.append(
                f"{EXPORT}: {key} differs from the live ruleset. export: {json.dumps(export.get(key), sort_keys=True)}; "
                f"live: {json.dumps(live.get(key), sort_keys=True)}"
            )
    if export.get("bypass_actors") != []:
        errors.append(f"{EXPORT}: bypass_actors is {json.dumps(export.get('bypass_actors'))}, not []")
    if live.get("bypass_actors") != []:
        errors.append(f"the live ruleset's bypass_actors is {json.dumps(live.get('bypass_actors'))}, not []: somebody can bypass main")
    return errors


NO_TOKEN_FLAG = "AGENTKEEL_NO_RULESET_TOKEN"


def check(root: Path, *, fetcher=fetch) -> list[str]:
    # evals.yml's `checks` job carries no secret, so that a fork's pull
    # request can run it (BLOCK C); it sets this flag, and the compare is
    # not pretended to there: the line printed says it is skipped. The
    # compare runs in the `evals` job, which has the secret, on every
    # non-fork PR and on every push to main; what it watches is the live
    # ruleset, which no outsider can edit (Security, M02 PR 2 ruling, item 2).
    if os.environ.get(NO_TOKEN_FLAG, "").lower() == "true":
        print(f"     note: {EXPORT}: the live compare is skipped in this job, which carries no token that is shown the "
              "bypass list; it runs in the evals job on every non-fork PR and on main")  # fmt: skip
        return []
    path = root / EXPORT
    if not path.is_file():
        return [f"{EXPORT}: missing"]
    try:
        export = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{EXPORT}: not JSON: {exc}"]
    if not isinstance(export, dict) or not isinstance(export.get("id"), int):
        return [f"{EXPORT}: not a ruleset export with an integer id"]
    repo = repository(root)
    if repo is None:
        return [f"{EXPORT}: cannot tell which repository to read the live ruleset from (GITHUB_REPOSITORY or origin)"]
    live, status = fetcher(repo, export["id"])
    if live is None:
        return [f"{EXPORT}: the live ruleset {export['id']} on {repo} could not be read ({status}); unread is not unchanged"]
    return compare(export, live, status)
