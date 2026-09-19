"""pack: one agent's bundle as one archive, the same bytes on any machine (SPEC/01 §2).

    python -m src.bundle.pack agents/refagent --out agents/refagent/dist

The recipe, which `.github/workflows/sign-fixture.yml` wrote first and this
module has to match byte for byte: every file under the bundle directory,
sorted by its path relative to that directory, ustar, mode 0644, mtime 0,
uid and gid 0, empty uname and gname, no directory entries, and CRLF
normalised to LF. Nothing in the archive says when or where it was built,
so the digest is the tree's.

The line endings matter: this repo has `core.autocrlf` on, so a Windows
checkout holds CRLF where the repo holds LF, and the same tree would
otherwise pack to two different digests. The archive holds LF, as the repo
does. A bundle is text at M01 (manifest, prompt, tools, rules); a binary
file in a bundle would need this rule reconsidered, and there is none.

`tests/test_bundle.py` packs S1 and compares the digest with the one inside
the signature the bot made; if this recipe drifts, that test fails.

The digest is the sha256 of the archive. It is what CI signs, what the
cosign bundle records, and what a deploy tags the runtime with (ruling h);
the manifest carries no digest of itself.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import sys
import tarfile
from pathlib import Path

ARCHIVE_NAME = "bundle.tar"
BUNDLE_NAME = "bundle.cosign.json"  # the cosign bundle: signature, certificate, rekor entry


def files(bundle_dir: Path) -> list[Path]:
    """Every file in the bundle, in the order the archive holds them.

    The signature and the build folder are not part of what is signed: the
    cosign bundle is written beside the bundle after the archive is made
    (ruling h), so packing it would change the digest it records.

    Nor is anything Python left behind. `__pycache__` holds bytes that
    differ by interpreter and by when the file was last imported, so a
    bundle packed after a local run would not have the digest CI signed.
    The fixtures have no such folder, so this excludes nothing sign-fixture
    packed.
    """
    return sorted(
        path
        for path in bundle_dir.rglob("*")
        if path.is_file()
        and path.name != BUNDLE_NAME
        and not {"dist", "__pycache__"} & set(path.relative_to(bundle_dir).parts)
    )


def pack(bundle_dir: Path, out: Path) -> Path:
    """Write the archive of `bundle_dir` to `out`, and return its path."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out, "w", format=tarfile.USTAR_FORMAT) as tar:
        for path in files(bundle_dir):
            content = path.read_bytes().replace(b"\r\n", b"\n")
            info = tarfile.TarInfo(path.relative_to(bundle_dir).as_posix())
            info.size = len(content)
            info.mode, info.mtime, info.uid, info.gid = 0o644, 0, 0, 0
            info.uname = info.gname = ""
            tar.addfile(info, io.BytesIO(content))
    return out


def digest(archive: Path) -> str:
    return hashlib.sha256(archive.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--out", type=Path, help="folder for the archive (default <bundle>/dist)")
    args = parser.parse_args(argv)

    out_dir = args.out or args.bundle / "dist"
    archive = pack(args.bundle, out_dir / ARCHIVE_NAME)
    print(f"{digest(archive)}  {archive.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
