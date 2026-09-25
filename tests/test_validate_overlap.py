"""validate: golden/corpus overlap at 12 words, and no row id in the corpus (M03 PR 2, S3's reader)."""

from __future__ import annotations

import shutil

import pytest

from src.validate import overlap
from src.verdict import ROOT

G010 = ("The German theatrical release of 'Quorum of Kites: Second Wind' has moved up two weeks, to 2026-12-03. "
        "PVOD usually follows theatrical by 45 days. Can we publish it on PVOD in Germany on 2027-01-20?")  # fmt: skip


def test_words_collapse_punctuation_and_split_dates():
    assert overlap.words("On 2026-12-03, 'Quorum' ends.") == ["on", "2026", "12", "03", "quorum", "ends"]


def test_the_longest_shared_run():
    assert overlap.longest_shared_run("a b c d e".split(), "x b c d y".split()) == 3
    assert overlap.longest_shared_run([], ["a"]) == 0


@pytest.fixture
def tree(tmp_path):
    shutil.copytree(ROOT / "evals" / "goldens", tmp_path / "evals" / "goldens")
    (tmp_path / "data" / "corpus").mkdir(parents=True)
    return tmp_path


def document(tree, text: str) -> None:
    (tree / "data" / "corpus" / "doc.md").write_text(text, encoding="utf-8")


def test_the_tree_has_no_corpus_yet_and_nothing_to_refuse():
    assert overlap.check(ROOT) == []


def test_eleven_shared_words_pass_and_twelve_are_refused(tree):
    eleven = " ".join(overlap.words(G010)[:11])
    document(tree, f"Unrelated text. {eleven}. More unrelated text.")
    assert overlap.check(tree) == []
    twelve = " ".join(overlap.words(G010)[:12])
    document(tree, f"Unrelated text. {twelve}. More unrelated text.")
    assert overlap.check(tree) == [
        "data/corpus/doc.md: shares 12 words in a row with g-010's question (the bound is 12)"]


def test_a_row_id_in_a_document_is_refused(tree):
    document(tree, "The governing row is r-009.")
    assert overlap.check(tree) == ["data/corpus/doc.md: names rights-table rows r-009; a corpus document never names a row"]


def test_admitted_yaml_is_not_a_document(tree):
    (tree / "data" / "corpus" / "admitted.yaml").write_text(f"# {G010}\n- key: r-009\n", encoding="utf-8")
    assert overlap.check(tree) == []


def test_a_retired_golden_is_not_held(tree):
    retired = tree / "evals" / "goldens" / "v1" / "g-010.yaml"
    retired.write_text(retired.read_text(encoding="utf-8").replace("retired: null", "retired: M03"), encoding="utf-8")
    document(tree, G010)
    assert overlap.check(tree) == []
