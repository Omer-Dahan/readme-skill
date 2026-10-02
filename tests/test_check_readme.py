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
