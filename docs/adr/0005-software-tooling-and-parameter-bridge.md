# ADR-0005: Software tooling and parameter bridge

## Status

Accepted

## Date

2026-09-30

## Context

Roadmap phase 2 adds leg and body kinematics and a gait engine under `software/`. The numbers that define the leg (link lengths, joint limits, servo data) already live in the OpenSCAD model. Copying them by hand into Python would let the two drift apart without any check noticing. The repository also needs a reproducible Python toolchain and a CI check that does not depend on the CAD toolchain.

## Decision

1. **Toolchain.** `software/` is a Python 3.12 project with a `src` layout. Runtime dependency: numpy. Dev tooling, pinned exactly in `software/pyproject.toml`: pytest, ruff, mypy and matplotlib. The environment is a plain `venv` (`software/.venv`) created and populated by `make software`; the interpreter is `PYTHON` (default `python3.12`).
2. **Quality gate.** `make software` runs `ruff check`, `ruff format --check`, `mypy --strict` and `pytest`, and exits non-zero if any fails. Strict TDD is enabled in `openspec/config.yaml`: tests are written before the code.
3. **CI.** A separate workflow, `.github/workflows/software.yml`, runs `make software` with Python 3.12. It has no path filters, so the check always reports a status and never stays pending on a required check. It requests `contents: read` only.
4. **Parameter sharing.** The CAD model stays the single source of truth. A small OpenSCAD exporter evaluates the real leg assembly and echoes one parameter record; a stdlib-only converter turns the echo into JSON; the Python package loads that snapshot. Python never parses `.scad` sources. The bridge ships in this change: exporter, converter, committed snapshot, loader and drift gate.
5. **Committed generated JSON (exception).** The repository does not commit generated artifacts (STL, PNG). The parameter snapshot `software/src/hexapod/data/leg-params.json` is the single exception: it is package data that the library needs at runtime and that a reviewer can read and diff. A CI drift check regenerates it and fails on any difference, so it cannot go stale. `.gitignore` does not ignore it.
6. **Conventions.** Pure numpy functions, degrees, CAD frames and CAD angle names. Values that are not yet backed by a real part are marked PROVISIONAL and the flag propagates to every report and plot.

## Alternatives considered

- **uv instead of pip + venv.** Faster, but adds a tool to install. Pinned pins in `pyproject.toml` already give reproducibility, and switching later is cheap.
- **Parsing `params.scad` in Python.** Cannot see values that only exist after evaluation (derived offsets, foot geometry) and duplicates the OpenSCAD grammar.
- **Hand-copied constants.** Simple, but silent drift between model and software.
- **Path filters on the workflow.** Saves runner minutes, but a required check that is skipped stays pending.
- **A job inside `cad.yml`.** Couples Python failures to the slow CAD job and its container toolchain.

## Consequences

- One command, `make software`, is the local and CI gate for Python code.
- Contributors need Python 3.12 (or pass `PYTHON=`); nothing else is installed globally.
- The committed JSON snapshot must be regenerated whenever the CAD parameters change; the drift check enforces it.
- Repository hygiene rules are extended: `.editorconfig` gains a `[*.py]` section (4 spaces) and `.gitignore` ignores Python environments and caches.
