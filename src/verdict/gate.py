"""verdict.gate: the only reader that rules on an envelope (P5).

    python -m src.verdict.gate ENVELOPE      exit 0 GREEN, 1 RED or UNMEASURED, 2 REJECTED
    python -m src.verdict.gate --plants      make plants

The gate does not trust the writer. It rejects an envelope that does not
validate, or whose baseline card is missing, altered or for another commit;
a hand-written envelope gets no pass for being hand-written (F0.2). Then it
works the lists out again from `goldens` and history and goes RED where the
envelope disagrees with itself or with the gate.

What it rules on (SPEC/00 §5 `regression`, P7, R2): RED on a golden that
has ever passed and now fails, on plants_expected != plants_fired, or on a
failed check. A golden that has never passed reports and does not gate.

What it cannot see: a hand-written envelope that validates, points at a
real card and agrees with itself. Nothing signs an envelope yet.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.verdict import (
    ROOT,
    canonical_sha256,
    load_golden_kinds,
    plants,
    replay_history,
    schema_errors,
)

__all__ = ["Rejected", "judge", "measured", "measured_at", "read", "rule", "schema_errors"]

GOLDENS = ROOT / "evals" / "goldens" / "v1"
HISTORY = ROOT / "evals" / "history"


class Rejected(Exception):
    """Not an envelope the gate will rule on."""


def read(path: Path, root: Path = ROOT) -> dict[str, Any]:
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Rejected(f"{path}: unreadable: {exc}") from exc
    if errors := schema_errors(envelope):
        raise Rejected(f"{path}: does not validate: " + "; ".join(errors))

    ref = envelope["baseline_card_ref"]
    card_path = Path(ref["path"]) if Path(ref["path"]).is_absolute() else root / ref["path"]
    try:
        card = json.loads(card_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Rejected(f"{path}: baseline_card_ref {ref['path']} does not resolve: {exc}") from exc
    if canonical_sha256(card) != ref["sha256"]:
        raise Rejected(f"{path}: baseline card {ref['path']} is not the one the envelope names")
    if card.get("commit") != envelope["commit"]:
        raise Rejected(f"{path}: baseline card is for {card.get('commit')}, not {envelope['commit']}")
    # When the run is the baseline itself (M00), the envelope and its card
    # scored the same replies and must say the same thing.
    if card.get("model_id") == envelope["model_id"] and card.get("goldens") != envelope["goldens"]:
        raise Rejected(f"{path}: per-golden results differ from the baseline card for the same run")
    return envelope


def judge(
    envelope: dict[str, Any],
    kinds: dict[str, str],
    history: replay_history.History,
    plant_ids: list[str],
) -> tuple[str, list[str]]:
    """The gate's own verdict and its reasons. `envelope` has passed `read`."""
    results = envelope["goldens"]
    reasons: list[str] = []

    if {g: r["kind"] for g, r in results.items()} != kinds:
        reasons.append("the envelope's goldens are not the goldens in the tree")
    reasons += [f"{g}: pass is not score" for g, r in results.items() if r["pass"] != r["score"]]

    failing = [g for g in sorted(results) if not results[g]["pass"]]
    regressed = [g for g in failing if replay_history.ever_passed(history, g)]
    never_passed = [g for g in failing if g not in regressed]
    fired = sum(results[g]["pass"] for g in plant_ids if g in results)

    for name, mine in (("regressed", regressed), ("never_passed", never_passed)):
        if sorted(envelope[name]) != mine:
            reasons.append(f"envelope says {name}={sorted(envelope[name])}, the gate reads {mine}")
    if envelope["plants_expected"] != len(plant_ids):
        reasons.append(
            f"envelope says plants_expected={envelope['plants_expected']}, the plant rule gives {len(plant_ids)}"
        )
    if envelope["plants_fired"] != fired:
        reasons.append(f"envelope says plants_fired={envelope['plants_fired']}, the gate reads {fired}")

    reasons += [f"regressed: {g} has passed before and fails now" for g in regressed]
    if fired != len(plant_ids):
        reasons.append(f"silent plant: expected {len(plant_ids)}, fired {fired}")
    reasons += [
        f"check {name} failed: {check['url']}"
        for name, check in sorted(envelope["checks"].items())
        if check["status"] == "fail"
    ]

    if envelope["verdict"] == "UNMEASURED":
        return "UNMEASURED", reasons + ["the run did not measure: a call failed"]
    verdict = "RED" if reasons else "GREEN"
    if envelope["verdict"] != verdict:
        reasons.append(f"build said {envelope['verdict']}, the gate says {verdict}")
        verdict = "RED"
    return verdict, reasons


def measured(envelope: dict[str, Any], verdict: str) -> str:
    """The ledger's Measured cell. `verdict` is the gate's own (`rule`), never the envelope's."""
    results = envelope["goldens"]

    def tally(kind: str) -> str:
        of_kind = [r for r in results.values() if r["kind"] == kind]
        return f"{sum(r['pass'] for r in of_kind)}/{len(of_kind)}"

    traps = sorted(g for g, r in results.items() if r["kind"] == "trap" and r["pass"])
    parts = [
        f"traps {tally('trap')}" + (f" ({', '.join(traps)})" if traps else ""),
        f"ordinary {tally('ordinary')}",
        f"guardrail {tally('guardrail')}",
        f"never_passed {len(envelope['never_passed'])}",
        f"regressed {len(envelope['regressed'])}",
        f"plants {envelope['plants_fired']}/{envelope['plants_expected']}",
        *(f"{name} {c['status']} {c['url']}" for name, c in sorted(envelope["checks"].items())),
        verdict,
        f"envelope `{envelope['commit']}`",
    ]
    return "; ".join(parts)


def latest(history_dir: Path = HISTORY) -> Path | None:
    """The envelope for the nearest commit at or behind HEAD."""
    have = {p.stem: p for p in replay_history.envelope_paths(history_dir)}
    commits = subprocess.run(
        ["git", "rev-list", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    return next((have[c] for c in commits if c in have), None)


def rule(path: Path, history_dir: Path = HISTORY) -> tuple[str, list[str]]:
    envelope = read(path)
    try:
        history = replay_history.load(history_dir, exclude_commit=envelope["commit"])
    except ValueError as exc:  # a bad file in history: the gate cannot rule, which is not RED
        raise Rejected(f"history cannot be replayed: {exc}") from exc
    kinds = load_golden_kinds(GOLDENS)
    return judge(envelope, kinds, history, plants.plant_ids(kinds, ROOT))


def measured_at(path: Path, history_dir: Path = HISTORY) -> str:
    """What `make ledger` holds a Measured cell to: the envelope's numbers under the gate's verdict."""
    verdict, _ = rule(path, history_dir)
    return measured(read(path), verdict)


def print_plants() -> int:
    kinds = load_golden_kinds(GOLDENS)
    plant_ids = plants.plant_ids(kinds, ROOT)
    path = latest()
    try:
        results = read(path)["goldens"] if path else {}
    except Rejected as rejection:
        print(f"REJECTED {rejection}")
        return 2
    print(f"plants_expected = {len(plant_ids)}")
    for g in plant_ids:
        fired = {True: "fired", False: "SILENT", None: "not run"}[results.get(g, {}).get("pass")]
        print(f"  {g} {kinds[g]:<9} {fired}")
    waiting = sorted(g for g, k in kinds.items() if k in ("guardrail", "redteam") and g not in plant_ids)
    if waiting:
        print("not plants until their enforcing control is in the repo (SPEC/00 section 5):")
        print("  " + " ".join(waiting))
    print(f"last run: {path.relative_to(ROOT).as_posix() if path else 'no CI-written envelope yet'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("envelope", nargs="?", type=Path)
    parser.add_argument("--history-dir", type=Path, default=HISTORY)
    parser.add_argument("--plants", action="store_true")
    args = parser.parse_args(argv)
    if args.plants:
        return print_plants()
    if args.envelope is None:
        parser.error("an envelope path, or --plants")
    try:
        verdict, reasons = rule(args.envelope, args.history_dir)
    except Rejected as rejection:
        print(f"REJECTED {rejection}")
        return 2
    print(f"{verdict} {args.envelope}")
    for reason in reasons:
        print(f"  {reason}")
    return 0 if verdict == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
