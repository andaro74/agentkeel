"""The registry's one writer: deploy.yml on main, as the deploy role (SPEC/06 section 2, section 6, item 9).

    python scripts/registry.py deployed --name NAME --commit SHA             # exit 0 if that commit is deployed
    python scripts/registry.py claim --name NAME --repository ORG/REPO --repository-id ID   # before the stack
    python scripts/registry.py write --name NAME --repository ORG/REPO --repository-id ID \
        --commit SHA --run-id RUN [--answer-put first|stood]                  # after the agent answered
    python scripts/registry.py retiring --name NAME --repository-id ID --arn ARN   # before the runtime is removed
    python scripts/registry.py retire --name NAME --repository-id ID --commit SHA --run-id RUN   # after it is gone

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

From M07 PR 2 (SPEC/07 section 6):

- `write --answer-put stood` says the answer record in the audit bucket for
  this commit is an earlier run's: the put was refused as already there (a
  412), so this run's `deploy_run_id` is not the run that wrote it. Until
  then the row named a run against a record that run did not write (re-read
  of 52ebd57 at M07 PR 1). `first` is this run's own put.
- `retiring` keeps the runtime's ARN on the row before the stack update
  removes it, so the one invocation after the deletion, and a rerun of a
  retirement that failed halfway, still know which ARN to ask.
- `retire` writes `retired_at` on the row, which stays: a retired agent is
  listed as retired, not forgotten. Both hold the row to its repository id,
  and neither will touch `refagent`. The table is not write-once; the
  retirement is also put once in the audit bucket (`scripts/retire_agent.py`).
- A retirement is one-way: `claim` exits 3 for a name whose row says
  `retired_at`, before the stack is touched, and `write` carries the same
  condition, so a later head that drops `rollout: retired` is not deployed
  and cannot replace the row (security-reviewer 8 on M07 PR 2: `write` puts
  a whole item, and would have dropped `retired_at`).
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
    item = dynamodb.get_item(TableName=TABLE, Key={"name": {"S": name}}, ConsistentRead=True).get("Item") or {}
    held = (item.get("repository_id") or {}).get("S")
    if held != repository_id:
        return 3, f"{name} is held by repository {held}, not {repository_id}: refused before the stack is touched"
    if "retired_at" in item:
        return 3, f"{name} was retired at {item['retired_at']['S']}: a retirement is one-way, and nothing is deployed under it"
    return 0, f"{name}: already this repository's"


def write(dynamodb: Any, name: str, repository: str, repository_id: str, commit: str, run_id: str,
          answer_put: str | None = None) -> tuple[int, str]:  # fmt: skip
    from botocore.exceptions import ClientError

    now = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    said = {} if answer_put is None else {"answer_put": {"S": answer_put}}
    try:
        dynamodb.put_item(
            TableName=TABLE,
            Item={"name": {"S": name}, "repository": {"S": repository}, "repository_id": {"S": repository_id},
                  "commit_sha": {"S": commit}, "deploy_run_id": {"S": run_id}, "deployed_at": {"S": now}, **said},
            ConditionExpression="attribute_not_exists(#n) OR (repository_id = :id AND attribute_not_exists(retired_at))",
            ExpressionAttributeNames={"#n": "name"},
            ExpressionAttributeValues={":id": {"S": repository_id}},
        )  # fmt: skip
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return 3, f"{name} was taken by another repository, or retired, between the claim and the write"
        raise
    return 0, f"{name}: {repository}@{commit[:12]}, run {run_id}, {now}" + (f", answer record {answer_put}" if answer_put else "")


PLATFORM_AGENT = "refagent"  # never retired by this path (SPEC/07 section 6)


def _own_row(dynamodb: Any, name: str, repository_id: str) -> tuple[dict[str, Any] | None, str]:
    """The agent's row when it is this repository's and may be retired; else None and why."""
    if name == PLATFORM_AGENT:
        return None, f"{PLATFORM_AGENT} is the platform's own agent: never retired by this path"
    item = dynamodb.get_item(TableName=TABLE, Key={"name": {"S": name}}, ConsistentRead=True).get("Item")
    if item is None:
        return None, f"{name}: no registry row: nothing was deployed under this name, so there is nothing to retire"
    if item["repository_id"]["S"] != repository_id:
        return None, f"{name} is held by repository {item['repository_id']['S']}, not {repository_id}: refused"
    return item, ""


def _put_own(dynamodb: Any, item: dict[str, Any], repository_id: str) -> None:
    dynamodb.put_item(TableName=TABLE, Item=item, ConditionExpression="repository_id = :id",
                      ExpressionAttributeValues={":id": {"S": repository_id}})  # fmt: skip


def retiring(dynamodb: Any, name: str, repository_id: str, arn: str | None) -> tuple[int, str]:
    """Keep the runtime's ARN on the row before it is removed; print the ARN the row holds.

    Exit 0 with the ARN when there is a runtime to retire; 4 when the row already says `retired_at`
    (nothing to do); 3 when the row is not this repository's, is refagent's, or is not there. A rerun
    after a failure keeps the ARN the first run wrote."""
    item, why = _own_row(dynamodb, name, repository_id)
    if item is None:
        return 3, why
    if "retired_at" in item:
        return 4, f"{name}: already retired at {item['retired_at']['S']}"
    held = (item.get("retiring_arn") or {}).get("S")
    if held:
        return 0, held
    if not arn:
        return 3, f"{name}: the stack gives no RuntimeArn and the row holds none: the runtime's ARN is not known"
    _put_own(dynamodb, {**item, "retiring_arn": {"S": arn}}, repository_id)
    return 0, arn


def retire(dynamodb: Any, name: str, repository_id: str, commit: str, run_id: str) -> tuple[int, str]:
    """`retired_at` on the row, with the commit that said `rollout: retired` and the run that retired it."""
    item, why = _own_row(dynamodb, name, repository_id)
    if item is None:
        return 3, why
    if "retired_at" in item:
        return 0, f"{name}: already retired at {item['retired_at']['S']}"
    now = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    _put_own(dynamodb, {**item, "retired_at": {"S": now}, "retired_commit": {"S": commit},
                        "retire_run_id": {"S": run_id}}, repository_id)  # fmt: skip
    return 0, f"{name}: retired at {now}, commit {commit[:12]}, run {run_id}"


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
    two.add_argument("--answer-put", choices=("first", "stood"))
    three = sub.add_parser("retiring")
    for flag in ("--name", "--repository-id"):
        three.add_argument(flag, required=True)
    three.add_argument("--arn", default="")
    four = sub.add_parser("retire")
    for flag in ("--name", "--repository-id", "--commit", "--run-id"):
        four.add_argument(flag, required=True)
    args = parser.parse_args(argv)
    if args.what == "retiring":
        code, said = retiring(client(), args.name, args.repository_id, args.arn or None)
        print(said, file=sys.stderr if code else sys.stdout)  # on 0, stdout is the ARN and nothing else
        return code
    if args.what == "retire":
        code, said = retire(client(), args.name, args.repository_id, args.commit, args.run_id)
        print(said, file=sys.stderr if code else sys.stdout)
        return code
    if args.what == "deployed":
        code, said = deployed(client(), args.name, args.commit)
        print(said)
        return code
    if args.what == "claim":
        code, said = claim(client(), args.name, args.repository, args.repository_id)
    else:
        code, said = write(client(), args.name, args.repository, args.repository_id, args.commit, args.run_id,
                           args.answer_put)  # fmt: skip
    print(said, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
