"""Look up seed S5's attempt in AWS, as CI's eval role (M03 PR 2; SPEC/03 §5.1, §6; seed S5's reader).

    python scripts/observe_ingest.py milestones/M03/runs/f3_5_amendment.yaml --out f3_5.json

The human made the attempt at stop B and wrote what AWS returned into the run
file's `observed`. What the human wrote feeds no check by itself: this script
looks the object up again, and its answer is what `checks.F3_5` is built
from (SPEC/03 §4). The expected refusal is no admission (SPEC/03 §2):

1. **the record** for the run file's key and version id (the promoter's
   table): there, for the seed's bytes (its sha256), not promoted, written
   by a promoter holding the admitted list of the commit the stack was
   deployed from (`admitted_fingerprint` equals `admitted.yaml`'s
   fingerprint at the run file's `admitted_at`, not at this tree: a later
   admission must not turn F3_5 red on every run after it; the cold review
   of PR 2, F4);
2. **quarantine**: that version is in the bucket (S3's own word, not only
   the promoter's; `security-reviewer` on the ingest stack, F4);
3. **production**: no object and no version, current or deleted, under the
   seed's sha256 (a delete marker would read as absent to a HEAD);
4. **admitted.yaml** does not name the seed's sha256, then or now;
5. **the positive half** (`data-owner` on PR 2, F2): every document
   admitted at `admitted_at` is in production, under `<sha256>.md`.

The lookup is read-only and needs what the ingest stack's resource policies
give `agentkeel-evals`. It never fails the job: a lookup it cannot make is a
reason, and `pass` is false.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml

from src.verdict import fingerprint_of, text_at

REGION = "us-west-2"
RECORD = "agentkeel-refagent-ingest-record"


def production_of(quarantine: str) -> str:
    """The production bucket beside a quarantine bucket (infra/ingest/app.py names both)."""
    return quarantine.replace("-quarantine-", "-corpus-")


def lookup(observed: dict[str, Any], session: Any = None) -> dict[str, Any]:
    """What AWS holds for the attempt. Every call's failure is recorded, never raised."""
    import boto3

    session = session or boto3.session.Session(region_name=REGION)
    s3, db = session.client("s3"), session.client("dynamodb")
    quarantine, key, version = observed["quarantine_bucket"], observed["key"], observed["version_id"]
    sha = observed["sha256"]
    found: dict[str, Any] = {"errors": []}
    try:
        item = db.get_item(TableName=RECORD, Key={"key": {"S": key}, "version_id": {"S": version}}, ConsistentRead=True)
        found["record"] = {k: next(iter(v.values())) for k, v in item.get("Item", {}).items()} or None
    except Exception as exc:  # noqa: BLE001 - a lookup that fails is a reason
        found["errors"].append(f"record: {type(exc).__name__}: {exc}")
    try:
        s3.head_object(Bucket=quarantine, Key=key, VersionId=version)
        found["in_quarantine"] = True
    except Exception as exc:  # noqa: BLE001
        found["in_quarantine"] = False
        found["errors"].append(f"quarantine: {type(exc).__name__}: {exc}")
    try:
        page = s3.list_object_versions(Bucket=production_of(quarantine), Prefix=sha)
        found["production_versions"] = [v["Key"] for v in page.get("Versions", [])] + [
            m["Key"] for m in page.get("DeleteMarkers", [])]  # fmt: skip
        listed = s3.list_objects_v2(Bucket=production_of(quarantine))
        found["production_keys"] = [o["Key"] for o in listed.get("Contents", [])]
    except Exception as exc:  # noqa: BLE001
        found["errors"].append(f"production: {type(exc).__name__}: {exc}")
    return found


def judge(observed: dict[str, Any], found: dict[str, Any], document: bytes, admitted: str,
          admitted_then: str | None = None) -> dict[str, Any]:  # fmt: skip
    """F3_5's observation: pass only when the lookup shows the seed refused, and why not otherwise.

    `admitted` is admitted.yaml in this tree; `admitted_then` at the commit the stack was deployed
    from (the run file's `admitted_at`), which is what the promoter held. None: the same.
    """
    admitted_then = admitted if admitted_then is None else admitted_then
    reasons = list(found.get("errors", []))
    sha = hashlib.sha256(document).hexdigest()
    if observed.get("sha256") != sha:
        reasons.append(f"the run file names sha256 {observed.get('sha256')!r}, not the seed's {sha}")
    record = found.get("record")
    if record is None and not any(r.startswith("record:") for r in reasons):
        reasons.append("no record of this version: the promoter did not see it")
    elif record is not None:
        if record.get("sha256") != sha:
            reasons.append(f"the record is for sha256 {record.get('sha256')}, not the seed's")
        if record.get("promoted") is not False:
            reasons.append(f"the record says promoted {record.get('promoted')!r}")
        if record.get("admitted_fingerprint") != fingerprint_of(admitted_then):
            reasons.append("the promoter held another admitted list than admitted.yaml at the commit it was "
                           "deployed from")  # fmt: skip
    if found.get("in_quarantine") is not True:
        reasons.append("the version is not in quarantine")
    if found.get("production_versions"):
        reasons.append(f"production holds {found['production_versions']}")
    for text in {admitted, admitted_then}:
        if sha in {e["sha256"] for e in yaml.safe_load(text) or []}:
            reasons.append("admitted.yaml names the seed")
    if "production_keys" in found:
        wanted = {e["sha256"] + Path(e["key"]).suffix for e in yaml.safe_load(admitted_then) or []}
        if missing := sorted(wanted - set(found["production_keys"])):
            reasons.append(f"admitted documents not in production: {missing}")
    return {"falsifier": "F3.5", "sha256": sha, "pass": not reasons, "reasons": reasons,
            "scan_result": (record or {}).get("scan_result")}  # fmt: skip


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    run = yaml.safe_load(args.run.read_text(encoding="utf-8"))
    observed = run.get("observed")
    document = (ROOT / run["document"]).read_bytes()
    admitted = (ROOT / "data" / "corpus" / "admitted.yaml").read_text(encoding="utf-8")
    if not observed:
        result = {"falsifier": "F3.5", "pass": False, "reasons": ["the attempt has not been made (observed: null)"]}
    else:
        then = observed.get("admitted_at")
        admitted_then = text_at(then, "data/corpus/admitted.yaml", ROOT)[0] if then else admitted
        result = judge(observed, lookup(observed), document, admitted, admitted_then or "")
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(("ok  " if result["pass"] else "FAIL ") + "F3.5: " + ("; ".join(result["reasons"]) or "the seed stayed out"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
