# Exploration: hexapod-repo-bootstrap

## Current State
- Repo contains README.md (one line), openspec/ (config, specs, archive), .atl/. One commit on master.
- No architecture, license, .gitignore, tooling, or CI. Greenfield.

## Layout Approaches
1. **A: Hardware/Software split** — `hardware/{cad,electronics,bom}`, `software/{firmware,control,sim}`, `docs/`. Familiar, but "software" mixes MCU firmware and hosted code (different toolchains). Effort: Low.
2. **B: Top-level per-domain (recommended)** — `hardware/cad`, `hardware/electronics`, `hardware/bom`, `firmware/`, `software/`, `docs/`, `tools/`, `libs/`. One toolchain and one CI job per domain, shallow paths, screaming. Cons: cross-domain refs need a shared params file. Effort: Low.
3. **C: Per-subsystem (leg/body/head)** — poor fit: six identical legs, cross-cutting firmware/software, duplication risk. Effort: Medium-High.

Suggested skeleton for B:
```
hardware/cad/{parts/,assemblies/,lib/params.scad,lib/util.scad}
hardware/electronics/   hardware/bom/bom.csv
firmware/   software/   docs/{architecture,build-guide,adr}/
libs/BOSL2 (submodule)   tools/   build/ (gitignored)
```

## OpenSCAD Conventions
- BOSL2 pinned as git submodule under `libs/`, `OPENSCADPATH` set in Makefile/CI.
- One `params.scad` for global dimensions; one part per file; assemblies use `use <...>`; ghost models of servos/boards for fit checks, excluded from export.
- STL not committed: built in CI, attached to releases/artifacts. No Git LFS needed. PNG renders likewise; only a small hero image in docs/.
- No dominant formatter: use `.editorconfig` plus a CI gate "renders without warnings".
- CI: GitHub Actions running `make stl` in an OpenSCAD Docker image (avoids third-party action lock-in).

## Tooling and Hygiene
- `.gitignore`, `.editorconfig`, `.gitattributes` (only if LFS/line endings), root `Makefile` as single entry point.
- Licensing: hardware CC-BY-SA 4.0 or CERN-OHL; firmware/software MIT or Apache-2.0; `LICENSES/` folder plus README table.
- ADRs under `docs/adr/`; conventional commits.

## Firmware/Software Stack (open)
- 18 servos (6 legs x 3 DOF): PCA9685 x2, dedicated controller, or MCU PWM.
- MCU: ESP32, RP2040/RP2350, Raspberry Pi, or Pi + MCU split.
- Languages: C++/PlatformIO, MicroPython, Rust; Python or ROS 2 for hosted.

## Recommendation
Option B, BOSL2 submodule, per-part parametric SCAD with shared `params.scad`, Makefile as sole interface, CI-built STL/PNG (no LFS), split licensing, ADR trail. Phases: (1) scaffolding; (2) OpenSCAD toolchain (Makefile, BOSL2, sample part, CI); (3) empty firmware/software stubs pending stack decisions.

## Product Decisions Needed
1. Layout: B / A / C
2. STL policy: CI artifacts / commit / Git LFS
3. BOSL2: submodule / vendored / none
4. Licensing: hardware CC-BY-SA 4.0 or CERN-OHL; software MIT or Apache-2.0; or single license
5. MCU/compute (deferrable)
6. Servo model and driver (deferrable; drives mechanical params)
7. Firmware/software languages (deferrable)
8. Scope: scaffolding only vs. also sample part + CI
9. Electronics tooling: KiCad / other
10. Hosting/CI: GitHub Actions? Public or private?

## Risks
- Servo/MCU choice drives OpenSCAD parameters: keep in one `params.scad`, defer stack.
- Submodule friction and long OpenSCAD render times (consider Manifold backend).
- Mixed-license mistakes; no OpenSCAD formatter (style drift); committing STL later bloats history.

## Ready for Proposal
Yes, once decisions 1-4 and 8 are answered; 5-7 can be deferred.
