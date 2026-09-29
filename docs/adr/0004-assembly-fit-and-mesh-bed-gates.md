# ADR-0004: Assembly fit and mesh bed gates

## Status

Accepted

## Date

2026-09-29

## Context

The first leg passed every per-part gate but its parts interfered when assembled: the femur servo, coxa bracket, femur plates and tibia overlapped by up to about 2000 mm3 per pair in the servo command envelope, and nothing in CI could see it. The bed gate also relied on hand-written `*_size()` functions that could drift from the real geometry. This change adds an assembly fit check, moves the bed gate onto the exported mesh, and fixes the interference found.

## Decision

1. **Mesh bed gate.** Bed fit is checked on the exported ASCII STL (`tools/cad/stl-bbox.awk`, called by the `stl` recipe) against `bed_max`; a part that exceeds it fails and its STL is removed. The `*_size()` functions and the `size` argument of `leg_part_checks` are removed.
2. **check-fit.** `make check-fit` runs one OpenSCAD export per pose of the union of the `intersection()` of every distinct pair of the 8 assembly bodies (28 pairs), plus a sentinel cube so the top level is never empty. `tools/cad/stl-volume.awk` sums the signed volume of the closed shells; a pose passes when the total is at most `fit_vol_tol`. Pose STLs are cached targets in `build/fit/` and the check re-runs on every invocation. A failing pose is re-exported with `fit_diag` and reported per pair. It is never a prerequisite of `stl`.
   - Grid (narrowed by the user): `fit_alpha` [-30, 0, 30] x `fit_phi` [-15, 0, 20, 45], 12 poses. The originally proposed `fit_phi` [-30, 0, 20, 45] fails at `(alpha -30, phi -30)` by about 5.7 mm with B1.
   - Pose convention (D4): `alpha` is the femur pitch (knee up positive); `phi` is the knee joint angle from the femur-plate normal, equal to the torque-model `phi` at `alpha = 0`. The grid is the servo command envelope. A world-frame `phi` would demand a 75 degree knee angle at `alpha -30, phi 45`, which no same-lane design can clear.
   - Tolerance: `fit_vol_tol = 2.0` mm3 (first proposed 0.1 mm3). Eps-level model contacts measured 0.3 to 1.1 mm3 (`tibia x foot` 0.501, `coxa-bracket x tibia` 1.065); the smallest real interference measured 17.7 mm3. 2.0 mm3 separates them.
   - Axial gap: `leg_axial_gap = tol_fit` (0.2 mm) between plate B and the idler boss, in the assembly only. Plate B rotates against the boss, so a running clearance is physically right and it removes a zero-thickness contact sliver.
3. **gate-test.** Four fixtures (warning, torque-infeasible, bed-oversize, fit-interference) run through the `expect_fail` macro; each passes only when its own gate fails with the expected message.
4. **CI.** The `Fit check` step (`make check-fit` with `TOOLCHAIN=docker`, the pinned image) runs after `Gate test` in `.github/workflows/cad.yml`. Serial runtime measured at 1.4 to 2.3 minutes (12 poses), well inside the 20 minute job timeout, so no `-j` is used.
5. **ASCII STL export.** `--export-format asciistl` is used when the OpenSCAD binary supports it (the pinned `dev.2026-01-19` image does) so the awk gates can read vertices. Binaries without the flag already write ASCII. The Makefile runs awk with `LC_ALL=C` so a comma-decimal locale cannot truncate the numbers.
6. **Flat plates, pocket cut and plate A relief.** The femur plate spacers, bosses and bolts are deleted; both plates are flat two-disc hulls (`leg_plate_d`, `leg_plate_a_t`) and the servo cage plus the idler boss set the plate spacing (`leg_joint_span`). The coxa bracket subtracts the femur servo pocket (c1) and `leg_plate_a_relief()` (c3, the plate A femur-end sweep).
7. **B1 coxa bracket geometry.** The femur servo body points down inside the bracket cage: `femur_servo_frame()` spins the servo by `cb_femur_spin = -90` about its shaft, so the servo +X axis (far body end, slide-in slot, cable exit) maps to world -Z and the servo slides in from the open bottom rim. The femur axis, the coaxial idler boss, the plate femur ends, the knee position and `leg_joint_span` are unchanged. The web moves to `cb_web_x = coxa_l - 13.15 - wall` and spans z from `cb_zmin = cb_zmid - 40.9 = -17.8` to 51.9. `leg_lane_dy = -5` slides the joint along its own axis, so plate A (y -16.6 to -10.9) clears the coxa servo ear (y +/-9.85) by 1.05 mm; this closes the (c2) overlap without touching `coxa_l`, the tier lengths or the femur margin. The foot lateral offset changes from +3.7 to -1.3 mm.
   - Rationale: body up fails `(alpha 30, phi 45)` (the tibia end face lies inside the cage); a body tilted inboard still fails `(-30, -30)` and beyond about 15 degrees hits the coxa servo. Body down is the only same-lane orientation that clears the envelope the coxa servo leaves. B2 (tibia servo in its own lane with separate femur and tibia idler plates) was not needed.
   - Ear bolts run along world Y at x = 30 +/- 5 and z = 37.5 / -12.0. Head choice: low-profile heads on the plate A side (or the bolts fitted with the nut on the plate A side), because standard near-end heads (r 15.24 mm) would protrude about 0.4 mm into the plate A sweep (r 15.5 mm). Heads are not modelled; this is also true of the previous design.
   - Body keep-out: the bracket now reaches 12.1 mm below the bottom arm (z -5.7 down to -17.8, radius 10.85 to 43.15 mm from the coxa axis along X). The body must keep this region free below the bracket arm. The mount interface (`leg_mount_gap`, the arms, the femur axis height `cb_zmid` 23.1 mm) is otherwise unchanged; the bracket z-range grows from [-5.7, 51.9] (57.6 mm) to [-17.8, 51.9] (69.7 mm).
   - Printing: the print pose stands on the cage and web rim (`up(-cb_zmin)`). The bottom arm becomes a 12.1 mm overhang that needs supports. The mesh gate reports 58.65 x 54.80 x 69.70 mm, inside `bed_max` 180.

## Amendments

- ADR-0002 item 4 (entry points): `check-fit` is a new entry point and `build/fit/` (and `build/fit-diag/`) are new outputs; `hardware/cad/asm-leg/fit.scad` is a non-entry helper because it is not named `main.scad`.
- ADR-0002 item 5 (warnings gate proof): `make gate-test` now proves four gates (warnings, torque, bed, fit), not two.
- ADR-0002 item 6 (CI): the workflow runs `doctor`, `gate-test`, `check-fit`, then `stl render`.
- ADR-0003 item 5 (fasteners): no M3 spacers between the femur plates; M3 remains for servo ears, M4 for pivots.
- ADR-0003 item 6 (`asm-*`): `asm-leg` carries no bed assert; bed fit is now the mesh gate on printable parts. `asm-leg` hosts the posed-body library and the non-entry `fit.scad`.
- ADR-0003 item 7 (torque gate under `gate-test`): extended by decision 3 above; the torque model is untouched and the femur peak margin stays 1.02.

## Alternatives considered

- Analytic bed sizes: rejected, they can drift from the mesh.
- `--summary bounding-box` for the bed gate: rejected in favour of awk over the ASCII STL, which is present on runners and macOS.
- One OpenSCAD run for all poses; Python or trimesh; an "empty means pass" rule: rejected. Per-pose runs give pose-level diagnostics and parallelism without a new toolchain, and the sentinel avoids empty exports.
- Zero volume tolerance, or 0.1 mm3: rejected, below the eps-level model noise.
- World-frame `phi`, or the original grid with `phi -30`: rejected by the user (see decision 2).
- Femur servo body up, or tilted: rejected (decision 7).
- B2 (separate lane for the tibia servo): kept as the fallback only, needs a new plate topology.
- `coxa_l +4` for (c2): not applied; it would change tier lengths and drop the femur margin to about 1.009. `leg_lane_dy = -5` was sufficient.

## Consequences

- Assembly interference is now a CI failure. Any geometry change that overlaps bodies beyond 2.0 mm3 in the grid fails `check-fit`.
- CI time grows by about 1 to 2 minutes (measured job total 1m23s); ASCII STL artifacts are several times larger than binary ones.
- The flat plates lose out-of-plane stiffness (no spacers or bolts); physical validation is pending. The real mass change of about -5 to -10 g per leg is not in the torque model.
- The taller bracket needs supports and a body keep-out below the arm; the future body design must respect it.
- Servo dimensions stay PROVISIONAL, so the fit result holds only until the servo is measured; re-run `check-fit` after updating the profile.
