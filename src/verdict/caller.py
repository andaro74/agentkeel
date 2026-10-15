"""build's reading of M10's live run: the envelope's `caller` field (SPEC/10 §2, §4, §6; P5).

`scripts/observe_caller.py` writes what the security account's audit bucket
holds for the four calls the run file states (each raw call record with the
object's `LastModified`), the answer record of the deploy that put the door
on, and the agent's `callers` at its merge; this module rules on those raw
observations into one entry per falsifier, `{read, held, reasons, ...}`,
and the measured value, admitted n of n and refused m of m, each on the
record within N. `build` records the result in the optional envelope field
`caller`; the gate rules nothing on it, and the ledger's row 10 reading
(`gate.caller_misses`) is what turns it into a measurement. A bypass, an
answered stranger or an unrecorded refusal stops no merge at M10 (ADR-0015
decision 5).

Two readers the seed test names (`tests/test_m10_seeds.py`, S1):

- `from_raw(record)`: the raw record AWS delivered to the *read* shape
  SPEC/10 §2 fixes: `subject`, `issuer`, `agent`, `outcome`, `reason`,
  `request_id`, `time` (AWS's time of the call) and `delivered` (the
  object's `LastModified`). Two raw shapes (R2, door 2 hybrid): the API's
  access-log line, for a call that reached the door's front, and
  CloudTrail's `InvokeAgentRuntime` data event, for a call made straight at
  the runtime. **A raw record carries no credential** (R5): one that does is
  refused, naming the field, so nothing of the kind reaches
  `evals/history/`.
- `calls(records, stated, callers, max_seconds)`: the read records against
  what the run file stated for each call and what the manifest admits.
  Today's answer record, which names no caller, is not held; a stranger
  answered, a call that reached the agent without the door, a record naming
  a caller other than the one that called, and a refusal delivered later
  than N are each not held with the reason naming it; the four calls as
  stated, each refusal within N, are held: admitted 1 of 1, refused 3 of 3.

The record's facts are AWS's; `stated` is the run file's (its `steps[].caller`
and the bypass principal the owner wrote, derived by the observer, cold
review F3 on PR 1); `callers` is the manifest's. A reader decides nothing an
observation does not show; a part it cannot find is unread, which row 10
reads as RED (SPEC/10 §4).
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

READINGS = ("F10_1", "F10_2", "F10_3", "F10_4")
STEPS = ("admitted", "none", "stranger", "bypass")
PLATFORM = "platform"  # the construct's own goldens caller; never in `callers` (SPEC/10 §2)
NOT_THE_DOOR = "not the door"
ABSENT = (None, "", "-")  # API Gateway writes "-" for a $context value it has none of
DATA_EVENT_SOURCE = "bedrock-agentcore.amazonaws.com"
# A header, a field or a value a log line could carry and an envelope never may (SPEC/10 §2, R5).
CREDENTIAL_KEYS = ("authorization", "token", "workloadaccesstoken", "access_token", "id_token", "refresh_token",
                   "secret", "client_secret", "password", "x-amz-security-token", "cookie")
JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]*")
HIDDEN = "HIDDEN_DUE_TO_SECURITY_REASONS"  # CloudTrail's own redaction, which is not a credential


class Unreadable(Exception):
    """The observation is not in the observer's shape."""


class Credential(Unreadable):
    """The raw record carries a credential; it is refused, never copied."""


def _entry(read: bool, reasons: list[str], **extra: Any) -> dict[str, Any]:
    return {"read": read, "held": (not reasons) if read else None, "reasons": reasons, **extra}


def _absent(value: Any) -> bool:
    return value in ABSENT


def seconds(event_time: str | None, delivered: str | None) -> float | None:
    """`delivered` minus `time`, the two timestamps M05's `alarm_latency_s` read (SPEC/10 §2 "Refused")."""
    if not event_time or not delivered:
        return None
    try:
        parse = lambda value: datetime.fromisoformat(str(value).replace("Z", "+00:00"))  # noqa: E731
        return round((parse(delivered) - parse(event_time)).total_seconds(), 1)
    except ValueError:
        return None


def iso_of_epoch_ms(value: Any) -> str | None:
    """API Gateway's `$context.requestTimeEpoch`, milliseconds, to AWS's ISO form with a Z."""
    try:
        return datetime.fromtimestamp(int(str(value)) / 1000, tz=UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    except (TypeError, ValueError, OverflowError, OSError):
        return None


# --- R5: a raw record carries no credential -------------------------------------


def refuse_credential(raw: Any, at: str = "raw") -> None:
    """Raise `Credential` on a field a credential lives in, or a value that is a token, anywhere in the record."""
    if isinstance(raw, dict):
        for key, value in raw.items():
            path = f"{at}.{key}"
            if str(key).lower() in CREDENTIAL_KEYS and not _absent(value) and value != HIDDEN:
                raise Credential(f"{path}: a raw record carries a credential ({key}); refused, never copied (SPEC/10 §2, R5)")
            refuse_credential(value, path)
    elif isinstance(raw, list):
        for index, value in enumerate(raw):
            refuse_credential(value, f"{at}[{index}]")
    elif isinstance(raw, str) and raw != HIDDEN and JWT.search(raw):
        raise Credential(f"{at}: a raw record carries a token; refused, never copied (SPEC/10 §2, R5)")


# --- from_raw: the raw record to the read shape -----------------------------------


def agent_of(runtime_arn: str | None) -> str | None:
    """`runtime/agentkeel_festival_desk-XXXX` to `festival-desk`; `runtime/refagent-XXXX` to `refagent`."""
    if not isinstance(runtime_arn, str) or ":runtime/" not in runtime_arn:
        return None
    name = runtime_arn.rsplit(":runtime/", 1)[1].split("/", 1)[0].rsplit("-", 1)[0]
    return name.removeprefix("agentkeel_").replace("_", "-")


def _read_data_event(raw: dict[str, Any], delivered: str | None) -> dict[str, Any]:
    """CloudTrail's `InvokeAgentRuntime` data event: a call made straight at the runtime (the probe, door_probe.md).

    Who called: an IAM principal's ARN for a SigV4 call, else the token's `sub` where the event carries the
    claims (an admitted token call does; a refused one carries none, and the no-token call leaves no event).
    A refusal at the runtime is `not the door`: with the door on, the runtime admits the door's client only."""
    identity = raw.get("userIdentity") or {}
    claims = ((raw.get("additionalEventData") or {}).get("jwt") or {}).get("claims") or {}
    if identity.get("type") in ("AssumedRole", "IAMUser", "Root", "FederatedUser") and identity.get("arn"):
        subject, issuer = identity["arn"], None
    elif claims.get("sub"):
        subject, issuer = claims["sub"], claims.get("iss")
    else:
        subject = issuer = None
    refused = bool(raw.get("errorCode"))
    runtime = next((r.get("ARN") for r in raw.get("resources") or [] if r.get("type") == "AWS::BedrockAgentCore::Runtime"), None)
    return {"subject": subject, "issuer": issuer, "agent": agent_of(runtime),
            "outcome": "refused" if refused else "admitted", "reason": NOT_THE_DOOR if refused else None,
            "request_id": raw.get("requestID"), "time": raw.get("eventTime"), "delivered": delivered}  # fmt: skip


def _read_access_log(raw: dict[str, Any], delivered: str | None) -> dict[str, Any]:
    """The door's access-log line (the construct's ACCESS_LOG_FORMAT): a call that reached the door's front.

    The authoriser's context names the subject, the issuer, the outcome and the reason where it ran; a call
    the API refused before any authoriser ran (no token) has none, a 401 and the API's own error, which reads
    as refused for no identity."""
    status = str(raw.get("status") or "")
    subject = None if _absent(raw.get("subject")) else raw.get("subject")
    issuer = None if _absent(raw.get("issuer")) else raw.get("issuer")
    outcome = raw.get("outcome")
    if _absent(outcome):
        outcome = "admitted" if status.startswith("2") else "refused"
    reason = raw.get("reason")
    if _absent(reason):
        reason = ("no identity" if outcome == "refused" and subject is None else None)
    return {"subject": subject, "issuer": issuer, "agent": None if _absent(raw.get("agent")) else raw.get("agent"),
            "outcome": outcome, "reason": reason, "request_id": None if _absent(raw.get("request_id")) else raw.get("request_id"),
            "time": iso_of_epoch_ms(raw.get("time_epoch_ms")), "delivered": delivered}  # fmt: skip


def from_raw(record: dict[str, Any], delivered: str | None = None) -> dict[str, Any]:
    """The raw record AWS delivered, bare or in the observer's wrapper (`{source, key, last_modified, raw}`),
    to the read shape SPEC/10 §2 fixes. Refuses a record that carries a credential (R5)."""
    if not isinstance(record, dict):
        raise Unreadable("not a raw record: not a mapping")
    raw = record.get("raw") if isinstance(record.get("raw"), dict) else record
    delivered = record.get("last_modified") or delivered if raw is not record else delivered
    refuse_credential(raw)
    if raw.get("eventSource") == DATA_EVENT_SOURCE or raw.get("eventName") == "InvokeAgentRuntime":
        return _read_data_event(raw, delivered)
    if raw.get("source") == "access-log" or "request_id" in raw and "status" in raw:
        return _read_access_log(raw, delivered)
    raise Unreadable("not a raw record of a call: neither an InvokeAgentRuntime data event nor an access-log line")


# --- calls: the read records against what the run stated --------------------------------


def _step_of(record: dict[str, Any], stated: dict[str, Any]) -> str:
    """Which stated call a record is of: its `step` where the observer matched a request id, else by its subject."""
    if record.get("step") in stated:
        return record["step"]
    subject = record.get("subject")
    for step, expected in stated.items():
        if isinstance(expected, dict) and expected.get("subject") == subject:
            return step
    if record.get("reason") == NOT_THE_DOOR or (record.get("issuer") is None and str(subject).startswith("arn:")):
        return "bypass"
    return "admitted" if record.get("outcome") == "admitted" else "stranger"


def calls(records: list[dict[str, Any]], stated: dict[str, Any], callers: list[dict[str, Any]],
          max_seconds: float) -> dict[str, Any]:  # fmt: skip
    """The read records against the run's stated callers and the manifest's `callers` (F10.1, F10.3, F10.4).

    Each reason ends with the falsifier it is, in brackets, so `record` can file it. `stated` is
    `{step: {subject, outcome, reason}}` for the four calls; `callers` is the manifest's list."""
    stated = {step: value for step, value in (stated or {}).items() if step in STEPS}
    expected_admitted = sum(1 for value in stated.values() if isinstance(value, dict) and value.get("outcome") == "admitted")
    expected_refused = sum(1 for value in stated.values() if isinstance(value, dict) and value.get("outcome") == "refused")
    counts = {"admitted": 0, "refused": 0, "expected_admitted": expected_admitted, "expected_refused": expected_refused}
    if not records:
        return _entry(False, ["no call record was read"], **counts, steps={})
    admitted_subjects = {c.get("subject") for c in callers or [] if isinstance(c, dict)}
    reasons: list[str] = []
    steps: dict[str, str] = {}
    for record in records:
        if not isinstance(record, dict) or "subject" not in record or "outcome" not in record:
            reasons.append("a record names no caller: it has no subject and no outcome, today's answer record shape, "
                           "written once per deploy and naming nobody (F10.3)")  # fmt: skip
            continue
        subject = record.get("subject")
        if record.get("step") == PLATFORM or subject == PLATFORM:
            # The deploy's own goldens call through the door: not one of the run's four, counted for nothing.
            steps[PLATFORM] = PLATFORM if record["outcome"] == "admitted" else "refused"
            continue
        step = _step_of(record, stated)
        expected = stated.get(step) if isinstance(stated.get(step), dict) else {}
        if record["outcome"] == "admitted":
            if record.get("reason") == NOT_THE_DOOR or record.get("issuer") is None:
                steps[step] = "not held"
                reasons.append(f"{subject!r} reached the agent without the door: outcome admitted with reason "
                               f"{record.get('reason')!r} and issuer {record.get('issuer')!r} (F10.1)")  # fmt: skip
            elif subject not in admitted_subjects:
                steps[step] = "not held"
                reasons.append(f"a caller the manifest does not admit was answered: {subject!r} is not in callers "
                               f"{sorted(s for s in admitted_subjects if s)} (F10.4)")  # fmt: skip
            elif expected.get("outcome") != "admitted" or subject != expected.get("subject"):
                steps[step] = "not held"
                reasons.append(f"the record names a caller other than the one that called: {subject!r}, the run stated "
                               f"{expected.get('subject')!r} for the {step} call (F10.3)")  # fmt: skip
            else:
                steps[step] = "admitted"
                counts["admitted"] += 1
            continue
        latency = seconds(record.get("time"), record.get("delivered"))
        if latency is None:
            steps[step] = "not held"
            reasons.append(f"the {step} refusal's record has no event time or no delivery time: within N is unread (F10.4)")
        elif latency > max_seconds:
            steps[step] = "not held"
            reasons.append(f"the {step} refusal was recorded later than N: {latency} s after its event time, over "
                           f"{max_seconds} s (F10.4)")  # fmt: skip
        elif expected.get("outcome") != "refused":
            steps[step] = "not held"
            reasons.append(f"the {step} call was stated {expected.get('outcome')!r} and its record reads refused (F10.3)")
        elif subject != expected.get("subject"):
            steps[step] = "not held"
            reasons.append(f"the {step} refusal names a caller other than the one that called: {subject!r}, the run "
                           f"stated {expected.get('subject')!r} (F10.3)")  # fmt: skip
        elif expected.get("reason") and record.get("reason") != expected["reason"]:
            steps[step] = "not held"
            reasons.append(f"the {step} refusal's reason reads {record.get('reason')!r}, not {expected['reason']!r} (F10.3)")
        else:
            steps[step] = "refused"
            counts["refused"] += 1
    for step in stated:
        if step not in steps:
            steps[step] = "no record"
            reasons.append(f"no record of the {step} call was read (F10.4)" if stated[step].get("outcome") == "refused"
                           else f"no record of the {step} call was read (F10.3)")  # fmt: skip
    return _entry(True, reasons, **counts, steps=steps)


# --- F10.2: the guardrail stays on the call through the door ---------------------------------


def guardrail_through_the_door(answer: dict[str, Any] | None, plant: str = "g-030") -> dict[str, Any]:
    """The answer record of the deploy that put the door on: it names a pin, and its plant is blocked, 1 of 1.

    refagent's half (its plants 7 of 7 on the first envelope after the construct change) is the gate's own
    count, read again by row 10 (`gate.caller_misses`), not here."""
    out = {"pin": None, "plant": plant, "blocked": None}
    if not isinstance(answer, dict):
        return _entry(False, ["no answer record of the deploy that put the door on was read"], **out)
    reasons: list[str] = []
    pin = answer.get("guardrail") if isinstance(answer.get("guardrail"), dict) else None
    out["pin"] = f"{pin.get('id')}:{pin.get('version')}" if pin and pin.get("id") else None
    if out["pin"] is None:
        reasons.append("the answer record through the door names no guardrail (F10.2)")
    observation = (answer.get("observations") or {}).get(plant) if isinstance(answer.get("observations"), dict) else None
    if not isinstance(observation, dict):
        reasons.append(f"the answer record through the door has no observation of {plant} (F10.2)")
    else:
        out["blocked"] = observation.get("stop_reason") == "guardrail_intervened"
        if not out["blocked"]:
            reasons.append(f"{plant} was answered through the door (stop_reason {observation.get('stop_reason')!r}), "
                           f"not blocked: the door lost the guardrail (F10.2)")  # fmt: skip
    return _entry(True, reasons, **out)


# --- the whole reading, for build --------------------------------------------------------


def _filed(reasons: list[str], falsifier: str) -> list[str]:
    tag = f"({falsifier})"
    return [reason for reason in reasons if reason.endswith(tag)]


def record(observation: dict[str, Any], max_seconds: float) -> dict[str, Any]:
    """`scripts/observe_caller.py`'s observation, ruled into the envelope's `caller` (SPEC/10 §4).

    A run the observer wrote as not made is every falsifier unread with its reason; the gate rules
    nothing on the field, and row 10's cell reads it (`gate.caller_misses`)."""
    if not isinstance(observation, dict):
        raise Unreadable("not the observer's shape: not a mapping")
    out: dict[str, Any] = {
        "looked_up_at": observation.get("looked_up_at"),
        "made": bool(observation.get("made")),
        "repository": observation.get("repository"),
        "agent": observation.get("agent"),
        "max_seconds": max_seconds,
        "admitted": 0, "expected_admitted": 0, "refused": 0, "expected_refused": 0,
        "records": [],
    }  # fmt: skip
    if not out["made"]:
        unread = ["the door is not deployed and no call has been made: the run file's observed is null"]
        return {**out, "F10_1": _entry(False, unread), "F10_2": _entry(False, unread, pin=None, plant="g-030", blocked=None),
                "F10_3": _entry(False, unread), "F10_4": _entry(False, unread, manifest_callers=None)}  # fmt: skip
    records: list[dict[str, Any]] = []
    unreadable: list[str] = []
    for wrapper in observation.get("records") or []:
        if not isinstance(wrapper, dict):
            continue
        try:
            read = from_raw(wrapper)
        except Unreadable as exc:
            # One of the run's four calls whose record could not be read (a credential the observer refused to
            # copy, a shape neither source has) names no caller; a line of some other call's is not the run's.
            if wrapper.get("step") in STEPS:
                unreadable.append(f"{wrapper.get('key')} ({wrapper.get('step')}): {wrapper.get('error') or exc}")
            continue
        records.append({"step": wrapper.get("step"), "source": wrapper.get("source"), "key": wrapper.get("key"),
                        "last_modified": wrapper.get("last_modified"), "read": read, "raw": wrapper.get("raw")})  # fmt: skip
    out["records"] = records
    callers = observation.get("callers") if isinstance(observation.get("callers"), list) else None
    stepped = [{**r["read"], "step": r["step"]} for r in records if r["step"] in STEPS]
    read = calls(stepped, observation.get("stated") or {}, callers or [], max_seconds)
    out.update({k: read[k] for k in ("admitted", "expected_admitted", "refused", "expected_refused")})
    refused = [f"{u} (F10.3)" for u in unreadable]
    if read["read"]:
        # Each reason filed under the falsifier it names; an unreadable record is F10.3's (it names no caller).
        reasons = list(read["reasons"]) + refused
        filed = {f: _filed(reasons, f) for f in ("F10.1", "F10.3", "F10.4")}
        was_read = True
    elif refused:
        # Records were observed and none could be read: every falsifier is not held on them, not unread.
        filed = {f: list(refused) for f in ("F10.1", "F10.3", "F10.4")}
        was_read = True
    else:
        filed = {f: list(read["reasons"]) for f in ("F10.1", "F10.3", "F10.4")}
        was_read = False
    if callers is None:
        filed["F10.4"].append("the agent's callers at its merge were not read: whether the manifest admits the caller is unread (F10.4)")
    elif not callers:
        filed["F10.4"].append("the agent's manifest admits no caller: the admitted call had no one to be (F10.4)")
    return {**out,
            "F10_1": _entry(was_read, filed["F10.1"]),
            "F10_2": guardrail_through_the_door(observation.get("answer") if isinstance(observation.get("answer"), dict) else None),
            "F10_3": _entry(was_read, filed["F10.3"]),
            "F10_4": _entry(was_read, filed["F10.4"], manifest_callers=callers)}  # fmt: skip
