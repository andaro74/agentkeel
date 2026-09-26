"""infra/ingest: the corpus ingest stack and its promoter (M03 PR 2, SPEC/03 §6; seed S5's pipeline).

The template is synthesised here, as tests/test_bootstrap.py does, and the
promoter is run against fakes: nothing here calls AWS.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "infra" / "ingest" / "app.py"
S5 = ROOT / "tests" / "fixtures" / "m03" / "s5-unsigned-amendment.md"


@pytest.fixture(scope="module")
def template(tmp_path_factory) -> dict[str, Any]:
    out = tmp_path_factory.mktemp("ingest")
    done = subprocess.run([sys.executable, str(APP)], cwd=ROOT, capture_output=True, text=True, check=False,
                          env={**os.environ, "PYTHONPATH": str(ROOT), "CDK_OUTDIR": str(out)})  # fmt: skip
    assert done.returncode == 0, done.stderr
    return json.loads((out / "AgentkeelIngest.template.json").read_text(encoding="utf-8"))


def of_type(template, kind):
    return {k: v for k, v in template["Resources"].items() if v["Type"] == kind}


def bucket(template, prefix):
    return next(v for k, v in of_type(template, "AWS::S3::Bucket").items() if k.startswith(prefix))


def test_production_is_locked_in_compliance_for_one_day(template):
    """The human as Security, 2026-09-25. A shorter period or GOVERNANCE is a relaxation."""
    props = bucket(template, "Production")["Properties"]
    assert props["ObjectLockEnabled"] is True
    assert props["ObjectLockConfiguration"]["Rule"]["DefaultRetention"] == {"Mode": "COMPLIANCE", "Days": 1}
    assert props["VersioningConfiguration"] == {"Status": "Enabled"}


def policy_of(template, prefix):
    policies = of_type(template, "AWS::S3::BucketPolicy")
    return next(v["Properties"]["PolicyDocument"]["Statement"] for v in policies.values()
                if prefix in json.dumps(v["Properties"]["Bucket"]))  # fmt: skip


def test_only_the_promoter_puts_into_production(template):
    deny = next(s for s in policy_of(template, "Production") if s.get("Sid") == "OnlyThePromoterPromotes")
    assert deny["Effect"] == "Deny" and deny["Principal"] == {"AWS": "*"} and deny["Action"] == "s3:PutObject"
    assert "PromoterRole" in json.dumps(deny["Condition"]["ArnNotEquals"]["aws:PrincipalArn"])


def test_nobody_hides_replicates_into_holds_or_relocks_a_promoted_object(template):
    """security-reviewer F1 and platform-architect F3 on 2e93d27: a delete marker would read as absent."""
    deny = next(s for s in policy_of(template, "Production") if s.get("Sid") == "NobodyHidesOrReLocksAPromotedObject")
    assert deny["Effect"] == "Deny" and deny["Principal"] == {"AWS": "*"} and "Condition" not in deny
    assert set(deny["Action"]) == {"s3:DeleteObject", "s3:DeleteObjectVersion", "s3:ReplicateObject",
                                   "s3:ReplicateDelete", "s3:PutObjectLegalHold", "s3:PutObjectRetention",
                                   "s3:PutBucketObjectLockConfiguration"}  # fmt: skip


def test_the_eval_role_reads_production_and_the_record_and_writes_neither(template):
    read = next(s for s in policy_of(template, "Production") if s.get("Sid") == "TheEvalRoleReads")
    assert sorted(read["Action"]) == ["s3:GetObject", "s3:GetObjectVersion", "s3:ListBucket", "s3:ListBucketVersions"]
    assert "role/agentkeel-evals" in json.dumps(read["Principal"])
    quarantine = next(s for s in policy_of(template, "Quarantine") if s.get("Sid") == "TheEvalRoleReadsVersions")
    assert sorted(quarantine["Action"]) == ["s3:GetObjectVersion", "s3:ListBucketVersions"]
    (table,) = of_type(template, "AWS::DynamoDB::Table").values()
    statements = table["Properties"]["ResourcePolicy"]["PolicyDocument"]["Statement"]
    assert [sorted(s["Action"]) for s in statements] == [["dynamodb:GetItem", "dynamodb:Query"]]
    assert table["Properties"]["DeletionProtectionEnabled"] is True


def test_the_promoter_is_trusted_by_lambda_alone_and_carries_the_deploy_boundary(template):
    (role,) = [v for k, v in of_type(template, "AWS::IAM::Role").items() if k.startswith("PromoterRole")]
    trust = role["Properties"]["AssumeRolePolicyDocument"]["Statement"]
    assert [s["Principal"] for s in trust] == [{"Service": "lambda.amazonaws.com"}]
    assert "agentkeel-deploy-boundary" in json.dumps(role["Properties"]["PermissionsBoundary"])


def test_the_promoter_may_do_these_things_and_nothing_else(template):
    (policy,) = [v for k, v in of_type(template, "AWS::IAM::Policy").items() if k.startswith("PromoterRole")]
    actions = {s["Sid"]: s["Action"] for s in policy["Properties"]["PolicyDocument"]["Statement"]}
    assert actions == {
        "ReadQuarantine": ["s3:GetObject", "s3:GetObjectVersion"], "WriteProduction": "s3:PutObject",
        "WriteTheRecord": "dynamodb:PutItem", "ScanWithRefagentsGuardrail": "bedrock:ApplyGuardrail",
        "ItsOwnLogs": ["logs:CreateLogStream", "logs:PutLogEvents"]}  # fmt: skip


def test_the_promoter_holds_the_admitted_list_and_the_manifests_guardrail_pin(template):
    (function,) = of_type(template, "AWS::Lambda::Function").values()
    env = function["Properties"]["Environment"]["Variables"]
    admitted = yaml.safe_load((ROOT / "data" / "corpus" / "admitted.yaml").read_text(encoding="utf-8"))
    assert json.loads(env["ADMITTED"]) == {e["sha256"]: Path(e["key"]).suffix for e in admitted}
    from src.verdict import fingerprint_of

    text = (ROOT / "data" / "corpus" / "admitted.yaml").read_text(encoding="utf-8")
    assert env["ADMITTED_FINGERPRINT"] == fingerprint_of(text)
    pin = yaml.safe_load((ROOT / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8"))["guardrail"]
    assert (env["GUARDRAIL_ID"], env["GUARDRAIL_VERSION"]) == (pin["id"], pin["version"])
    source = (ROOT / "infra" / "ingest" / "promoter.py").read_text(encoding="utf-8")
    assert function["Properties"]["Code"]["ZipFile"] == source


def test_the_unsigned_amendment_is_not_on_the_promoters_list(template):
    (function,) = of_type(template, "AWS::Lambda::Function").values()
    s5 = hashlib.sha256(S5.read_bytes()).hexdigest()
    assert s5 not in json.loads(function["Properties"]["Environment"]["Variables"]["ADMITTED"])


def test_every_name_is_refagents(template):
    """platform-architect on 2e93d27, F5: the corpus is one agent's, and M05 allows no shared surface."""
    names = [bucket(template, "Quarantine")["Properties"]["BucketName"],
             bucket(template, "Production")["Properties"]["BucketName"]]
    for kind, field in [("AWS::DynamoDB::Table", "TableName"), ("AWS::IAM::Role", "RoleName"),
                        ("AWS::Lambda::Function", "FunctionName")]:
        names += [v["Properties"][field] for v in of_type(template, kind).values()]
    assert all("agentkeel-refagent-" in json.dumps(n) for n in names), names


def test_no_reserved_concurrency(template):
    """security-reviewer on 2e93d27, F7: a new account may reserve none."""
    (function,) = of_type(template, "AWS::Lambda::Function").values()
    assert "ReservedConcurrentExecutions" not in function["Properties"]


def test_every_new_quarantine_object_invokes_the_promoter(template):
    props = bucket(template, "Quarantine")["Properties"]
    assert [c["Event"] for c in props["NotificationConfiguration"]["LambdaConfigurations"]] == ["s3:ObjectCreated:*"]
    assert props["VersioningConfiguration"] == {"Status": "Enabled"}


# --- the promoter, against fakes ---------------------------------------------------


@pytest.fixture
def promoter(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-west-2")
    monkeypatch.setenv("PRODUCTION", "prod")
    monkeypatch.setenv("RECORD", "record")
    import importlib.util

    spec = importlib.util.spec_from_file_location("promoter", ROOT / "infra" / "ingest" / "promoter.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Fake:
    def __init__(self, body: bytes):
        self.body, self.put, self.items = body, [], []

    def get_object(self, Bucket, Key, VersionId):
        return {"Body": io.BytesIO(self.body)}

    def put_object(self, **kwargs):
        self.put.append(kwargs)

    def put_item(self, TableName, Item, ConditionExpression=None):
        self.items.append(Item)


def test_an_admitted_document_is_promoted_under_its_sha256_and_extension_and_recorded(promoter, monkeypatch):
    monkeypatch.setenv("ADMITTED_FINGERPRINT", "f" * 64)
    body = b"admitted bytes"
    sha = hashlib.sha256(body).hexdigest()
    fake = Fake(body)
    out = promoter.promote("q", "doc.md", "v1", s3=fake, db=fake, scanner=lambda b: "NONE", admitted={sha: ".md"})
    assert out["promoted"] and [p["Key"] for p in fake.put] == [sha + ".md"] and fake.put[0]["Bucket"] == "prod"
    assert fake.put[0]["ChecksumAlgorithm"] == "SHA256"
    item = fake.items[0]
    assert item["promoted"] == {"BOOL": True} and item["sha256"] == {"S": sha}
    assert item["production_key"] == {"S": sha + ".md"} and item["admitted_fingerprint"] == {"S": "f" * 64}


def test_a_document_nobody_admitted_stays_in_quarantine_and_is_recorded(promoter):
    """Seed S5: the expected refusal is no admission; the scan decides nothing."""
    fake = Fake(S5.read_bytes())
    out = promoter.promote("q", "amendment-2.md", "v1", s3=fake, db=fake, scanner=lambda b: "NONE", admitted={})
    assert not out["promoted"] and fake.put == []
    assert fake.items[0]["promoted"] == {"BOOL": False} and fake.items[0]["scan_result"] == {"S": "NONE"}


def test_a_scan_hit_is_recorded_and_does_not_stop_an_admitted_document(promoter):
    """The Data Owner's ruling: the master license's invented contact details are a PII hit, and admitted."""
    body = b"licence with a phone"
    fake = Fake(body)
    hit = "GUARDRAIL_INTERVENED sensitiveInformationPolicy"
    out = promoter.promote("q", "m.md", "v1", s3=fake, db=fake, scanner=lambda b: hit,
                           admitted={hashlib.sha256(body).hexdigest(): ".md"})  # fmt: skip
    assert out["promoted"] and fake.items[0]["scan_result"] == {"S": hit}


def test_a_scan_that_fails_is_recorded_as_failing(promoter, monkeypatch):
    class Refusing:
        def apply_guardrail(self, **kwargs):
            raise RuntimeError("throttled")

    monkeypatch.setattr(promoter, "BR", Refusing())
    monkeypatch.setenv("GUARDRAIL_ID", "g")
    monkeypatch.setenv("GUARDRAIL_VERSION", "4")
    assert promoter.scan(b"x") == "ERROR RuntimeError"


def test_an_odd_key_is_escaped_in_metadata_and_still_recorded(promoter):
    """security-reviewer on 2e93d27: a non-ASCII key in an HTTP header raised before the record was written."""
    body = b"bytes"
    fake = Fake(body)
    promoter.promote("q", "amendment ü\n.md", "v1", s3=fake, db=fake, scanner=lambda b: "NONE",
                     admitted={hashlib.sha256(body).hexdigest(): ".md"})  # fmt: skip
    assert fake.put[0]["Metadata"]["quarantine-key"].isascii() and fake.items


def test_a_record_is_written_once(promoter):
    class Once(Fake):
        def put_item(self, TableName, Item, ConditionExpression):
            assert ConditionExpression == "attribute_not_exists(version_id)"
            if self.items:
                raise RuntimeError("ConditionalCheckFailedException: the item exists")
            self.items.append(Item)

    fake = Once(b"bytes")
    for _ in range(2):  # S3 retries an async invoke; the second write is refused and ignored
        promoter.promote("q", "k.md", "v1", s3=fake, db=fake, scanner=lambda b: "NONE", admitted={})
    assert len(fake.items) == 1


def test_a_partial_scan_says_so(promoter, monkeypatch):
    class Fine:
        def apply_guardrail(self, **kwargs):
            return {"action": "NONE", "assessments": []}

    monkeypatch.setattr(promoter, "BR", Fine())
    monkeypatch.setenv("GUARDRAIL_ID", "g")
    monkeypatch.setenv("GUARDRAIL_VERSION", "4")
    assert promoter.scan(b"x" * 20001) == "NONE (first 20000 of 20001 characters)"


def test_the_ingest_citation_serves_the_ingest_stack_only():
    """security-reviewer on 2e93d27: SPEC/03 section 6 names one stack."""
    from src.validate import checks

    assert checks._names_its_case("SPEC/03 §6: the promoter", "AgentkeelIngest/PromoterRole/DefaultPolicy/Resource")
    assert not checks._names_its_case("SPEC/03 §6: the promoter", "AgentkeelBootstrap/EvalRole/DefaultPolicy/Resource")


def test_the_promoter_fits_inline():
    assert len((ROOT / "infra" / "ingest" / "promoter.py").read_bytes()) <= 4096


def test_the_app_synthesises_the_way_cdk_runs_it(tmp_path):
    """cdk.json runs app.py from infra/ingest with no PYTHONPATH; the first stop B failed on `import src`."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    done = subprocess.run([sys.executable, "app.py"], cwd=APP.parent, capture_output=True, text=True, check=False,
                          env={**env, "CDK_OUTDIR": str(tmp_path)})  # fmt: skip
    assert done.returncode == 0, done.stderr
