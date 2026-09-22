"""The runtime image is arm64, and the deploy says so in three places (M02 PR 2).

AgentCore Runtime runs arm64 images only. deploy.yml built refagent's image
with `docker build` on an x86 runner, so every image it pushed was amd64.
CreateAgentRuntime accepted the first one (run 35734541276) and the runtime
never started: its log said "parent snapshot ... does not exist" every few
seconds, and the load check hung until the job's limit. UpdateAgentRuntime
refused the second one outright: "Architecture incompatible ... Supported
platforms: [arm64]" (the rerun, 14:23 UTC). Nothing in the tree had said
which architecture the runtime needs, so nothing could have read it.

Three readers, so it cannot happen quietly again:
- the Dockerfile pins the platform in FROM, so the image's architecture is
  a property of the file and not of whichever machine built it;
- the deploy job runs on an arm64 runner, so the build is native;
- the build step refuses to push, and the reuse branch refuses to reuse,
  an image whose architecture is not arm64, naming the digest.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / ".github" / "workflows" / "deploy.yml"
DOCKERFILE = ROOT / "agents" / "refagent" / "Dockerfile"


def test_the_dockerfile_pins_the_platform_the_runtime_supports():
    froms = [line for line in DOCKERFILE.read_text(encoding="utf-8").splitlines() if line.startswith("FROM ")]
    assert froms and all("--platform=linux/arm64" in line for line in froms), froms


def test_the_deploy_job_builds_on_an_arm64_runner():
    workflow = yaml.safe_load(DEPLOY.read_text(encoding="utf-8"))
    runs_on = workflow["jobs"]["deploy"]["runs-on"]
    assert "arm" in str(runs_on), f"deploy runs on {runs_on!r}; docker build there is not arm64"


def test_the_build_step_reads_the_architecture_before_it_pushes_or_reuses():
    workflow = yaml.safe_load(DEPLOY.read_text(encoding="utf-8"))
    build = next(s for s in workflow["jobs"]["deploy"]["steps"] if s.get("id") == "image")
    script = build["run"]
    # One reader, called from both branches: the fresh build, and the image already under this tag.
    assert "{{.Architecture}}" in script and '"arm64"' in script
    assert script.count('refuse_unless_arm64 "') >= 2, "both the push and the reuse branch read the architecture"
