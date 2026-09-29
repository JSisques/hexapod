# Proposal: Leg interference fix

## Intent

The leg parts collide in motion: the tibia hits the femur cage (about -4.7 mm at phi 20), the spacers sit inside the servo bodies, the femur servo overlaps the bracket web, and the coxa servo ear hits plate A. Nothing detects this, and the bed check measures analytic sizes, not meshes. This change adds mesh-based gates and fixes the geometry so they pass.

## Scope

### In Scope
- Mesh bed gate in the `stl` recipe (awk over ASCII STL, `BED_MAX` parsed from `params.scad`, overridable). Removes the analytic `*_size()` functions and their asserts.
- `make check-fit` (phony): per-pose `intersection()` over `fit_alpha` [-30,0,30] x `fit_phi` [-15,0,20,45] (previously [-30,0,20,45], narrowed after design), signed-volume test (tol 0.1 mm3), sentinel object, optional 0.2 mm axial gap. It runs as its own CI step after `gate-test` and is not a prerequisite of `make stl`.
- Refactor `asm-leg` into pose-parameterised modules plus `fit.scad`.
- `gate-test` gets an `expect_fail` macro and the `fit-interference` and `bed-oversize` fixtures.
- Geometry: (a) delete the spacer bosses and M3 bolts; (c1) cut the femur `servo_pocket` from the whole bracket; (b) B1, femur servo body vertical in a redesigned coxa bracket; (c2) absorbed by B1.
- ADR-0004, which amends ADR-0002 items 5/6 and ADR-0003 item 6. Updates to `hardware/cad/README.md` and a note in `docs/architecture/leg-torque-budget.md`.

### Out of Scope
- Body, firmware, servo measurement, tier change, servo swap, and yaw sweep.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `leg-design`: MODIFIED Bed size fit (measured on the mesh); ADDED Assembly interference-free; MODIFIED Params location and defaults, and Part naming and inclusion.
- `cad-build`: ADDED Mesh bed-fit gate and Assembly fit check; MODIFIED Warnings gate (four fixtures).
- `ci`: MODIFIED Canonical build (adds a `check-fit` step).
- `repo-structure`: MODIFIED Deferred scope excluded (permits the new fixtures and the awk script).

## Approach

Build the tooling first, then fix the geometry, with the fit check as the oracle. If B1 fails the sweep, fall back to B2 (tibia servo in a separate Y-lane), decided by evidence during design or apply. Any `coxa_l` +4 mm fallback for (c2) changes tier XS and the 1.016 femur margin, so it MUST be flagged to the user before it is applied. The torque gate, tier XS, `femur_l` 55 and stall 11.0 kg.cm stay unchanged.

## Affected Areas

| Area | Impact |
|------|--------|
| `Makefile`, `.github/workflows/cad.yml` | Modified |
| `hardware/cad/asm-leg/`, `hardware/cad/common/params.scad` | Modified |
| `hardware/cad/<coxa, femur-plate>/` | Modified |
| `tools/cad/fixtures/`, `tools/cad/*.awk` | New |
| `docs/adr/0004-*.md` | New |
| `hardware/cad/README.md`, `docs/architecture/leg-torque-budget.md` | Modified |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Hand-derived numbers are unconfirmed | Med | The sweep is the oracle |
| B1 still collides at alpha -30 with phi 45 | Med | B2 fallback, decided by evidence |
| ASCII STL precision or `--export-format` not supported on the pinned image | Med | Probe in PR1; tolerance 0.1 mm3 |
| Flat plates lose out-of-plane stiffness | Med | Record it; validate physically |
| MG996R profile is PROVISIONAL | High | The parts stay NOT safe to print until the servo is measured |

## Rollback Plan

Revert the tracker merge commit. Each slice reverts on its own branch. The ADRs stay immutable, so revert ADR-0004 as a whole file.

## Delivery

The PRs are chained into a tracker branch, each under 400 lines. `check-fit` fails on main-based PRs until PR4 lands. There is no known-failure allowlist: PR1 and PR2 are verified with fixtures only, and the chain merges as a unit.

1. Mesh bed check, `bed-oversize` fixture, `expect_fail`, and spec/ADR skeleton.
2. `asm-leg` refactor, `check-fit`, and `fit-interference` fixture (no CI step yet).
3. Spacer removal, pocket fix, and plate A relief.
4. B1 coxa bracket redesign, sweep-driven tuning, the CI `check-fit` step, and docs (CI step moved from PR2 to PR4 per design D9).

## Success Criteria

- [ ] `make gate-test` proves all four fixtures.
- [ ] `make check-fit` passes the full grid.
- [ ] `make stl` fails on mesh oversize.
- [ ] CI is green at the chain end.
- [ ] Torque margin is unchanged (1.016).
