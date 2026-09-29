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

## PR 2 (branch feat/leg-module-foundation-2-parts) - DONE

Tasks 2.1-2.6 complete. Phase 4 covered in PR 2: 4.2 (re-run), 4.3, 4.4, 4.5; 4.1 partially (asm-leg.png is PR 3). 4.7 still pending (push + CI).
Authored lines: 223 (179 in the four part dirs + 44 in common/), under the 400 budget.

### Work Unit Evidence

| Evidence | Value |
|---|---|
| Focused test | `make clean stl render` (local) and `make clean stl render TOOLCHAIN=docker`: exit 0, 0 WARNING/ERROR matches; `make gate-test` local + docker: `OK` + `torque OK` |
| Runtime harness | `-D 'leg_tier="M"'` on leg-tibia/main.scad: exit 1, `torque budget exceeded: femur static 9.51 kg.cm > allowable 6.6 ...`, no STL written; `rg PROVISIONAL build/log/stl/leg-tibia.log` matches; `sv(servo,"nope")` scratch: `key not found or duplicated: nope`; touch params.scad + `make stl` rebuilt 4 STLs |
| Rollback boundary | `hardware/cad/leg-*/`, plus the additions in `hardware/cad/common/{servo,params}.scad` |

### Part envelopes (measured from STL vertices, print pose; bed_max 180)

| Part | Measured X x Y x Z (mm) | Max | Design estimate |
|---|---|---|---|
| leg-coxa-bracket | 86.4 x 59.8 x 57.6 | 86.4 | ~85 x 50 x 60 |
| leg-femur-plate (A+B) | 86.0 x 72.0 x 30.8 | 86.0 | ~86 x 72 x 29 |
| leg-tibia | 120.9 x 26.3 x 47.6 | 120.9 | ~120 x 30 x 50 |
| leg-foot | 16.2 x 16.2 x 26.0 | 26.0 | ~20 x 20 x 26 |

All match the analytic `*_size()` functions passed to `leg_part_checks`. 2.6 hard-coded dimension scan: no match outside `**/servos/**` (the design's `!common/servos/**` glob does not exclude in ripgrep; `!**/servos/**` does).

### Deviations from design

1. Helpers added to `common/servo.scad`: `servo_cage(p, spec)` (cage + slide-in slot + ear bolts/nut traps + idler boss), `servo_cage_x`, `servo_cage_w`, `servo_cage_depth`. Coxa bracket and tibia share it instead of duplicating cage code.
2. `common/params.scad` gained `idler_boss_h` 4, `leg_spigot_d` 10, `leg_spigot_l` 12, `leg_joint_span` (plate-to-plate distance 50.2, so each femur plate carries 25.1 mm spacers).
3. Servo slides into the cage from the +X end (not the -Z side), so the cage floor and idler boss can close the -Z side. Tibia idler boss is a protruding boss (same as coxa) rather than recessed, so both joints share `leg_joint_span`.
4. BOSL2 `cyl(teardrop=true)` only limits edge rounding; it does not create a teardrop hole. `screw_clear(..., teardrop=true)` from PR 1 is therefore a plain cylinder. The foot cross hole uses BOSL2 `teardrop()` (`zrot(90) teardrop(...)`). Servo ear holes stay round (`servo_ear_holes` has no teardrop option).
5. Coxa servo body pocket is subtracted from the bracket web (`servo_pocket` mirrored at the coxa axis) so the web clears the coxa servo and its ears.
6. Coxa bottom-arm nut trap uses the plain M4 nut depth (3.2), not the nylock height (5.0), to keep 2.5 mm of floor.

### Issues / risks

- Geometry is provisional (unmeasured MG996R); no interference check with the coxa servo mounting ears beyond the pocket cut. Assembly check comes with asm-leg (PR 3).
- Femur peak margin remains 1.02 (unchanged; femur_l 55 and 11.0 kg.cm kept).

### Files

hardware/cad/leg-{coxa-bracket,femur-plate,tibia,foot}/{<name>,main}.scad; modified hardware/cad/common/{servo,params}.scad.

## PR 3 (branch feat/leg-module-foundation-3-asm-docs) - DONE

Tasks 3.1-3.5 complete; 4.1 and 4.6 closed. Only 4.7 (push + CI green) remains, owned by the orchestrator.
Authored lines: about 216 (asm-leg 36, torque doc 82, ADR-0003 43, hardware/cad/README +44, small edits in root README, adr index, config), under the 400 budget.

### Work Unit Evidence

| Evidence | Value |
|---|---|
| Focused test | `make clean stl render TOOLCHAIN=docker`: exit 0, 0 WARNING/ERROR matches, `build/stl` has 4 leg STLs + smoke and no `asm-leg.stl`, `build/png` has `asm-leg.png`; same with `TOOLCHAIN=local` (exit 0, 0 matches); `make gate-test` local and docker: `gate-test: OK` + `gate-test: torque OK` |
| Runtime harness | `make help` shows `asm-* parts are PNG-only`; `git check-ignore build` prints `build`; torque numbers recomputed by an `openscad` echo run over `torque_rows` for every tier |
| Rollback boundary | `hardware/cad/asm-leg/`, `docs/architecture/leg-torque-budget.md`, `docs/adr/0003-*`, `docs/adr/README.md`, `hardware/cad/README.md`, `README.md`, `openspec/config.yaml` |

### 3.2 colour result

Colours SURVIVE with `--render` in `build/png/asm-leg.png` on both the pinned Docker image and the local snapshot (dimgray servos, orange coxa/tibia, steelblue femur plates, black foot). Monochrome fallback not needed.

### Assembly interference findings (scratch intersection tests in the torque-model pose, not committed)

asm-leg exposed real geometry clashes in the PR 2 parts; not fixed here (out of the assigned tasks):
1. Femur servo body vs femur plate spacer bosses: overlap at world x 53-62 (spacers at femur_l/2, y +-8, versus the servo body reaching +30.7 mm along the femur). Needs the spacers moved off the servo footprint (or moved to the far end).
2. Tibia (cage/servo side) vs coxa bracket cage: overlap about 4.7 x 43 x 13 mm at x 66-71 in the nominal pose.
3. Femur servo vs coxa bracket: minor (about 2.7 x 2.5 x 20 mm), femur servo vs tibia servo: sliver at the touching edge.
4. Tibia idler boss end face vs plate B: zero-thickness contact only (expected).

### Deviations from design

1. Femur plate A is placed with `xrot(180)` (proper rotation) rather than a mirror; the plate is symmetric in Y so the result is identical.
2. The design says the femur margin at `femur_l` 50 is 1.08; recomputed it is 1.09 (mass also drops to 2.086 kg). Torque doc uses the recomputed value.
3. Tier table in the torque doc adds a "required stall per tier" column derived from the same model (XS 10.8, S 12.2, M 17.8, L 25.0, XL 35.5 kg.cm). Tier S also fails with MG996R (femur peak 9.80 > 8.80), consistent with PR 1 notes.
4. Root README status line, repo map row and decisions list were stale and were updated.
