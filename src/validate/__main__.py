from __future__ import annotations

import sys
from pathlib import Path

from src.validate.checks import CHECKS

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    failed = 0
    for name, check in CHECKS.items():
        errors = check(ROOT)
        print(f"{'FAIL' if errors else 'ok  '} {name}")
        for error in errors:
            print(f"     {error}")
        failed += bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
