"""refagent: the tool's contract, and what the runner writes (SPEC/01 §6, ruling l).

No Bedrock call is made here. What is tested is what refagent is answerable
for without one: the tool refuses what its schema forbids, both ways; it
returns the row and never the verdict; and the manifest, the prompt and the
tool contract agree with each other.
"""

from __future__ import annotations

import json

import pytest
import yaml

from agents.refagent import agent
from src.verdict import ROOT

ROWS, SOURCE = agent.rights_rows(None)
MANIFEST = yaml.safe_load((ROOT / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8"))
ASKED = {"title_id": "t-001", "territory": "US", "platform": "SVOD", "date": "2026-12-25"}


def test_the_rights_table_is_read_from_the_file_when_there_is_no_table():
    """On a PR there is no DynamoDB table: refagent's stack is deployed from main (ruling l)."""
    assert SOURCE == "data/rights_table.json"
    assert len(ROWS) == len(json.loads((ROOT / "data" / "rights_table.json").read_text(encoding="utf-8")))


def test_the_tool_returns_one_row_and_the_clauses_it_can_be_read_under():
    result = agent.check_availability(ASKED, ROWS, SOURCE)
    assert result["found"] is True
    assert result["row"]["table_row"] == "r-001"
    assert result["clause_candidates"] and all(isinstance(c, str) for c in result["clause_candidates"])
    # The tool says nothing about whether we may publish. That is the model's.
    assert not {"available", "exclusive", "constraints"} & set(result)


def test_every_clause_the_tool_can_name_exists_in_the_clause_index():
    clauses = set(json.loads((ROOT / "data" / "clause_index.json").read_text(encoding="utf-8")))
    named = set(agent.ALWAYS) | {c for group in agent.BY_FIELD.values() for c in group}
    assert named <= clauses  # F1.4 fails on a clause that does not exist; the tool cannot cause that


def test_a_row_that_is_not_scheduled_is_an_answer_not_an_error():
    result = agent.check_availability({**ASKED, "territory": "JP"}, ROWS, SOURCE)
    assert result == {"found": False, "row": None, "clause_candidates": ["ML-2.1"], "source": SOURCE}


@pytest.mark.parametrize("bad", [
    {**ASKED, "platform": "DVD"},           # not one of the four
    {**ASKED, "territory": "United States"},  # the name, not the code
    {**ASKED, "title_id": "Quorum of Kites"},  # the title, not the id
    {**ASKED, "date": "Christmas"},
    {**ASKED, "extra": 1},                  # additionalProperties false
    {"title_id": "t-001"},                  # required
])  # fmt: skip
def test_the_tool_refuses_arguments_its_schema_forbids(bad):
    with pytest.raises(ValueError, match="check_availability arguments"):
        agent.check_availability(bad, ROWS, SOURCE)


def test_the_tool_refuses_its_own_result_if_the_row_is_not_the_shape_it_promises():
    """Strict both ways: a row with a field the contract does not name is refused here, not downstream."""
    with pytest.raises(ValueError, match="check_availability result"):
        agent.check_availability(ASKED, [{**ROWS[0], "note": "added by hand"}], SOURCE)


def test_the_tool_spec_bedrock_is_given_is_the_contract_in_the_tree():
    spec = agent.tool_config()["tools"][0]["toolSpec"]
    contract = json.loads((ROOT / "agents" / "refagent" / "tools" / "check_availability.json").read_text("utf-8"))
    assert spec["name"] == contract["name"] == "check_availability"
    assert spec["inputSchema"]["json"] == contract["input"]
    assert contract["input"]["additionalProperties"] is False
    assert contract["output"]["additionalProperties"] is False


def test_the_prompt_names_every_title_and_the_model_the_manifest_pins():
    slate = json.loads((ROOT / "data" / "slate.json").read_text(encoding="utf-8"))["titles"]
    for title in slate:
        assert f"{title['title_id']} {title['title']}" in agent.PROMPT
    assert MANIFEST["model"]["profile"] == "us.anthropic.claude-sonnet-4-6"
    assert MANIFEST["memory"] is None and MANIFEST["may_call"] == []  # cuts 1, 3 and 4, taken at open


def test_a_reply_that_is_not_json_parses_to_nothing_rather_than_being_repaired():
    assert agent.parse_json("I think we can publish.") is None
    assert agent.parse_json('here you go: {"table_row": "r-001"} ok') == {"table_row": "r-001"}


def test_two_rows_on_one_key_is_refused_rather_than_chosen_between():
    """Tool Owner finding 6: nothing holds (title, territory, platform) unique in the table."""
    twice = [*ROWS, {**ROWS[0], "table_row": "r-999"}]
    with pytest.raises(ValueError, match="2 rows for t-001/US/SVOD: r-001, r-999"):
        agent.check_availability(ASKED, twice, SOURCE)


def test_every_row_field_the_prompt_names_is_in_the_tool_contract():
    """Tool Owner finding 9: nothing bound the prompt's field names to the schema."""
    contract = json.loads((ROOT / "agents" / "refagent" / "tools" / "check_availability.json").read_text("utf-8"))
    row_fields = set(contract["output"]["properties"]["row"]["anyOf"][1]["properties"])
    for field in ("window_start", "window_end", "holdback_until", "clearance_expiry", "embargo_lift_local"):
        assert field in row_fields and field in agent.PROMPT
    assert "clause_candidates" in contract["output"]["properties"] and "clause_candidates" in agent.PROMPT


def test_the_rights_table_has_one_row_per_title_territory_platform_today():
    """The tool refuses a repeat; this says the table does not have one now."""
    keys = [(r["title_id"], r["territory"], r["platform"]) for r in ROWS]
    assert len(keys) == len(set(keys))
