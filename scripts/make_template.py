"""Write the template repository's files from refagent, at this commit (SPEC/06 section 2, section 6).

    python scripts/make_template.py --out DIR [--name example-agent]

The template's source lives in the template repository only (finding 16 on
M06 PR 1); this is what makes it, so that what the owner pushes there is
refagent as it stands on `agentkeel`'s `main`, reproducibly, and not a copy
edited by hand. It writes, at DIR's root, the agent folder as an agent
repository holds it:

- `manifest.yaml`: refagent's, renamed, **every seat null**, the
  platform's guardrail pinned (SPEC/06 section 6, item 6), no edges, and
  none of refagent's swap pins; `platform_version` is the milestone tag
  HEAD carries, else the short commit (M07 PR 2: it was the literal "m06");
- `agent.py`, `server.py`, `__init__.py`, `prompt.txt`, `tools/`: refagent's
  code, with the one change the platform's image needs: the server imports
  its agent module relatively (`infra/construct/agent.Dockerfile` copies the
  folder into the package `agent`);
- `data/table.json` and `data/clauses.json`: refagent's rights table and
  clause index, as the example agent's own data (R5);
- `goldens/`: **empty**. An agent repository's first pull request without
  goldens is refused (S1b's reader);
- `README.md`: Product's, from `docs/developer/template-README.md`.

No workflow: the platform check is `agentkeel`'s (R2), and nothing in an
agent repository asks for it. Prints the commit it was made from.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REFAGENT = ROOT / "agents" / "refagent"
SEATS = ("product", "rule-owner", "data-owner", "tool-owner", "threshold-owner", "security", "engineering")
KEPT = ("model", "judge_model_id", "guardrail", "endpoint_allowlist", "ceilings", "max_tokens_per_session",
        "daily_usd", "memory", "data_class", "deprecated_after", "rollout")  # fmt: skip
OWN_IMPORT = "from agents.refagent import agent"


MILESTONE_TAG = re.compile(r"^m[0-9]{2}$")


def platform_version(root: Path = ROOT) -> str:
    """The platform's version: the milestone tag HEAD carries, else the short commit (SPEC/07 section 2).

    Until M07 PR 2 this was the literal "m06", whatever commit the template was made from, and nothing
    read it. `scripts/platform_upgrade.py` reads it now: an agent is behind when the commit its version
    names is an ancestor of the template's."""
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout.strip()

    tags = sorted(tag for tag in git("tag", "--points-at", "HEAD").split() if MILESTONE_TAG.match(tag))
    return tags[-1] if tags else git("rev-parse", "--short=12", "HEAD")


def manifest(name: str, version: str | None = None) -> str:
    source = yaml.safe_load((REFAGENT / "manifest.yaml").read_text(encoding="utf-8"))
    doc = {"name": name, "version": "1.0.0", **{k: source[k] for k in KEPT},
           "seats": {seat: None for seat in SEATS}, "may_call": [], "may_be_called_by": [],
           "platform_version": version or platform_version()}  # fmt: skip
    # The template is never made retired, whatever refagent's manifest says.
    doc["rollout"] = "all-at-once"
    head = (
        "# Your agent's manifest (docs/developer/quickstart.md in agentkeel).\n"
        "# Every seat is a GitHub login with access to this repository; the platform\n"
        "# check refuses a pull request while any is null. The guardrail is the\n"
        "# platform's: an agent from the template pins it as given (M06).\n"
    )
    return head + yaml.safe_dump(doc, sort_keys=False)


def write(out: Path, name: str) -> str:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                            check=True).stdout.strip()  # fmt: skip
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} is not empty")
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.yaml").write_text(manifest(name), encoding="utf-8", newline="\n")
    for file in ("__init__.py", "agent.py", "prompt.txt"):
        shutil.copyfile(REFAGENT / file, out / file)
    server = (REFAGENT / "server.py").read_text(encoding="utf-8")
    if server.count(OWN_IMPORT) != 1:
        raise SystemExit(f"agents/refagent/server.py no longer imports {OWN_IMPORT!r} once; the template needs it")
    (out / "server.py").write_text(server.replace(OWN_IMPORT, "from . import agent"), encoding="utf-8", newline="\n")
    shutil.copytree(REFAGENT / "tools", out / "tools")
    (out / "data").mkdir()
    shutil.copyfile(ROOT / "data" / "rights_table.json", out / "data" / "table.json")
    shutil.copyfile(ROOT / "data" / "clause_index.json", out / "data" / "clauses.json")
    (out / "goldens").mkdir()
    (out / "goldens" / ".gitkeep").write_text("", encoding="utf-8")
    shutil.copyfile(ROOT / "docs" / "developer" / "template-README.md", out / "README.md")
    (out / ".template-source.json").write_text(json.dumps({"agentkeel_commit": commit}, indent=2) + "\n",
                                               encoding="utf-8", newline="\n")  # fmt: skip
    return commit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--name", default="example-agent")
    args = parser.parse_args(argv)
    commit = write(args.out, args.name)
    print(f"wrote the template's files to {args.out} from agentkeel {commit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
