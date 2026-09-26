"""The corpus is what admitted.yaml says, byte for byte (M03 PR 2; data-owner F7 at M03 PR 1).

`data/corpus/admitted.yaml` is the Data Owner's list of admitted documents:
a list of `{key, sha256, ruling}`, `key` relative to `data/corpus/`. The
ingest pipeline promotes an object to the production bucket only when this
file names its sha256 (SPEC/03 §6), and the corpus fingerprint is read from
it. So it must not drift from the documents:

- every entry's file exists and its sha256 is the entry's (bytes as
  committed: `.gitattributes` keeps `data/corpus/**` LF everywhere);
- every file under `data/corpus/` but `admitted.yaml` has an entry, once;
- every entry names a ruling file whose `seat:` is the Data Owner and whose
  `authorises` covers the document's path.

No corpus (no `admitted.yaml`) passes: nothing is admitted.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from src.gates import pattern_regex

CORPUS = Path("data") / "corpus"
ADMITTED = CORPUS / "admitted.yaml"


def front_matter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    loaded = yaml.safe_load(text.split("---", 2)[1])
    return loaded if isinstance(loaded, dict) else None


def check(root: Path) -> list[str]:
    admitted = root / ADMITTED
    corpus = root / CORPUS
    files = {p.relative_to(corpus).as_posix() for p in corpus.rglob("*") if p.is_file()} - {"admitted.yaml"} \
        if corpus.is_dir() else set()  # fmt: skip
    if not admitted.is_file():
        return [f"{CORPUS.as_posix()}/{name}: a document with no admitted.yaml" for name in sorted(files)]
    entries = yaml.safe_load(admitted.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        return [f"{ADMITTED.as_posix()}: a list of {{key, sha256, ruling}}"]
    errors: list[str] = []
    keys = [e.get("key") for e in entries if isinstance(e, dict)]
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"key", "sha256", "ruling"}:
            errors.append(f"{ADMITTED.as_posix()}: {entry!r} is not {{key, sha256, ruling}}")
            continue
        path = corpus / entry["key"]
        rel = f"{CORPUS.as_posix()}/{entry['key']}"
        if not path.is_file():
            errors.append(f"{rel}: admitted and not in the tree")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            errors.append(f"{rel}: its bytes are not the sha256 admitted.yaml names")
        ruling = root / entry["ruling"]
        fm = front_matter(ruling) if ruling.is_file() else None
        if fm is None:
            errors.append(f"{rel}: admitted under {entry['ruling']}, which is not a ruling file")
        elif fm.get("seat") != "Data Owner":
            errors.append(f"{rel}: admitted under {entry['ruling']}, whose seat is {fm.get('seat')!r}, not Data Owner")
        elif not any(pattern_regex(str(p), anchored=True).match(rel) for p in fm.get("authorises") or []):
            errors.append(f"{rel}: {entry['ruling']} does not authorise it")
    errors += [f"{ADMITTED.as_posix()}: {key} is admitted twice" for key in sorted({k for k in keys if keys.count(k) > 1})]
    errors += [f"{CORPUS.as_posix()}/{name}: in the corpus and not in admitted.yaml" for name in sorted(files - set(keys))]
    return errors
