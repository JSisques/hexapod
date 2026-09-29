# Repo Hygiene Specification

## Purpose

Define ignore rules, editor conventions, and the base Makefile entry point.

## Requirements

### Requirement: Generated artifacts ignored

`.gitignore` MUST ignore `build/`, generated `*.stl`, and generated `*.png`. Git LFS MUST NOT be used.

#### Scenario: Build output ignored

- GIVEN files `build/out.stl` and `build/render.png`
- WHEN `git status` runs
- THEN neither file is listed as untracked

#### Scenario: Stray STL ignored

- GIVEN a file `hardware/cad/part.stl`
- WHEN `git check-ignore` runs on it
- THEN it is reported as ignored

### Requirement: Editor conventions

A root `.editorconfig` MUST exist, set `root = true`, and define indentation and end-of-line/final-newline rules for all files. Makefiles MUST use tab indentation.

#### Scenario: Config present

- GIVEN the repo root
- WHEN `.editorconfig` is read
- THEN it contains `root = true` and a `[Makefile]` section using tabs

### Requirement: Makefile entry point

A root `Makefile` MUST provide `help` as the default goal, listing all targets. Other targets MUST be placeholders that print "not implemented" and exit with a non-zero status.

#### Scenario: Default goal lists targets

- GIVEN the repo root
- WHEN `make` runs with no arguments
- THEN it exits 0 and prints the available targets

#### Scenario: Placeholder target

- GIVEN a placeholder target such as `stl`
- WHEN `make stl` runs
- THEN the output contains "not implemented" and the exit code is non-zero (1)
