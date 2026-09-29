# Apply Progress: leg-module-foundation

Mode: Standard (Strict TDD false). Store: openspec. Chain: feature-branch-chain.

## PR 1 (branch feat/leg-module-foundation-1-common) - DONE

Tasks 1.1-1.9 complete. Phase 4 items covered in PR 1: 4.2 (docker and local), 4.6.
Deferred (need parts from PR 2/3): 4.1 full, 4.3 (proved with fixture instead), 4.4, 4.5, 4.7.

### Work Unit Evidence

| Evidence | Value |
|---|---|
| Focused test | `make gate-test` and `make gate-test TOOLCHAIN=docker`: `gate-test: OK` + `gate-test: torque OK`, exit 0 |
| Runtime harness | `make clean stl render TOOLCHAIN=docker`: exit 0, smoke.stl + smoke.png; scratch file exercising every library module built with `--hardwarnings` on local snapshot and pinned image: exit 0, no WARNING/ERROR |
| Rollback boundary | `hardware/cad/common/`, `tools/cad/fixtures/torque-infeasible.scad`, `Makefile` |

### Observed checks

- Torque numbers match the design: m_total 2.104 kg; XS femur static 5.78/6.60 (1.14), femur peak 8.66/8.80 (1.02), tibia 1.92/6.60 and 2.88/8.80. Tier M fixture: femur static 9.51 > 6.6.
- 1.8: `-D leg_tier=... -D phi_nom=25 -D check_torque=false` and a double `include` of params.scad: no WARNING (local + pinned Docker image).
- 1.9: cuboid, cyl (h, d, teardrop, anchor), move, zrot, BOTTOM exist at BOSL2 402be42 (shapes3d, transforms, constants, all pulled by std.scad).
- Missing key: `sv(servo,"nope")` fails with `key not found or duplicated: nope`.
- `-D leg_tier="S"` with checks on fails: femur peak 9.8 > 8.8 (design implied only M is infeasible; S is also infeasible, informational).

### Deviations from design

1. `servo_pocket(p, clear = sv(p,"body_clear"), ...)` is invalid OpenSCAD (module defaults cannot reference earlier params; emits `WARNING: Ignoring unknown variable "p"`). Changed to `clear = undef`, resolved inside the module. Same call API.
2. `leg_torque_gate` echoes the margin with `r2()`, so the peak femur margin prints `1.02` (design text lists 1.016).
3. `torque_rows` gained an optional trailing `alpha = 0` argument.
4. `servo_model` hub diameter is `body_w / 2` (no profile key exists); provisional geometry.
5. `r2()` helper added in torque.scad.

### Files

hardware/cad/common/{params,servo,torque,fasteners}.scad, hardware/cad/common/servos/mg996r.scad, tools/cad/fixtures/torque-infeasible.scad, Makefile.
