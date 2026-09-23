"""src/gates: what `ruling-cited` and `two-key` share (SPEC/02 §2, §6). Engineering.

Each gate is a function `refusal(tree, base, pr) -> str | None` and a command
that exits 1 on a refusal with every reason listed, never the first alone.
`.github/workflows/gates.yml` (Security) runs both on every pull request as
the required checks `ruling-cited` and `two-key`. Nothing here writes or
reads an envelope (P5).

What they share:

- **Two trees.** `base` is the PR's base ref, `tree` its merge ref. A tree
  is a directory that is a git checkout (the PR's, or a worktree with a seed
  applied by `tests/test_m02_seeds.py`) or a revision of this repository
  (the base sha CI passes). A checkout's file list includes untracked files
  that are not ignored, so a seed applied with `git apply` is seen; a file
  deleted on disk is absent whatever the index says.
- **The changed paths**: every path whose content differs between the two,
  added and deleted included, compared by git blob id so that line endings
  do not count (this repo is checked out CRLF on Windows).
- **The owner of a path**, from `.github/CODEOWNERS` **read from the base**
  (SPEC/02 §6): a PR cannot move a path to a seat whose ruling it carries.
  The seat is the `# seat: <Seat>` line above a block of owner lines; GitHub
  reads only the login. Last matching line wins, as GitHub resolves it. A
  manifest is one file with several owners (ADR-0003 amendment 1), so a
  change to it is attributed field by field (`MANIFEST_FIELD_SEATS`).
- **The rulings** in the PR's tree whose `pr:` is this PR's number. A ruling
  covers a path when its `seat:` is the path's owner and one of its
  `authorises:` globs matches the path; a ruling file with this PR's `pr:`
  covers itself (SPEC/02 §2, "Covers").
- **The bot exemption**: a path under `evals/history/**` whose every commit
  since the base is by `github-actions[bot]` is CI-written and needs no
  ruling; any other change there is a human commit, which `two-key` reads
  as a relaxation (SPEC/02 §2).
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from src.verdict import ROOT

CODEOWNERS = ".github/CODEOWNERS"
RULING_GLOB = re.compile(r"^milestones/[^/]+/rulings/[^/]+\.md$")
BOT = "github-actions[bot]"
HISTORY = "evals/history/"

# SPEC/00 §5's seven seats, as ruling files write them and as the subagent
# prompts' `seat:` front matter writes them. Both spellings are accepted;
# the display form is used in every message.
SEATS: dict[str, str] = {
    "Product": "product",
    "Rule Owner": "rule-owner",
    "Data Owner": "data-owner",
    "Tool Owner": "tool-owner",
    "Threshold Owner": "threshold-owner",
    "Security": "security",
    "Engineering": "engineering",
}

# A manifest's fields by owner (SPEC/00 §5, §6; ADR-0003 amendment 1; the
# comments in agents/refagent/manifest.yaml). Every other top-level key is
# the file's CODEOWNERS owner, Engineering.
MANIFEST_FIELD_SEATS: dict[str, str] = {
    "model": "Threshold Owner",
    "judge_model_id": "Threshold Owner",
    "max_tokens_per_session": "Threshold Owner",
    "daily_usd": "Threshold Owner",
    "pinned_roles": "Threshold Owner",
    "guardrail": "Rule Owner",
    "seats": "Security",
    "endpoint_allowlist": "Security",
    "may_call": "Tool Owner",
    "may_be_called_by": "Tool Owner",
    "ceilings": "Tool Owner",
    "version": "Tool Owner",
}
MANIFEST = re.compile(r"^agents/[^/]+/manifest\.yaml$")


def canonical_seat(name: Any) -> str | None:
    """`Threshold Owner`, `threshold-owner` and `threshold_owner` are one seat. None when it is not one."""
    if not isinstance(name, str):
        return None
    key = re.sub(r"[\s_]+", "-", name.strip().lower())
    return next((display for display, slug in SEATS.items() if slug == key), None)


# --- git --------------------------------------------------------------------


def git(cwd: Path, *args: str, binary: bool = False) -> Any:
    done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=True)
    return done.stdout if binary else done.stdout.decode("utf-8", errors="replace")


def blob_id(content: bytes) -> str:
    """git's id for these bytes with LF line endings: what the index holds for a text file."""
    content = content.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\0" % len(content) + content).hexdigest()


class Tree:
    """A checkout directory, or a revision of this repository. See the module docstring."""

    def __init__(self, spec: str | Path, repo: Path = ROOT) -> None:
        self.repo = repo
        candidate = Path(spec)
        if candidate.is_dir():
            self.dir: Path | None = candidate.resolve()
            self.rev = git(self.dir, "rev-parse", "HEAD").strip()
        else:
            self.dir = None
            self.rev = git(repo, "rev-parse", "--verify", f"{spec}^{{commit}}").strip()
        self._files: set[str] | None = None
        self._blobs: dict[str, str] = {}
        self._uncommitted: set[str] = set()

    @property
    def name(self) -> str:
        return self.dir.as_posix() if self.dir else self.rev[:12]

    def _load(self) -> None:
        if self._files is not None:
            return
        if self.dir is None:
            files = set()
            for entry in git(self.repo, "ls-tree", "-r", "-z", self.rev).split("\0"):
                if entry:
                    meta, path = entry.split("\t", 1)
                    files.add(path)
                    self._blobs[path] = meta.split()[2]
            self._files = files
            return
        tracked = {p for p in git(self.dir, "ls-files", "-z").split("\0") if p}
        others = {p for p in git(self.dir, "ls-files", "-z", "--others", "--exclude-standard").split("\0") if p}
        files = sorted(p for p in tracked | others if (self.dir / p).is_file())
        # Every file's blob id from its bytes on disk, with the attribute
        # filters `git add` would apply (CRLF to LF for text): one call, not
        # the index's stat cache, which misses a same-size edit made in the
        # same second as the checkout (the seeds are exactly that).
        done = subprocess.run(
            ["git", "hash-object", "--stdin-paths"], cwd=self.dir, capture_output=True, check=True,
            input="\n".join(files).encode("utf-8"),
        )  # fmt: skip
        self._blobs = dict(zip(files, done.stdout.decode("utf-8").split(), strict=True))
        head: dict[str, str] = {}
        for entry in git(self.dir, "ls-tree", "-r", "-z", "HEAD").split("\0"):
            if entry:
                meta, path = entry.split("\t", 1)
                head[path] = meta.split()[2]
        self._uncommitted = {p for p in files if head.get(p) != self._blobs[p]}
        self._files = set(files)

    def files(self) -> set[str]:
        self._load()
        return set(self._files or ())

    def read(self, path: str) -> bytes | None:
        self._load()
        if path not in (self._files or ()):
            return None
        if self.dir is not None:
            return (self.dir / path).read_bytes()
        return git(self.repo, "show", f"{self.rev}:{path}", binary=True)

    def text(self, path: str) -> str | None:
        raw = self.read(path)
        return None if raw is None else raw.decode("utf-8", errors="replace")

    def blob(self, path: str) -> str | None:
        self._load()
        if path not in (self._files or ()):
            return None
        if path not in self._blobs:
            self._blobs[path] = blob_id(self.read(path) or b"")
        return self._blobs[path]

    def uncommitted(self, path: str) -> bool:
        self._load()
        return path in self._uncommitted


def changed(base: Tree, tree: Tree) -> list[str]:
    """Every path whose content differs between the two trees, added and deleted included."""
    return sorted(p for p in base.files() | tree.files() if base.blob(p) != tree.blob(p))


def bot_only(tree: Tree, base: Tree, path: str) -> bool:
    """Every commit touching `path` since the base is the bot's, and the checkout matches its HEAD."""
    if tree.uncommitted(path):
        return False
    authors = git(tree.dir or tree.repo, "log", "--format=%an", f"{base.rev}..{tree.rev}", "--", path).split("\n")
    authors = [a for a in authors if a]
    return bool(authors) and all(a == BOT for a in authors)


# --- CODEOWNERS -------------------------------------------------------------


@dataclass(frozen=True)
class OwnerLine:
    number: int
    pattern: str
    seat: str
    logins: tuple[str, ...]
    regex: re.Pattern[str]


def pattern_regex(pattern: str, *, anchored: bool) -> re.Pattern[str]:
    """A CODEOWNERS or `authorises:` glob as a regex over a repo-relative posix path.

    `**` crosses directories, `*` and `?` do not. A pattern names a file or
    a directory; a directory pattern matches everything under it. A
    CODEOWNERS pattern with no slash matches that name anywhere (as
    GitHub reads it); `authorises:` globs are always from the root.
    """
    body = pattern.strip()
    from_root = anchored or body.startswith("/") or "/" in body.rstrip("/")
    body = body.strip("/")
    out = []
    i = 0
    while i < len(body):
        if body.startswith("**", i):
            out.append(".*")
            i += 2
        elif body[i] == "*":
            out.append("[^/]*")
            i += 1
        elif body[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(body[i]))
            i += 1
    prefix = "" if from_root else "(?:.*/)?"
    return re.compile(f"^{prefix}{''.join(out)}(?:/.*)?$")


class Owners:
    """The seat table: `.github/CODEOWNERS` with `# seat:` headers."""

    def __init__(self, lines: list[OwnerLine]) -> None:
        self.lines = lines

    @classmethod
    def parse(cls, text: str) -> Owners:
        seat: str | None = None
        lines: list[OwnerLine] = []
        for number, raw in enumerate(text.splitlines(), 1):
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                if match := re.match(r"^#\s*seat:\s*(.+?)\s*$", line):
                    seat = canonical_seat(match[1])
                    if seat is None:
                        raise ValueError(f"{CODEOWNERS}:{number}: {match[1]!r} is not a SPEC/00 section 5 seat")
                continue
            pattern, *logins = line.split()
            if seat is None:
                raise ValueError(f"{CODEOWNERS}:{number}: an owner line before any '# seat:' line")
            if not logins or not all(login.startswith("@") for login in logins):
                raise ValueError(f"{CODEOWNERS}:{number}: an owner line names logins as @login")
            lines.append(OwnerLine(number, pattern, seat, tuple(logins), pattern_regex(pattern, anchored=False)))
        if not lines:
            raise ValueError(f"{CODEOWNERS}: no owner lines")
        return cls(lines)

    def matching(self, path: str) -> list[OwnerLine]:
        return [line for line in self.lines if line.regex.match(path)]

    def owner(self, path: str) -> str | None:
        """The seat of the last matching line, as GitHub resolves an owner. None when nothing matches."""
        matched = self.matching(path)
        return matched[-1].seat if matched else None

    def logins(self) -> set[str]:
        return {login.lstrip("@") for line in self.lines for login in line.logins}


def owner_table(base: Tree, tree: Tree) -> tuple[Owners, str]:
    """The base's CODEOWNERS, and where it was read.

    The one PR that adds the file has no base table to read; that PR's own
    table is used and the refusal says so. Every later PR is read against
    what is on `main`.
    """
    if (text := base.text(CODEOWNERS)) is not None:
        return Owners.parse(text), f"the base {base.name}"
    if (text := tree.text(CODEOWNERS)) is not None:
        return Owners.parse(text), f"the PR itself, because the base {base.name} has no {CODEOWNERS}"
    raise ValueError(f"neither the base nor the PR has {CODEOWNERS}")


def seats_of(path: str, base: Tree, tree: Tree, owners: Owners) -> list[tuple[str | None, str]]:
    """(seat, detail) for each seat a change to `path` needs a ruling from.

    One entry for any file but a manifest, whose changed top-level fields
    are attributed to their owners; a manifest change that moves no field
    (a comment) is the file owner's.
    """
    owner = owners.owner(path)
    if RULING_GLOB.match(path):
        # A ruling file is owned by the seat in its own front matter, as a
        # subagent prompt is (SPEC/00 §5, last row): Product's `milestones/**`
        # key must not cover an edit to another seat's past ruling
        # (security-reviewer on PR 2, F5). A new file with this PR's number
        # covers itself before this is reached.
        fm = front_matter(base.text(path) or tree.text(path) or "") or {}
        return [(canonical_seat(fm.get("seat")) or owner, " (a ruling file, owned by its seat:)")]
    if not MANIFEST.match(path):
        return [(owner, "")]
    before = _yaml_mapping(base.text(path))
    after = _yaml_mapping(tree.text(path))
    if before is None or after is None:
        return [(owner, "")]
    moved = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    if not moved:
        return [(owner, "")]
    by_seat: dict[str | None, list[str]] = {}
    for key in moved:
        by_seat.setdefault(MANIFEST_FIELD_SEATS.get(key, owner), []).append(key)
    return [(seat, f" ({', '.join(keys)})") for seat, keys in by_seat.items()]


def _yaml_mapping(text: str | None) -> dict[str, Any] | None:
    if text is None:
        return {}
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return doc if isinstance(doc, dict) else None


# --- rulings ----------------------------------------------------------------


def front_matter(text: str) -> dict[str, Any] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None
    try:
        doc = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return None
    return doc if isinstance(doc, dict) else None


def pr_number(value: Any) -> int | None:
    """`12`, `#12` and `https://github.com/<owner>/<repo>/pull/12` all name PR 12."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if match := re.match(r"^\s*#?(\d+)\s*$", value):
            return int(match[1])
        if match := re.match(r"^\s*https://github\.com/[^/]+/[^/]+/pull/(\d+)/?\s*$", value):
            return int(match[1])
    return None


@dataclass
class Ruling:
    path: str
    seat: str | None
    authorises: list[str] = field(default_factory=list)
    body: str = ""
    _globs: list[re.Pattern[str]] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self._globs = [pattern_regex(str(g), anchored=True) for g in self.authorises]

    def authorises_path(self, path: str) -> bool:
        return any(g.match(path) for g in self._globs)

    def covers(self, path: str, seat: str | None) -> bool:
        """SPEC/02 §2 "Covers": the seat that owns the path, and a glob that matches it."""
        return seat is not None and self.seat == seat and self.authorises_path(path)

    def names(self, path: str) -> bool:
        """The second key of a two-key change names the path in its body or its globs (M01 PR 1, ruling B)."""
        return self.authorises_path(path) or path in self.body


def rulings(tree: Tree, pr: int) -> list[Ruling]:
    """Every ruling file in the tree whose `pr:` is this PR."""
    found = []
    for path in sorted(tree.files()):
        if not RULING_GLOB.match(path):
            continue
        text = tree.text(path) or ""
        fm = front_matter(text)
        if fm is None or pr_number(fm.get("pr")) != pr:
            continue
        authorises = fm.get("authorises") if isinstance(fm.get("authorises"), list) else []
        found.append(Ruling(path, canonical_seat(fm.get("seat")), [str(a) for a in authorises], text))
    return found
