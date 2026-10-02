"""verdict.template: build's readings of claim 6's live observations (SPEC/06 §4; P5).

`scripts/observe_template.py` writes raw lists only (BLOCK 3): what GitHub,
AWS and Grafana returned, each with the time it was read. Everything that
compares one record with another, or rules on one, is here, and only
`build` calls it. The result is the envelope's optional `template`; the gate
rules nothing on it, and row 6's Measured cell reads it (`gate.template_misses`).

One entry per live falsifier, each `read` (every record it needs was found),
`held` (the control did what SPEC/06 §7 states; null when unread) and
`reasons` (each miss, named):

- **F6.1, live half.** The timed run's first pull request: at every commit
  of it whose agent folder carried a planted fault (a seat null or empty, or
  goldens under one live ordinary and one live trap), no successful check
  run from the platform's App; at least one such commit (the run is refused
  before it is merged); merged, with the App's success on the merged head.
- **F6.2.** S2's pull request: not merged, a check run of the platform
  check's name from another app concluded success on its head (the stand-in
  was there), and none from the platform's App did.
- **F6.3.** S3's records, each time GitHub's or AWS's own: the repository's
  `created_at`, the first pull request's merge, the completion of the deploy
  run that wrote the agent's **first** answer record (GitHub's), and that
  record's `LastModified` (AWS's), with one of its own goldens passed.
  Elapsed is the last less `created_at`; held when it is at most
  `quickstart.max_seconds`. The registry row must hold the agent for this
  repository (`listed`), and is not timed: its `deployed_at` is a runner's
  clock, rewritten by every redeploy (threshold-owner N8 on M06 PR 2), and
  the deploy run that wrote it ends after it. Panel 1's listing is read under
  F6.4, not timed: the panel reads the registry when it is asked.
- **F6.4.** Panel 1's rows against a registry scan, by name: held when the
  panel names no agent the registry does not hold.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

PLATFORM_CHECK = "platform-check"  # the required context's name (infra/ruleset/agent.json)
# The names the platform's App posts its two planted refusals under (src/validate/agent.py), so that
# "refused" can be read as refused for the fault that was planted (M07 PR 2; re-read of 69f8383, B).
SEAT_CHECK = "seats assigned, each a login that administers the repository"
GOLDENS_CHECK = "an agent's goldens: one ordinary and one trap at least, citing its own data"
SEAT_SLUGS = ("product", "rule-owner", "data-owner", "tool-owner", "threshold-owner", "security", "engineering")


class Unreadable(Exception):
    """An observation that is not in the observer's shape: build refuses it."""


# --- F6.4: panel 1 against the registry (S4's comparison) -------------------


def panel_names(frame: dict[str, Any]) -> list[str]:
    """The `name` column of panel 1's rows, as Grafana's `/api/ds/query` returns them (every frame of A)."""
    try:
        frames = frame["results"]["A"]["frames"]
    except (KeyError, TypeError) as exc:
        raise Unreadable(f"panel 1's frame has no results.A.frames ({exc!r})") from exc
    names: list[str] = []
    for one in frames:
        fields = [f.get("name") for f in (one.get("schema") or {}).get("fields") or []]
        if "name" not in fields:
            raise Unreadable(f"a panel 1 frame has no `name` field (fields {fields})")
        names += [str(v) for v in (one.get("data") or {}).get("values", [])[fields.index("name")]]
    return names


def registry_names(registry: dict[str, Any]) -> list[str]:
    """The `name` of every item in a DynamoDB scan of the registry, as the API returns it."""
    items = registry.get("Items") if isinstance(registry, dict) else None
    if not isinstance(items, list):
        raise Unreadable("the registry scan has no Items list")
    try:
        return [item["name"]["S"] for item in items]
    except (KeyError, TypeError) as exc:
        raise Unreadable(f"a registry item has no name ({exc!r})") from exc


def panel_not_in_registry(frame: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    """F6.4: the agents panel 1 shows that the registry does not hold, by name, sorted (BLOCK 3)."""
    held = set(registry_names(registry))
    return sorted({name for name in panel_names(frame) if name not in held})


# --- helpers ----------------------------------------------------------------


def when(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def entry(read: bool, reasons: list[str], **extra: Any) -> dict[str, Any]:
    return {"read": read, "held": (not reasons) if read else None, "reasons": reasons, **extra}


def app_success(runs: list[dict[str, Any]], app_id: int) -> bool:
    return any(r.get("app_id") == app_id and r.get("conclusion") == "success" for r in runs)


def bound_to_the_app(rulesets: Any, app_id: int) -> bool:
    """The repository's live ruleset requires `platform-check` from the platform's App (cold review F3, F6)."""
    return isinstance(rulesets, list) and any(
        r.get("context") == PLATFORM_CHECK and r.get("integration_id") == app_id for r in rulesets)


def planted_checks(commit: dict[str, Any]) -> set[str]:
    """The App's check names a commit's planted faults must be refused under."""
    faults = planted_fault(commit)
    return ({SEAT_CHECK} if any(f.startswith(("seats", "no seats")) for f in faults) else set()) | (
        {GOLDENS_CHECK} if any(f.startswith("goldens") for f in faults) else set())


def planted_fault(commit: dict[str, Any]) -> list[str]:
    """What is wrong with a commit's agent folder as F6.1 counts it; [] if nothing."""
    faults = []
    seats = commit.get("seats")
    if not isinstance(seats, dict):
        faults.append("no seats read")
    else:
        empty = [s for s in SEAT_SLUGS if not isinstance(seats.get(s), str) or not seats[s].strip()]
        if empty:
            faults.append(f"seats unassigned: {', '.join(empty)}")
    live = [g.get("kind") for g in commit.get("goldens") or [] if g.get("retired") is None]
    short = [k for k in ("ordinary", "trap") if live.count(k) < 1]
    if short:
        faults.append(f"goldens under the minimum: no live {' or '.join(short)}")
    return faults


# --- the four readings ------------------------------------------------------


def f6_1(s3: dict[str, Any] | None, app_id: int | None) -> dict[str, Any]:
    if not s3 or not s3.get("found") or app_id is None:
        return entry(False, [f"unread: {(s3 or {}).get('error') or 'no S3 observation or no platform App id'}"])
    pr = s3.get("first_pr") or {}
    commits = pr.get("commits")
    if not isinstance(commits, list) or not commits:
        return entry(False, ["unread: the first pull request's commits were not read"])
    if unread := [str(c.get("sha"))[:12] for c in commits if c.get("read_error")]:
        # A commit that could not be read is not a planted fault (cold review F5 on M06 PR 2).
        return entry(False, [f"unread: commits {', '.join(unread)} of the first pull request"])
    reasons = []
    if not bound_to_the_app(s3.get("required_checks"), app_id):
        reasons.append("the repository's ruleset does not require platform-check from the platform's App")
    faulty = [c for c in commits if planted_fault(c)]
    # Refused first (second cold read, F4; S3's run file): its first commit carries a planted fault and the App
    # failed it. A fault pushed over before the App reached it was never refused.
    first = commits[0]
    failed = next((r for r in first.get("check_runs") or []
                   if r.get("app_id") == app_id and r.get("conclusion") == "failure"), None)  # fmt: skip
    if not planted_fault(first):
        reasons.append("the first pull request's first commit carried no planted fault: nothing was refused")
    elif failed is None:
        reasons.append("the first commit's planted fault has no failure from the platform's App: it was never refused")
    elif not isinstance(failed.get("refused"), list):
        # Any failure from the App used to count (M07 PR 2; re-read of 69f8383, B): a head refused for the
        # hidden bypass_actors alone was read as refused for its seats. The App's reasons are read now.
        return entry(False, ["unread: the App's reasons for refusing the first commit were not read"])
    elif missing := sorted(planted_checks(first) - set(failed["refused"])):
        reasons.append(f"the first commit was refused, and not for its planted fault: the App did not refuse it on {'; '.join(missing)}")
    for c in faulty:
        if app_success(c.get("check_runs") or [], app_id):
            reasons.append(f"{str(c.get('sha'))[:12]} passed the platform check with {'; '.join(planted_fault(c))}")
    if pr.get("merged") is not True:
        reasons.append("the first pull request was not merged")
    else:
        head = next((c for c in commits if c.get("sha") == pr.get("merge_head_sha")), None)
        if head is None or not app_success(head.get("check_runs") or [], app_id):
            reasons.append("merged at a head with no success from the platform's App")
    return entry(True, reasons, faulty_commits=len(faulty))


def f6_2(s2: dict[str, Any] | None, app_id: int | None) -> dict[str, Any]:
    if not s2 or not s2.get("found") or app_id is None:
        return entry(False, [f"unread: {(s2 or {}).get('error') or 'no S2 observation or no platform App id'}"])
    runs = s2.get("check_runs") or []
    reasons = []
    # Read before the unread return below (M07 PR 2; re-read of 69f8383, A): GitHub gives a merged pull
    # request the state "unknown", so a merged S2 was read as unread, not as the miss it is.
    if s2.get("merged") is True:
        return entry(True, ["S2's pull request merged"])
    if s2.get("merged") is not False:
        return entry(False, ["unread: whether S2's pull request merged was not read"])
    # Mergeable, not only merged (cold review F3 on M06 PR 2): GitHub's own reading. Held on `blocked` alone:
    # `clean`, `unstable` and `has_hooks` can merge, and `dirty`, `behind` or `draft` block for another reason
    # (second cold read, F1). `unknown` is GitHub still computing, and is unread, as no reading is.
    state = s2.get("mergeable_state")
    if state in (None, "unknown"):
        return entry(False, [f"unread: S2's mergeable_state is {state!r}"])
    if state != "blocked":
        reasons.append(f"S2's mergeable_state is {state!r}, not 'blocked' by its required check")
    if not bound_to_the_app(s2.get("required_checks"), app_id):
        reasons.append("S2's repository does not require platform-check from the platform's App, so its refusal "
                       "is not that control's")  # fmt: skip
    if app_success(runs, app_id):
        reasons.append("the platform's App passed S2's head: the attempt carried no fault the check refuses")
    stand_in = [r for r in runs if r.get("name") == PLATFORM_CHECK and r.get("app_id") != app_id
                and r.get("conclusion") == "success"]  # fmt: skip
    if not stand_in:
        reasons.append("no stand-in check run of the platform check's name succeeded on S2's head: not made as planted")
    return entry(True, reasons)


def f6_3(s3: dict[str, Any] | None, max_seconds: float, panel: list[str] | None = None) -> dict[str, Any]:
    if not s3 or not s3.get("found"):
        return entry(False, [f"unread: {(s3 or {}).get('error') or 'no S3 observation'}"], elapsed_s=None, records={},
                     listed=False)  # fmt: skip
    pr, deploy = s3.get("first_pr") or {}, s3.get("deploy") or {}
    answer, row = s3.get("answer") or {}, s3.get("registry_row") or {}
    records = {
        "created_at": s3.get("created_at"),
        "merged_at": pr.get("merged_at"),
        "deployed_at": deploy.get("completed_at") if deploy.get("conclusion") == "success" else None,
        "answered_at": answer.get("last_modified")
        if any(g.get("pass") is True for g in (answer.get("goldens") or {}).values()) else None,
    }  # fmt: skip
    # The registry and panel 1 listing it (cold review F2 on M06 PR 2): both, read, neither timed.
    in_registry = row.get("name") == s3.get("agent_name") and row.get("repository") == s3.get("repository")
    on_panel = panel is not None and s3.get("agent_name") in panel
    listed = in_registry and on_panel
    unread = [name for name, value in records.items() if when(value) is None]
    unread += ([] if in_registry else ["registry row"]) + ([] if on_panel else ["panel 1's row"])
    if unread:
        return entry(False, [f"unread: {', '.join(unread)}"], elapsed_s=None, records=records, listed=listed)
    start = when(records["created_at"])
    elapsed = max((when(v) - start).total_seconds() for v in records.values())  # type: ignore[operator]
    reasons = [f"{elapsed:.0f} s, over quickstart.max_seconds {max_seconds:.0f}"] if elapsed > max_seconds else []
    if any((when(v) - start).total_seconds() < 0 for v in records.values()):  # type: ignore[operator]
        reasons.append("a record is earlier than the repository's created_at: the wrong record was matched")
    return entry(True, reasons, elapsed_s=round(elapsed, 1), records=records, listed=listed)


def f6_4(panel: dict[str, Any] | None, registry: dict[str, Any] | None) -> dict[str, Any]:
    if not panel or panel.get("error") or not registry or registry.get("error"):
        why = (panel or {}).get("error") or (registry or {}).get("error") or "panel 1 or the registry not read"
        return entry(False, [f"unread: {why}"], not_in_registry=None)
    try:
        missing = panel_not_in_registry(panel["frame"], registry["scan"])
    except (Unreadable, KeyError) as exc:
        return entry(False, [f"unread: {exc}"], not_in_registry=None)
    return entry(True, [f"panel 1 shows {name}, which the registry does not hold" for name in missing],
                 not_in_registry=missing)  # fmt: skip


def as_the_app_saw(own: Any, app: Any) -> tuple[Any, str]:
    """One GitHub record, and the viewpoint it is ruled on (SPEC/07 section 2 "The viewpoint").

    The App's stored record where `main`'s scheduled observer found it, laid over the run's own, so
    what only the run reads (AWS's records, under its own roles) stays the run's. Otherwise the run's
    own, read with a token that has no rights in the organisation."""
    if isinstance(app, dict) and app.get("found"):
        mine = own if isinstance(own, dict) else {}
        return {**mine, **{k: v for k, v in app.items() if v is not None}}, "app"
    return own, "anonymous"


def record(observation: dict[str, Any], max_seconds: float, app: dict[str, Any] | None = None) -> dict[str, Any]:
    """The envelope's `template` from the observer's raw observation.

    `app` (M07 PR 2; milestones/M07/open.md row 3) is the observation `main`'s scheduled observer
    stored, read as the platform's observer App. A pull request's own run asks GitHub with a token
    that has no rights in the organisation, and GitHub's `mergeable_state` depends on who asks: the
    owner read `blocked` where CI read `unstable` (M06's second finding). Each GitHub reading now says
    which viewpoint it was ruled on, and F6.2 keeps the raw state beside its verdict."""
    if not isinstance(observation, dict) or "looked_up_at" not in observation:
        raise Unreadable("not scripts/observe_template.py's observation (no looked_up_at)")
    app_id = observation.get("platform_app_id")
    app_id = app_id if isinstance(app_id, int) and not isinstance(app_id, bool) else None
    stored = (app or {}).get("template")
    stored = stored if isinstance(stored, dict) else {}
    (s2, s2_seen), (s3, s3_seen) = (as_the_app_saw(observation.get(name), stored.get(name)) for name in ("s2", "s3"))
    panel = observation.get("panel") or {}
    try:
        names = panel_names(panel["frame"]) if panel.get("frame") and not panel.get("error") else None
    except Unreadable:
        names = None
    return {
        "looked_up_at": observation["looked_up_at"],
        "max_seconds": max_seconds,
        "platform_app_id": app_id,
        "app_observation": None if not app else {"run_id": app.get("run_id"), "read_at": app.get("read_at"),
                                                 "key": app.get("key")},
        "F6_1": {**f6_1(s3, app_id), "viewpoint": s3_seen},
        "F6_2": {**f6_2(s2, app_id), "viewpoint": s2_seen,
                 "mergeable_state": s2.get("mergeable_state") if isinstance(s2, dict) else None},
        "F6_3": {**f6_3(s3, max_seconds, names), "viewpoint": s3_seen},
        "F6_4": f6_4(observation.get("panel"), observation.get("registry")),
    }  # fmt: skip
