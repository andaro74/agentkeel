"""M05's seeded cases S1-S7 (SPEC/05 §5), committed before the code that reads them.

Two kinds. **Attempt seeds** (S1, S2, S3, S6, S7) are run files under
`milestones/M05/runs/`, each the attempt to make with `observed: null`, M01
S4's and S6's pattern: the test reads the file as the human filled it and
asserts every attempt was made and refused. It fails until the attempt is
made, after its control is deployed (SPEC/05 §5.1: S1, S2 and S6 during PR 2,
S3 and S7 after PR 2's merge deploy). What records an attempt is
`scripts/observe_containment.py`'s lookup in the audit bucket, not this test
(SPEC/05 §4): these tests are the test-only witnesses `F5_*` is built from.
**Code seeds** (S4, S5) are fixtures under `tests/fixtures/m05/`; each test
asks the reader to refuse its fixture and asserts the planted reason.

Each is marked `xfail(strict=True, raises=...)` with the one exception class
its planted reason raises, so an exception of any other class (a moved
fixture, a run file that no longer parses) is a failure, not an expected
one. Preconditions raise `SeedBroken`. Each was run once with `--runxfail`
and its message read, and the marker comes off in the commit that lands the
reader (or records the attempt). Nothing here calls AWS or a model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from src.verdict import ROOT

RUNS = ROOT / "milestones" / "M05" / "runs"
FIXTURES = Path(__file__).parent / "fixtures" / "m05"


class SeedBroken(Exception):
    """A seed's own precondition failed. Not AssertionError, which the strict markers expect of the
    planted failure: a broken seed must fail the run, not pass as an expected one (M04's rule)."""


def holds(condition: bool, message: str) -> None:
    if not condition:
        raise SeedBroken(message)


def run_file(name: str, seed: str) -> dict[str, Any]:
    run = yaml.safe_load((RUNS / name).read_text(encoding="utf-8"))
    holds(isinstance(run, dict) and run.get("seed") == seed, f"{name} is seed {seed}'s run file")
    holds(isinstance(run.get("attempts"), list) and run["attempts"], f"{name} names the attempts to make")
    holds(all(a.get("what") and a.get("refused_when") for a in run["attempts"]),
          f"{name}: every attempt says what it is and when it counts as refused")  # fmt: skip
    return run


def made(run: dict[str, Any]) -> list[dict[str, Any]]:
    """The observed entries, one per attempt: the planted failure is that there are none yet."""
    observed = run["observed"]
    assert observed is not None, f"seed {run['seed']}: the attempt has not been made"
    assert len(observed) == len(run["attempts"]), f"seed {run['seed']}: every attempt is made, not some"
    return observed


# --- S1: curl to the internet -------------------------------------------------


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="S1 is attempted during M05 PR 2 (SPEC/05 §5.1)")
def test_s1_curl_to_the_internet_was_refused():
    """From the platform VPC with refagent's security group, `curl https://example.com`. Held today
    (no internet gateway, no NAT, egress to the listed endpoints only); what is missing is its
    record in the security account (SPEC/05 §3.1, §3.6). Refused when curl cannot connect and the
    flow record reads REJECT."""
    run = run_file("f5_1_curl.yaml", "S1")
    observed = made(run)
    assert all(o.get("eni") and o.get("destination") and o.get("result") for o in observed), observed


# --- S2: a write to another agent's prefix ------------------------------------


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="S2 is attempted during M05 PR 2 (SPEC/05 §5.1)")
def test_s2_a_write_to_another_agents_prefix_was_refused():
    """As refagent's stand-in, `s3:PutObject` under `agents/ratings-helper/` in the audit bucket.
    The stand-in's own policy grants the write, so the refusal can only be the audit bucket's
    policy, which scopes each agent role to its own prefix (SPEC/05 §2, §5). Today there is no
    audit bucket and no prefix, own or another's (SPEC/05 §3.7)."""
    run = run_file("f5_2_prefix.yaml", "S2")
    observed = made(run)
    assert all(o.get("result") == "AccessDenied" and o.get("request_id") for o in observed), observed
