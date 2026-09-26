"""refagent's corpus promoter (SPEC/03 §6). Inlined into the Lambda at synth; keep it under 4096 bytes."""

import hashlib
import json
import os
import time
from urllib.parse import quote, unquote_plus

import boto3

S3, DB, BR = boto3.client("s3"), boto3.client("dynamodb"), boto3.client("bedrock-runtime")
ADMITTED = json.loads(os.environ.get("ADMITTED", "{}"))  # sha256 -> the extension admitted.yaml's key has
SCAN_MAX = 20000


def scan(body):
    """The guardrail's action and the policies it hit. Recorded; never decides promotion."""
    text = body.decode("utf-8", "replace")
    part = "" if len(text) <= SCAN_MAX else f" (first {SCAN_MAX} of {len(text)} characters)"
    try:
        r = BR.apply_guardrail(guardrailIdentifier=os.environ["GUARDRAIL_ID"],
                               guardrailVersion=os.environ["GUARDRAIL_VERSION"], source="INPUT",
                               content=[{"text": {"text": text[:SCAN_MAX]}}])
        hits = sorted({k for a in r.get("assessments", []) for k in a})
        return r["action"] + (" " + ",".join(hits) if hits else "") + part
    except Exception as e:  # a scan that fails is recorded as failing, and still decides nothing
        return "ERROR " + type(e).__name__ + part


def promote(bucket, key, version, s3=S3, db=DB, scanner=scan, admitted=ADMITTED, now=time.time):
    body = s3.get_object(Bucket=bucket, Key=key, VersionId=version)["Body"].read()
    sha = hashlib.sha256(body).hexdigest()
    result = scanner(body)
    promoted = sha in admitted
    target = sha + admitted.get(sha, "")
    if promoted:
        s3.put_object(Bucket=os.environ["PRODUCTION"], Key=target, Body=body, ChecksumAlgorithm="SHA256",
                      Metadata={"sha256": sha, "quarantine-key": quote(key, safe="")[:512]})
    item = {"key": {"S": key}, "version_id": {"S": version}, "sha256": {"S": sha},
            "scan_result": {"S": result}, "promoted": {"BOOL": promoted},
            "production_key": {"S": target if promoted else ""},
            "admitted_fingerprint": {"S": os.environ.get("ADMITTED_FINGERPRINT", "")},
            "at": {"S": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now()))}}
    try:  # one item per version, written once: a retry does not rewrite it
        db.put_item(TableName=os.environ["RECORD"], Item=item, ConditionExpression="attribute_not_exists(version_id)")
    except Exception as e:
        if "ConditionalCheckFailed" not in type(e).__name__ + str(e):
            raise
    return {"key": key, "sha256": sha, "promoted": promoted, "scan": result}


def handler(event, context):
    out = []
    for record in event.get("Records", []):
        obj = record["s3"]["object"]
        out.append(promote(record["s3"]["bucket"]["name"], unquote_plus(obj["key"]), obj.get("versionId", "null")))
    print(json.dumps(out))
    return out
