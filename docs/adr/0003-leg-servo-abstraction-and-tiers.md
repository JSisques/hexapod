# ADR-0003: Leg servo abstraction and size tiers

## Status

Accepted

## Date

2026-09-29

## Context

ADR-0001 deferred the servo choice and left the CAD library undefined. The target servo class for the finished robot is a serial-bus servo such as the STS3215, but the first leg has to be designed and validated now with a cheap, available servo (MG996R). The MG996R dimensions in this repository come from generic drawings and are unmeasured. Leg size is also undecided: the same design should scale across several leg lengths. Accepted ADRs are immutable, so this ADR extends ADR-0001 and ADR-0002 without editing them. The servo driver decision stays deferred.

## Decision

1. **Servo profile abstraction.** A servo is a function returning a `[[key, value], ...]` table (`hardware/cad/common/servos/<name>.scad`), read only through the asserting getter `sv(profile, key)`. A missing or duplicated key fails the build with `key not found`. Parts never hard-code servo dimensions, so swapping a servo means writing a new profile and setting `servo = <profile>()` in `params.scad`.
2. **PROVISIONAL marker.** A profile carries `provisional = true` until its dimensions are measured. Every part build echoes `servo profile <name> is PROVISIONAL: dimensions unmeasured, measure the servo before printing`. Nothing is printed before the servo is measured.
3. **Size tiers.** `leg_tiers` defines XS, S, M, L and XL as `[coxa, femur, tibia]` lengths in mm. Tier XS (30, 55, 80) is the validation target, built with the MG996R.
4. **Torque gate.** `leg_torque_gate()` computes joint torques from a tripod-stance mass model and asserts `tau <= stall * derate` per joint and case: static at 60% and peak at 80% of the rated stall at the supply voltage, with a dynamic factor of 1.5. The stall figure is the datasheet value (11.0 kg.cm at 6 V), not the retailer listing (13 kg.cm). At tier XS the femur peak margin is 1.02. Tiers S and larger fail with the MG996R, and a medium or larger leg needs a 20-30 kg.cm servo profile. The derivation is in [leg-torque-budget.md](../architecture/leg-torque-budget.md).
5. **Fasteners and materials.** M3 for servo ears and spacers, M4 for pivots (nylock), with nut traps and heat-set insert pockets defined once in `fasteners.scad`. Parts print in PETG; the foot prints in TPU.
6. **`asm-*` convention.** A part directory whose name starts with `asm-` is a PNG-only assembly preview: `make render` builds it, `make stl` skips it, and it carries no bed-fit assert.
7. **Torque gate under `gate-test`.** `make gate-test` also builds `tools/cad/fixtures/torque-infeasible.scad` (tier M with the MG996R) and passes only when the build fails with `torque budget exceeded`. This extends ADR-0002 item 5 (warnings gate proof) to a second gate, and CI already runs `gate-test`, so no workflow change is needed.

## Alternatives considered

- **Prefixed global variables per servo:** rejected; not namespaced and not swappable.
- **BOSL2 `struct_val`:** rejected; a missing key returns `undef` silently.
- **Gate call inside `params.scad`:** rejected; including the file twice (assemblies) would run the checks twice. Checks run once, from each part's `main.scad`.
- **BOSL2 `screws.scad`:** rejected; it is not pulled in by `std.scad`, is heavier, and does not carry this project's nut and insert tolerances.
- **Retailer stall figure (13 kg.cm):** rejected; clones underperform, so the derating is the margin.
- **A separate CI step for the torque gate:** rejected; `gate-test` already runs in CI.
- **Shortening the femur to 50 mm for margin:** deferred; femur 55 mm is a confirmed product decision (margin would be 1.09).

## Consequences

- Tier XS with the MG996R passes with a thin femur peak margin (1.02): about 33 g of extra mass fails the build.
- Every printed part is provisional until the servo is measured; STL files exist only to validate the toolchain and geometry.
- Tiers M and larger need a new servo profile (about 20-30 kg.cm, for example STS3215 at 12 V) and a matching supply.
- The torque inputs (masses, dynamic factor) are guesses until calibrated, so the gate is a feasibility check, not a guarantee.
- The servo driver and control-bus decision remains deferred to a later ADR.

License: CC-BY-SA-4.0 — see [LICENSES/CC-BY-SA-4.0.txt](../../LICENSES/CC-BY-SA-4.0.txt)
