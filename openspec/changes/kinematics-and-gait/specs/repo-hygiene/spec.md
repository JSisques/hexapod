# Delta for Repo Hygiene

## MODIFIED Requirements

### Requirement: Editor conventions

A root `.editorconfig` MUST exist, set `root = true`, and define indentation and end-of-line/final-newline rules for all files. Makefiles MUST use tab indentation. Python files (`[*.py]`) MUST use 4-space indentation.
(Previously: only the Makefile tab rule; no Python rule.)

#### Scenario: Config present

- GIVEN the repo root
- WHEN `.editorconfig` is read
- THEN it contains `root = true` and a `[Makefile]` section using tabs

#### Scenario: Python indentation

- GIVEN the `.editorconfig`
- WHEN the `[*.py]` section is read
- THEN it sets spaces with `indent_size = 4`

### Requirement: Makefile entry point

A root `Makefile` MUST provide `help` as the default goal, listing all targets. `stl`, `render`, `clean` (see `cad-build`) and `software` (see `software-tooling`) MUST be real targets. The remaining targets (`firmware`, `docs`) MUST be placeholders that print "not implemented" and exit with a non-zero status.
(Previously: `software` was a placeholder.)

#### Scenario: Default goal lists targets

- GIVEN the repo root
- WHEN `make` runs with no arguments
- THEN it exits 0 and prints the available targets

#### Scenario: Placeholder target

- GIVEN a placeholder target such as `firmware`
- WHEN `make firmware` runs
- THEN the output contains "not implemented" and the exit code is non-zero (the recipe exits 1; make itself reports 2)

#### Scenario: CAD targets are real

- GIVEN the repo root
- WHEN `make clean` runs
- THEN it exits 0 and does not print "not implemented"

#### Scenario: Software target is real

- GIVEN a prepared Python environment
- WHEN `make software` runs
- THEN it runs ruff, mypy and pytest and does not print "not implemented"

## ADDED Requirements

### Requirement: Python artifacts ignored

`.gitignore` MUST ignore Python caches and virtual environments (`__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.venv/`) and MUST NOT ignore the committed parameter snapshot.

#### Scenario: Cache ignored

- GIVEN `software/.pytest_cache/x`
- WHEN `git check-ignore` runs on it
- THEN it is reported as ignored

#### Scenario: Snapshot tracked

- GIVEN the committed parameter snapshot
- WHEN `git check-ignore` runs on it
- THEN it is not ignored
