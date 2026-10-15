"""M10 PR 2's readers beyond the seed tests (SPEC/10 §4, §6).

The seed tests (`test_m10_seeds.py`) say each planted fault is refused for its
planted reason. These say what the readers do with what was not planted: every
way `callers_errors` refuses a field, and the platform check naming that reader
over the fixture agent; the raw record to the read shape (`from_raw`) for both
raw sources and the credential it refuses; the whole reading on a run not made
and on one held; row 10's reading of it; the observer on a run not made.
Nothing here calls AWS, GitHub or a model.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

from src.validate import agent as platform_check
from src.validate.callers import FIELD, callers_errors

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "m10"
M09_AGENT = ROOT / "tests" / "fixtures" / "m09" / "s1-festival-desk"
CALLERS_CHECK = "an agent's manifest says who may call it, even if nobody (callers)"


def manifest(**override: Any) -> dict[str, Any]:
    doc = yaml.safe_load((FIXTURES / "s2-manifest-no-callers" / "with_callers.yaml").read_text(encoding="utf-8"))
    return {**doc, **override}


# --- callers_errors: every refusal names the field (SPEC/10 §2, §6; S2's reader) -------------------


def test_an_empty_list_says_nobody_and_is_admitted():
    assert callers_errors(manifest(callers=[])) == []
    assert callers_errors(manifest()) == []  # one subject, issuer self


def test_a_missing_key_is_refused_naming_the_field_and_the_default():
    doc = manifest()
    del doc["callers"]
    (error,) = callers_errors(doc)
    assert error.startswith(f"{FIELD}: missing") and "callers: []" in error


def test_platform_is_reserved_and_refused_by_name():
    errors = callers_errors(manifest(callers=[{"subject": "platform", "issuer": "self"}]))
    assert len(errors) == 1 and "'platform' is reserved" in errors[0] and "goldens caller" in errors[0]


def test_an_issuer_that_is_not_self_is_refused():
    errors = callers_errors(manifest(callers=[{"subject": "lantern-desk", "issuer": "https://cognito-idp.us-west-2.amazonaws.com/us-west-2_x"}]))
    assert len(errors) == 1 and "issuer" in errors[0] and "'self'" in errors[0]


def test_a_duplicate_subject_is_refused_naming_both_entries():
    errors = callers_errors(manifest(callers=[{"subject": "lantern-desk", "issuer": "self"},
                                              {"subject": "box-office", "issuer": "self"},
                                              {"subject": "lantern-desk", "issuer": "self"}]))  # fmt: skip
    assert errors == [f"{FIELD}[2]: subject 'lantern-desk' is already {FIELD}[0]'s; one entry per subject"]


def test_a_malformed_entry_is_refused_part_by_part():
    errors = callers_errors(manifest(callers=[{"subject": "Lantern Desk", "issuer": "self", "scope": "x"}, "box-office", {"issuer": "self"}]))
    assert any("unknown key(s) ['scope']" in e for e in errors)
    assert any("'Lantern Desk' is not a name" in e for e in errors)
    assert f"{FIELD}[1]: not a mapping of subject and issuer" in errors
    assert f"{FIELD}[2]: no subject" in errors
    assert callers_errors(manifest(callers="lantern-desk")) == [f"{FIELD}: not a list of {{subject, issuer}} entries (str)"]
    assert callers_errors("not a mapping")[0].startswith(FIELD)


# --- the platform check names the reader (SPEC/10 §6) -------------------------------------------------


def door_layout(tmp_path: Path, callers: list[dict[str, str]] | None) -> tuple[Path, Path]:
    """agentkeel's root as the deploy's checkout holds it, with the fixture agent placed at agents/<name>/ and
    `callers` as given (None: the key left out, as festival-desk's repository held it at 19864419)."""
    root = tmp_path / "agentkeel"
    for name in ("refagent", "ratings-helper"):
        (root / "agents" / name).mkdir(parents=True)
        shutil.copy2(ROOT / "agents" / name / "manifest.yaml", root / "agents" / name / "manifest.yaml")
    shutil.copy2(ROOT / "thresholds.yaml", root / "thresholds.yaml")
    (root / "rules").mkdir()
    shutil.copy2(ROOT / "rules" / "baseline.yaml", root / "rules" / "baseline.yaml")
    bundle = root / "agents" / "festival-desk"
    shutil.copytree(M09_AGENT, bundle)
    if callers is not None:
        with (bundle / "manifest.yaml").open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(yaml.safe_dump({"callers": callers}, sort_keys=False))
    return root, bundle


def test_the_platform_check_refuses_a_manifest_with_no_callers_under_the_named_check_and_admits_one_with(tmp_path):
    from .test_m06_seeds import stand_in_lookup

    root, bundle = door_layout(tmp_path, None)
    refused = platform_check.evaluate(bundle, "agentkeel-studio/festival-desk", root=root, lookup=stand_in_lookup)
    assert {name for name, errs in refused.items() if errs} == {CALLERS_CHECK}, refused
    assert refused[CALLERS_CHECK][0].startswith(f"{FIELD}: missing")
    root, bundle = door_layout(tmp_path / "with", [{"subject": "lantern-desk", "issuer": "self"}])
    admitted = platform_check.evaluate(bundle, "agentkeel-studio/festival-desk", root=root, lookup=stand_in_lookup)
    assert {name for name, errs in admitted.items() if errs} == set(), admitted


# --- two-key entry 7 (ADR-0016), beyond the seed's four cases --------------------------------------------


def test_entry_7_reads_subjects_not_bytes():
    from src.gates.two_key import caller_relaxations

    one = [{"subject": "lantern-desk", "issuer": "self"}]
    two = one + [{"subject": "box-office", "issuer": "self"}]
    assert caller_relaxations({}, {"callers": []}) == []  # absent to [] (the two manifests of this PR)
    assert caller_relaxations({"callers": two}, {"callers": one}) == []  # a subject removed
    assert caller_relaxations({"callers": one}, {"callers": one[::-1] + []}) == []  # the same list
    assert caller_relaxations({}, {"callers": one}) == ["callers: subject 'lantern-desk' admitted (ADR-0016 entry 7)"]
    assert caller_relaxations({"callers": one}, {"callers": two}) == ["callers: subject 'box-office' admitted (ADR-0016 entry 7)"]
    assert caller_relaxations({"callers": one}, {}) == ["callers removed from a value (ADR-0016 entry 7)"]
    assert caller_relaxations({"callers": one}, {"callers": None}) == ["callers removed from a value (ADR-0016 entry 7)"]
    assert caller_relaxations({"callers": []}, {"callers": "lantern-desk"}) == ["callers no longer a list from a value (ADR-0016 entry 7)"]
    assert caller_relaxations({}, {}) == []


# --- from_raw: the raw record to the read shape, for both raw sources (SPEC/10 §2; R5) ------------------

import json  # noqa: E402

from src.verdict import SCHEMA_PATH, caller, gate  # noqa: E402

RAW = FIXTURES / "s1-call-records" / "raw"


def raw_events() -> dict[str, dict[str, Any]]:
    loaded = json.loads((RAW / "data_events.json").read_text(encoding="utf-8"))
    return {event["call"]: event for event in loaded["events"]}


def access_lines() -> dict[str, dict[str, Any]]:
    loaded = json.loads((RAW / "access_log.json").read_text(encoding="utf-8"))
    by_subject = {}
    for line in loaded["lines"]:
        wrapper = {"source": "access-log", "key": loaded["key"], "last_modified": loaded["last_modified"], "raw": line}
        by_subject[line["subject"] if line["subject"] != "-" else "none"] = wrapper
    return by_subject


READ_FIELDS = {"subject", "issuer", "agent", "outcome", "reason", "request_id", "time", "delivered"}


def test_a_data_event_of_an_admitted_token_call_names_the_tokens_sub_and_issuer():
    """door_probe.md (b): the event carries the claims, so the record names the pool user's sub, not a name."""
    read = caller.from_raw(raw_events()["admitted"])
    assert set(read) == READ_FIELDS
    assert read["subject"] == "00000000-0000-4000-8000-00000000a0a1"
    assert read["issuer"] == "https://cognito-idp.us-west-2.amazonaws.com/us-west-2_pr0bep00l"
    assert (read["outcome"], read["reason"], read["agent"]) == ("admitted", None, "probe-door-agent")
    assert read["time"] == "2026-10-14T14:21:48Z" and read["delivered"] == "2026-10-14T14:26:47Z"
    assert read["request_id"] == "b2b2b2b2-0000-4000-8000-000000000001"


def test_a_data_event_of_a_refused_token_call_names_no_caller_and_is_not_the_door():
    """door_probe.md (c): the stranger's refusal names no one (userIdentity anonymous, no claims), 298 s to deliver."""
    read = caller.from_raw(raw_events()["stranger"])
    assert read["subject"] is None and read["issuer"] is None
    assert (read["outcome"], read["reason"]) == ("refused", "not the door")
    assert caller.seconds(read["time"], read["delivered"]) == 298.0


def test_a_data_event_of_a_sigv4_call_names_the_principals_arn_and_is_refused_as_not_the_door():
    """door_probe.md (a): the bypass as an assumed role, refused 'Authorization method mismatch'."""
    read = caller.from_raw(raw_events()["bypass"])
    assert read["subject"] == "arn:aws:sts::000000000000:assumed-role/probe-door-bypass/probe-door-bypass"
    assert read["issuer"] is None and read["outcome"] == "refused" and read["reason"] == "not the door"
    platform = caller.from_raw(raw_events()["platform"])
    assert platform["subject"] == "d00rc1ient0000000000000000" and platform["outcome"] == "admitted"


def test_an_access_log_line_names_the_authorisers_subject_and_the_no_token_call_is_no_identity():
    lines = access_lines()
    admitted = caller.from_raw(lines["lantern-desk"])
    assert set(admitted) == READ_FIELDS
    assert (admitted["subject"], admitted["outcome"], admitted["reason"], admitted["agent"]) == ("lantern-desk", "admitted", None, "festival-desk")
    assert admitted["time"] == "2026-10-20T10:00:00Z" and admitted["delivered"] == "2026-10-20T10:04:20Z"
    assert admitted["request_id"] == "a1a1a1a1-0000-4000-8000-000000000011"
    none = caller.from_raw(lines["none"])
    assert (none["subject"], none["issuer"], none["outcome"], none["reason"]) == (None, None, "refused", "no identity")
    assert caller.seconds(none["time"], none["delivered"]) == 200.0
    stranger = caller.from_raw(lines["stranger"])
    assert (stranger["subject"], stranger["outcome"], stranger["reason"]) == ("stranger", "refused", "not admitted")
    platform = caller.from_raw(lines["platform"])
    assert (platform["subject"], platform["outcome"]) == ("platform", "admitted")


def test_a_raw_record_with_a_credential_is_refused_naming_the_field():
    import pytest

    leak = json.loads((RAW / "credential_leak.json").read_text(encoding="utf-8"))
    with pytest.raises(caller.Credential, match="raw.authorization: a raw record carries a credential"):
        caller.from_raw(leak)
    # a token as a value under any name, and CloudTrail's own redaction, which is not one
    with pytest.raises(caller.Credential, match="carries a token"):
        caller.from_raw({**leak["raw"], "authorization": "-", "note": leak["raw"]["authorization"].split(" ", 1)[1]})
    hidden = raw_events()["admitted"]
    assert caller.from_raw({**hidden, "raw": {**hidden["raw"], "requestParameters": {"userToken": caller.HIDDEN}}})["outcome"] == "admitted"
    with pytest.raises(caller.Unreadable, match="neither"):
        caller.from_raw({"what": "agent answer"})


def test_agent_of_runtime_reads_the_platforms_runtime_names():
    assert caller.agent_of("arn:aws:bedrock-agentcore:us-west-2:000000000000:runtime/agentkeel_festival_desk-AbC123") == "festival-desk"
    assert caller.agent_of("arn:aws:bedrock-agentcore:us-west-2:000000000000:runtime/refagent-Du2VJx6xWc") == "refagent"
    assert caller.agent_of(None) is None


# --- calls: beyond the seed's six cases -----------------------------------------------------------------

from .test_m10_seeds import CALLERS, MAX_SECONDS, STATED  # noqa: E402


def held_records() -> list[dict[str, Any]]:
    return json.loads((FIXTURES / "s1-call-records" / "calls_held.json").read_text(encoding="utf-8"))["records"]


def test_no_record_reads_as_unread_and_a_missing_step_as_a_reason():
    unread = caller.calls([], STATED, CALLERS, MAX_SECONDS)
    assert unread["read"] is False and unread["held"] is None and unread["reasons"] == ["no call record was read"]
    assert (unread["expected_admitted"], unread["expected_refused"]) == (1, 3)
    three = caller.calls(held_records()[:3], STATED, CALLERS, MAX_SECONDS)
    assert three["held"] is False and three["refused"] == 2
    assert "no record of the bypass call was read (F10.4)" in three["reasons"]


def test_a_record_the_observer_stepped_is_read_for_that_step_and_the_platforms_own_call_counts_for_nothing():
    records = held_records()
    stepped = [{**r, "step": s} for r, s in zip(records, ("admitted", "none", "stranger", "bypass"))]
    platform = {**records[0], "subject": "platform", "step": "platform"}
    read = caller.calls(stepped + [platform], {**STATED, "platform": {"subject": "platform", "outcome": "admitted"}}, CALLERS, MAX_SECONDS)
    assert read["held"] is True and (read["admitted"], read["refused"]) == (1, 3)
    assert read["steps"]["platform"] == "platform"
    # a refusal for the wrong reason, and a stated admitted call that reads refused
    wrong_reason = {**records[1], "reason": "not admitted"}
    assert any("reason reads 'not admitted', not 'no identity'" in r for r in caller.calls([wrong_reason], STATED, CALLERS, MAX_SECONDS)["reasons"])
    refused_instead = {**records[0], "outcome": "refused", "reason": "not admitted"}
    assert any("was stated 'admitted' and its record reads refused" in r for r in caller.calls([refused_instead], STATED, CALLERS, MAX_SECONDS)["reasons"])


# --- the whole reading, and row 10's reading of it (P5) ----------------------------------------------------


def observation(**override: Any) -> dict[str, Any]:
    """What scripts/observe_caller.py writes after the run: the four records stepped by request id, the answer
    record of the door's deploy, the manifest's callers and the stated callers derived from the run file."""
    lines = access_lines()
    bypass = raw_events()["bypass"]
    records = [
        {**lines["lantern-desk"], "step": "admitted"},
        {**lines["none"], "step": "none"},
        {**lines["stranger"], "step": "stranger"},
        {**bypass, "step": "bypass"},
        {**lines["platform"], "step": "platform"},
    ]
    answer = json.loads((FIXTURES / "s1-call-records" / "record_no_caller.json").read_text(encoding="utf-8"))
    stated = {**STATED, "bypass": {**STATED["bypass"], "subject": "arn:aws:sts::000000000000:assumed-role/probe-door-bypass/probe-door-bypass"}}
    return {"looked_up_at": "2026-10-20T10:30:00Z", "made": True, "repository": "agentkeel-studio/festival-desk",
            "agent": "festival-desk", "records": records, "answer": answer, "callers": CALLERS, "stated": stated, **override}  # fmt: skip


def test_the_whole_reading_holds_on_the_fixtures_and_validates():
    reading = caller.record(observation(), MAX_SECONDS)
    assert reading["made"] is True and (reading["admitted"], reading["refused"]) == (1, 3)
    for name in caller.READINGS:
        assert reading[name]["read"] is True and reading[name]["held"] is True, (name, reading[name])
    assert reading["F10_2"]["pin"] == "at8e36cosq1r:1" and reading["F10_2"]["blocked"] is True
    assert reading["F10_4"]["manifest_callers"] == CALLERS
    assert [r["step"] for r in reading["records"]] == ["admitted", "none", "stranger", "bypass", "platform"]
    assert reading["records"][3]["source"] == "data-event" and reading["records"][3]["raw"]["eventName"] == "InvokeAgentRuntime"
    from jsonschema import Draft202012Validator

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(e.message for e in Draft202012Validator(schema["properties"]["caller"]).iter_errors(reading))
    assert errors == []
    assert gate.caller_misses({"caller": reading, "plants_fired": 7, "plants_expected": 7}, MAX_SECONDS, "the tree") == []


def test_a_run_not_made_reads_every_falsifier_unread_and_row_10_reads_red():
    reading = caller.record({"made": False, "repository": "agentkeel-studio/festival-desk", "agent": "festival-desk"}, MAX_SECONDS)
    assert reading["made"] is False and all(reading[n]["read"] is False for n in caller.READINGS)
    misses = gate.caller_misses({"caller": reading, "plants_fired": 7, "plants_expected": 7}, MAX_SECONDS, "the tree")
    assert misses[0] == "the run has not been made: no door is deployed and no call was read"
    assert any(m.startswith("F10_1 unread") for m in misses) and not any("calls admitted" in m for m in misses)
    assert gate.caller_misses({}, MAX_SECONDS, "the tree") == ["caller not read: the envelope records no call"]
    assert gate.caller_reading({"caller": reading})[0] == "callers admitted 0 of 0, refused 0 of 0 (run not made)"


def test_row_10_holds_n_the_counts_and_refagents_plants_again():
    reading = caller.record(observation(), MAX_SECONDS)
    envelope = {"caller": reading, "plants_fired": 7, "plants_expected": 7}
    assert any("read against N 600, the commit's is 300.0" in m for m in gate.caller_misses(envelope, 300.0, "x"))
    assert any("N cannot be read" in m for m in gate.caller_misses(envelope, None, "x"))
    short = {**envelope, "plants_fired": 6}
    assert any("refagent's plants read 6 of 7" in m and "F10.2" in m for m in gate.caller_misses(short, MAX_SECONDS, "x"))
    forged = {**envelope, "caller": {**reading, "admitted": 0}}
    assert "calls admitted 0 of 1" in gate.caller_misses(forged, MAX_SECONDS, "x")


def test_a_credential_in_an_observed_record_is_filed_under_f10_3_and_an_unreadable_part_is_named():
    leak = json.loads((RAW / "credential_leak.json").read_text(encoding="utf-8"))
    reading = caller.record(observation(records=[{**leak, "step": "admitted"}]), MAX_SECONDS)
    assert reading["F10_3"]["held"] is False
    assert any("carries a credential" in r for r in reading["F10_3"]["reasons"])
    assert reading["records"] == []
    missing = caller.record(observation(callers=None, answer=None), MAX_SECONDS)
    assert missing["F10_2"]["read"] is False and missing["F10_4"]["held"] is False
    assert any("callers at its merge were not read" in r for r in missing["F10_4"]["reasons"])


# --- the observer writes raw records (scripts/observe_caller.py) -------------------------------------------


def run_file_text(observed: Any) -> str:
    run = yaml.safe_load((ROOT / "milestones" / "M10" / "runs" / "f10_x_caller_run.yaml").read_text(encoding="utf-8"))
    return yaml.safe_dump({**run, "observed": observed}, sort_keys=False)


def test_the_observer_writes_a_run_not_made_as_not_made_and_derives_stated_from_the_run_file(tmp_path, monkeypatch):
    from scripts import observe_caller as observer

    def never(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("a run not made reads nothing")

    monkeypatch.setattr(observer, "gh", never)
    monkeypatch.setattr(observer, "read_bucket", never)
    run = tmp_path / "run.yaml"  # its own run file, not the tree's, which the owner fills at PR 3
    run.write_text(run_file_text(None), encoding="utf-8")
    out = tmp_path / "caller.json"
    assert observer.main(["--read", "bucket,github", "--run", str(run), "--out", str(out)]) == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["made"] is False and written["records"] is None and written["callers"] is None
    assert written["stated"] == {
        "admitted": {"subject": "lantern-desk", "outcome": "admitted", "reason": None},
        "none": {"subject": None, "outcome": "refused", "reason": "no identity"},
        "stranger": {"subject": "stranger", "outcome": "refused", "reason": "not admitted"},
        "bypass": {"subject": None, "outcome": "refused", "reason": "not the door"},  # the principal is observed.bypass's
    }
    assert caller.record(written, MAX_SECONDS)["F10_1"]["read"] is False


class FakeS3:
    """The audit bucket as the read role sees it: the door's objects, the trail's, the answer record."""

    def __init__(self, keyed: dict[str, tuple[str, bytes]]) -> None:
        self.keyed = keyed  # key -> (LastModified, body)

    def get_paginator(self, name: str) -> Any:
        assert name == "list_objects_v2"
        keyed = self.keyed

        class Paginator:
            def paginate(self, Bucket: str, Prefix: str) -> list[dict[str, Any]]:  # noqa: N803
                return [{"Contents": [{"Key": k, "LastModified": v[0]} for k, v in keyed.items() if k.startswith(Prefix)]}]

        return Paginator()

    def get_object(self, Bucket: str, Key: str) -> dict[str, Any]:  # noqa: N803
        import io

        modified, data = self.keyed[Key]
        return {"Body": io.BytesIO(data), "LastModified": modified}


def test_the_observer_steps_each_line_by_request_id_finds_the_bypass_event_and_copies_no_credential(tmp_path, monkeypatch):
    from scripts import observe_caller as observer

    access = json.loads((RAW / "access_log.json").read_text(encoding="utf-8"))
    leak = json.loads((RAW / "credential_leak.json").read_text(encoding="utf-8"))["raw"]
    lines = "\n".join(json.dumps(line) for line in access["lines"] + [leak]) + "\n"
    bypass = raw_events()["bypass"]
    bypass["raw"] = {**bypass["raw"], "eventTime": "2026-10-20T10:03:00Z"}  # the probe's event, on the run's day
    trail_key = "AWSLogs/581208540944/CloudTrail/us-west-2/2026/10/20/581208540944_CloudTrail_us-west-2_20261020T1005Z_x.json.gz"
    import gzip

    keyed = {
        access["key"]: (access["last_modified"], lines.encode()),
        trail_key: ("2026-10-20T10:06:05Z", gzip.compress(json.dumps({"Records": [bypass["raw"], {"eventName": "GetAgentRuntime"}]}).encode())),
        "envelopes/agents/festival-desk/abc.json": ("2026-10-19T09:00:00Z", (FIXTURES / "s1-call-records" / "record_no_caller.json").read_bytes()),
    }
    import types

    monkeypatch.setitem(sys.modules, "boto3", types.SimpleNamespace(client=lambda *a, **k: FakeS3(keyed)))
    observed = {"callers": {"pull_request": 4}, "deploy": {"run_id": 1, "answer_key": "envelopes/agents/festival-desk/abc.json"},
                "admitted": {"request_id": "a1a1a1a1-0000-4000-8000-000000000011"},
                "none": {"request_id": "a1a1a1a1-0000-4000-8000-000000000012"},
                "stranger": {"request_id": "a1a1a1a1-0000-4000-8000-000000000013"},
                "bypass": {"request_id": bypass["raw"]["requestID"], "principal": bypass["raw"]["userIdentity"]["arn"]}}  # fmt: skip
    run = tmp_path / "run.yaml"
    run.write_text(run_file_text(observed), encoding="utf-8")
    out = tmp_path / "caller.json"
    assert observer.main(["--read", "bucket", "--run", str(run), "--out", str(out)]) == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["made"] is True and written["records_errors"] == []
    steps = [(r["source"], r["step"]) for r in written["records"]]
    assert steps == [("access-log", None), ("access-log", "admitted"), ("access-log", "none"), ("access-log", "stranger"),
                     ("access-log", None), ("data-event", "bypass")]  # fmt: skip
    refused = written["records"][4]
    assert refused["raw"] is None and "carries a credential" in refused["error"]
    assert written["records"][5]["raw"]["requestID"] == bypass["raw"]["requestID"]
    assert written["answer"]["what"] == "agent answer" and written["answer"]["key"].endswith("abc.json")
    assert written["stated"]["bypass"]["subject"] == bypass["raw"]["userIdentity"]["arn"]
    # build reads it: the credential-bearing line was not copied, so it is not a record, and the four hold
    written["callers"] = CALLERS
    reading = caller.record(written, MAX_SECONDS)
    assert (reading["admitted"], reading["refused"]) == (1, 3)
    assert reading["F10_1"]["held"] and reading["F10_3"]["held"] and reading["F10_4"]["held"]


def test_the_observer_reads_the_callers_pull_request_and_the_manifest_at_its_merge(tmp_path, monkeypatch):
    import base64
    import urllib.error

    from scripts import observe_caller as observer

    manifest_bytes = (FIXTURES / "s2-manifest-no-callers" / "with_callers.yaml").read_bytes()
    answers = {
        "/repos/agentkeel-studio/festival-desk/pulls/4": {"merged": True, "merged_at": "t", "head": {"sha": "a" * 40}, "merge_commit_sha": "4" * 40},
        f"/repos/agentkeel-studio/festival-desk/commits/{'a' * 40}/check-runs?per_page=100": {"check_runs": [
            {"name": "platform-check", "app": {"id": 5144253}, "conclusion": "success", "output": {"summary": "Every check passed."}}]},
        f"/repos/agentkeel-studio/festival-desk/contents/manifest.yaml?ref={'4' * 40}": {
            "encoding": "base64", "content": base64.b64encode(manifest_bytes).decode()},
    }  # fmt: skip

    def fake_gh(path: str) -> Any:
        if path not in answers:
            raise urllib.error.HTTPError(path, 404, "not found", {}, None)  # type: ignore[arg-type]
        return answers[path]

    monkeypatch.setattr(observer, "gh", fake_gh)
    run = tmp_path / "run.yaml"
    run.write_text(run_file_text({"callers": {"pull_request": 4}}), encoding="utf-8")
    out = tmp_path / "caller.json"
    assert observer.main(["--read", "github", "--run", str(run), "--out", str(out)]) == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["pull"]["merged"] is True and written["pull"]["check_runs"][0]["conclusion"] == "success"
    assert written["callers"] == [{"subject": "lantern-desk", "issuer": "self"}] and written["manifest_error"] is None
    # an unmerged pull request reads no manifest, and says so
    answers["/repos/agentkeel-studio/festival-desk/pulls/4"]["merged"] = False
    out.unlink()
    assert observer.main(["--read", "github", "--run", str(run), "--out", str(out)]) == 0
    again = json.loads(out.read_text(encoding="utf-8"))
    assert again["callers"] is None and "not merged" in again["manifest_error"]
