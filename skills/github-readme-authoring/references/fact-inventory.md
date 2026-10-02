# Fact Inventory Checklist

Build this before writing a single README line. Every row ends with a source (`file:line`).
Anything you cannot source is deleted from the plan, not guessed.

## 1. Identity

| Fact | Where it lives |
|---|---|
| Project name, description, version | manifest (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`) |
| License (SPDX) | manifest `license` field |
| Minimum runtime/language version | manifest (`requires-python`, `engines`, `rust-version`) |
| Repo remote / canonical URL | `git remote -v` |

## 2. Capabilities (the feature cards)

Read the entry points and the modules behind each user-visible behavior. For every feature card write:

- what triggers it (command, input, file type)
- the module that implements it
- one concrete detail that proves it exists (limit, algorithm, table name, endpoint)

Cross-check against the *old* README's claims: mark each as **still true**, **stale**, or **unverifiable**.

## 3. Configuration

| Fact | Where it lives |
|---|---|
| Every variable name and effective default | the config loader (pydantic/viper/envconfig/argparse) |
| Which variables change behavior vs. cosmetics | the code that reads them |
| Format constraints (IDs, paths, URLs) | validators and the code that parses the value |

Do not copy defaults from `.env.example` comments — read the loader. State the value the process
actually uses when the variable is absent.

## 4. Operations

- install/build/run commands that exist (`Makefile`, `scripts/`, `package.json` scripts)
- service units, containers, CI workflows, and the real deploy directory
- update procedure, and the literal command a maintainer runs
- required external binaries and services, with how to verify each (`--version`, health probe)

## 5. User-visible behavior

- every command/menu/endpoint the product exposes
- hard limits (max file size, max items, timeouts) and their source constants
- error messages users actually see, and which failures are retryable
- privacy/scope constraints (e.g. "private chats only") taken from the router/guard code

## 6. Honest edges

- documented known limitations (issue tracker, `docs/LIMITATIONS.md`, code comments)
- anything the product promises users but does not implement — these are **code findings to report**,
  not README material
- measured numbers only (benchmarks, recorded timings). No estimate dressed as a measurement.

## 7. Completeness pass

Enumerate the public surface from the code (CLI parser, router registrations, route table,
exported API) and tick off each entry against your draft. Omitted capabilities are the most common
accuracy failure in a rewritten README.
