# Exploration: openscad-toolchain

## Current State
- `Makefile`: `stl`, `render`, `clean` are placeholders (exit 1). `help` regex is `[a-zA-Z_-]+:.*## `.
- `.gitignore` already covers `/build/`, `*.stl`, `*.png` (with `!/docs/**/*.png`).
- ADR-0001 deferred "OpenSCAD library strategy (BOSL2 as a submodule)" and "Hosting and CI (GitHub Actions)".
- Spec conflicts to resolve with MODIFIED deltas:
  - `repo-structure` "Deferred scope excluded" forbids `.gitmodules`, `*.scad`, `.github/workflows`.
  - `repo-hygiene` "Placeholder target" uses `make stl` as a failing placeholder.
- `licensing` spec does not cover `libs/` (BOSL2 is BSD-2-Clause).

## Verified external facts (2026-09-29)
- Stable OpenSCAD is still 2021.01 (apt, Homebrew stable, docker `latest`). No Manifold, no `--backend`, headless PNG needs xvfb.
- Manifold is default in dev snapshots since 2025-08; `--backend=cgal` opts out.
- `openscad/openscad:dev.<date>` Docker images (amd64/arm64) ship a snapshot with EGL headless PNG. Retention of dated tags not verified.
- `--hardwarnings` exit code is unreliable (issue 3616); also scan stderr for `WARNING|ERROR`.
- `openscad -o out.stl -d out.d in.scad` emits a make dependency file.
- BOSL2: BSD-2-Clause, beta, needs `OPENSCADPATH` pointing at `libs/`; pin by SHA via submodule.
- macOS: `brew install --cask openscad@snapshot`; DMG binary not on PATH.

## Forks and recommendations
- **A. Canonical build:** A1 apt 2021.01 / **A2 Docker `dev.<date>` pinned (recommended)** / A3 AppImage.
- **B. Local Makefile:** B1 local binary only / **B2 local with Docker fallback (recommended)**.
- **C. BOSL2:** **C1 submodule at `libs/BOSL2` (recommended)** / C2 vendored / C3 user-installed.
- **D. Warnings gate:** D1 `--hardwarnings` only / **D2 flag + stderr scan (recommended)**.

## Makefile sketch
- Entry points by convention (e.g. `hardware/cad/**/main.scad`), outputs `build/stl/%.stl`, `build/png/%.png`, `-d` dependency files, `BACKEND` flag only if supported, `clean` = `rm -rf build`.
- Fail with a clear message if `libs/BOSL2/std.scad` is missing (submodule not initialized).

## CI sketch
- `.github/workflows/cad.yml`: PR + push to main, path filters, checkout with submodules, `make stl render` via Docker image, upload `build/` artifacts (retention ~14 days), `contents: read`.

## Affected areas
Makefile, `.gitmodules`, `libs/BOSL2`, `hardware/cad/smoke/main.scad`, `.github/workflows/cad.yml`, READMEs (libs, hardware/cad, root), optional `LICENSES/BSD-2-Clause.txt`, `docs/adr/0002-openscad-toolchain.md`, `openspec/config.yaml`, spec deltas (repo-structure, repo-hygiene, licensing, plus new `cad-build` and `ci` capabilities).

## Risks
Version drift local vs CI; dated Docker tag retention; unreliable `--hardwarnings`; submodule friction; BOSL2 beta API; existing specs contradict this change unless MODIFIED; multi-platform Makefile portability.

## Open items
Local `openscad` install status; BOSL2 pin SHA; Docker `bookworm` OpenSCAD version; dated tag retention.

## Product decisions needed
1. Canonical OpenSCAD build (A2 vs A1). 2. Local behavior (B1 vs B2). 3. BOSL2 pin and bump policy. 4. Entry-point convention. 5. Warnings gate scope (local + CI vs CI only). 6. CI outputs on every PR vs main only. 7. PNG camera/size. 8. BSD-2 license text in `LICENSES/`. 9. Spec organization. 10. Scope: smoke test is the only `.scad`.

## Ready for Proposal
Yes, once decisions 1-4 are answered; the rest have safe defaults.
