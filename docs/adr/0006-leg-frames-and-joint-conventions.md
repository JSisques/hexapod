# ADR-0006: Leg frames and joint conventions

## Status

Accepted

## Date

2026-09-30

## Context

Leg kinematics in `software/` must agree with the OpenSCAD leg assembly and with the servo mapping planned for a later phase. Frame origins, angle signs, units and the IK branch have to be fixed once, in one place, so that CAD, Python and firmware never disagree by a sign.

## Decision

1. **Units.** Millimetres and degrees. Angle names follow the CAD: `theta`, `alpha`, `phi`.
2. **Leg frame L.** Origin on the coxa axis at the coxa frame plane. +Z up, +X radial outward when `theta = 0`, +Y along the femur axis. All six legs are identical and unmirrored, so the lateral foot offset is the same in every leg frame.
3. **Joints.** `theta` is the coxa yaw, counter-clockwise about +Z. `alpha` is the femur pitch, knee up positive. `phi` is the knee angle relative to the femur; the tibia angle from vertical is `alpha + phi`. Neutral is `(0, 0, 0)`.
4. **Foot point.** The foot-sphere centre, `knee_to_foot` (86 mm) from the knee axis, with a lateral offset `foot_dy` (-1.3 mm) taken from the snapshot. With `r = coxa_l + femur_l cos(alpha) + knee_to_foot sin(alpha + phi)`, the point is `Rz(theta) [r, foot_dy, cb_zmid + femur_l sin(alpha) - knee_to_foot cos(alpha + phi)]`. Tests compare it with 12 CAD-evaluated poses (`fk_golden`) to 1e-3 mm.
5. **IK branch.** Knee-up with an outward coxa. The knee angle relative to the femur is `q2 = phi - 90 = -acos(c)`, which is the only branch that intersects the fit envelope (`phi` in [-15, 45]). `theta` is wrapped into (-180, 180]. IK never returns NaN: it raises `UnreachableError` with one of three reasons, `LATERAL`, `TOO_FAR` or `TOO_CLOSE`.
6. **Limits.** Hard limits are the `fit_alpha` and `fit_phi` envelopes (min to max) from the snapshot and, PROVISIONALLY, `theta` within +/-45 degrees. IK does not clamp; `violations()` reports each offending joint and the excess, and callers decide. `servo_range_failures()` checks that the largest limit magnitude of each joint is within half the servo `range_deg`, assuming the neutral pose sits at the servo centre.
7. **Placeholders.** The +/-45 degree yaw range and the stance geometry of a later body layout are PROVISIONAL until backed by a real part. The neutral stance target `(100, -1.3, -52)` gives `alpha` of about 9.9 and `phi` of about 0.7 degrees, inside the envelope; a test asserts it.

## Alternatives considered

- **Mirrored left and right legs.** Matches a mirrored build, but the CAD models one leg; mirroring is a later CAD decision.
- **Knee-down branch.** Lies outside the CAD envelope for every reachable pose.
- **Clamping or NaN for unreachable targets.** Hides the failure. A typed error keeps the reason.
- **Clamping to limits inside IK.** Mixes geometry with policy and hides violations from reports.

## Consequences

- The servo mapping in a later phase reads these signs and limits and adds only per-servo offsets and directions.
- A CAD change to the leg geometry is picked up through `make params`; the FK golden test fails if the Python maths and the CAD chain diverge.
- The yaw limit must be revisited when the coxa mount is designed.
