# Design: Leg Module Foundation

## Technical Approach

A side-effect-free OpenSCAD library in `hardware/cad/common/` (profile data, getters, cutters, torque functions) is consumed by flat part directories. Each part directory holds a geometry module file (`<name>.scad`, reusable by `asm-leg`) plus a thin `main.scad` that runs the checks (provisional echo, torque gate, bed fit) and places the part in print orientation. Implements specs `leg-design`, `cad-build` (delta), `repo-structure` (delta).

## Architecture Decisions

| Decision | Choice | Rejected | Rationale |
|---|---|---|---|
| Profile format | Function returning `[[key,value],...]`, read by asserting `kv_get` | Prefixed globals; BOSL2 `struct_val` (silent `undef`) | Namespaced, swappable, fails loudly |
| Library side effects | `common/*.scad` define only functions, modules and variables; no top-level instantiation | Gate call inside `params.scad` | Double includes (asm-leg) stay silent; checks run once, from `main.scad` |
| Part code split | `leg-x/<name>.scad` (module, assembly frame) + `leg-x/main.scad` (checks + print pose) | Geometry in `main.scad` | `asm-leg` can reuse modules without running another part's top level |
| Cutters | Plain `difference()` with explicit cutters overshooting by `eps` | BOSL2 `diff()`/`tag()` | Fewer attachable-tree surprises; no coplanar faces |
| Fasteners | Own table + cutters in `fasteners.scad` | `BOSL2/screws.scad` | Not in `std.scad`; heavier; own nut/insert tolerances |
| Torque gate proof | New fixture `tools/cad/fixtures/torque-infeasible.scad`, checked by `gate-test` | New CI step; manual `-D` only | CI already runs `gate-test`; no workflow change (out of scope) |
| Stall figure | TowerPro datasheet 11.0 kg.cm @ 6 V | Retailer 13 kg.cm (used in exploration) | Clones underperform; derating is the margin, not an inflated rating |
| Servo preview in parts | `if ($preview) %servo_model(...)` | Always ghost; BOSL2 `ghost()` | `$preview` is false for STL and `--render`, so exports never see it |

## Data Flow

```
main.scad ─include─> <name>.scad ─include─> common/params.scad
                                             ├─ servo.scad (kv_get, sv, cutters, servo_model)
                                             ├─ servos/mg996r.scad (mg996r())
                                             ├─ fasteners.scad
                                             └─ torque.scad
main.scad: leg_part_checks(name,size) ──> echo provisional ──> leg_torque_gate() ──assert──> bed assert
           then <part>_print() ──> geometry ──> STL/PNG (gate scans stderr)
```

## Library Tree and API

```
hardware/cad/common/
  params.scad        servo.scad        torque.scad        fasteners.scad
  servos/mg996r.scad
```

```openscad
// servo.scad (includes <BOSL2/std.scad>)
function kv_get(table, key, what="table") =
    let(hits = [for (kv = table) if (kv[0] == key) kv[1]])
    assert(len(hits) == 1, str(what, ": key not found or duplicated: ", key))
    hits[0];
function sv(p, key) = kv_get(p, key, str("servo profile ", p[0][1]));  // name is first
function servo_stall_kgcm(p, v);        // asserts v is a rated voltage in sv(p,"stall_kgcm")
module servo_model(p);                  // real solid: body, ears, hub, spline; uncoloured
module servo_pocket(p, clear=sv(p,"body_clear"), extra_top=0);  // body+clear, open toward -Z insertion, cable slot
module servo_ear_holes(p, l, spec=M3);  // 4 through cutters on the ear pattern
module horn_interface(p, depth);        // horn disc recess (horn_d+tol_fit), n screw holes on PCD, centre clearance
module servo_provisional_echo(p);       // echo only when provisional
// torque.scad
function leg_mass_total_kg(n_servo, m_servo_kg, g_per_mm, lengths, m_body_kg)
    = n_servo*m_servo_kg + 6*g_per_mm*(lengths[0]+lengths[1]+lengths[2])/1000 + m_body_kg;
function tripod_force_kgf(m_total, k=1) = m_total/3*k;
function tau_tibia_kgcm(F, tibia_l, phi) = F*tibia_l/10*sin(phi);
function tau_femur_kgcm(F, femur_l, tibia_l, phi, alpha=0)
    = F*(femur_l*cos(alpha) + tibia_l*sin(phi))/10;
function torque_allowable(stall, derate) = stall*derate;
function torque_rows(p, lengths, m_total, v, phi, k_dyn, d_s, d_p); // [[joint, case, tau, allow],...]
module leg_torque_gate(p=servo, tier=leg_tier);  // echo each row, assert tau <= allow per row
// fasteners.scad
M3 = [["d",3],["clear",3.4],["nut_af",5.5],["nut_h",2.4],["head_d",5.5],["head_h",3.0],
      ["insert_d",4.1],["insert_h",5.7]];
M4 = [["d",4],["clear",4.5],["pivot",4.4],["nut_af",7.0],["nut_h",3.2],["nylock_h",5.0],
      ["head_d",7.0],["head_h",4.0]];
function fs(spec, key) = kv_get(spec, key, "fastener");
module screw_clear(spec, l, teardrop=false);  module nut_trap(spec, depth);  // hex: d=(af+tol_fit)/cos(30), $fn=6
module insert_pocket(spec);
// params.scad
function leg_lengths(tier) = kv_get(leg_tiers, tier, "leg tier table");  // [coxa, femur, tibia]
module leg_part_checks(name, size=undef);  // provisional echo; torque gate if check_torque; bed assert if size
```

**params.scad values**: `tol_press 0.10`, `tol_fit 0.20`, `tol_loose 0.40`, `eps 0.01`, `$fa 2`, `$fs 0.4`, `wall 3.0`, `plate_t 4.0`; `material_default "PETG"`, `material_foot "TPU"`; `leg_tiers = [["XS",[30,55,80]],["S",[30,60,90]],["M",[35,80,120]],["L",[40,100,160]],["XL",[45,130,200]]]`; `leg_tier "XS"`; `coxa_l/femur_l/tibia_l` from it; `servo = mg996r()`; `supply_v 6.0`; `n_servo 18`, `link_g_per_mm 0.6`, `m_body_kg 0.52` (body+electronics+battery, guess); `k_dyn 1.5`, `phi_nom 20`, `phi_stress 45` (echo only), `alpha 0`, `derate_static 0.6`, `derate_peak 0.8`, `check_torque true`; `leg_mount_gap = sv(servo,"body_h")+sv(servo,"top_h")+sv(servo,"horn_t")+2*tol_loose`, `leg_mount_pivot = M4`; `bed_max 180`.

**MG996R profile** (frame: Z = output shaft up, origin on shaft axis at case top face, +X toward the far body end). P = provisional, S = standard/datasheet.

| Key | Value | | Key | Value | |
|---|---|---|---|---|---|
| `name` | `"mg996r"` | S | `spline_teeth` | 25 | S |
| `provisional` | `true` | S | `spline_od` | 5.8 | P |
| `source` | `"TowerPro datasheet + generic drawings; unmeasured"` | S | `horn_d` / `horn_t` | 25.0 / 2.5 | P |
| `body_l` / `body_w` / `body_h` | 40.7 / 19.7 / 37.0 | P | `horn_hole_pcd` / `horn_hole_n` / `horn_screw_d` | 18.0 / 4 / 2.0 | P |
| `top_h` (hub above case, total 42.9) | 5.9 | P | `horn_center_clear_d` | 8.0 | P |
| `shaft_offset_x` (to near end) / `shaft_offset_y` | 10.0 / 0 | P | `cable_exit_z` / `cable_exit_w` (at +X end) | -33.0 / 6.0 | P |
| `ear_span` / `ear_t` | 54.5 / 2.5 | P | `mass_kg` | 0.055 | S |
| `ear_top_z` | -10.0 | P | `stall_kgcm` | `[[4.8,9.4],[6.0,11.0]]` | S |
| `ear_hole_pitch_l` / `ear_hole_pitch_w` | 49.5 / 10.0 | P | `stall_a` (highest source) | 2.5 | P |
| `ear_hole_d` / `mount_screw` | 4.2 / `"M3"` | P/S | `pulse_us` / `range_deg` | `[500,2500]` / 180 | P |
| `body_clear` | 0.3 | P | `v_nom` | 6.0 | S |

## Torque Budget (tier XS, MG996R @ 6 V)

`m_total = 18*0.055 + 6*0.6*(30+55+80)/1000 + 0.52 = 2.104 kg`. F static 0.701 kgf, peak (k_dyn 1.5) 1.052 kgf. Femur lever `5.5 + 8.0*sin 20 = 8.236 cm`; tibia lever 2.736 cm.

| Joint | Case | tau (kg.cm) | Allow @11.0 | Margin | Allow @13 (retailer) | Margin |
|---|---|---|---|---|---|---|
| Femur | static 60% | 5.78 | 6.60 | 1.14 | 7.80 | 1.35 |
| Femur | peak 80% | 8.66 | 8.80 | **1.016** | 10.40 | 1.20 |
| Tibia | static / peak | 1.92 / 2.88 | 6.60 / 8.80 | 3.44 / 3.06 | | |

**Honest finding**: XS + MG996R passes, but at the datasheet 11.0 kg.cm the femur peak margin is 1.6%: +33 g on `m_total` fails CI. At `phi_stress` 45 deg XS fails even at 13 kg.cm (femur static 7.82 > 7.80), so 45 deg stays an echo, not an assert. Tier M fails clearly (femur static 9.51 > 6.60), which the fixture uses. Smallest contingency if calibrated mass grows: `femur_l` 55 -> 50 (peak margin 1.08). Not applied, because femur 55 is a confirmed product decision.

**Assert design**: one `assert(tau <= allow, msg)` per row (femur/tibia x static/peak). Message: `str("torque budget exceeded: ", joint, " ", case, " ", r2(tau), " kg.cm > allowable ", r2(allow), " kg.cm (servo ", name, ", tier ", tier, ", ", v, " V)")`. Echo per row: `"leg torque: femur peak 8.66 / 8.80 kg.cm, margin 1.02"`. Provisional echo: `"servo profile mg996r is PROVISIONAL: dimensions unmeasured, measure the servo before printing"`. No text contains `WARNING`/`ERROR`; OpenSCAD itself prefixes a real failure with `ERROR: Assertion`. `-D check_torque=false` skips the asserts and echoes `"torque gate skipped (check_torque=false)"`; exploratory use only, CI never sets it.

## Printable Parts (all PETG except foot; `main.scad` asserts `max(size) <= bed_max`)

| Part | Geometry outline | Fasteners | Print orientation | Envelope (mm) |
|---|---|---|---|---|
| `leg-coxa-bracket` | C-bracket around the body-mounted coxa servo: top arm with `horn_interface` on the coxa axis, bottom arm with M4 pivot hole (gap `leg_mount_gap`); outboard web carries a femur-servo cage (`servo_pocket`, shaft horizontal at `coxa_l`), ear holes, and a coaxial M4 idler boss opposite the shaft | M3 ear bolts + nut traps; M4 pivots + nylock | On outboard web face; horizontal holes `teardrop=true` | ~85 x 50 x 60 |
| `leg-femur-plate` | One STL = plate A + plate B side by side. Stadium (hull of two discs `horn_d+2*wall`, centres `femur_l` apart), `plate_t`. A: `horn_interface` at both ends. B: M4 `pivot` holes at both ends. Two half-height spacer bosses per plate, M3 through | M3 bolt + nut through spacers | Flat, servo-facing face up (recess and bosses grow up) | ~86 x 72 x 29 |
| `leg-tibia` | Knee cage around tibia servo (horn toward plate A), recessed M4 idler boss with nut trap on the opposite face, tapered beam (hull) to a d10 x 12 foot spigot at `tibia_l` | M3 ear bolts + nuts; M3 cross pin at spigot | Shaft axis vertical, flat bottom face by construction | ~120 x 30 x 50 |
| `leg-foot` (TPU) | Socket (spigot d + `tol_fit`, depth 12) hulled to a d16 sphere tip; M3 cross hole | M3 bolt + nylock | Socket opening up | ~20 x 20 x 26 |

No split needed at XS (all well under 180). Contingency: coxa bracket splits at the web/top-arm joint with two M3 bolts if a later tier trips the bed assert. Joint rule: servo body in one link, horn on the next, M4 idler opposite each horn.

**Warning-free rules (`--hardwarnings`)**: every part yields non-empty geometry; cutters overshoot by `eps`; no main-file reassignment of an included variable (OpenSCAD warns on include-overwritten main vars); only verified BOSL2 parameters; `$fa/$fs` set once in `params.scad`; no `%` outside `$preview`; no `import()`.

**Verified BOSL2 at `402be42`**: `cuboid(size, chamfer, rounding, edges, except, anchor, spin, orient)` and `cyl(h|l, d|d1|d2, chamfer, rounding, teardrop, anchor, spin, orient)` (`shapes3d.scad`), `xcyl/ycyl/zcyl`, `tube`, `xcopies/ycopies/grid_copies` (`distributors.scad`), `move/up/xrot/yrot/zrot/zflip` (`transforms.scad`), `ghost()` (sets `$ghost` for attachables only; not used), `left_half/right_half` (`partitions.scad`, split contingency). `screws.scad` is not in `std.scad` and is not used.

## asm-leg

`hardware/cad/asm-leg/main.scad` includes the four module files, calls `leg_part_checks("asm-leg")` (no bed assert), and places parts in the torque-model pose (femur horizontal, tibia `phi_nom` from vertical). Real coloured geometry: servos `color("dimgray") servo_model(servo)`, coxa/tibia `"orange"`, femur plates `"steelblue"`, foot `"black"`. Assumption: the pinned image keeps colours with `--render`; a monochrome PNG is still acceptable.

## Makefile Diff

```diff
-STLS := $(PARTS:%=build/stl/%.stl)
+STL_PARTS := $(filter-out asm-%,$(PARTS))
+STLS := $(STL_PARTS:%=build/stl/%.stl)
@@
-stl: $(STLS) ## Export STL models to build/stl
+stl: $(STLS) ## Export STL models to build/stl (asm-* parts are PNG-only)
@@
-gate-test: ## Prove the warnings gate fails on the warning fixture
-	@rm -f build/gate/warning.stl; \
+gate-test: ## Prove the warnings and torque gates fail on their fixtures
+	@rm -f build/gate/warning.stl build/gate/torque-infeasible.stl; \
 	out=$$($(MAKE) build/gate/warning.stl 2>&1); st=$$?; \
 	if [ $$st -ne 0 ] && printf '%s\n' "$$out" | grep -q WARNING; then echo "gate-test: OK"; \
-	else printf '%s\n' "$$out" >&2; echo "gate-test: FAILED (gate did not fire)" >&2; exit 1; fi
+	else printf '%s\n' "$$out" >&2; echo "gate-test: FAILED (gate did not fire)" >&2; exit 1; fi; \
+	out=$$($(MAKE) build/gate/torque-infeasible.stl 2>&1); st=$$?; \
+	if [ $$st -ne 0 ] && printf '%s\n' "$$out" | grep -q 'torque budget exceeded'; then echo "gate-test: torque OK"; \
+	else printf '%s\n' "$$out" >&2; echo "gate-test: FAILED (torque gate did not fire)" >&2; exit 1; fi
```

Fixture (`// SPDX-License-Identifier: MIT`): `include <../../../hardware/cad/common/params.scad>` then `leg_torque_gate(servo, "M"); cube(1);` (the cube keeps the geometry non-empty, so only the assert can fail it).

## File Changes

| File | Action | Description |
|---|---|---|
| `hardware/cad/common/{params,servo,torque,fasteners}.scad`, `common/servos/mg996r.scad` | Create | Library and provisional profile |
| `hardware/cad/leg-{coxa-bracket,femur-plate,tibia,foot}/{main,<name>}.scad` | Create | Printable parts |
| `hardware/cad/asm-leg/main.scad` | Create | PNG-only preview |
| `tools/cad/fixtures/torque-infeasible.scad` | Create | Torque gate fixture |
| `Makefile` | Modify | `STL_PARTS`, help text, `gate-test` |
| `docs/adr/0003-leg-servo-abstraction-and-tiers.md`, `docs/adr/README.md` | Create/Modify | ADR + index row |
| `docs/architecture/leg-torque-budget.md` | Create | Derivation |
| `hardware/cad/README.md`, `openspec/config.yaml` | Modify | Conventions, context |

**ADR-0003** (Nygard + Alternatives): Context (ADR-0001 deferred servo; target STS3215 class); Decision (1 profile contract + getter, 2 PROVISIONAL marker, 3 tiers XS..XL with XS+MG996R as validation, 4 torque gate numbers and derating, 5 fasteners/materials, 6 `asm-*` PNG-only, 7 `gate-test` extended to the torque fixture, extending ADR-0002 item 5 without editing it); Alternatives; Consequences (thin XS margin, measure before print, M needs a new profile).

**`leg-torque-budget.md`**: model and assumptions; mass model table; formulas; tier table recomputed with `params.scad`; XS margins (both stall figures); sensitivity (+33 g limit, 45 deg); calibration plan (weigh parts, measure stall at 6 V); supply sizing at 2.5 A x 18.

**README** (`hardware/cad`): `common/` helper convention, part module + `main.scad` split, `asm-*` PNG-only, PROVISIONAL rule, torque gate and `check_torque`, materials table. **config.yaml context**: "leg module foundation: common lib in hardware/cad/common, provisional MG996R profile, tier XS, torque gate in gate-test".

## Testing Strategy

| Check | Command | Expected |
|---|---|---|
| Build | `make clean stl render TOOLCHAIN=docker` | exit 0; no `WARNING`/`ERROR` in output |
| Outputs | `eza build/stl build/png` | 4 leg STLs + smoke; no `asm-leg.stl`; `asm-leg.png` present |
| Gates | `make gate-test` | both `OK` lines |
| Provisional echo | `rg PROVISIONAL build/log/stl/leg-tibia.log` | match |
| Infeasible via `-D` | `OPENSCADPATH=libs openscad --hardwarnings -D 'leg_tier="M"' -o $SCRATCH/x.stl hardware/cad/leg-tibia/main.scad` | non-zero or `ERROR: Assertion`; message has `torque budget exceeded` (`-D` overrides are silent) |
| Missing key | temporary `sv(servo,"nope")` in a scratch file | `key not found` assertion |
| Deps | `touch hardware/cad/common/params.scad && make stl` | leg STLs rebuilt |
| Hard-coded dims | `rg -n '40\.7|19\.7|54\.5|49\.5' hardware/cad --glob '!common/servos/**'` | no match |

CI: unchanged workflow; `gate-test` now covers the torque gate, `stl render` covers the parts and uploads artifacts.

## Threat Matrix

N/A: no routing, subprocess, VCS/PR automation, executable-file classification or process-integration boundary. The `gate-test` shell recipe change follows the existing pattern with no new inputs.

## Migration / Rollout

No migration. Three chained PRs (authored lines estimated):

1. Common lib + profile + fixture + Makefile + ADR-0003 (~380). If over 400, ADR-0003 moves to PR 3.
2. Four printable parts (~280).
3. `asm-leg`, torque doc, READMEs, config (~190).

## Open Questions

- [ ] Accept the 1.6% femur peak margin at 11.0 kg.cm, or use `femur_l` 50? (not blocking; default keeps 55)
- [ ] Spec deltas must add `tools/cad/fixtures/torque-infeasible.scad` to the `repo-structure` allow-list and the torque check to `cad-build` gate-test wording.
