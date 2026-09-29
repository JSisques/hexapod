# Leg torque budget

Derivation of the torque gate that `hardware/cad/common/torque.scad` enforces on every leg part build. All figures are recomputed from the values in `hardware/cad/common/params.scad` (evaluated with OpenSCAD `echo`, not copied from the design notes). Every input is a guess until the leg is weighed and the servo is measured.

## Model and assumptions

- Static case: tripod stance, three legs on the ground, so one leg carries one third of the total mass.
- Peak case: the same load scaled by `k_dyn = 1.5` for gait dynamics.
- Femur joint: the load acts at the foot, at a horizontal lever of `femur_l * cos(alpha) + tibia_l * sin(phi)`, with `alpha = 0` (femur horizontal) and `phi = phi_nom = 20` deg (tibia angle from vertical).
- Tibia joint: lever `tibia_l * sin(phi)`.
- Allowable torque is the rated stall torque at the supply voltage times a derating: `derate_static = 0.6`, `derate_peak = 0.8`.
- Supply: `supply_v = 6.0` V. The 45 deg tibia case (`phi_stress`) is informational; it is echoed, never asserted.

## Mass model

`m_total = n_servo * m_servo + 6 * link_g_per_mm * (coxa + femur + tibia) / 1000 + m_body`

Inputs: `n_servo = 18`, `m_servo = 0.055 kg` (MG996R), `link_g_per_mm = 0.6`, `m_body = 0.52 kg` (body, electronics and battery; a guess).

For tier XS: `18 * 0.055 + 6 * 0.6 * 165 / 1000 + 0.52 = 2.104 kg`. Static leg force is `2.104 / 3 = 0.701 kgf`, peak `0.701 * 1.5 = 1.052 kgf`. Femur lever `5.5 + 8.0 * sin 20 = 8.236 cm`; tibia lever `2.736 cm`.

## Formulas

```
tau_femur = F * (femur_l * cos(alpha) + tibia_l * sin(phi)) / 10     [kg.cm, lengths in mm]
tau_tibia = F * tibia_l * sin(phi) / 10
allowable = stall(supply_v) * derate
```

The gate asserts `tau <= allowable` once per row (femur and tibia, static and peak). A failure prints `torque budget exceeded: <joint> <case> ...` and fails the build.

## Tier table (MG996R, 6 V, 11.0 kg.cm)

| Tier | [coxa, femur, tibia] mm | m_total kg | Femur static | Femur peak | Tibia static | Tibia peak | Result |
|---|---|---|---|---|---|---|---|
| XS | 30, 55, 80 | 2.104 | 5.78 / 6.60 (1.14) | 8.66 / 8.80 (1.02) | 1.92 / 6.60 (3.44) | 2.88 / 8.80 (3.06) | passes |
| S | 30, 60, 90 | 2.158 | 6.53 / 6.60 (1.01) | 9.80 / 8.80 (0.90) | 2.21 / 6.60 (2.98) | 3.32 / 8.80 (2.65) | fails (femur peak) |
| M | 35, 80, 120 | 2.356 | 9.51 / 6.60 (0.69) | 14.26 / 8.80 (0.62) | 3.22 / 6.60 (2.05) | 4.83 / 8.80 (1.82) | fails (femur) |
| L | 40, 100, 160 | 2.590 | 13.36 / 6.60 (0.49) | 20.04 / 8.80 (0.44) | 4.72 / 6.60 (1.40) | 7.09 / 8.80 (1.24) | fails (femur) |
| XL | 45, 130, 200 | 2.860 | 18.91 / 6.60 (0.35) | 28.37 / 8.80 (0.31) | 6.52 / 6.60 (1.01) | 9.78 / 8.80 (0.90) | fails (femur, tibia peak) |

Cells read `tau / allowable kg.cm (margin)`; margin is `allowable / tau`, and below 1.00 fails.

Minimum rated stall torque a servo needs at each tier (worst of `static / 0.6` and `peak / 0.8`, same mass model, servo mass kept at 55 g):

| Tier | Required stall (kg.cm) |
|---|---|
| XS | 10.8 |
| S | 12.2 |
| M | 17.8 |
| L | 25.0 |
| XL | 35.5 |

Medium and larger tiers therefore need a servo of roughly 20-30 kg.cm, such as the STS3215 at 12 V. That requires a new servo profile (see [ADR-0003](../adr/0003-leg-servo-abstraction-and-tiers.md)) and, for a 12 V bus, a different supply.

## Tier XS margins and the stall figure

The profile uses the TowerPro datasheet value (11.0 kg.cm at 6 V), not the retailer listing (13 kg.cm at 6 V) that the exploration used. Retailer clones tend to underperform their listing, so the derating is the margin, not an inflated rating.

| Joint | Case | tau | Allow at 11.0 | Margin | Allow at 13 | Margin |
|---|---|---|---|---|---|---|
| Femur | static (60%) | 5.78 | 6.60 | 1.14 | 7.80 | 1.35 |
| Femur | peak (80%) | 8.66 | 8.80 | 1.02 | 10.40 | 1.20 |
| Tibia | static | 1.92 | 6.60 | 3.44 | 7.80 | 4.06 |
| Tibia | peak | 2.88 | 8.80 | 3.06 | 10.40 | 3.61 |

**Finding: the femur peak margin is 1.02 (1.016 unrounded) at the datasheet figure.** The listing discrepancy (11.0 kg.cm datasheet against 13 kg.cm retailer) decides whether that margin is thin or comfortable, and the datasheet number is the one the gate uses.

## Sensitivity

- Mass headroom: the femur peak row reaches its limit at `m_total = 2.137 kg`, only about 33 g above the current 2.104 kg. Any calibrated mass above that fails CI.
- Contingency, not applied: `femur_l` 55 to 50 mm gives `m_total = 2.086 kg`, femur peak 8.07 kg.cm and margin 1.09. It is not applied because femur 55 mm is a confirmed product decision.
- `phi = 45` deg (stress pose): femur static 7.82 kg.cm, which exceeds 7.80 even at 13 kg.cm (femur peak 11.74). This is why 45 deg stays an echo, not an assert.

## Geometry and the torque model

Geometry does not enter the torque model: the gate reads only the tier lengths, `n_servo`, `link_g_per_mm` and `m_body_kg`. The interference fix (flat femur plates, femur servo body pointing down in the coxa bracket, `leg_lane_dy = -5`) leaves them untouched, so the femur peak margin stays 1.02 (`8.66 / 8.8 kg.cm`). The real mass per leg changes by about -5 to -10 g (the plate spacers and two M3 bolts go; the taller bracket web adds about 2 g), which the model ignores. Only the weighing in the calibration plan below captures it.

## Calibration plan

1. Weigh every printed part and the complete leg; replace `link_g_per_mm` and `m_body_kg`.
2. Measure the actual servo stall torque at 6 V on the bench; replace the profile figure if it differs.
3. Re-run `make gate-test` and any part build; the gate re-evaluates with the new inputs.
4. Supply sizing: `stall_a = 2.5 A` per servo, times 18 servos is 45 A worst case at 6 V; size the supply and wiring for the expected concurrent load, not for all servos stalled.

License: CC-BY-SA-4.0 — see [LICENSES/CC-BY-SA-4.0.txt](../../LICENSES/CC-BY-SA-4.0.txt)
