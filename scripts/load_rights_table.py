"""Load `data/rights_table.json` into refagent's DynamoDB table (SPEC/01 §6).

    python scripts/load_rights_table.py --table agentkeel-refagent-rights

The rights table is the truth (SPEC/00 §9), and the file is where the Data
Owner keeps it. The DynamoDB table is a copy for the deployed runtime to
read; this script is what makes the copy, run after a deploy.

It writes rows and nothing else: no deletes, no schema changes. A row the
file no longer holds stays in the table until somebody removes it on
purpose, and this says how many that is.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import boto3

ROOT = Path(__file__).resolve().parents[1]
REGION = "us-west-2"


def attribute(value: Any) -> dict[str, Any]:
    if value is None:
        return {"NULL": True}
    if isinstance(value, bool):
        return {"BOOL": value}
    return {"S": str(value)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--table", required=True)
    parser.add_argument("--region", default=REGION)
    parser.add_argument("--rights", type=Path, default=ROOT / "data" / "rights_table.json")
    args = parser.parse_args(argv)

    rows = json.loads(args.rights.read_text(encoding="utf-8"))
    client = boto3.client("dynamodb", region_name=args.region)
    for row in rows:
        client.put_item(TableName=args.table, Item={k: attribute(v) for k, v in row.items()})
    in_table = client.describe_table(TableName=args.table)["Table"].get("ItemCount")
    print(f"wrote {len(rows)} rows from {args.rights.name} into {args.table} (table reported {in_table} before)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
