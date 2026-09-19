"""cost-cap (SPEC/00 §5): the run's token spend against the cap in thresholds.yaml.

    python -m src.cost_cap --raw RAW [--raw RAW ...]

Reads the runners' raw observations, not the envelope, and prints what the
run spent against the cap. From M01 an over-cap run is a recorded RED, not
a missing file (Threshold Owner, M01 item 22): this prints the spend and
exits 0, and verdict.build writes the envelope RED, which verdict.gate works
out again. A run always writes an envelope, the agent's or, when no agent
ran, the control's. It exits 1 only when it cannot count: no cap, or a
reply with no usage.

It reads the spend after it is spent, and only the spend the runner wrote
down. It does not stop this run or the next one.
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
        if "error" in observation:  # the call failed; the runner saw no bill
            continue
        usage = observation.get("usage")
        if not usage:
            raise ValueError(f"{observation.get('id')}: a reply with no usage cannot be counted")
        # in plus out, as verdict.build counts it: one count in both readers
        spent += usage.get("inputTokens", 0) + usage.get("outputTokens", 0)
    return spent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", required=True, type=Path, action="append")
    parser.add_argument("--thresholds", type=Path, default=ROOT / "thresholds.yaml")
    args = parser.parse_args(argv)

    thresholds = yaml.safe_load(args.thresholds.read_text(encoding="utf-8"))
    cap = thresholds["cost_cap"]["tokens_per_run"]  # no cap is an error, not a pass
    if not isinstance(cap, int) or isinstance(cap, bool) or cap <= 0:
        print(f"FAIL cost-cap: tokens_per_run must be a positive integer, got {cap!r}")
        return 1
    try:
        spent = sum(tokens_spent(json.loads(raw.read_text(encoding="utf-8"))) for raw in args.raw)
    except ValueError as exc:
        print(f"FAIL cost-cap: {exc}")
        return 1
    over = spent > cap
    print(f"{'OVER' if over else 'ok  '} cost-cap: {spent:,} tokens this run, cap {cap:,}"
          + ("; the envelope is RED (M01 item 22)" if over else ""))  # fmt: skip
    return 0


if __name__ == "__main__":
    sys.exit(main())
