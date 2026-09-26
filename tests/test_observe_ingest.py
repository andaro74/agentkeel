"""scripts/observe_ingest.py: F3_5 passes only when AWS shows the seed refused (M03 PR 2, seed S5's reader).

No AWS: the lookup is passed in, as runtime_for_tree's is.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from scripts import observe_ingest as oi
from src.verdict import ROOT, fingerprint_of

DOCUMENT = (ROOT / "tests" / "fixtures" / "m03" / "s5-unsigned-amendment.md").read_bytes()
SHA = hashlib.sha256(DOCUMENT).hexdigest()
ADMITTED = (ROOT / "data" / "corpus" / "admitted.yaml").read_text(encoding="utf-8")
OBSERVED = {"quarantine_bucket": "agentkeel-refagent-quarantine-111122223333", "key": "amendment-2.md",
            "version_id": "v1", "sha256": SHA}  # fmt: skip


def found(**change):
    base = {"errors": [], "in_quarantine": True, "production_versions": [],
            "record": {"sha256": SHA, "promoted": False, "admitted_fingerprint": fingerprint_of(ADMITTED)}}  # fmt: skip
    return {**base, **change}


def test_the_seed_refused_passes():
    assert oi.judge(OBSERVED, found(), DOCUMENT, ADMITTED) == {
        "falsifier": "F3.5", "sha256": SHA, "pass": True, "reasons": [], "scan_result": None}


@pytest.mark.parametrize(("change", "said"), [
    ({"production_versions": [f"{SHA}.md"]}, "production holds"),
    ({"record": {"sha256": SHA, "promoted": True, "admitted_fingerprint": fingerprint_of(ADMITTED)}}, "promoted True"),
    ({"record": {"sha256": SHA, "promoted": False, "admitted_fingerprint": "x"}}, "another admitted list"),
    ({"record": None}, "no record"),
    ({"in_quarantine": False}, "not in quarantine"),
    ({"errors": ["record: ClientError: AccessDenied"], "record": None}, "record: ClientError"),
])  # fmt: skip
def test_anything_else_fails_and_says_why(change, said):
    verdict = oi.judge(OBSERVED, found(**change), DOCUMENT, ADMITTED)
    assert not verdict["pass"] and any(said in reason for reason in verdict["reasons"]), verdict


def test_a_run_file_naming_other_bytes_fails():
    verdict = oi.judge({**OBSERVED, "sha256": "0" * 64}, found(), DOCUMENT, ADMITTED)
    assert not verdict["pass"] and "not the seed's" in verdict["reasons"][0]


def test_an_admitted_list_naming_the_seed_fails():
    admitted = ADMITTED + f"- key: amendment-2.md\n  sha256: {SHA}\n  ruling: x\n"
    record = {"sha256": SHA, "promoted": False, "admitted_fingerprint": fingerprint_of(admitted)}
    verdict = oi.judge(OBSERVED, found(record=record), DOCUMENT, admitted)
    assert verdict["reasons"] == ["admitted.yaml names the seed"]


def test_production_is_the_corpus_bucket_beside_quarantine():
    assert oi.production_of("agentkeel-refagent-quarantine-1") == "agentkeel-refagent-corpus-1"


def test_the_lookup_reads_versions_and_delete_markers_and_never_raises():
    class Session:
        def client(self, name):
            return self

        def get_item(self, **kwargs):
            return {"Item": {"sha256": {"S": SHA}, "promoted": {"BOOL": False}}}

        def head_object(self, **kwargs):
            raise RuntimeError("403")

        def list_object_versions(self, **kwargs):
            assert kwargs["Bucket"] == "agentkeel-refagent-corpus-111122223333" and kwargs["Prefix"] == SHA
            return {"DeleteMarkers": [{"Key": f"{SHA}.md"}]}

    looked = oi.lookup(OBSERVED, Session())
    assert looked["record"] == {"sha256": SHA, "promoted": False}
    assert looked["in_quarantine"] is False and looked["production_versions"] == [f"{SHA}.md"]
    assert looked["errors"] == ["quarantine: RuntimeError: 403"]


def test_main_writes_the_observation_and_exits_0(tmp_path, monkeypatch):
    monkeypatch.setattr(oi, "lookup", lambda observed: found())
    out = tmp_path / "f3_5.json"
    assert oi.main([str(ROOT / "milestones" / "M03" / "runs" / "f3_5_amendment.yaml"), "--out", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["pass"] is True
