"""M09 PR 2's readers beyond the seed tests (SPEC/09 §4, §6).

The seed tests (`test_m09_seeds.py`) say each planted fault is refused for its
planted reason. These say what the readers do with what was not planted: F9.1's
pin and digest against the read-back and the registry (rule-owner N5 on PR 1:
`record_held.json` pins the placeholder, so it is not F9.1's held case), the
three heads, the weakened file's refusal, the whole reading on a run not made
and on one held, row 9's reading of it, the answer record's new shape, and the
digest's line-ending rule. Nothing here calls AWS, GitHub or a model.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from src.validate import agent_rules as merge_module
from src.verdict import SCHEMA_PATH, agent_rules, build, gate

FIXTURES = Path(__file__).parent / "fixtures" / "m09"
AGENT = FIXTURES / "s1-festival-desk"
RULES = yaml.safe_load((AGENT / "rules" / "guardrail.yaml").read_text(encoding="utf-8"))
BASELINE = yaml.safe_load((build.ROOT / "rules" / "baseline.yaml").read_text(encoding="utf-8"))
REFAGENT = {"id": "1088aw3ujhyd", "version": "5"}
STACK = {"id": "fd7k2m9q1x0b", "version": "1", "source": "stack"}
DIGEST = merge_module.digest((build.ROOT / "rules" / "baseline.yaml").read_bytes(),
                             (AGENT / "rules" / "guardrail.yaml").read_bytes())  # fmt: skip
RULES_CHECK = agent_rules.RULES_CHECK


def record(name: str = "record_held.json", **override: Any) -> dict[str, Any]:
    loaded = json.loads((FIXTURES / "s3-silent-plant" / name).read_text(encoding="utf-8"))
    return {**loaded, **override}


def read_back(**override: Any) -> dict[str, Any]:
    return {"source": "read_back", "id": STACK["id"], "version": STACK["version"], "name": "agentkeel-festival-desk",
            "description": f"rules sha256 {DIGEST}", "topics": ["unannounced-selection-leak"],
            "pii": [{"entity": "PHONE", "action": "ANONYMIZE"}, {"entity": "EMAIL", "action": "ANONYMIZE"}], **override}  # fmt: skip


def check_run(conclusion: str, refused: list[str] | None = None, summary: str = "") -> dict[str, Any]:
    return {"name": "platform-check", "conclusion": conclusion, "refused": refused if conclusion != "success" else [],
            "summary": summary}  # fmt: skip


def pulls(**override: Any) -> dict[str, Any]:
    weakened = f"- **{RULES_CHECK}**: rules/guardrail.yaml: pii EMAIL: ANONYMIZE to NONE: a baseline entity's action may not be changed"
    base = {
        "first": {"found": True, "pull_request": 1, "merged": True, "merge_commit": "1" * 40, "head_sha": "a" * 40,
                  "check_runs": [check_run("success")]},
        "second": {"found": True, "pull_request": 2, "merged": False, "head_sha": "b" * 40,
                   "check_runs": [check_run("failure", [RULES_CHECK], weakened)]},
        "third": {"found": True, "pull_request": 3, "merged": True, "head_sha": "c" * 40,
                  "check_runs": [check_run("success")]},
    }  # fmt: skip
    return {**base, **override}


def observation(**override: Any) -> dict[str, Any]:
    return {"looked_up_at": "2026-10-20T10:00:00Z", "made": True, "repository": "agentkeel-studio/festival-desk",
            "agent": "festival-desk", "answer": record(guardrail=STACK), "read_back": read_back(), "registry": None,
            "pulls": pulls(), "rules": {"guardrail": RULES, "redteam": None}, "baseline": {"pii": BASELINE["pii"]},
            "tree_digest": DIGEST, **override}  # fmt: skip


# --- F9.1: the pin and the digest -------------------------------------------------


def test_f9_1_the_record_pin_and_the_read_back_digest_are_held_to_the_tree():
    """The stack's pin on the record, the guardrail read back at that pin, its description the tree's digest: held.
    Each of the four ways it can differ is a reason that names it; the placeholder is not a held case (N5)."""
    held = agent_rules.guardrail(record(guardrail=STACK), read_back(), DIGEST, platform=REFAGENT)
    assert held["read"] is True and held["held"] is True and held["reasons"] == [], held
    assert held["pin"] == f"{STACK['id']}:1" and held["digest_read"] == DIGEST and held["source"] == "read_back"
    other = agent_rules.guardrail(record(guardrail=STACK), read_back(description="rules sha256 " + "0" * 64), DIGEST, platform=REFAGENT)
    assert other["held"] is False and any("version description" in r and DIGEST in r for r in other["reasons"])
    refagents = agent_rules.guardrail(record(guardrail=REFAGENT), read_back(**REFAGENT), DIGEST, platform=REFAGENT)
    assert refagents["held"] is False and any("is refagent's" in r for r in refagents["reasons"])
    moved = agent_rules.guardrail(record(guardrail=STACK), read_back(version="2"), DIGEST, platform=REFAGENT)
    assert moved["held"] is False and any("not the record's pin" in r for r in moved["reasons"])
    unnamed = agent_rules.guardrail(record(), None, DIGEST, platform=REFAGENT)  # the fixture's placeholder: no stack pin
    assert unnamed["held"] is False and any("not read back" in r for r in unnamed["reasons"])
    assert agent_rules.guardrail(None, read_back(), DIGEST, platform=REFAGENT)["read"] is False


def test_the_registry_row_stands_in_for_the_read_back_when_the_read_is_not_granted():
    """SPEC/09 §9 cut 3 (R4): with no read-back, the row's id, version and digest are F9.1's source, named as such."""
    row = {"guardrail_id": STACK["id"], "guardrail_version": "1", "rules_digest": DIGEST}
    reading = agent_rules.record(observation(read_back=None, registry=row))
    assert reading["F9_1"]["held"] is True and reading["F9_1"]["source"] == "registry"
    # and F9_2's second half is then unread: whether the built guardrail holds every baseline rule rests on the digest
    assert reading["F9_2"]["held"] is False and any("not read back" in r for r in reading["F9_2"]["reasons"])


# --- F9.2 and F9.4: the three heads ---------------------------------------------------


def test_the_three_heads_are_read_from_the_platform_checks_own_runs():
    held = agent_rules.heads(pulls())
    assert held["held"] is True and held["heads"] == {"first": "admitted", "second": "refused", "third": "admitted"}
    admitted = agent_rules.heads(pulls(second={**pulls()["second"], "check_runs": [check_run("success")]}))
    assert admitted["held"] is False and any("admitted the weakened" in r for r in admitted["reasons"])
    refused = agent_rules.heads(pulls(first={**pulls()["first"], "check_runs": [check_run("failure", ["the agent's own guardrail"])]}))
    assert refused["held"] is False and any("own pin or its guardrail golden" in r for r in refused["reasons"])
    on_more = agent_rules.heads(pulls(second={**pulls()["second"], "check_runs": [check_run("failure", [RULES_CHECK, "seats"])]}))
    assert on_more["held"] is False and any("not on the rules file alone" in r for r in on_more["reasons"])
    assert agent_rules.heads(None)["read"] is False
    partial = agent_rules.heads({"first": pulls()["first"]})
    assert partial["read"] is True and partial["heads"]["second"] == "unread" and partial["held"] is False


def test_the_weakened_file_is_refused_naming_email_and_the_built_guardrail_holds_the_baseline():
    held = agent_rules.weakened(pulls(), read_back(), {"pii": BASELINE["pii"]})
    assert held["held"] is True and held["refused_on"] == [RULES_CHECK]
    unnamed = agent_rules.weakened(pulls(second={**pulls()["second"], "check_runs": [check_run("failure", [RULES_CHECK], "refused")]}),
                                   read_back(), {"pii": BASELINE["pii"]})  # fmt: skip
    assert unnamed["held"] is False and any("EMAIL" in r for r in unnamed["reasons"])
    lacking = agent_rules.weakened(pulls(), read_back(pii=[{"entity": "PHONE", "action": "ANONYMIZE"}]), {"pii": BASELINE["pii"]})
    assert lacking["held"] is False and any("lacks the baseline's" in r and "EMAIL" in r for r in lacking["reasons"])


# --- the whole reading, and row 9's -----------------------------------------------------


def agent_rules_schema_errors(reading: dict[str, Any]) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    sub = {**schema["properties"]["agent_rules"], "$defs": schema["$defs"]}
    return sorted(e.message for e in Draft202012Validator(sub).iter_errors(reading))


def test_a_run_not_made_reads_every_falsifier_unread_and_row_9_red():
    """PR 2's own envelope: `observed: null`, no agent repository with rules exists (SPEC/09 §7)."""
    reading = agent_rules.record({"looked_up_at": "2026-10-20T10:00:00Z", "made": False, "repository": None, "agent": None})
    assert agent_rules_schema_errors(reading) == []
    assert all(reading[name]["read"] is False for name in gate.RULES_READINGS)
    assert (reading["fired"], reading["expected"]) == (0, 0) and reading["pin"] is None
    misses = gate.rules_misses({"agent_rules": reading})
    assert any("has not been made" in m for m in misses) and len([m for m in misses if "unread" in m]) == 4
    assert gate.rules_reading({"agent_rules": reading})[0] == "planted rules fired 0 of 0 (run not made)"
    assert gate.rules_misses({}) == ["agent_rules not read: the envelope records no plant run"]


def test_a_held_run_reads_fired_1_of_1_and_row_9_finds_nothing():
    """What PR 3's run is expected to read (SPEC/09 §7): fired 1 of 1, F9.1 to F9.4 held."""
    reading = agent_rules.record(observation())
    assert agent_rules_schema_errors(reading) == []
    assert all(reading[name]["held"] is True for name in gate.RULES_READINGS), {n: reading[n]["reasons"] for n in gate.RULES_READINGS}
    assert (reading["fired"], reading["expected"]) == (1, 1) and reading["pin"] == f"{STACK['id']}:1"
    assert reading["F9_3"]["fired_by"] == {"g-030": ["unannounced-selection-leak"]}
    assert gate.rules_misses({"agent_rules": reading}) == []
    assert gate.rules_reading({"agent_rules": reading}) == ["planted rules fired 1 of 1", "F9_1 held (read_back)", "F9_2 held",
                                                            "F9_3 held", "F9_4 held"]  # fmt: skip


def test_a_silent_plant_in_a_made_run_is_row_9s_miss():
    reading = agent_rules.record(observation(answer=record("record_answered.json", guardrail=STACK)))
    assert (reading["fired"], reading["expected"]) == (0, 1) and reading["F9_3"]["held"] is False
    assert "planted rules fired 0 of 1" in gate.rules_misses({"agent_rules": reading})


def test_the_measured_cell_reads_agent_rules_for_row_9(chain):
    """`gate.measured` with `rules`: a GREEN run reads RED on an envelope with no plant run (the plant going RED)."""
    envelope_path, card_path, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    card = json.loads(card_path.read_text(encoding="utf-8"))
    cell = gate.measured(envelope, "GREEN", card, rules=True)
    assert "; RED; " in cell and "agent_rules not read" in cell
    assert "; GREEN; " in gate.measured(envelope, "GREEN", card)  # another row's reading of the same envelope


# --- the answer record's shape (R7) ----------------------------------------------------------


def observed(golden_id: str, kind: str, **extra: Any) -> dict[str, Any]:
    return {"id": golden_id, "kind": kind, "usage": {"inputTokens": 100, "outputTokens": 20}, "tool_calls": [], **extra}


def test_build_answer_carries_each_observation_and_the_stacks_pin_and_scores_a_plant_by_its_named_rule():
    """R7: the blocked observation's shape is the one build scores refagent's plants from; the pin is the stack's."""
    call = {"name": "check_availability", "status": "success", "output": {"found": True, "row": {"table_row": "r-019"}, "clause_candidates": ["ML-2.1"]}}
    raw = {"commit": "1" * 40, "dirty": False, "model_id": "us.anthropic.claude-sonnet-4-6", "region": "us-west-2", "mode": "runtime",
           "runtime_arn": "arn:aws:bedrock-agentcore:us-west-2:1:runtime/agentkeel_festival_desk-x", "bundle": "agents/festival-desk",
           "observations": [
               observed("g-001", "ordinary", parsed={"table_row": "r-019", "clause_id": "ML-2.1", "available": True, "exclusive": True, "constraints": []},
                        stop_reason="end_turn", tool_calls=[call]),
               observed("g-010", "trap", parsed={"table_row": "r-009", "clause_id": "HS-4", "available": False}, stop_reason="end_turn"),
               observed("g-030", "guardrail", parsed=None, stop_reason="guardrail_intervened", guardrail_topics=["unannounced-selection-leak"]),
           ]}  # fmt: skip
    document = build.compose_answer(raw, AGENT, "agentkeel-studio/festival-desk", "f" * 40, "https://run", {"id": STACK["id"], "version": "1"})
    assert build.answer_errors(document) == []
    assert document["guardrail"] == STACK and document["goldens"]["g-030"] == {"kind": "guardrail", "score": True, "cites": None, "pass": True}
    assert document["observations"]["g-030"] == {"stop_reason": "guardrail_intervened", "guardrail_topics": ["unannounced-selection-leak"], "parsed": None}
    # Read back by the plant reader as the observer would hand it over: fired 1 of 1.
    assert agent_rules.plants(document, RULES["blocks"])["fired"] == 1
    # Blocked by another rule: the membership rule scores it silent, on the record and in the reader alike.
    raw["observations"][2]["guardrail_topics"] = ["some-other-rule"]
    silent = build.compose_answer(raw, AGENT, "agentkeel-studio/festival-desk", "f" * 40, "https://run", {"id": STACK["id"], "version": "1"})
    assert silent["goldens"]["g-030"]["pass"] is False and agent_rules.plants(silent, RULES["blocks"])["fired"] == 0
    # An agent without rules/ names no pin and carries observations all the same.
    plain = build.compose_answer(raw, AGENT, "agentkeel-studio/festival-desk", "f" * 40, "https://run")
    assert "guardrail" not in plain and build.answer_errors(plain) == []


# --- the digest -----------------------------------------------------------------------------


def test_the_digest_ignores_line_endings_and_orders_the_baseline_first():
    """What the construct writes on the version and the observer computes again from `git show` (cold review N7 on PR 1)."""
    assert merge_module.digest(b"a: 1\r\n", b"b: 2\r\n") == merge_module.digest(b"a: 1\n", b"b: 2\n")
    assert merge_module.digest(b"a: 1\n", b"b: 2\n") != merge_module.digest(b"b: 2\n", b"a: 1\n")


# --- the registry row's guardrail fields (scripts/registry.py) -------------------------------


def test_the_registry_row_records_the_built_guardrail_and_prints_the_pin_it_holds():
    """R3: the deploy writes id, version and digest from the stack's outputs; `guardrail` prints the pin, or nothing."""
    from scripts import registry

    from .test_m06_readers import FakeTable

    table = FakeTable()
    assert registry.guardrail(table, "festival-desk") == (0, "")  # no row: a placeholder is admitted
    assert registry.claim(table, "festival-desk", "agentkeel-studio/festival-desk", "9")[0] == 0
    assert registry.guardrail(table, "festival-desk") == (0, "")  # a row with no guardrail yet
    code, said = registry.write(table, "festival-desk", "agentkeel-studio/festival-desk", "9", "1" * 40, "7",
                                "first", f"{STACK['id']}:1", DIGEST)  # fmt: skip
    assert code == 0 and f"guardrail {STACK['id']}:1" in said
    row = table.items["festival-desk"]
    assert (row["guardrail_id"]["S"], row["guardrail_version"]["S"], row["rules_digest"]["S"]) == (STACK["id"], "1", DIGEST)
    assert registry.guardrail(table, "festival-desk") == (0, f"{STACK['id']}:1")
    assert registry.write(table, "festival-desk", "agentkeel-studio/festival-desk", "9", "2" * 40, "8", None, "nocolon")[0] == 3


# --- the observer writes raw records (scripts/observe_rules.py) -----------------------------


def test_the_observer_writes_a_run_not_made_as_not_made_and_reads_nothing(tmp_path, monkeypatch):
    from scripts import observe_rules as observer

    def never(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("a run not made reads nothing")

    monkeypatch.setattr(observer, "gh", never)
    out = tmp_path / "rules.json"
    assert observer.main(["--read", "github,bucket,registry,guardrail", "--out", str(out)]) == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["made"] is False and written["answer"] is None and written["pulls"] is None
    assert agent_rules.record(written)["F9_1"]["read"] is False


def test_the_observer_computes_the_digest_from_the_merge_commit_and_main_and_reads_the_checks(tmp_path, monkeypatch):
    """The digest is the observer's own, from bytes it fetched by the merge commit and `git show` of main, never
    the builder's (SPEC/09 §4, note 9); the heads' check runs are GitHub's own."""
    import base64

    from scripts import observe_rules as observer

    guardrail_bytes = (AGENT / "rules" / "guardrail.yaml").read_bytes()
    summary = f"- **{RULES_CHECK}**: rules/guardrail.yaml: pii EMAIL: ANONYMIZE to NONE"
    answers = {
        "/repos/agentkeel-studio/festival-desk/pulls/1": {"merged": True, "merged_at": "t", "head": {"sha": "a" * 40}, "merge_commit_sha": "1" * 40},
        "/repos/agentkeel-studio/festival-desk/pulls/2": {"merged": False, "merged_at": None, "head": {"sha": "b" * 40}, "merge_commit_sha": None},
        "/repos/agentkeel-studio/festival-desk/pulls/3": {"merged": True, "merged_at": "t", "head": {"sha": "c" * 40}, "merge_commit_sha": "3" * 40},
        f"/repos/agentkeel-studio/festival-desk/commits/{'a' * 40}/check-runs?per_page=100": {"check_runs": [
            {"name": "platform-check", "app": {"id": 5144253}, "conclusion": "success", "output": {"summary": "Every check passed."}}]},
        f"/repos/agentkeel-studio/festival-desk/commits/{'b' * 40}/check-runs?per_page=100": {"check_runs": [
            {"name": "platform-check", "app": {"id": 5144253}, "conclusion": "failure", "output": {"summary": summary}}]},
        f"/repos/agentkeel-studio/festival-desk/commits/{'c' * 40}/check-runs?per_page=100": {"check_runs": [
            {"name": "platform-check", "app": {"id": 5144253}, "conclusion": "success", "output": {"summary": "Every check passed."}}]},
        f"/repos/agentkeel-studio/festival-desk/contents/rules/guardrail.yaml?ref={'1' * 40}": {
            "encoding": "base64", "content": base64.b64encode(guardrail_bytes).decode()},
    }  # fmt: skip

    def fake_gh(path: str, *, raw: bool = False) -> Any:
        import urllib.error

        if path not in answers:
            raise urllib.error.HTTPError(path, 404, "not found", {}, None)  # type: ignore[arg-type]
        return answers[path]

    monkeypatch.setattr(observer, "gh", fake_gh)
    run = tmp_path / "run.yaml"
    run.write_text(yaml.safe_dump({"seed": "run", "repository": "agentkeel-studio/festival-desk", "agent": "festival-desk",
                                   "observed": {"first": {"pull_request": 1}, "second": {"pull_request": 2},
                                                "third": {"pull_request": 3}, "deploy": {"run_id": 1}}}), encoding="utf-8")  # fmt: skip
    out = tmp_path / "rules.json"
    assert observer.main(["--read", "github", "--run", str(run), "--out", str(out)]) == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["made"] is True and written["pulls"]["second"]["check_runs"][0]["refused"] == [RULES_CHECK]
    assert written["pulls"]["second"]["check_runs"][0]["summary"] == summary
    assert written["rules"]["guardrail"]["blocks"] == RULES["blocks"] and written["rules"]["redteam"] is None
    assert written["baseline"]["read_from"] in ("origin/main", "main", "HEAD") and written["tree_digest"] is not None
    # build reads it as the observer handed it over: the heads held, the weakened file refused naming EMAIL
    reading = agent_rules.record({**written, "answer": record(guardrail=STACK), "read_back": read_back(description=f"rules sha256 {written['tree_digest']}")})
    assert reading["F9_4"]["held"] is True and reading["F9_2"]["held"] is True
