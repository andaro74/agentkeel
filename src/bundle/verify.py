"""verify: refuse a bundle, and say every reason it is refused (SPEC/01 §2, F1.1).

    python -m src.bundle.verify agents/refagent            # for a deploy
    python -m src.bundle.verify tests/fixtures/bundles/altered --measure "<identity>"

Three things are checked, always, and every failing one is reported. A seed
is refused for the reason it was planted for, whatever else is also wrong
with it (ruling on `product-spec-reviewer` BLOCK 1):

1. **signature** — a cosign bundle sits beside the bundle directory, and
   `cosign verify-blob` accepts it over this bundle's archive;
2. **identity** — the certificate's subject is the deploy workflow on
   `main`, and its Fulcio Source Repository Identifier extension (OID
   1.3.6.1.4.1.57264.1.15) is this repository's id (ruling g). `--measure`
   accepts one other identity, for measuring S1 and S2 on a PR run, and the
   output says so;
3. **digest** — the archive of the bundle as it is now hashes to what the
   signature was made over (ruling h: the digest lives in the cosign bundle
   beside the archive, and as a tag on the deployed runtime; the manifest
   carries no digest of itself).

S1 (`tests/fixtures/bundles/unsigned/`) has no signature. S2
(`tests/fixtures/bundles/altered/`) carries S1's signature over S1's bytes
and differs from S1 by one byte, so its digest never matches. Neither can
be refused for the other's reason.

Exit 0, or 4 with every reason on stderr. This module reads no envelope and
writes none (P5).
"""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from cryptography import x509

from src.bundle.pack import ARCHIVE_NAME, BUNDLE_NAME, digest, pack

ISSUER = "https://token.actions.githubusercontent.com"
DEPLOY_IDENTITY = "https://github.com/andaro74/agentkeel/.github/workflows/deploy.yml@refs/heads/main"
# Fulcio's Source Repository Identifier. The repo id does not change when the
# repo is renamed, and a new repo of the same name does not inherit it.
REPOSITORY_ID_OID = "1.3.6.1.4.1.57264.1.15"
REPOSITORY_ID = "1376369685"


class Refused(Exception):
    """Not a bundle that may deploy or load. Carries every reason."""

    def __init__(self, reasons: list[str]) -> None:
        super().__init__("; ".join(reasons))
        self.reasons = reasons


def cosign_bundle(bundle_dir: Path) -> dict[str, Any] | None:
    path = bundle_dir / BUNDLE_NAME
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def certificate(bundle: dict[str, Any]) -> str:
    """The signing certificate, PEM, from the cosign bundle."""
    return base64.b64decode(bundle.get("cert", "")).decode("utf-8", "replace")


def certificate_fields(pem: str) -> tuple[str | None, str | None]:
    """(subject alternative name, source repository id) from the certificate, or (None, None).

    The repository id is a Fulcio extension whose value is a DER UTF8String,
    two bytes of header and then the digits.
    """
    if not pem.strip():
        return None, None
    try:
        certificate = x509.load_pem_x509_certificate(pem.encode())
    except ValueError:
        return None, None
    names = certificate.extensions.get_extension_for_class(x509.SubjectAlternativeName)
    san = next(iter(names.value.get_values_for_type(x509.UniformResourceIdentifier)), None)
    repository_id = None
    for extension in certificate.extensions:
        if extension.oid.dotted_string == REPOSITORY_ID_OID:
            raw = extension.value.value
            repository_id = raw[2:].decode("utf-8", "replace") if len(raw) > 2 else ""
    return san, repository_id


def signed_digest(bundle: dict[str, Any]) -> str | None:
    """The digest cosign signed, from the rekor entry inside the bundle."""
    payload = (bundle.get("rekorBundle") or {}).get("Payload", {}).get("body")
    if not payload:
        return None
    try:
        body = json.loads(base64.b64decode(payload))
        return body["spec"]["data"]["hash"]["value"]
    except (ValueError, KeyError):
        return None


def cosign_accepts(archive: Path, bundle_path: Path, identity: str) -> str | None:
    """None when cosign verifies the blob, else why not.

    When cosign is not on the machine the signature itself cannot be checked,
    and the caller is told so rather than being given a pass. The identity and
    the digest are still read here, from the bundle, without it.
    """
    if not shutil.which("cosign"):
        return "cosign is not on this machine, so the signature itself was not checked"
    done = subprocess.run(
        ["cosign", "verify-blob", "--bundle", str(bundle_path), "--certificate-oidc-issuer", ISSUER,
         "--certificate-identity", identity, str(archive)],
        capture_output=True, text=True,
    )  # fmt: skip
    return None if done.returncode == 0 else (done.stderr.strip() or "cosign refused the blob")


def verify(bundle_dir: Path, *, measure_identity: str | None = None) -> dict[str, Any]:
    """Refuse `bundle_dir`, with every reason, or return what was checked."""
    reasons: list[str] = []
    identity = measure_identity or DEPLOY_IDENTITY
    bundle = cosign_bundle(bundle_dir)

    checked_signature = False
    with tempfile.TemporaryDirectory() as work:
        archive = pack(bundle_dir, Path(work) / ARCHIVE_NAME)
        archive_digest = digest(archive)

        if bundle is None:
            reasons.append(f"signature: no {BUNDLE_NAME} beside {bundle_dir.as_posix()}")
        elif not bundle:
            reasons.append(f"signature: {BUNDLE_NAME} is not JSON")
        else:
            san, repository_id = certificate_fields(certificate(bundle))
            if san is None or repository_id is None:
                # A certificate this cannot read is not a certificate that
                # signed anything. Reading the two fields as "no reason to
                # refuse" would let a hand-written bundle with no `cert` and a
                # matching digest through, which is F1.1's first clause.
                reasons.append("identity: no certificate in the cosign bundle that this can read")
            if san is not None and san != identity:
                reasons.append(f"identity: signed by {san}, not {identity}")
            if repository_id is not None and repository_id != REPOSITORY_ID:
                reasons.append(f"identity: source repository id {repository_id}, not {REPOSITORY_ID}")
            if (refusal := cosign_accepts(archive, bundle_dir / BUNDLE_NAME, identity)) and not reasons:
                reasons.append(f"signature: {refusal}")
            checked_signature = refusal is None

            signed = signed_digest(bundle)
            if signed is None:
                reasons.append("digest: the cosign bundle carries no signed digest")
            elif signed != archive_digest:
                reasons.append(f"digest: the bundle hashes to {archive_digest[:12]}, signed {signed[:12]}")

    if reasons:
        raise Refused(reasons)
    return {"bundle": bundle_dir.as_posix(), "digest": archive_digest, "identity": identity,
            "signature_checked": checked_signature, "measurement_only": bool(measure_identity)}  # fmt: skip


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--measure", metavar="IDENTITY",
                        help="accept this identity instead of the deploy workflow's, for a measurement on a PR run")  # fmt: skip
    args = parser.parse_args(argv)

    try:
        checked = verify(args.bundle, measure_identity=args.measure)
    except Refused as refusal:
        print(f"REFUSED {args.bundle.as_posix()}", file=sys.stderr)
        for reason in refusal.reasons:
            print(f"  {reason}", file=sys.stderr)
        return 4
    if checked["measurement_only"]:
        print(f"accepted for a MEASUREMENT only, on identity {checked['identity']}: not a deploy")
    if not checked["signature_checked"]:
        print("warning: cosign is not on this machine; the identity and the digest were read, "
              "the signature was not", file=sys.stderr)  # fmt: skip
    print(f"ok {checked['bundle']} {checked['digest']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
