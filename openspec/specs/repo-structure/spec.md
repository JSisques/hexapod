# Repo Structure Specification

## Purpose

Define the top-level per-domain layout, per-directory READMEs, and the root repo map.

## Requirements

### Requirement: Domain directory skeleton

The repository MUST contain these directories: `hardware/cad`, `hardware/electronics`, `hardware/bom`, `firmware`, `software`, `docs/architecture`, `docs/build-guide`, `docs/adr`, `tools`, `libs`.

#### Scenario: All directories present

- GIVEN a fresh checkout after the change
- WHEN each listed path is checked
- THEN every path exists as a directory tracked by git

### Requirement: Per-directory README

Every directory in the skeleton MUST contain a `README.md` stating its purpose, so git tracks it. `firmware/` and `software/` MUST be stubs with no source code.

#### Scenario: README in each directory

- GIVEN the skeleton directories
- WHEN each is listed
- THEN each contains a non-empty `README.md`

#### Scenario: Stubs hold no code

- GIVEN `firmware/` and `software/`
- WHEN their files are listed
- THEN only README files (and license notes) exist

### Requirement: Root README repo map

The root `README.md` MUST replace the one-line README and MUST list every top-level domain directory with a one-line description.

#### Scenario: Map covers every directory

- GIVEN the root `README.md`
- WHEN it is compared with the top-level directories `hardware`, `firmware`, `software`, `docs`, `tools`, `libs`
- THEN each appears in the repo map with a description

### Requirement: Deferred scope excluded

The change MUST NOT add a BOSL2 submodule, `params.scad`, sample OpenSCAD parts, or CI workflows.

#### Scenario: No deferred artifacts

- GIVEN the tree after the change
- WHEN searching for `.gitmodules`, `params.scad`, `*.scad`, and `.github/workflows`
- THEN none exist
