# Apply Progress: openscad-toolchain

## PR 1 (branch feat/openscad-toolchain-1-bosl2): tasks 1.1-1.6 done

- 1.1 BOSL2 submodule added at libs/BOSL2, pinned to 402be424319c2ed1bd8c11f29a71fe22b16b06b2 (v2.0.763, tip of origin/master at apply time).
- 1.2 LICENSES/BSD-2-Clause.txt copied with `cp` from libs/BOSL2/LICENSE (verified with `cmp`).
- 1.3 libs/README.md: table, init and bump commands.
- 1.4 .editorconfig: `[.gitmodules]` with `indent_style = tab`.
- 1.5 README.md: `libs/BOSL2` BSD-2-Clause license row.
- 1.6 Verified: `git submodule status libs/BOSL2` shows the pinned SHA; license file exists.

## PR 2 (branch feat/openscad-toolchain-2-build): tasks 2.1-2.12 done

- 2.1 Image pinned: `openscad/openscad:dev.2026-01-19@sha256:0af06bc2aa7a45d18b01a23cfb9dae6dddcd9542611e7be50edea6beb3b52fa7` (index digest; amd64, arm64, riscv64). dev.2026-09-28 and dev.2026-09-23 rejected: PNG fails with GLAD error.
- 2.2 In-image binary `/usr/local/bin/openscad`; `--entrypoint openscad` works.
- 2.3-2.5 smoke part, warning fixture, Makefile written per design.
- 2.6 BOSL2 smoke build: no WARNING/ERROR (local 2026.09.29 and Docker 2026.01.19).
- 2.7 EGL PNG in Docker (dev.2026-01-19): no WARNING.
- 2.8 `build/dep/stl/smoke.d` first line is `build/stl/smoke.stl: \`.
- 2.9 ADR-0002 + index row. 2.10 hardware/cad/README.md. 2.11 openspec/config.yaml.
- 2.12 all shell checks run (see return summary). Local openscad: 2026.09.29.

Deviations: image tag (above); no "Nothing to be done" message (preflight always runs); gate macro removes output on failure; internal `TC` variable.

Not committed (per instructions). Remaining: PR 3 (3.1-3.4).

## PR 3 (branch feat/openscad-toolchain-3-ci): tasks 3.1-3.3 done, 3.4 pending

- 3.1 SHAs (lightweight tags, commit objects): actions/checkout v7.0.1 = 3d3c42e5aac5ba805825da76410c181273ba90b1; actions/upload-artifact v7.0.1 = 043fb46d1a93c77aae656e7c1c64a875d1fc6a0a.
- 3.2 `.github/workflows/cad.yml` created; `actionlint` and `yaml.safe_load` pass. Checkout uses `submodules: recursive`.
- 3.3 README: status, `--recurse-submodules` clone, prerequisites, `make stl render doctor`, ADR-0002 link, placeholders are firmware/software/docs only; repo map and license table consistent.
- 3.4 NOT done: needs the PR CI run after the PR is opened.

Not committed (per instructions).
