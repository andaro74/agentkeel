"""F0.2: an envelope validates without a baseline ref.

The second seed is tests/fixtures/hand_written_envelope_no_baseline_card_ref.json.
It was committed with this file before src/verdict/ existed. CI reads this
module's junit result into the envelope as checks.F0_2.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.verdict import gate

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
