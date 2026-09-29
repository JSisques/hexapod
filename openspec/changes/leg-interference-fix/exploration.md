# Exploration: leg-interference-fix

Note: all geometry numbers below are hand-derived from source (no OpenSCAD run in the exploration); the pinned image and the sweep must confirm them.

## Current State
- Torque gate depends only on lengths (`coxa_l`, `femur_l`, `tibia_l`), `n_servo`, `m_body_kg`; geometry changes that keep `[30,55,80]` cannot break or help it (femur peak margin stays 1.016). Real mass is not modelled.
- Bed check: `leg_part_checks(name, size)` asserts `max(size) <= bed_max` using analytic `*_size()` functions; OpenSCAD cannot measure geometry in-language.
- `asm-leg/main.scad` places bodies in two frames and models only `phi_nom`; no femur angle alpha, no sweep.
- Kinematic groups: coxa bracket and femur servo are fixed for the femur joint; plates A/B, tibia servo, tibia and foot rotate about the femur axis (alpha); tibia servo, tibia and foot also rotate about the knee axis (phi); coxa servo is body-fixed.

## Root causes (hand-derived)
- (b) tibia vs coxa-bracket femur cage: clearance `clr(phi) = 14.1 - 13.15*(1+sin phi)/cos phi` gives -4.68 mm at 20 deg (matches verify's 4.7 mm). Zero at ~2 deg; 0.95 mm at phi 0. Trimming the cage or flipping the tibia servo cannot clear 20 deg (ear bolts at x=35.1 with nut traps). Lengthening the femur fails torque (femur_l 60 -> margin ~0.94). This is an architectural limit: two 40.7 mm servos in the same Y-lane only 55 mm apart.
- (a) spacers sit inside the femur servo body and inside the tibia cage swept disc; no free position exists during motion. They look kinematically redundant (plate B is a rigid 2-pin link); their only role is out-of-plane stiffness.
- (c1) femur servo vs bracket: the web is unioned outside `servo_cage`'s pocket difference; fix by subtracting the femur `servo_pocket` from the whole bracket.
- (c2) coxa servo ear tip vs plate A occurs at every alpha; needs `coxa_l` +3-4 mm, rotating the coxa servo 90 deg, or being absorbed by a bracket redesign.
- Tibia vs femur plate contact: idler boss end face on plate B at exactly `leg_joint_span`; numerically noisy zero-thickness sliver in the yrot(-110) frame, so a volume tolerance is the right allowance.

## 1. Interference detection
| Approach | Verdict |
|---|---|
| **A. scad `intersection()` per pose exported as ASCII STL, awk signed-volume test, sentinel object** | Recommended. No new deps; fits the `scad` macro and warnings gate. |
| B. Inverted "empty top-level = pass" | Fragile (empty export exits 1, WARNING under --hardwarnings). |
| C. Python/trimesh | Adds a toolchain the repo lacks. |
| D. `--summary bounding-box` | Bbox only; cannot separate slivers from real overlaps. |

Design for A: refactor `asm-leg` into `asm-leg/asm-leg.scad` (one module per body with pose args) plus non-main `fit.scad`; sentinel 1 mm cube at [-1000,-1000,-1000] keeps top-level non-empty; awk sums signed tetrahedron volumes, fails above `FIT_VOL_TOL` (suggested 0.1 mm3); per-pair diagnostics only on failure. Sweep grid: `fit_alpha` [-30,0,30] x `fit_phi` [-15,0,20,45] (narrowed after design; previously [-30,0,20,45]) (yaw excluded; body out of scope). New phony `make check-fit` (outputs `build/fit/`), CI step after `gate-test`; not a prerequisite of `make stl`. Proof fixtures: `tools/cad/fixtures/fit-interference.scad` (overlapping cubes) and optional touching-cubes fixture; `gate-test` refactored with an `expect_fail` macro. Optional 0.2 mm axial gap (`leg_axial_gap = tol_fit`) on the boss/plate B face.

## 2. bed_max on the mesh
Export with `--export-format asciistl` (probe support); awk min/max over `vertex` lines in the `build/stl/%.stl` recipe; fail with `error: <part>: STL size ... exceeds bed_max N mm` and remove the STL; `BED_MAX` parsed from `params.scad` (overridable). Remove analytic `*_size()` and their asserts. Proof fixture `tools/cad/fixtures/bed-oversize.scad`; `gate-test` expects `exceeds bed_max`.

## 3. Geometry fix options
- (a): **A1 delete spacer bosses and M3 spacer bolts (recommended)**; plates become flat (~8 g less real mass, better print pose; less out-of-plane stiffness). A2 outboard tie posts; A3 static-only relocation (fails sweeps).
- (c1): subtract femur `servo_pocket` from the whole bracket (recommended).
- (b): **B1 rotate the femur servo 90 deg (body vertical) in the coxa bracket (recommended, validated by the new check)**; B2 separate Y-lane for the tibia servo (fallback); B3 trim/flip (marginal, fails beyond ~22 deg); B4 lengthen femur and B5 lower phi_nom rejected.
- (c2): let the (b) redesign absorb it; otherwise `coxa_l` +4 mm (+14.4 g, margin ~1.009) or rotate the coxa servo (out of scope).

## 4. Spec and ADR impact
- leg-design: MODIFIED "Bed size fit" (measured on the STL), ADDED "Assembly interference-free", MODIFIED params/defaults (`fit_alpha`, `fit_phi`, tolerance, optional gap) and part naming (`asm-leg` module file + `fit.scad`).
- cad-build: ADDED "Mesh bed-fit gate" and "Assembly fit check"; MODIFIED "Warnings gate" (`gate-test` proves four fixtures); MODIFIED "Entry points and outputs" only for a `build/fit/` note.
- ci: MODIFIED "Canonical build" to run `gate-test` and `make check-fit`.
- repo-structure: MODIFIED "Deferred scope excluded" to permit the new fixtures.
- ADR-0004 "Assembly fit gate and mesh bed gate" (amends ADR-0002 items 5/6 and ADR-0003 item 6; ADR-0002/0003 stay immutable). Update `hardware/cad/README.md` and note in `docs/architecture/leg-torque-budget.md` that geometry does not enter the torque model.

## Recommendation
1. Tooling first (mesh bed check, `asm-leg` refactor, `check-fit`, fixtures, CI step) in a chained-PR set against a tracker branch; `check-fit` fails on main until the geometry PRs land, so no known-failure allowlist.
2. Fix (a) by deleting spacers and (c1) via the pocket cut.
3. Solve (b) and (c2) with B1, validated by the check; fall back to B2 if combined poses fail.
4. ADR-0004 and the spec deltas above.

## Risks
Hand-derived numbers unconfirmed; the 2D grid may reveal more collisions (B1 may still collide at alpha -30 with phi 45); ASCII STL precision and `--export-format asciistl` support on `dev.2026-01-19` unverified; 0.1 mm3 tolerance is a guess; the servo profile is provisional; deleting spacers is an unverified stiffness decision; B1 touches the body-mount interface height.

## Product decisions
D1 gate location (own CI step). D2 sweep set (grid above; final ranges after a scratch sweep). D3 contact allowance (0.1 mm3 + 0.2 mm gap). D4 spacers (delete). D5 (b) architecture (B1 vs B2 vs reduced range; blocks the proposal). D6 (c2). D7 remove analytic size functions. D8 ADR-0004. D9 chained PRs into a tracker.

## Ready for Proposal
Tooling scope: yes. Geometry scope: after D5 (and preferably D2/D4).
