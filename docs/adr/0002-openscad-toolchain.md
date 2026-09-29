# ADR-0002: OpenSCAD toolchain

## Status

Accepted

## Date

2026-09-29

## Context

ADR-0001 deferred CAD tooling: it says CI will build artifacts later and left `make stl` and `make render` as placeholders. The repository now needs a reproducible way to turn OpenSCAD sources into STL and PNG files, locally and in CI, with the same result in both places. Accepted ADRs are immutable, so this ADR resolves the deferred items without editing ADR-0001.

## Decision

1. **Container image.** The canonical toolchain is `openscad/openscad:dev.2026-01-19@sha256:0af06bc2aa7a45d18b01a23cfb9dae6dddcd9542611e7be50edea6beb3b52fa7`. The digest is the multi-arch index digest (amd64, arm64, riscv64), so CI (amd64) and Apple Silicon (arm64) resolve the same reference. The tag keeps it readable; the digest keeps it immutable. The tag `dev.2026-09-28` was rejected at apply time: its PNG export fails with "Can't create OffscreenView: Unable to initialize GLAD" (as does `dev.2026-09-23`), while `dev.2026-01-19` renders PNG without warnings.
2. **Toolchain selection.** `TOOLCHAIN=auto` (default) uses a local `openscad` (on `PATH`, or the macOS app bundle) when found, otherwise the pinned image. `TOOLCHAIN=local|docker` forces one. A local binary without `--backend` (Manifold) gets a warning; the CI image is canonical, so use `TOOLCHAIN=docker` for parity. In Docker mode the repository is mounted at the same absolute path and the container runs with the host uid/gid, so paths in dependency files are valid on the host and `build/` stays user-owned.
3. **BOSL2.** BOSL2 is a git submodule at `libs/BOSL2`, pinned to `402be424319c2ed1bd8c11f29a71fe22b16b06b2` (v2.0.763), under BSD-2-Clause. The Makefile exports `OPENSCADPATH=libs`, so parts use `include <BOSL2/std.scad>`. A missing submodule fails with a `git submodule update --init` hint.
4. **Entry points and outputs.** Only `hardware/cad/<part>/main.scad` is built, with `<part>` restricted to `[a-z0-9-]`. `make stl` writes `build/stl/<part>.stl`; `make render` writes `build/png/<part>.png`. `make clean`, `make doctor` and `make gate-test` are the other entry points.
5. **Warnings gate.** Every OpenSCAD call passes `--hardwarnings` and its stderr is scanned for `WARNING|ERROR`; a match, or a non-zero exit, fails the build and removes the output. `make gate-test` builds the fixture `tools/cad/fixtures/warning.scad` and passes only when the build fails and the output contains `WARNING`, which proves the gate still fires.
6. **CI.** A GitHub Actions workflow runs on every pull request and on pushes to `main`, on the `ubuntu-24.04` host runner with `TOOLCHAIN=docker` (a job-level `container:` would break submodule checkout, which needs `git`). It runs `doctor`, `gate-test`, then `stl render`, and uploads `build/stl` and `build/png` as an artifact. Actions are pinned by full commit SHA. The workflow itself lands in a follow-up change.
7. **PNG camera.** PNG previews use `--imgsize=1024,768 --autocenter --viewall --render`.

## Alternatives considered

- **Tag-only or digest-only image pin:** rejected; a tag alone is mutable, a digest alone is unreadable.
- **Job-level `container:` in CI:** rejected; checkout without `git` cannot fetch submodules.
- **Post-processing `.d` files:** rejected in favor of an empty `%.scad: ;` rule, so a deleted include rebuilds the part instead of failing.
- **Documented manual warnings check:** rejected; `gate-test` proves the gate on every CI run.
- **Vendoring BOSL2 or a package manager:** rejected; a submodule gives an exact pin and a small diff.

## Consequences

- Local and CI builds run the same OpenSCAD bytes when `TOOLCHAIN=docker` is used.
- A local OpenSCAD older than the image may produce different output or lack Manifold; `make doctor` shows what is in use.
- Bumping either pin is a deliberate, reviewed change.
- Newer `dev` images may fix or reintroduce the PNG offscreen failure; re-verify `make render TOOLCHAIN=docker` on every image bump.

## Bump procedure

1. Image: choose a `dev.<date>` tag, run `docker buildx imagetools inspect openscad/openscad:<tag>`, and copy the index (top-level) `Digest`. Update `OPENSCAD_IMAGE` in the `Makefile` and this ADR. Run `make clean stl render gate-test TOOLCHAIN=docker`; it must print no `WARNING`.
2. BOSL2: `git -C libs/BOSL2 fetch && git -C libs/BOSL2 checkout <sha>`, then commit the new gitlink. Update the pin in `libs/README.md` and this ADR, and refresh `LICENSES/BSD-2-Clause.txt` if the upstream `LICENSE` changed.

License: CC-BY-SA-4.0 — see [LICENSES/CC-BY-SA-4.0.txt](../../LICENSES/CC-BY-SA-4.0.txt)
