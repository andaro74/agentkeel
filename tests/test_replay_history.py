"""replay_history: keyed on golden id, strict about what it reads."""

from __future__ import annotations

import json

import pytest

from src.verdict import replay_history

from .conftest import COMMIT


def test_keyed_on_golden_id_and_blind_to_cards_and_raw(chain):
    envelope_path, _, _ = chain(right={"g-001"})
    history = replay_history.load(envelope_path.parent)  # the folder also holds the card and the raw
    assert set(history) == {f"g-{n:03d}" for n in range(1, 16)}
    assert history["g-001"] == [(COMMIT, True)] and history["g-002"] == [(COMMIT, False)]
    assert replay_history.ever_passed(history, "g-001")
    assert not replay_history.ever_passed(history, "g-002")
    assert not replay_history.ever_passed(history, "g-999")


def test_the_run_under_judgment_is_not_its_own_history(chain):
    envelope_path, _, _ = chain(right={"g-001"})
    assert replay_history.load(envelope_path.parent, exclude_commit=COMMIT) == {}


def test_no_folder_is_an_empty_history(tmp_path):
    assert replay_history.load(tmp_path / "nothing") == {}


def test_a_bad_file_in_history_stops_the_replay(chain):
    envelope_path, _, _ = chain()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    (envelope_path.parent / f"{'b' * 40}.json").write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(ValueError, match="is not the file name"):
        replay_history.load(envelope_path.parent)
    del envelope["baseline_card_ref"]
    (envelope_path.parent / f"{'b' * 40}.json").write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(ValueError, match="not a valid envelope"):
        replay_history.load(envelope_path.parent)
