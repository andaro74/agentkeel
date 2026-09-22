"""`GovernedAgent`, and the checks over the whole synthesised stack (Security seat).

An agent on this platform is an instance of this construct (SPEC/01 §2),
and that is checked at synth, in a stack that installs these checks, and no
further (BLOCK D). The account holds less than that. There is no service
control policy. Since M01 PR 3, `agentkeel-cfn-exec` may call
`CreateAgentRuntime`, held by IAM to the platform VPC's subnets: that limits
where a runtime is made, not who built it. Binding an author who never
installs these checks is M05's (SPEC/00 §2, §12).

Three of M01's seeded cases are read here, and each is read over the whole
stack, not inside the construct:

- **S3** an egress rule the manifest does not list, added through the
  construct's security group or as a separate resource naming it;
- **S5** a role handed to the construct with no permission boundary, or a
  different one from the bootstrap stack's;
- **S8** an AgentCore runtime made with no `GovernedAgent`.

A check inside the construct sees only its own children, and S3's second
form and S8 are both outside them. So the checks are a validation on the
stack (`Stack.node.add_validation`), which CDK runs after every aspect —
after `PermissionsBoundary.of(stack).apply(...)` has written the boundary
onto the roles it covers. `GovernedAgent` installs it; a stack with no
agent in it installs it by calling `refuse_outside_construct(stack)`.

Where the numbers come from. Nothing here is read from CDK context: the
boundary ARN, the VPC, the subnets, the endpoint security groups and the
gateway-endpoint prefix lists are all read from Security-owned SSM
parameters (SPEC/01 §6). A parameter the Security seat has not written is
a deploy that fails, not a default that is guessed.

Gateway and Identity are **props, and nothing else** (ruling SCOPE and
finding 17, `feasibility.md` §2.6). They are declared here so the seam is
visible and so a caller cannot invent its own; passing either is refused
at synth. Identity's claim is M05's, Gateway's is M02's and M07's.

    python -m infra.construct.app        # refagent's stack, the one deploy.yml deploys
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

__all__ = ["GovernedAgent", "refuse_outside_construct", "synth_refusal"]


def synth_refusal(app_path: Path | str) -> str | None:
    """Synthesise a CDK app in a subprocess. The refusal, or None if it synthesised.

    A seed is a whole app: `cdk.App()`, the thing that must be refused, and
    `app.synth()`. Running it in this process would leave CDK's tree behind
    for the next test, so each one gets its own interpreter.
    """
    done = subprocess.run(
        [sys.executable, str(app_path)],
        cwd=ROOT, capture_output=True, text=True, check=False,
        env={**_env(), "PYTHONPATH": str(ROOT)},
    )  # fmt: skip
    if done.returncode == 0:
        return None
    return (done.stderr.strip() or done.stdout.strip() or f"synth exited {done.returncode}")


def _env() -> dict[str, str]:
    import os

    # cdk.out per app, under the app's own name, so two seeds never share one.
    return {k: v for k, v in os.environ.items() if k != "CDK_OUTDIR"}


def __getattr__(name: str):
    """`GovernedAgent` and `refuse_outside_construct` need aws-cdk-lib; `synth_refusal` does not."""
    if name in ("GovernedAgent", "refuse_outside_construct"):
        from infra.construct.governed_agent import (
            GovernedAgent,
            refuse_outside_construct,
        )

        return {"GovernedAgent": GovernedAgent, "refuse_outside_construct": refuse_outside_construct}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
