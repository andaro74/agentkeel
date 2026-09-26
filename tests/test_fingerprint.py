"""The corpus fingerprint: build writes it, the gate reads it again at the commit (M03 PR 2; SPEC/03 §2, S4)."""

from __future__ import annotations

import hashlib
import json

import yaml

from src.verdict import ROOT, fingerprint_at, fingerprint_of, gate

ADMITTED = (ROOT / "data" / "corpus" / "admitted.yaml").read_text(encoding="utf-8")


def test_the_fingerprint_is_sha256_over_key_and_sha256_lines_sorted_by_key():
    entries = yaml.safe_load(ADMITTED)
    lines = "".join(f"{e['key']} {e['sha256']}\n" for e in sorted(entries, key=lambda e: e["key"]))
    assert fingerprint_of(ADMITTED) == hashlib.sha256(lines.encode("utf-8")).hexdigest()


def test_the_order_of_admitted_yaml_does_not_move_it_and_a_changed_byte_does():
    entries = yaml.safe_load(ADMITTED)
    assert fingerprint_of(yaml.safe_dump(list(reversed(entries)))) == fingerprint_of(ADMITTED)
    entries[0]["sha256"] = "0" * 64
    assert fingerprint_of(yaml.safe_dump(entries)) != fingerprint_of(ADMITTED)


def test_no_corpus_is_none():
    assert fingerprint_of(None) is None
    assert fingerprint_at("d2d1e6de29d85d2e566afb913c46c7780ec3467c")[0] is None, "main before the corpus"


def test_the_gate_reads_the_tree_it_is_given(tmp_path):
    assert gate.corpus_fingerprint(tmp_path) is None
    (tmp_path / "data" / "corpus").mkdir(parents=True)
    (tmp_path / "data" / "corpus" / "admitted.yaml").write_text(ADMITTED, encoding="utf-8")
    assert gate.corpus_fingerprint(tmp_path) == fingerprint_of(ADMITTED)


def test_an_envelope_whose_fingerprint_is_not_the_gates_reading_is_red():
    envelope = json.loads((ROOT / "evals" / "history" / "8033c2a7a0588e557df577464c190e64a435e88a.json")
                          .read_text(encoding="utf-8"))  # fmt: skip
    kinds = {g: r["kind"] for g, r in envelope["goldens"].items()}
    # Row 2's envelope, null, against no corpus: nothing about the fingerprint.
    _, reasons = gate.judge(envelope, kinds, {}, [], corpus=None)
    assert not any("corpus_fingerprint" in r for r in reasons)
    # The same envelope claiming a corpus the gate does not read.
    envelope["corpus_fingerprint"] = "f" * 64
    verdict, reasons = gate.judge(envelope, kinds, {}, [], corpus=None)
    assert verdict == "RED" and any(r.startswith("corpus_fingerprint: the envelope says") for r in reasons)


def test_rule_holds_an_envelope_to_the_fingerprint_it_reads_at_the_commit(monkeypatch):
    """The cold review of PR 2, F1: through gate.rule, not judge alone. Row 2's envelope says null; a commit
    that admits a corpus reads non-null, so the same envelope there is RED for the fingerprint."""
    envelope = ROOT / "evals" / "history" / "8033c2a7a0588e557df577464c190e64a435e88a.json"
    assert gate.rule(envelope)[0] == "GREEN", "at 8033c2a no corpus is admitted, and null agrees"
    monkeypatch.setattr(gate, "fingerprint_at", lambda commit, root=ROOT: ("f" * 64, "a commit that admits one"))
    verdict, reasons = gate.rule(envelope)
    assert verdict == "RED" and any(r.startswith("corpus_fingerprint: the envelope says None") for r in reasons)


def test_the_gate_refuses_a_shallow_clone(monkeypatch):
    """The cold review of PR 2, F3: the readers at a commit fall back to the tree where git cannot place it."""
    import pytest

    assert gate.shallow() is False, "this checkout has its full history"
    monkeypatch.setattr(gate, "shallow", lambda root=ROOT: True)
    with pytest.raises(gate.Rejected, match="a shallow clone"):
        gate.rule(ROOT / "evals" / "history" / "8033c2a7a0588e557df577464c190e64a435e88a.json")
