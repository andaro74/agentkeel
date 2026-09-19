"""M01's seeded cases S1-S8 (SPEC/01 §5), committed before the code that reads them.

Each test says what the reader must do to its seed. Until the reader is in
the tree the test fails, and it is marked `xfail(strict=True)`: an expected
failure now, and a failure the first time it passes, so the marker has to
come off in the commit that lands the reader. A seed cannot start passing
without somebody saying so.

S1-S6 and S8 are read at M01 PR 2. S7 is read by `verdict.build` and `verdict.gate`
in M01 PR 1, in the commit after this one.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from src.verdict import ROOT, build, gate

from .conftest import COMMIT, URL, make_raw

FIXTURES = Path(__file__).parent / "fixtures"
RUNS = ROOT / "milestones" / "M01" / "runs"
PR2 = "no reader until M01 PR 2"


@pytest.mark.xfail(strict=True, raises=ModuleNotFoundError, reason=f"S1: {PR2} (src/bundle/verify.py)")
def test_s1_an_unsigned_bundle_is_refused():
    from src.bundle import verify  # type: ignore[import-not-found]

    with pytest.raises(verify.Refused, match="signature"):
        verify.verify(FIXTURES / "bundles" / "unsigned")


@pytest.mark.xfail(strict=True, raises=ModuleNotFoundError, reason=f"S2: {PR2} (src/bundle/verify.py)")
def test_s2_a_bundle_changed_after_signing_is_refused():
    from src.bundle import verify  # type: ignore[import-not-found]

    with pytest.raises(verify.Refused, match="digest"):
        verify.verify(FIXTURES / "bundles" / "altered")


@pytest.mark.xfail(strict=True, raises=ModuleNotFoundError, reason=f"S3: {PR2} (infra/construct/)")
def test_s3_egress_not_in_the_manifest_is_refused_at_synth():
    from infra.construct import synth_refusal  # type: ignore[import-not-found]

    assert synth_refusal(FIXTURES / "construct" / "extra_egress.py") is not None
    assert synth_refusal(FIXTURES / "construct" / "extra_egress_standalone.py") is not None


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=f"S4: {PR2} (the bootstrap stack's deploy role)")
def test_s4_a_laptop_deploy_was_refused():
    observed = yaml.safe_load((RUNS / "f1_1_laptop.yaml").read_text(encoding="utf-8"))["observed"]
    assert observed is not None, "the attempt has not been made"
    assert all(attempt["result"] == "AccessDenied" for attempt in observed)


@pytest.mark.xfail(strict=True, raises=ModuleNotFoundError, reason=f"S5: {PR2} (infra/construct/)")
def test_s5_a_role_without_the_boundary_is_refused_at_synth():
    from infra.construct import synth_refusal  # type: ignore[import-not-found]

    assert synth_refusal(FIXTURES / "construct" / "role_without_boundary.py") is not None


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=f"S6: {PR2} (the bootstrap stack's key policy)")
def test_s6_the_agent_role_cannot_read_its_key_policy():
    observed = yaml.safe_load((RUNS / "f1_3_key_policy.yaml").read_text(encoding="utf-8"))["observed"]
    assert observed is not None, "the attempt has not been made"
    assert all(attempt["result"] == "AccessDenied" for attempt in observed)
    assert all("resource-based policy" in attempt["message"] for attempt in observed)  # the key policy refused it


@pytest.mark.xfail(strict=True, reason="S7: the F1.4 rule is not in verdict.build or verdict.gate yet")
def test_s7_an_answer_that_cites_nothing_is_not_a_pass(tmp_path, goldens):
    """Every answer field right, no table_row, no clause_id: pass false, checks.F1_4 fail, RED (F1.4)."""
    control_raw = tmp_path / f"{COMMIT}.baseline-raw.json"
    control_raw.write_text(json.dumps(make_raw(goldens)), encoding="utf-8")
    card = tmp_path / f"{COMMIT}.baseline-card.json"
    assert build.main(["card", "--raw", str(control_raw), "--out", str(card)]) == 0

    seed = json.loads((FIXTURES / "refagent_raw_uncited.json").read_text(encoding="utf-8"))
    agent_raw = tmp_path / f"{COMMIT}.agent-raw.json"
    agent_raw.write_text(json.dumps({**seed, "commit": COMMIT}), encoding="utf-8")
    out, no_history = tmp_path / f"{COMMIT}.json", tmp_path / "no-history"
    assert build.main(["envelope", "--raw", str(agent_raw), "--control-card", str(card), "--out", str(out),
                       "--history-dir", str(no_history), "--run-url", URL]) == 0  # fmt: skip

    citing = {g: r for g, r in gate.read(out)["goldens"].items() if r["kind"] in build.CITING_KINDS}
    assert len(citing) == 12
    for result in citing.values():
        assert result == {"kind": result["kind"], "scope": "agent", "score": True, "cites": False, "pass": False}
    envelope = gate.read(out)
    assert envelope["checks"]["F1_4"]["status"] == "fail"  # build: RED on the first run, whatever the history
    assert envelope["verdict"] == "RED"
    verdict, reasons = gate.rule(out, no_history)
    assert verdict == "RED"  # the gate works F1.4 out again from goldens, and agrees
    assert not any("pass is not" in reason or "F1_4 is" in reason for reason in reasons)


@pytest.mark.xfail(strict=True, raises=ModuleNotFoundError, reason=f"S8: {PR2} (infra/construct/)")
def test_s8_an_agent_outside_the_construct_is_refused_at_synth():
    from infra.construct import synth_refusal  # type: ignore[import-not-found]

    assert synth_refusal(FIXTURES / "construct" / "outside_construct.py") is not None
