# CAD

OpenSCAD parts and assemblies.

## Part convention

- Each part lives in its own directory: `hardware/cad/<part>/`, where `<part>` uses only `[a-z0-9-]`.
- The entry point is `hardware/cad/<part>/main.scad`. Other `.scad` files are helpers and are never built on their own.
- Use BOSL2 with `include <BOSL2/std.scad>`; `make` sets `OPENSCADPATH=libs`.

## Outputs

- `make stl` writes `build/stl/<part>.stl` as ASCII STL and checks the mesh bounding box against `bed_max` (parts that exceed it fail and the STL is removed).
- `make render` writes `build/png/<part>.png` (1024x768).
- `smoke/` is a minimal part that proves the toolchain works.
- Directories named `asm-*` are assembly previews: `make render` builds their PNG, `make stl` skips them, and they have no bed-fit check.

## Leg module

The first leg (tier XS, 3 DOF) is built from the shared library and four printable parts plus one preview.

| Path | Role |
|---|---|
| `common/` | Helper library, no `main.scad`, never built on its own: `params.scad` (tolerances, tiers, torque inputs), `servo.scad`, `fasteners.scad`, `torque.scad`, `servos/<name>.scad` (servo profiles) |
| `leg-coxa-bracket/`, `leg-femur-plate/`, `leg-tibia/`, `leg-foot/` | Printable parts |
| `asm-leg/` | Coloured assembly preview in the torque-model pose (PNG only); `asm-leg.scad` is the posed-body library and `fit.scad` (not an entry point) is the fit check scene |

Each part directory holds a geometry module file (`<name>.scad`) that `asm-leg` reuses, and a thin `main.scad` that runs the checks (provisional echo, torque gate) and places the part in its print pose. Library files define only functions, modules and variables, so including them twice is silent.

## Provisional servo profile

The MG996R profile (`common/servos/mg996r.scad`) is **PROVISIONAL**: its dimensions come from generic drawings and are unmeasured. Every part build echoes a `PROVISIONAL` line. **Do not print any part before measuring the servo** and updating the profile (then set `provisional = false`).

## Torque gate

Every part build runs `leg_torque_gate()`, which asserts the joint torques against the derated servo stall torque and fails with `torque budget exceeded: ...`. `-D check_torque=false` skips it for exploration only; CI never sets it. At tier XS the femur peak margin is only 1.02. See [leg-torque-budget.md](../../docs/architecture/leg-torque-budget.md) and [ADR-0003](../../docs/adr/0003-leg-servo-abstraction-and-tiers.md).

## Materials

| Part | Material |
|---|---|
| Coxa bracket, femur plates, tibia | PETG |
| Foot | TPU |

Fasteners: M3 for servo ears (no plate spacers; the flat femur plates are held apart by the servo cage and the idler boss), M4 (nylock) for pivots. Femur servo ear bolts run along world Y with the nuts trapped on the cage floor; use low-profile heads on the plate A side (see the bracket source and ADR-0004).

## Print list (per leg, x6 legs)

| Part | Per leg | Total for the robot |
|---|---|---|
| `leg-coxa-bracket` | 1 | 6 |
| `leg-femur-plate` (plates A and B in one file) | 1 | 6 |
| `leg-tibia` | 1 | 6 |
| `leg-foot` (TPU) | 1 | 6 |

## Swapping the servo or the tier

- Servo: add `common/servos/<name>.scad` with the same keys as `mg996r.scad`, include it in `params.scad`, and set `servo = <name>();`. A missing key fails with `key not found`.
- Tier: set `leg_tier` in `params.scad` (`XS`, `S`, `M`, `L`, `XL`) or pass `-D 'leg_tier="S"'`. Only XS passes the gate with the MG996R; larger tiers need a stronger servo profile.

## Warnings gate

Any OpenSCAD `WARNING` or `ERROR` fails the build, locally and in CI. `make gate-test` proves the four gates (warnings, torque, bed, fit) still fire, each on its own fixture in `tools/cad/fixtures/`. See [ADR-0002](../../docs/adr/0002-openscad-toolchain.md).

## Fit check

`make check-fit` exports one intersection STL per pose to `build/fit/` and sums the signed volume of all body-pair overlaps (28 pairs of the 8 assembly bodies) with awk. A pose passes when the total is at most `fit_vol_tol` (2.0 mm3, above the eps-level model contacts of 0.3-1.1 mm3 and below the smallest real interference of 17.7 mm3). The grid is `fit_alpha` [-30, 0, 30] x `fit_phi` [-15, 0, 20, 45] in `common/params.scad` (12 poses, about 3.5 minutes serial). `alpha` is the femur pitch (knee up positive) and `phi` the knee joint angle from the femur-plate normal. A failing pose is re-exported with `fit_diag` and reported pair by pair. `TOOLCHAIN=docker make check-fit` runs it in the pinned image, and CI runs it after `gate-test`. See [ADR-0004](../../docs/adr/0004-assembly-fit-and-mesh-bed-gates.md).

## Coxa bracket mount interface

The femur servo body points down inside the bracket cage (B1), so the bracket reaches 12.1 mm below the bottom arm: z-range [-17.8, 51.9] mm in the leg frame (69.7 mm tall), at 10.85 to 43.15 mm from the coxa axis along X. The body must keep that region free below the bottom arm. The arm, the M4 pivot and the femur axis height (`cb_zmid` 23.1 mm) are unchanged. Print the bracket on its cage and web rim; the bottom arm is then a 12.1 mm overhang that needs supports.

STL and PNG files are build outputs produced by `make` and CI. They are never committed.

License: CC-BY-SA-4.0 — see [LICENSES/CC-BY-SA-4.0.txt](../../LICENSES/CC-BY-SA-4.0.txt)
