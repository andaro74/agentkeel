"""replay_history: keyed on (scope, golden id), strict about what it reads."""

from __future__ import annotations

import json
import shutil

import pytest

from src.verdict import ROOT, replay_history

from .conftest import COMMIT

PRE_SCOPE = ROOT / "evals" / "history" / "pre-scope"


def test_keyed_on_scope_and_golden_id_and_blind_to_cards_and_raw(chain, goldens):
    envelope_path, _, _ = chain(right={"g-001"})
    history = replay_history.load(envelope_path.parent)  # the folder also holds the card and the raw
    assert set(history) == {("control", g) for g in goldens}  # the live goldens: g-012 is retired, g-021 added (M02 PR 2)
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


# --- only the ancestors (SPEC/03 §6, seed S7) ------------------------------------

HISTORY = ROOT / "evals" / "history"
ROW_2 = "8033c2a7a0588e557df577464c190e64a435e88a"  # row 2's envelope
LATER = "164a95bc4d1b393624e917e89012c64838def531"  # an envelope for a descendant (M03 PR 1)


def test_history_holds_only_the_envelopes_for_ancestors():
    commits = {commit for runs in replay_history.load(HISTORY).values() for commit, _ in runs}
    before = {commit for runs in replay_history.load(HISTORY, ancestors_of=ROW_2).values() for commit, _ in runs}
    assert LATER in commits and LATER not in before, "a later run is not a run before row 2"
    assert ROW_2 in before, "the commit itself is its own ancestor; exclude_commit is what leaves it out"
    assert before < commits
    assert before <= replay_history.ancestry(ROW_2)


def test_a_commit_git_cannot_resolve_reads_every_envelope():
    """A test's made-up sha, a shallow clone: the whole folder, as text_at reads the tree."""
    assert replay_history.ancestry("a" * 40) is None
    assert replay_history.load(HISTORY, ancestors_of="a" * 40) == replay_history.load(HISTORY)
