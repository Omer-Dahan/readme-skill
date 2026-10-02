#!/usr/bin/env python3
"""Lint a README before publishing it.

Checks the failure modes that push a polished README into "inaccurate" territory:
machine-local paths, dead anchors, unresolved relative links, placeholder tokens,
unhedged counts, an unverifiable license badge, and unbacked superlatives.

Usage:  python3 check_readme.py README.md --repo .
Exit:   0 when clean, 1 when findings exist.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|FIXME|XXX|LOREM)\b|\{\{[^}]+\}\}|<PLACEHOLDER")
LOCAL_PATH_RE = re.compile(
    r"file:///|(?:^|[\s(\[\"'])(?:/home/|/Users/|/root/|/tmp/|[A-Za-z]:\\\\)"
)
ANCHOR_RE = re.compile(r"\]\(#([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
LINK_RE = re.compile(r"\]\((?!https?://|mailto:|#)([^)\s]+)")
SUPERLATIVE_RE = re.compile(
    r"\b(blazing|ultra-?fast|lightning[- ]?fast|world[- ]?class|best-in-class|100% secure|"
    r"zero[- ]downtime|enterprise[- ]grade|revolutionary|cutting[- ]edge)\b",
    re.IGNORECASE,
)
COUNT_RE = re.compile(r"\b(\d{2,5})\s+(tests?|files?|users?|downloads?|stars?|contributors?)\b", re.IGNORECASE)
HEDGE_RE = re.compile(r"as of this writing|at the time of writing|currently|approx|~", re.IGNORECASE)
BADGE_ANCHOR_RE = re.compile(r'<a href="#([^"]+)"')


def slugify(heading: str) -> str:
    """Approximate GitHub's heading anchor: lowercase, keep letters/digits/marks/spaces/hyphens,
    drop other punctuation and emoji, spaces to hyphens (leading hyphen is real GitHub behavior)."""
    import unicodedata

    kept: list[str] = []
    for ch in heading.strip().lower():
        if ch.isspace():
            kept.append(" ")
        elif ch.isalnum() or ch in "-_" or unicodedata.category(ch).startswith("M"):
            kept.append(ch)
    return "".join(kept).replace(" ", "-")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("readme")
    parser.add_argument("--repo", default=".", help="Repository root for relative-link checks")
    parser.add_argument("--license-file", default="LICENSE", help="Expected license filename")
    args = parser.parse_args(argv)

    path = Path(args.readme)
    root = Path(args.repo)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: list[str] = []

    def add(kind: str, lineno: int, detail: str) -> None:
        findings.append(f"{kind}:{lineno}: {detail}")

    headings = {slugify(m.group(1)) for m in HEADING_RE.finditer(text)}
    # GitHub de-duplicates identical headings with -1, -2, ... suffixes
    seen: dict[str, int] = {}
    for m in HEADING_RE.finditer(text):
        base = slugify(m.group(1))
        count = seen.get(base, 0)
        headings.add(base if count == 0 else f"{base}-{count}")
        seen[base] = count + 1

    fence = False
    for n, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            fence = not fence
        if fence:
            continue
        if PLACEHOLDER_RE.search(line):
            add("placeholder", n, line.strip()[:80])
        if LOCAL_PATH_RE.search(line):
            add("local-path", n, line.strip()[:80])
        if SUPERLATIVE_RE.search(line) and not HEDGE_RE.search(line):
            add("superlative", n, SUPERLATIVE_RE.search(line).group(0) if SUPERLATIVE_RE.search(line) else "")
        if COUNT_RE.search(line) and not HEDGE_RE.search(line):
            add("unhedged-count", n, COUNT_RE.search(line).group(0))
        for anchor in ANCHOR_RE.findall(line) + BADGE_ANCHOR_RE.findall(line):
            if anchor not in headings:
                add("dead-anchor", n, f"#{anchor}")
        for target in LINK_RE.findall(line):
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            if not (root / clean).exists():
                add("missing-file", n, target)

    if "license" in text.lower() and "shields.io" in text and not (root / args.license_file).exists():
        findings.append(f"license:0: license badge present but {args.license_file} not found in {root}")

    if findings:
        print(f"{len(findings)} finding(s) in {path}:")
        for item in findings:
            print(f"  {item}")
        return 1
    print(f"clean: {path} — no findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
