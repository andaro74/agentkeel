"""Seed the fictional slate (SPEC/00 §9, ADR-0001 amendment 1 items 7 and 8).

Writes data/slate.json, data/rights_table.json and data/clause_index.json.
Everything here is invented: no real title, person, contract or studio
workflow. The output is deterministic; running this twice changes nothing.

M01 loads DynamoDB from the first two files. The baseline reads none of them.
"""

from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

PLATFORMS = ["THEATRICAL", "PVOD", "SVOD", "AVOD"]

# Reference time zone per territory; embargo_lift_local is read in it (EM-2).
TERRITORIES = {
    "AU": "Australia/Sydney",
    "BR": "America/Sao_Paulo",
    "DE": "Europe/Berlin",
    "FR": "Europe/Paris",
    "GB": "Europe/London",
    "JP": "Asia/Tokyo",
    "US": "America/New_York",
}

# fmt: off
# title_id, title, year, kind, franchise, sequel_of, note
TITLES = [
    ("t-001", "Quorum of Kites", 2024, "feature", "kites", None, None),
    ("t-002", "Quorum of Kites: Second Wind", 2026, "feature", "kites", "t-001", None),
    ("t-003", "Brackenfield Nine", 2023, "feature", "brackenfield", None, None),
    ("t-004", "Brackenfield Nine: The Tenth", 2027, "feature", "brackenfield", "t-003", None),
    ("t-005", "Pim and the Paper Whale", 2025, "animated_family", None, None, None),
    ("t-006", "The Ninth Aquifer", 2027, "tentpole", None, None, "unreleased; under embargo"),
    ("t-007", "Summer at Dunmore Pier", 1987, "library", None, None, "music clearances expired in some territories"),
    ("t-008", "A Ledger of Small Mercies", 2025, "feature", None, None, None),
    ("t-009", "Turnstile Saints", 2026, "feature", None, None, None),
    ("t-010", "Algebra for Apiarists", 2024, "feature", None, None, None),
    ("t-011", "Nightbus to Varnholt", 2026, "feature", None, None, None),
    ("t-012", "Tin Orchard", 2022, "feature", None, None, None),
]

EMBARGO = "2027-05-14T00:00:00"

# table_row, title_id, territory, platform, window_start, window_end,
# exclusive, holdback_until, clearance_expiry, embargo_lift_local
ROWS = [
    ("r-001", "t-001", "US", "SVOD", "2025-03-01", "2028-02-29", True, None, None, None),
    ("r-002", "t-001", "GB", "SVOD", "2025-03-01", "2028-02-29", True, None, None, None),
    ("r-003", "t-001", "DE", "SVOD", "2025-06-01", "2027-05-31", False, None, None, None),
    ("r-004", "t-001", "FR", "SVOD", "2025-06-01", "2028-05-31", True, None, None, None),
    ("r-005", "t-001", "JP", "AVOD", "2026-01-01", "2027-12-31", False, None, None, None),
    ("r-006", "t-002", "US", "THEATRICAL", "2026-11-20", "2027-02-18", True, None, None, None),
    ("r-007", "t-002", "US", "PVOD", "2026-12-15", "2027-06-30", True, "2027-01-04", None, None),
    ("r-008", "t-002", "DE", "THEATRICAL", "2026-12-03", "2027-03-03", True, None, None, None),
    ("r-009", "t-002", "DE", "PVOD", "2027-01-15", "2027-07-31", True, "2027-02-01", None, None),
    ("r-010", "t-002", "FR", "SVOD", "2028-01-01", "2030-12-31", True, None, None, None),
    ("r-011", "t-003", "US", "SVOD", "2024-02-01", "2027-01-31", True, None, None, None),
    ("r-012", "t-003", "GB", "SVOD", "2024-02-01", "2027-01-31", False, None, None, None),
    ("r-013", "t-003", "AU", "AVOD", "2025-07-01", "2027-06-30", False, None, None, None),
    ("r-014", "t-003", "BR", "SVOD", "2024-09-01", "2026-08-31", True, None, None, None),
    ("r-015", "t-004", "US", "THEATRICAL", "2027-03-19", "2027-06-17", True, None, None, None),
    ("r-016", "t-004", "US", "PVOD", "2027-04-15", "2027-10-31", True, "2027-05-03", None, None),
    ("r-017", "t-004", "GB", "THEATRICAL", "2027-03-26", "2027-06-24", True, None, None, None),
    ("r-018", "t-004", "GB", "PVOD", "2027-04-22", "2027-11-30", True, "2027-05-10", None, None),
    ("r-019", "t-005", "US", "SVOD", "2025-11-01", "2028-10-31", True, None, None, None),
    ("r-020", "t-005", "GB", "SVOD", "2025-11-01", "2028-10-31", True, None, None, None),
    ("r-021", "t-005", "DE", "SVOD", "2026-01-15", "2028-01-14", False, None, None, None),
    ("r-022", "t-005", "JP", "SVOD", "2026-04-01", "2028-03-31", True, None, None, None),
    ("r-023", "t-005", "BR", "AVOD", "2026-06-01", "2027-05-31", False, None, None, None),
    ("r-024", "t-006", "US", "THEATRICAL", "2027-05-01", "2027-08-12", True, None, None, EMBARGO),
    ("r-025", "t-006", "GB", "THEATRICAL", "2027-05-01", "2027-08-12", True, None, None, EMBARGO),
    ("r-026", "t-006", "JP", "THEATRICAL", "2027-05-01", "2027-08-12", True, None, None, EMBARGO),
    ("r-027", "t-006", "BR", "THEATRICAL", "2027-05-01", "2027-08-12", True, None, None, EMBARGO),
    ("r-028", "t-006", "US", "PVOD", "2027-06-20", "2027-12-31", True, "2027-07-05", None, EMBARGO),
    ("r-029", "t-007", "US", "SVOD", "2020-01-01", "2029-12-31", False, None, "2026-06-30", None),
    ("r-030", "t-007", "GB", "SVOD", "2020-01-01", "2029-12-31", False, None, "2026-06-30", None),
    ("r-031", "t-007", "AU", "AVOD", "2021-01-01", "2028-12-31", False, None, "2027-12-31", None),
    ("r-032", "t-008", "US", "SVOD", "2026-02-01", "2029-01-31", True, None, None, None),
    ("r-033", "t-008", "FR", "SVOD", "2026-05-01", "2028-04-30", False, None, None, None),
    ("r-034", "t-009", "US", "PVOD", "2026-09-14", "2027-04-04", True, "2026-10-05", None, None),
    ("r-035", "t-009", "DE", "SVOD", "2027-02-01", "2029-01-31", True, None, None, None),
    ("r-036", "t-010", "GB", "AVOD", "2025-01-01", "2026-12-31", False, None, None, None),
    ("r-037", "t-010", "JP", "SVOD", "2025-04-01", "2027-03-31", True, None, None, None),
    ("r-038", "t-011", "US", "SVOD", "2026-12-01", "2029-11-30", True, None, None, None),
    ("r-039", "t-011", "BR", "SVOD", "2027-01-15", "2029-01-14", False, None, None, None),
    ("r-040", "t-012", "DE", "AVOD", "2024-01-01", "2027-12-31", False, None, None, None),
]

ROW_FIELDS = [
    "table_row", "title_id", "territory", "platform", "window_start", "window_end",
    "exclusive", "holdback_until", "clearance_expiry", "embargo_lift_local",
]

# clause_id -> one-line description. The documents themselves are M01
# (data/corpus/, Data Owner). ML master license, AM1 amendment 1, HS holdback
# schedule, MC music-clearance sheet, EM embargo memo, RL ratings letter.
CLAUSES = {
    "ML-2.1": "Grant of rights: a title may be published only in the territories and on the platforms listed for it in the rights schedule.",
    "ML-2.3": "Sequels, prequels and spin-offs are separate titles; a grant for one title conveys no rights in another.",
    "ML-3.1": "Licence term: a title may be published only from its window start to its window end, inclusive.",
    "ML-5.2": "Exclusivity is per title, territory and platform as scheduled; a non-exclusive grant permits publication and supports no exclusivity claim.",
    "ML-12.3": "Notices: contact details for talent representatives; confidential and not to be disclosed.",
    "ML-14.1": "Confidentiality: deal terms are not disclosed to any third party.",
    "AM1-2": "Amendment 1: revised theatrical dates for the listed titles; every other scheduled date is unchanged.",
    "HS-2": "Holdback: PVOD may not begin before the holdback date listed for the title and territory.",
    "HS-4": "Holdback dates are fixed calendar dates; a change to a theatrical date does not move them unless amended in writing.",
    "MC-3": "Music clearances: a title may not be published in a territory after its clearance expiry until the clearances are renewed.",
    "MC-4": "Music clearances are per territory; expiry in one territory does not affect another.",
    "EM-1": "Embargo: no plot, synopsis or story detail of the embargoed title is released before the embargo lifts.",
    "EM-2": "The embargo lifts at 00:00 local time in each territory's reference time zone, not UTC.",
    "RL-1": "Ratings: publication in a territory requires the version rated for that territory, with any required cuts.",
}
# fmt: on


def build() -> dict[str, object]:
    titles = [
        {
            "title_id": i,
            "title": t,
            "year": y,
            "kind": k,
            "franchise": f,
            "sequel_of": s,
            "note": n,
        }
        for i, t, y, k, f, s, n in TITLES
    ]
    rows = [dict(zip(ROW_FIELDS, r, strict=True)) for r in ROWS]

    title_ids = {t["title_id"] for t in titles}
    assert len(title_ids) == len(titles) == 12
    assert len({r["table_row"] for r in rows}) == len(rows)
    for r in rows:
        assert r["title_id"] in title_ids, r
        assert r["territory"] in TERRITORIES, r
        assert r["platform"] in PLATFORMS, r
        assert r["window_start"] <= r["window_end"], r

    slate = {
        "fictional": True,
        "titles": titles,
        "territories": {k: {"reference_tz": v} for k, v in sorted(TERRITORIES.items())},
        "platforms": PLATFORMS,
    }
    return {
        "slate.json": slate,
        "rights_table.json": rows,
        "clause_index.json": CLAUSES,
    }


def main() -> None:
    DATA.mkdir(exist_ok=True)
    for name, content in build().items():
        path = DATA / name
        path.write_text(
            json.dumps(content, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote {path.relative_to(DATA.parent).as_posix()}")


if __name__ == "__main__":
    main()
