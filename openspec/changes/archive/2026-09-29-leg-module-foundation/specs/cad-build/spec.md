# Delta for CAD Build

## MODIFIED Requirements

### Requirement: Entry points and outputs

Only `hardware/cad/<part>/main.scad` files MUST be built; a directory without `main.scad` (for example the helper directory `hardware/cad/common/`) MUST NOT be built. `make stl` MUST write `build/stl/<part>.stl` for every part except those whose directory name starts with `asm-`; `make render` MUST write `build/png/<part>.png` at 1024x768 using `--autocenter --viewall --render` for every part, including `asm-*`. `asm-*` parts are preview-only and MUST NOT produce an STL.
(Previously: every part produced both an STL and a PNG; no helper-directory or preview-only rule.)

#### Scenario: Smoke part built

- GIVEN `hardware/cad/smoke/main.scad` exists
- WHEN `make stl render` runs
- THEN `build/stl/smoke.stl` and `build/png/smoke.png` exist and are non-empty

#### Scenario: Non-entry files ignored

- GIVEN a `.scad` file not named `main.scad`
- WHEN `make stl` runs
- THEN no output is produced for that file

#### Scenario: Assembly produces PNG only

- GIVEN `hardware/cad/asm-leg/main.scad` exists
- WHEN `make stl render` runs
- THEN `build/png/asm-leg.png` exists and is non-empty
- AND `build/stl/asm-leg.stl` does not exist

#### Scenario: Helper directory not built

- GIVEN `hardware/cad/common/` contains `.scad` files and no `main.scad`
- WHEN `make stl render` runs
- THEN no `build/stl/common.stl` or `build/png/common.png` is produced

### Requirement: Warnings gate

Builds MUST pass `--hardwarnings` and MUST scan OpenSCAD stderr for `WARNING|ERROR`; any match MUST fail the build, locally and in CI. `make gate-test` MUST prove the gate fires by building the warning fixture `tools/cad/fixtures/warning.scad`, and MUST also prove the torque gate fires by building the fixture `tools/cad/fixtures/torque-infeasible.scad`: that build MUST fail and its output MUST contain the message `torque budget exceeded`.
(Previously: `gate-test` proved only the warning fixture; the torque assertion had no proof of failure.)

#### Scenario: Warning fails build

- GIVEN a part that emits a WARNING
- WHEN `make stl` runs
- THEN the exit code is non-zero, even if OpenSCAD exits 0

#### Scenario: Gate-test proves the torque gate

- GIVEN the fixture `tools/cad/fixtures/torque-infeasible.scad` (tier M with the MG996R profile)
- WHEN `make gate-test` runs
- THEN building the fixture exits non-zero and its output contains `torque budget exceeded`
- AND `make gate-test` exits 0 only if both the warning fixture and the torque fixture fail as expected
