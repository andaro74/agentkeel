"""build's reading of M08's game-day drill: the envelope's `drill` field (SPEC/08 §4, §6; P5).

`scripts/observe_drill.py` writes what the audit bucket, the trail, the flow
records, the answer record, the registry and panel 1 hold for each of the
three runs; this module rules on those raw observations, per run, into
`{read, held, reasons}`. `build` imports it and records the result in the
optional envelope field `drill`; the gate rules nothing on it, and the
ledger's row 8 reading (`gate.drill_misses`) is what turns it into a
measurement. M08 builds no control (ADR-0013): this is the instrument, not a
refusal.

Five readers, the names `tests/test_m08_seeds.py` fixes (S2 to S7):

- `run1(observation, max_seconds)` — run 1's six attempts, each read on its
  two halves apart (refused, recorded) and counted. a2 is **unread on both
  halves** (the missing route leaves no record, M05's S1) and a3 is
  **recorded and not refused** (no filter on a tool result, SPEC/00 §12); both
  are expected, and both stay in the count, so the stated reading is refused
  4 of 6 and recorded 5 of 6 (SPEC/08 §2, §7). An attempt with no entry is
  unread; one answered that should have been refused, or recorded over N, is a
  reason. Returns the two counts beside `{read, held, reasons}`.
- `run2(observation, max_seconds)` — run 2's second layer: a1's connect
  completes (the flow record reads `ACCEPT`, so the egress rule was removed)
  and IAM refuses `kms:ListKeys` in the trail, both within N (F8.2).
- `run3(observation)` — run 3's answer record GREEN, no refusal by the role
  and no `REJECT` flow in its window, its registry row read through panel 1
  (F8.3). F8.3 reads the record's verdict as ruled; both goldens' `pass` are
  recorded beside it and gate nothing (finding 3).
- `evidence(observation, max_seconds)` — every record a run rests on present,
  in one version, under a lock, written no later than its run's close (plus N
  for a delivered object), and no refusal by the role in the window the
  observation does not name (F8.4).
- `quarantine(observation)` — after the attach, no call by the role answered,
  and a refused call by it in the trail (F8.5). Its hazard: the deny-all may
  refuse the agent before any call reaches the trail (M05's S7), so no refused
  call reads unread, not held (SPEC/08 §2).

The attempt's time is AWS's, never a person's (SPEC/08 §2): the record's own
`event_time`/`start` and the object's `last_modified`. A reader decides
nothing an observation does not show; an attempt it cannot find is unread,
which reads as absent (P5).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

# The six attempts run 1 makes on every invocation (SPEC/08 §2).
ATTEMPTS = ("a1", "a2", "a3", "a4", "a5", "a6")
# a2 is unread on both halves: routing drops the packet, so no flow record and no trail event is made
# (SPEC/08 §2, BLOCK 1). Its expected shape is refused None and no record.
UNREAD = {"a2"}
# a3 is recorded and not refused: nothing filters a tool result, so `build.carries_credential` reads the
# key off the answer record and refuses nothing (SPEC/00 §12, SPEC/08 §2).
NOT_REFUSED = {"a3"}


class Unreadable(Exception):
    """The observation is not in the observer's shape."""


def seconds(start: Any, end: Any) -> float | None:
    """`end` minus `start` in seconds, both ISO 8601; None when either is missing."""
    if not start or not end:
        return None
    parse = lambda value: datetime.fromisoformat(str(value).replace("Z", "+00:00"))  # noqa: E731
    return round((parse(end) - parse(start)).total_seconds(), 1)


def _entry(read: bool, reasons: list[str], **extra: Any) -> dict[str, Any]:
    return {"read": read, "held": (not reasons) if read else None, "reasons": reasons, **extra}


def refused_from_record(record: dict[str, Any]) -> bool | None:
    """Whether AWS refused the attempt, read from its own record (P5), not from the observer's claim.

    A flow record refuses when it reads REJECT; a trail record when it carries an error code; the answer
    record (a3) refuses nothing. No record is unread, not refused. build rules; the observer only records."""
    if not record.get("found"):
        return None
    kind = record.get("kind")
    if kind == "flow":
        return record.get("flow_action") == "REJECT"
    if kind == "answer":
        return False
    return record.get("error_code") is not None


# --- S2, S3: run 1's attempts -------------------------------------------------


def run1(observation: dict[str, Any], max_seconds: float) -> dict[str, Any]:
    """Run 1's six attempts, read on their two halves and counted (F8.1; SPEC/08 §2, §7)."""
    if not isinstance(observation, dict) or "attempts" not in observation:
        return _entry(False, ["the run has not been made"], refused=0, recorded=0)
    by_id = {a.get("id"): a for a in observation.get("attempts") or []}
    reasons: list[str] = []
    refused = recorded = 0
    for aid in ATTEMPTS:
        attempt = by_id.get(aid)
        if attempt is None:
            reasons.append(f"{aid}: no entry (unread)")
            continue
        record = attempt.get("record") or {}
        found = bool(record.get("found"))
        read_refused = refused_from_record(record)  # build's reading, not the observer's claim (P5)
        if found:
            recorded += 1
        if read_refused is True:
            refused += 1
        if aid in UNREAD:
            # Expected unread on both halves; anything else is a surprise worth a reason.
            if read_refused is not None:
                reasons.append(f"{aid}: expected unread on refusal, read {read_refused}")
            if found:
                reasons.append(f"{aid}: expected no record (the missing route leaves none), one was found")
        elif aid in NOT_REFUSED:
            if read_refused is True:
                reasons.append(f"{aid}: expected not refused (no filter on a tool result), read as refused")
            if not found:
                reasons.append(f"{aid}: expected recorded on the answer record, none found")
        else:
            if read_refused is not True:
                reasons.append(f"{aid}: not shown refused")
            if not found:
                reasons.append(f"{aid}: unrecorded")
            else:
                latency = seconds(record.get("event_time"), record.get("last_modified"))
                if latency is not None and latency > max_seconds:
                    reasons.append(f"{aid}: recorded {latency:.0f} s after the attempt, over N {max_seconds:.0f} s")
    return _entry(True, reasons, refused=refused, recorded=recorded)


# --- S4: run 2's second layer -------------------------------------------------


def run2(observation: dict[str, Any], max_seconds: float) -> dict[str, Any]:
    """Run 2's second layer: a1 found by IAM and the flow record, both within N (F8.2; SPEC/08 §8)."""
    if not isinstance(observation, dict) or not (observation.get("flow") or observation.get("iam")):
        return _entry(False, ["the run has not been made"])
    flow = observation.get("flow") or {}
    iam = observation.get("iam") or {}
    reasons: list[str] = []
    if not flow.get("found"):
        reasons.append("a1: no flow record for the ENI and the KMS endpoint's address")
    elif flow.get("flow_action") != "ACCEPT":
        reasons.append(f"a1: the flow record reads {flow.get('flow_action')}, not ACCEPT: the egress rule was not removed, so nothing new is learned")
    else:
        latency = seconds(flow.get("event_time"), flow.get("last_modified"))
        if latency is not None and latency > max_seconds:
            reasons.append(f"a1: the ACCEPT flow record was recorded {latency:.0f} s after its start, over N {max_seconds:.0f} s")
    if not iam.get("found"):
        reasons.append("a1: no IAM refusal of kms:ListKeys in the trail")
    else:
        latency = seconds(iam.get("event_time"), iam.get("last_modified"))
        if latency is not None and latency > max_seconds:
            reasons.append(f"a1: the IAM refusal was recorded {latency:.0f} s after its eventTime, late, over N {max_seconds:.0f} s")
    return _entry(True, reasons)


# --- S5: run 3 fires a control ------------------------------------------------


def run3(observation: dict[str, Any]) -> dict[str, Any]:
    """Run 3's answer record GREEN, no refusal, no REJECT flow, registry row read (F8.3; SPEC/08 §2)."""
    answer = observation.get("answer_record") if isinstance(observation, dict) else None
    if not answer:
        return _entry(False, ["the run has not been made"], goldens={})
    reasons: list[str] = []
    verdict = answer.get("verdict")
    if verdict != "GREEN":
        reasons.append(f"the answer record's verdict is {verdict}, not GREEN")
    for refusal in observation.get("refusals") or []:
        reasons.append(f"a refusal by the role in run 3's window: {refusal.get('event_name')} {refusal.get('error_code')}")
    for flow in observation.get("rejected_flows") or []:
        reasons.append(f"a REJECT flow from the role's interfaces in run 3's window: {flow}")
    if not observation.get("registry_row_in_panel1"):
        reasons.append("the registry row is not read through panel 1")
    goldens = {g: (v or {}).get("pass") for g, v in (answer.get("goldens") or {}).items()}
    return _entry(True, reasons, goldens=goldens)


# --- S6: the evidence is complete ---------------------------------------------


def evidence(observation: dict[str, Any], max_seconds: float) -> dict[str, Any]:
    """Every record present, singular, locked, in time, and no unnamed refusal (F8.4; SPEC/08 §2)."""
    if not isinstance(observation, dict) or "records" not in observation:
        return _entry(False, ["the run has not been made"])
    closed = (observation.get("window") or {}).get("closed")
    reasons: list[str] = []
    for record in observation.get("records") or []:
        key = record.get("key")
        if not record.get("found"):
            reasons.append(f"missing: {key} is absent from the bucket")
            continue
        if (record.get("versions") or 1) > 1:
            reasons.append(f"versions: {key} has {record['versions']} versions, not one")
        if not record.get("retention"):
            reasons.append(f"retention: {key} carries no lock (no retention was ever set)")
        # A delivered object (a trail or flow object) is delivered up to N after the event by design, so
        # its close is read with N's margin; an object written at once has no margin (SPEC/08 §2).
        margin = max_seconds if record.get("kind") == "delivered" else 0.0
        over = seconds(closed, record.get("last_modified"))
        if over is not None and over > margin:
            reasons.append(f"late: {key} was last written {over:.0f} s after its run closed (margin {margin:.0f} s)")
    for unnamed in observation.get("unnamed_refusals") or []:
        reasons.append(f"unnamed: the bucket holds a refusal by the role the observation does not name ({unnamed.get('event_name')})")
    return _entry(True, reasons)


# --- S7: the quarantine against the role --------------------------------------


def quarantine(observation: dict[str, Any]) -> dict[str, Any]:
    """After the attach, no call by the role answered and a refused call by it in the trail (F8.5)."""
    if not isinstance(observation, dict) or "calls_after_attach" not in observation:
        return _entry(False, ["the run has not been made"])
    reasons: list[str] = []
    for call in observation.get("calls_after_attach") or []:
        if call.get("answered"):
            reasons.append(f"a call by the role was answered after the attach: {call.get('event_name')}")
    if not (observation.get("refused_calls_in_window") or []):
        reasons.append("no refused call by the role is in the window (unread: the deny-all may refuse the "
                       "agent before any call reaches the trail, as M05's S7)")  # fmt: skip
    return _entry(True, reasons)


# --- the whole drill, for build ------------------------------------------------

READERS = ("run1", "run2", "run3", "evidence", "quarantine")


def record(observation: dict[str, Any], max_seconds: float) -> dict[str, Any]:
    """`scripts/observe_drill.py`'s observation, ruled into the envelope's `drill` (SPEC/08 §4).

    Each of the five runs is read by its own reader; a run the observer wrote
    as null (not made, or the bucket unreadable) is `{read: False}` with its
    reason. Recorded only: the gate rules nothing on `drill`, and row 8's cell
    reads it (`gate.drill_misses`)."""
    if not isinstance(observation, dict):
        raise Unreadable("not the observer's shape: not a mapping")
    return {
        "looked_up_at": observation.get("looked_up_at"),
        "max_seconds": max_seconds,
        "readable": bool(observation.get("readable")),
        "run1": run1(observation.get("run1"), max_seconds) if observation.get("run1") else _entry(False, ["run 1 not made"], refused=0, recorded=0),
        "run2": run2(observation.get("run2"), max_seconds) if observation.get("run2") else _entry(False, ["run 2 not made"]),
        "run3": run3(observation.get("run3")) if observation.get("run3") else _entry(False, ["run 3 not made"], goldens={}),
        "evidence": evidence(observation.get("evidence"), max_seconds) if observation.get("evidence") else _entry(False, ["run 1's evidence not read"]),
        "quarantine": quarantine(observation.get("quarantine")) if observation.get("quarantine") else _entry(False, ["the quarantine not read"]),
    }
