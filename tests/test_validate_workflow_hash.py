"""validate's workflow-hash check (Security, M01 open item 29)."""

from __future__ import annotations

import shutil

from src.validate import checks
from src.verdict import ROOT


def tree(tmp_path):
    """A copy of the repo's workflows and their hash file."""
    shutil.copytree(ROOT / ".github" / "workflows", tmp_path / ".github" / "workflows")
    (tmp_path / "infra").mkdir()
    shutil.copy(ROOT / checks.WORKFLOW_HASHES, tmp_path / checks.WORKFLOW_HASHES)
    return tmp_path


def test_the_repo_passes():
    assert checks.check_workflow_hashes(ROOT) == []


def test_an_edited_workflow_fails(tmp_path):
    root = tree(tmp_path)
    evals = root / ".github" / "workflows" / "evals.yml"
    evals.write_bytes(evals.read_bytes() + b"# one more line\n")
    assert any("evals.yml: sha256" in error for error in checks.check_workflow_hashes(root))


def test_a_new_workflow_fails_and_a_missing_one_fails(tmp_path):
    root = tree(tmp_path)
    (root / ".github" / "workflows" / "second.yml").write_text("name: second\n", encoding="utf-8")
    assert "second.yml: a workflow file not listed" in " ".join(checks.check_workflow_hashes(root))
    (root / ".github" / "workflows" / "second.yml").unlink()
    (root / ".github" / "workflows" / "cold-review-ruling.yml").unlink()
    assert any("listed in infra/workflows.sha256 and not in the tree" in e for e in checks.check_workflow_hashes(root))


def test_line_endings_do_not_change_the_hash(tmp_path):
    root = tree(tmp_path)
    evals = root / ".github" / "workflows" / "evals.yml"
    evals.write_bytes(evals.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    assert checks.check_workflow_hashes(root) == []


def test_no_hash_file_fails(tmp_path):
    root = tree(tmp_path)
    (root / checks.WORKFLOW_HASHES).unlink()
    assert checks.check_workflow_hashes(root) == ["infra/workflows.sha256: missing"]
