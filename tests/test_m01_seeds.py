"""M01's seeded cases S1-S8 (SPEC/01 §5), committed before the code that reads them.

Each test says what the reader must do to its seed. Until the reader is in
the tree the test fails, and it is marked `xfail(strict=True)`: an expected
failure now, and a failure the first time it passes, so the marker has to
come off in the commit that lands the reader. A seed cannot start passing
without somebody saying so.

Every marker is off as of M01 PR 2: each seed's reader is in the tree. S1
and S2 are read by src/bundle/verify.py, S3, S5 and S8 by infra/construct/,
S4 and S6 by scripts/observe_attempt.py and `--check-attempt`, S7 by
`verdict.build` and `verdict.gate` (its marker came off at PR 1).

S4 and S6 fail while their run files say `observed: null`, and that is the
row going RED until the human makes the attempts — not a marker waiting to
come off. A strict xfail here would have done the opposite: it would have
failed the measuring run the moment the attempts were recorded.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from src.verdict import ROOT, build, gate

from .conftest import COMMIT, URL, make_raw

FIXTURES = Path(__file__).parent / "fixtures"
RUNS = ROOT / "milestones" / "M01" / "runs"


def test_s1_an_unsigned_bundle_is_refused():
    from src.bundle import verify

    with pytest.raises(verify.Refused, match="signature"):
        verify.verify(FIXTURES / "bundles" / "unsigned")


def test_s2_a_bundle_changed_after_signing_is_refused():
    """Refused because its bytes hash to something else — not because no digest was found."""
    from src.bundle import pack, verify

    with pytest.raises(verify.Refused) as refusal:
        verify.verify(FIXTURES / "bundles" / "altered")
    signed = verify.signed_digest(verify.cosign_bundle(FIXTURES / "bundles" / "altered"))
    digests = [reason for reason in refusal.value.reasons if reason.startswith("digest: ")]
    assert len(digests) == 1 and signed[:12] in digests[0]
    assert pack.digest(pack.pack(FIXTURES / "bundles" / "altered", Path(tempfile.mkdtemp()) / "s2.tar"))[:12] \
        in digests[0]  # the bundle's own digest is in the reason, so the comparison really ran


def test_s3_egress_not_in_the_manifest_is_refused_at_synth():
    """Both forms: through the construct's own security group, and as a separate resource."""
    from infra.construct import synth_refusal

    through = synth_refusal(FIXTURES / "construct" / "extra_egress.py")
    standalone = synth_refusal(FIXTURES / "construct" / "extra_egress_standalone.py")
    for refusal in (through, standalone):
        assert refusal is not None and "egress to 0.0.0.0/0" in refusal
    # the second is refused as what it is: a rule the construct never saw
    assert "added outside the construct" in standalone
    assert "added outside the construct" not in through


def test_s4_a_laptop_deploy_was_refused():
    run = yaml.safe_load((RUNS / "f1_1_laptop.yaml").read_text(encoding="utf-8"))
    observed = run["observed"]
    assert observed is not None, "the attempt has not been made"
    assert len(observed) == len(run["attempts"]), "every attempt is made, not some"
    assert all(attempt["result"] == "AccessDenied" and attempt["request_id"] for attempt in observed)


def test_s5_a_role_without_the_boundary_is_refused_at_synth():
    from infra.construct import synth_refusal

    refusal = synth_refusal(FIXTURES / "construct" / "role_without_boundary.py")
    assert refusal is not None and "no permissions boundary" in refusal


def test_s6_the_agent_role_cannot_read_its_key_policy():
    run = yaml.safe_load((RUNS / "f1_3_key_policy.yaml").read_text(encoding="utf-8"))
    observed = run["observed"]
    assert observed is not None, "the attempt has not been made"
    assert len(observed) == len(run["attempts"]), "every attempt is made, not some"
    assert all(attempt["result"] == "AccessDenied" and attempt["request_id"] for attempt in observed)
    assert all("resource-based policy" in attempt["message"] for attempt in observed)  # the key policy refused it


def test_s8_an_agent_outside_the_construct_is_refused_at_synth():
    from infra.construct import synth_refusal

    refusal = synth_refusal(FIXTURES / "construct" / "outside_construct.py")
    assert refusal is not None and "not a GovernedAgent's own runtime" in refusal


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
