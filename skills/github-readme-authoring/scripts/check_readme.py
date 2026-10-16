#!/usr/bin/env python3
"""Lint a README before publishing it.

Three families of checks:

1. Accuracy (markdown text outside fenced code): machine-local paths, dead anchors,
   unresolved relative links, placeholder tokens, an unverifiable license badge,
   unbacked superlatives, unhedged counts, and two test counts that disagree (count claims
   are read inside fenced code too, where counts usually live).
2. Fenced code, where a documentation sweep corrupts text silently: a comment line that
   carries two comment markers was two lines joined by a repo-wide dash replacement.
3. Rendering, the defects a text diff cannot show: Hebrew mixed with digits or Latin and
   no directional mark (the bidi algorithm reorders the numbers around it on the page),
   an ASCII box holding emoji or Hebrew (glyph widths are not one monospace cell, so the
   borders drift), and a shields.io badge URL carrying a flag emoji or non-ASCII letters.
   Only *closed* boxes (a right border on the line) are checked: a directory tree drawn with
   box-drawing characters has nothing to align against.

Usage:  python3 check_readme.py README.md --repo . [--tests 1057]
Exit:   0 when clean, 1 when findings exist.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

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
COUNT_RE = re.compile(r"\b(\d+)\s+(tests?|files?|users?|downloads?|stars?|contributors?)\b", re.IGNORECASE)
HEDGE_RE = re.compile(r"as of this writing|at the time of writing|currently|approx|~", re.IGNORECASE)
BADGE_ANCHOR_RE = re.compile(r'<a href="#([^"]+)"')

# Rendering and fenced-content checks
HEBREW_RE = re.compile(r"[֐-׿]")
DIR_MARK_RE = re.compile(r"[‎‏⁦-⁩]")
LATIN_DIGIT_RE = re.compile(r"[A-Za-z0-9]")
WIDE_GLYPH_RE = re.compile(r"[\U0001F000-\U0001FAFF☀-➿️]")
BOX_RE = re.compile(r"^\s*[│┌├└].*[│┐┘]\s*$")  # a closed box line only
MERGED_COMMENT_RE = re.compile(r"#[^#\n]*\s-\s+#")
BADGE_RE = re.compile(r"img\.shields\.io/badge/([^\s)\"'<>]*)")
FLAG_RE = re.compile(r"[\U0001F1E6-\U0001F1FF]{2}")
# A parenthesised ASCII run right after a Hebrew label is left in place by the bidi algorithm's
# bracket-pair rule (N0), so it is not a hazard; ``מהירות: 5.4MB/s`` is.
SAFE_TAIL_RE = re.compile(r":\s*\([A-Za-z0-9./% -]+\)\s*$")
# A line whose first strong character is Hebrew takes an RTL reading order, so ASCII punctuation at
# its end is displayed at the left end (GitHub gives the paragraph an LTR base direction). An
# ellipsis-terminated status label ("מוריד...") is the product's own text, not a mixing defect.
RTL_PUNCT_RE = re.compile(r"[:.,;]\s*$")
TEST_COUNT_RE = re.compile(r"\b(\d[\d,]{0,6})\s+pass(?:ing|ed)\b", re.IGNORECASE)


def slugify(heading: str) -> str:
    """Approximate GitHub's heading anchor: lowercase, keep letters/digits/marks/spaces/hyphens,
    drop other punctuation and emoji, spaces to hyphens (leading hyphen is real GitHub behavior)."""
    kept: list[str] = []
    for ch in heading.strip().lower():
        if ch.isspace():
            kept.append(" ")
        elif ch.isalnum() or ch in "-_" or unicodedata.category(ch).startswith("M"):
            kept.append(ch)
    return "".join(kept).replace(" ", "-")


def first_strong_is_hebrew(line: str) -> bool:
    """True when the line's first directional character is Hebrew (markdown markers, emoji, spaces
    and digits before it are ignored) - that line reads right-to-left on an LTR page."""
    for ch in line:
        if HEBREW_RE.match(ch):
            return True
        if LATIN_DIGIT_RE.match(ch):
            return False
    return False


def badge_problem(label: str) -> str | None:
    """Why a shields.io badge label will not render as written, or None."""
    if FLAG_RE.search(label):
        return "flag emoji in the label (no glyph on Windows: it renders as the letters 'IL')"
    if any(ord(ch) > 127 and unicodedata.category(ch).startswith("L") for ch in label):
        return "non-ASCII letters in the label (shields.io force-fits them with textLength)"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("readme")
    parser.add_argument("--repo", default=".", help="Repository root for relative-link checks")
    parser.add_argument("--license-file", default="LICENSE", help="Expected license filename")
    parser.add_argument(
        "--tests",
        type=int,
        default=None,
        help="Measured number of passing tests; every claimed count must match it",
    )
    args = parser.parse_args(argv)

    path = Path(args.readme)
    root = Path(args.repo)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: list[str] = []
    claims: list[tuple[int, int]] = []

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
            continue

        # -- rendering checks: they apply inside and outside fenced code --
        for m in TEST_COUNT_RE.finditer(line):
            claims.append((n, int(m.group(1).replace(",", ""))))
        for m in BADGE_RE.finditer(line):
            why = badge_problem(m.group(1))
            if why:
                add("badge-render", n, f"{why}: {m.group(1)[:60]}")
        if BOX_RE.match(line) and (WIDE_GLYPH_RE.search(line) or HEBREW_RE.search(line)):
            add(
                "wide-box",
                n,
                "closed ASCII box holds emoji or Hebrew; glyph widths are not one monospace cell, "
                "so the borders drift - drop the borders or pad by measured width",
            )

        rtl_tail = line.rstrip()
        if first_strong_is_hebrew(line) and RTL_PUNCT_RE.search(rtl_tail) and not rtl_tail.endswith("..."):
            add(
                "rtl-punctuation",
                n,
                "the first strong character is Hebrew, so this line reads right-to-left and its "
                "trailing punctuation is displayed at the left end - start the line with something "
                "neutral or move the mark inside the line",
            )

        if fence:
            if MERGED_COMMENT_RE.search(line):
                add(
                    "merged-line",
                    n,
                    "two comment markers with a dash between them: a character sweep probably "
                    "joined two comment lines",
                )
            elif len(line) > 200 and any(k in line for k in ("#", "git ", "sudo ", "uv ", "python")):
                add("long-fenced-line", n, "fenced line over 200 chars: confirm it is one logical line")
            if (
                HEBREW_RE.search(line)
                and LATIN_DIGIT_RE.search(line)
                and not DIR_MARK_RE.search(line)
                and not SAFE_TAIL_RE.search(line)
            ):
                add(
                    "rtl-hazard",
                    n,
                    "Hebrew mixed with digits/Latin and no LRM (U+200E): bidi reorders the "
                    "numbers and units on the rendered page - paste the program's real output",
                )
            continue

        # -- accuracy checks: markdown text outside fenced code --
        if PLACEHOLDER_RE.search(line):
            add("placeholder", n, line.strip()[:80])
        if LOCAL_PATH_RE.search(line):
            add("local-path", n, line.strip()[:80])
        if SUPERLATIVE_RE.search(line) and not HEDGE_RE.search(line):
            add("superlative", n, SUPERLATIVE_RE.search(line).group(0) if SUPERLATIVE_RE.search(line) else "")
        if COUNT_RE.search(line) and not HEDGE_RE.search(line):
            add("unhedged-count", n, COUNT_RE.search(line).group(0))
        for anchor in ANCHOR_RE.findall(line) + BADGE_ANCHOR_RE.findall(line):
            # GitHub percent-encodes non-ASCII fragments (Hebrew headings arrive as #%D7%94...)
            if anchor not in headings and unquote(anchor) not in headings:
                add("dead-anchor", n, f"#{anchor}")
        for target in LINK_RE.findall(line):
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            if not (root / clean).exists():
                add("missing-file", n, target)

    if "license" in text.lower() and "shields.io" in text and not (root / args.license_file).exists():
        findings.append(f"license:0: license badge present but {args.license_file} not found in {root}")

    distinct = {count for _, count in claims}
    if len(distinct) > 1:
        first_line, _ = claims[0]
        add(
            "count-conflict",
            first_line,
            "the README states more than one test count "
            f"({', '.join(str(c) for c in sorted(distinct))}); they must move together",
        )
    if args.tests is not None:
        for lineno, count in claims:
            if count != args.tests:
                add("stale-count", lineno, f"claims {count} passing, the measured count is {args.tests}")

    if findings:
        print(f"{len(findings)} finding(s) in {path}:")
        for item in findings:
            print(f"  {item}")
        return 1
    print(f"clean: {path} — no findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
