# Proposal: Leg Module Foundation

## Intent

The repo builds only a smoke part. The goal is a medium-large hexapod, which needs a ~20-30 kg.cm servo (STS3215 class). This change delivers one parametric leg at tier XS (femur 55 / tibia 80 mm) on a PROVISIONAL MG996R-clone profile as the **validation stage, not the end goal**. A later change moves to tier M by swapping the servo profile. MG996R dimensions are unmeasured: do not print before measuring.

## Scope

### In Scope
- `hardware/cad/common/`: `params.scad`, `servo.scad` (asserting getter over `[[key,value],...]`), `torque.scad`, `fasteners.scad`, `servos/mg996r.scad` (`provisional=true`).
- Torque `assert` (60% static / 80% peak of stall, k_dyn 1.5, phi 20 deg). Defaults are XS + MG996R, so CI stays green.
- Parts: `leg-coxa-bracket`, `leg-femur-plate`, `leg-tibia`, `leg-foot` (TPU), `asm-leg` (PNG only).
- Makefile: `STL_PARTS` filters out `asm-%`.
- ADR-0003, `docs/architecture/leg-torque-budget.md`, README/config updates.

### Out of Scope
- Body, firmware, software, vision, electronics.
- STS3215 profile, tier M, release gate for PROVISIONAL, CI workflow changes.

## Capabilities

### New Capabilities
- `leg-design`: servo profile contract, PROVISIONAL marker, torque gate, default tier/servo agreement, `bed_max` fit, fastener and material defaults.

### Modified Capabilities
- `repo-structure`: "Deferred scope excluded" allows `hardware/cad/common/` and real part dirs.
- `cad-build`: "Entry points and outputs": `asm-*` dirs produce PNG only; helper dirs without `main.scad` are not built.

## Approach

- Flat part dirs; helpers included relatively (`include <../common/params.scad>`), tracked by `-d` files.
- Everything reads the profile through the getter; axis conventions live only in profile files.
- Echo/assert text never contains `WARNING`/`ERROR` except an actual assertion failure.
- Defaults: PETG (TPU foot), M3 (M4 pivots), nuts on structural joints, heat-set inserts only where re-driven, `bed_max` 180 mm asserted, regulated 6 V assumed.
- ADR-0003 records servo abstraction, tiers, fasteners; ADR-0001 stays immutable.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `hardware/cad/common/` | New | Shared library and profile |
| `hardware/cad/leg-*/`, `hardware/cad/asm-leg/` | New | Parts and preview |
| `Makefile` | Modified | `STL_PARTS` filter |
| `docs/adr/0003-*.md`, `docs/architecture/leg-torque-budget.md` | New | Decision and derivation |
| `hardware/cad/README.md`, `openspec/config.yaml` | Modified | Conventions, context |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Unmeasured MG996R dimensions | High | PROVISIONAL flag and echo; measure before printing |
| Clones underperform datasheet | Med | 60% margin; XS is validation only |
| Guessed mass model | Med | Documented as screening; calibrate later |
| Tier/servo mismatch breaks CI | Low | Defaults agree; the assert is intended |
| Echo text trips the gate | Low | Text rule in spec |

## Rollback Plan

Revert each slice PR in reverse order. The Makefile filter is inert without `asm-*` dirs, and the smoke part stays, so the build returns to its current state.

## Dependencies

- None new (BOSL2 and the pinned image are already in place).

## Delivery Slices (chained PRs, <400 lines each)

1. Common lib, profile, params, torque assert, ADR-0003, spec deltas, Makefile filter.
2. Printable parts (split coxa/femur vs tibia/foot if over budget).
3. `asm-leg` preview, torque doc, READMEs.

## Success Criteria

- [ ] `make stl render gate-test` passes locally and in CI with no `WARNING`.
- [ ] `build/stl` has every printable leg part and no `asm-leg.stl`; `build/png/asm-leg.png` exists.
- [ ] Setting an infeasible tier (e.g. M with MG996R) fails the build via the assert.
- [ ] Every part fits `bed_max`; no hard-coded servo dimensions outside profiles.
