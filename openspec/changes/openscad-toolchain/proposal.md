# Proposal: OpenSCAD Toolchain

## Intent

The `stl`/`render`/`clean` targets are placeholders, and there is no CAD library or CI. This change delivers one reproducible OpenSCAD build (local and CI) before any part is designed. It resolves the BOSL2 and CI items that ADR-0001 deferred.

## Scope

### In Scope
- Canonical build on Docker `openscad/openscad:dev.<date>`, pinned by dated tag (date/digest recorded in ADR-0002)
- Makefile uses local `openscad` when present, else the pinned image. It warns when the local build lacks Manifold/`--backend`
- BOSL2 submodule at `libs/BOSL2`, pinned by SHA. The Makefile exports `OPENSCADPATH=libs` and fails with a hint when the submodule is uninitialized
- Entry points: only `hardware/cad/<part>/main.scad` files are exported, to `build/stl`, and rendered to `build/png`
- Warnings gate: `--hardwarnings` plus a stderr scan for `WARNING|ERROR`, locally and in CI
- PNG renders: 1024x768, `--autocenter --viewall --render`
- `.github/workflows/cad.yml` builds STL+PNG on every PR and on `main` and uploads artifacts with 14-day retention
- Smoke part `hardware/cad/smoke/main.scad`
- `LICENSES/BSD-2-Clause.txt` and a license note in `libs/README.md`
- `docs/adr/0002-openscad-toolchain.md`

### Out of Scope
- `params.scad`, servo, leg, or other real part design
- Firmware/software/docs build targets (stay placeholders)
- Release publishing, REUSE lint, BOSL2 bump automation

## Capabilities

### New Capabilities
- `cad-build`: entry-point convention, make targets, toolchain selection, BOSL2 path/guard, warnings gate, output layout
- `ci`: CAD workflow triggers, pinned image, submodule checkout, artifacts, retention, permissions

### Modified Capabilities
- `repo-structure`: "Deferred scope excluded" is relaxed to allow `.gitmodules`, the smoke `.scad`, and `.github/workflows`. `params.scad` stays excluded
- `repo-hygiene`: "Placeholder target" scenario changes: `stl`/`render`/`clean` are now real; `firmware`/`software`/`docs` stay placeholders
- `licensing`: ADDED requirement: third-party `libs/*` keep their upstream license, and the license text lives in `LICENSES/`

## Approach

Follow exploration recommendations A2/B2/C1/D2. Use pattern rules `build/stl/%.stl` and `build/png/%.png` with `-d` dependency files. Pass `--backend` only when the binary supports it. CI runs `make stl render` inside the pinned image with `contents: read`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `Makefile` | Modified | Real CAD targets |
| `.gitmodules`, `libs/BOSL2`, `libs/README.md` | New/Modified | Library pin + license note |
| `hardware/cad/smoke/main.scad` | New | Smoke part |
| `.github/workflows/cad.yml` | New | CI |
| `LICENSES/BSD-2-Clause.txt` | New | BOSL2 license |
| `docs/adr/0002-openscad-toolchain.md` | New | Decision record |
| `README.md`, `hardware/cad/README.md` | Modified | Usage docs |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Local 2021.01 differs from CI snapshot | High | Version warning; CI is canonical |
| Dated Docker tag removed | Med | Record digest; pin by digest if needed |
| `--hardwarnings` exit unreliable | Med | stderr scan |
| Submodule friction | Med | Clear make hint; CI `submodules: true` |
| BOSL2 beta API churn | Low | SHA pin |

## Rollback Plan

Revert the slice PRs in reverse order. Run `git submodule deinit libs/BOSL2`, then remove `.gitmodules` and the workflow. The Makefile goes back to its placeholders. The spec deltas are reverted with the PRs, before archive.

## Dependencies

- Docker (local fallback, CI), GitHub Actions on `JSisques/hexapod`

## Delivery Slices (chained PRs, ≤400 lines each)

1. BOSL2 submodule + BSD-2 license + `libs/README.md`
2. Makefile targets + smoke part + ADR-0002
3. CI workflow + README docs

## Success Criteria

- [ ] `make stl render` produces the smoke STL under `build/stl/` and PNG under `build/png/` locally (native or Docker)
- [ ] Any WARNING/ERROR fails the build
- [ ] Uninitialized submodule yields a clear failure hint
- [ ] PR CI run uploads STL+PNG artifacts
- [ ] `make firmware` (placeholder) still exits non-zero
