# Independent README Verification Brief

Hand this to a model that is **not** the author of the README, with read-only access to the repo.
Its job is to falsify, not to approve.

## Constraints to state up front

- Do not modify files, do not commit, do not push, do not run the application.
- Read the code; you may run the project's own test/lint commands and scratch scripts under a temp dir.

## What to check, in priority order

1. **Unsupported claims.** For each feature, limit, command, and default in the README: point at the
   code that implements it. No evidence → report it with the line and what the code actually does.
   For claims that name a *mechanism* (how the output is produced, how it is encoded, how it is
   ordered), open the implementing module and its docstring — a sentence can survive several
   milestones that deleted the mechanism it describes.
2. **Inverted or stale semantics.** Especially configuration variables documented as deprecated,
   ignored, or optional. Read the consumer of the value, not the comment near it.
3. **Configuration matrix drift.** Compare every row against the config loader: variable name,
   effective default, and described effect. Flag rows borrowed from `.env.example` comments.
4. **Commands and deploy steps.** Do the documented commands exist and would they work in the
   order given? Are paths, service names, and service files real?
5. **Numbers that drift.** Re-measure every test/coverage/file count yourself (the project's own
   test command); two occurrences of the same count must agree.
6. **Badges.** Language/runtime version, license, and dependency badges against the manifest. Flag a
   license badge when no `LICENSE` file exists, and any badge whose label is not ASCII (a flag emoji
   renders as letters on Windows and shields.io force-fits non-ASCII labels with `textLength`).
7. **Rendering.** For each block that mixes Hebrew with digits or Latin, each ASCII box, and each
   badge, does it render as written? Measure the rendered page (per-character x positions, or the
   box borders' x coordinates) instead of trusting the source: a mock that drops the program's
   directional marks (U+200E) renders scrambled, and an ASCII box padded by character count drifts
   whenever emoji or Hebrew sit inside it. Report what the page shows, with the measurement.
8. **Links.** Every anchor resolves to an existing heading; every relative link resolves in the repo;
   zero machine-local or scratch-directory paths.
9. **Omissions.** List real, user-visible capabilities the README fails to mention (commands, hard
   limits, privacy constraints, retry behavior).
10. **Overstatement.** Marketing language with no measurement behind it; process claims ("verified by
    two models") that cannot be checked from the repository.
11. **User-facing promises the code does not keep.** Menu text, help copy, or README promises for a
    feature with no implementation — report as a code finding.

## Required report shape

For each item: `severity` (blocker / high / medium / low), `README line`, the **exact quote**, what the
code says (`file:line`), and the corrected statement. Then two lists: *checked and accurate*
(so the author does not re-litigate) and *suspected but unproven*, with what would settle it.
Finish with: would you block the merge, and if so on which items.
