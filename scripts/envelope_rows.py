"""The writer of panel 2's table: one row per envelope on main, each put once (SPEC/07 §2 "Panel 2", §6).

    python scripts/envelope_rows.py --history evals/history     # evals.yml's envelope-rows job, on main

A row is an envelope's commit, the verdict it stores and its mode. The
envelopes are read by `src/verdict/replay_history.rows`, the shared reader
of past ones; this script opens none (cold review B1 on M07 PR 2). The
table, `agentkeel-envelopes`, is a copy for a surface, not evidence:
`build.f7_4` compares what panel 2 shows with `evals/history/`.

A row that is there is left alone: each put carries the condition that the
commit is not in the table. That condition is this script's, not IAM's:
the role may `PutItem`, which could replace a row. Nothing here has written
a row until the table and the role are deployed (rulings/pr2-security.md
item 13d).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.verdict import replay_history  # noqa: E402

TABLE = "agentkeel-envelopes"
REGION = "us-west-2"


def held(dynamodb: Any) -> set[str]:
    """Every commit the table holds, each page of the scan."""
    commits: set[str] = set()
    more: dict[str, Any] = {}
    while True:
        page = dynamodb.scan(TableName=TABLE, ProjectionExpression="#c", ExpressionAttributeNames={"#c": "commit"}, **more)
        commits |= {item["commit"]["S"] for item in page.get("Items") or []}
        if not page.get("LastEvaluatedKey"):
            return commits
        more = {"ExclusiveStartKey": page["LastEvaluatedKey"]}


def put_rows(dynamodb: Any, history_dir: Path) -> list[str]:
    """Put each envelope's row that the table does not hold; the commits written, in order."""
    from botocore.exceptions import ClientError

    there = held(dynamodb)
    written = []
    for row in replay_history.rows(history_dir):
        if row["commit"] in there:
            continue
        try:
            dynamodb.put_item(TableName=TABLE, Item={name: {"S": value} for name, value in row.items()},
                              ConditionExpression="attribute_not_exists(#c)", ExpressionAttributeNames={"#c": "commit"})  # fmt: skip
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") != "ConditionalCheckFailedException":
                raise
            continue  # another run put it between the scan and here: it stands
        written.append(row["commit"])
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--history", required=True, type=Path)
    args = parser.parse_args(argv)
    import boto3

    written = put_rows(boto3.client("dynamodb", region_name=REGION), args.history)
    print(f"### Rows written to {TABLE}: {len(written)}")
    for commit in written:
        print(f"- {commit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
