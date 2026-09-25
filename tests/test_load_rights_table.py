"""scripts/load_rights_table.py and src/rights_table.py: the copy is the file, and the marker says so (M03 PR 2, S1).

No AWS: a dict stands for the table and a list for the marker's writes.
"""

from __future__ import annotations

import json

import pytest

from scripts import load_rights_table as loader
from src import rights_table
from src.verdict import ROOT

FILE = json.loads((ROOT / "data" / "rights_table.json").read_text(encoding="utf-8"))


class Table:
    """put_item, delete_item and scan over a dict keyed by table_row, in two pages."""

    def __init__(self, rows=()):
        self.items = {row["table_row"]: {k: loader.attribute(v) for k, v in row.items()} for row in rows}

    def put_item(self, TableName, Item):  # noqa: N803 - boto3's keywords
        self.items[Item["table_row"]["S"]] = Item

    def delete_item(self, TableName, Key):  # noqa: N803
        del self.items[Key["table_row"]["S"]]

    def scan(self, TableName, ConsistentRead, ExclusiveStartKey=None):  # noqa: N803
        keys = sorted(self.items)
        half = len(keys) // 2
        if ExclusiveStartKey is None:
            return {"Items": [self.items[k] for k in keys[:half]], "LastEvaluatedKey": {"at": half}}
        return {"Items": [self.items[k] for k in keys[half:]]}


class Marker:
    def __init__(self):
        self.written: list[str] = []

    def put_parameter(self, Name, Value, Type, Overwrite):  # noqa: N803
        assert Name == loader.MARKER and Type == "String" and Overwrite
        self.written.append(Value)


def test_a_row_read_back_from_dynamodb_digests_as_the_file_row_it_was_written_from():
    table = Table(FILE)
    assert rights_table.digest(loader.scan(table, "t")) == rights_table.digest(FILE) == rights_table.file_digest(ROOT)


def test_the_load_deletes_rows_the_file_lacks_and_sets_the_marker_to_what_it_scanned():
    stale = {**FILE[0], "table_row": "r-999"}
    table, marker = Table([*FILE, stale]), Marker()
    code, said = loader.load(table, marker, "t", FILE)
    assert code == 0 and "deleted 1 (r-999)" in said
    assert "r-999" not in table.items and len(table.items) == len(FILE)
    assert marker.written == [loader.LOADING, rights_table.digest(FILE)]


def test_a_table_that_does_not_read_back_as_the_file_leaves_the_marker_loading():
    """The marker is a read of the table, not the deployer's claim (security-reviewer on e2839f2, NOTE 5)."""

    class Lossy(Table):
        def put_item(self, TableName, Item):  # noqa: N803
            if Item["table_row"]["S"] != FILE[0]["table_row"]:
                super().put_item(TableName, Item)

    table, marker = Lossy(), Marker()
    code, said = loader.load(table, marker, "t", FILE)
    assert code == 1 and marker.written == [loader.LOADING] and "stays 'loading'" in said


def test_a_changed_row_changes_the_digest():
    """Seed S1's r-003, exclusive false -> true: the digest the runtime match compares must move."""
    changed = [dict(row, exclusive=True) if row["table_row"] == "r-003" else row for row in FILE]
    assert rights_table.digest(changed) != rights_table.digest(FILE)


def test_a_type_the_loader_never_writes_is_refused():
    with pytest.raises(ValueError, match="not a type load_rights_table writes"):
        rights_table.from_item({"table_row": {"S": "r-001"}, "n": {"N": "1"}})
