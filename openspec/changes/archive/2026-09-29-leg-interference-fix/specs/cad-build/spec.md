# Delta for CAD Build

## ADDED Requirements

### Requirement: Mesh bed-fit gate

The `stl` recipe MUST measure each exported ASCII STL with an awk script under `tools/cad/` and fail if any bounding-box extent exceeds `BED_MAX`. `BED_MAX` MUST be read from `params.scad` and MUST be overridable on the make command line. On failure the recipe MUST print a message containing `exceeds bed_max` and MUST remove the offending STL.

#### Scenario: Oversize mesh fails

- GIVEN a part whose mesh extent is above `BED_MAX`
- WHEN `make stl` runs
- THEN it exits non-zero, the output contains `exceeds bed_max`, and the STL file is removed

#### Scenario: Override respected

- GIVEN a default part of 100 mm
- WHEN `make stl BED_MAX=50` runs
- THEN the build fails with `exceeds bed_max`

#### Scenario: Default value from params

- GIVEN no override
- WHEN `make stl` runs
- THEN the limit equals `bed_max` in `params.scad` (180 mm)

### Requirement: Assembly fit check

`make check-fit` MUST be a phony target that exports, for each pose of `fit_alpha` x `fit_phi`, an intersection-based ASCII STL under `build/fit/`, with a sentinel object so an empty intersection still yields a parseable mesh. An awk script MUST compute the signed volume of each result and fail when it exceeds the fit volume tolerance, with a message containing `interference`. `check-fit` MUST NOT be a prerequisite of `make stl` and MUST NOT write to `build/stl/`.

#### Scenario: Clean assembly passes

- GIVEN an interference-free assembly
- WHEN `make check-fit` runs
- THEN it exits 0 and `build/fit/` holds one output per pose

#### Scenario: Interference fails

- GIVEN a pose with overlap volume above the tolerance
- WHEN `make check-fit` runs
- THEN it exits non-zero and the output contains `interference`

#### Scenario: Empty intersection is valid

- GIVEN a pose with no overlap
- WHEN its STL is measured
- THEN the sentinel keeps the file parseable and the volume is within tolerance

#### Scenario: Not part of stl

- GIVEN a failing assembly
- WHEN `make stl` runs
- THEN `check-fit` is not invoked and the build result is unaffected

## MODIFIED Requirements

### Requirement: Warnings gate

Builds MUST pass `--hardwarnings` and MUST scan OpenSCAD stderr for `WARNING|ERROR`; any match MUST fail the build, locally and in CI. `make gate-test` MUST prove, through an expect-fail check per fixture in `tools/cad/fixtures/`, that each gate fires: `warning.scad` (the warnings gate), `torque-infeasible.scad` (output contains `torque budget exceeded`), `fit-interference.scad` (output contains `interference`) and `bed-oversize.scad` (output contains `exceeds bed_max`). Each fixture build MUST fail, and `make gate-test` MUST exit 0 only if all four fail as expected.
(Previously: `gate-test` proved only the warning and torque fixtures.)

#### Scenario: Warning fails build

- GIVEN a part that emits a WARNING
- WHEN `make stl` runs
- THEN the exit code is non-zero, even if OpenSCAD exits 0

#### Scenario: Gate-test proves the torque gate

- GIVEN the fixture `tools/cad/fixtures/torque-infeasible.scad` (tier M with the MG996R profile)
- WHEN `make gate-test` runs
- THEN building the fixture exits non-zero and its output contains `torque budget exceeded`

#### Scenario: Gate-test proves the fit gate

- GIVEN the fixture `tools/cad/fixtures/fit-interference.scad`
- WHEN `make gate-test` runs
- THEN its build fails and the output contains `interference`

#### Scenario: Gate-test proves the bed gate

- GIVEN the fixture `tools/cad/fixtures/bed-oversize.scad`
- WHEN `make gate-test` runs
- THEN its build fails and the output contains `exceeds bed_max`

#### Scenario: All four must fail as expected

- GIVEN the four fixtures
- WHEN any one of them builds successfully
- THEN `make gate-test` exits non-zero
- AND it exits 0 only when all four fail with their expected messages
