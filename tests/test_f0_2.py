"""F0.2: an envelope validates without a baseline ref.

The second seed is tests/fixtures/hand_written_envelope_no_baseline_card_ref.json.
It was committed with the first two tests here before src/verdict/ existed.
CI reads this module's junit result into the envelope as checks.F0_2.

The rest build the same false state in memory (ruling on report 3.2): an
in-memory dict is not a committed envelope.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.verdict import build, gate

from .conftest import make_raw

FIXTURE = (
    Path(__file__).parent / "fixtures" / "hand_written_envelope_no_baseline_card_ref.json"
)
REF = {"path": "evals/history/" + "0" * 40 + ".baseline-card.json", "sha256": "0" * 64}


def test_gate_rejects_the_hand_written_envelope():
    with pytest.raises(gate.Rejected, match="baseline_card_ref"):
        gate.read(FIXTURE)


def test_the_missing_ref_is_the_only_reason():
    envelope = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert "baseline_card_ref" not in envelope
    assert any("baseline_card_ref" in e for e in gate.schema_errors(envelope))
    assert gate.schema_errors({**envelope, "baseline_card_ref": REF}) == []


def envelope_without_ref(chain) -> dict:
    """A real build-written envelope, with the ref taken out in memory."""
    envelope_path, _, _ = chain()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    assert gate.schema_errors(envelope) == []  # valid until the ref goes
    del envelope["baseline_card_ref"]
    return envelope


def test_build_refuses_to_emit_an_envelope_with_no_ref(chain, tmp_path):
    out = tmp_path / "refused.json"
    with pytest.raises(build.Refused, match="baseline_card_ref"):
        build.emit(envelope_without_ref(chain), out, envelope=True)
    assert not out.exists()


def test_gate_rejects_it_if_written_by_hand(chain, tmp_path):
    by_hand = tmp_path / "by_hand.json"
    by_hand.write_text(json.dumps(envelope_without_ref(chain)), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="baseline_card_ref"):
        gate.read(by_hand)
    assert gate.main([str(by_hand)]) == 2


def test_a_run_without_a_baseline_card_is_refused(goldens, tmp_path, capsys):
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps(make_raw(goldens)), encoding="utf-8")
    out = tmp_path / "envelope.json"
    assert build.main(["envelope", "--raw", str(raw), "--out", str(out)]) == 3
    assert "no baseline card" in capsys.readouterr().err
    assert not out.exists()


def test_a_ref_to_nothing_or_to_an_altered_card_is_rejected(chain):
    envelope_path, card_path, _ = chain()
    gate.read(envelope_path)  # accepted as built

    card = json.loads(card_path.read_text(encoding="utf-8"))
    card_path.write_text(json.dumps({**card, "tokens_out": 1}), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="not the one the envelope names"):
        gate.read(envelope_path)

    card_path.unlink()
    with pytest.raises(gate.Rejected, match="does not resolve"):
        gate.read(envelope_path)
