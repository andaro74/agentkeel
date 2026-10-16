"""The platform check's reading of who may call an agent: `callers` (SPEC/10 §2, §6; seed S2; F10.4).

An agent's manifest says who may call it, even if nobody: `callers` is a list
of `{subject, issuer}` entries, `[]` the default. The schema admits the key
as optional (`src/manifest/schema.json`), so a manifest with no key fails
here, for its named reader, and not for the schema (tool-owner note 2 on M10
PR 1). What this refuses, each naming the field:

- no `callers` key, or one that is not a list;
- an entry that is not a mapping of exactly `subject` and `issuer`;
- a `subject` that is not a name (`^[a-z][a-z0-9-]{2,30}$`), or is
  `platform`, which the construct reserves for the platform's own goldens
  caller (SPEC/10 §2; tool-owner F2);
- an `issuer` that is not the symbol `self`, the agent's own pool at M10;
- two entries with one `subject`.

It reads the manifest it is given and nothing else: no pool, no door, no
record. Whether a subject is admitted at a call is the door's (the
construct's authoriser) and is read from the call record by
`src/verdict/caller.py`. A subject added here is two keys
(`src/gates/two_key.py` entry 7, ADR-0016); this check counts no keys.
"""

from __future__ import annotations

import re
from typing import Any

FIELD = "callers"
SUBJECT = re.compile(r"^[a-z][a-z0-9-]{2,30}$")
RESERVED = "platform"
ISSUERS = ("self",)
KEYS = ("subject", "issuer")


def callers_errors(manifest: Any) -> list[str]:
    """Every way the manifest's `callers` differs from SPEC/10 §2's shape; empty means it says who may call."""
    if not isinstance(manifest, dict):
        return [f"{FIELD}: the manifest is not a mapping, so it cannot say who may call"]
    if FIELD not in manifest:
        return [f"{FIELD}: missing; an agent's manifest says who may call it, even if nobody (`{FIELD}: []`)"]
    callers = manifest[FIELD]
    if not isinstance(callers, list):
        return [f"{FIELD}: not a list of {{subject, issuer}} entries ({type(callers).__name__})"]
    errors: list[str] = []
    seen: dict[str, int] = {}
    for index, entry in enumerate(callers):
        at = f"{FIELD}[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{at}: not a mapping of subject and issuer")
            continue
        if extra := sorted(set(entry) - set(KEYS)):
            errors.append(f"{at}: unknown key(s) {extra}; an entry is subject and issuer only")
        for key in KEYS:
            if key not in entry:
                errors.append(f"{at}: no {key}")
        subject, issuer = entry.get("subject"), entry.get("issuer")
        if "subject" in entry:
            if not isinstance(subject, str) or not SUBJECT.match(subject):
                errors.append(f"{at}: subject {subject!r} is not a name (^[a-z][a-z0-9-]{{2,30}}$)")
            elif subject == RESERVED:
                errors.append(f"{at}: subject {RESERVED!r} is reserved for the platform's own goldens caller, which the "
                              "construct admits and the manifest cannot list")  # fmt: skip
            else:
                if subject in seen:
                    errors.append(f"{at}: subject {subject!r} is already {FIELD}[{seen[subject]}]'s; one entry per subject")
                seen.setdefault(subject, index)
        if "issuer" in entry and issuer not in ISSUERS:
            errors.append(f"{at}: issuer {issuer!r} is not {ISSUERS[0]!r} (the agent's own pool, the one issuer at M10)")
    return errors
