# ADR-0004: Assembly fit and mesh bed gates

## Status

Proposed

## Date

2026-09-29

## Context

Skeleton. To be completed and set to Accepted in the last PR of the `leg-interference-fix` chain.

## Decision

1. **Mesh bed gate.** Bed fit is checked on the exported ASCII STL (`tools/cad/stl-bbox.awk`) instead of analytic `*_size()` functions.
2. **check-fit.** Pose grid, pose convention, body pairs, sentinel, tolerance and axial gap.
3. **gate-test.** Four fixtures run through the `expect_fail` macro.
4. **CI.** A `check-fit` step after `Gate test`.
5. **ASCII STL export.** `--export-format asciistl` on the pinned image.
6. **Flat plates.** Spacers removed, femur servo pocket cut in the coxa bracket, plate A relief.
7. **Coxa bracket geometry.** Femur servo orientation, `leg_lane_dy` and the body keep-out.

## Amendments

To be listed: ADR-0002 items 4, 5 and 6; ADR-0003 items 5 and 6.

## Alternatives considered

To be completed.

## Consequences

To be completed.
