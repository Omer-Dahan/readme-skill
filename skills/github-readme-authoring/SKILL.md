---
name: github-readme-authoring
description: Write fact-checked GitHub READMEs in a house style.
version: 1.0.0
author: Omer Dahan (Omer-Dahan), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
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
- Don't use for: changelogs, API references, or authoring `SKILL.md` files (use `hermes-agent-skill-authoring`).

## Prerequisites

- A local checkout of the target repo.
- Hermes tools: `terminal`, `read_file`, `search_files`, `write_file`, `patch`.
- A second agent that is **not** the author, for the verification pass (see references/verification-brief.md).
- Facts come from the repo: manifests, config loader, entry points, deploy files, tests. Never from memory.

## Quick Reference

```bash
# Fact inventory sources (adapt to the stack)
pyproject.toml package.json Cargo.toml go.mod composer.json setup.cfg   # name, version, deps, license, entry points
.env.example  config/*.py  internal/config/*.go                       # every configuration variable + real default
Dockerfile* docker-compose* deploy/* .github/workflows/*               # how it is actually run and shipped
Makefile scripts/* tests/                                               # the commands that really exist
```

- Template: `templates/readme-house-style.md`
- Fact checklist: `references/fact-inventory.md`
- Verifier brief: `references/verification-brief.md`
- Lint the result: `python3 scripts/check_readme.py README.md --repo .`
- Publish the *skill* (not the README): `hermes skills publish <skill-dir> --to github --repo <owner/repo>`

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
   license badge without a LICENSE file, every relative link resolves in the repo.
6. **Independent verification.** Hand the README plus `references/verification-brief.md` to a
   **different model than the author**. Fix every "no evidence" finding, then re-verify. *Done when*
   the verifier returns no unsupported claim — including claims the README omits that the code exposes.
7. **Deliver.** Commit README (and any LICENSE/badge fix) as a docs-only commit; report the commit
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

## Verification

- `python3 scripts/check_readme.py README.md --repo .` → zero findings (exit code 0).
- A different model than the author confirms each published claim; every "no evidence" item is fixed
  and re-checked.
- Spot-check the high-risk claims by hand: configuration defaults, command names, hard limits,
  badge values, and every anchor link resolving to an existing heading.
- The final commit touches documentation only (plus a `LICENSE` fix if one was required).
