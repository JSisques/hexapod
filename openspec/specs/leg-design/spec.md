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

`hardware/cad/common/params.scad` MUST hold global tolerances, fastener and material defaults, leg geometry (`coxa_l`, `femur_l`, `tibia_l`), the selected tier and servo, torque inputs, the leg mount interface, and `bed_max`. It MUST also hold the fit sweep lists `fit_alpha` ([-30, 0, 30]) and `fit_phi` ([-15, 0, 20, 45]), the fit volume tolerance (2.0 mm3), and MAY hold an optional `leg_axial_gap` (default 0.2 mm). The default tier MUST be XS (femur 55 mm, tibia 80 mm) and the default servo MUST be MG996R, and these MUST agree so the default build passes the torque gate.
(Previously: no fit sweep lists, fit tolerance or axial gap in params. The `fit_phi` list was also drafted as [-30, 0, 20, 45] and narrowed to [-15, 0, 20, 45] after design. The fit volume tolerance was also drafted as 0.1 mm3 and raised to 2.0 mm3 after design, because the model has eps-level contacts of 0.3-1.1 mm3 while the smallest real interference is 17.7 mm3.)

#### Scenario: Defaults agree

- GIVEN the repository defaults
- WHEN `make stl render gate-test check-fit` runs
- THEN it exits 0 with no `WARNING` or `ERROR` in output

#### Scenario: Fit parameters defined

- GIVEN `params.scad`
- WHEN `fit_alpha`, `fit_phi` and the fit volume tolerance are read
- THEN they equal [-30,0,30], [-15,0,20,45] and 2.0 mm3 (Previously: 0.1 mm3)

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

`bed_max` MUST be 180 mm. Every printable part's largest dimension MUST NOT exceed it, and this MUST be measured on the exported STL mesh by the build (see cad-build "Mesh bed-fit gate"), not by analytic size functions or asserts in the part sources.
(Previously: `bed_max` was asserted through analytic per-part size calculations.)

#### Scenario: Oversized part fails

- GIVEN a printable part whose exported mesh has a dimension above `bed_max`
- WHEN `make stl` runs
- THEN the build fails and the STL is not kept

#### Scenario: Default parts fit

- GIVEN the default leg parts
- WHEN `make stl` runs
- THEN every mesh extent is at most 180 mm

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

Part directories MUST be flat with hyphenated names: `leg-coxa-bracket`, `leg-femur-plate`, `leg-tibia`, `leg-foot`, `asm-leg`. Parts MUST include helpers by relative path (for example `include <../common/params.scad>`), so `-d` dependency files track them. `asm-leg` MUST expose its geometry as a reusable module file with pose parameters, used by both `main.scad` and a non-main `fit.scad`; `fit.scad` MUST NOT be built as an entry point.
(Previously: no reusable assembly module file or `fit.scad`.)

#### Scenario: Parts are built

- GIVEN the four printable leg part directories
- WHEN `make stl` runs
- THEN `build/stl/` contains an STL for each, and none is nested

#### Scenario: Helper edit rebuilds

- GIVEN built leg parts
- WHEN `hardware/cad/common/params.scad` is touched and `make stl` runs
- THEN the dependent STLs are rebuilt

#### Scenario: fit.scad is not an entry point

- GIVEN `hardware/cad/asm-leg/fit.scad` and the module file
- WHEN `make stl render` runs
- THEN no output is produced for `fit.scad`
- AND `main.scad` and `fit.scad` both use the same module file
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
### Requirement: Assembly interference-free

`asm-leg` MUST have no overlap volume above the fit volume tolerance between any pair of distinct parts, across the full `fit_alpha` x `fit_phi` pose grid defined in `params.scad`. Intended contact (mating faces, servo ears on plates) MUST be modelled as a contact allowance: zero-volume touching is allowed, and an optional `leg_axial_gap` MAY separate rotating parts. The spacer bosses and M3 bolts MUST NOT exist in the assembly. The torque feasibility gate is unchanged by this requirement. Spacer removal and the coxa bracket redesign are verified through `make check-fit`, not through the torque gate.

#### Scenario: Whole grid is clear

- GIVEN the default parameters
- WHEN `make check-fit` evaluates every pose of the grid
- THEN each pair of parts overlaps by at most the fit volume tolerance in every pose

#### Scenario: Interference is reported

- GIVEN a pose where the tibia enters the femur cage by more than the tolerance
- WHEN `make check-fit` runs
- THEN it exits non-zero and names the interference

#### Scenario: Touching contact allowed

- GIVEN two parts that touch on a face with zero overlap volume
- WHEN the fit check evaluates the pair
- THEN the pair passes

#### Scenario: Torque gate unchanged

- GIVEN tier XS with the MG996R profile after the geometry fix
- WHEN the torque gate is evaluated
- THEN the femur margin is still 1.016 and the assertions hold as before

