"""The workflows that hold an App's key (SPEC/07 §6; milestones/M07/rulings/pr2-security.md items 4 to 6).

What the ruling asks of the files, read from the files: each key is read by one job per workflow, in
its own environment; that job runs `main`'s code and checks out no other repository; the grant is read
back before anything else uses the key; an input never reaches a shell by interpolation; and no key is
in a workflow that checks out a pull request's code. A test of the YAML, not of GitHub: whether an
environment refuses a branch is read from GitHub's own record (seed S0's second attempt).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
KEYS = {"PLATFORM_APP_PRIVATE_KEY": "platform-app", "UPGRADES_APP_PRIVATE_KEY": "platform-upgrades",
        "OBSERVER_APP_PRIVATE_KEY": "platform-observer"}  # fmt: skip
APP_OF = {"platform-app": "agentkeel-platform", "platform-upgrades": "agentkeel-upgrades", "platform-observer": "agentkeel-observer"}
KEYED = {"platform-check.yml": {"post": "platform-app"}, "platform-upgrade.yml": {"open": "platform-upgrades"},
         "model-watch.yml": {"open": "platform-upgrades"}, "observe.yml": {"observe": "platform-observer"},
         "deploy.yml": {"retire-open": "platform-upgrades"}}  # fmt: skip


def load(name: str) -> dict[str, Any]:
    return yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))


def triggers(workflow: dict[str, Any]) -> dict[str, Any]:
    return workflow.get("on") or workflow.get(True)  # YAML reads a bare `on` as true


def keyed_jobs() -> list[tuple[str, str, str, dict[str, Any]]]:
    return [(name, job, environment, load(name)["jobs"][job]) for name, jobs in KEYED.items() for job, environment in jobs.items()]


def secrets_in(value: Any) -> set[str]:
    return set(re.findall(r"secrets\.([A-Z_]+)", str(value)))


def test_every_job_that_names_an_environment_is_one_the_ruling_names_and_no_other():
    found = {name: {job: body["environment"] for job, body in load(name)["jobs"].items() if "environment" in body}
             for name in sorted(p.name for p in WORKFLOWS.glob("*.yml"))}  # fmt: skip
    assert {name: jobs for name, jobs in found.items() if jobs} == KEYED


def test_each_key_is_read_only_in_its_own_environment_and_evals_holds_none():
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for job, body in load(path.name)["jobs"].items():
            for secret in secrets_in(body) & set(KEYS):
                assert body.get("environment") == KEYS[secret], f"{path.name} {job} reads {secret} outside {KEYS[secret]}"
    assert not secrets_in(load("evals.yml")) & set(KEYS)  # it checks out pull-request code
    assert not secrets_in(load("gates.yml")) and not secrets_in(load("cold-review-ruling.yml")) & set(KEYS)


@pytest.mark.parametrize("name, job, environment, body", keyed_jobs(), ids=lambda v: v if isinstance(v, str) else "")
def test_a_keyed_job_runs_mains_code_on_data_and_reads_the_grant_first(name, job, environment, body):
    steps = body["steps"]
    checkouts = [s for s in steps if str(s.get("uses", "")).startswith("actions/checkout@")]
    # One checkout: this repository, at the ref the run was started for, which the environment holds to main.
    assert len(checkouts) == 1 and not {"repository", "ref"} & set(checkouts[0].get("with") or {}), (name, job)
    assert (checkouts[0].get("with") or {}).get("persist-credentials") is False
    keyed = [s for s in steps if secrets_in(s)]
    assert keyed, (name, job)
    first = keyed[0]
    assert f"scripts/platform_check.py grant --app {APP_OF[environment]} " in first["run"], (name, job)
    for step in keyed:  # the key reaches a step's environment, never a command line, and only agentkeel's scripts
        assert secrets_in(step.get("run")) == set() and set(secrets_in(step["env"])) == {k for k, e in KEYS.items() if e == environment}
        assert re.match(r"\s*(mkdir -p \S+\s+)?uv run python scripts/\w+\.py ", step["run"]), step["run"]
    # No third-party action is handed the key, and no step after the first use installs anything new.
    assert all("uses" not in s for s in keyed)
    assert body.get("permissions", {}).get("contents") == "read" and "write" not in str(
        {k: v for k, v in body["permissions"].items() if k != "id-token"})  # fmt: skip


def test_a_keyed_job_takes_the_earlier_jobs_output_as_an_artifact_never_a_checkout():
    for name, job, _environment, body in keyed_jobs():
        uses = [str(s.get("uses", "")).split("@")[0] for s in body["steps"]]
        if name == "observe.yml":
            assert "actions/download-artifact" not in uses  # one job: it reads GitHub's API, and nothing from a pull request
            continue
        assert "actions/download-artifact" in uses, (name, job)


def test_no_input_or_matrix_value_is_interpolated_into_a_keyed_jobs_script():
    for name, job, _environment, body in keyed_jobs():
        for step in body["steps"]:
            assert "${{" not in str(step.get("run", "")), f"{name} {job}: {step.get('name')}"
    # And the two dispatch inputs reach their scripts through env.
    post = load("platform-check.yml")["jobs"]["post"]
    relax = next(s for s in post["steps"] if "relax" in str(s.get("run", "")))
    assert relax["env"]["RELAX_SEED"] == "${{ inputs.relax_seed }}" and '--agent "$RELAX_SEED"' in relax["run"]
    assert relax["if"] == "github.event_name == 'workflow_dispatch' && inputs.relax_seed != ''"
    plan = next(s for s in load("deploy.yml")["jobs"]["retire-plan"]["steps"] if s.get("id") == "plan")
    assert plan["env"]["RETIRE"] == "${{ inputs.retire }}" and '--name "$RETIRE"' in plan["run"]


def test_the_keyed_workflows_run_from_a_schedule_or_a_dispatch_and_never_from_a_pull_request():
    for name in ("platform-check.yml", "platform-upgrade.yml", "model-watch.yml", "observe.yml"):
        on = triggers(load(name))
        assert set(on) == {"schedule", "workflow_dispatch"}, name
        assert load(name)["permissions"] == {}
    assert triggers(load("platform-upgrade.yml"))["schedule"] == [{"cron": "*/15 * * * *"}]  # arrive_max_seconds: one period and an hour
    assert "pull_request" not in triggers(load("deploy.yml")) and "pull_request_target" not in str(
        [triggers(load(p.name)) for p in WORKFLOWS.glob("*.yml")])  # fmt: skip


def test_the_jobs_that_read_an_agent_repository_hold_no_secret():
    for name, job in (("platform-upgrade.yml", "plan"), ("platform-check.yml", "evaluate"), ("platform-check.yml", "find"),
                      ("deploy.yml", "retire-plan"), ("deploy.yml", "sign-agent")):  # fmt: skip
        body = load(name)["jobs"][job]
        assert not secrets_in(body) and "environment" not in body, (name, job)
    read = load("model-watch.yml")["jobs"]["read"]
    assert not secrets_in(read) and "environment" not in read  # Bedrock's lifecycle, as a role that may read it and no more


INVOCATION = "One invocation of the retired runtime; anything but ResourceNotFoundException stops here"
SAME = "The retired head's manifest is the deployed one's, but for rollout"


def test_deploy_agent_reads_nothing_of_sign_agents_from_outside_the_one_folder():
    """Cold review N2 on M07 PR 3: the layout test read only paths under the staged folder, so a step that
    still read the old `$RUNNER_TEMP/image.tar` would not have been seen."""
    import re

    steps = load("deploy.yml")["jobs"]["deploy-agent"]["steps"]
    read = [path for step in steps for path in re.findall(r"\$RUNNER_TEMP/[A-Za-z0-9_./$-]+", str(step.get("run", "")))]
    signed = [path for path in read if path.endswith((".tar", ".cosign.json"))]
    assert signed and all(path.startswith("$RUNNER_TEMP/signed/") for path in signed), signed


def test_a_retirement_is_held_to_the_deployed_manifest_before_the_registry_or_the_stack_is_touched():
    """rulings/pr2-security.md item 13i: a retirement is a stack update from a head nobody signed."""
    steps = load("deploy.yml")["jobs"]["retire-agent"]["steps"]
    names = [s.get("name") or s.get("uses", "").split("@")[0] for s in steps]
    held = names.index(SAME)
    assert names.index("aws-actions/configure-aws-credentials") < held  # the registry is read as the deploy role
    assert held < names.index("Keep the runtime's ARN, before it is removed") \
        < names.index("Update agentkeel-<name> to the stack without its runtime")
    step = steps[held]
    assert "if" not in step  # never skipped
    assert "retire_agent.py same" in step["run"] and '--retired "agents/$NAME/manifest.yaml"' in step["run"]
    assert step["env"] == {"GITHUB_TOKEN": "${{ github.token }}"}  # no App key, no other secret


def test_the_table_panel_2_reads_is_written_through_the_shared_reader_of_envelopes():
    """Cold review B1 on M07 PR 2: the archive job read each envelope with jq, a second reader (P5)."""
    jobs = load("evals.yml")["jobs"]
    assert "agentkeel-envelopes" not in str(jobs["archive"]) and "ROW_PUT" not in str(jobs["archive"])
    rows = jobs["envelope-rows"]
    assert "github.event_name == 'push'" in rows["if"] and "refs/heads/main" in rows["if"]
    runs = [s["run"] for s in rows["steps"] if "run" in s]
    assert runs[-1].startswith("uv run python scripts/envelope_rows.py --history evals/history")
    assert "jq" not in str(rows) and not secrets_in(rows) and "environment" not in rows


def test_refagents_own_deploy_jobs_are_as_m06_left_them_and_a_retirement_deploys_no_image():
    deploy = load("deploy.yml")["jobs"]
    assert deploy["sign"]["if"] == "github.event_name == 'push'" and deploy["deploy"]["needs"] == "sign"
    retire = deploy["retire-agent"]
    said = str(retire)
    assert retire["needs"] == "find-agents" and "docker" not in said and "cosign" not in said and "bundle.pack" not in said
    assert 'test "$NAME" != "refagent"' in said and "AWS::BedrockAgentCore::Runtime" in said
    names = [s.get("name") for s in retire["steps"] if s.get("name")]
    assert names.index("Keep the runtime's ARN, before it is removed") < names.index("Update agentkeel-<name> to the stack without its runtime") \
        < names.index(INVOCATION) < names.index("Put the retirement in the security account, once") \
        < names.index("retired_at on the agent's row, which stays")  # fmt: skip
    # platform-architect B1 on M07 PR 2: the record and retired_at only after an invocation that says the
    # runtime is gone. The step fails on the script's exit code, and no later step runs on a failure.
    invocation = next(s for s in retire["steps"] if s.get("name") == INVOCATION)
    assert 'if [ "$code" != "0" ]; then' in invocation["run"] and "exit 1" in invocation["run"]
    assert invocation["run"].index("exit 1") < invocation["run"].index("retire_agent.py record")
    after = retire["steps"][retire["steps"].index(invocation) + 1:]
    assert all("always()" not in str(s.get("if", "")) for s in after if "upload-artifact" not in str(s.get("uses", "")))
    agent = [s.get("name") for s in deploy["deploy-agent"]["steps"] if s.get("name")]
    assert agent.index("Put the signed bundle in the security account, once") < agent.index("Put the answer record in the security account, once") \
        < agent.index("The agent's row in the registry")  # fmt: skip


def test_the_observer_stores_once_and_holds_the_key_in_the_step_that_uses_it():
    steps = load("observe.yml")["jobs"]["observe"]["steps"]
    aws = next(i for i, s in enumerate(steps) if str(s.get("uses", "")).startswith("aws-actions/configure-aws-credentials@"))
    keyed = [i for i, s in enumerate(steps) if secrets_in(s)]
    assert max(keyed) < aws  # the key is used, then the AWS credentials arrive: never both in one step
    put = steps[-1]["run"]
    assert "--if-none-match '*'" in put and 'key="observations/$GITHUB_RUN_ID.json"' in put and not secrets_in(steps[-1])


def test_evals_hands_build_the_observation_and_the_stored_one():
    evals = load("evals.yml")["jobs"]["evals"]["steps"]
    make = next(s for s in evals if str(s.get("run", "")).startswith("make evals "))
    assert 'UPGRADE_OBS="$RUNNER_TEMP/upgrade.json"' in make["run"] and 'APP_OBS="$RUNNER_TEMP/app-observation.json"' in make["run"]
    names = [s.get("name") for s in evals]
    assert names.index("Look up claim 7's records and the stored observation in the security account") \
        < names.index("Look up claim 7's pull requests, runtimes and panel 2") < names.index("make evals")  # fmt: skip
    panel2 = next(s for s in evals if s.get("name") == "Read panel 2 as the workspace's viewer")
    assert panel2["continue-on-error"] is True and "infra/grafana/panel2.json" in panel2["run"]


# --- M07 PR 3: the artifact sign-agent hands to deploy-agent (run 37023118799) -----------------------


def test_deploy_agent_reads_the_signed_files_where_sign_agent_put_them():
    """The first deploy of an agent from the template to reach deploy-agent failed at its first read
    (owner-check, run 37023118799): sign-agent uploaded three paths under two roots, GitHub rooted the
    artifact at their common parent, and nothing was at the paths deploy-agent reads. One folder is
    uploaded whole now; every path deploy-agent reads under it is one the staging step writes."""
    jobs = load("deploy.yml")["jobs"]
    sign, deploy = jobs["sign-agent"]["steps"], jobs["deploy-agent"]["steps"]
    upload = next(s for s in sign if str(s.get("uses", "")).startswith("actions/upload-artifact@"))
    download = next(s for s in deploy if str(s.get("uses", "")).startswith("actions/download-artifact@"))
    assert upload["with"]["path"] == "${{ runner.temp }}/signed" == download["with"]["path"]  # one root, not three paths
    assert upload["with"]["name"] == download["with"]["name"]
    stage = next(s for s in sign if s.get("name") == "Stage what deploy-agent reads, under one folder")
    assert sign.index(stage) == sign.index(upload) - 1
    written = {"agents/$NAME/bundle.cosign.json", "agents/$NAME/dist/bundle.tar", "image.tar"}
    for path in written:
        assert f"$RUNNER_TEMP/signed/{path}" in stage["run"] or f"$RUNNER_TEMP/signed/{path.rsplit('/', 1)[0]}/" in stage["run"], path
    read = set()
    for step in deploy:
        read |= set(re.findall(r"\$RUNNER_TEMP/signed/([A-Za-z0-9_./$-]+)", str(step.get("run", ""))))
    read = {p.removesuffix("$") for p in read}  # the bundle put names its two files through a shell variable
    assert read and all(any(w.startswith(p) or p == w for w in written) for p in read), read
