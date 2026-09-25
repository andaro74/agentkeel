"""validate: admitted.yaml is the corpus, byte for byte, under a Data Owner ruling (M03 PR 2; data-owner F7)."""

from __future__ import annotations

import shutil

import pytest
import yaml

from src.validate import corpus
from src.verdict import ROOT

RULING = "milestones/M03/rulings/pr2-data-owner.md"


def test_the_corpus_in_the_tree_passes():
    assert corpus.check(ROOT) == []


def test_the_unsigned_amendment_is_not_in_the_corpus():
    """Seed S5 is never under data/corpus/ and never admitted (SPEC/03 section 5)."""
    import hashlib

    s5 = hashlib.sha256((ROOT / "tests" / "fixtures" / "m03" / "s5-unsigned-amendment.md").read_bytes()).hexdigest()
    admitted = yaml.safe_load((ROOT / corpus.ADMITTED).read_text(encoding="utf-8"))
    assert s5 not in {e["sha256"] for e in admitted}
    assert not any("amendment no. 2" in p.read_text(encoding="utf-8").lower()
                   for p in (ROOT / corpus.CORPUS).glob("*.md"))  # fmt: skip


@pytest.fixture
def tree(tmp_path):
    shutil.copytree(ROOT / corpus.CORPUS, tmp_path / corpus.CORPUS)
    (tmp_path / "milestones" / "M03" / "rulings").mkdir(parents=True)
    shutil.copy(ROOT / RULING, tmp_path / RULING)
    return tmp_path


def entries(tree) -> list[dict]:
    return yaml.safe_load((tree / corpus.ADMITTED).read_text(encoding="utf-8"))


def rewrite(tree, entries_: list[dict]) -> None:
    (tree / corpus.ADMITTED).write_text(yaml.safe_dump(entries_), encoding="utf-8")


def test_a_changed_byte_is_refused(tree):
    path = tree / corpus.CORPUS / "embargo-memo.md"
    path.write_bytes(path.read_bytes() + b"\n")
    assert corpus.check(tree) == ["data/corpus/embargo-memo.md: its bytes are not the sha256 admitted.yaml names"]


def test_a_document_nobody_admitted_is_refused(tree):
    (tree / corpus.CORPUS / "amendment-2.md").write_text("Amendment No. 2, unsigned.\n", encoding="utf-8")
    assert corpus.check(tree) == ["data/corpus/amendment-2.md: in the corpus and not in admitted.yaml"]


def test_an_admitted_document_that_is_gone_is_refused(tree):
    (tree / corpus.CORPUS / "ratings-letter.md").unlink()
    assert corpus.check(tree) == ["data/corpus/ratings-letter.md: admitted and not in the tree"]


def test_a_ruling_of_another_seat_does_not_admit(tree):
    path = tree / RULING
    path.write_text(path.read_text(encoding="utf-8").replace("seat: Data Owner", "seat: Engineering"), encoding="utf-8")
    assert all("not Data Owner" in e for e in corpus.check(tree)) and len(corpus.check(tree)) == 6


def test_a_ruling_that_does_not_authorise_the_path_does_not_admit(tree):
    path = tree / RULING
    path.write_text(path.read_text(encoding="utf-8").replace("  - data/corpus/**\n", ""), encoding="utf-8")
    assert all("does not authorise it" in e for e in corpus.check(tree)) and len(corpus.check(tree)) == 6


def test_an_entry_admitted_twice_is_refused(tree):
    rewrite(tree, entries(tree) + entries(tree)[:1])
    assert "data/corpus/admitted.yaml: amendment-1.md is admitted twice" in corpus.check(tree)


def test_no_corpus_passes(tmp_path):
    assert corpus.check(tmp_path) == []
