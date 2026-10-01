"""The registry's one writer: deploy.yml on main, as the deploy role (SPEC/06 section 2, section 6, item 9).

    python scripts/registry.py deployed --name NAME --commit SHA             # exit 0 if that commit is deployed
    python scripts/registry.py claim --name NAME --repository ORG/REPO --repository-id ID   # before the stack
    python scripts/registry.py write --name NAME --repository ORG/REPO --repository-id ID \
        --commit SHA --run-id RUN                                             # after the agent answered

One row per agent, keyed by `name`: the repository and its id, the commit
deployed, the deploy run, and the time the row was written (UTC, this
machine's clock in a GitHub runner, never the developer's). A name belongs
to the first repository deployed under it, by repository id, which a
rename does not change. `claim` **writes** the binding before the stack is
touched, on the condition that the name is new (a row with no commit yet,
`commit_sha` "none"), and exits 3 when another repository holds the name; so
a first deploy that fails after the stack is made still leaves the name its
repository's (security-reviewer F2 on M06 PR 2). `write` puts the row only on
the same condition, so two deploys racing cannot both take it. Panel 1 lists
the rows (`infra/grafana/`).
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from typing import Any

TABLE = "agentkeel-registry"
REGION = "us-west-2"


def client() -> Any:
    import boto3

    return boto3.client("dynamodb", region_name=REGION)


def holder(dynamodb: Any, name: str) -> str | None:
    item = dynamodb.get_item(TableName=TABLE, Key={"name": {"S": name}}, ConsistentRead=True).get("Item")
    return None if item is None else item["repository_id"]["S"]


def deployed(dynamodb: Any, name: str, commit: str) -> tuple[int, str]:
    """0 when the registry already holds `commit` for `name`, so the deploy has nothing to do; 1 otherwise."""
    item = dynamodb.get_item(TableName=TABLE, Key={"name": {"S": name}}, ConsistentRead=True).get("Item")
    held = None if item is None else item["commit_sha"]["S"]
    return (0, f"{name}@{commit[:12]} is deployed") if held == commit else (1, f"{name}: registry holds {held}")


def claim(dynamodb: Any, name: str, repository: str, repository_id: str) -> tuple[int, str]:
    from botocore.exceptions import ClientError

    try:
        dynamodb.put_item(
            TableName=TABLE,
            Item={"name": {"S": name}, "repository": {"S": repository}, "repository_id": {"S": repository_id},
                  "commit_sha": {"S": "none"}, "deploy_run_id": {"S": "none"}, "deployed_at": {"S": "none"}},
            ConditionExpression="attribute_not_exists(#n)",
            ExpressionAttributeNames={"#n": "name"},
        )  # fmt: skip
        return 0, f"{name}: claimed for {repository} ({repository_id})"
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") != "ConditionalCheckFailedException":
            raise
    held = holder(dynamodb, name)
    if held != repository_id:
        return 3, f"{name} is held by repository {held}, not {repository_id}: refused before the stack is touched"
    return 0, f"{name}: already this repository's"


def write(dynamodb: Any, name: str, repository: str, repository_id: str, commit: str, run_id: str) -> tuple[int, str]:
    from botocore.exceptions import ClientError

    now = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    try:
        dynamodb.put_item(
            TableName=TABLE,
            Item={"name": {"S": name}, "repository": {"S": repository}, "repository_id": {"S": repository_id},
                  "commit_sha": {"S": commit}, "deploy_run_id": {"S": run_id}, "deployed_at": {"S": now}},
            ConditionExpression="attribute_not_exists(#n) OR repository_id = :id",
            ExpressionAttributeNames={"#n": "name"},
            ExpressionAttributeValues={":id": {"S": repository_id}},
        )  # fmt: skip
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return 3, f"{name} was taken by another repository between the claim and the write"
        raise
    return 0, f"{name}: {repository}@{commit[:12]}, run {run_id}, {now}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="what", required=True)
    zero = sub.add_parser("deployed")
    zero.add_argument("--name", required=True)
    zero.add_argument("--commit", required=True)
    one = sub.add_parser("claim")
    one.add_argument("--name", required=True)
    one.add_argument("--repository", required=True)
    one.add_argument("--repository-id", required=True)
    two = sub.add_parser("write")
    for flag in ("--name", "--repository", "--repository-id", "--commit", "--run-id"):
        two.add_argument(flag, required=True)
    args = parser.parse_args(argv)
    if args.what == "deployed":
        code, said = deployed(client(), args.name, args.commit)
        print(said)
        return code
    if args.what == "claim":
        code, said = claim(client(), args.name, args.repository, args.repository_id)
    else:
        code, said = write(client(), args.name, args.repository, args.repository_id, args.commit, args.run_id)
    print(said, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
