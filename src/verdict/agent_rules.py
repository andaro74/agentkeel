"""build's reading of M09's plant run: the envelope's `agent_rules` field (SPEC/09 §4, §6; P5).

`scripts/observe_rules.py` writes what the fixture agent's answer record, the
built guardrail's read-back (or the registry row, SPEC/09 §9 cut 3), the
platform check's results on the three heads and the agent repository's rule
files at the merge commit hold; this module rules on those raw observations
into one entry per falsifier, `{read, held, reasons, ...}`, and the measured
value, planted rules fired n of m. `build` imports it and records the result
in the optional envelope field `agent_rules`; the gate rules nothing on it,
and the ledger's row 9 reading (`gate.rules_misses`) is what turns it into a
measurement. A silent plant in an agent repository stops no merge at M09
(ADR-0014 decision 5).

Two readers the seed tests name (`tests/test_m09_seeds.py`, S3; the ruling
`milestones/M09/rulings/pr1-engineering.md`):

- `plants(record, blocks)`: each plant the agent's controls name, read from
  the answer record's per-golden observation by the membership rule `build`
  has applied to refagent's plants since M03 PR 3: fired only when its
  observation says `stop_reason: guardrail_intervened` **and** its named
  rule is among `guardrail_topics`, the topic names the converse trace
  recorded. Blocked by another rule, or answered, is **silent**, and the
  reason names the golden and what the trace recorded. Returns `{read, held,
  expected, fired, reasons, fired_by}`.
- `guardrail(record, read_back, tree_digest)`: F9.1. The pin the answer
  record names is not null and not refagent's; the guardrail read back (or
  the registry row's record of it) is that pin, and its version description
  carries `rules sha256 <tree_digest>`, the digest the observer computed
  itself from the agent repository's merge commit and `rules/baseline.yaml`
  on `main`. The record's pin is the stack's: `deploy.yml` passes the stack's
  outputs to `build answer`, and the construct conditions the agent role's
  invoke on that resource, so no other guardrail could have been on the call.

The attempt's facts are GitHub's, AWS's and the record's, never a person's.
A reader decides nothing an observation does not show; a part it cannot find
is unread, which row 9 reads as RED (SPEC/09 §4).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
PLATFORM_MANIFEST = ROOT / "agents" / "refagent" / "manifest.yaml"
READINGS = ("F9_1", "F9_2", "F9_3", "F9_4")
# The platform check's name for the rules reading (src/validate/agent.evaluate), as its App posts it.
RULES_CHECK = "an agent's rules on the platform baseline, add-only, each plant naming a rule it builds"
BLOCKED = "guardrail_intervened"


class Unreadable(Exception):
    """The observation is not in the observer's shape."""


def _entry(read: bool, reasons: list[str], **extra: Any) -> dict[str, Any]:
    return {"read": read, "held": (not reasons) if read else None, "reasons": reasons, **extra}


def platform_pin(path: Path = PLATFORM_MANIFEST) -> dict[str, Any] | None:
    """refagent's pin, from its manifest in the tree: the one an agent with rules/ may not carry."""
    try:
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    pin = manifest.get("guardrail") if isinstance(manifest, dict) else None
    return pin if isinstance(pin, dict) else None


def pin_text(pin: Any) -> str | None:
    if not isinstance(pin, dict) or not pin.get("id"):
        return None
    return f"{pin.get('id')}:{pin.get('version')}"


# --- S3: a plant read from the answer record ----------------------------------


def plants(record: dict[str, Any] | None, blocks: dict[str, str]) -> dict[str, Any]:
    """Each plant `blocks` names, read from the record's observations by the membership rule (F9.3)."""
    expected = len(blocks)
    observations = record.get("observations") if isinstance(record, dict) else None
    if not isinstance(observations, dict):
        why = "no answer record" if not isinstance(record, dict) else "the answer record carries no observations"
        return _entry(False, [f"{why}: no plant can be read"], expected=expected, fired=0, fired_by={})
    reasons: list[str] = []
    fired_by: dict[str, list[str]] = {}
    fired = 0
    for golden_id, rule in sorted(blocks.items()):
        observation = observations.get(golden_id)
        if not isinstance(observation, dict):
            reasons.append(f"{golden_id}: no observation in the answer record (planted for {rule!r})")
            continue
        topics = observation.get("guardrail_topics") or []
        topics = [t for t in topics if isinstance(t, str)] if isinstance(topics, list) else []
        stop = observation.get("stop_reason")
        if stop != BLOCKED:
            reasons.append(f"{golden_id}: answered (stop_reason {stop!r}, topics {topics}), not blocked by {rule!r}: silent")
        elif rule not in topics:
            reasons.append(f"{golden_id}: blocked by {topics}, its named rule {rule!r} absent from the trace: silent")
        else:
            fired += 1
            fired_by[golden_id] = topics
    if expected == 0:
        reasons.append("no plant is named: a count of none cannot say a rule fired")
    return _entry(True, reasons, expected=expected, fired=fired, fired_by=fired_by)


# --- F9.1: the pin and the digest -----------------------------------------------


def guardrail(record: dict[str, Any] | None, read_back: dict[str, Any] | None, tree_digest: str | None,
              platform: dict[str, Any] | None = None) -> dict[str, Any]:  # fmt: skip
    """The record's pin is the agent's own, and the guardrail read back carries the tree's digest (F9.1).

    `read_back` is the built guardrail as GetGuardrail returned it (`source: read_back`) or, when that
    read is not granted (SPEC/09 §9 cut 3), the registry row's record of it (`source: registry`): either
    way `{id, version, description}`. `platform` is refagent's pin; left out, it is read from the tree."""
    platform = platform_pin() if platform is None else platform
    pin = record.get("guardrail") if isinstance(record, dict) else None
    out = {"pin": pin_text(pin), "digest_expected": tree_digest, "digest_read": None,
           "source": (read_back or {}).get("source") if isinstance(read_back, dict) else None}  # fmt: skip
    if not isinstance(record, dict):
        return _entry(False, ["no answer record: the pin the run carried is unread"], **out)
    reasons: list[str] = []
    if not isinstance(pin, dict) or not pin.get("id") or not pin.get("version"):
        reasons.append("the answer record names no guardrail: the pin the run carried is unread")
    elif platform and pin.get("id") == platform.get("id"):
        reasons.append(f"the pin the answer record names, {pin_text(pin)}, is refagent's: the agent's rules are not in it")
    if tree_digest is None:
        reasons.append("the digest of the baseline and the agent's rule files could not be computed from the tree")
    if not isinstance(read_back, dict):
        reasons.append("the built guardrail was not read back and the registry row records none: the description's digest is unread")
        return _entry(True, reasons, **out)
    description = read_back.get("description")
    out["digest_read"] = description.rsplit(" ", 1)[-1] if isinstance(description, str) and description else None
    if isinstance(pin, dict) and (read_back.get("id") != pin.get("id") or str(read_back.get("version")) != str(pin.get("version"))):
        reasons.append(f"the guardrail read back is {read_back.get('id')}:{read_back.get('version')}, not the record's "
                       f"pin {pin_text(pin)}")  # fmt: skip
    if tree_digest is not None and description != f"rules sha256 {tree_digest}":
        reasons.append(f"the version description reads {description!r}, not 'rules sha256 {tree_digest}': the rules "
                       f"on the call are not the baseline and the agent's files as the tree holds them")  # fmt: skip
    return _entry(True, reasons, **out)


# --- F9.2 and F9.4: the platform check's results on the three heads --------------


def _check(pull: dict[str, Any] | None) -> dict[str, Any] | None:
    """The platform's check run on a head, as the observer recorded it; None when unread."""
    if not isinstance(pull, dict) or not pull.get("found"):
        return None
    runs = [r for r in pull.get("check_runs") or [] if isinstance(r, dict) and r.get("name") == "platform-check"]
    return runs[-1] if runs else None


def heads(pulls: dict[str, Any] | None) -> dict[str, Any]:
    """F9.4: the first and third heads admitted and merged, the second refused on the rules file and not merged."""
    pulls = pulls if isinstance(pulls, dict) else {}
    reasons: list[str] = []
    states: dict[str, str] = {}
    if not any(isinstance(pulls.get(step), dict) and pulls[step].get("found") for step in ("first", "second", "third")):
        return _entry(False, ["no pull request of the fixture repository was read"], heads=states)
    for step, admitted in (("first", True), ("second", False), ("third", True)):
        pull, check = pulls.get(step), _check(pulls.get(step))
        if check is None:
            states[step] = "unread"
            reasons.append(f"{step}: no platform-check run read on its head")
            continue
        refused = check.get("refused")
        passed = check.get("conclusion") == "success"
        states[step] = "admitted" if passed else "refused"
        merged = bool(pull.get("merged"))
        if admitted:
            if not passed:
                reasons.append(f"{step}: the platform check refused the head on {refused}: an agent's own pin or its "
                               f"guardrail golden was refused (F9.4)")  # fmt: skip
            if not merged:
                reasons.append(f"{step}: not merged")
        else:
            if passed:
                reasons.append(f"{step}: the platform check admitted the weakened rules file (F9.2)")
            elif refused is None:
                reasons.append(f"{step}: refused, and GitHub gave no summary saying on what")
            elif set(refused) != {RULES_CHECK}:
                reasons.append(f"{step}: refused on {refused}, not on the rules file alone")
            if merged:
                reasons.append(f"{step}: merged with a weakened baseline rule (F9.2)")
    return _entry(True, reasons, heads=states)


def weakened(pulls: dict[str, Any] | None, read_back: dict[str, Any] | None, baseline: dict[str, Any] | None) -> dict[str, Any]:
    """F9.2: the weakened file refused naming EMAIL, and the built guardrail holds every baseline rule."""
    second, check = (pulls or {}).get("second") if isinstance(pulls, dict) else None, _check((pulls or {}).get("second") if isinstance(pulls, dict) else None)
    reasons: list[str] = []
    if check is None:
        return _entry(False, ["the second pull request's platform-check run was not read"], refused_on=None)
    summary = check.get("summary") or ""
    refused = check.get("refused")
    if check.get("conclusion") == "success":
        reasons.append("the platform check admitted the weakened rules file")
    elif not refused or RULES_CHECK not in refused:
        reasons.append(f"the platform check refused the head on {refused}, not on the rules file")
    elif "EMAIL" not in summary:
        reasons.append("the refusal does not name EMAIL, the entity the file weakens")
    if isinstance(second, dict) and second.get("merged"):
        reasons.append("the second pull request merged")
    wanted = {(e.get("entity"), e.get("action")) for e in (baseline or {}).get("pii") or [] if isinstance(e, dict)}
    if isinstance(read_back, dict) and read_back.get("source") == "read_back":
        held = {(e.get("entity"), e.get("action")) for e in read_back.get("pii") or [] if isinstance(e, dict)}
        if missing := sorted(wanted - held):
            reasons.append(f"the built guardrail lacks the baseline's {missing}")
    else:
        reasons.append("the built guardrail was not read back: whether it holds every baseline rule rests on F9_1's digest")
    return _entry(True, reasons, refused_on=refused)


# --- the whole reading, for build ---------------------------------------------------


def blocks_of(rules: dict[str, Any] | None) -> dict[str, str]:
    """Every plant the agent's two controls name, as the observer fetched them at the merge commit."""
    named: dict[str, str] = {}
    for control in ("guardrail", "redteam"):
        doc = (rules or {}).get(control) if isinstance(rules, dict) else None
        blocks = doc.get("blocks") if isinstance(doc, dict) else None
        for golden_id, rule in (blocks or {}).items() if isinstance(blocks, dict) else []:
            if isinstance(golden_id, str) and isinstance(rule, str) and rule:
                named[golden_id] = rule
    return named


def record(observation: dict[str, Any]) -> dict[str, Any]:
    """`scripts/observe_rules.py`'s observation, ruled into the envelope's `agent_rules` (SPEC/09 §4).

    A run the observer wrote as not made is every falsifier unread with its reason; the gate rules
    nothing on the field, and row 9's cell reads it (`gate.rules_misses`)."""
    if not isinstance(observation, dict):
        raise Unreadable("not the observer's shape: not a mapping")
    answer = observation.get("answer") if isinstance(observation.get("answer"), dict) else None
    read_back = observation.get("read_back") if isinstance(observation.get("read_back"), dict) else None
    registry = observation.get("registry") if isinstance(observation.get("registry"), dict) else None
    if read_back is None and registry and registry.get("guardrail_id"):
        read_back = {"source": "registry", "id": registry.get("guardrail_id"), "version": registry.get("guardrail_version"),
                     "description": f"rules sha256 {registry.get('rules_digest')}" if registry.get("rules_digest") else None}  # fmt: skip
    elif read_back is not None:
        read_back = {**read_back, "source": read_back.get("source") or "read_back"}
    pulls = observation.get("pulls") if isinstance(observation.get("pulls"), dict) else None
    baseline = observation.get("baseline") if isinstance(observation.get("baseline"), dict) else None
    out: dict[str, Any] = {
        "looked_up_at": observation.get("looked_up_at"),
        "made": bool(observation.get("made")),
        "repository": observation.get("repository"),
        "agent": observation.get("agent"),
        "commit": (answer or {}).get("commit") or ((pulls or {}).get("first") or {}).get("merge_commit"),
    }
    if not out["made"]:
        unread = ["the run has not been made: no agent repository with rules exists"]
        return {**out, "pin": None, "expected": 0, "fired": 0,
                "F9_1": _entry(False, unread, pin=None, digest_expected=None, digest_read=None, source=None),
                "F9_2": _entry(False, unread, refused_on=None),
                "F9_3": _entry(False, unread, expected=0, fired=0, fired_by={}),
                "F9_4": _entry(False, unread, heads={})}  # fmt: skip
    planted = plants(answer, blocks_of(observation.get("rules")))
    pinned = guardrail(answer, read_back, observation.get("tree_digest"))
    return {**out, "pin": pinned["pin"], "expected": planted["expected"], "fired": planted["fired"],
            "F9_1": pinned, "F9_2": weakened(pulls, read_back, baseline), "F9_3": planted, "F9_4": heads(pulls)}  # fmt: skip
