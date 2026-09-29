"""cold-review-ruling's own script, run against rulings in a scratch tree (milestones/M05/open.md row 44).

The step is shell in the workflow; these run that shell, as it is in the file, with bash.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "cold-review-ruling.yml"
BASH = shutil.which("bash")


def script() -> str:
    steps = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["cold-review-ruling"]["steps"]
    return next(step["run"] for step in steps if step.get("name") == "A ruling file names this PR")


def ruling(pr: int, body: str) -> str:
    return f"---\n# Drafted by someone, in a comment\nruling: x\nseat: Product\nauthorises: []\nevidence: []\npr: {pr}\n---\n\n{body}\n"


def run(tmp_path: Path, files: dict[str, str], pr: int = 31) -> subprocess.CompletedProcess:
    for name, text in files.items():
        path = tmp_path / "milestones" / "M05" / "rulings" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    return subprocess.run([BASH, "-c", script()], cwd=tmp_path, capture_output=True, text=True,
                          env={"PR": str(pr), "REPO": "andaro74/agentkeel", "PATH": str(Path(BASH).parent)})  # fmt: skip


pytestmark = pytest.mark.skipif(BASH is None, reason="bash is not on this machine")


def test_every_ruling_for_the_pr_ruled_passes(tmp_path):
    done = run(tmp_path, {"pr2.md": ruling(31, "# Ruling\n\nRuled by andaro74 as Product, 2026-09-29, as written."),
                          "pr1.md": ruling(30, "Drafted by the session.")})  # another PR's draft is not this PR's
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_ruling_still_drafted_fails_and_names_the_file(tmp_path):
    done = run(tmp_path, {"pr2.md": ruling(31, "Ruled by andaro74 as Product, 2026-09-29."),
                          "pr2-security.md": ruling(31, "Drafted by the session; the human rules as Security.")})
    assert done.returncode == 1 and "pr2-security.md" in done.stdout and "not ruled" in done.stdout


def test_a_ruling_that_says_both_fails(tmp_path):
    done = run(tmp_path, {"pr2.md": ruling(31, "Drafted by the session.\n\nRuled by andaro74 as Product.")})
    assert done.returncode == 1 and "still says 'Drafted'" in done.stdout


def test_no_ruling_for_the_pr_still_fails_as_before(tmp_path):
    done = run(tmp_path, {"pr1.md": ruling(30, "Ruled by andaro74 as Product.")})
    assert done.returncode == 1 and "no file under milestones" in done.stdout
