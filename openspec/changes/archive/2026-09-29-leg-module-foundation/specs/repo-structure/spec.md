# Delta for Repo Structure

## MODIFIED Requirements

### Requirement: Deferred scope excluded

The change MUST NOT add firmware or software source code, body designs, or electronics designs. A BOSL2 submodule (`.gitmodules`), the smoke part `hardware/cad/smoke/main.scad`, the warnings-gate fixture `tools/cad/fixtures/warning.scad`, the torque-gate fixture `tools/cad/fixtures/torque-infeasible.scad`, `.github/workflows`, the shared helper directory `hardware/cad/common/` (including `params.scad`), and the leg part directories under `hardware/cad/` (`leg-*`, `asm-leg`) are permitted. `firmware/` and `software/` MUST remain stubs.
(Previously: forbade `params.scad` and any OpenSCAD parts other than the smoke part.)

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
