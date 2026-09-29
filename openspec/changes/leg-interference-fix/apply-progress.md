# Apply progress: leg-interference-fix

Mode: Standard (Strict TDD false). Store: openspec. Chain: feature-branch-chain.

## PR1: Mesh bed gate (tasks 1.1-1.12): COMPLETE, 12/12

Remaining: PR2 (2.1-2.14), PR3 (3.1-3.8), PR4 (4.1-4.13) not started.

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
