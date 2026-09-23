"""Look up M02's seed PRs, the owner's bypass attempts and the three doors on GitHub, and write what it recorded (P5).

    python scripts/observe_pr.py milestones/M02/runs/f2_1_seed_prs.yaml --out seed_prs.json
    python scripts/observe_pr.py milestones/M02/runs/f2_1_bypass.yaml --out bypass.json
    python scripts/observe_pr.py milestones/M02/runs/f2_2_three_doors.yaml --out doors.json

An instrument, in the pattern of `scripts/observe_pr_check.py` (M00) and
`scripts/observe_attempt.py` (M01). It reads the run file the human filled
in after opening the seed PRs and making the attempts (SPEC/02 §5.1), asks
the GitHub API what happened to each, and writes a raw observation. It
decides nothing: `src/verdict/build.py` reads the observation into
`checks.F2_1` and `checks.F2_2` (`--check-seed-prs`, `--check-bypass`,
`--check-doors`), and only `verdict.gate` rules.

What is read, per run file:

- **seed PRs** (`seeds:`): for each PR number the human recorded, the
  pull's state and `merged`, the head sha, the conclusion of the check
  the seed expects to fail (`ruling-cited`, `two-key` or `checks`),
  whether that check is required on the base, and the job's log, in which
  the gate must have named the seed's path (`uncovered <path>`,
  `unkeyed <path>`, or `validate`'s FAIL line for it). A red check that
  does not name the path proves nothing about the seed (security-reviewer
  on PR 1, §8).
- **bypass** (`attempts:`): attempt 1, `gh pr merge --admin` on S1's PR:
  the PR's `merged` state, and whether the rule-suites API
  (`GET /repos/{owner}/{repo}/rulesets/rule-suites`) holds a failed
  evaluation for the actor at the time. That endpoint needs a token with
  `administration:read`, which a workflow's `GITHUB_TOKEN` cannot carry;
  `RULESET_TOKEN` (the fine-grained token `validate` reads the ruleset
  with) is used when set, else `GITHUB_TOKEN`, and the observation records
  the status code it got. Whether GitHub records a
  refused merge there at all is read at the attempt (SPEC/02 §5.1); when it
  does not, Door 3 rests on the PR's unmerged state and the human's own
  output, and the observation says which. Attempt 2, the owner in
  `bypass_actors`: the live ruleset's `bypass_actors` and `updated_at` now,
  beside what the human recorded before, during and after.
- **doors** (`doors:`): door 1 and door 3 are S1's PR (unmerged, `two-key`
  red naming `thresholds.yaml`, the attempt above); door 2 is M02 PR 2
  (merged, `two-key` green on its head, and the merge commit carrying two
  ruling files with distinct seats and `pr:` equal to its number, read
  with git from the checkout's history).

An entry the human has not filled (`observed: null`) writes an observation
that says so, and the check fails; it does not error (ruling i, M01).
Exit 0 when the observation is written, whatever it says; 1 only when it
could not be written at all.

Environment: GITHUB_REPOSITORY; GITHUB_TOKEN (check runs and job logs);
RULESET_TOKEN (the rule-suites lookup and the live ruleset's bypass list).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.observe_pr_check import required_on
from src.gates import canonical_seat, front_matter, pr_number

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
WINDOW = timedelta(hours=2)  # either side of the time the human wrote, for the rule-suites lookup


# --- the API ------------------------------------------------------------------


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(url: str, token: str | None, *, follow: bool = True) -> tuple[int, Any, dict[str, str]]:
    """(status, body or None, headers). A body that is JSON is parsed; other bodies are text."""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=60) as response:
            raw = response.read()
            headers = dict(response.headers)
            status = response.status
    except urllib.error.HTTPError as exc:
        if exc.code in (301, 302, 303, 307):
            return exc.code, None, dict(exc.headers)
        return exc.code, None, {}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return 0, f"{type(exc).__name__}: {exc}", {}
    text = raw.decode("utf-8", errors="replace")
    try:
        return status, json.loads(text), headers
    except json.JSONDecodeError:
        return status, text, headers


def get(repo: str, path: str, token: str | None) -> tuple[int, Any]:
    status, body, _ = request(f"{API}/repos/{repo}{path}", token)
    return status, body


def job_log(repo: str, job_id: int, token: str | None) -> tuple[int, str | None]:
    """The job's log: the API answers with a redirect to a blob, fetched without the token."""
    status, body, headers = request(f"{API}/repos/{repo}/actions/jobs/{job_id}/logs", token, follow=False)
    if status in (301, 302, 303, 307) and (location := headers.get("Location") or headers.get("location")):
        status, body, _ = request(location, None)
        return status, body if isinstance(body, str) else json.dumps(body)
    return status, body if isinstance(body, str) else None


# --- the pull requests ----------------------------------------------------------


def pull(repo: str, number: int, token: str | None) -> dict[str, Any]:
    status, body = get(repo, f"/pulls/{number}", token)
    if status != 200 or not isinstance(body, dict):
        return {"pr": number, "found": False, "status": status}
    return {
        "pr": number, "found": True, "pr_url": body["html_url"], "state": body["state"], "merged": body["merged"],
        "merge_commit_sha": body.get("merge_commit_sha") if body["merged"] else None,
        "base": body["base"]["ref"], "head_sha": body["head"]["sha"],
    }  # fmt: skip


def check_run(repo: str, head_sha: str, name: str, token: str | None) -> dict[str, Any] | None:
    status, body = get(repo, f"/commits/{head_sha}/check-runs?check_name={name}&per_page=50", token)
    runs = body.get("check_runs", []) if status == 200 and isinstance(body, dict) else []
    if not runs:
        return None
    latest = max(runs, key=lambda run: run["id"])
    return {"id": latest["id"], "status": latest["status"], "conclusion": latest["conclusion"], "html_url": latest["html_url"]}


def lines_naming(log: str, path: str, check: str) -> list[str]:
    """The log lines in which the gate or validate named the seed's path."""
    wanted = []
    for raw in log.splitlines():
        line = re.sub(r"^\S+T\S+Z ", "", raw.strip())  # the timestamp GitHub prefixes
        gate_named = check in ("ruling-cited", "two-key") and re.search(rf"\b(uncovered|unkeyed) {re.escape(path)}\b", line)
        validate_named = check == "checks" and path in line and ("FAIL" in line or line.startswith("     ") or "retired" in line or "one-sided" in line)
        if gate_named or validate_named:
            wanted.append(line)
    return wanted


def observe_seed(repo: str, seed: dict[str, Any], record: dict[str, Any], token: str | None) -> dict[str, Any]:
    entry = {"seed": seed["seed"], "expected_check": seed["expected_check"], "expected_path": seed["expected_path"],
             "human_said": {k: v for k, v in record.items() if k not in ("seed",)}}  # fmt: skip
    number = pr_number(record.get("pr"))
    if number is None:
        return entry | {"pr": None, "found": False, "note": "no PR number recorded for this seed"}
    entry |= pull(repo, number, token)
    if not entry["found"]:
        return entry
    entry["required_on_base"] = required_on(repo, entry["base"], seed["expected_check"])
    run = check_run(repo, entry["head_sha"], seed["expected_check"], token)
    entry["check_run"] = run
    entry["path_named_in_log"] = False
    entry["log_lines"] = []
    if run is not None:
        status, log = job_log(repo, run["id"], token)
        entry["log_status"] = status
        if log:
            entry["log_lines"] = lines_naming(log, seed["expected_path"], seed["expected_check"])
            entry["path_named_in_log"] = bool(entry["log_lines"])
    return entry


# --- the bypass attempts -----------------------------------------------------------


def parse_time(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def login_in(principal: str) -> str:
    """The bare login in a `principal:` line such as `the repository owner, andaro74, with admin on ...`.

    The comma-separated part that is a login and nothing else; "" when
    none is. The first draft indexed into a split of the wrong part and
    raised on the seed's own line (cold review of PR 2, F1).
    """
    for part in principal.split(","):
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*", part.strip()):
            return part.strip()
    return ""


def rule_suites(repo: str, actor: str, at: datetime | None, token: str | None) -> dict[str, Any]:
    """Failed rule-suite evaluations for the actor on main around `at`, and what the API said to the call."""
    path = f"/rulesets/rule-suites?ref=main&actor_name={actor}&rule_suite_result=fail&per_page=100"
    if at is not None:
        path += "&time_period=week"
    status, body = get(repo, path, token)
    out: dict[str, Any] = {"status": status, "readable": status == 200 and isinstance(body, list)}
    if not out["readable"]:
        out["note"] = "the rule-suites API could not be read with this token (needs administration:read)"
        return out
    suites = body
    if at is not None:
        suites = [s for s in suites if (t := parse_time(s.get("pushed_at"))) is not None and abs(t - at) <= WINDOW]
    out["failed_evaluations"] = [{k: s.get(k) for k in ("id", "actor_name", "before_sha", "after_sha", "ref", "pushed_at", "result")}
                                 for s in suites]  # fmt: skip
    return out


def live_ruleset(repo: str, ruleset_id: int, token: str | None) -> dict[str, Any]:
    status, body = get(repo, f"/rulesets/{ruleset_id}", token)
    if status != 200 or not isinstance(body, dict):
        return {"status": status, "readable": False}
    return {"status": status, "readable": True, "bypass_actors": body.get("bypass_actors"), "updated_at": body.get("updated_at"),
            "shown_bypass_actors": body.get("bypass_actors") is not None}  # fmt: skip


def observe_bypass(repo: str, run: dict[str, Any], token: str | None, suites_token: str | None) -> dict[str, Any]:
    observed = run.get("observed") or []
    attempts = run.get("attempts") or []
    out: dict[str, Any] = {"principal": run.get("principal"), "attempt_1": None, "attempt_2": None}
    actor = login_in(str(run.get("principal") or ""))
    if len(observed) >= 1 and isinstance(observed[0], dict):
        first = observed[0]
        entry: dict[str, Any] = {"human_said": first}
        number = pr_number(first.get("pr"))
        if number is not None:
            entry |= pull(repo, number, token)
        entry["rule_suites"] = rule_suites(repo, actor, parse_time(first.get("at")), suites_token or token)
        entry["rule_suite_fail_found"] = bool(entry["rule_suites"].get("failed_evaluations"))
        phrase = str(attempts[0].get("message_must_contain", "")) if attempts else ""
        entry["human_message_contains"] = bool(phrase) and phrase.lower() in str(first.get("message", "")).lower()
        entry["witness"] = ("the rule-suites API" if entry["rule_suite_fail_found"]
                            else "the PR's unmerged state and the human's own output (the API records no refused merge, or could not be read)")  # fmt: skip
        out["attempt_1"] = entry
    if len(observed) >= 2 and isinstance(observed[1], dict):
        second = observed[1]
        export = json.loads((ROOT / "infra" / "ruleset" / "main.json").read_text(encoding="utf-8"))
        entry = {"human_said": second, "live_now": live_ruleset(repo, int(export["id"]), token)}
        # A CI witness of the RED, when the human recorded the `checks` job
        # that ran while the actor was listed (`checks_job_id` in the
        # observed entry): validate's own line in that job's log. Without
        # it the observation says the RED is the human's word (cold review
        # of PR 2, F3), as attempt 1's `witness` does.
        entry["ci_red_lines"] = []
        if job := second.get("checks_job_id"):
            _status, log = job_log(repo, int(job), token)
            entry["ci_red_lines"] = [line for line in (log or "").splitlines() if "somebody can bypass main" in line]
        entry["witness"] = ("validate's line in the checks job's log" if entry["ci_red_lines"]
                            else "the human's own output (no checks_job_id recorded, or the line was not in its log)")  # fmt: skip
        out["attempt_2"] = entry
    if not observed:
        out["note"] = "the attempts have not been made: `observed` is empty in the run file"
    return out


# --- the three doors ---------------------------------------------------------------


def rulings_in(commit: str, number: int) -> list[dict[str, Any]]:
    """Ruling files at `commit` with this PR's number: path and seat, read with git from the checkout."""
    done = subprocess.run(["git", "ls-tree", "-r", "--name-only", commit, "--", "milestones"], cwd=ROOT,
                          capture_output=True, text=True, check=False)  # fmt: skip
    found = []
    for path in done.stdout.split():
        if not re.match(r"^milestones/[^/]+/rulings/[^/]+\.md$", path):
            continue
        shown = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True, text=True, check=False)
        fm = front_matter(shown.stdout) if shown.returncode == 0 else None
        if fm and pr_number(fm.get("pr")) == number:
            found.append({"path": path, "seat": canonical_seat(fm.get("seat")),
                          "authorises": [str(a) for a in (fm.get("authorises") or [])]})  # fmt: skip
    return found


def observe_doors(repo: str, run: dict[str, Any], token: str | None, suites_token: str | None) -> list[dict[str, Any]]:
    doors = []
    for door in run.get("doors") or []:
        entry: dict[str, Any] = {"door": door["door"], "what": door["what"], "expected": door["expected"]}
        number = pr_number(door.get("pr"))
        if number is None:
            doors.append(entry | {"pr": None, "found": False, "note": "no PR number recorded for this door"})
            continue
        entry |= pull(repo, number, token)
        if not entry["found"]:
            doors.append(entry)
            continue
        entry["two_key"] = check_run(repo, entry["head_sha"], "two-key", token)
        if door["door"] == 1 and entry["two_key"] is not None:
            _status, log = job_log(repo, entry["two_key"]["id"], token)
            entry["log_lines"] = lines_naming(log or "", "thresholds.yaml", "two-key")
            entry["path_named_in_log"] = bool(entry["log_lines"])
        if door["door"] == 2 and entry.get("merge_commit_sha"):
            entry["rulings_in_merge"] = rulings_in(entry["merge_commit_sha"], number)
            entry["distinct_seats"] = sorted({r["seat"] for r in entry["rulings_in_merge"] if r["seat"]})
            # A merged PR with two seat files and nothing relaxed is not Door
            # 2 (cold review of PR 2, F2): the gate's own line on a keyed
            # relaxation, from the two-key job's log, is what says a
            # relaxation was there to key.
            entry["keyed_lines"] = []
            if entry["two_key"] is not None:
                _status, log = job_log(repo, entry["two_key"]["id"], token)
                entry["keyed_lines"] = [line for line in (log or "").splitlines() if "two keys with pr:" in line]
            entry["relaxation_keyed"] = bool(entry["keyed_lines"])
        if door["door"] == 3:
            bypass_file = ROOT / "milestones" / "M02" / "runs" / "f2_1_bypass.yaml"
            bypass = yaml.safe_load(bypass_file.read_text(encoding="utf-8"))
            entry["bypass"] = observe_bypass(repo, bypass, token, suites_token)
        doors.append(entry)
    return doors


# --- command line ----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    run = yaml.safe_load(args.run.read_text(encoding="utf-8"))
    repo = os.environ.get("GITHUB_REPOSITORY", "andaro74/agentkeel")
    token = os.environ.get("GITHUB_TOKEN") or None
    suites_token = os.environ.get("RULESET_TOKEN") or None
    result: dict[str, Any] = {
        "what": "GitHub's record of M02's seeded cases; not an envelope; rules nothing",
        "looked_up_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "run": args.run.as_posix(),
        "repo": repo,
    }
    observed = run.get("observed")
    if "seeds" in run:
        result["kind"] = "seed_prs"
        records = {str(r.get("seed")): r for r in (observed or []) if isinstance(r, dict)}
        result["seeds"] = [observe_seed(repo, seed, records.get(str(seed["seed"]), {}), token) for seed in run["seeds"]]
        if not observed:
            result["note"] = "the seed PRs have not been opened: `observed` is empty in the run file"
    elif "attempts" in run:
        result["kind"] = "bypass"
        result |= observe_bypass(repo, run, token, suites_token)
    elif "doors" in run:
        result["kind"] = "doors"
        result["doors"] = observe_doors(repo, run, token, suites_token)
        if not observed:
            result["note"] = "the doors have not been filled in: `observed` is empty in the run file"
    else:
        print(f"{args.run}: not a seed-PR, bypass or doors run file", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.out} ({result['kind']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
