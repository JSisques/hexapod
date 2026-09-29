# Tasks: Leg interference fix

Grid (user-narrowed): `fit_alpha` [-30,0,30], `fit_phi` [-15,0,20,45]. Pose convention: phi = knee joint angle. Geometry: B1. Strict TDD: false (fixtures are the RED proofs).

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~790 total (PR1 ~180, PR2 ~300, PR3 ~90, PR4 ~220) |
| 400-line budget risk | High as one PR; each slice under 400 |
| Chained PRs recommended | Yes |
| Suggested split | PR1 -> PR2 -> PR3 -> PR4 |
| Delivery strategy | ask-on-risk |
| Chain strategy | feature-branch-chain |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

Tracker branch `feat/leg-interference-fix` off `main` (base `main`). PR1 base = tracker; PR2 base = PR1 branch; PR3 base = PR2 branch; PR4 base = PR3 branch. Only the tracker merges to main. The change folder is committed on the tracker base, outside PR diffs. Decision before apply: confirm the chain (already chosen) and the PR1 start.

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Mesh bed gate, `expect_fail`, bed fixture, ADR skeleton | PR1 (~180) | `make gate-test` (3 OK) | `make stl BED_MAX=50` fails; `make clean stl TOOLCHAIN=docker` | Makefile, `stl-bbox.awk`, fixture, size-fn removal, ADR-0004 |
| 2 | Posed `asm-leg`, `fit.scad`, `check-fit`, fit fixture (no CI step) | PR2 (~300) | `make gate-test` (4 OK) | `make check-fit FIT_VOL_TOL=1e9` exit 0, 12 STLs; `make check-fit` red baseline | `asm-leg/`, `stl-volume.awk`, fit rules, fixture, params |
| 3 | Flat plates, pocket cut, plate A relief, `leg_axial_gap` | PR3 (~90) | `make check-fit` | spacer/pocket/c3 pairs gone from the report | `leg-femur-plate/`, `leg-coxa-bracket/` pocket line, params |
| 4 | B1 bracket, lane offset, CI step, docs, ADR Accepted | PR4 (~220) | `make check-fit` | `make clean stl render gate-test check-fit TOOLCHAIN=docker` and CI run | bracket, params, `cad.yml`, docs, ADR |

## PR1: Mesh bed gate (base: tracker)

- [x] 1.1 Probe `docker run --rm --entrypoint openscad $IMG --help 2>&1 | rg -- --export-format` on the pinned `dev.2026-01-19` image. Record: flag exists (asciistl supported).
- [x] 1.2 Apply-time check: export a smoke part as asciistl; confirm vertices carry enough precision (at least 4 decimals) and the header is `solid`. Record in the PR body.
- [x] 1.3 Create `tools/cad/stl-bbox.awk` (MIT header) as in design section 1.
- [x] 1.4 Edit `Makefile`: `HAS_EXPORT_FORMAT` probe, `STL_FMT`, `param()`, `BED_MAX`, `bed_check`, `stl_export`, and the `build/stl/%.stl` and `build/gate/%.stl` rules; add `stl-bbox.awk` prerequisite; add `doctor` lines (`stl format:`, `bed_max:`).
- [x] 1.5 Edit `Makefile`: add the `expect_fail` macro; refactor `gate-test` to use it for warning and torque; add the bed line.
- [x] 1.6 Create `tools/cad/fixtures/bed-oversize.scad` (`cube([bed_max + 10, 10, 10])`, MIT header).
- [x] 1.7 Remove `*_size()` functions, their size asserts and the `size` argument of `leg_part_checks` under `hardware/cad/common/`, `hardware/cad/leg-coxa-bracket/`, `hardware/cad/leg-femur-plate/`, `hardware/cad/leg-tibia/`, `hardware/cad/leg-foot/`, `hardware/cad/asm-leg/`.
- [x] 1.8 Create `docs/adr/0004-assembly-fit-and-mesh-bed-gates.md` skeleton (Status Proposed; Context, Decision items 1-7, Amendments, Alternatives, Consequences headings).
- [x] 1.9 Verify (shell): `make clean stl TOOLCHAIN=docker` exits 0, `head -c5 build/stl/smoke.stl` is `solid`, printed sizes equal the verify-report sizes (86.4x59.8x57.6, 86.0x72.0x30.8, 120.9x26.3x47.6, 16.2x16.2x26.0).
- [x] 1.10 Verify: `make stl BED_MAX=50; echo $?` non-zero with `exceeds bed_max`; `test ! -f build/stl/leg-tibia.stl`; `rg -n '_size\(' hardware/cad` has no match.
- [x] 1.11 Verify: `make gate-test` prints 3 OK lines; swap the bed fixture for `cube(1)` and confirm exit 1 with "gate did not fire"; restore.
- [x] 1.12 Verify: apply-time Manifold closed-shell check for the asciistl output (no warnings in `make stl`); PR CI green.

## PR2: asm-leg refactor and check-fit (base: PR1)

- [x] 2.1 Add to `hardware/cad/common/params.scad` one-line entries: `fit_alpha = [-30, 0, 30];`, `fit_phi = [-15, 0, 20, 45];`, `fit_vol_tol = 0.1;` (raised to `2.0` after PR2 verification; see 2.10), `leg_lane_dy = 0;`.
- [x] 2.2 Create `hardware/cad/asm-leg/asm-leg.scad` (library: `asm_bodies`, `asm_colors`, `asm_link_frame`, `asm_tibia_frame`, `asm_body`, `asm_leg`). No gap and no lane offset yet.
- [x] 2.3 Rewrite `hardware/cad/asm-leg/main.scad` to include the library and call `leg_part_checks("asm-leg"); asm_leg(alpha, phi_nom);`.
- [x] 2.4 Verify: build the base PNG in a `git worktree` of `main`; `cmp` it with the refactored `build/png/asm-leg.png`; if not byte-identical, run a pixel compare and record the result.
- [x] 2.5 Create `hardware/cad/asm-leg/fit.scad` (pairs, `fit_diag`, offsets, sentinel).
- [x] 2.6 Create `tools/cad/stl-volume.awk` as in design section 1.
- [x] 2.7 Edit `Makefile`: `FIT_*` variables, `fit_defs`, `build/fit/%`, `build/fit-diag/%`, `build/gate-fit/%` rules, `check-fit` target, `.PHONY`, `doctor` `fit grid:` line, `-d` dep files in `build/dep/fit/`.
- [x] 2.8 Create `tools/cad/fixtures/fit-interference.scad` (100 mm3 overlap plus sentinel); add the fit line to `gate-test`.
- [x] 2.9 Verify: `make gate-test` prints 4 OK lines; swapping the fit fixture for a non-overlapping one makes it exit 1.
- [x] 2.10 Verify (unverified in design): contact noise. `make check-fit FIT_VOL_TOL=1e9` exits 0 and `ls build/fit/*.stl | wc -l` is 12. Record per-pair volumes for zero-thickness contacts; confirm the noise is under 0.1 mm3 (result: noise reaches 1.1 mm3, so `fit_vol_tol` became 2.0 mm3) (or adjust `fit_vol_tol` and report).
- [x] 2.11 Verify: `make check-fit` is red with per-pair lines including `tibia x coxa-bracket` at `a0_p20`; record the baseline in the PR body. Confirm the awk names pairs via the ECHO log.
- [x] 2.12 Verify: Manifold closed shells; sentinel-only pose yields a parseable STL; `make -n stl | rg -c 'fit'` is 0; `ls build/stl build/png | rg fit` is empty.
- [x] 2.13 Measure `check-fit` runtime (12 poses, serial, docker); record it. If over 5 minutes, add `-j` to the future CI step design and note in ADR.
- [x] 2.14 Confirm no `.github/workflows/cad.yml` change in this PR; PR CI green (gate-test proves the fit fixture).

## PR3: Spacer removal and pocket cut (base: PR2)

- [x] 3.1 Add to params: `leg_axial_gap = tol_fit;`, `leg_plate_d = horn_d + 2*wall;`, `leg_plate_a_t = horn_t + tol_fit + wall;`; make `fp_d`, `fp_a_t` aliases.
- [x] 3.2 Edit `hardware/cad/leg-femur-plate/`: delete `fp_spacer_*`, bosses and `_fp_bolts`; both plates become a flat two-disc hull; add `leg_plate_a_relief()` subtraction (c3, ycyl d = `leg_plate_d + 2*tol_loose` on the femur axis over the lane +/- `tol_loose`).
- [x] 3.3 Edit `hardware/cad/leg-coxa-bracket/`: add `femur_servo_frame() servo_pocket(servo);` to the bracket `difference()` (c1).
- [x] 3.4 Edit `hardware/cad/asm-leg/asm-leg.scad`: apply `leg_axial_gap` in the `femur-plate-b` offset.
- [x] 3.5 Verify: `make stl` fits the bed; plate envelope about 86x72x5.7; print pose unchanged.
- [x] 3.6 Verify: `make check-fit` no longer lists the spacer, `femur-servo x coxa-bracket`, `femur-plate-a x coxa-bracket` (c3) pairs; only tibia-side (b) and coxa-servo ear (c2) remain. Confirm the c3 relief closes the ~1.3 mm overlap.
- [x] 3.7 Verify: `make gate-test` 4 OK; torque log still `margin 1.02`; PR CI green. (Local and Docker verified; PR CI pending until pushed.)
- [x] 3.8 (PR body text prepared in apply-progress; pending PR creation) Note in the PR body: flat plates lose out-of-plane stiffness (physical validation pending).

## PR4: B1 redesign, CI step, docs (base: PR3)

- [x] 4.1 Flag to the user BEFORE applying anything that touches `coxa_l`: the `coxa_l +4` (c2) fallback changes tier lengths and the femur margin (~1.009). Do not apply it without approval.
- [x] 4.2 Edit `hardware/cad/common/params.scad`: `leg_lane_dy = -5;`, `cb_femur_spin = -90`; edit `hardware/cad/leg-coxa-bracket/` for B1: `femur_servo_frame` with spin, `cb_web_x = coxa_l - 13.15 - wall`, `cb_zmin`, slot and cable exit at the open bottom rim, ear bolts along world Y (heads on plate A side, nuts trapped on the +Y floor), print pose `up(-cb_zmin)`.
- [x] 4.3 Ear-bolt head note: flip the bolts (nut on top) or use low-profile heads, since near-end heads (r 15.24 < 15.5) protrude ~0.4 mm into the plate A sweep. Record the choice in the bracket source and ADR-0004.
- [x] 4.4 Verify: `make check-fit` reports clearance for the narrowed grid; expect pass with minimum ~2.8 mm at `(30, 45)` (hand-derived). Record real numbers. If any `{tibia, tibia-servo, foot} x {femur-servo, coxa-bracket}` pair fails and a cage trim (wall at least 2 mm, pocket intact) cannot clear it, STOP and report to the user; do NOT switch to B2 silently.
- [x] 4.5 Verify: plate A clears the coxa servo ear (~1.05 mm gap) at `leg_lane_dy = -5`; if not, STOP and flag the `coxa_l +4` fallback to the user.
- [x] 4.6 Verify: bracket z-range about [-17.8, 51.9]; fits the bed; the bottom arm overhang (12.1 mm) needs supports; body keep-out below the arm recorded.
- [x] 4.7 Verify femur peak margin unchanged: `rg 'femur peak' build/log/stl/leg-tibia.log` shows `margin 1.02`.
- [x] 4.8 Edit `.github/workflows/cad.yml`: add a `Fit check` step (`make check-fit` in the pinned image) after `Gate test`.
- [x] 4.9 Finalise `docs/adr/0004-assembly-fit-and-mesh-bed-gates.md` (Status Accepted): decisions 1-7 and Amendments to ADR-0002 items 4 (`check-fit`, `build/fit/`), 5 (four gates), 6 (CI runs `check-fit`) and ADR-0003 items 5 (no M3 spacers) and 6 (no asm bed assert; mesh gate; non-entry `fit.scad`). Record the narrowed grid and the D4 convention.
- [x] 4.10 Edit `hardware/cad/README.md`: ASCII STL, bed gate, `check-fit`, `build/fit/`, asm line, no plate spacers, four fixtures, new "Fit check" section.
- [x] 4.11 Edit `docs/architecture/leg-torque-budget.md`: add the "Geometry and the torque model" note (margin unchanged; real mass change about -5 to -10 g per leg covered only by calibration).
- [x] 4.12 Verify: `make clean stl render gate-test check-fit TOOLCHAIN=docker 2>&1 | rg -c 'WARNING|ERROR'` gives 0 matches and exit 0; `check-fit: OK (12 poses`; `build/png` render outputs exist.
- [x] 4.13 Verify CI: PR CI runs `Gate test` then `Fit check` and passes; temporarily break geometry on a scratch branch to confirm the step fails (optional). Then open the tracker-to-main PR and confirm full CI (including `check-fit`) is green.
