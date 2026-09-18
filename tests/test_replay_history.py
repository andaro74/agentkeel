"""replay_history: keyed on (scope, golden id), strict about what it reads."""

from __future__ import annotations

import json
import shutil

import pytest

from src.verdict import ROOT, replay_history

from .conftest import COMMIT

PRE_SCOPE = ROOT / "evals" / "history" / "pre-scope"


def test_keyed_on_scope_and_golden_id_and_blind_to_cards_and_raw(chain):
    envelope_path, _, _ = chain(right={"g-001"})
    history = replay_history.load(envelope_path.parent)  # the folder also holds the card and the raw
    assert set(history) == {("control", f"g-{n:03d}") for n in range(1, 16)}
    assert history[("control", "g-001")] == [(COMMIT, True)]
    assert history[("control", "g-002")] == [(COMMIT, False)]
    assert replay_history.ever_passed(history, "control", "g-001")
    assert not replay_history.ever_passed(history, "agent", "g-001")  # a control pass is not an agent pass
    assert not replay_history.ever_passed(history, "control", "g-002")
    assert not replay_history.ever_passed(history, "control", "g-999")


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


def test_the_pre_scope_envelope_is_kept_and_is_not_read(tmp_path):
    """8fb4b80's envelope: evidence of the gate before scope existed. Refused if it were read; it is not read."""
    kept = sorted(PRE_SCOPE.glob("*.json"))
    assert [p.name for p in kept] == ["8fb4b809abcdc00919012e7db65baa495779d3c8.json"]
    assert kept[0] not in replay_history.envelope_paths(PRE_SCOPE.parent)  # a subfolder is not history

    shutil.copy(kept[0], tmp_path / kept[0].name)  # put it where history is read: no tolerance flag
    with pytest.raises(ValueError, match="'scope' is a required property"):
        replay_history.load(tmp_path)
