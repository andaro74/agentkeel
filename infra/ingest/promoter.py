"""The corpus promoter (SPEC/03 §6). Inlined into the Lambda at synth; keep it under 4096 bytes."""

import hashlib
import json
import os
import time
from urllib.parse import unquote_plus

import boto3

S3, DB, BR = boto3.client("s3"), boto3.client("dynamodb"), boto3.client("bedrock-runtime")
ADMITTED = set(json.loads(os.environ.get("ADMITTED", "[]")))


def scan(body):
    """The guardrail's action and the policies it hit. Recorded; never decides promotion."""
    try:
        r = BR.apply_guardrail(guardrailIdentifier=os.environ["GUARDRAIL_ID"],
                               guardrailVersion=os.environ["GUARDRAIL_VERSION"], source="INPUT",
                               content=[{"text": {"text": body.decode("utf-8", "replace")[:20000]}}])
        hits = sorted({k for a in r.get("assessments", []) for k in a})
        return r["action"] + (" " + ",".join(hits) if hits else "")
    except Exception as e:  # a scan that fails is recorded as failing, and still decides nothing
        return "ERROR " + type(e).__name__


def promote(bucket, key, version, s3=S3, db=DB, scanner=scan, admitted=ADMITTED, now=time.time):
    body = s3.get_object(Bucket=bucket, Key=key, VersionId=version)["Body"].read()
    sha = hashlib.sha256(body).hexdigest()
    result = scanner(body)
    promoted = sha in admitted
    if promoted:
        s3.put_object(Bucket=os.environ["PRODUCTION"], Key=sha, Body=body,
                      Metadata={"sha256": sha, "quarantine-key": key[:512]})
    db.put_item(TableName=os.environ["RECORD"], Item={
        "key": {"S": key}, "version_id": {"S": version}, "sha256": {"S": sha},
        "scan_result": {"S": result}, "promoted": {"BOOL": promoted},
        "at": {"S": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now()))}})
    return {"key": key, "sha256": sha, "promoted": promoted, "scan": result}


def handler(event, context):
    out = []
    for record in event.get("Records", []):
        obj = record["s3"]["object"]
        out.append(promote(record["s3"]["bucket"]["name"], unquote_plus(obj["key"]), obj.get("versionId", "null")))
    print(json.dumps(out))
    return out
