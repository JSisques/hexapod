# CAD Build Specification

## Purpose

Define the reproducible OpenSCAD build: entry points, make targets, toolchain selection, library path, warnings gate, and output layout.

## Requirements

### Requirement: Entry points and outputs

Only `hardware/cad/<part>/main.scad` files MUST be built. `make stl` MUST write `build/stl/<part>.stl`; `make render` MUST write `build/png/<part>.png` at 1024x768 using `--autocenter --viewall --render`.

#### Scenario: Smoke part built

- GIVEN `hardware/cad/smoke/main.scad` exists
- WHEN `make stl render` runs
- THEN `build/stl/smoke.stl` and `build/png/smoke.png` exist and are non-empty

#### Scenario: Non-entry files ignored

- GIVEN a `.scad` file not named `main.scad`
- WHEN `make stl` runs
- THEN no output is produced for that file

### Requirement: Toolchain selection

The Makefile MUST use a local `openscad` binary when present, otherwise the Docker image pinned by dated tag. It SHOULD warn when the local binary lacks Manifold. It MUST pass `--backend` only when the binary supports it.

#### Scenario: Docker fallback

- GIVEN no `openscad` on PATH and Docker available
- WHEN `make stl` runs
- THEN the build runs in the pinned image

#### Scenario: Old local binary

- GIVEN a local OpenSCAD without `--backend`
- WHEN `make stl` runs
- THEN `--backend` is not passed and a version warning is printed

### Requirement: Library path and submodule guard

The Makefile MUST export `OPENSCADPATH=libs`. If `libs/BOSL2/std.scad` is missing, it MUST fail non-zero with a hint naming `git submodule update --init`.

#### Scenario: Uninitialized submodule

- GIVEN `libs/BOSL2` is empty
- WHEN `make stl` runs
- THEN it exits non-zero and the output contains the hint

### Requirement: Warnings gate

Builds MUST pass `--hardwarnings` and MUST scan OpenSCAD stderr for `WARNING|ERROR`; any match MUST fail the build, locally and in CI.

#### Scenario: Warning fails build

- GIVEN a part that emits a WARNING
- WHEN `make stl` runs
- THEN the exit code is non-zero, even if OpenSCAD exits 0

### Requirement: Dependency tracking

Builds MUST emit `-d` dependency files so editing an included file rebuilds dependent outputs.

#### Scenario: Included file changes

- GIVEN a built part and an unchanged `main.scad`
- WHEN an included file is touched and `make stl` runs
- THEN the STL is rebuilt

### Requirement: Clean

`make clean` MUST remove `build/` and exit 0, including when it is absent.

#### Scenario: Clean twice

- GIVEN `build/` exists
- WHEN `make clean` runs twice
- THEN both runs exit 0 and `build/` is absent
