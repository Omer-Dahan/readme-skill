"""Behavioral tests for skills/github-readme-authoring/scripts/check_readme.py.

Imports the script as a module (it exposes `main(argv)`) instead of shelling
out, so failures point straight at the offending regex/rule.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "github-readme-authoring"
    / "scripts"
    / "check_readme.py"
)


def _load_check_readme():
    spec = importlib.util.spec_from_file_location("check_readme", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_readme"] = module
    spec.loader.exec_module(module)
    return module


check_readme = _load_check_readme()


BAD_README = """\
# Demo Project

![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

See [the roadmap](#-roadmap) for what's next.

TODO: write a real description.

Logs are written to /home/vm/demo/logs for now.
"""

CLEAN_README = """\
# Demo Project

![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

A small demo project used to exercise check_readme.py.

## Features

Does one thing well: it says hello.

## License

MIT, see [LICENSE](LICENSE).
"""


@pytest.fixture
def repo(tmp_path):
    return tmp_path


def test_bad_readme_fails_with_nonzero_exit(repo):
    readme = repo / "README.md"
    readme.write_text(BAD_README, encoding="utf-8")

    assert check_readme.main([str(readme), "--repo", str(repo)]) == 1


def test_bad_readme_reports_dead_anchor(repo, capsys):
    readme = repo / "README.md"
    readme.write_text(BAD_README, encoding="utf-8")

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "dead-anchor" in capsys.readouterr().out


def test_bad_readme_reports_local_path(repo, capsys):
    readme = repo / "README.md"
    readme.write_text(BAD_README, encoding="utf-8")

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "local-path" in capsys.readouterr().out


def test_bad_readme_reports_placeholder(repo, capsys):
    readme = repo / "README.md"
    readme.write_text(BAD_README, encoding="utf-8")

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "placeholder" in capsys.readouterr().out


def test_bad_readme_reports_missing_license_file(repo, capsys):
    readme = repo / "README.md"
    readme.write_text(BAD_README, encoding="utf-8")
    assert not (repo / "LICENSE").exists()

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "license:0" in capsys.readouterr().out


def test_clean_readme_has_zero_findings(repo, capsys):
    readme = repo / "README.md"
    readme.write_text(CLEAN_README, encoding="utf-8")
    (repo / "LICENSE").write_text("MIT License\n", encoding="utf-8")

    exit_code = check_readme.main([str(readme), "--repo", str(repo)])

    assert exit_code == 0
    assert "clean:" in capsys.readouterr().out


def test_small_unhedged_count_is_flagged(repo, capsys):
    """COUNT_RE used to require 2-5 digits, missing single-digit counts like "3 tests"."""
    readme = repo / "README.md"
    readme.write_text("# Demo\n\nShipped with 3 tests.\n", encoding="utf-8")

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "unhedged-count" in capsys.readouterr().out


def test_hedged_count_is_not_flagged(repo, capsys):
    readme = repo / "README.md"
    readme.write_text("# Demo\n\nAs of this writing, 3 tests pass.\n", encoding="utf-8")

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "unhedged-count" not in capsys.readouterr().out


@pytest.mark.parametrize(
    "heading,expected_slug",
    [
        ("Features", "features"),
        ("✨ Features", "-features"),
        ("⚙️ Deploying to the Server", "️-deploying-to-the-server"),
        ("⚠️ Known Limitations", "️-known-limitations"),
    ],
)
def test_slugify_handles_emoji_and_variation_selectors(heading, expected_slug):
    """Plain emoji (no variation selector) are dropped entirely by GitHub's slugger,
    leaving a leading hyphen; emoji with a U+FE0F variation selector keep that
    invisible character in the slug. See SKILL.md Pitfalls item 5.
    """
    assert check_readme.slugify(heading) == expected_slug


@pytest.mark.parametrize(
    "phrase",
    ["blazing fast", "ultra-fast", "ultrafast", "zero-downtime", "zero downtime", "cutting-edge"],
)
def test_superlative_re_matches_known_phrases(phrase):
    assert check_readme.SUPERLATIVE_RE.search(phrase)


def test_superlative_re_does_not_match_plain_text():
    assert check_readme.SUPERLATIVE_RE.search("a fast, reliable script") is None


def test_merged_comment_line_in_fence_is_flagged(repo, capsys):
    """A repo-wide dash sweep can join two comment lines into one that still has two
    comment markers; the old linter skipped fenced code entirely and missed this."""
    readme = repo / "README.md"
    readme.write_text(
        "# Demo\n\n```python\n# as of this writing - # the count grows over time\n```\n",
        encoding="utf-8",
    )

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "merged-line" in capsys.readouterr().out


def test_mermaid_semicolon_is_flagged(repo, capsys):
    readme = repo / "README.md"
    readme.write_text(
        "# Demo\n\n```mermaid\nstateDiagram-v2\n  A --> B: SSRF guard; direct-link engine\n```\n",
        encoding="utf-8",
    )

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "mermaid-semicolon" in capsys.readouterr().out


def test_semicolon_in_bash_fence_is_not_flagged_as_mermaid(repo, capsys):
    readme = repo / "README.md"
    readme.write_text(
        "# Demo\n\n```bash\necho hello; echo world\n```\n",
        encoding="utf-8",
    )

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "mermaid-semicolon" not in capsys.readouterr().out


def test_badge_with_flag_emoji_is_flagged(repo, capsys):
    readme = repo / "README.md"
    readme.write_text(
        "# Demo\n\n![Lang](https://img.shields.io/badge/🇮🇱_Hebrew-blue)\n",
        encoding="utf-8",
    )

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "badge-render" in capsys.readouterr().out


def test_badge_with_hebrew_label_is_flagged(repo, capsys):
    readme = repo / "README.md"
    readme.write_text(
        "# Demo\n\n![Lang](https://img.shields.io/badge/עברית-blue)\n",
        encoding="utf-8",
    )

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "badge-render" in capsys.readouterr().out


def test_closed_ascii_box_with_emoji_is_flagged(repo, capsys):
    readme = repo / "README.md"
    readme.write_text("# Demo\n\n```\n│ 🌕 moon │\n```\n", encoding="utf-8")

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "wide-box" in capsys.readouterr().out


def test_directory_tree_line_is_not_flagged_as_wide_box(repo, capsys):
    """A directory tree drawn with box-drawing characters has no right border to
    align against, so it must not be mistaken for a closed box."""
    readme = repo / "README.md"
    readme.write_text(
        "# Demo\n\n```\nproject/\n├── foo/\n└── bar/\n```\n",
        encoding="utf-8",
    )

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "wide-box" not in capsys.readouterr().out


def test_hebrew_mixed_with_digits_and_no_directional_mark_is_flagged(repo, capsys):
    readme = repo / "README.md"
    readme.write_text("# Demo\n\n```\nמהירות: 5.4MB/s\n```\n", encoding="utf-8")

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "rtl-hazard" in capsys.readouterr().out


def test_hebrew_mixed_with_digits_and_lrm_is_clean(repo, capsys):
    """A U+200E (LRM) right before the digits is the real formatter's own marker,
    not a hazard."""
    readme = repo / "README.md"
    readme.write_text("# Demo\n\n```\nמהירות:‎ 5.4MB/s\n```\n", encoding="utf-8")

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "rtl-hazard" not in capsys.readouterr().out


def test_hebrew_label_with_parenthesised_ascii_tail_is_clean(repo, capsys):
    """A parenthesised ASCII run right after a Hebrew label is left in place by the
    bidi algorithm's bracket-pair rule, so it is not a mixing hazard."""
    readme = repo / "README.md"
    readme.write_text("# Demo\n\n```\nתווית: (5.4MB/s)\n```\n", encoding="utf-8")

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "rtl-hazard" not in capsys.readouterr().out


def test_hebrew_first_line_ending_in_colon_is_flagged(repo, capsys):
    readme = repo / "README.md"
    readme.write_text("# Demo\n\nשלום עולם:\n", encoding="utf-8")

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "rtl-punctuation" in capsys.readouterr().out


def test_hebrew_first_line_ending_in_ellipsis_is_clean(repo, capsys):
    """An ellipsis-terminated status label is the product's own text, not punctuation
    displaced by the bidi algorithm."""
    readme = repo / "README.md"
    readme.write_text("# Demo\n\nמוריד...\n", encoding="utf-8")

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "rtl-punctuation" not in capsys.readouterr().out


def test_two_different_test_counts_are_a_count_conflict(repo, capsys):
    readme = repo / "README.md"
    readme.write_text(
        "# Demo\n\nAs of this writing, 24 passing.\n\nActually 30 passing.\n",
        encoding="utf-8",
    )

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "count-conflict" in capsys.readouterr().out


def test_tests_flag_mismatch_is_a_stale_count(repo, capsys):
    readme = repo / "README.md"
    readme.write_text("# Demo\n\nAs of this writing, 24 passing.\n", encoding="utf-8")

    check_readme.main([str(readme), "--repo", str(repo), "--tests", "30"])

    assert "stale-count" in capsys.readouterr().out


def test_link_to_percent_encoded_hebrew_heading_resolves(repo, capsys):
    """GitHub percent-encodes non-ASCII fragments; the linter must decode before
    comparing against the slugified heading or it reports a false dead-anchor."""
    readme = repo / "README.md"
    readme.write_text(
        "# Demo\n\n## עברית כותרת\n\n"
        "See [here](#%D7%A2%D7%91%D7%A8%D7%99%D7%AA-%D7%9B%D7%95%D7%AA%D7%A8%D7%AA)\n",
        encoding="utf-8",
    )

    check_readme.main([str(readme), "--repo", str(repo)])

    assert "dead-anchor" not in capsys.readouterr().out
