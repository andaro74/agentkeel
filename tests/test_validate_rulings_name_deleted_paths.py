"""`validate`'s ruling front-matter check and a path a ruling named that was later deleted (M02 PR 3; ADR-0009).

Four rulings from M00 and M01 authorise files under `infra/eval-role/`,
which M02 PR 3 removed after the human destroyed the stack. A ruling is
the record of its PR and is not edited later. Until M03 PR 2 the check
accepted a glob that matched anything deleted anywhere in HEAD's history,
so any new ruling could name any path ever deleted (M02 PR 3 finding 3).
From M03 PR 2 (ADR-0009) a glob must match the tree at its own PR's merge
commit or that commit's first parent; a ruling whose PR has not merged is
held to the tree.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from src.validate import checks

RULING = """---
ruling: r
seat: Engineering
authorises:
  - {pattern}
evidence:
  - SPEC/00-overview.md#8-M02
pr: {pr}
---
"""


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@x", *args], cwd=repo, check=True, capture_output=True)


def repo_where_pr_1_merged_then_deleted(tmp_path: Path) -> Path:
    """infra/old/app.py lands with PR 1's merge commit; PR 2 deletes it; infra/other.py was deleted before PR 1."""
    repo = tmp_path / "repo"
    (repo / "milestones" / "M00" / "rulings").mkdir(parents=True)
    (repo / "infra").mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / "infra" / "other.py").write_text("x\n", encoding="utf-8")
    (repo / "README").write_text("r\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "start")
    git(repo, "rm", "-q", "infra/other.py")
    git(repo, "commit", "-q", "-m", "delete other")
    git(repo, "checkout", "-q", "-b", "pr1")
    (repo / "infra" / "old").mkdir(parents=True)
    (repo / "infra" / "old" / "app.py").write_text("x\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "add old")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "pr1", "-m", "Merge pull request #1 from someone/pr1")
    git(repo, "rm", "-q", "-r", "infra/old")
    git(repo, "commit", "-q", "-m", "delete old")
    return repo


def test_a_glob_that_matched_at_its_own_merge_is_accepted_after_a_later_deletion(tmp_path):
    repo = repo_where_pr_1_merged_then_deleted(tmp_path)
    ruling = repo / "milestones" / "M00" / "rulings" / "r.md"
    for pattern in ("infra/old/app.py", "infra/old/**"):
        ruling.write_text(RULING.format(pattern=pattern, pr=1), encoding="utf-8")
        assert checks.check_rulings(repo) == [], pattern


def test_a_glob_that_only_matches_a_path_deleted_elsewhere_in_history_is_refused(tmp_path):
    """The hole ADR-0009 closes: infra/other.py was deleted before PR 1, so PR 1's ruling never named it."""
    repo = repo_where_pr_1_merged_then_deleted(tmp_path)
    ruling = repo / "milestones" / "M00" / "rulings" / "r.md"
    ruling.write_text(RULING.format(pattern="infra/other.py", pr=1), encoding="utf-8")
    errors = checks.check_rulings(repo)
    assert len(errors) == 1 and "PR 1's merge commit or its first parent" in errors[0]
    # A PR that has not merged is held to the tree: a deleted path is refused there too.
    ruling.write_text(RULING.format(pattern="infra/old/app.py", pr=2), encoding="utf-8")
    errors = checks.check_rulings(repo)
    assert len(errors) == 1 and "matches nothing in the tree" in errors[0]


def test_the_eval_role_rulings_still_validate_in_this_tree():
    """M00 pr2.md and pr3.md, M01 pr1.md and pr2.md name infra/eval-role/ paths; the directory is gone."""
    root = Path(__file__).resolve().parents[1]
    assert not (root / "infra" / "eval-role").exists()
    assert [e for e in checks.check_rulings(root) if "eval-role" in e] == []
