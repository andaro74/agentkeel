"""Call every model the manifest pins, and say which ones this account may use.

    python scripts/check_model_access.py                 # every pinned role
    python scripts/check_model_access.py --role baseline --role agent

`list-foundation-models` reporting `modelLifecycle: ACTIVE` says the model
exists in the region. It does not say this account may call it. The two
were read as one when refagent's model was pinned, and the difference cost
a CI run: fifteen goldens, fifteen `AccessDeniedException` (M01 PR 2, run
35529132275). The only thing that settles it is a call.

So this makes one, per pinned model, with `maxTokens: 1`. It spends — a
few tokens per model — which is why it is a script the Threshold Owner
runs when pinning, and not a check in `make validate`. It writes nothing
and rules nothing.

Exit 0 when every model asked about answered, 1 otherwise.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import boto3
import yaml
from botocore.exceptions import BotoCoreError, ClientError

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "agents" / "refagent" / "manifest.yaml"
PROBE = [{"role": "user", "content": [{"text": "hi"}]}]


def pinned(manifest: dict[str, Any]) -> dict[str, str]:
    """role -> the inference profile to call, from the manifest's own fields."""
    roles: dict[str, str] = {"agent": manifest["model"]["profile"]}
    for role, pin in (manifest.get("pinned_roles") or {}).items():
        if isinstance(pin, dict) and pin.get("profile"):
            roles[role] = pin["profile"]
        elif isinstance(pin, list):
            for number, candidate in enumerate(pin, 1):
                if candidate.get("profile"):
                    roles[f"{role}[{number}]"] = candidate["profile"]
                else:  # ON_DEMAND only: the model id is what is called
                    roles[f"{role}[{number}]"] = candidate["id"]
    return roles


def answers(client: Any, profile: str) -> str | None:
    """None when the model answered, else the reason it did not."""
    try:
        client.converse(modelId=profile, messages=PROBE, inferenceConfig={"maxTokens": 1})
    except (BotoCoreError, ClientError) as exc:
        return f"{type(exc).__name__}: {str(exc).split(': ', 1)[-1]}"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--role", action="append", help="only these roles (default: all)")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    args = parser.parse_args(argv)

    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    roles = pinned(manifest)
    if args.role:
        roles = {role: profile for role, profile in roles.items() if role.split("[")[0] in args.role}

    client = boto3.client("bedrock-runtime", region_name=manifest["model"]["region"])
    refused = 0
    for role, profile in roles.items():
        reason = answers(client, profile)
        refused += bool(reason)
        print(f"{'REFUSED' if reason else 'ok     '} {role:<26} {profile}")
        if reason:
            print(f"        {reason[:160]}")
    print(f"{len(roles) - refused} of {len(roles)} pinned models answered in {manifest['model']['region']}")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
