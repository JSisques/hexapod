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

The change MUST NOT add firmware or software source code, body designs, or electronics designs. A BOSL2 submodule (`.gitmodules`), the smoke part `hardware/cad/smoke/main.scad`, the warnings-gate fixture `tools/cad/fixtures/warning.scad`, the torque-gate fixture `tools/cad/fixtures/torque-infeasible.scad`, the fit-gate fixture `tools/cad/fixtures/fit-interference.scad`, the bed-gate fixture `tools/cad/fixtures/bed-oversize.scad`, any awk script under `tools/cad/`, `.github/workflows`, the shared helper directory `hardware/cad/common/` (including `params.scad`), and the leg part directories under `hardware/cad/` (`leg-*`, `asm-leg`) are permitted. `firmware/` and `software/` MUST remain stubs.
(Previously: only the warning and torque fixtures were permitted; no fit or bed fixtures and no awk scripts.)

#### Scenario: No deferred artifacts

- GIVEN the tree after the change
- WHEN searching `firmware/` and `software/` for source files
- THEN only README files (and license notes) are found
- AND no body or electronics design files exist

#### Scenario: Only permitted CAD sources exist

- GIVEN the tree after the change
- WHEN searching for `hardware/cad/**/*.scad`
- THEN every file is under `hardware/cad/smoke/`, `hardware/cad/common/`, `hardware/cad/leg-*/`, or `hardware/cad/asm-leg/`

#### Scenario: Shared params permitted in common

- GIVEN the tree after the change
- WHEN searching for `params.scad`
- THEN it exists only at `hardware/cad/common/params.scad`

#### Scenario: Only permitted tooling files exist

- GIVEN the tree after the change
- WHEN listing `tools/cad/`
- THEN fixtures are limited to `warning`, `torque-infeasible`, `fit-interference` and `bed-oversize`
- AND any other file is an awk script
