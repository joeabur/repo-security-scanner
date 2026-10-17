#!/usr/bin/env python3
"""Verify that every SHA-pinned GitHub Action matches the upstream tag named in its comment.

A pin like ``uses: actions/checkout@<sha> # v7.0.1`` is only trustworthy if ``<sha>`` really is what the
tag ``v7.0.1`` points at upstream (a SHA can also belong to an unrelated fork commit). This asks the
action's repository directly with ``git ls-remote`` (network access to github.com required).

    python scripts/verify_pins.py .github/workflows
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

USES_RE = re.compile(
    r"uses:\s*(?P<action>[\w.\-]+/[\w.\-]+(?:/[\w.\-/]+)?)@(?P<sha>[0-9a-f]{40})\s*#\s*(?P<tag>v?[\w.\-]+)"
)
REPO_RE = re.compile(r"^[A-Za-z0-9][\w.\-]*/[A-Za-z0-9][\w.\-]*$")  # no leading dot: rejects "../x"
TAG_RE = re.compile(r"^v?[\w.\-]+$")


def parse_pins(directory: Path) -> set[tuple[str, str, str, str]]:
    """Return {(workflow file, owner/repo, tag, sha)} for every pinned action."""
    pins = set()
    for file in sorted(directory.glob("*.y*ml")):
        for match in USES_RE.finditer(file.read_text(encoding="utf-8")):
            repo = "/".join(match["action"].split("/")[:2])
            pins.add((file.name, repo, match["tag"], match["sha"]))
    return pins


def upstream_sha(repo: str, tag: str, timeout: int = 60) -> str | None:
    """Commit SHA the upstream tag points at (annotated tags are dereferenced), or None."""
    if not REPO_RE.match(repo) or not TAG_RE.match(tag):
        raise ValueError(f"refusing odd repo/tag: {repo!r} {tag!r}")
    out = subprocess.run(
        ["git", "ls-remote", f"https://github.com/{repo}.git", f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}"],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if out.returncode != 0:
        raise RuntimeError(f"git ls-remote failed for {repo}: {out.stderr.strip()[:200]}")
    refs = {}
    for line in out.stdout.splitlines():
        sha, _, ref = line.partition("\t")
        refs[ref] = sha
    return refs.get(f"refs/tags/{tag}^{{}}") or refs.get(f"refs/tags/{tag}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_pins.py WORKFLOW_DIR", file=sys.stderr)
        return 2
    pins = parse_pins(Path(argv[1]))
    if not pins:
        print("no pinned actions found", file=sys.stderr)
        return 2
    bad = 0
    cache: dict[tuple[str, str], str | None] = {}
    for file, repo, tag, sha in sorted(pins):
        key = (repo, tag)
        if key not in cache:
            cache[key] = upstream_sha(repo, tag)
        real = cache[key]
        if real == sha:
            print(f"OK        {file}: {repo}@{tag} = {sha[:12]}")
        else:
            bad += 1
            found = real[:12] if real else "tag not found"
            print(f"MISMATCH  {file}: {repo}@{tag} pinned {sha[:12]}, upstream {found}")
    print(f"{len(pins)} pin(s) checked, {bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
