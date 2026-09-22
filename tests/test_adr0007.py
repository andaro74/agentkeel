"""ADR-0007: the envelope says where the agent ran, in which region, on which version.

build writes what the run reports; the gate judges it. Each rule below has a
case the gate refuses, and the build-and-gate pair disagrees on two of them,
which is what CLAUDE.md asks of every envelope field (P5).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.verdict import ROOT, build, gate, replay_history, schema_errors

from .conftest import AGENT_TOP, REFAGENT_PIN

RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-west-2:111122223333:runtime/refagent-abc"


def rewrite(path: Path, **fields) -> Path:
    envelope = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps({**envelope, **fields}), encoding="utf-8")
    return path


# --- history is version 1, and stays readable -------------------------------


def test_every_envelope_in_history_still_validates_and_replays():
    """The fields are versioned, not required outright: 23 envelopes of evidence are not rewritten."""
    paths = replay_history.envelope_paths(ROOT / "evals" / "history")
    assert paths
    for path in paths:
        envelope = json.loads(path.read_text(encoding="utf-8"))
        assert "schema_version" not in envelope, f"{path.name} predates ADR-0007"
        assert schema_errors(envelope) == [], path.name
    replay_history.load(ROOT / "evals" / "history")


# --- the schema --------------------------------------------------------------


def test_version_2_requires_all_four_fields(chain):
    envelope = json.loads(chain(agent=True)[0].read_text(encoding="utf-8"))
    for field in ("mode", "runtime_arn", "region", "model_version"):
        assert schema_errors({k: v for k, v in envelope.items() if k != field}), f"{field} is optional on v2"


def test_a_field_without_the_version_does_not_validate(chain):
    """Otherwise a version 1 envelope could carry a mode the gate never checks."""
    envelope = json.loads(chain(agent=True)[0].read_text(encoding="utf-8"))
    envelope.pop("schema_version")
    assert schema_errors(envelope)


# --- build writes what the run reports --------------------------------------


def test_build_writes_version_2_with_the_runs_mode(chain):
    control = json.loads(chain()[0].read_text(encoding="utf-8"))
    assert (control["schema_version"], control["mode"], control["runtime_arn"]) == (2, "control", None)
    agent = json.loads(chain(agent=True)[0].read_text(encoding="utf-8"))
    assert (agent["mode"], agent["runtime_arn"], agent["region"]) == ("runner", None, REFAGENT_PIN["region"])
    assert agent["model_version"] == REFAGENT_PIN["version"]  # T1: the pin's, not a second source


def test_build_refuses_an_agent_raw_that_does_not_say_where_it_ran(goldens):
    from .conftest import make_raw

    raw = make_raw(goldens, **{k: v for k, v in AGENT_TOP.items() if k != "mode"})
    with pytest.raises(build.Refused, match="does not say where it ran"):
        build.subject(raw, "agent")


def test_a_runtime_run_is_read(chain):
    path = chain(agent=True, mode="runtime", runtime_arn=RUNTIME_ARN)[0]
    assert gate.read(path)["mode"] == "runtime"


# --- the gate judges it -------------------------------------------------------


@pytest.mark.parametrize("mode, arn", [("runtime", None), ("runner", RUNTIME_ARN)])
def test_build_and_gate_disagree_on_a_mode_without_its_arn(chain, mode, arn):
    """P5: build writes the pairing as the run reports it; only the gate refuses it."""
    path = chain(agent=True, mode=mode, runtime_arn=arn)[0]  # build wrote it: exit 0
    with pytest.raises(gate.Rejected, match="a runtime run names its runtime"):
        gate.read(path)


@pytest.mark.parametrize("field, value", [
    ("model_id", "us.anthropic.claude-sonnet-5"),
    ("region", "us-east-1"),
    ("model_version", "20260101"),
])  # fmt: skip
def test_a_run_off_the_pin_is_rejected_not_red(chain, field, value):
    """T3. A run on another model or region did not measure the pinned subject."""
    path = rewrite(chain(agent=True)[0], **{field: value})
    with pytest.raises(gate.Rejected, match=f"{field} .* is not the pin .*T3"):
        gate.read(path)


def test_build_and_gate_disagree_on_a_region_off_the_pin(chain):
    """P5 again: build writes the region the run reports; the gate compares it with the pin."""
    path = chain(agent=True, region="us-east-1")[0]  # build wrote it: exit 0
    with pytest.raises(gate.Rejected, match="region 'us-east-1' is not the pin"):
        gate.read(path)


@pytest.mark.parametrize("agent, mode", [(True, "control"), (False, "runner")])
def test_the_mode_matches_the_shape_of_the_envelope(chain, agent, mode):
    path = rewrite(chain(agent=agent)[0], mode=mode)
    with pytest.raises(gate.Rejected, match=f"envelope says mode {mode}"):
        gate.read(path)


def test_the_ledger_cell_names_the_mode_only_on_version_2(chain):
    envelope_path = chain()[0]
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    assert "mode control" in gate.measured(envelope, "GREEN")
    v1 = {k: v for k, v in envelope.items()
          if k not in ("schema_version", "mode", "runtime_arn", "region", "model_version")}  # fmt: skip
    assert "mode" not in gate.measured(v1, "GREEN")
