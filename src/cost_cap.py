"""cost-cap (SPEC/00 §5): the run's token spend against the cap in thresholds.yaml.

    python -m src.cost_cap --raw RAW

Reads the runner's raw observations, not the envelope. Runs before
verdict.build, so a run over the cap writes no envelope.

It reads the spend after it is spent. It bounds the next run, not this one.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def tokens_spent(raw: dict) -> int:
    spent = 0
    for observation in raw["observations"]:
        usage = observation.get("usage", {})
        spent += usage.get("totalTokens", usage.get("inputTokens", 0) + usage.get("outputTokens", 0))
    return spent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--thresholds", type=Path, default=ROOT / "thresholds.yaml")
    args = parser.parse_args(argv)

    thresholds = yaml.safe_load(args.thresholds.read_text(encoding="utf-8"))
    cap = thresholds["cost_cap"]["tokens_per_run"]  # no cap is an error, not a pass
    if not isinstance(cap, int) or isinstance(cap, bool) or cap <= 0:
        print(f"FAIL cost-cap: tokens_per_run must be a positive integer, got {cap!r}")
        return 1
    spent = tokens_spent(json.loads(args.raw.read_text(encoding="utf-8")))
    over = spent > cap
    print(f"{'FAIL' if over else 'ok  '} cost-cap: {spent:,} tokens this run, cap {cap:,}")
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
