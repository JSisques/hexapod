# Delta for Repo Structure

## MODIFIED Requirements

### Requirement: Deferred scope excluded

The change MUST NOT add `params.scad` or real part designs. A BOSL2 submodule (`.gitmodules`), the smoke part `hardware/cad/smoke/main.scad`, the warnings-gate fixture `tools/cad/fixtures/warning.scad`, and `.github/workflows` are permitted.
(Previously: forbade the BOSL2 submodule, `params.scad`, any OpenSCAD parts, and CI workflows.)

#### Scenario: No deferred artifacts

- GIVEN the tree after the change
- WHEN searching for `params.scad`
- THEN it does not exist

#### Scenario: Only smoke part exists

- GIVEN the tree after the change
- WHEN searching for `hardware/cad/**/*.scad`
- THEN only `hardware/cad/smoke/main.scad` is found
