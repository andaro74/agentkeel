"""`validate`'s ruling front-matter check and a path a ruling named that was later deleted (M02 PR 3).

Four rulings from M00 and M01 authorise files under `infra/eval-role/`,
which M02 PR 3 removed after the human destroyed the stack. A ruling is
the record of its PR and is not edited later, so the check accepts a glob
that names something deleted from the tree in HEAD's history; a glob that
never named anything is still an error.
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
pr: 1
---
"""


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def repo_with_a_deleted_file(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "milestones" / "M00" / "rulings").mkdir(parents=True)
    (repo / "infra" / "old").mkdir(parents=True)
    (repo / "infra" / "old" / "app.py").write_text("x\n", encoding="utf-8")
    git(repo, "init", "-q")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@x", "add", ".")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@x", "commit", "-q", "-m", "add")
    git(repo, "rm", "-q", "-r", "infra/old")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@x", "commit", "-q", "-m", "delete")
    return repo


def test_a_glob_that_names_a_deleted_path_is_accepted_and_one_that_never_named_anything_is_not(tmp_path):
    repo = repo_with_a_deleted_file(tmp_path)
    ruling = repo / "milestones" / "M00" / "rulings" / "r.md"
    for pattern in ("infra/old/app.py", "infra/old/**", "infra/**"):
        ruling.write_text(RULING.format(pattern=pattern), encoding="utf-8")
        assert checks.check_rulings(repo) == [], pattern
    ruling.write_text(RULING.format(pattern="infra/never/**"), encoding="utf-8")
    errors = checks.check_rulings(repo)
    assert len(errors) == 1 and "nor anything deleted from it" in errors[0]


def test_the_eval_role_rulings_still_validate_in_this_tree():
    """M00 pr2.md and pr3.md, M01 pr1.md and pr2.md name infra/eval-role/ paths; the directory is gone."""
    root = Path(__file__).resolve().parents[1]
    assert not (root / "infra" / "eval-role").exists()
    assert "infra/eval-role/app.py" in checks.deleted_paths(root)
    assert [e for e in checks.check_rulings(root) if "eval-role" in e] == []
