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

So between 442484f and its repair a RED envelope **would have** reported a
green required check. No RED run occurred in that window, so the protection
was gone and no result was wrong.

`shell: bash` is not the only way to swallow the exit, and the first version
of this file asserted only that. `continue-on-error: true` on the step, or
`|| true` on the end of the command, each restores the hole and each left all
four tests green. Both are asserted now. The job's other guard —
`evals.yml`'s "Gate the recorded envelope" step — runs only on the
already-measured path, so it does not cover this one.
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


def job_of(workflow: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
    """The job a step belongs to. `continue-on-error` at that level covers every step."""
    for job in workflow["jobs"].values():
        if any(one is step for one in job.get("steps", [])):
            return job
    raise AssertionError("the step belongs to no job")


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


def test_neither_the_step_nor_its_job_may_fail_quietly(workflow):
    """`continue-on-error` restores B1's hole with `shell: bash` still set.

    The step would still exit non-zero and the job would still be green, and
    nothing else on this path reads the verdict: the only other `exit 1` is
    keyed to `steps.pytest.outcome`, and `gate_exit` is read solely by the
    `record` job's `if:`, where a bad value skips a commit and fails nothing.

    **Both levels.** The first version of this test read the step only, and a
    job-level `continue-on-error: true` passed all six tests while fully
    restoring the hole — GitHub applies it to every step in the job. Caught
    by injection, not by reading.
    """
    step = measuring_steps(workflow)[0]
    assert step.get("continue-on-error") in (None, False), (
        "a step that may fail quietly cannot be the thing that fails on a RED gate"
    )
    job = job_of(workflow, step)
    assert job.get("continue-on-error") in (None, False), (
        "the job carries continue-on-error, so no step in it can fail the workflow"
    )


def test_the_measuring_command_does_not_discard_its_own_status(workflow):
    """The other way round the guard: `make evals ... || true`.

    `measuring_steps` matches on the substring `make evals`, so a trailing
    `|| true` or `; true` would keep every other test green while making the
    step's exit status unconditionally 0.
    """
    run = measuring_steps(workflow)[0]["run"]
    for swallow in ("|| true", "|| :", "; true", "; :", "|| exit 0"):
        assert swallow not in run, f"`{swallow}` discards the exit status the gate sets"


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
