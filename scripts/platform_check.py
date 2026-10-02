"""The platform check's two halves and the deploy's list, for `.github/workflows/` on `main` (SPEC/06 §6, R2, R3).

    python scripts/platform_check.py find --out heads.json            # no secret: what to evaluate
    python scripts/platform_check.py grant --app SLUG --out READ.json  # the App's key: its grant, read back
    python scripts/platform_check.py post --results DIR               # the App's key: seats, ruleset, the check
    python scripts/platform_check.py deployable --out merged.json     # no secret: what deploy.yml may deploy
    python scripts/platform_check.py relax --agent NAME --out ANSWER.json   # the App's key: seed S0's third attempt, once

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
  evaluated, success only when every list is empty. From M07 PR 2 it mints
  two tokens per repository from the App's key, each for that repository and
  one named permission set (`PERMISSION_SETS`): `rulesets` for the one read
  that needs Administration, revoked after it, then `check`.
- `grant` (M07 PR 2; seed S0's reader): what GitHub says one App holds, read
  with the App's own JWT (its registered permissions, each installation's
  permissions, selection and repositories) and its key's environment (branch
  policies, admin bypass), against `infra/platform_grant.yaml`, which is
  Security's (from M07 PR 3; until then the block was in a ruling file under
  `milestones/M07/rulings/`, on Product's path). It writes what it read and
  exits 1 on any value beyond the grant. It runs first in every keyed job.
- `deployable`: every public repository's default-branch head that carries a
  successful `platform-check` run from the App, with the agent name its
  manifest holds there. `deploy.yml` reads the registry to skip what is
  already deployed and to refuse a name another repository holds.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
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
    if not isinstance(repository, str) or not re.fullmatch(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+", repository):
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


# --- the reader of the grant (M07 PR 2; SPEC/07 section 6; rulings/pr2-security.md item 6; S0's reader) ----

GRANT_FILE = "infra/platform_grant.yaml"  # Security's path (rulings/pr2-security.md item 13j, at M07 PR 3)
RULING_PATH = re.compile(r"milestones/M[0-9]{2}/rulings/[a-z0-9][a-z0-9-]*\.md")
PLATFORM_REPOSITORY = "andaro74/agentkeel"  # whose environments hold the Apps' keys
LEVELS = {"read": 1, "write": 2, "admin": 3}


class NoGrant(Exception):
    """No ruled grant can be read: a keyed job then stops before it mints anything."""


def grant_file(root: Path = ROOT) -> dict[str, Any]:
    """`infra/platform_grant.yaml` as a mapping, or NoGrant: missing, not YAML, or with no `grant:` mapping."""
    path = root / GRANT_FILE
    if not path.is_file():
        raise NoGrant(f"{GRANT_FILE}: missing; no grant is ruled")
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise NoGrant(f"{GRANT_FILE} does not parse ({exc.__class__.__name__})") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("grant"), dict):
        raise NoGrant(f"{GRANT_FILE} carries no grant: mapping")
    return doc


def load_grant(root: Path = ROOT, *, ruled_only: bool = True) -> dict[str, Any]:
    """The `grant:` mapping of `infra/platform_grant.yaml`.

    Read from the checkout, which in a keyed job is `main`'s (each key's environment deploys from
    `main` only): a pull request cannot widen the grant it is checked against. The file is on
    Security's path, so a change to it needs a Security ruling. Until M07 PR 3 the block was in a
    ruling file under milestones/M07/rulings/, which is Product's path (security-reviewer 5 on M07 PR 2).

    A draft is not a grant: with `ruled_only`, the file must name, in `ruled_in`, a ruling file that is
    on the checkout, whose `seat:` is Security, and which carries a line that starts "Ruled by", as
    `cold-review-ruling` reads it."""
    doc = grant_file(root)
    if ruled_only:
        named = doc.get("ruled_in")
        if not isinstance(named, str) or not RULING_PATH.fullmatch(named):
            raise NoGrant(f"{GRANT_FILE}: ruled_in names no ruling file ({named!r}); no seat has ruled the grant")
        ruling = root / named
        if not ruling.is_file():
            raise NoGrant(f"{GRANT_FILE}: {named}, which it says rules it, is not on this checkout")
        lines = ruling.read_text(encoding="utf-8").replace("\r\n", "\n").splitlines()
        seat = None
        if lines and lines[0].strip() == "---":
            front = lines[1:lines.index("---", 1)] if "---" in lines[1:] else []
            seat = next((line.split(":", 1)[1].strip() for line in front if line.startswith("seat:")), None)
        if seat != "Security":
            raise NoGrant(f"{named} is not a Security ruling (seat: {seat!r}): it cannot rule the grant")
        if not any(line.startswith("Ruled by ") for line in lines):
            raise NoGrant(f"{named}: the grant is a draft; no seat has ruled it (no line starts 'Ruled by')")
    return doc["grant"]


def seeded_repository(root: Path = ROOT) -> str | None:
    """The one repository the seeded relaxation may be pointed at, from the grant file (Security's)."""
    seed = grant_file(root).get("relax_seed")
    name = seed.get("repository") if isinstance(seed, dict) else None
    return name if isinstance(name, str) else None


def _beyond(held: Any, granted: Any) -> bool:
    """True when a permission level is more than the grant's. A level this does not know is more."""
    return LEVELS.get(str(held), 99) > LEVELS.get(str(granted), 0)


def permission_errors(who: str, permissions: Any, granted: dict[str, Any]) -> list[str]:
    if not isinstance(permissions, dict):
        return [f"{who}: its permissions were not read"]
    errors = []
    for name, level in sorted(permissions.items()):
        if name not in granted:
            errors.append(f"{who}: permission {name}: {level} is not in the grant")
        elif _beyond(level, granted[name]):
            errors.append(f"{who}: permission {name} is {level}, the grant names {granted[name]}")
    return errors


def environment_errors(slug: str, app: dict[str, Any], environment: Any, rules: Any) -> list[str]:
    """The environment that holds an App's key, against the grant's `environments` (items 1, 6)."""
    if not isinstance(environment, dict) or not isinstance(rules, dict):
        return [f"{slug}: its key's environment, or the grant's environments, was not read"]
    name = environment.get("name")
    errors = []
    if name != app.get("environment"):
        errors.append(f"{slug}: its key was read in environment {name!r}, the grant names {app.get('environment')!r}")
    wanted = [(p.get("name"), p.get("type")) for p in rules.get("branch_policies") or []]
    policies = environment.get("branch_policies")
    if not isinstance(policies, list):
        errors.append(f"environment {name}: its deployment branch policies were not read")
        policies = []
    found = [(p.get("name"), p.get("type")) for p in policies if isinstance(p, dict)]
    errors += [f"environment {name}: deployment policy {n} ({t}) is not in the grant" for n, t in found
               if (n, t) not in wanted]  # fmt: skip
    errors += [f"environment {name}: no deployment policy {n} ({t}), which the grant names" for n, t in wanted
               if (n, t) not in found]  # fmt: skip
    if environment.get("can_admins_bypass") is not rules.get("can_admins_bypass"):
        errors.append(f"environment {name}: can_admins_bypass is {environment.get('can_admins_bypass')!r}, "
                      f"the grant names {rules.get('can_admins_bypass')!r}")  # fmt: skip
    # The secrets' names, where a caller that may list them read them (an admin's token; no job's own).
    secrets = environment.get("secrets")
    if isinstance(secrets, list):
        if len(secrets) != 1:
            errors.append(f"environment {name} holds {len(secrets)} secrets ({', '.join(map(str, secrets)) or 'none'}); "
                          "the grant names one, the App's key")  # fmt: skip
        shared = sorted(set(secrets) & set(environment.get("repository_secrets") or []))
        errors += [f"environment {name}: {secret} is also a repository secret, which a workflow on any branch can read"
                   for secret in shared]  # fmt: skip
    return errors


def grant_errors(installation: dict[str, Any], environment: dict[str, Any], grant: dict[str, Any]) -> list[str]:
    """What one installation of one App, and the environment that holds its key, hold beyond the grant.

    `installation` is GitHub's answer for it, with `repositories`, the names it reaches. `grant` is the
    ruling's `grant:` block: one entry per App, and `environments`. [] when nothing is beyond it; a
    value narrower than the grant is not an error (a grant not yet made reads as narrower). Each error
    names what is not covered: an App or an id the grant does not name, an account it is not installed
    on by ruling, a permission or a level, a repository, a widened selection, a branch policy, an admin
    bypass, a second secret."""
    slug = installation.get("app_slug")
    app = grant.get(slug) if slug != "environments" else None
    if not isinstance(app, dict):
        return [f"the grant names no App {slug!r} (it names {', '.join(sorted(a for a in grant if a != 'environments'))})"]
    errors = []
    if app.get("app_id") is None:
        errors.append(f"{slug}: the grant holds no app_id for it yet, so no installation is covered")
    elif installation.get("app_id") != app["app_id"]:
        errors.append(f"{slug}: the installation is App {installation.get('app_id')}, the grant names {app['app_id']}")
    account = (installation.get("account") or {}).get("login")
    who = f"{slug} on {account}"
    selection = app.get("repository_selection")
    covered = selection.get(account) if isinstance(selection, dict) else selection
    if account not in (app.get("installed_on") or []):
        # An App installed on two accounts has to be public on GitHub, so anybody may install it on an
        # account of their own. That gives this platform's key reach into their repositories and gives
        # them nothing here: no token is minted for an account the grant does not name, by `app_token`
        # or by `read_grant` (security-reviewer BLOCK 1 on M07 PR 2: until then `read_grant` minted a
        # metadata token on every installation). The grant says which App is public; for it, such an
        # installation is recorded from the App's own listing and is not an error, suspended or not,
        # or a stranger could stop every keyed job by installing the App. For every other App it is one.
        if app.get("public") is True:
            return errors
        errors.append(f"{slug} is installed on {account}, which the grant does not name "
                      f"(installed_on {', '.join(app.get('installed_on') or []) or 'nothing'})")  # fmt: skip
    elif covered == "all":
        pass  # every repository of the account, as ruled; `selected` is narrower
    elif isinstance(covered, list):
        if installation.get("repository_selection") != "selected":
            errors.append(f"{who}: repository_selection is {installation.get('repository_selection')!r}, "
                          f"the grant names {', '.join(covered)} and no other")  # fmt: skip
        repositories = installation.get("repositories")
        if not isinstance(repositories, list):
            errors.append(f"{who}: the repositories it reaches were not read")
        else:
            errors += [f"{who}: it reaches {repo}, which the grant does not name" for repo in repositories
                       if repo not in covered]  # fmt: skip
    else:
        errors.append(f"{who}: the grant names no repository_selection for {account}")
    errors += permission_errors(who, installation.get("permissions"), app.get("permissions") or {})
    return errors + environment_errors(slug, app, environment, grant.get("environments"))


def installations_of_the_app() -> list[dict[str, Any]]:
    """Every installation of the App whose JWT is the caller's credential, each page (security-reviewer 2
    on M07 PR 2: one page of a public App's list can leave a named account's installation unread)."""
    found: list[dict[str, Any]] = []
    page = 1
    while True:
        got = gh(f"/app/installations?per_page=100&page={page}")
        if not isinstance(got, list):
            raise KeyError("the App's installations did not come back as a list")
        found += got
        if len(got) < 100:
            return found
        page += 1


def read_environment(name: str, repository: str = PLATFORM_REPOSITORY) -> dict[str, Any]:
    """An environment's rules as GitHub returns them, in `grant_errors`' shape. A read that fails is
    written with its error and no policies, which the reader refuses.

    The secrets' names are not read: no token a job holds may list them (`secrets` is None, and the
    artifact says so). They are read by hand, by an admin, and recorded under milestones/M07/runs/."""
    out: dict[str, Any] = {"name": name, "can_admins_bypass": None, "branch_policies": None, "secrets": None,
                           "error": None}  # fmt: skip
    try:
        environment = gh(f"/repos/{repository}/environments/{name}")
        out["can_admins_bypass"] = environment.get("can_admins_bypass")
        policy = environment.get("deployment_branch_policy")
        if policy is None:
            out["branch_policies"] = []  # no policy: any branch may deploy
        elif policy.get("custom_branch_policies"):
            listed = gh(f"/repos/{repository}/environments/{name}/deployment-branch-policies?per_page=100")
            out["branch_policies"] = [{"name": p.get("name"), "type": p.get("type")}
                                      for p in listed.get("branch_policies") or []]  # fmt: skip
        else:
            out["branch_policies"] = [{"name": "(every protected branch)", "type": "protected"}]
    except (urllib.error.URLError, TimeoutError, OSError, KeyError) as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def read_grant(slug: str, app_id: int, private_key_pem: str, named: Any = None) -> dict[str, Any]:
    """What GitHub says one App holds, read with the App's own JWT: its registered permissions, each of
    its installations, and, for an installation on an account in `named` (the grant's `installed_on`),
    the repositories it reaches.

    That repository list is read with a token that holds `metadata: read` and nothing else, revoked
    after the read (item 6). **No token is asked for on any other account**: an installation the grant
    does not name is recorded as the App's own listing gives it (id, account, selection, permissions)
    and its repositories are left unread. The environment is read with the job's own token."""
    named = set(named or [])
    read: dict[str, Any] = {"app": slug, "app_id": app_id, "registered": None, "installations": [], "error": None}
    try:
        with _As(app_jwt(app_id, private_key_pem)):
            registered = gh("/app")
            read["registered"] = {"slug": registered.get("slug"), "id": registered.get("id"),
                                  "permissions": registered.get("permissions")}  # fmt: skip
            for one in installations_of_the_app():
                installation = {"id": one.get("id"), "app_id": one.get("app_id"), "app_slug": one.get("app_slug"),
                                "account": {"login": (one.get("account") or {}).get("login")},
                                "repository_selection": one.get("repository_selection"),
                                "permissions": one.get("permissions"), "suspended_at": one.get("suspended_at"),
                                "repositories": None}  # fmt: skip
                if installation["account"]["login"] not in named:
                    read["installations"].append(installation)
                    continue
                token = gh(f"/app/installations/{one['id']}/access_tokens", method="POST",
                           body={"permissions": {"metadata": "read"}})["token"]  # fmt: skip
                try:
                    with _As(token):
                        names, page = [], 1
                        while True:
                            got = gh(f"/installation/repositories?per_page=100&page={page}")
                            names += [r["name"] for r in got.get("repositories") or []]
                            if len(names) >= got.get("total_count", 0) or not got.get("repositories"):
                                break
                            page += 1
                        installation["repositories"] = sorted(names)
                finally:
                    revoke(token)
                read["installations"].append(installation)
    except (urllib.error.URLError, TimeoutError, OSError, KeyError) as exc:
        read["error"] = f"{type(exc).__name__}: {exc}"
    return read


def check_grant(slug: str, private_key_pem: str, root: Path = ROOT) -> tuple[dict[str, Any], list[str]]:
    """What was read, and every way it is beyond the ruled grant. Any error stops the keyed job."""
    grant = load_grant(root)
    app = grant.get(slug) if slug != "environments" else None
    if not isinstance(app, dict):
        raise NoGrant(f"the grant names no App {slug!r}")
    if not isinstance(app.get("app_id"), int):
        raise NoGrant(f"{slug}: the grant holds no app_id for it yet; the App is made, and its id pushed, first")
    named = list(app.get("installed_on") or [])
    read = read_grant(slug, app["app_id"], private_key_pem, named)
    read["environment"] = read_environment(str(app.get("environment")))
    errors = []
    if read["error"]:
        errors.append(f"{slug}: GitHub could not be read as the App ({read['error']})")
    if read["environment"]["error"]:
        errors.append(f"environment {app.get('environment')}: could not be read ({read['environment']['error']})")
    registered = read.get("registered") or {}
    if registered and (registered.get("slug"), registered.get("id")) != (slug, app["app_id"]):
        errors.append(f"{slug}: the key is App {registered.get('slug')} ({registered.get('id')})'s, "
                      f"the grant names {slug} ({app['app_id']})")  # fmt: skip
    errors += permission_errors(f"{slug} as registered", registered.get("permissions"), app.get("permissions") or {})
    if not read["installations"] and not read["error"]:
        errors.append(f"{slug}: no installation was read")
    # The key's environment, once, whatever was installed where (security-reviewer 3 on M07 PR 2: inside
    # an installation's pass alone, a read that found only unnamed accounts never compared it).
    errors += environment_errors(slug, app, read["environment"], grant.get("environments"))
    for installation in read["installations"]:
        errors += [e for e in grant_errors(installation, read["environment"], grant) if e not in errors]
        account = installation["account"]["login"]
        # A stranger's installation of the public App, suspended or not, is theirs and stops nothing here.
        if installation.get("suspended_at") and (account in named or app.get("public") is not True):
            errors.append(f"{slug} on {account}: the installation is suspended")
    # Narrower than the grant is not an error; it is what a grant not yet made, or not yet accepted, reads as.
    narrower = []
    for installation in read["installations"]:
        held = installation.get("permissions") or {}
        narrower += [f"{slug} on {installation['account']['login']}: {name} is {held.get(name) or 'not held'}, "
                     f"the grant names {level}" for name, level in sorted((app.get("permissions") or {}).items())
                     if held.get(name) is None or LEVELS.get(str(held[name]), 99) < LEVELS.get(str(level), 0)]  # fmt: skip
    installed = {i["account"]["login"] for i in read["installations"]}
    read["not_ours"] = sorted(installed - set(app.get("installed_on") or [])) if app.get("public") is True else []
    narrower += [f"{slug}: not installed on {account}, which the grant names" for account in app.get("installed_on") or []
                 if account not in installed]  # fmt: skip
    read |= {"grant": {slug: app, "environments": grant.get("environments")}, "errors": errors, "narrower": narrower}
    return read, errors


# --- the seeded relaxation (M07 PR 2; SPEC/07 section 6; rulings/pr2-security.md item 8; S0's third attempt) ----

SEED_RUN_FILE = "milestones/M07/runs/f7_0_owner_test.yaml"


def relax_seed(name: str, org: str, app_id: int, private_key_pem: str, root: Path = ROOT) -> dict[str, Any]:
    """Ask GitHub, once, as the App, to remove the required status check from one agent repository's
    ruleset, and return GitHub's answer as it came.

    The App holds Administration: write because nothing less shows it `bypass_actors`. This is the
    seeded attempt to use that for what it must not: relax the ruleset that binds its own check. It
    is expected to be accepted, and then detected: the next platform check refuses every head of that
    repository until its owner restores the export. Which it is comes from the attempt.

    It can be pointed at one repository only: the one `infra/platform_grant.yaml` names under
    `relax_seed` on `main` (Security's path from M07 PR 3; until then the seed's run file named it, on
    Product's). Any other name is refused before a token is minted, so this is not a tool for relaxing
    an agent's ruleset.
    And it is made once: when the run file on `main` already records the attempt (an `observed` entry
    whose `what` names the relaxation, as the observer matches it), it is refused before a token is minted (security-reviewer 6 on M07 PR 2:
    "made once" was a sentence, not a check). Between the attempt and the commit that records it,
    nothing but the dispatch's own log stops a second one."""
    from src.validate.agent import NAME

    if not isinstance(name, str) or not NAME.match(name):
        raise ValueError(f"{name!r} is not an agent's name")
    seed = yaml.safe_load((root / SEED_RUN_FILE).read_text(encoding="utf-8")) or {}
    try:
        seeded = seeded_repository(root)
    except NoGrant as exc:
        raise ValueError(f"the seeded relaxation's repository cannot be read: {exc}") from exc
    repository = f"{org}/{name}"
    if repository != seeded:
        raise ValueError(f"the seeded relaxation is made on {seeded} and on no other repository; got {repository}")
    made = [o for o in seed.get("observed") or [] if isinstance(o, dict) and "relax" in str(o.get("what", ""))]
    if made:
        raise ValueError(f"the seeded relaxation was already made ({SEED_RUN_FILE} records it): it is made once")
    record: dict[str, Any] = {"what": "the App's token asked to remove the required status check from the ruleset",
                              "repository": repository, "ruleset": None, "status": None, "message": None,
                              "at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")}  # fmt: skip
    token = app_token(app_id, org, private_key_pem, repository, "rulesets")
    try:
        with _As(token):
            mine = [r for r in live_rulesets(repository)
                    if any(rule.get("type") == "required_status_checks" and any(
                        c.get("context") == CHECK and c.get("integration_id") == app_id
                        for c in (rule.get("parameters") or {}).get("required_status_checks") or [])
                        for rule in r.get("rules") or [])]  # fmt: skip
            if not mine:
                record["message"] = "no ruleset of the repository requires the platform check from the App: nothing to ask"
                return record
            record["ruleset"] = mine[0]["id"]
            body = {key: mine[0][key] for key in ("name", "target", "enforcement", "conditions") if key in mine[0]}
            body["rules"] = [rule for rule in mine[0]["rules"] if rule.get("type") != "required_status_checks"]
            try:
                gh(f"/repos/{repository}/rulesets/{mine[0]['id']}", method="PUT", body=body)
                record |= {"status": 200, "message": "GitHub accepted the change"}
            except urllib.error.HTTPError as exc:
                record |= {"status": exc.code, "message": (exc.read() or b"").decode("utf-8", "replace")[:500] if exc.fp else str(exc)}
    finally:
        revoke(token)
    return record


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
            # `rollout` from M07 PR 2 (SPEC/07 section 6): at a head the App passed, `retired` is retired by
            # deploy.yml's retire job and deployed by nothing. Any other value is deployed, as before.
            out.append({"repository": name, "repository_id": str(repo["id"]), "commit": head, "name": agent,
                        "rollout": "retired" if manifest.get("rollout") == "retired" else "all-at-once"})  # fmt: skip
    return out


def grant_command(slug: str, out: Path) -> int:
    """Read one App's grant back and write what was read; exit 1 on anything beyond the ruled grant.

    The key is taken from the environment and removed from it. Nothing with a write permission is
    minted here: the JWT, and one `metadata: read` token per installation on an account the grant
    names, for its repository list."""
    key = os.environ.pop("AGENTKEEL_APP_PRIVATE_KEY", None)
    if not key:
        print(f"no AGENTKEEL_APP_PRIVATE_KEY: {slug}'s grant is read in its key's environment only")
        return 1
    try:
        read, errors = check_grant(slug, key)
    except NoGrant as refusal:
        print(f"REFUSED: {refusal}")
        return 1
    _org, platform_app = identity()
    if slug == "agentkeel-platform" and read["app_id"] != platform_app:
        errors.append(f"{slug}: the grant names App {read['app_id']}, infra/platform_identity.json names {platform_app}")
        read["errors"] = errors
    read["read_at"] = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(read, indent=2) + "\n", encoding="utf-8")
    for installation in read["installations"]:
        print(f"{slug} on {installation['account']['login']}: {installation['repository_selection']}, "
              f"{'repositories not read' if installation['repositories'] is None else str(len(installation['repositories'])) + ' repositories'}, "
              f"{json.dumps(installation['permissions'], sort_keys=True)}")
    environment = read["environment"]
    print(f"environment {environment['name']}: policies {environment['branch_policies']}, "
          f"can_admins_bypass {environment['can_admins_bypass']}; its secrets' names are not read by a job")
    for note in read["narrower"]:
        print(f"narrower than the grant: {note}")
    for account in read.get("not_ours") or []:
        print(f"{slug} is public and is also installed on {account}: recorded, never minted for")
    for error in errors:
        print(f"FAIL {error}")
    print(f"{slug}: {'beyond the ruled grant; nothing is minted' if errors else 'within the ruled grant'}")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="what", required=True)
    for name in ("find", "deployable"):
        one = sub.add_parser(name)
        one.add_argument("--out", required=True, type=Path)
        if name == "deployable":
            # As the deploy role, in deploy.yml's find-agents: drop a commit the registry already holds.
            one.add_argument("--skip-deployed", action="store_true")
            # M07 PR 2: the heads that say `rollout: retired`, less the agents the registry says are retired.
            one.add_argument("--retiring", type=Path)
    two = sub.add_parser("post")
    two.add_argument("--results", required=True, type=Path)
    # M07 PR 2: the reader of the grant, first in every keyed job (rulings/pr2-security.md item 6).
    three = sub.add_parser("grant")
    three.add_argument("--app", required=True)
    three.add_argument("--out", required=True, type=Path)
    # M07 PR 2: seed S0's third attempt, made once, from main, by a dispatch input (item 8).
    four = sub.add_parser("relax")
    four.add_argument("--agent", required=True)
    four.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    if args.what == "grant":
        return grant_command(args.app, args.out)
    if args.what == "relax":
        org, app_id = identity()
        key = os.environ.pop("AGENTKEEL_APP_PRIVATE_KEY", None)
        if not key or not org or not isinstance(app_id, int):
            print("no AGENTKEEL_APP_PRIVATE_KEY, organisation or App: the seeded relaxation is made in the platform-app environment only")
            return 1
        try:
            record = relax_seed(args.agent, org, app_id, key)
        except ValueError as refusal:
            print(f"REFUSED: {refusal}")
            return 1
        args.out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(f"{record['repository']}: GitHub answered {record['status']} ({record['message']})")
        return 0

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
    if args.what == "deployable":
        # A retired head is never in the list that is deployed, with or without the registry.
        retiring = [a for a in found if a.get("rollout") == "retired"]
        found = [a for a in found if a.get("rollout") != "retired"]
        if args.skip_deployed:
            from scripts import registry

            table = registry.client()
            found = [a for a in found if registry.deployed(table, a["name"], a["commit"])[0] != 0]
            # Left to retire: the registry holds a row for this repository with no `retired_at` yet.
            retiring = [a for a in retiring if registry.retiring(table, a["name"], a["repository_id"], None)[0] != 4
                        and registry.holder(table, a["name"]) == a["repository_id"]]  # fmt: skip
        if args.retiring:
            args.retiring.write_text(json.dumps(retiring) + "\n", encoding="utf-8")
            print(f"to retire, {len(retiring)}: {json.dumps(retiring)}")
    args.out.write_text(json.dumps(found) + "\n", encoding="utf-8")
    print(f"{len(found)}: {json.dumps(found)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
