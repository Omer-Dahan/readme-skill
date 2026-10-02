<div align="center">

<br>

### github-readme-authoring

**A Hermes skill that writes fact-checked GitHub READMEs in a fixed house style.**<br>
Every claim is sourced to a `file:line` in the repo, linted by a script, then re-checked
by a second, independent model before it ships. It writes documentation only — no
application code, no invented features.

<br>

<a href="#-quick-start"><img src="https://img.shields.io/badge/🚀_Quick_Start-06B6D4?style=for-the-badge&logoColor=white" alt="Quick Start"></a>
<a href="#-features"><img src="https://img.shields.io/badge/✨_Features-D98324?style=for-the-badge&logoColor=white" alt="Features"></a>
<a href="#-how-it-works"><img src="https://img.shields.io/badge/🧠_How_It_Works-0D1117?style=for-the-badge&logoColor=white" alt="How It Works"></a>
<a href="#-testing"><img src="https://img.shields.io/badge/🧪_Testing-22C55E?style=for-the-badge&logoColor=white" alt="Testing"></a>

<br><br>

![Skill](https://img.shields.io/badge/Hermes-Skill-0088CC?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

</div>

---

## 📑 Table of Contents

<table>
<tr>
<td valign="top" width="33%">

**Getting Started**
- [✨ Features](#-features)
- [🧠 How It Works](#-how-it-works)
- [🚀 Quick Start](#-quick-start)

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
order — one template (`templates/readme-house-style.md`), not a blank page.

</td>
<td width="33%" valign="top">

### 🧹 Self-Linting
`scripts/check_readme.py` catches dead anchors, machine-local paths, placeholder
tokens, unhedged counts, unbacked superlatives, and a license badge with no
matching `LICENSE` file.

</td>
</tr>
<tr>
<td width="33%" valign="top">

### 🕵️ Independent Verification
`references/verification-brief.md` hands the draft to a second, different model
that checks it against the code and flags unsupported or omitted claims.

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

## 🚀 Quick Start

Install the skill into Hermes from this repo:

```bash
hermes skills tap add Omer-Dahan/readme-skill
```

This pulls `skills/github-readme-authoring` into your skill set. The next time you ask an
agent for a README, badges, or a "make this repo's page look professional", it applies the
procedure in `SKILL.md`.

To lint a README by hand, without the full skill flow:

```bash
python3 skills/github-readme-authoring/scripts/check_readme.py README.md --repo .
```

---

## 🧪 Testing

`tests/test_check_readme.py` imports `check_readme.py` directly and exercises it against a
known-bad README (dead anchor, local path, placeholder token, license badge with no
`LICENSE` file) and a clean one, asserting zero findings on the clean case.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pytest
pytest tests/
```

---

## 🧱 Repository Layout

```
readme-skill/
├── LICENSE                                 # MIT
├── README.md                               # this file
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
- **Written for Hermes-style agent tooling** (`terminal`, `read_file`, `search_files`,
  `write_file`, `patch`). Using it with another agent framework means mapping those tool
  names to its equivalents.

---

## 📜 License & Credits

MIT, see [LICENSE](LICENSE). Author: Omer Dahan ([@Omer-Dahan](https://github.com/Omer-Dahan)).

Repo: [github.com/Omer-Dahan/readme-skill](https://github.com/Omer-Dahan/readme-skill)
