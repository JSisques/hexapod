# Apply progress: leg-interference-fix

Mode: Standard (Strict TDD false). Store: openspec. Chain: feature-branch-chain.

## PR1: Mesh bed gate (tasks 1.1-1.12): COMPLETE, 12/12

Remaining: PR2 verification (2.4 docker half, 2.9-2.14), PR3 (3.1-3.8), PR4 (4.1-4.13).

## PR2: asm-leg refactor and check-fit (tasks 2.1-2.14): PARTIAL, authoring done (2.1-2.3, 2.5-2.8 marked [x]); verification not run

Authored (uncommitted): `hardware/cad/common/params.scad` (fit params), `hardware/cad/asm-leg/asm-leg.scad`, `hardware/cad/asm-leg/main.scad`, `hardware/cad/asm-leg/fit.scad`, `tools/cad/stl-volume.awk`, `tools/cad/fixtures/fit-interference.scad`, `Makefile` (FIT_* vars, gate-fit/fit/fit-diag rules, `check-fit`, `.PHONY`, doctor line, 4th gate-test line). awk runs with `LC_ALL=C`.

Observed before the shell became unavailable (auto-mode classifier returned no verdict for every later Bash call):
- `make doctor` prints `fit grid:   alpha -30 0 30 x phi -15 0 20 45`.
- Task 2.4 local: PNG built from a `main` worktree and from the refactor with local OpenSCAD 2026.09.29 are byte-identical (sha256 88102b5b...b2ac both). Docker compare not completed (base worktree needs a real copy of libs/BOSL2, a symlink is not visible in the container).

Not run: 2.4 docker half, 2.9 through 2.14 (gate-test 4 OK, contact noise, red baseline, closed shells, runtime, workflow check), on both toolchains.

### Work Unit Evidence (PR1)

| Evidence | Value |
|---|---|
| Focused test command | `make gate-test` (local and `TOOLCHAIN=docker`): `warnings OK`, `torque OK`, `bed OK`, exit 0. With the bed fixture swapped for `cube(1)`: `FAILED (bed gate did not fire)`, recipe exit 1 (make reports 2); fixture restored. |
| Runtime harness | `make clean stl TOOLCHAIN=docker` exit 0, STL starts with `solid`, sizes 86.40x59.80x57.60, 86.00x72.00x30.80, 16.20x16.20x26.00, 120.90x26.30x47.60 (identical on local); `make stl BED_MAX=50` fails with `exceeds bed_max 50 mm`; `make build/stl/leg-tibia.stl BED_MAX=100` fails and the STL is removed. `make stl render` on both toolchains: exit 0, 0 WARNING/ERROR, 6 PNGs. |
| Rollback boundary | `Makefile`, `tools/cad/stl-bbox.awk`, `tools/cad/fixtures/bed-oversize.scad`, `*_size()` removal in `hardware/cad/**`, `docs/adr/0004-*.md` and its row in `docs/adr/README.md` |

### Findings
- Pinned image `dev.2026-01-19` (2026.01.19) and local OpenSCAD 2026.09.29 both support `--export-format`; asciistl output has full double precision vertices and header `solid OpenSCAD_Model`.
- Deviation: awk is run with `LC_ALL=C` in `bed_check` and `param` (locale `es_ES` makes awk print/parse decimals with a comma, producing truncated sizes such as `[16,00, ...]`). Design snippet did not have it.
- Deviation: `stl-bbox.awk` output uses `expect_fail` labels `warnings OK` / `torque OK` (previous lines were `gate-test: OK` / `gate-test: torque OK`), as the design macro dictates.
- Not done in PR1 (deferred by task list): `hardware/cad/README.md` and ADR-0003 wording about "no bed-fit assert" (PR4 task 4.10 / 4.9); `.PHONY` unchanged (no `check-fit` yet).
- PR CI not run (no push).

## PR 2 verification (run by the orchestrator, local snapshot 2026.09.29 and pinned Docker image)

- 2.4: `asm-leg.png` built from `main` and from the refactor is byte-identical on both toolchains (Docker sha256 `ab01d1c131ec6b69cf2c649b10a978391eeb340c397cf4cf225f3150f3d0e764`).
- 2.9: `make gate-test` prints `warnings OK`, `torque OK`, `bed OK`, `fit OK`. With a non-overlapping fit fixture it prints `gate-test: FAILED (fit gate did not fire)`, exit non-zero; a sentinel-only pose parses as `0.000 mm3`. Fixture restored.
- 2.10 (contact noise): `make check-fit FIT_VOL_TOL=1e9` exits 0 with 12 STLs in `build/fit/`. Smallest per-pair volumes: `tibia x foot` 0.501 mm3 in every pose (tibia spigot tip enters the foot socket floor by `eps`), `femur-servo x tibia` 0.311 mm3 (a-30_p20), `coxa-bracket x tibia` 1.065 mm3 (a-30_p0). Smallest volume that is a real interference: `coxa-servo x femur-plate-a` 17.709 mm3. The configured tolerance of 0.1 mm3 is therefore below the eps-level model noise; a value of about 2 mm3 would separate noise from real overlaps. Open decision for the user (see PR body).
- 2.11 (red baseline on current geometry): all 12 poses fail (2174-6858 mm3 total per pose). Recurring pairs: `coxa-bracket x femur-servo` 93.6, `femur-servo x femur-plate-a/b` 790/715 at alpha -30 (1328/1208 at alpha 0), `coxa-bracket x femur-plate-a/b` 307/251 at alpha -30 (891/804 at alpha 0), `coxa-servo x femur-plate-a` 17.7, and for phi >= 20 `coxa-bracket x tibia` 628 (a-30_p20) up to 2085 (a-30_p45), `coxa-bracket x tibia-servo` 53-856, `femur-servo x tibia` up to 1980 (a-30_p45). Pair names are parsed from the ECHO log. Local and Docker reports are identical (0 diff lines). Note: `coxa-bracket x femur-plate-a/b` is larger than the verify-report listed; part of it may be the plate pivot boss modelled solid without a hole in the plate (to review in PR 3/4).
- 2.12: every export logs `Top level object is a 3D object (manifold)`, `Status: NoError`; `make -n stl` references no fit target; `build/stl` and `build/png` contain no fit files.
- 2.13: `make check-fit` from clean takes 3 min 32 s on both local and Docker (12 poses, serial).
- 2.14: `.github/workflows/cad.yml` is untouched in this PR.
