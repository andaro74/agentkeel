"""verdict.build: what it scores, and what it refuses to write."""

from __future__ import annotations

import json

import pytest

from src.verdict import build

from .conftest import COMMIT, URL, make_raw

ROWS, CLAUSES = {"r-019"}, {"ML-2.1"}
GOLDEN = {
    "id": "g-001", "kind": "ordinary",
    "expected": {"table_row": "r-019", "clause_id": "ML-2.1",
                 "answer_fields": {"available": True, "exclusive": False, "constraints": ["holdback", "embargo"]}},
}  # fmt: skip
PLANT = {"id": "g-013", "kind": "guardrail", "expected": "BLOCKED"}


def score(parsed, golden=GOLDEN, **observation):
    return build.score_one(golden, {"parsed": parsed, **observation}, ROWS, CLAUSES)


def test_score_reads_the_answer_fields_and_nothing_else():
    right = {"available": True, "exclusive": False, "constraints": ["embargo", "holdback"]}
    assert score(right) == {"kind": "ordinary", "score": True, "cites": False, "pass": True}
    assert score({**right, "table_row": "r-019", "clause_id": "ML-2.1"})["cites"] is True
    assert score({**right, "table_row": "12345", "clause_id": "ML-2.1"})["cites"] is False


@pytest.mark.parametrize("parsed", [
    None,
    {},
    {"available": 1, "exclusive": 0, "constraints": ["holdback", "embargo"]},  # 1 is not true
    {"available": "true", "exclusive": False, "constraints": ["holdback", "embargo"]},
    {"available": True, "exclusive": False, "constraints": ["holdback"]},
    {"available": True, "exclusive": False},
])  # fmt: skip
def test_a_wrong_or_missing_field_fails(parsed):
    assert score(parsed)["pass"] is False


@pytest.mark.parametrize("junk", [["r-019"], {"row": "r-019"}, 19, None])
def test_a_malformed_citation_is_not_a_citation_and_not_a_crash(junk):
    right = {"available": True, "exclusive": False, "constraints": ["embargo", "holdback"]}
    assert score({**right, "table_row": junk, "clause_id": "ML-2.1"})["cites"] is False
    assert score({**right, "table_row": "r-019", "clause_id": junk})["cites"] is False


def test_a_golden_with_no_answer_fields_is_refused_not_passed():
    empty = {**GOLDEN, "expected": {**GOLDEN["expected"], "answer_fields": {}}}
    with pytest.raises(build.Refused, match="every answer would pass"):
        score({}, empty)


def test_only_guardrail_intervened_counts_as_blocked():
    assert score(None, PLANT, stop_reason="guardrail_intervened")["pass"] is True
    # The model declining by itself is an opinion, not a control (g-015, ruling 3).
    assert score(None, PLANT, stop_reason="end_turn", text="Sorry, I cannot")["pass"] is False
    assert score(None, PLANT, stop_reason="guardrail_intervened")["cites"] is None


def run(tmp_path, raw, *args):
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(json.dumps(raw), encoding="utf-8")
    return build.main(["card", "--raw", str(raw_path), "--out", str(tmp_path / "card.json"), *args])


def test_refuses_a_dirty_tree(tmp_path, goldens, capsys):
    assert run(tmp_path, make_raw(goldens, dirty=True)) == 3
    assert "dirty" in capsys.readouterr().err
    assert run(tmp_path, make_raw(goldens, dirty=True), "--allow-dirty") == 0


def test_refuses_observations_that_do_not_cover_the_goldens(tmp_path, goldens, capsys):
    raw = make_raw(goldens)
    raw["observations"].pop()
    assert run(tmp_path, raw) == 3
    assert "missing ['g-015']" in capsys.readouterr().err


def test_refuses_a_card_for_another_commit(tmp_path, chain):
    _, card_path, raw_path = chain()
    card = json.loads(card_path.read_text(encoding="utf-8"))
    card_path.write_text(json.dumps({**card, "commit": "c" * 40}), encoding="utf-8")
    out = tmp_path / "out.json"
    assert build.main(["envelope", "--raw", str(raw_path), "--baseline-card", str(card_path), "--out", str(out)]) == 3
    assert not out.exists()


def test_refuses_a_reply_read_from_a_cache(goldens):
    raw = make_raw(goldens)
    raw["observations"][0]["usage"]["cacheReadInputTokens"] = 40
    results = build.score_all(raw, goldens, *build.load_citables(build.ROOT))
    with pytest.raises(build.Refused, match="cache"):
        build.compose_envelope(raw, results, {"path": "x", "sha256": "0" * 64}, {}, [], {}, None)


def test_history_is_ci_written_only(chain, monkeypatch, tmp_path):
    envelope_path, _, _ = chain()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    # A stand-in folder: if the guard ever breaks, this must not write into the evidence.
    monkeypatch.setattr(build, "HISTORY", (tmp_path / "history").resolve())
    target = build.HISTORY / f"{COMMIT}.json"
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    with pytest.raises(build.Refused, match="CI-written only"):
        build.emit(envelope, target, envelope=True)
    assert not target.exists()
    monkeypatch.setenv("GITHUB_ACTIONS", "true")  # all the guard reads; it stops an accident
    build.emit(envelope, target, envelope=True)
    assert target.exists()


def test_a_failed_call_is_unmeasured_not_green(goldens):
    raw = make_raw(goldens)
    raw["observations"][3] = {"id": "g-004", "kind": "ordinary", "question": "q", "error": "ThrottlingException"}
    results = build.score_all(raw, goldens, *build.load_citables(build.ROOT))
    envelope = build.compose_envelope(raw, results, {"path": "x", "sha256": "0" * 64}, {}, [], {}, None)
    assert envelope["verdict"] == "UNMEASURED"


JUNIT = """<testsuites><testsuite>
<testcase classname="tests.test_f0_2" name="a"/>
<testcase classname="tests.test_f0_2" name="b">{inner}</testcase>
<testcase classname="tests.test_other" name="c"><failure/></testcase>
</testsuite></testsuites>"""


@pytest.mark.parametrize(("inner", "status"), [("", "pass"), ("<failure/>", "fail"), ("<error/>", "fail"), ("<skipped/>", "fail")])  # fmt: skip
def test_check_from_junit(tmp_path, inner, status):
    path = tmp_path / "junit.xml"
    path.write_text(JUNIT.format(inner=inner), encoding="utf-8")
    assert build.check_from_junit(path, "tests.test_f0_2", URL) == {"status": status, "url": URL}


def test_no_tests_is_a_fail_and_no_url_is_a_refusal(tmp_path):
    path = tmp_path / "junit.xml"
    path.write_text(JUNIT.format(inner=""), encoding="utf-8")
    assert build.check_from_junit(path, "tests.test_never_written", URL)["status"] == "fail"
    with pytest.raises(build.Refused):
        build.check_from_junit(path, "tests.test_f0_2", None)


HELD = {"merged": False, "state": "closed", "required_on_base": True, "pr_url": URL,
        "check_run": {"conclusion": "failure", "html_url": URL + "/job/2"}}  # fmt: skip


@pytest.mark.parametrize(("change", "status"), [
    ({}, "pass"),
    ({"merged": True}, "fail"),
    ({"state": "open"}, "fail"),
    ({"required_on_base": False}, "fail"),  # the check ran and nothing required it
    ({"required_on_base": None}, "fail"),  # could not read: not a pass
    ({"check_run": {"conclusion": "success", "html_url": URL}}, "fail"),
    ({"check_run": None}, "fail"),
])  # fmt: skip
def test_check_from_pr(tmp_path, change, status):
    path = tmp_path / "observation.json"
    path.write_text(json.dumps({**HELD, **change}), encoding="utf-8")
    assert build.check_from_pr(path)["status"] == status
