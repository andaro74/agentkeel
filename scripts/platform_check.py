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


# What one post needs, on one repository (security-reviewer N6 on PR 2): the token is minted per repository
# with these permissions only, not every permission the App holds on every repository.
POST_PERMISSIONS = {"checks": "write", "administration": "read", "contents": "read", "metadata": "read"}


def app_token(app_id: int, org: str, private_key_pem: str, repository: str | None = None) -> str:
    """The App's installation token, minted here so it never leaves this process.

    A JWT the App's key signs (RS256, ten minutes), then the organisation's installation's token, for
    `repository` alone and POST_PERMISSIONS when one is named. No third-party action holds the key
    (SPEC/06 section 6: the key is in the `platform-app` environment)."""
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
    jwt = f"{head}.{body}.{signature}"
    saved = os.environ.get("GITHUB_TOKEN")
    os.environ["GITHUB_TOKEN"] = jwt
    try:
        installation = gh(f"/orgs/{org}/installation")
        scope = {} if repository is None else {"repositories": [repository.split("/", 1)[1]],
                                                 "permissions": POST_PERMISSIONS}  # fmt: skip
        return gh(f"/app/installations/{installation['id']}/access_tokens", method="POST", body=scope)["token"]
    finally:
        if saved is None:
            os.environ.pop("GITHUB_TOKEN", None)
        else:
            os.environ["GITHUB_TOKEN"] = saved


def post(results: Path, app_id: int, mint=None) -> int:
    """`mint(repository)` gives the App's token for that repository alone; each post runs under its own."""
    from src.validate import agent as platform
    from src.validate import seats

    posted = 0
    for path in sorted(results.rglob("result.json")):
        result = json.loads(path.read_text(encoding="utf-8"))
        repository, head = result["repository"], result["head"]
        if mint is not None:
            os.environ["GITHUB_TOKEN"] = mint(repository)
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
        try:
            errors["the repository's ruleset is the export"] = platform.ruleset_errors(live_rulesets(repository))
        except urllib.error.HTTPError as exc:
            errors["the repository's ruleset is the export"] = [f"the live rulesets could not be read ({exc.code})"]
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
        print(f"posted {post(args.results, app_id, mint=lambda repo: app_token(app_id, org, key, repo))} check runs")
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
