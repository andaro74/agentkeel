"""The platform check's two halves and the deploy's list, for `.github/workflows/` on `main` (SPEC/06 §6, R2, R3).

    python scripts/platform_check.py find --out heads.json            # no secret: what to evaluate
    python scripts/platform_check.py post --results DIR               # the App's token: seats, ruleset, the check
    python scripts/platform_check.py deployable --out merged.json     # no secret: what deploy.yml may deploy

Nothing comes from an agent repository but what GitHub's API says about
it. The organisation and the App are `infra/platform_identity.json`'s; while
either is null every subcommand writes an empty list and says so, and no
check is posted (the ruleset export's `integration_id` must equal the App's
id, `tests/test_m06_readers.py`).

- `find`: every open pull request's head, and every default-branch head, in
  the organisation's repositories, that has no `platform-check` run from the
  App. The default-branch head is the merge commit a merge makes, which no
  pull request's head is; `deployable` deploys only a head the App passed
  (security-reviewer F1 on PR 2). At most `LIMIT` per run; the next run
  takes the rest.
- `post`: for each result `src/validate/agent.py evaluate` wrote, the seats'
  access to that repository (deferred from the evaluating job, which holds
  no token that may ask an organisation repository about its
  collaborators), then that the repository is public (GitHub Free enforces
  a ruleset nowhere else), then the repository's live rulesets against
  `infra/ruleset/agent.json`, then one check run on the head that was
  evaluated, success only when every list is empty. Run with the App's
  installation token as `GITHUB_TOKEN`.
- `deployable`: every public repository's default-branch head that carries a
  successful `platform-check` run from the App, with the agent name its
  manifest holds there. `deploy.yml` reads the registry to skip what is
  already deployed and to refuse a name another repository holds.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
IDENTITY = ROOT / "infra" / "platform_identity.json"
CHECK = "platform-check"
LIMIT = 20
SEAT_CHECK = "seats assigned, each a login that administers the repository"
# GitHub Free enforces a repository's ruleset only while it is public (SPEC/06 section 2): a private agent
# repository's required check binds nothing, so the App refuses it and deploy.yml does not deploy it
# (security-reviewer F1 on the post-review delta of PR 2).
PUBLIC_CHECK = "the repository is public, where its ruleset is enforced"


def identity() -> tuple[str | None, int | None]:
    doc = json.loads(IDENTITY.read_text(encoding="utf-8"))
    return doc.get("organisation"), doc.get("platform_app_id")


def gh(path: str, *, method: str = "GET", body: Any = None, raw: bool = False) -> Any:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(path if path.startswith("http") else f"{API}{path}", data=data, method=method)
    request.add_header("Accept", "application/vnd.github.raw" if raw else "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token := os.environ.get("GITHUB_TOKEN"):
        request.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read()
    return payload.decode("utf-8") if raw else (json.loads(payload) if payload else None)


def repositories(org: str) -> list[dict[str, Any]]:
    """The organisation's repositories that can hold an agent: not archived, not the template itself."""
    return [r for r in gh(f"/orgs/{org}/repos?per_page=100&type=all")
            if not r.get("archived") and not r.get("is_template")]  # fmt: skip


def app_runs(repository: str, sha: str, app_id: int) -> list[dict[str, Any]]:
    found = gh(f"/repos/{repository}/commits/{sha}/check-runs?check_name={CHECK}&app_id={app_id}&per_page=100")
    return [r for r in found.get("check_runs") or [] if (r.get("app") or {}).get("id") == app_id]


def find(org: str, app_id: int) -> list[dict[str, Any]]:
    heads: list[dict[str, Any]] = []
    for repo in repositories(org):
        name = repo["full_name"]
        branch = gh(f"/repos/{name}/branches/{repo['default_branch']}")
        candidates = [(0, branch["commit"]["sha"])]
        candidates += [(pull["number"], pull["head"]["sha"]) for pull in gh(f"/repos/{name}/pulls?state=open&per_page=100")]
        for number, head in candidates:
            if any(h["repository"] == name and h["head"] == head for h in heads):
                continue
            if not app_runs(name, head, app_id):
                heads.append({"repository": name, "number": number, "head": head})
            if len(heads) >= LIMIT:
                return heads
    return heads


def live_rulesets(repository: str) -> list[dict[str, Any]]:
    listed = gh(f"/repos/{repository}/rulesets?includes_parents=false&per_page=100") or []
    return [gh(f"/repos/{repository}/rulesets/{r['id']}") for r in listed]


# The one table of what a token may be minted for (M07 PR 2; milestones/M07/rulings/pr2-security.md, item 5,
# ruled 2026-10-02; S0's reader). A token is minted for one repository and one of these sets, by name; a set
# that is not here cannot be minted, and no call mints the installation's whole grant. Each set belongs to
# one App, whose key is in one environment (item 2): the key that can post the check cannot open a pull
# request, and the key that can open one cannot post the check.
PERMISSION_SETS: dict[str, dict[str, str]] = {
    # agentkeel-platform (5144253), platform-check.yml's `post` job. Two tokens, never one (item 5):
    # GitHub shows a ruleset's bypass_actors only to a caller that can administer it (M06's finding,
    # milestones/M07/open.md row 2), so the ruleset is read with `rulesets` and that token is revoked
    # after the read; the seats, the visibility and the check run are `check`'s, which cannot administer.
    "rulesets": {"administration": "write", "metadata": "read"},
    "check": {"checks": "write", "contents": "read", "metadata": "read", "pull_requests": "read"},
    # agentkeel-upgrades: platform-upgrade.yml, the retire job's pull request, model-watch.yml.
    "open": {"contents": "write", "pull_requests": "write", "metadata": "read"},
    # agentkeel-observer: the scheduled observer on main. It writes nothing.
    "observe": {"administration": "read", "checks": "read", "contents": "read", "metadata": "read",
                "pull_requests": "read"},
}  # fmt: skip


def app_jwt(app_id: int, private_key_pem: str) -> str:
    """A JWT the App's key signs (RS256, ten minutes). It names the App and nothing else."""
    import base64
    import time

    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    def b64(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    now = int(time.time())
    head = b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    body = b64(json.dumps({"iat": now - 60, "exp": now + 540, "iss": str(app_id)}).encode())
    key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    signature = b64(key.sign(f"{head}.{body}".encode(), padding.PKCS1v15(), hashes.SHA256()))  # type: ignore[union-attr]
    return f"{head}.{body}.{signature}"


class _As:
    """`GITHUB_TOKEN` set to one credential for the block, and put back after it: it never outlives the call."""

    def __init__(self, token: str) -> None:
        self.token = token

    def __enter__(self) -> None:
        self.saved = os.environ.get("GITHUB_TOKEN")
        os.environ["GITHUB_TOKEN"] = self.token

    def __exit__(self, *exc: object) -> None:
        if self.saved is None:
            os.environ.pop("GITHUB_TOKEN", None)
        else:
            os.environ["GITHUB_TOKEN"] = self.saved


def app_token(app_id: int, account: str, private_key_pem: str, repository: str | None,
              permission_set: str | None = None) -> str:  # fmt: skip
    """The App's installation token for one repository and one named permission set, minted here so it
    never leaves this process.

    It refuses, before any request, a call with no repository, a repository that is not `account`'s, or
    a permission set that is not in PERMISSION_SETS. Until M07 PR 2 a call with no repository minted
    the installation's token with no scope: every permission the App holds on every repository it
    reaches (seed S0; milestones/M07/open.md row 2). That call is gone, not defaulted.

    A JWT the App's key signs, then the token of the installation that reaches `repository`, for that
    repository alone and that set alone. No third-party action holds the key (SPEC/06 section 6: each
    key is in its own environment, limited to `main`)."""
    if not isinstance(repository, str) or repository.count("/") != 1 or not all(repository.split("/")):
        raise ValueError(f"app_token() mints for one repository, owner/name; got {repository!r}: no token is asked for")
    owner, name = repository.split("/")
    if owner != account:
        raise ValueError(f"app_token() was asked for {repository}, which is not {account}'s: no token is asked for")
    if not isinstance(permission_set, str) or permission_set not in PERMISSION_SETS:
        raise ValueError(f"app_token() mints a named permission set ({', '.join(sorted(PERMISSION_SETS))}); "
                         f"got {permission_set!r}: no token is asked for")  # fmt: skip
    with _As(app_jwt(app_id, private_key_pem)):
        installation = gh(f"/repos/{repository}/installation")
        scope = {"repositories": [name], "permissions": PERMISSION_SETS[permission_set]}
        return gh(f"/app/installations/{installation['id']}/access_tokens", method="POST", body=scope)["token"]


def revoke(token: str) -> None:
    """Revoke an installation token GitHub would otherwise keep for an hour. Never raises: an unrevoked
    token is narrower than the key the job already holds, and the read it was for is done."""
    try:
        with _As(token):
            gh("/installation/token", method="DELETE")
    except (urllib.error.URLError, TimeoutError, OSError):
        print("note: a token could not be revoked; it expires within the hour")


def post(results: Path, app_id: int, mint=None) -> int:
    """`mint(repository, permission_set)` gives the App's token for that repository and that set alone.

    Each repository is read and posted under its own tokens: `rulesets`, for the one read that needs
    Administration, revoked as soon as the ruleset is read; then `check`, for the seats, the visibility
    and the check run. With no `mint` (a test), the caller's own GITHUB_TOKEN is used throughout."""
    from src.validate import agent as platform
    from src.validate import seats

    ruleset_check = "the repository's ruleset is the export"
    posted = 0
    for path in sorted(results.rglob("result.json")):
        result = json.loads(path.read_text(encoding="utf-8"))
        repository, head = result["repository"], result["head"]
        ruleset_errors: list[str]
        administer = None
        try:
            if mint is not None:
                administer = mint(repository, "rulesets")
                os.environ["GITHUB_TOKEN"] = administer
            ruleset_errors = platform.ruleset_errors(live_rulesets(repository))
        except urllib.error.HTTPError as exc:
            # 422 before the grant: the installation does not hold Administration: write, so no such token
            # exists. The head is refused, as a hidden bypass_actors is: closed, never open.
            ruleset_errors = [f"the live rulesets could not be read ({exc.code})"]
        finally:
            if administer is not None:
                os.environ.pop("GITHUB_TOKEN", None)
                revoke(administer)
        if mint is not None:
            os.environ["GITHUB_TOKEN"] = mint(repository, "check")
        errors: dict[str, list[str]] = dict(result["errors"])
        os.environ["AGENTKEEL_SEAT_REPOSITORY"] = repository
        seats.login_holds_seat.cache_clear()
        for login in result.get("seat_logins") or []:
            real, status = seats.login_holds_seat(login)
            if not real:
                errors.setdefault(SEAT_CHECK, []).append(f"manifest.yaml: seat login {login} is not a holder ({status})")
        try:
            public = gh(f"/repos/{repository}").get("private") is False
            errors[PUBLIC_CHECK] = [] if public else [f"{repository} is private: its ruleset is not enforced"]
        except urllib.error.HTTPError as exc:
            errors[PUBLIC_CHECK] = [f"the repository's visibility could not be read ({exc.code})"]
        errors[ruleset_check] = ruleset_errors
        failed = {name: errs for name, errs in errors.items() if errs}
        summary = "\n".join(f"- **{name}**: " + "; ".join(errs) for name, errs in failed.items()) or "Every check passed."
        gh(f"/repos/{repository}/check-runs", method="POST", body={
            "name": CHECK, "head_sha": head, "status": "completed",
            "conclusion": "failure" if failed else "success",
            "output": {"title": f"{len(failed)} refused" if failed else "passed",
                       "summary": summary[:60000],
                       "text": "Posted by agentkeel's platform check from its main (SPEC/06 section 6)."},
        })  # fmt: skip
        print(f"{repository}@{head[:12]}: {'failure' if failed else 'success'} ({', '.join(failed) or 'none refused'})")
        posted += 1
    return posted


def deployable(org: str, app_id: int) -> list[dict[str, Any]]:
    out = []
    for repo in repositories(org):
        name = repo["full_name"]
        if repo.get("private") is not False:
            continue
        branch = gh(f"/repos/{name}/branches/{repo['default_branch']}")
        head = branch["commit"]["sha"]
        if not any(r.get("conclusion") == "success" for r in app_runs(name, head, app_id)):
            continue
        try:
            manifest = yaml.safe_load(gh(f"/repos/{name}/contents/manifest.yaml?ref={head}", raw=True))
        except (urllib.error.HTTPError, yaml.YAMLError):
            continue
        agent = manifest.get("name") if isinstance(manifest, dict) else None
        # Again here, though the App passed it: deploy.yml puts the name in a path (cold review N3).
        from src.validate.agent import NAME

        if isinstance(agent, str) and NAME.match(agent):
            out.append({"repository": name, "repository_id": str(repo["id"]), "commit": head, "name": agent})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="what", required=True)
    for name in ("find", "deployable"):
        one = sub.add_parser(name)
        one.add_argument("--out", required=True, type=Path)
        if name == "deployable":
            # As the deploy role, in deploy.yml's find-agents: drop a commit the registry already holds.
            one.add_argument("--skip-deployed", action="store_true")
    two = sub.add_parser("post")
    two.add_argument("--results", required=True, type=Path)
    args = parser.parse_args(argv)

    org, app_id = identity()
    if not org or not isinstance(app_id, int):
        print("infra/platform_identity.json names no organisation or App yet: nothing is read and nothing posted")
        if args.what != "post":
            args.out.write_text("[]\n", encoding="utf-8")
        return 0
    if args.what == "post":
        key = os.environ.pop("AGENTKEEL_APP_PRIVATE_KEY", None)
        if not key:
            print("no AGENTKEEL_APP_PRIVATE_KEY: the posting job runs in the platform-app environment only")
            return 1
        count = post(args.results, app_id, mint=lambda repo, named: app_token(app_id, org, key, repo, named))
        print(f"posted {count} check runs")
        return 0
    found = find(org, app_id) if args.what == "find" else deployable(org, app_id)
    if args.what == "deployable" and args.skip_deployed:
        from scripts import registry

        table = registry.client()
        found = [a for a in found if registry.deployed(table, a["name"], a["commit"])[0] != 0]
    args.out.write_text(json.dumps(found) + "\n", encoding="utf-8")
    print(f"{len(found)}: {json.dumps(found)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
