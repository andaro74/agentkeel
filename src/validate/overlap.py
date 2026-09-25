"""Golden/corpus overlap (M03 PR 2; SPEC/03 §2 and §6, seed S3's reader).

"Never let the corpus that judges an answer also supply the answer"
(CLAUDE.md). A golden whose question sits in a corpus document, or a
document that names the answer's row, lets retrieval hand the agent what
the golden grades. Two refusals, over every file under `data/corpus/` but
`admitted.yaml`:

- **the question side**: a run of BOUND or more words shared by a live
  golden's question and a document, after lower-casing and collapsing
  everything but letters and digits to one space (so `2026-12-03` is three
  words). BOUND is 12, the Data Owner's upper bound (feasibility F6):
  it may be lowered, and raised past 12 only by a ruling that re-reads S3;
- **the answer side, its mechanical half** (data-owner F1 at M03 PR 1): no
  `r-NNN` rights-table row id in a document. Retrieval never needs one;
  a document that names one hands over the answer's `table_row`. The other
  half, no document pairing a golden's title, territory and platform with
  its date or exclusivity, is the Data Owner's ruling on each document at
  admission, not a check.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

BOUND = 12
ROW_ID = re.compile(r"\br-\d{3}\b")


def words(text: str) -> list[str]:
    return re.sub(r"[^0-9a-z]+", " ", text.lower()).split()


def longest_shared_run(a: list[str], b: list[str]) -> int:
    """The longest run of consecutive words in both (dynamic programming over the two word lists)."""
    best, previous = 0, [0] * (len(b) + 1)
    for word in a:
        current = [0] * (len(b) + 1)
        for j, other in enumerate(b, 1):
            if word == other:
                current[j] = previous[j - 1] + 1
                best = max(best, current[j])
        previous = current
    return best


def documents(root: Path) -> list[Path]:
    corpus = root / "data" / "corpus"
    if not corpus.is_dir():
        return []
    return sorted(p for p in corpus.rglob("*") if p.is_file() and p.name != "admitted.yaml")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    goldens = []
    for path in sorted((root / "evals" / "goldens" / "v1").glob("g-*.yaml")):
        golden = yaml.safe_load(path.read_text(encoding="utf-8"))
        if golden.get("retired") is None:
            goldens.append((golden["id"], words(golden["question"])))
    for document in documents(root):
        rel = document.relative_to(root).as_posix()
        text = document.read_text(encoding="utf-8", errors="replace")
        body = words(text)
        for golden_id, question in goldens:
            if (run := longest_shared_run(question, body)) >= BOUND:
                errors.append(f"{rel}: shares {run} words in a row with {golden_id}'s question (the bound is {BOUND})")
        if rows := sorted(set(ROW_ID.findall(text))):
            errors.append(f"{rel}: names rights-table rows {', '.join(rows)}; a corpus document never names a row")
    return errors
