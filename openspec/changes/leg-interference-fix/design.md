# Design: Leg interference fix

All geometry numbers below are hand-derived from the sources (no OpenSCAD run). Every number marked **(confirm)** must be confirmed at apply by `make check-fit` or a scratch render. Servo dimensions are PROVISIONAL (ADR-0003).

## Technical Approach

The work lands as tooling first and geometry second, and `make check-fit` is the oracle for the geometry. PR1 moves the bed gate onto the exported ASCII STL mesh (awk). PR2 splits `asm-leg` into a posed module library, adds `fit.scad`, and adds a per-pose intersection export checked by an awk signed-volume script. PR3 and PR4 fix the geometry. The torque model is not touched. This design implements the spec deltas in `specs/{leg-design,cad-build,ci,repo-structure}`.

**Key finding (resolved by user decisions after design):** B1 alone was predicted to fail the originally proposed grid (`fit_phi` [-30, 0, 20, 45]) at `alpha -30, phi -30` by about 5.7 mm. The user narrowed the grid to `fit_phi = [-15, 0, 20, 45]` (`fit_alpha` stays [-30, 0, 30]) and confirmed the D4 convention (phi = knee joint angle, equal to the torque-model phi at alpha 0). B1 is predicted to pass the whole narrowed grid with a minimum clearance of about 2.8 mm (hand-derived; to confirm at apply by `make check-fit`). B2 is used only if apply proves B1 fails the narrowed grid, and then apply MUST stop and report to the user, not switch silently.

## Architecture Decisions

| # | Decision | Choice | Rejected | Rationale |
|---|---|---|---|---|
| D1 | Bed gate | awk bbox over the ASCII STL in the `stl` recipe; `*_size()` functions and the `leg_part_checks` size assert removed | Analytic sizes; `--summary bounding-box` | The mesh is the truth, and analytic sizes can drift. awk is already present on runners and macOS. |
| D2 | Fit detector | One OpenSCAD run per pose: the union of the `intersection()` of every body pair, plus a sentinel cube, exported as ASCII STL, then an awk signed-volume sum | One run for all poses; Python/trimesh; an "empty = pass" rule | Per-pose runs give pose-level diagnostics and `-j` parallelism and need no new toolchain. The sentinel keeps the top level non-empty. |
| D3 | Export vs check | Pose STLs are cached make targets. `check-fit` re-runs awk on every invocation. | Checking inside the export recipe | Changing `FIT_VOL_TOL` would not re-check cached targets. The check is cheap. |
| D4 | Pose convention | `alpha` = femur pitch (knee up > 0). `phi` = **knee joint angle**, measured from the femur-plate normal. At `alpha = 0` it equals the torque-model `phi`. | World-frame `phi` (tibia from vertical) | Interference depends only on joint angles, so the grid is the servo command envelope. World `phi` with `alpha -30, phi 45` means a knee angle of 75 deg, which no same-lane design can clear (section 3.5). |
| D5 | Pair table | Generated: every distinct pair of the 8 bodies (28 pairs) | A hand-picked list | New bodies are checked automatically. The OpenSCAD geometry cache evaluates each body once per run. |
| D6 | Contact allowance | `fit_vol_tol = 2.0` mm3 (previously 0.1 mm3; eps-level model contacts reach 0.3-1.1 mm3, the smallest real interference is 17.7 mm3), plus `leg_axial_gap = tol_fit` (0.2) between plate B and both idler bosses, in the assembly only | Zero tolerance; no gap | Plate B rotates against the bosses, so a running clearance (washer or loose nylock) is physically right, and it removes the noisy zero-thickness contact sliver. |
| D7 | Awk location | `tools/cad/stl-bbox.awk` and `tools/cad/stl-volume.awk`, called by the Makefile | Inline awk in recipes | Readable, reviewable, and no `$$` escaping. The repo-structure delta permits them. |
| D8 | (b) geometry | B1: femur servo spun -90 deg about its own shaft (body down), `leg_lane_dy = -5` | Body up (fails `alpha 30, phi 45`); tilted body (hits the coxa servo) | The only orientation that clears the envelope the coxa servo leaves (section 3.4) |
| D9 | CI step timing | The `check-fit` CI step lands in **PR4** | Step in PR2 with `continue-on-error`; a branch condition | Every chained PR then shows an honest CI result for its own content, with no disguised allowlist. PR2 proves the checker through the `gate-test` fixture, which already runs in CI. |

## Data Flow

```
params.scad --awk param()--> BED_MAX, FIT_VOL_TOL, FIT_ALPHA, FIT_PHI   (make vars, overridable)

make stl:   part/main.scad --openscad asciistl--> build/stl/P.stl --stl-bbox.awk--> ok | rm + "exceeds bed_max"

make check-fit (sequence):
  make            openscad (per pose)                 stl-volume.awk
   |-- a{A}_p{P} --> fit.scad -D fit_a -D fit_p --> build/fit/a{A}_p{P}.stl
   |-- for pose ----------------------------------------------> volume <= tol ? ok
   |      fail --> fit.scad -D fit_diag=true --> build/fit-diag/<pose>.stl + log
   |                                            ----------------> per-pair lines (names from ECHO)
   '-- any fail --> "error: check-fit: interference in poses: ..." exit 1
```

## 1. Makefile

Everything below is compatible with make 3.81 (macOS): no `!=`, `.ONESHELL`, `undefine`, `$(file)` or `.RECIPEPREFIX`. The new pattern rules use distinct directories, so rule order never decides a match (3.81 picks the first matching rule, 3.82 and later the shortest stem).

```make
.PHONY: help stl render firmware software docs clean doctor gate-test check-fit preflight

# (docker branch)  HAS_EXPORT_FORMAT := yes
# (local branch)   HAS_EXPORT_FORMAT := $(shell "$(OPENSCAD)" --help 2>&1 | grep -q -- --export-format && echo yes)
# ASCII STL so the awk gates can read vertices; binaries without the flag already write ASCII.
STL_FMT = $(if $(HAS_EXPORT_FORMAT),--export-format asciistl)

PARAMS := hardware/cad/common/params.scad
# Value of a one-line "name = value;" in params.scad; list brackets and commas become spaces.
param = $(strip $(shell awk '$$1 == "$(1)" && $$2 == "=" { sub(/^[^=]*=/, ""); sub(/;.*/, ""); gsub(/[][,]/, " "); print; exit }' $(PARAMS)))
ifeq ($(origin BED_MAX),undefined)
BED_MAX := $(call param,bed_max)
endif
ifeq ($(origin FIT_VOL_TOL),undefined)
FIT_VOL_TOL := $(call param,fit_vol_tol)
endif
FIT_ALPHA := $(call param,fit_alpha)
FIT_PHI   := $(call param,fit_phi)
FIT_POSES := $(foreach a,$(FIT_ALPHA),$(foreach p,$(FIT_PHI),a$(a)_p$(p)))
FIT_STLS  := $(FIT_POSES:%=build/fit/%.stl)
FIT_SRC   := hardware/cad/asm-leg/fit.scad
FIT_VOL    = awk -v tol='$(FIT_VOL_TOL)' -f tools/cad/stl-volume.awk
# Pose stem a-30_p45 -> -D fit_a=-30 -D fit_p=45
fit_defs = -D fit_a=$(patsubst a%,%,$(word 1,$(subst _, ,$(1)))) -D fit_p=$(patsubst p%,%,$(word 2,$(subst _, ,$(1))))

# Mesh bed check: $(1) ASCII STL, $(2) name. The STL is removed on failure.
bed_check  = awk -v max='$(BED_MAX)' -v name='$(2)' -f tools/cad/stl-bbox.awk $(1) || { rm -f $(1); exit 1; }
stl_export = $(call scad,$(1),$(2),$(STL_FMT),$(3)); $(call bed_check,$(1),$*)

# Build $(1) and pass only if it fails with output matching the ERE $(2); $(3) is the label.
expect_fail = rm -f $(1); out=$$($(MAKE) --no-print-directory $(1) 2>&1); st=$$?; \
  if [ $$st -ne 0 ] && printf '%s\n' "$$out" | grep -Eq '$(2)'; then echo "gate-test: $(3) OK"; \
  else printf '%s\n' "$$out" >&2; echo "gate-test: FAILED ($(3) gate did not fire)" >&2; exit 1; fi

build/stl/%.stl: hardware/cad/%/main.scad tools/cad/stl-bbox.awk | preflight ; @$(call stl_export,$@,$<,stl)
build/gate/%.stl: tools/cad/fixtures/%.scad tools/cad/stl-bbox.awk | preflight ; @$(call stl_export,$@,$<,gate)
build/gate-fit/%.stl: tools/cad/fixtures/%.scad tools/cad/stl-volume.awk | preflight ; @$(call scad,$@,$<,$(STL_FMT),gate-fit); $(FIT_VOL) -v name='$*' $@
build/fit/%.stl: $(FIT_SRC) | preflight ; @$(call scad,$@,$<,$(STL_FMT) $(call fit_defs,$*),fit)
build/fit-diag/%.stl: $(FIT_SRC) | preflight ; @$(call scad,$@,$<,$(STL_FMT) $(call fit_defs,$*) -D fit_diag=true,fit-diag)

gate-test: ## Prove the warnings, torque, bed and fit gates fail on their fixtures
	@$(call expect_fail,build/gate/warning.stl,WARNING,warnings)
	@$(call expect_fail,build/gate/torque-infeasible.stl,torque budget exceeded,torque)
	@$(call expect_fail,build/gate/bed-oversize.stl,exceeds bed_max,bed)
	@$(call expect_fail,build/gate-fit/fit-interference.stl,interference,fit)

check-fit: $(FIT_STLS) ## Check the leg assembly for interference over the fit pose grid
	@[ -n "$(FIT_POSES)" ] || { echo "error: check-fit: fit_alpha/fit_phi not found in $(PARAMS)" >&2; exit 1; }
	@fail=; for p in $(FIT_POSES); do \
	  $(FIT_VOL) -v name="$$p" build/fit/$$p.stl && continue; \
	  fail="$$fail $$p"; \
	  $(MAKE) --no-print-directory build/fit-diag/$$p.stl && \
	    $(FIT_VOL) -v name="$$p" -v pairs=build/log/fit-diag/$$p.log build/fit-diag/$$p.stl; \
	done; \
	if [ -n "$$fail" ]; then echo "error: check-fit: interference in poses:$$fail" >&2; exit 1; fi; \
	echo "check-fit: OK ($(words $(FIT_POSES)) poses, tolerance $(FIT_VOL_TOL) mm3)"
```

- `doctor` adds the lines `stl format:` (asciistl or default), `bed_max: $(BED_MAX)` and `fit grid: $(FIT_ALPHA) x $(FIT_PHI)`.
- `.DELETE_ON_ERROR` already removes a failed target. `bed_check` also removes it explicitly, because the spec requires it.
- `check-fit` is never a prerequisite of `stl` and never writes to `build/stl/`. `-d` dep files in `build/dep/fit/` re-export poses when the geometry changes.
- Adding `-j` is optional (D2). The CI runs it serially unless it measures more than 5 minutes (confirm).

`tools/cad/stl-bbox.awk`:

```awk
# SPDX-License-Identifier: MIT
# Mesh bed gate. Usage: awk -v max=180 -v name=<part> -f tools/cad/stl-bbox.awk <file.stl>
BEGIN { if (max + 0 <= 0) { err = "BED_MAX is not set (bed_max not found in params.scad)"; exit 1 } }
FNR == 1 && $1 != "solid" { err = "not an ASCII STL"; exit 1 }
$1 == "vertex" {
    for (i = 1; i <= 3; i++) {
        v = $(i + 1) + 0
        if (n == 0 || v < lo[i]) lo[i] = v
        if (n == 0 || v > hi[i]) hi[i] = v
    }
    n++
}
END {
    if (err == "" && n == 0) err = "STL has no vertices"
    if (err != "") { printf "error: %s: %s\n", name, err > "/dev/stderr"; exit 1 }
    s = sprintf("[%.2f, %.2f, %.2f]", hi[1] - lo[1], hi[2] - lo[2], hi[3] - lo[3])
    if (hi[1] - lo[1] > max + 0 || hi[2] - lo[2] > max + 0 || hi[3] - lo[3] > max + 0) {
        printf "error: %s: STL size %s exceeds bed_max %s mm\n", name, s, max > "/dev/stderr"; exit 1
    }
    printf "%s: STL size %s mm, bed_max %s mm\n", name, s, max
}
```

`tools/cad/stl-volume.awk` (the volume per facet is `v1 . (v2 x v3) / 6`; its sum is the volume of each closed shell):

```awk
# SPDX-License-Identifier: MIT
# Fit gate: signed volume of an ASCII STL. Facets with x < -500 are the sentinel (at least one must exist).
# Group g = int((x1 + 500) / 1000): g = 0 is the scene; with -v pairs=<log>, g >= 1 is fit pair g - 1
# (fit.scad offsets pair i by 1000 * (i + 1) mm in X) and names come from ECHO: "fit-pair", i, "a", "b".
# Usage: awk -v tol=2.0 -v name=<pose> [-v pairs=<log>] -f tools/cad/stl-volume.awk <file.stl>
BEGIN {
    if (tol == "") { err = "FIT_VOL_TOL is not set (fit_vol_tol not found in params.scad)"; exit 1 }
    if (pairs != "")
        while ((getline line < pairs) > 0)
            if (line ~ /^ECHO: "fit-pair"/) {
                split(line, f, "\""); i = f[3]; gsub(/[^0-9]/, "", i); label[i + 1] = f[4] " x " f[6]
            }
}
FNR == 1 && $1 != "solid" { err = "not an ASCII STL"; exit 1 }
$1 == "vertex" {
    k++; x[k] = $2 + 0; y[k] = $3 + 0; z[k] = $4 + 0
    if (k < 3) next
    k = 0
    if (x[1] < -500) { sentinel++; next }
    g = int((x[1] + 500) / 1000)
    a = x[1] - 1000 * g; b = x[2] - 1000 * g; c = x[3] - 1000 * g
    vol[g] += (a * (y[2] * z[3] - z[2] * y[3]) - b * (y[1] * z[3] - z[1] * y[3]) + c * (y[1] * z[2] - z[1] * y[2])) / 6
}
END {
    if (err == "" && !sentinel) err = "sentinel missing (truncated or empty export)"
    if (err != "") { printf "error: fit: %s: %s\n", name, err > "/dev/stderr"; exit 1 }
    if (pairs != "") {
        for (g in vol) {
            v = vol[g] < 0 ? -vol[g] : vol[g]
            if (g + 0 > 0 && v > tol + 0)
                printf "fit:   %s: %s: interference %.3f mm3\n", name, ((g in label) ? label[g] : "pair " (g - 1)), v > "/dev/stderr"
        }
        exit 0
    }
    v = vol[0] < 0 ? -vol[0] : vol[0]
    if (v > tol + 0) { printf "error: fit: %s: interference volume %.3f mm3 exceeds tolerance %s mm3\n", name, v, tol > "/dev/stderr"; exit 1 }
    printf "fit: %s: %.3f mm3, tolerance %s mm3\n", name, v, tol
}
```

Subtracting the group origin keeps the terms small. The leg spans roughly x -31..200 mm, so it stays well inside group 0.

## 2. asm-leg refactor

- `hardware/cad/asm-leg/asm-leg.scad`: a library with no top-level instantiation. It includes params and the four part files.

```scad
asm_bodies = ["coxa-servo", "coxa-bracket", "femur-servo", "femur-plate-a", "femur-plate-b", "tibia-servo", "tibia", "foot"];
asm_colors = [["coxa-servo", "dimgray"], ["coxa-bracket", "orange"], ["femur-servo", "dimgray"], ["femur-plate-a", "steelblue"],
              ["femur-plate-b", "steelblue"], ["tibia-servo", "dimgray"], ["tibia", "orange"], ["foot", "black"]];
module asm_link_frame(alpha)       move([coxa_l, leg_lane_dy, cb_zmid]) yrot(-alpha) xrot(90) children();
module asm_tibia_frame(alpha, phi) move([coxa_l, leg_lane_dy, cb_zmid]) yrot(-alpha) move([femur_l, 0, 0]) yrot(-90 - phi) xrot(90) children();
module asm_body(name, alpha, phi)  // dispatch on name; unknown name -> assert(false, ...)
//   coxa-servo:    move([0, 0, cb_case_top]) zrot(180) servo_model(servo)
//   coxa-bracket:  coxa_bracket()
//   femur-servo:   femur_servo_frame() servo_model(servo)      (frame owned by coxa-bracket.scad)
//   femur-plate-a: asm_link_frame(alpha) move([0, 0, top_h]) xrot(180) femur_plate_a()
//   femur-plate-b: asm_link_frame(alpha) move([0, 0, -(servo_cage_depth + idler_boss_h + leg_axial_gap)]) femur_plate_b()
//   tibia-servo / tibia / foot: asm_tibia_frame(alpha, phi) ... as in the current main.scad
module asm_leg(alpha, phi) for (b = asm_bodies) color(kv_get(asm_colors, b, "asm colour")) asm_body(b, alpha, phi);
```

- `main.scad` becomes `include <asm-leg.scad>; leg_part_checks("asm-leg"); asm_leg(alpha, phi_nom);`. With `alpha = 0`, `leg_lane_dy = 0` and no gap (PR2), every transform reduces to the current `_femur_frame` / `_tibia_frame`, so the PNG is unchanged (byte-identical is to be confirmed; the fallback is a pixel compare).
- `fit.scad` is not an entry point, because it is not named `main.scad`:

```scad
include <BOSL2/std.scad>
include <asm-leg.scad>
fit_a = alpha; fit_p = phi_nom; fit_diag = false;       // make passes -D fit_a / fit_p / fit_diag
fit_pairs = [for (i = [0 : len(asm_bodies) - 2], j = [i + 1 : len(asm_bodies) - 1]) [asm_bodies[i], asm_bodies[j]]];
for (i = [0 : len(fit_pairs) - 1]) {
    if (fit_diag) echo("fit-pair", i, fit_pairs[i][0], fit_pairs[i][1]);
    right(fit_diag ? 1000 * (i + 1) : 0) intersection() { asm_body(fit_pairs[i][0], fit_a, fit_p); asm_body(fit_pairs[i][1], fit_a, fit_p); }
}
move([-1000, -1000, -1000]) cube(1);                     // sentinel: never empty, skipped by awk
```

- Fixtures (MIT header, as the existing ones):
  - `tools/cad/fixtures/bed-oversize.scad`: `include <../../../hardware/cad/common/params.scad>` plus `cube([bed_max + 10, 10, 10]);`
  - `tools/cad/fixtures/fit-interference.scad`: `intersection() { cube(10); right(9) cube(10); }` (100 mm3 of overlap) plus the same sentinel.

## 3. Geometry

Shared figures (mm): cage half-width 13.15, cage extent along the servo X axis [-20.2, 40.9], `cb_zmid` 23.1, femur axis at world x = 30.

**(a) Spacers (PR3).** Delete `fp_spacer_*`, the bosses and `_fp_bolts`. Both plates become a flat hull of two discs. `fp_d` and `fp_a_t` become aliases of the new `leg_plate_d` and `leg_plate_a_t`. The print envelope goes from about 86 x 72 x 30.8 to 86 x 72 x 5.7. The print pose is unchanged.

**(c1) Femur pocket (PR3).** Add `femur_servo_frame() servo_pocket(servo);` to the bracket `difference()`, so the web can no longer overlap the femur servo ear.

**(c3) New, hand-found (PR3).** The femur-end disc of plate A (r 15.5, y [-11.6, -5.9]) enters the web (x [9.8, 15.8], y ±15.5) by about 1.3 mm radially at every alpha (confirm). Fix: subtract `leg_plate_a_relief()`, a `ycyl` of diameter `leg_plate_d + 2*tol_loose` on the femur axis over the plate A lane ± `tol_loose`.

**B1 (PR4).**
- Transform: `femur_servo_frame() = move([coxa_l, leg_lane_dy, cb_zmid]) xrot(90) zrot(cb_femur_spin)` with `cb_femur_spin = -90`. The servo +X axis maps to world -Z.
- The shaft axis line, the coaxial idler boss, the plate A/B femur ends, the knee position and `leg_joint_span` are all unchanged. The lane offset only slides the joint along its own axis.
- Cage footprint, relative to the femur axis: x ±13.15, z [-40.9, +20.2], y [dy-3.3, dy+44.3] (with the boss).
- The web moves to `cb_web_x = coxa_l - 13.15 - wall` (x [10.85, 16.85]) and spans z from `cb_zmin = cb_zmid - 40.9 = -17.8` to 51.9.
- The bracket z-range grows from [-5.7, 51.9] (57.6) to [-17.8, 51.9] (69.7).
- The slide-in slot and the cable exit are at the servo +X end, which is now the open bottom rim. The servo inserts upward and the cable exits downward.
- Ear bolts run along world Y, at x = 30 ± 5 and z = 37.5 / -12.0. Heads are on the plate A side and nuts are trapped on the +Y floor.
- Leg-mount interface: `leg_mount_gap`, the arms and the femur axis height are unchanged. The part now reaches 12.1 mm below the bottom arm at radius 10.85-43.15 mm from the coxa axis. ADR-0004 records this as a body keep-out.
- Print pose: `up(-cb_zmin)`, on the cage and web rim. The bottom arm becomes a 12.1 mm overhang that needs supports (confirm).
- `leg_lane_dy = -5` moves plate A to y [-16.6, -10.9], clear of the coxa servo ear (y ±9.85) with a 1.05 mm gap. This absorbs **(c2)** without touching `coxa_l` or the tier. The foot lateral offset also changes from +3.7 to -1.3 mm.

**3.4 Clearance.** This extends the exploration's `clr(phi)`. The tibia cage/beam is a rectangle in joint coordinates about the knee `K = 55(cos a, sin a)`, with `u = (-sin s, cos s)`, `v = (-cos s, -sin s)` and `s = phi + alpha`. The cage spans sx [-20.2, 40.9] and sy ±13.15. The beam continues from sx -20.2 to -68 with a half-width tapering from 13.15 to 7. The femur cage is the fixed rectangle above. Minimum distance in mm, body down, joint convention (negative means overlap), all (confirm):

| alpha \ phi | -30 | -15 (alt.) | 0 | 20 | 45 |
|---|---|---|---|---|---|
| -30 | **-5.7** (the bare femur ear alone is -0.6) | +3.5 | +11.1 | +18.4 | +11.2 |
| 0 | +7.3 | >7 | +28.7 | +19.3 | +3.7 |
| 30 | +21.3 | >20 | +20.4 | +14.6 | +2.8 |

For reference, body up fails `(30, 45)`: the tibia end face lies inside the cage. Tilting the body 10-15 deg inboard still fails `(-30, -30)`, and beyond about 15 deg the cage hits the coxa servo body. The coxa servo, bracket arms, web and plates stay at least 17 mm clear in every grid pose.

**3.5 Verdict and B2 trigger.**
- B1 was predicted to fail the originally proposed grid (now narrowed): under D4 it failed `(-30, -30)`, and under world `phi` it would fail `(-30, 45)` (world convention rejected by the user). The world case is a knee angle of 75 deg, where the tibia cage end comes within 12.3 mm of the femur shaft, so no same-lane femur orientation can clear it.
- B1 is predicted to pass the whole narrowed grid `fit_phi = [-15, 0, 20, 45]` x `fit_alpha = [-30, 0, 30]` with a minimum clearance of about 2.8 mm at `(30, 45)` (hand-derived; confirm at apply).
- The B2 trigger fires at PR4 apply when `check-fit` reports any `{tibia, tibia-servo, foot} x {femur-servo, coxa-bracket}` pair above the tolerance, and that pair cannot be cleared by a cage trim that keeps a wall of at least 2 mm and leaves the servo pocket intact. It does not fire if the user has narrowed the grid.
- B2 outline: the tibia servo moves to its own Y-lane on the far side of plate A, with separate femur and tibia idler plates. This removes every tibia-vs-femur-servo pair. It needs a new plate topology, is likely to exceed 400 lines, and brings back a tie problem on the tibia side.

**(c2) fallback.** If `leg_lane_dy` is rejected, `coxa_l +4` fixes (c2), but it changes the tier lengths and the femur margin (about 1.009). It MUST be flagged to the user first.

**Torque.** No impact. The gate reads only the lengths, `n_servo` and `m_body_kg`, so the margin stays 1.016. The real mass changes by about -5 to -10 g per leg: the spacers and two M3 bolts go, and the web gains about 2 g. The model ignores this; only the weighing in the calibration plan captures it.

## 4. Params additions (`params.scad`, one `name = value;` per line so that `param()` can read it)

| Name | Value | PR |
|---|---|---|
| `fit_alpha`, `fit_phi` | `[-30, 0, 30]`, `[-15, 0, 20, 45]` (narrowed by user decision; previously `[-30, 0, 20, 45]`) | 2 |
| `fit_vol_tol` | `2.0` (mm3; previously `0.1`) | 2 |
| `leg_lane_dy` | `0` in PR2, `-5` in PR4 | 2/4 |
| `leg_axial_gap` | `tol_fit` (0.2) | 3 |
| `leg_plate_d`, `leg_plate_a_t` | `horn_d + 2*wall`, `horn_t + tol_fit + wall` | 3 |

`leg_part_checks(name)` loses its `size` argument. `bed_max = 180` stays and is read by make.

## 5. ADR-0004 and docs

`docs/adr/0004-assembly-fit-and-mesh-bed-gates.md` (Status Proposed in PR1, Accepted in PR4) has these sections: Context, Decision, Amendments, Alternatives, Consequences. Its decisions:
1. Mesh bed gate.
2. check-fit: grid, pose convention, pairs, sentinel, tolerance and gap.
3. `gate-test` with four fixtures through `expect_fail`.
4. The CI `check-fit` step.
5. ASCII STL export.
6. Flat plates, the pocket cut and the plate A relief.
7. B1 (or B2 per the decision), `leg_lane_dy`, and the body keep-out.

It amends:
- ADR-0002 item 5 (gate-test proves four gates).
- ADR-0002 item 6 (CI runs `check-fit`).
- ADR-0003 item 6 (asm has no bed assert; bed fit is now a mesh gate; `asm-leg` hosts the non-entry `fit.scad`).
- Beyond the proposal, ADR-0002 item 4 (`check-fit` entry point and `build/fit/`) and ADR-0003 item 5 (no M3 spacers). These are needed to stay consistent.

Doc updates:
- `hardware/cad/README.md`: outputs (ASCII STL, bed gate, `check-fit`, `build/fit/`), the asm line, the `main.scad` checks (no bed fit), fasteners (no plate spacers), the warnings gate (four fixtures), and a new "Fit check" section.
- `leg-torque-budget.md`: a "Geometry and the torque model" note (geometry does not enter the model, the margin is unchanged, and the real mass change is covered only by calibration).

## 6. Verification

| PR | Check | Expected |
|---|---|---|
| 1 | `docker run --rm --entrypoint openscad $IMG --help 2>&1 \| rg -- --export-format` | the flag exists (confirm) |
| 1 | `make clean stl TOOLCHAIN=docker`; `head -c5 build/stl/smoke.stl` | exit 0; `solid`; sizes printed equal to the verify-report ones (86.4x59.8x57.6, 86.0x72.0x30.8, 120.9x26.3x47.6, 16.2x16.2x26.0) |
| 1 | `make stl BED_MAX=50; echo $?`; `test ! -f build/stl/leg-tibia.stl` | non-zero, `exceeds bed_max`, STL removed |
| 1 | `rg -n '_size\(' hardware/cad` | no match |
| 1-2 | `make gate-test` | 3 (PR1) / 4 (PR2+) `OK` lines, exit 0. Temporarily replacing a fixture with `cube(1)` makes it exit 1. |
| 2 | `git worktree add ../base main && make -C ../base render && make render && cmp ../base/build/png/asm-leg.png build/png/asm-leg.png` | identical (confirm) |
| 2 | `make check-fit FIT_VOL_TOL=1e9` ; `ls build/fit/*.stl \| wc -l` | exit 0; 12 |
| 2 | `make check-fit` | non-zero with per-pair lines that include `tibia x coxa-bracket` at `a0_p20`: the red baseline, recorded in the PR body |
| 2 | `make -n stl \| rg -c 'fit'` ; `ls build/stl build/png \| rg fit` | 0 ; none |
| 3 | `make check-fit` | spacer, `femur-servo x coxa-bracket` and `femur-plate-a x coxa-bracket` pairs gone; only (b) and (c2) remain |
| 4 | `make clean stl render gate-test check-fit TOOLCHAIN=docker 2>&1 \| rg -c 'WARNING\|ERROR'` | exit 0; 0 matches; `check-fit: OK (12 poses` |
| 4 | `rg 'femur peak' build/log/stl/leg-tibia.log` | `margin 1.02` (unchanged) |

CI: `gate-test` runs 2 extra fast fixtures. `check-fit` costs about 12 x (1-2 s container start + 3-15 s render), roughly 1-4 minutes (confirm), well inside the 20-minute timeout. ASCII STL artifacts grow about 4-5 times (confirm).

## 7. PR slices (tracker `feat/leg-interference-fix`; the openspec change folder is committed on the tracker base, outside the PR diffs)

| PR | Content | Est. lines | CI state |
|---|---|---|---|
| 1 | `STL_FMT` probe, `param()`, `bed_check`, `stl-bbox.awk`, `bed-oversize` fixture, `expect_fail` + gate-test refactor, `*_size()` removal, ADR-0004 skeleton | ~180 | green |
| 2 | `asm-leg.scad`, `main.scad`, `fit.scad`, `stl-volume.awk`, `check-fit`/fit rules, `fit-interference` fixture, fit params | ~300 | green (no CI step yet; the fixture is proven by gate-test) |
| 3 | Flat plates, (c1) pocket cut, (c3) relief, `leg_axial_gap`, `leg_plate_*` | ~90 | green |
| 4 | B1 bracket, `leg_lane_dy = -5`, grid decision, **CI `Fit check` step after `Gate test`**, ADR-0004 Accepted, README, torque note | ~220 | green only if check-fit passes |

The chain merges as a unit. The tracker-to-main PR runs the full CI, including `check-fit`.

## Threat Matrix

| Boundary | Applicability |
|---|---|
| Documentation-like paths | N/A: nothing classifies or executes files by name; the make rules take only `.scad` sources |
| Git repository selection / Commit / Push / PR commands | N/A: no VCS or PR automation. Only the verification uses `git worktree`, run manually. |

The shell recipes interpolate `BED_MAX`/`FIT_VOL_TOL` from local make variables that the developer controls. This is not a trust boundary.

## Migration / Rollout

No data migration. Roll back per slice or by reverting the tracker merge. ADR-0004 is reverted as a whole file.

## Open Questions

- [x] RESOLVED: keep B1 and narrow `fit_phi` to `[-15, 0, 20, 45]` (spec deltas updated; previously `[-30, 0, 20, 45]`).
- [x] RESOLVED: D4 joint-space convention for `phi` confirmed.
- [ ] Ear-bolt heads are not modelled. The near-end heads (r 15.24 < 15.5) protrude about 0.4 mm into the plate A sweep; this is also true of the current design. Flip them (nut on top) or use low-profile heads.
- [ ] Print pose and supports of the taller B1 bracket.
