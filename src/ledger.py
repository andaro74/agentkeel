"""`make ledger`: print the ledger and hold its Measured cells to the envelopes.

    python -m src.ledger            make ledger: print; exit 1 if a Measured cell differs from its envelope
    python -m src.ledger --plain    make ledger-plain: also write docs/milestones/README.md

A Measured cell is written by Product in the close PR, copied from the
CI-written envelope (ruling on report 4.2). This does not write the cell.
It reads the cell, finds the envelope the cell names, asks verdict.gate to
rule on it, and fails if the cell differs from the envelope's numbers under
the gate's verdict. It also fails a GREEN State over an empty cell, and a
State that is not the cell's verdict. It reads no envelope itself; gate does.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from src.verdict import gate

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "milestones" / "README.md"
SPEC = ROOT / "SPEC" / "00-overview.md"
PLAIN = ROOT / "docs" / "milestones" / "README.md"

UNMEASURED = "—"
CITES = re.compile(r"envelope `([0-9a-f]{40})`")
CELL_BREAK = re.compile(r"(?<!\\)\|")


def table_after(text: str, heading: str) -> list[dict[str, str]]:
    """The first markdown table after `heading`, as one dict per row."""
    lines = text.split(heading, 1)[1].splitlines()
    table = []
    for line in lines[1:]:
        if line.startswith("|"):
            table.append([cell.strip() for cell in CELL_BREAK.split(line.strip())[1:-1]])
        elif table:
            break
    header, _rule, *rows = table
    return [dict(zip(header, row, strict=True)) for row in rows]


def rows() -> list[dict[str, str]]:
    return table_after(LEDGER.read_text(encoding="utf-8"), "## Rows")


def check_measured(row: dict[str, str], history_dir: Path) -> str | None:
    """None if the cell is empty or equals what its envelope measured; else what is wrong."""
    cell, state = row["Measured"], row["State"]
    if cell == UNMEASURED:
        # SPEC/00 section 7: a milestone that closes without a measurement is RED, never GREEN.
        return f"row {row['#']}: State {state} with no measurement" if state == "GREEN" else None
    cited = CITES.search(cell)
    if not cited:
        return f"row {row['#']}: Measured names no envelope"
    try:
        expected = gate.measured_at(history_dir / f"{cited[1]}.json", history_dir)
    except gate.Rejected as rejection:
        return f"row {row['#']}: {rejection}"
    if cell != expected:
        return f"row {row['#']}: Measured differs from the envelope.\n  ledger:   {cell}\n  envelope: {expected}"
    if state in ("GREEN", "RED") and f"; {state}; " not in cell:
        return f"row {row['#']}: State {state} is not the verdict in the Measured cell"
    return None


def plain(ledger_rows: list[dict[str, str]]) -> str:
    sentences = _sentences()
    out = [
        "# Milestones",
        "",
        "Generated from `milestones/README.md` by `make ledger-plain`. Do not edit.",
        "",
        "| Milestone | In plain words | Result | Video |",
        "|---|---|---|---|",
    ]
    for row in ledger_rows:
        m = row["M"]
        title, sentence = sentences[m]
        name = f"{m} — {title}"
        if (PLAIN.parent / f"{m}.md").exists():
            name = f"[{name}]({m}.md)"
        video = ROOT / "docs" / "video" / "milestones" / f"{m}.mp4"
        watch = f"[watch](../video/milestones/{m}.mp4)" if video.exists() else "not recorded"
        out.append(f"| {name} | {sentence} | {row['State']} | {watch} |")
    return "\n".join(out) + "\n"


def _sentences() -> dict[str, tuple[str, str]]:
    """MNN -> (explainer title, plain sentence), from the SPEC/00 §10.3 table."""
    text = SPEC.read_text(encoding="utf-8")
    start = text.index("| M | Explainer title | The plain sentence |")
    found = {}
    for line in text[start:].splitlines()[2:]:
        if not line.startswith("|"):
            break
        number, title, sentence = (c.strip() for c in CELL_BREAK.split(line.strip())[1:-1])
        found[f"M{number}"] = (title, sentence)
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plain", action="store_true")
    parser.add_argument("--history-dir", type=Path, default=gate.HISTORY)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")  # the ledger has an em dash; a Windows console does not

    ledger_rows = rows()
    problems = []
    for row in ledger_rows:
        print(f"{row['#']} {row['M']} {row['State']:<6} {row['PRs used / cap']:<6} {row['Claim']}")
        print(f"    measured: {row['Measured']}")
        if problem := check_measured(row, args.history_dir):
            problems.append(problem)

    if path := gate.latest(args.history_dir):
        try:
            print(f"\nlatest CI-written envelope reads:\n    {gate.measured_at(path, args.history_dir)}")
        except gate.Rejected as rejection:
            problems.append(str(rejection))
    else:
        print("\nno CI-written envelope in evals/history/ yet")

    if args.plain:
        PLAIN.parent.mkdir(parents=True, exist_ok=True)
        PLAIN.write_text(plain(ledger_rows), encoding="utf-8", newline="\n")
        print(f"wrote {PLAIN.relative_to(ROOT).as_posix()}")

    for problem in problems:
        print(f"FAIL {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
