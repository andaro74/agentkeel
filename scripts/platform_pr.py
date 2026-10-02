"""One draft pull request, opened by the platform as `agentkeel-upgrades` (SPEC/07 §1, §6; M07 PR 2).

An upgrade "arrives as a pull request the platform opened": a draft, carrying
the change and nothing else, which no person wrote. Three callers open one,
each from a keyed job on `main` that runs `agentkeel`'s code on an artifact
of data: `scripts/platform_upgrade.py` (a platform bump),
`scripts/retire_agent.py` (a retirement) and `scripts/model_watch.py` (a pin
move). This is the one place that does it, so the three cannot differ in
what they are able to write.

What it holds: a token minted for one repository and the `open` permission
set (`contents: write`, `pull_requests: write`, `metadata: read`;
`scripts/platform_check.py` `PERMISSION_SETS`). It cannot post a check, read
or change a ruleset, or touch a workflow file: the App holds no `workflows`
permission, and a path under `.github/` is refused here before any request.
It cannot merge into a default branch whose ruleset requires a check it
cannot post.

**One pull request per branch name, ever.** The branch name is fixed by what
the pull request is for (`platform-upgrade/<version>`, `platform-retire`,
`model-watch/<role>`). If that branch exists, or any pull request was ever
opened from it, open or closed or merged, nothing is opened: a revert that
puts an agent back behind does not get the same upgrade a second time, and a
closed pull request is a seat's answer.
"""

from __future__ import annotations

import re
import urllib.error
import urllib.parse
from typing import Any

from scripts import platform_check

REFUSED_PREFIXES = (".github/",)  # never a workflow, in any repository (F7.1)
BRANCH = re.compile(r"^(platform-upgrade|platform-retire|model-watch)(/[a-z0-9][a-z0-9._-]{0,60})?$")


class Refused(Exception):
    """The platform will not open this pull request."""


def gh(path: str, **kwargs: Any) -> Any:
    return platform_check.gh(path, **kwargs)


def already(repository: str, branch: str) -> str | None:
    """Why nothing is opened for `branch`, or None: the branch is there, or a pull request ever came from it."""
    owner = repository.split("/")[0]
    try:
        gh(f"/repos/{repository}/git/ref/heads/{urllib.parse.quote(branch)}")
        return f"the branch {branch} exists"
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
    pulls = gh(f"/repos/{repository}/pulls?state=all&head={owner}:{urllib.parse.quote(branch)}&per_page=100")
    if pulls:
        return f"pull request #{pulls[0]['number']} was opened from {branch} ({pulls[0]['state']})"
    return None


def open_draft(repository: str, base_branch: str, base_sha: str, branch: str, files: dict[str, str], *,
               title: str, body: str, message: str) -> dict[str, Any]:  # fmt: skip
    """One commit on a new branch from `base_sha`, and a draft pull request for it into `base_branch`.

    The caller's GITHUB_TOKEN is the `open` token for this repository. Refuses a workflow path, an
    empty change, a branch name outside the three kinds, and a base that is no longer the default
    branch's head (the change was computed against another tree)."""
    if not BRANCH.match(branch):
        raise Refused(f"{branch!r} is not a branch the platform opens a pull request from")
    if not files:
        raise Refused("nothing to change: no pull request is opened for an empty diff")
    for path in files:
        if path.startswith(REFUSED_PREFIXES) or path.startswith("/") or ".." in path.split("/"):
            raise Refused(f"{path}: the platform never writes this path in a pull request")
    head = gh(f"/repos/{repository}/git/ref/heads/{urllib.parse.quote(base_branch)}")["object"]["sha"]
    if head != base_sha:
        raise Refused(f"{repository}@{base_branch} is at {head[:12]}, the change was computed at {base_sha[:12]}: "
                      "the next run computes it again")  # fmt: skip
    if reason := already(repository, branch):
        raise Refused(f"{repository}: {reason}; nothing is opened twice")
    tree = gh(f"/repos/{repository}/git/trees", method="POST", body={
        "base_tree": gh(f"/repos/{repository}/git/commits/{base_sha}")["tree"]["sha"],
        "tree": [{"path": path, "mode": "100644", "type": "blob", "content": content} for path, content in sorted(files.items())],
    })  # fmt: skip
    commit = gh(f"/repos/{repository}/git/commits", method="POST",
                body={"message": message, "tree": tree["sha"], "parents": [base_sha]})  # fmt: skip
    gh(f"/repos/{repository}/git/refs", method="POST", body={"ref": f"refs/heads/{branch}", "sha": commit["sha"]})
    pull = gh(f"/repos/{repository}/pulls", method="POST",
              body={"title": title, "head": branch, "base": base_branch, "body": body, "draft": True})  # fmt: skip
    return {"repository": repository, "number": pull["number"], "url": pull.get("html_url"), "head": commit["sha"],
            "branch": branch, "files": sorted(files)}  # fmt: skip


def add_commit(repository: str, branch: str, files: dict[str, str], message: str) -> str:
    """A second commit on a branch the platform opened: a drafted ruling file that names the pull
    request's own number, which exists only once the pull request does (`model_watch`)."""
    for path in files:
        if path.startswith(REFUSED_PREFIXES) or path.startswith("/") or ".." in path.split("/"):
            raise Refused(f"{path}: the platform never writes this path in a pull request")
    ref = f"/repos/{repository}/git/refs/heads/{urllib.parse.quote(branch)}"
    parent = gh(f"/repos/{repository}/git/ref/heads/{urllib.parse.quote(branch)}")["object"]["sha"]
    tree = gh(f"/repos/{repository}/git/trees", method="POST", body={
        "base_tree": gh(f"/repos/{repository}/git/commits/{parent}")["tree"]["sha"],
        "tree": [{"path": path, "mode": "100644", "type": "blob", "content": content} for path, content in sorted(files.items())],
    })  # fmt: skip
    commit = gh(f"/repos/{repository}/git/commits", method="POST",
                body={"message": message, "tree": tree["sha"], "parents": [parent]})  # fmt: skip
    gh(ref, method="PATCH", body={"sha": commit["sha"], "force": False})
    return commit["sha"]
