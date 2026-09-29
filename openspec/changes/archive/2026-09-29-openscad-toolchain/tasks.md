# Tasks: OpenSCAD Toolchain

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~410 total (PR1 ~60, PR2 ~260, PR3 ~90) |
| 400-line budget risk | Medium (each PR under 400) |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 |
| Delivery strategy | ask-on-risk |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No (chain strategy already chosen by user)
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | BOSL2 submodule, license, docs | PR 1 (base = tracker branch off main) | `git submodule status libs/BOSL2` | N/A: no executable | Revert PR 1 |
| 2 | Makefile, smoke, gate, ADR | PR 2 (base = PR 1 branch) | `make gate-test` | `make clean stl render` | Revert PR 2 |
| 3 | CI workflow, README usage | PR 3 (base = PR 2 branch) | `rg -n 'contents: read' .github/workflows/cad.yml` | CI run on the PR | Revert PR 3 |

## PR 1: Submodule and licensing

- [x] 1.1 Pin BOSL2 SHA; `git submodule add https://github.com/BelfrySCAD/BOSL2.git libs/BOSL2` at it (`.gitmodules`).
- [x] 1.2 Create `LICENSES/BSD-2-Clause.txt` verbatim from BOSL2 `LICENSE` at the pinned SHA.
- [x] 1.3 Edit `libs/README.md`: table (library, path, upstream, `BSD-2-Clause`, pin, init/bump commands).
- [x] 1.4 Edit `.editorconfig`: add `[.gitmodules]` with `indent_style = tab`.
- [x] 1.5 Edit `README.md`: add `libs/BOSL2` BSD-2-Clause license row.
- [x] 1.6 Verify: `git submodule status libs/BOSL2` shows the pinned SHA; `LICENSES/BSD-2-Clause.txt` exists.

## PR 2: Build system

- [x] 2.1 Apply-time: pick `dev.<date>` tag and its multi-arch index digest (`docker buildx imagetools inspect`); record it.
- [x] 2.2 Apply-time: confirm the binary name/path in the image works with `--entrypoint openscad`.
- [x] 2.3 Create `hardware/cad/smoke/main.scad` (SPDX header, BOSL2 include, `cuboid`).
- [x] 2.4 Create `tools/cad/fixtures/warning.scad` (`cube(size = undefined_on_purpose);`).
- [x] 2.5 Edit `Makefile`: variables, detection, `scad` macro, pattern rules, `preflight`, `stl`, `render`, `clean`, `doctor`, `gate-test`, `%.scad: ;`, `.DELETE_ON_ERROR`, placeholders, `%-12s` help.
- [x] 2.6 Apply-time: confirm BOSL2 at the pinned SHA builds `smoke` with no WARNING.
- [x] 2.7 Apply-time: confirm the EGL PNG render prints no WARNING (Docker mode).
- [x] 2.8 Apply-time: confirm the first line of `build/dep/stl/smoke.d` is `build/stl/smoke.stl:`.
- [x] 2.9 Create `docs/adr/0002-openscad-toolchain.md` (image tag+digest, BOSL2 SHA, gate, CI, camera, bump procedure); add index row in `docs/adr/README.md`.
- [x] 2.10 Edit `hardware/cad/README.md`: part convention (`[a-z0-9-]`, `main.scad`), outputs, gate.
- [x] 2.11 Edit `openspec/config.yaml`: OpenSCAD and GitHub Actions context; `verify.build_command: make stl render`, `verify.test_command: make gate-test`.
- [x] 2.12 Verify (no test runner; shell checks):
  - `make help` lists `stl render clean doctor gate-test`.
  - `make clean && make stl render && test -s build/stl/smoke.stl && test -s build/png/smoke.png`.
  - Second `make stl` is silent and runs no OpenSCAD (make prints no "Nothing to be done" because the phony `preflight` always runs); `touch hardware/cad/smoke/main.scad` rebuilds.
  - `rg -q '^build/stl/smoke.stl:' build/dep/stl/smoke.d`.
  - `make gate-test` prints `gate-test: OK`.
  - `git submodule deinit -f libs/BOSL2; make stl` fails with hint; then `git submodule update --init`.
  - `make clean stl render TOOLCHAIN=docker && test -O build/stl/smoke.stl`.
  - `make firmware` exits non-zero; `git check-ignore build/stl/smoke.stl`; `make clean` twice exits 0.

## PR 3: CI and docs

- [x] 3.1 Resolve full commit SHAs for `actions/checkout` and `actions/upload-artifact` (`# vX` comments).
- [x] 3.2 Create `.github/workflows/cad.yml`: triggers, `contents: read`, concurrency, `ubuntu-24.04`, `timeout-minutes: 20`, `TOOLCHAIN: docker`, steps `doctor` → `gate-test` → `stl render` → upload (`cad-${{ github.sha }}`, 14 days, `if-no-files-found: error`).
- [x] 3.3 Edit `README.md`: status, `--recurse-submodules` clone, prerequisites, `make stl render doctor`, ADR-0002 link, placeholders are `firmware/software/docs` only.
- [x] 3.4 Verify: the PR CI run passes and artifact `cad-<sha>` holds `smoke.stl` and `smoke.png`.
