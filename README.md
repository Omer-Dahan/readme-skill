<div align="center">

<br>

### github-readme-authoring

**An agent skill for writing GitHub READMEs that are actually true.**<br>
Every claim is sourced to a `file:line` in the repo, linted by a script, then re-checked
by a second, independent model before it ships. It writes documentation only — no
application code, no invented features.

<br>

<a href="#-compatibility"><img src="https://img.shields.io/badge/🔌_Compatibility-06B6D4?style=for-the-badge&logoColor=white" alt="Compatibility"></a>
<a href="#-features"><img src="https://img.shields.io/badge/✨_Features-D98324?style=for-the-badge&logoColor=white" alt="Features"></a>
<a href="#-how-it-works"><img src="https://img.shields.io/badge/🧠_How_It_Works-0D1117?style=for-the-badge&logoColor=white" alt="How It Works"></a>
<a href="#-testing"><img src="https://img.shields.io/badge/🧪_Testing-22C55E?style=for-the-badge&logoColor=white" alt="Testing"></a>

<br><br>

![Skill](https://img.shields.io/badge/Agent-Skill-0088CC?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

</div>

---

## 📑 Table of Contents

<table>
<tr>
<td valign="top" width="33%">

**Getting Started**
- [🔌 Compatibility](#-compatibility)
- [✨ Features](#-features)
- [🧠 How It Works](#-how-it-works)
- [📦 Installation](#-installation)

</td>
<td valign="top" width="33%">

**Operations**
- [🧪 Testing](#-testing)
- [🧱 Repository Layout](#-repository-layout)

</td>
<td valign="top" width="33%">

**Reference**
- [🚧 Known Limitations](#-known-limitations)
- [📜 License & Credits](#-license--credits)

</td>
</tr>
</table>

---

## 🔌 Compatibility

This is a plain agent skill: a `SKILL.md` procedure, a template, two reference docs, and a
standalone lint script. Nothing in those files is tied to one vendor.

- **Any agent that reads `SKILL.md`** — Hermes Agent, Claude Code, and similar tools — can load
  `skills/github-readme-authoring` and follow the procedure.
- **No agent at all.** Copy `skills/github-readme-authoring/templates/readme-house-style.md`,
  fill it in by hand, and run `skills/github-readme-authoring/scripts/check_readme.py` yourself.
  See [Installation](#-installation) below.

---

## ✨ Features

<table>
<tr>
<td width="33%" valign="top">

### 🔎 Fact Inventory First
Reads manifests, config loaders, deploy files, and tests before writing a line.
Every published claim is tied to a source location.

</td>
<td width="33%" valign="top">

### 🏛️ Fixed House Style
Centered header, badge navigation, three-column feature tables, and a set section
order — one template (`skills/github-readme-authoring/templates/readme-house-style.md`), not a blank page.

</td>
<td width="33%" valign="top">

### 🧹 Self-Linting
`skills/github-readme-authoring/scripts/check_readme.py` catches dead anchors, machine-local
paths, placeholder tokens, unhedged counts, unbacked superlatives, and a license badge with no
matching `LICENSE` file.

</td>
</tr>
<tr>
<td width="33%" valign="top">

### 🕵️ Independent Verification
`skills/github-readme-authoring/references/verification-brief.md` hands the draft to a second,
different model that checks it against the code and flags unsupported or omitted claims.

</td>
<td width="33%" valign="top">

### 🗂️ Configuration Matrix
One row per real configuration variable, read from the loader that consumes it —
not from `.env.example` comments, which drift from the code.

</td>
<td width="33%" valign="top">

### 🚫 No Invented Features
Documents what the code does. A feature the product promises but doesn't
implement gets flagged for a code fix, not written into the README.

</td>
</tr>
<tr>
<td width="33%" valign="top">

### ⚓ Anchor Slug Fidelity
`check_readme.py`'s slugifier reproduces GitHub's heading-anchor rules, including the
invisible U+FE0F variation-selector quirk on emoji headings.

</td>
<td width="33%" valign="top">

### 🧩 Agent-Agnostic Procedure
`SKILL.md` names generic read/write/search/patch steps, not one vendor's tool calls — Hermes
Agent, Claude Code, or a human following it by hand all qualify.

</td>
<td width="33%" valign="top">

### 🪤 Documented Pitfalls Library
Eleven named failure modes in `SKILL.md` — backwards config docs, drifting counts, unbacked
superlatives — each tied to a real cause, not a style guess.

</td>
</tr>
<tr>
<td width="33%" valign="top">

### 📋 Omission-First Completeness Pass
`skills/github-readme-authoring/references/fact-inventory.md` step 7 enumerates the full public
surface and ticks it against the draft, since omission is the most common accuracy failure.

</td>
<td width="33%" valign="top">

### 🔄 Refresh, Don't Append
Stale status or milestone prose is deleted outright instead of being left under a new section
heading next to outdated claims.

</td>
<td width="33%" valign="top">

### 🚚 Docs-Only Delivery
The final commit touches only documentation (plus a LICENSE fix if one was required), reported
with the commit hash and the exact corrections made.

</td>
</tr>
</table>

---

## 🧠 How It Works

The skill is a procedure, not a generator: `skills/github-readme-authoring/SKILL.md` walks
an agent through seven steps — recon the repo into a fact inventory, pick the doc language,
draft from the template, build the configuration matrix from the config loader, self-lint,
hand the draft to an independent verifier, then deliver a docs-only commit.

```
repo files ──▶ fact inventory ──▶ draft (template) ──▶ check_readme.py ──▶ independent model ──▶ commit
                (file:line each)                         (lint, exit 0)      (fact re-check)
```

---

## 📦 Installation

Pick whichever fits your setup — none of them is the "official" way.

**A. Copy it into your agent's skills folder**

```bash
cp -r skills/github-readme-authoring /path/to/your/agent/skills/
```

Any agent that discovers skills by reading `SKILL.md` files will pick it up from there. The
next time you ask it for a README, badges, or "make this repo's page look professional", it
applies the procedure in `SKILL.md`.

**B. Hermes Agent install**

If you use Hermes Agent, its `install` command fetches the skill directly from this repo —
the identifier is the GitHub path down to the skill directory:

```bash
hermes skills install Omer-Dahan/readme-skill/skills/github-readme-authoring
```

`hermes skills tap add Omer-Dahan/readme-skill` is a separate, optional step: it only
registers this repo as a skill *source* for `hermes skills browse`/`search`, it does not
install anything by itself.

**C. Standalone, no agent**

Clone the repo and use the template and linter directly:

```bash
git clone https://github.com/Omer-Dahan/readme-skill
cp readme-skill/skills/github-readme-authoring/templates/readme-house-style.md README.md
# fill it in by hand, then:
python3 readme-skill/skills/github-readme-authoring/scripts/check_readme.py README.md --repo .
```

---

## 🧪 Testing

`tests/test_check_readme.py` imports `check_readme.py` directly and exercises it against a
known-bad README (dead anchor, local path, placeholder token, license badge with no
`LICENSE` file) and a clean one, asserting zero findings on the clean case.

```bash
uv sync             # installs the dev dependency group (pytest) from pyproject.toml
uv run pytest tests/
```

No `uv`? Any Python 3.11+ environment works: `python3 -m venv .venv && source .venv/bin/activate &&
pip install pytest && pytest tests/`.

---

## 🧱 Repository Layout

```
readme-skill/
├── LICENSE                                 # MIT
├── README.md                               # this file
├── pyproject.toml                          # requires-python, dev dependency group (pytest)
├── skills/
│   └── github-readme-authoring/
│       ├── SKILL.md                        # the procedure an agent follows
│       ├── templates/
│       │   └── readme-house-style.md       # the README template to copy and fill
│       ├── references/
│       │   ├── fact-inventory.md           # checklist for sourcing every claim
│       │   └── verification-brief.md       # brief for the independent verifying model
│       └── scripts/
│           └── check_readme.py             # lints a README for the failure modes above
└── tests/
    └── test_check_readme.py                # pytest coverage for check_readme.py
```

---

## 🚧 Known Limitations

- **The verification step isn't enforced mechanically.** Step 6 of the procedure requires a
  second, different model to re-check the draft; nothing in this repo forces that hand-off to
  happen — it depends on the agent following `SKILL.md`.
- **`check_readme.py` approximates GitHub's heading-anchor rules**, including the emoji
  variation-selector quirk described in `SKILL.md`'s pitfalls section. It is not GitHub's own
  slugger, so an edge case can still slip through.
- **The procedure assumes generic file read/write/search/patch actions.** Every agent names
  these differently; following `SKILL.md` with a given agent means mapping those steps to its
  actual tool names.

---

## 📜 License & Credits

MIT, see [LICENSE](LICENSE). Author: Omer Dahan ([@Omer-Dahan](https://github.com/Omer-Dahan)).

Repo: [github.com/Omer-Dahan/readme-skill](https://github.com/Omer-Dahan/readme-skill)
