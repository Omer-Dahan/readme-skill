---
name: github-readme-authoring
description: Write fact-checked GitHub READMEs in a house style.
version: 1.0.0
author: Omer Dahan (Omer-Dahan)
license: MIT
platforms: [linux, macos, windows]
metadata:
  # Optional, namespaced for Hermes Agent's skill registry; other agents ignore it safely.
  hermes:
    tags: [readme, documentation, github, house-style, fact-checking]
---

# GitHub README Authoring Skill

Produce a repository README in a fixed, high-polish house style (centered header, badge
navigation, three-column tables, emoji sections) where **every factual claim is verified
against the repository's own code** and then re-checked by a second, independent model.
It writes documentation only: no application code, no invented features.

## When to Use

- User asks for a README, repo description, badges, or "make the project page look professional".
- An existing README is outdated, milestone-flavored, or factually wrong and needs a rewrite.
- You need a configuration matrix, architecture overview, or deploy section derived from code.
- Don't use for: changelogs, API references, or authoring other `SKILL.md` files — that's a
  separate concern.

## Prerequisites

- A local checkout of the target repo.
- An agent that can read files, write files, run shell commands, and apply patches — any
  agent that follows the open `SKILL.md` convention qualifies (tool names vary; map them to
  the steps below). The template and `scripts/check_readme.py` also work with no agent at
  all — see the repo's README for standalone use.
- A second agent that is **not** the author, for the verification pass (see references/verification-brief.md).
- Facts come from the repo: manifests, config loader, entry points, deploy files, tests. Never from memory.

## Quick Reference

All paths below (`templates/...`, `references/...`, `scripts/check_readme.py`) are relative to
*this skill's own directory* (`skills/github-readme-authoring/`), not the target repo you are
writing a README for — resolve them against wherever this skill was installed.

```bash
# Fact inventory sources, read from the TARGET repo (adapt to the stack)
pyproject.toml package.json Cargo.toml go.mod composer.json setup.cfg   # name, version, deps, license, entry points
.env.example  config/*.py  internal/config/*.go                       # every configuration variable + real default
Dockerfile* docker-compose* deploy/* .github/workflows/*               # how it is actually run and shipped
Makefile scripts/* tests/                                               # the commands that really exist
```

- Template: `templates/readme-house-style.md`
- Fact checklist: `references/fact-inventory.md`
- Verifier brief: `references/verification-brief.md`
- Render check (per-character measurement on the live page): `references/render-check.md`
- Lint the result: `python3 scripts/check_readme.py README.md --repo .` (accuracy, fenced-code and
  rendering checks; add `--tests <measured>` to pin every test count to a number you just ran)
- Publish the *skill* (not the README) by pushing this directory to a repo. If you use Hermes
  Agent, install it straight from that repo with `hermes skills install <owner/repo>/<path/to/skill>`;
  `hermes skills tap add <owner/repo>` only registers the repo as a skill source, it does not install.

## Procedure

1. **Recon (no writing yet).** Read the manifest, the existing README, every config source,
   the deploy files, and the test tree. Build a fact inventory using `references/fact-inventory.md`;
   record `file:line` for every entry. *Done when* every claim you plan to publish has a source line,
   or is explicitly marked "unverified" and left out.
2. **Decide language and audience.** Match the repo's existing public-doc language (default English).
   Do not translate an existing English public README into another language without being asked.
3. **Draft from the template.** Copy `templates/readme-house-style.md`, keep the section order,
   and fill it only from the inventory. Replace every placeholder; a surviving `TODO`/`<...>` fails step 5.
4. **Build the configuration matrix last.** One row per variable, straight from the config loader
   (not from the `.env.example` comments, which drift). Include the *effective* default and one
   short consequence note for the settings that actually change behavior.
5. **Self-lint.** Run `scripts/check_readme.py` and fix every finding. *Done when* zero findings:
   no machine-local paths, no dead anchors, no placeholder tokens, no unhedged counts, no
   license badge without a LICENSE file, every relative link resolves in the repo, no comment line
   that a sweep joined inside a code fence, no Hebrew mixed with digits without a directional mark,
   no Hebrew line whose trailing punctuation lands on the left, no ASCII box or badge holding a
   glyph that is not one cell wide.
6. **Render check.** Open the page (local preview, or wherever it renders once pushed) and *measure*
   what the lint cannot see: for every block holding Hebrew, emoji, or an ASCII box, read the
   per-character x positions and confirm the visual order matches the intended text and that all
   borders share one x coordinate; read each badge's rendered width against the string's natural
   width. *Done when* the measurements are clean — a Hebrew block that looks correct in the editor
   is routinely scrambled on the page (measured: `⚡ מהירות: 5.4MB/s` displaying as `⚡ 5.4 :מהירותMB/s`).
7. **Independent verification.** Hand the README plus `references/verification-brief.md` to a
   **different model than the author**. Fix every "no evidence" finding, then re-verify. *Done when*
   the verifier returns no unsupported claim — including claims the README omits that the code exposes.
8. **Deliver.** Commit README (and any LICENSE/badge fix) as a docs-only commit; report the commit
   hash plus the exact list of corrections made in step 6.

## House Style Contract

- **Centered header** in a `<div align="center">`: project title, one bold tagline, a 2-3 line pitch,
  then anchor-navigation badges (`shields.io` `for-the-badge`) and tech badges (`flat-square`).
- **Banner image only if the asset exists in the repo.** A broken `<img src="assets/...">` is worse
  than no banner; substitute a centered title block.
- **Table of contents** as a three-column HTML `<table>` grouped by theme (getting started /
  operations / reference).
- **Feature cards** as three-column HTML tables of `### emoji Title` + two lines of concrete text.
  10-12 cards, each describing something the code really does.
- **Section order:** Features, Architecture (with an ASCII or mermaid flow of one request), Quick Start,
  Interactive Workflow (what the end user sees), Deploying to the Server, Project Structure,
  Configuration Matrix, Design Decisions / Reliability, Known Limitations, License & Credits.
- **No attribution to previous upstream authors** when the owner has replaced the codebase;
  keep the license as declared in the manifest.
- Length 200-350 lines. Every line earns its place; no filler and no repeated pitch.

## Pitfalls

1. **Documenting a configuration variable backwards.** Real failure: a README called a concurrency
   variable "legacy, safely ignored" while it was the only real ceiling. Always read the code that
   consumes the value, never the comment next to it.
2. **Hard-coded counts drift.** Test counts, file counts, coverage. Either verify at write time and
   hedge ("as of this writing"), or omit the number.
3. **Badge versions must match manifests.** A "Python 3.13" badge on a `>=3.11` project is a finding.
4. **Machine-local paths leak.** Agent scratch dirs appear as `file:///tmp/...` or `/home/<user>/...`
   links that are dead on GitHub. Only repo-relative links are allowed.
5. **Emoji headings produce invisible anchors.** GitHub keeps the variation selector (U+FE0F) in the
   slug but drops the emoji itself: `## ⚙️ Deploying to the Server` → `#️-deploying-to-the-server`,
   not `#-deploying-to-the-server`. A badge or TOC link that omits U+FE0F looks correct and silently
   does nothing. `scripts/check_readme.py` reproduces GitHub's slug rules (verified against the
   `/repos/{owner}/{repo}/readme` HTML) — run it, and when in doubt add an explicit
   `<a id="plain-ascii"></a>` before the heading and link to that.
6. **Never document a feature the code does not implement.** If the *product itself* promises it to
   users (menu text, help copy), fix the promise in code — do not enshrine it in the README.
7. **No unverifiable superlatives.** "Blazing fast", "ultra-fast", "zero-downtime", "maximum
   throughput" — replace with the measured number, or with an accurate statement of the mechanism.
8. **A license badge needs a `LICENSE` file.** If it is missing, report it; don't silently ship the badge.
9. **Omission is the most common accuracy failure.** Enumerate the commands, hard limits, and
   user-visible behaviors the code exposes; readers notice missing capabilities more than wrong
   adjectives.
10. **Refreshing beats appending.** Delete stale status/milestone prose that no longer describes the
    shipped system instead of leaving it under a new section.
11. **Do not let the author verify.** Style and facts drift in ways the author cannot see; the second
    agent is the only reliable check.
12. **A text sweep is blind inside code fences.** A repo-wide dash replacement (a "no em dash" house
    rule) merges two lines whenever the first ends with the dash: `# ... as of this writing - #     the
    count grows over time ...` reads plausibly, passes an old linter that skips fenced code, and is
    wrong. After any character sweep, grep the fenced content for lines carrying two comment markers,
    and re-read the fences by eye.
13. **Never hand-type what the program prints.** A hand-typed UI mock drops the invisible directional
    marks the real formatter emits (an LRM after each Hebrew label), so the mock renders differently
    from the product: measured on the rendered page, a line typed as `⚡ מהירות: 5.4MB/s` displayed as
    `⚡ 5.4 :מהירותMB/s`, and `(03:45)` displayed with mirrored parentheses. Generate the block from
    the code, paste the bytes verbatim, and note above it where it came from.
14. **Emoji are not one monospace cell.** An ASCII box padded by character count drifts: measured
    17.0px for a moon emoji against 8.17px for one cell, so the right border landed 7px short and the
    emoji line overshot it by 7px. Drop the borders, or pad by measured width.
15. **Badges must be ASCII.** Windows has no glyph for a regional-indicator flag, so `🇮🇱` renders as
    the letters "IL"; and shields.io sizes the label with its own measurement and force-fits it with
    `textLength` (the Hebrew UI badge: 79px for a 46px string). Describe the feature in ASCII
    (`UI-Hebrew_RTL`).
16. **Verify mechanism claims, not just feature claims.** "Formatted with explicit bi-di RTL/LTR
    embeddings" survived the milestone that deleted those embedding characters, because verification
    read the tests that pin the visible text instead of the formatter's module docstring and its
    output lines. When a claim names a mechanism, open the code that implements the mechanism.
17. **Hebrew is a rendering problem, not only a translation problem.** Every rule and every measured
    failure is in the "Hebrew and RTL content" section below; read it before writing a page that
    contains a single Hebrew word, and measure the page afterwards.

## Hebrew and RTL content (rules from measured failures)

Hebrew text on a Markdown page is laid out by the Unicode bidi algorithm, not by the character order in
the file, and most Markdown hosts give every paragraph a left-to-right base direction. Six rules
follow; each was measured on a rendered page (see `references/render-check.md`).

1. **Generate a Hebrew UI mock from the program's own output; never type it.** A formatter that emits
   RTL text inserts invisible directional marks (an LRM, U+200E, after every Hebrew label, say).
   A hand-typed mock loses them and renders differently from the product: measured, `⚡ מהירות: 5.4MB/s`
   displayed as `⚡ 5.4 :מהירותMB/s`, and `(03:45)` came out as `)03:45(`. Paste the bytes and prove
   equality with a `repr()` diff in the same commit.
2. **A line whose first strong character is Hebrew reads right-to-left, so its trailing punctuation
   is displayed at the left end.** Start such a line with something neutral (an emoji, a dash, a
   number) or move the mark into the middle. The linter reports this as `rtl-punctuation`.
3. **Never put Hebrew — or a flag emoji — inside a badge URL.** shields.io sizes a label with its own
   font measurement and force-fits it with `textLength` (the "Hebrew UI" badge: 79px of forced width
   for a 46px string), and Windows has no glyph for a regional-indicator flag, so `🇮🇱` renders as
   "IL". Describe the feature in ASCII: `UI-Hebrew_RTL`.
4. **Hebrew inside a closed ASCII box or a column-padded block drifts.** Glyph widths are not one
   cell (a moon emoji measured 17.0px against 8.17px). Drop the frame, or pad by measured width.
5. **Links to Hebrew headings arrive percent-encoded** (`#%D7%94...`); decode before comparing (the
   linter does), and prefer an explicit `<a id="plain-ascii"></a>` anchor over trusting the slug of a
   heading that mixes Hebrew, Latin and emoji.
6. **A Hebrew document of its own (`README-he.md`) needs its own direction**: wrap the body in
   `<div dir="rtl">` where the host honors that attribute, leave code blocks and commands as literal
   LTR text, and keep one file per language rather than mixing both in one page.

## Verification

- `python3 scripts/check_readme.py README.md --repo .` → zero findings (exit code 0).
- A different model than the author confirms each published claim; every "no evidence" item is fixed
  and re-checked.
- Spot-check the high-risk claims by hand: configuration defaults, command names, hard limits,
  badge values, and every anchor link resolving to an existing heading.
- The final commit touches documentation only (plus a `LICENSE` fix if one was required).
