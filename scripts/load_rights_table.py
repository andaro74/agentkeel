"""Load `data/rights_table.json` into refagent's DynamoDB table, and say which table it now holds (SPEC/01 §6).

    python scripts/load_rights_table.py --table agentkeel-refagent-rights

The rights table is the truth (SPEC/00 §9), and the file is where the Data
Owner keeps it. The DynamoDB table is a copy for the deployed runtime to
read; this script is what makes the copy, run after a deploy.

From M03 PR 2 (seed S1's reader, SPEC/03 §6) the copy is the file and
nothing else, and the table marker says so:

1. the marker (`/agentkeel/marker/refagent/rights-table-digest`) is set to
   `loading`, so a run that reads it meanwhile goes to the runner;
2. every row in the file is written;
3. every row the file no longer has is deleted (the deploy role may Scan
   and DeleteItem on the rights tables, never DeleteTable);
4. the table is scanned back, and the marker is set to the digest of what
   the scan read, and only if that equals the file's digest. Otherwise it
   stays `loading` and the script exits 1: the marker is a read of the
   table, not the deployer's claim (security-reviewer on e2839f2, NOTE 5).

A row deleted here is one key (the Data Owner's ruling on the file;
`milestones/M03/rulings/pr1.md` ruling 5), and `validate` still refuses a
golden whose row is gone.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import boto3

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import rights_table  # noqa: E402

REGION = "us-west-2"
MARKER = "/agentkeel/marker/refagent/rights-table-digest"
LOADING = "loading"


def attribute(value: Any) -> dict[str, Any]:
    if value is None:
        return {"NULL": True}
    if isinstance(value, bool):
        return {"BOOL": value}
    return {"S": str(value)}


def scan(client: Any, table: str) -> list[dict[str, Any]]:
    """Every row in the table, as stored values."""
    items, kwargs = [], {"TableName": table, "ConsistentRead": True}
    while True:
        page = client.scan(**kwargs)
        items += page.get("Items", [])
        if "LastEvaluatedKey" not in page:
            return [rights_table.from_item(item) for item in items]
        kwargs["ExclusiveStartKey"] = page["LastEvaluatedKey"]


def load(dynamodb: Any, ssm: Any, table: str, rows: list[dict[str, Any]]) -> tuple[int, str]:
    """(exit code, what happened). The marker is `loading` from the first write to the last read."""
    ssm.put_parameter(Name=MARKER, Value=LOADING, Type="String", Overwrite=True)
    for row in rows:
        dynamodb.put_item(TableName=table, Item={k: attribute(v) for k, v in row.items()})
    keep = {row[rights_table.KEY] for row in rows}
    gone = sorted(row[rights_table.KEY] for row in scan(dynamodb, table) if row[rights_table.KEY] not in keep)
    for key in gone:
        dynamodb.delete_item(TableName=table, Key={rights_table.KEY: {"S": key}})
    held, wanted = rights_table.digest(scan(dynamodb, table)), rights_table.digest(rows)
    if held != wanted:
        return 1, (f"the table holds {held[:12]}, the file is {wanted[:12]}: the marker stays {LOADING!r}, "
                   f"so every run is in the runner")  # fmt: skip
    ssm.put_parameter(Name=MARKER, Value=held, Type="String", Overwrite=True)
    return 0, f"wrote {len(rows)} rows, deleted {len(gone)} ({', '.join(gone) or 'none'}); marker {held[:12]}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--table", required=True)
    parser.add_argument("--region", default=REGION)
    parser.add_argument("--rights", type=Path, default=ROOT / "data" / "rights_table.json")
    args = parser.parse_args(argv)

    rows = json.loads(args.rights.read_text(encoding="utf-8"))
    code, said = load(boto3.client("dynamodb", region_name=args.region), boto3.client("ssm", region_name=args.region),
                      args.table, rows)  # fmt: skip
    print(f"{args.table}: {said}")
    return code


if __name__ == "__main__":
    sys.exit(main())
