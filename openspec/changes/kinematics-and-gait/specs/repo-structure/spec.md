# Delta for Repo Structure

## MODIFIED Requirements

### Requirement: Per-directory README

Every directory in the skeleton MUST contain a `README.md` stating its purpose, so git tracks it. `firmware/` MUST be a stub with no source code. `software/` MUST keep its `README.md` and MAY contain Python source, tests and project configuration.
(Previously: `firmware/` and `software/` were both stubs with no source code.)

#### Scenario: README in each directory

- GIVEN the skeleton directories
- WHEN each is listed
- THEN each contains a non-empty `README.md`

#### Scenario: Firmware stub holds no code

- GIVEN `firmware/`
- WHEN its files are listed
- THEN only README files (and license notes) exist

#### Scenario: Software may hold Python

- GIVEN `software/`
- WHEN its files are listed
- THEN `README.md` exists and Python sources, tests and config are permitted

### Requirement: Deferred scope excluded

The change MUST NOT add firmware source code, body designs, or electronics designs. Python source, tests and configuration under `software/`, the committed parameter snapshot and the params exporter source are permitted. A BOSL2 submodule (`.gitmodules`), the smoke part `hardware/cad/smoke/main.scad`, the warnings-gate fixture `tools/cad/fixtures/warning.scad`, the torque-gate fixture `tools/cad/fixtures/torque-infeasible.scad`, the fit-gate fixture `tools/cad/fixtures/fit-interference.scad`, the bed-gate fixture `tools/cad/fixtures/bed-oversize.scad`, any awk script under `tools/cad/`, `.github/workflows`, the shared helper directory `hardware/cad/common/` (including `params.scad`), and the leg part directories under `hardware/cad/` (`leg-*`, `asm-leg`) are permitted. `firmware/` MUST remain a stub.
(Previously: `software/` also had to remain a stub and software source code was excluded; no snapshot or exporter was permitted.)

#### Scenario: No deferred artifacts

- GIVEN the tree after the change
- WHEN searching `firmware/` for source files
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
- AND any other file is an awk script or the params exporter source
