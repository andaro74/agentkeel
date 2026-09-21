"""The eval job can still fail on the gate's verdict (cold review B1).

`evals` is a required status check (`infra/ruleset/main.json`), and the job's
only mechanism for failing on a RED or REJECTED envelope is `make evals`
exiting non-zero: the Makefile runs `verdict.gate` and exits with its code,
and GNU make exits 2. Nothing else in the job reads the verdict.

The step pipes through `tee` so a later step can report which refagent
answered. GitHub's default shell for a `run:` is `bash -e {0}`, which does
**not** set pipefail; only an explicit `shell: bash` adds `-o pipefail`.
Without it the step's status is tee's, which is 0:

    $ bash -ec 'false | tee /dev/null'; echo $?
    0
    $ bash -eo pipefail -c 'false | tee /dev/null'; echo $?
    1

So between 442484f and its repair a RED envelope reported a green required
check. These tests are what stops the pipe being added back without the
shell, and what stops the `record` job quietly recording an envelope the
gate rejected.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "evals.yml"


@pytest.fixture(scope="module")
def workflow() -> dict[str, Any]:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def steps(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    return [step for job in workflow["jobs"].values() for step in job.get("steps", [])]


def measuring_steps(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    return [step for step in steps(workflow) if "make evals" in str(step.get("run", ""))]


def test_there_is_exactly_one_step_that_measures(workflow):
    """If a second appeared, the rule below would have to cover it too."""
    assert len(measuring_steps(workflow)) == 1


def test_the_step_that_measures_declares_shell_bash(workflow):
    """Without it, `bash -e {0}` runs the step and the pipe swallows make's exit."""
    step = measuring_steps(workflow)[0]
    assert step.get("shell") == "bash", (
        "the step runs `make evals` through a pipe; without `shell: bash` there is no "
        "pipefail and the gate's non-zero exit is reported as success"
    )


def test_a_pipe_without_pipefail_really_does_swallow_the_exit():
    """The claim above, run rather than asserted from memory."""
    import subprocess

    without = subprocess.run(["bash", "-ec", "false | tee /dev/null"], check=False)
    with_it = subprocess.run(["bash", "-eo", "pipefail", "-c", "false | tee /dev/null"], check=False)
    assert without.returncode == 0, "bash -e alone would have caught it; this test is obsolete"
    assert with_it.returncode == 1


def test_the_record_job_still_refuses_an_envelope_the_gate_rejected(workflow):
    """`gate_exit` 2 is REJECTED: not evidence, and never committed (M01 item 9)."""
    condition = " ".join(workflow["jobs"]["record"]["if"].split())
    assert "needs.evals.outputs.gate_exit" in condition, "the record job no longer reads the gate's exit"
    assert "gate_exit == '0'" in condition and "gate_exit == '1'" in condition, (
        "the record job must commit only for GREEN (0) and RED/UNMEASURED (1); "
        "a REJECTED envelope (2) is not evidence"
    )
