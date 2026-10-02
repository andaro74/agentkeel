"""verdict.upgrade: build's readings of claim 7 (SPEC/07 §4; P5).

`scripts/observe_upgrade.py` writes raw observations only: what GitHub, AWS
and Grafana returned for each attempt a run file under
`milestones/M07/runs/` names, each with the time it was read and, for a
GitHub reading, the viewpoint it was read from. Everything that compares one
record with another, or rules on one, is here, and only `build` calls it.
The result is the envelope's optional `upgrade`. The gate rules nothing on
it, and row 7's Measured cell reads it (`gate.upgrade_misses`).

One entry per falsifier, each `read` (every record it needs was found),
`held` (null when unread), `reasons` (each miss, named) and `viewpoint`:

- **F7.0**, no agent from the template exists to upgrade. Four parts, all of
  which must be read and held: the owner's test (a head with the template's
  content refused on the seats and the goldens and nothing else; the fixed
  head passed, merged, deployed within `deploy_max_seconds`, answering and
  listed); the platform check dispatched from a branch (its `post` job
  rejected by the environment before it started); the App's token asked to
  relax a ruleset (refused, or detected); and the timed run's agent
  (merged, deployed, answering and listed, read from `template`).
- **F7.1**, an upgrade requires a manual edit. For each upgrade's pull
  request: opened by the platform's App within `arrive_max_seconds` of the
  trigger; no path under `.github/workflows/`; only the paths its kind may
  change; no person's edit (a commit by anyone but the App that touches
  anything but a ruling file, or a commit on the default branch between the
  opening and the merge that touches the same files);
  `infra/workflows.sha256` unchanged across it; merged on green checks.
- **F7.2**, a retired agent still answers (seed S2's reader, `f7_2`).
- **F7.3**, a rollback leaves the new digest live (seed S3's reader, `f7_3`).
- **F7.4**, panel 2 shows GREEN where the envelope says RED (seed S4's
  comparison, `panel_verdict_mismatch`, through `replay_history`).
- **F7.5**, the surfaces' plants (seed S5's counter, `surface_plants`). A
  test-only reading with no live half: it is read from the run's own tests.

And **`taken`**, the measured value: how many of the three upgrades
(platform, model, retirement) arrived as a pull request the platform opened
and went live with no workflow edit and no person's edit, n of 3.

An attempt that has not been made is unread, never held. Row 7 reads unread
as RED.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.verdict import plants, replay_history
from src.verdict.template import (
    GOLDENS_CHECK,
    PLATFORM_CHECK,
    SEAT_CHECK,
    Unreadable,
    app_success,
    as_the_app_saw,
    entry,
    planted_fault,
    when,
)

# The check name the platform's App posts a ruleset that differs under (scripts/platform_check.py).
RULESET_CHECK = "the repository's ruleset is the export"
REFUSED_AS_PLANTED = {SEAT_CHECK, GOLDENS_CHECK}
GONE = "ResourceNotFoundException"
BARS = ("arrive_max_seconds", "deploy_max_seconds", "retire_max_seconds")
KINDS = ("platform", "model", "retirement")
RULING_FILE = ("milestones/", "/rulings/")
WORKFLOWS = ".github/workflows/"
# What each kind's pull request may change (SPEC/07 §2). A ruling file is beside the pin move, in
# agentkeel only (BLOCK 2): a seat ruling a change is the gate working, not a person's edit.
MAY_CHANGE = {
    "platform": ("manifest.yaml", "server.py", "__init__.py"),
    "retirement": ("manifest.yaml",),
    "model": ("agents/refagent/manifest.yaml",),
}


def seconds(start: Any, end: Any) -> float | None:
    a, b = when(start), when(end)
    return None if a is None or b is None else (b - a).total_seconds()


def is_ruling(path: str) -> bool:
    return path.startswith(RULING_FILE[0]) and RULING_FILE[1] in path and path.endswith(".md")


# --- F7.2: a retired agent still answers (seed S2's reader) --------------------


def f7_2(observation: dict[str, Any] | None, max_seconds: float) -> dict[str, Any]:
    """The records of one retirement, read against each other (SPEC/07 §2 "Retired", §4).

    Unread until the retirement pull request has merged and the runtime, the invocation and the bundle
    were each looked up. Held when CloudTrail has `DeleteAgentRuntime` within `max_seconds` of the
    merge, `GetAgentRuntime` and the retire job's one invocation after it are both refused with
    ResourceNotFoundException (a refusal for access is not a deletion), no answer record is dated
    after the deletion, the signed bundle is in the audit bucket and the registry row says
    `retired_at`."""
    if not observation or observation.get("error"):
        return entry(False, [f"unread: {(observation or {}).get('error') or 'no retirement observed'}"], elapsed_s=None)
    pull = observation.get("pull_request") or {}
    merged_at = pull.get("merged_at")
    if pull.get("merged") is not True or when(merged_at) is None:
        return entry(False, ["unread: the retirement pull request has not merged"], elapsed_s=None)
    runtime, invocation, bundle = observation.get("get_runtime"), observation.get("invocation"), observation.get("bundle")
    unread = [name for name, value in (("GetAgentRuntime", runtime), ("the retire job's invocation", invocation),
                                       ("the bundle", bundle)) if not isinstance(value, dict)]  # fmt: skip
    if unread:
        return entry(False, [f"unread: {', '.join(unread)} not looked up"], elapsed_s=None)
    deleted = observation.get("delete_event") or {}
    deleted_at = deleted.get("eventTime") if deleted.get("eventName") == "DeleteAgentRuntime" else None
    elapsed = seconds(merged_at, deleted_at)
    reasons = []
    if runtime.get("found") is True:
        waited = seconds(merged_at, runtime.get("read_at"))
        if waited is None or waited <= max_seconds:
            return entry(False, ["unread: the runtime is still there and upgrade.retire_max_seconds has not passed"],
                         elapsed_s=elapsed)  # fmt: skip
        reasons.append(f"the runtime still exists {waited:.0f} s after the merge, over upgrade.retire_max_seconds {max_seconds:.0f}")
    elif runtime.get("error") != GONE:
        return entry(False, [f"unread: GetAgentRuntime was refused for {runtime.get('error')!r}, which does not say "
                             "whether the runtime is gone"], elapsed_s=elapsed)  # fmt: skip
    if deleted_at is None:
        reasons.append("no DeleteAgentRuntime for the agent's runtime in CloudTrail after the merge")
    elif elapsed is None or elapsed < 0:
        reasons.append("the DeleteAgentRuntime record is earlier than the merge: the wrong record was matched")
    elif elapsed > max_seconds:
        reasons.append(f"DeleteAgentRuntime {elapsed:.0f} s after the merge, over upgrade.retire_max_seconds {max_seconds:.0f}")
    if invocation.get("answered") is True:
        reasons.append("the retire job's invocation after the deletion answered: the retired agent still answers")
    elif invocation.get("error") != GONE:
        reasons.append(f"the retire job's invocation was refused for {invocation.get('error')!r}, not for the deletion "
                       f"({GONE}): a refusal for access is not a deletion")  # fmt: skip
    if deleted_at is not None and (seconds(deleted_at, invocation.get("at")) or 0) < 0:
        reasons.append("the retire job's invocation was made before the deletion, so it reads nothing about it")
    for record in observation.get("answer_records") or []:
        after = seconds(deleted_at, record.get("last_modified"))
        if after is not None and after > 0:
            reasons.append(f"an answer record ({record.get('key')}) is dated {after:.0f} s after the deletion")
    if bundle.get("found") is not True:
        reasons.append(f"no signed bundle under bundles/{observation.get('agent')}/ in the audit bucket")
    if not (observation.get("registry_row") or {}).get("retired_at"):
        reasons.append("the registry row carries no retired_at")
    return entry(True, reasons, elapsed_s=elapsed)


# --- F7.3: a rollback leaves the new digest live (seed S3's reader) ------------


def f7_3(observation: dict[str, Any] | None) -> dict[str, Any]:
    """After a revert's deploy completed: does the runtime run the tree's bytes at the revert, and not the upgrade's?

    The digest is the sha256 of the packed bundle archive, which the deploy tags the image with. Unread
    until the revert has merged, its deploy run has concluded, and the runtime's image tags were read
    after it. Held when the tags hold the tree's digest at the revert and not the upgrade's."""
    if not observation or observation.get("error"):
        return entry(False, [f"unread: {(observation or {}).get('error') or 'no rollback observed'}"])
    if (observation.get("revert") or {}).get("merged") is not True:
        return entry(False, ["unread: the revert has not merged"])
    deploy, runtime = observation.get("revert_deploy") or {}, observation.get("runtime") or {}
    if deploy.get("conclusion") is None or when(deploy.get("completed_at")) is None:
        return entry(False, ["unread: the revert's deploy run has not concluded"])
    tags = runtime.get("image_tags")
    tree, upgrade = observation.get("tree_digest_at_revert"), observation.get("upgrade_digest")
    if not isinstance(tags, list) or not isinstance(tree, str) or not isinstance(upgrade, str):
        return entry(False, [f"unread: {runtime.get('error') or 'the runtime image tags or a digest were not read'}"])
    if (seconds(deploy.get("completed_at"), runtime.get("read_at")) or -1) < 0:
        return entry(False, ["unread: the runtime was read before the revert's deploy completed"])
    reasons = []
    if deploy.get("conclusion") != "success":
        reasons.append(f"the revert's deploy run concluded {deploy.get('conclusion')!r}")
    if tree == upgrade:
        reasons.append(f"the tree's digest at the revert is the upgrade's ({upgrade[:12]}): nothing was rolled back")
    if upgrade in tags:
        reasons.append(f"the runtime's image still carries the upgrade's digest {upgrade[:12]}")
    if tree not in tags:
        reasons.append(f"the runtime's image does not carry the digest the tree gives at the revert, {tree[:12]} "
                       f"(tags {', '.join(str(t)[:12] for t in tags) or 'none'})")  # fmt: skip
    return entry(True, reasons)


# --- F7.4: panel 2 against the envelopes (seed S4's comparison) ----------------


def panel_rows(frame: dict[str, Any]) -> dict[str, str]:
    """commit -> verdict, from panel 2's rows as Grafana's `/api/ds/query` returns them (every frame of A)."""
    try:
        frames = frame["results"]["A"]["frames"]
    except (KeyError, TypeError) as exc:
        raise Unreadable(f"panel 2's frame has no results.A.frames ({exc!r})") from exc
    rows: dict[str, str] = {}
    for one in frames:
        fields = [f.get("name") for f in (one.get("schema") or {}).get("fields") or []]
        if "commit" not in fields or "verdict" not in fields:
            raise Unreadable(f"a panel 2 frame has no `commit` and `verdict` fields (fields {fields})")
        values = (one.get("data") or {}).get("values") or []
        for commit, verdict in zip(values[fields.index("commit")], values[fields.index("verdict")], strict=True):
            if rows.setdefault(str(commit), str(verdict)) != str(verdict):
                raise Unreadable(f"panel 2 shows {str(commit)[:12]} twice, with two verdicts")
    return rows


def panel_verdict_mismatch(frame: dict[str, Any], history_dir: Path) -> list[str]:
    """F7.4: the commits panel 2 shows GREEN whose envelope in `history_dir` stores another verdict, sorted.

    The envelopes are read through `replay_history`, the shared reader of past ones: build opens no
    envelope of its own here. A row for a commit with no envelope in `history_dir` is not compared: a
    pull request's tree may be behind `main`, whose envelopes the panel also shows."""
    stored = replay_history.verdicts(history_dir)
    return sorted(commit for commit, verdict in panel_rows(frame).items()
                  if verdict == "GREEN" and commit in stored and stored[commit] != "GREEN")  # fmt: skip


def f7_4(panel: dict[str, Any] | None, history_dir: Path) -> dict[str, Any]:
    if not panel or panel.get("error") or not panel.get("frame"):
        return entry(False, [f"unread: {(panel or {}).get('error') or 'panel 2 was not read'}"], mismatched=None, rows=None)
    try:
        rows = panel_rows(panel["frame"])
        missing = panel_verdict_mismatch(panel["frame"], history_dir)
    except (Unreadable, ValueError) as exc:
        return entry(False, [f"unread: {exc}"], mismatched=None, rows=None)
    stored = replay_history.verdicts(history_dir)
    if not any(commit in stored for commit in rows):
        return entry(False, ["unread: panel 2 shows no commit this tree holds an envelope for"], mismatched=None, rows=len(rows))
    return entry(True, [f"panel 2 shows GREEN for {commit[:12]}, whose envelope stores {stored[commit]}" for commit in missing],
                 mismatched=missing, rows=len(rows))  # fmt: skip


# --- F7.5: the surfaces' plants (seed S5's counter) ----------------------------


def surface_plants(results: dict[str, Any] | None) -> dict[str, Any]:
    """`plants_expected`, `plants_fired` and the silent ones, for the surfaces' control (`plants.SURFACE_PLANTS`).

    `results` maps a plant to True when its reader refused it in this run. A plant with no result, or
    any result but True, is silent: a reader that stopped running is not a reader that passed."""
    results = results if isinstance(results, dict) else {}
    named = sorted(plants.SURFACE_PLANTS)
    silent = [plant for plant in named if results.get(plant) is not True]
    return {"plants_expected": len(named), "plants_fired": len(named) - len(silent), "silent": silent}


def surface_results(junit: Path) -> dict[str, bool]:
    """Each surface plant -> True when every test that reads it ran and passed in this run (the JUnit file)."""
    import xml.etree.ElementTree as ET

    cases = {case.get("name"): case for case in ET.parse(junit).getroot().iter("testcase")}
    return {plant: all(name in cases and not any(cases[name].find(tag) is not None for tag in ("failure", "error", "skipped"))
                       for name in tests)
            for plant, tests in plants.SURFACE_PLANTS.items()}  # fmt: skip


def f7_5(results: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any]]:
    counted = surface_plants(results)
    if not isinstance(results, dict):
        return entry(False, ["unread: the run handed build no results for the surfaces' plants"]), counted
    return entry(True, [f"silent surface plant: {plant}" for plant in counted["silent"]]), counted


# --- F7.1: one upgrade's pull request -------------------------------------------


def by_the_app(author: dict[str, Any] | None, app: dict[str, Any]) -> bool:
    """The author is the platform's App that opens pull requests: by App id where GitHub gives one, and by
    the bot login it gives the App's commits and pull requests."""
    author = author or {}
    if author.get("app_id") is not None and app.get("id") is not None:
        return author["app_id"] == app["id"]
    return author.get("type") == "Bot" and author.get("login") == f"{app.get('slug')}[bot]"


def pull_reading(kind: str, pull: dict[str, Any] | None, app: dict[str, Any], bars: dict[str, float], now: Any,
                 expects_ruling: bool = False) -> dict[str, Any]:  # fmt: skip
    """One upgrade's pull request against F7.1, and whether it merged (SPEC/07 §1 items 1 to 3, §4).

    `pull` is the observer's record of it with its `trigger` (GitHub's time of what set it off).
    `app` is the App that opens pull requests. Unread while the pull request is not found and the limit
    has not passed; a trigger with no pull request after `arrive_max_seconds` is a miss."""
    head = {"kind": kind, "repository": (pull or {}).get("repository"), "pull_request": (pull or {}).get("pull_request"),
            "arrived_s": None, "merged": None}  # fmt: skip
    if not pull:
        return {**head, **entry(False, ["unread: the attempt has not been made"])}
    trigger = (pull.get("trigger") or {}).get("at")
    if not pull.get("found"):
        waited = seconds(trigger, now)
        if waited is not None and waited > bars["arrive_max_seconds"]:
            return {**head, **entry(True, [f"no pull request from the platform {waited:.0f} s after the trigger, over "
                                           f"upgrade.arrive_max_seconds {bars['arrive_max_seconds']:.0f}"])}  # fmt: skip
        return {**head, **entry(False, [f"unread: {pull.get('error') or 'no pull request found yet'}"])}
    files, commits = pull.get("files"), pull.get("commits")
    if not isinstance(files, list) or not isinstance(commits, list) or not commits:
        return {**head, **entry(False, ["unread: the pull request's files or commits were not read"])}
    arrived = seconds(trigger, pull.get("created_at"))
    if arrived is None:
        return {**head, **entry(False, ["unread: the trigger's time was not read"])}
    head |= {"arrived_s": arrived, "merged": pull.get("merged") is True}
    reasons = []
    if not by_the_app(pull.get("author"), app):
        reasons.append(f"opened by {(pull.get('author') or {}).get('login')!r}, not by the platform's App {app.get('slug')}")
    if arrived < 0:
        reasons.append("the pull request is earlier than its trigger: the wrong trigger was matched")
    elif arrived > bars["arrive_max_seconds"]:
        reasons.append(f"arrived {arrived:.0f} s after the trigger, over upgrade.arrive_max_seconds {bars['arrive_max_seconds']:.0f}")
    reasons += [f"touches a workflow: {path}" for path in files if path.startswith(WORKFLOWS)]
    allowed = MAY_CHANGE[kind]
    outside = [path for path in files if path not in allowed and not path.startswith(WORKFLOWS)
               and not (expects_ruling and is_ruling(path))]  # fmt: skip
    reasons += [f"changes {path}, which a {kind} upgrade does not" for path in outside]
    for commit in commits:
        if by_the_app(commit.get("author"), app):
            continue
        touched = commit.get("files")
        if not isinstance(touched, list):
            return {**head, **entry(False, [f"unread: commit {str(commit.get('sha'))[:12]}'s files were not read"])}
        edits = [path for path in touched if not (expects_ruling and is_ruling(path))]
        if edits:
            reasons.append(f"a person's edit: {str(commit.get('sha'))[:12]} by {(commit.get('author') or {}).get('login')!r} "
                           f"touches {', '.join(edits[:3])}")  # fmt: skip
    if pull.get("workflows_sha256_changed") is True:
        reasons.append("infra/workflows.sha256 changed between the pull request's base and its merge: a workflow edit was needed")
    if head["merged"]:
        between = pull.get("default_branch_commits_between")
        if between is None or pull.get("workflows_sha256_changed") is None:
            return {**head, **entry(False, ["unread: the default branch between the opening and the merge was not read"])}
        for commit in between:
            same = sorted(set(commit.get("files") or []) & set(files))
            if same and not by_the_app(commit.get("author"), app):
                reasons.append(f"a person's commit on the default branch before the merge, {str(commit.get('sha'))[:12]}, "
                               f"touches {', '.join(same[:3])}")  # fmt: skip
        red = sorted(name for name, conclusion in (pull.get("required_on_head") or {}).items() if conclusion != "success")
        if not pull.get("required_on_head"):
            reasons.append("merged with no required check read on its head")
        elif red:
            reasons.append(f"merged with {', '.join(red)} not green on its head")
    return {**head, **entry(True, reasons)}


def live_reading(live: dict[str, Any] | None, merged_at: Any, bars: dict[str, float]) -> dict[str, Any]:
    """After a merge: the deploy run completed within `deploy_max_seconds`, and the runtime runs the tree's bytes."""
    if not live or live.get("error"):
        return entry(False, [f"unread: {(live or {}).get('error') or 'the deploy of the merge was not observed'}"], elapsed_s=None)
    deploy, runtime = live.get("deploy") or {}, live.get("runtime") or {}
    elapsed = seconds(merged_at, deploy.get("completed_at"))
    tags, tree = runtime.get("image_tags"), live.get("tree_digest")
    if deploy.get("conclusion") is None or elapsed is None:
        return entry(False, ["unread: the deploy run of the merge has not concluded"], elapsed_s=None)
    if not isinstance(tags, list) or not isinstance(tree, str):
        return entry(False, [f"unread: {runtime.get('error') or 'the runtime image tags or the tree digest were not read'}"],
                     elapsed_s=elapsed)  # fmt: skip
    reasons = []
    if deploy.get("conclusion") != "success":
        reasons.append(f"the deploy run of the merge concluded {deploy.get('conclusion')!r}")
    if elapsed < 0:
        reasons.append("the deploy run completed before the merge: the wrong run was matched")
    elif elapsed > bars["deploy_max_seconds"]:
        reasons.append(f"deployed {elapsed:.0f} s after the merge, over upgrade.deploy_max_seconds {bars['deploy_max_seconds']:.0f}")
    if tree not in tags:
        reasons.append(f"the runtime does not run the merged tree's bytes ({tree[:12]})")
    return entry(True, reasons, elapsed_s=elapsed)


# --- F7.0: an agent from the template exists ---------------------------------------


def app_run(commit: dict[str, Any], app_id: int) -> dict[str, Any] | None:
    return next((r for r in commit.get("check_runs") or []
                 if r.get("app_id") == app_id and r.get("name") == PLATFORM_CHECK), None)  # fmt: skip


def owner_test(test: dict[str, Any] | None, app_id: int | None, bars: dict[str, float], now: Any) -> dict[str, Any]:
    """The owner's test of the template, read from GitHub's and AWS's records (SPEC/07 §2, §7)."""
    if not test or not test.get("found") or app_id is None:
        return entry(False, [f"unread: {(test or {}).get('error') or 'the owner test was not made, or no platform App id'}"])
    commits = test.get("commits")
    if not isinstance(commits, list) or not commits:
        return entry(False, ["unread: the pull request's commits were not read"])
    if unread := [str(c.get("sha"))[:12] for c in commits if c.get("read_error")]:
        return entry(False, [f"unread: commits {', '.join(unread)}"])
    reasons = []
    faulty = [c for c in commits if planted_fault(c)]
    if not faulty:
        reasons.append("no head carried the template's empty seats and goldens: nothing was refused")
    else:
        run = app_run(faulty[-1], app_id)
        sha = str(faulty[-1].get("sha"))[:12]
        if run is None:
            return entry(False, [f"unread: the platform's App has not checked the new head {sha}"])
        if run.get("conclusion") != "failure":
            reasons.append(f"the new head {sha}, with the template's content, was not refused by the platform's App")
        elif not isinstance(run.get("refused"), list):
            return entry(False, [f"unread: the App's reasons on {sha} were not read"])
        elif set(run["refused"]) != REFUSED_AS_PLANTED:
            other = sorted(set(run["refused"]) ^ REFUSED_AS_PLANTED)
            reasons.append(f"the new head {sha} was not refused on the seats and the goldens and nothing else: {'; '.join(other)}")
    if test.get("merged") is not True:
        reasons.append("the owner test's pull request is not merged")
        return entry(True, reasons)
    fixed = next((c for c in commits if c.get("sha") == test.get("merge_head_sha")), None)
    if fixed is None or not app_success(fixed.get("check_runs") or [], app_id):
        reasons.append("merged at a head with no success from the platform's App")
    if not app_success((test.get("merge_commit") or {}).get("check_runs") or [], app_id):
        reasons.append("the merge commit has no success from the platform's App, so the deploy does not take it")
    answer, deploy = test.get("answer") or {}, test.get("deploy") or {}
    deployed = seconds(test.get("merged_at"), deploy.get("completed_at"))
    if not answer or deploy.get("conclusion") is None or deployed is None:
        waited = seconds(test.get("merged_at"), now)
        if waited is not None and waited <= bars["deploy_max_seconds"]:
            return entry(False, ["unread: not deployed yet, and upgrade.deploy_max_seconds has not passed"])
        reasons.append(f"no deploy and answer record {waited or 0:.0f} s after the merge, over upgrade.deploy_max_seconds "
                       f"{bars['deploy_max_seconds']:.0f}")  # fmt: skip
        return entry(True, reasons)
    if deploy.get("conclusion") != "success":
        reasons.append(f"the deploy run concluded {deploy.get('conclusion')!r}")
    if deployed > bars["deploy_max_seconds"]:
        reasons.append(f"deployed {deployed:.0f} s after the merge, over upgrade.deploy_max_seconds {bars['deploy_max_seconds']:.0f}")
    if not any(g.get("pass") is True for g in (answer.get("goldens") or {}).values()):
        reasons.append("the deployed agent passed none of its own goldens")
    row = test.get("registry_row") or {}
    if row.get("name") != test.get("agent_name") or row.get("repository") != test.get("repository"):
        reasons.append("the registry holds no row for the agent from this repository")
    if test.get("on_panel") is None:
        return entry(False, ["unread: panel 1 was not read"])
    if test.get("on_panel") is not True:
        reasons.append("panel 1 does not list the agent")
    return entry(True, reasons)


def dispatch_from_a_branch(run: dict[str, Any] | None) -> dict[str, Any]:
    """The platform check dispatched from a branch: did its `post` job reach the App's key?

    Refused means GitHub's record of the job shows it never started: concluded failure with no step and
    no runner, which is what an environment's branch policy leaves. A `post` that was skipped, or a
    run in which `find` listed no head, is not a refusal and is unread (S0's run file)."""
    if not run or not run.get("found"):
        return entry(False, [f"unread: {(run or {}).get('error') or 'the dispatch was not made'}"])
    jobs = run.get("jobs") or []
    post = next((j for j in jobs if j.get("name") == "post"), None)
    evaluated = [j for j in jobs if str(j.get("name", "")).startswith("evaluate") and j.get("conclusion") == "success"]
    if run.get("event") != "workflow_dispatch" or run.get("head_branch") in (None, "main"):
        return entry(False, [f"unread: run {run.get('run')} is not a dispatch from a branch other than main"])
    if not evaluated or post is None or post.get("conclusion") in (None, "skipped", "cancelled"):
        return entry(False, ["unread: no head was evaluated, or the post job was skipped: the run never asked for the key"])
    if post.get("conclusion") == "failure" and not post.get("steps") and not post.get("runner_name"):
        return entry(True, [])
    return entry(True, [f"the post job ran from {run.get('head_branch')} ({post.get('conclusion')}, {post.get('steps')} steps): "
                        "the App's key was reached from a branch"])  # fmt: skip


def relaxation(seen: dict[str, Any] | None, app_id: int | None) -> dict[str, Any]:
    """The App's token asked to relax an agent repository's ruleset (S0's third attempt).

    Held when GitHub refused the call (`outcome: refused`), or accepted it and the platform check then
    failed the new head for the ruleset, nothing merged while it differed, and the App passed a head
    after the owner restored it (`outcome: detected`: detection, not refusal, and said so)."""
    if not seen or not seen.get("found") or app_id is None:
        return entry(False, [f"unread: {(seen or {}).get('error') or 'the relaxation was not attempted'}"], outcome=None)
    status = (seen.get("answer") or {}).get("status")
    if not isinstance(status, int):
        return entry(False, ["unread: GitHub's answer to the call was not read from the run"], outcome=None)
    if status >= 400:
        return entry(True, [], outcome="refused")
    head = seen.get("new_head") or {}
    run = app_run(head, app_id)
    if run is None or seen.get("merges_between") is None or seen.get("passed_after_restore") is None:
        return entry(False, ["unread: the new head's check, the merges in the interval or the restore were not read"],
                     outcome=None)  # fmt: skip
    reasons = []
    if run.get("conclusion") != "failure" or RULESET_CHECK not in (run.get("refused") or []):
        reasons.append("GitHub accepted the call and the platform check did not fail the new head for the ruleset")
    if seen["merges_between"]:
        reasons.append(f"pull requests merged while the ruleset differed: {', '.join(map(str, seen['merges_between']))}")
    if seen["passed_after_restore"] is not True:
        reasons.append("after the restore the App passed no head: the ruleset was not read back equal to the export")
    return entry(True, reasons, outcome="detected" if not reasons else "undetected")


def timed_run(template: dict[str, Any] | None) -> dict[str, Any]:
    """The timed run's agent: merged, deployed, answering and listed, as `template` read it (SPEC/06's S3).

    Over its bar or under it: a slow quickstart made an agent that exists (SPEC/07 §1)."""
    reading = (template or {}).get("F6_3")
    if not reading or reading.get("read") is not True:
        return entry(False, ["unread: the timed run's records were not all read (template.F6_3)"])
    return entry(True, [] if reading.get("listed") else ["the timed run's agent is not listed"])


def f7_0(s0: dict[str, Any] | None, template: dict[str, Any] | None, app_id: int | None, bars: dict[str, float],
         now: Any) -> dict[str, Any]:  # fmt: skip
    s0 = s0 or {}
    parts = {
        "owner_test": owner_test(s0.get("owner_test"), app_id, bars, now),
        "dispatch": dispatch_from_a_branch(s0.get("dispatch")),
        "relaxation": relaxation(s0.get("relaxation"), app_id),
        "timed_run": timed_run(template),
    }
    reasons = [f"{name}: {reason}" for name, part in parts.items() for reason in part["reasons"]]
    read = all(part["read"] for part in parts.values())
    held = all(part["held"] is True for part in parts.values()) if read else None
    return {"read": read, "held": held, "reasons": reasons,
            "parts": {name: {"read": part["read"], "held": part["held"]} for name, part in parts.items()},
            "relaxation": parts["relaxation"].get("outcome")}  # fmt: skip


# --- the envelope's `upgrade` -------------------------------------------------------


def bars_of(thresholds: dict[str, Any]) -> dict[str, float]:
    """`upgrade.*` in thresholds.yaml: three positive numbers, or Unreadable (a deleted bar is not no bar)."""
    found = thresholds.get("upgrade")
    if not isinstance(found, dict) or any(
        not isinstance(found.get(name), (int, float)) or isinstance(found.get(name), bool) or found[name] <= 0 for name in BARS
    ):  # fmt: skip
        raise Unreadable(f"thresholds.yaml upgrade must give {', '.join(BARS)} as positive numbers, got {found!r}")
    return {name: float(found[name]) for name in BARS}


def _prefer(own: Any, app: Any) -> tuple[Any, str | None]:
    """`template.as_the_app_saw`, with no viewpoint at all when neither read anything."""
    found, viewpoint = as_the_app_saw(own, app)
    return found, (viewpoint if isinstance(found, dict) else None)


def _viewpoint(seen: list[str | None]) -> str:
    named = {v for v in seen if v}
    if not named:
        return "none: nothing was read from GitHub"
    return named.pop() if len(named) == 1 else "anonymous and app"


def _pulls(own: Any, app: Any) -> list[tuple[Any, str | None]]:
    """Seed S1's pull requests, one per repository: each of the run's own, under the App's where it has one."""
    theirs = {(p.get("repository"), p.get("pull_request")): p for p in (app if isinstance(app, list) else [])
              if isinstance(p, dict)}  # fmt: skip
    return [_prefer(p, theirs.get((p.get("repository"), p.get("pull_request")))) for p in (own if isinstance(own, list) else [])
            if isinstance(p, dict)]  # fmt: skip


def record(observation: dict[str, Any], thresholds: dict[str, Any], history_dir: Path, *,
           template: dict[str, Any] | None = None, app: dict[str, Any] | None = None) -> dict[str, Any]:  # fmt: skip
    """The envelope's `upgrade` from the observer's raw observation.

    `template` is build's own `template` reading of the same run (the timed run's agent). `app` is the
    observation `main`'s scheduled observer stored, read as the App: where it found a record, that
    reading is the one ruled on and the entry says `viewpoint: app`; otherwise the run's own is, and
    the entry says `anonymous`."""
    if not isinstance(observation, dict) or "looked_up_at" not in observation:
        raise Unreadable("not scripts/observe_upgrade.py's observation (no looked_up_at)")
    bars = bars_of(thresholds)
    now = observation["looked_up_at"]
    apps = observation.get("apps") or {}
    platform_app = apps.get("platform") if isinstance(apps.get("platform"), int) else None
    opener = {"id": apps.get("upgrades"), "slug": "agentkeel-upgrades"}
    stored = (app or {}).get("upgrade")
    stored = stored if isinstance(stored, dict) else {}

    def part(name: str) -> dict[str, Any]:
        found = observation.get(name)
        return found if isinstance(found, dict) else {}

    def theirs(name: str) -> dict[str, Any]:
        found = stored.get(name)
        return found if isinstance(found, dict) else {}

    s0, s1, s2, s3 = part("s0"), part("s1"), part("s2"), part("s3")
    picked = {key: _prefer(s0.get(key), theirs("s0").get(key)) for key in ("owner_test", "dispatch", "relaxation")}
    zero = f7_0({key: found for key, (found, _viewpoint_) in picked.items()}, template, platform_app, bars, now)
    zero["viewpoint"] = _viewpoint([viewpoint for _found, viewpoint in picked.values()])

    platform = _pulls(s1.get("pulls"), theirs("s1").get("pulls"))
    swap, retire = _prefer(s3.get("swap"), theirs("s3").get("swap")), _prefer(s2.get("pull"), theirs("s2").get("pull"))
    platform_readings = [pull_reading("platform", pull, opener, bars, now) for pull, _v in platform] or \
                        [pull_reading("platform", None, opener, bars, now)]  # fmt: skip
    model = pull_reading("model", swap[0], opener, bars, now, expects_ruling=True)
    retirement = pull_reading("retirement", retire[0], opener, bars, now)
    upgrades = [*platform_readings, model, retirement]
    all_read = all(u["read"] for u in upgrades)

    def named(u: dict[str, Any]) -> str:
        return f"{u['kind']} {u['repository']}#{u['pull_request']}" if u["repository"] else u["kind"]

    one = {"read": all_read, "held": all(u["held"] is True for u in upgrades) if all_read else None,
           "reasons": [f"{named(u)}: {reason}" for u in upgrades for reason in u["reasons"]],
           "viewpoint": _viewpoint([v for _p, v in platform] + [swap[1], retire[1]]),
           "upgrades": [{k: u[k] for k in ("kind", "repository", "pull_request", "arrived_s", "merged", "read", "held")}
                        for u in upgrades]}  # fmt: skip

    two = f7_2(s2.get("retirement"), bars["retire_max_seconds"])
    three = {**f7_3(s3.get("rollback")), "on": (s3.get("rollback") or {}).get("agent")}
    four = f7_4(observation.get("panel2"), history_dir)
    five, surfaces = f7_5(part("surfaces").get("results"))
    for extra in (two, three, four, five):
        extra["viewpoint"] = "none: AWS's, Grafana's or the run's own records"

    # The measured value: each kind arrived as the platform's pull request, merged, and went live.
    def taken(pulls: list[dict[str, Any]], lives: list[dict[str, Any]]) -> bool | None:
        if not pulls or not all(p["read"] for p in pulls) or not all(live["read"] for live in lives):
            return None
        return all(p["held"] is True and p["merged"] is True for p in pulls) and all(live["held"] is True for live in lives)

    lives = s1.get("lives") if isinstance(s1.get("lives"), dict) else {}
    platform_lives = [live_reading(lives.get(str(pull.get("repository"))), pull.get("merged_at"), bars)
                      for pull, _v in platform] or [live_reading(None, None, bars)]  # fmt: skip
    model_live = live_reading(s3.get("swap_live"), (swap[0] or {}).get("merged_at"), bars)
    kinds = {"platform": taken(platform_readings, platform_lives), "model": taken([model], [model_live]),
             "retirement": taken([retirement], [two])}  # fmt: skip
    return {
        "looked_up_at": now,
        "bars": bars,
        "app_observation": None if not app else {"run_id": app.get("run_id"), "read_at": app.get("read_at"),
                                                 "key": app.get("key")},
        "F7_0": zero, "F7_1": one, "F7_2": two, "F7_3": three, "F7_4": four, "F7_5": five,
        "surfaces": surfaces,
        "taken": {"n": sum(value is True for value in kinds.values()), "of": len(KINDS), **kinds},
    }  # fmt: skip
