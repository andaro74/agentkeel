"""pack and verify: the archive recipe, and every reason a bundle is refused (SPEC/01 §2)."""

from __future__ import annotations

import base64
import json
import shutil
from pathlib import Path

import pytest

from src.bundle import pack, verify
from src.verdict import ROOT

S1 = ROOT / "tests" / "fixtures" / "bundles" / "unsigned"
S2 = ROOT / "tests" / "fixtures" / "bundles" / "altered"


def signed_digest_of(bundle_dir: Path) -> str:
    return verify.signed_digest(verify.cosign_bundle(bundle_dir))


def test_pack_reproduces_the_archive_ci_signed(tmp_path):
    """The recipe in sign-fixture.yml and the one here are the same bytes (run 35473348573)."""
    archive = pack.pack(S1, tmp_path / "s1.tar")
    assert pack.digest(archive) == signed_digest_of(S2)


def test_pack_is_the_same_on_any_line_endings(tmp_path):
    """core.autocrlf is on: a Windows checkout holds CRLF, the repo holds LF, one digest."""
    crlf = tmp_path / "crlf"
    crlf.mkdir()
    for path in pack.files(S1):
        target = crlf / path.relative_to(S1)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    assert pack.digest(pack.pack(crlf, tmp_path / "a.tar")) == pack.digest(pack.pack(S1, tmp_path / "b.tar"))


def test_pack_says_nothing_about_when_or_where_it_ran(tmp_path):
    copy = tmp_path / "copy"
    shutil.copytree(S1, copy)
    for path in pack.files(copy):  # a different mtime, a different place on disk
        path.touch()
    assert pack.digest(pack.pack(copy, tmp_path / "a.tar")) == pack.digest(pack.pack(S1, tmp_path / "b.tar"))


def test_s1_is_refused_for_its_missing_signature_and_nothing_else():
    with pytest.raises(verify.Refused) as refusal:
        verify.verify(S1)
    assert refusal.value.reasons == [f"signature: no {pack.BUNDLE_NAME} beside {S1.as_posix()}"]


def test_s2_is_refused_for_its_digest(tmp_path):
    """S2 carries S1's signature over S1's bytes; its own differ by one (SPEC/01 §5)."""
    with pytest.raises(verify.Refused) as refusal:
        verify.verify(S2)
    digests = [r for r in refusal.value.reasons if r.startswith("digest: ")]
    assert len(digests) == 1 and signed_digest_of(S2)[:12] in digests[0]


def test_a_seed_is_refused_for_its_own_reason_whoever_signed_it():
    """Ruling on BLOCK 1: every reason is reported, so the identity never hides the digest."""
    with pytest.raises(verify.Refused) as deploy:
        verify.verify(S2)
    with pytest.raises(verify.Refused) as measured:
        verify.verify(S2, measure_identity=signer_identity())
    assert any(r.startswith("digest: ") for r in deploy.value.reasons)
    assert any(r.startswith("digest: ") for r in measured.value.reasons)
    # the deploy run also refuses the identity; the measurement run accepts it
    assert any(r.startswith("identity: ") for r in deploy.value.reasons)
    assert not any(r.startswith("identity: ") for r in measured.value.reasons)


def signer_identity() -> str:
    """Who signed S2's bundle, from the certificate itself."""
    san, _ = verify.certificate_fields(verify.certificate(verify.cosign_bundle(S2)))
    return san or verify.DEPLOY_IDENTITY


def test_the_signature_is_the_workflows_and_this_repository_id():
    san, repository_id = verify.certificate_fields(verify.certificate(verify.cosign_bundle(S2)))
    assert san == "https://github.com/andaro74/agentkeel/.github/workflows/sign-fixture.yml@refs/pull/8/merge"
    assert repository_id == verify.REPOSITORY_ID  # Fulcio OID 1.3.6.1.4.1.57264.1.15, ruling g
    assert san != verify.DEPLOY_IDENTITY  # a fixture signature can never deploy


def test_a_bundle_with_a_broken_signature_file_is_refused(tmp_path):
    copy = tmp_path / "broken"
    shutil.copytree(S2, copy)
    (copy / pack.BUNDLE_NAME).write_text("{not json", encoding="utf-8")
    with pytest.raises(verify.Refused, match="is not JSON"):
        verify.verify(copy)


@pytest.mark.skipif(not shutil.which("cosign"), reason="the signature itself cannot be checked without cosign")
def test_a_bundle_signed_over_its_own_bytes_is_accepted(tmp_path):
    """S1's bytes with S1's signature: nothing to refuse. The signature file is not packed.

    Skipped where cosign is absent, and that is the point: `verify` refuses a
    bundle whose signature it could not check rather than accepting it, so
    this can only pass where the check really ran. CI installs cosign before
    pytest for exactly this test.
    """
    copy = tmp_path / "matching"
    shutil.copytree(S1, copy)
    (copy / pack.BUNDLE_NAME).write_text((S2 / pack.BUNDLE_NAME).read_text(encoding="utf-8"), encoding="utf-8")
    checked = verify.verify(copy, measure_identity=signer_identity())
    assert checked["digest"] == signed_digest_of(S2)
    assert checked["measurement_only"] is True and checked["signature_checked"] is True


def test_a_bundle_whose_signature_cannot_be_checked_is_refused_not_accepted(tmp_path, monkeypatch):
    """Cold review finding 5: no cosign, no certificate, matching digest — this used to pass."""
    copy = tmp_path / "unchecked"
    shutil.copytree(S1, copy)
    archive = pack.pack(copy, tmp_path / "s1.tar")
    forged = {"rekorBundle": {"Payload": {"body": base64.b64encode(json.dumps(
        {"spec": {"data": {"hash": {"algorithm": "sha256", "value": pack.digest(archive)}}}}).encode()).decode()}}}
    (copy / pack.BUNDLE_NAME).write_text(json.dumps(forged), encoding="utf-8")
    monkeypatch.setattr(verify.shutil, "which", lambda _: None)  # a machine with no cosign
    with pytest.raises(verify.Refused) as refusal:
        verify.verify(copy)
    assert "identity: no certificate in the cosign bundle that this can read" in refusal.value.reasons


def test_the_rekor_entry_carries_the_digest():
    bundle = verify.cosign_bundle(S2)
    body = json.loads(base64.b64decode(bundle["rekorBundle"]["Payload"]["body"]))
    assert body["spec"]["data"]["hash"]["algorithm"] == "sha256"
