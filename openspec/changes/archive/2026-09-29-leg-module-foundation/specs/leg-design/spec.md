# Leg Design Specification

## Purpose

Define the parametric hexapod leg foundation: servo profile contract, provisional marker, torque feasibility gate, default tier, bed fit, and fastener and material defaults.

## Requirements

### Requirement: Servo profile contract

A servo profile MUST be a function returning a list of `[key, value]` pairs, defined in `hardware/cad/common/servos/<name>.scad`. It MUST provide at least: identity (`name`, `provisional`, `source`), body dimensions, ear span, thickness and hole pattern, output shaft offsets and horn geometry, cable exit, electrical data (mass, stall torque per voltage, voltage, stall current), and clearances. Axis conventions MUST be normalised inside profile files only.

#### Scenario: Profile exposes required fields

- GIVEN the MG996R profile function
- WHEN each required key is read through the getter
- THEN every key returns a defined value

### Requirement: Asserting getter

`hardware/cad/common/servo.scad` MUST provide a getter over a profile that asserts when a key is missing, rather than returning `undef`. Parts MUST read servo data only through this getter and MUST NOT hard-code servo dimensions outside profile files.

#### Scenario: Missing key fails

- GIVEN a profile lacking key `x`
- WHEN the getter is called with `x`
- THEN the build fails with an assertion naming the missing key

#### Scenario: No hard-coded servo dimensions

- GIVEN the leg part sources
- WHEN searched for servo body or ear dimension literals
- THEN none are found outside `hardware/cad/common/servos/`

### Requirement: Provisional profile marker

A profile with unverified dimensions MUST set `provisional=true`. Using a provisional profile MUST emit an `echo` stating it is provisional and that dimensions must be measured before printing. A provisional profile MUST NOT fail the default `make stl`.

#### Scenario: MG996R is provisional

- GIVEN the MG996R profile
- WHEN `provisional` is read
- THEN it is `true`

#### Scenario: Echo emitted, build passes

- GIVEN the default configuration using the MG996R profile
- WHEN `make stl` runs
- THEN the output contains the provisional echo
- AND the build exits 0

### Requirement: Params location and defaults

`hardware/cad/common/params.scad` MUST hold global tolerances, fastener and material defaults, leg geometry (`coxa_l`, `femur_l`, `tibia_l`), the selected tier and servo, torque inputs, the leg mount interface, and `bed_max`. The default tier MUST be XS (femur 55 mm, tibia 80 mm) and the default servo MUST be MG996R, and these MUST agree so the default build passes the torque gate.

#### Scenario: Defaults agree

- GIVEN the repository defaults
- WHEN `make stl render gate-test` runs
- THEN it exits 0 with no `WARNING` or `ERROR` in output

### Requirement: Torque feasibility gate

`hardware/cad/common/torque.scad` MUST assert per joint (femur and tibia) that the required torque is within the allowed fraction of the servo stall torque at the profile voltage: 60% for static load and 80% for peak load. The model MUST use `F = (m_total/3) * k_dyn` with `k_dyn` 1.5 and nominal leg angle phi of 20 degrees. An infeasible combination MUST fail the build through `assert`.

#### Scenario: Infeasible tier fails

- GIVEN tier M (femur 80 mm, tibia 120 mm) with the MG996R profile
- WHEN `make stl` runs
- THEN the build exits non-zero due to the torque assertion

#### Scenario: Feasible default passes

- GIVEN tier XS with the MG996R profile
- WHEN the torque gate is evaluated
- THEN the femur and tibia assertions hold at 60% static and 80% peak

### Requirement: Bed size fit

`bed_max` MUST be 180 mm and MUST be asserted: every printable part's largest dimension MUST NOT exceed it.

#### Scenario: Oversized part fails

- GIVEN a printable part with a dimension above `bed_max`
- WHEN it is built
- THEN the build fails through the assertion

### Requirement: Fastener and material defaults

Fasteners MUST default to M3 with M4 for pivots, nuts on structural joints, and heat-set inserts only where a joint is re-driven often. The default material MUST be PETG, with TPU for the foot. Fastener dimensions MUST live in `hardware/cad/common/fasteners.scad` or `params.scad`.

#### Scenario: Foot material

- GIVEN the leg part list
- WHEN the foot part is inspected
- THEN it is documented as TPU and the other printable parts as PETG

### Requirement: Helper directory

Shared code MUST live in `hardware/cad/common/` and MUST NOT contain a `main.scad`.

#### Scenario: No entry point in common

- GIVEN `hardware/cad/common/`
- WHEN listing its files
- THEN no `main.scad` exists at any level

### Requirement: Part naming and inclusion

Part directories MUST be flat with hyphenated names: `leg-coxa-bracket`, `leg-femur-plate`, `leg-tibia`, `leg-foot`, `asm-leg`. Parts MUST include helpers by relative path (for example `include <../common/params.scad>`), so `-d` dependency files track them.

#### Scenario: Parts are built

- GIVEN the four printable leg part directories
- WHEN `make stl` runs
- THEN `build/stl/` contains an STL for each, and none is nested

#### Scenario: Helper edit rebuilds

- GIVEN built leg parts
- WHEN `hardware/cad/common/params.scad` is touched and `make stl` runs
- THEN the dependent STLs are rebuilt

### Requirement: Echo and assert text hygiene

`echo` and `assert` message text MUST NOT contain `WARNING` or `ERROR`, so the warnings gate triggers only on a real assertion failure or OpenSCAD warning.

#### Scenario: Provisional echo does not trip gate

- GIVEN the provisional echo is emitted
- WHEN the stderr gate scans output
- THEN no `WARNING|ERROR` match occurs

#### Scenario: Assertion failure is detected

- GIVEN an assertion fails
- WHEN the gate scans stderr
- THEN the failure is matched and the build fails
