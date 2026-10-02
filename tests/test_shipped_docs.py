"""Regression test: lint every markdown file this repo ships to agents and users.

This is the test that would have caught a real bug: templates/readme-house-style.md
linked to `#-deploying-to-the-server`, but GitHub's own slugger keeps the invisible
U+FE0F variation selector from the "gear" emoji, producing `#️-deploying-to-the-server`
instead (see SKILL.md's Pitfalls, item 5). check_readme.py's fence-tracking treats the
whole template as one code block -- it's wrapped in a ```markdown fence for copy/paste
display -- so linting the raw file never reaches that line. To actually exercise the
template's anchors, this test strips the outer fence before linting, the same way a
user strips it when pasting the template into their own README.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest
from test_check_readme import check_readme

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "github-readme-authoring"


def _lint(path: Path) -> list[str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        check_readme.main([str(path), "--repo", str(REPO_ROOT)])
    header, *rest = buf.getvalue().splitlines()
    return [line.strip() for line in rest]


def _kind_and_line(finding: str) -> tuple[str, int]:
    kind, rest = finding.split(":", 1)
    return kind, int(rest.split(":", 1)[0])


@pytest.mark.parametrize(
    "path",
    [
        REPO_ROOT / "README.md",
        SKILL_DIR / "references" / "fact-inventory.md",
        SKILL_DIR / "references" / "verification-brief.md",
    ],
    ids=lambda p: str(p.relative_to(REPO_ROOT)),
)
def test_shipped_doc_has_zero_findings(path: Path) -> None:
    assert _lint(path) == []


def test_skill_md_has_only_the_known_self_referential_findings() -> None:
    """SKILL.md's Pitfalls section documents forbidden patterns (a `TODO` token, local
    scratch paths, superlative words) by naming them explicitly, so the linter flags
    those exact lines. That makes these three findings permanent and expected -- not a
    regression. Any other finding here is new and must be investigated before SKILL.md
    ships.
    """
    expected = {
        ("placeholder", 71),  # names the forbidden `TODO` placeholder token
        ("local-path", 109),  # names the forbidden /tmp and /home/<user> example paths
        ("superlative", 119),  # lists the forbidden superlative words
    }
    actual = {_kind_and_line(f) for f in _lint(SKILL_DIR / "SKILL.md")}
    assert actual == expected


def test_readme_template_has_only_placeholder_findings(tmp_path: Path) -> None:
    """The template wraps its body in a ```markdown fence for copy/paste display;
    strip that wrapper before linting so headings and anchors inside it are actually
    checked (see module docstring) instead of being skipped as "inside a code fence".
    Every remaining `{{...}}` token is an intentional placeholder the user fills in
    before publishing, so `placeholder` findings are expected here -- anything else
    (a `dead-anchor`, for instance) is a real regression.
    """
    template_path = SKILL_DIR / "templates" / "readme-house-style.md"
    lines = template_path.read_text(encoding="utf-8").splitlines()
    fence_lines = [i for i, line in enumerate(lines) if line.strip().startswith("```")]
    inner = "\n".join(lines[fence_lines[0] + 1 : fence_lines[-1]])

    inner_path = tmp_path / "readme-house-style-inner.md"
    inner_path.write_text(inner, encoding="utf-8")

    findings = _lint(inner_path)
    kinds = {_kind_and_line(f)[0] for f in findings}
    assert findings, "expected placeholder findings for the template's {{...}} tokens"
    assert kinds == {"placeholder"}
