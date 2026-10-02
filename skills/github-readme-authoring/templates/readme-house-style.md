# README House-Style Template

Copy this file, replace every `{{PLACEHOLDER}}`, and delete any block whose asset or section does
not exist in the repo. A surviving placeholder is a lint failure.

---

```markdown
<div align="center">

<br>

### {{PROJECT_TITLE}}
**{{ONE_LINE_TAGLINE}}**<br>
{{TWO_TO_THREE_LINE_PITCH: what it does, for whom, the one thing that makes it different.}}

<br>

<a href="#-quick-start"><img src="https://img.shields.io/badge/🚀_Quick_Start-06B6D4?style=for-the-badge&logoColor=white" alt="Quick Start"></a>
<a href="#-features"><img src="https://img.shields.io/badge/✨_Features-D98324?style=for-the-badge&logoColor=white" alt="Features"></a>
<a href="#-architecture"><img src="https://img.shields.io/badge/🧠_Architecture-0D1117?style=for-the-badge&logoColor=white" alt="Architecture"></a>
<a href="#-deploying-to-the-server"><img src="https://img.shields.io/badge/⚙️_Deploy-22C55E?style=for-the-badge&logoColor=white" alt="Deploy"></a>

<br><br>

![Language](https://img.shields.io/badge/{{LANG}}-{{LANG_VERSION}}-{{LANG_COLOR}}?style=flat-square&logo={{LANG_LOGO}}&logoColor=white)
![Runtime](https://img.shields.io/badge/{{RUNTIME}}-{{RUNTIME_VALUE}}-0088CC?style=flat-square)
![License](https://img.shields.io/badge/License-{{SPDX}}-blue?style=flat-square)

</div>

---

## 📑 Table of Contents

<table>
<tr>
<td valign="top" width="33%">

**Getting Started**
- [✨ Features](#-features)
- [🧠 Architecture](#-architecture)
- [🚀 Quick Start](#-quick-start)
- [🎮 Interactive Workflow](#-interactive-workflow)

</td>
<td valign="top" width="33%">

**Operations**
- [⚙️ Deploying to the Server](#-deploying-to-the-server)
- [🧱 Project Structure](#-project-structure)
- [🔧 Configuration Matrix](#-configuration-matrix)

</td>
<td valign="top" width="33%">

**Reference**
- [💡 Design Decisions](#-design-decisions--reliability)
- [⚠️ Known Limitations](#️-known-limitations)
- [📜 License & Credits](#-license--credits)

</td>
</tr>
</table>

---

## ✨ Features

<table>
<tr>
<td width="33%" valign="top">

### {{EMOJI}} {{FEATURE_1}}
{{Two concrete lines. Name the mechanism, not an adjective.}}

</td>
<td width="33%" valign="top">

### {{EMOJI}} {{FEATURE_2}}
{{...}}

</td>
<td width="33%" valign="top">

### {{EMOJI}} {{FEATURE_3}}
{{...}}

</td>
</tr>
<tr>
<td width="33%" valign="top">

### {{EMOJI}} {{FEATURE_4}}
{{...}}

</td>
<td width="33%" valign="top">

### {{EMOJI}} {{FEATURE_5}}
{{...}}

</td>
<td width="33%" valign="top">

### {{EMOJI}} {{FEATURE_6}}
{{...}}

</td>
</tr>
</table>

---

## 🧠 Architecture

{{One paragraph: the module map and the responsibility of each top-level package.}}

```
{{REQUEST_FLOW: one real request, step by step, through the actual modules.}}
```

---

## 🚀 Quick Start

```bash
{{clone + install + configure + run — the commands that exist in the repo}}
```

---

## 🎮 Interactive Workflow

{{What the end user sees: commands, the happy path, the states, the failure messages.}}

---

## ⚙️ Deploying to the Server

{{The real deploy path: service files, prerequisites, the update command, verification.}}

---

## 🧱 Project Structure

```
{{TREE: real directories and the files that matter, each with a short purpose comment}}
```

---

## 🔧 Configuration Matrix

| Variable | Group | What it does | Default |
|---|---|---|---|
| `{{VAR}}` | {{GROUP}} | {{effect on behavior}} | `{{DEFAULT}}` |

---

## 💡 Design Decisions / Reliability

- **{{DECISION}}** — {{why, and what breaks without it}}

---

## ⚠️ Known Limitations

- **{{LIMITATION}}** — {{honest scope, and the workaround if one exists}}

---

## 📜 License & Credits

{{SPDX id as declared in the manifest. Attribution exactly as the owner requires — no upstream
attribution when the codebase is a clean rewrite.}}
```
