# hexapod

A six-legged walking robot (18 servos, 3 DOF per leg), designed as code: parametric 3D models in OpenSCAD, plus firmware, software and documentation, all in one repository.

> Status: the OpenSCAD toolchain is in place (Makefile build, BOSL2, CI). The first leg module (tier XS, provisional MG996R profile, four printable parts and an assembly preview) is modelled but not yet printed. No firmware or software yet.

## Repository map

| Path | Purpose |
| --- | --- |
| `hardware/cad/` | OpenSCAD parametric parts and assemblies (leg module, see its [README](hardware/cad/README.md)) |
| `hardware/electronics/` | Schematics and PCB |
| `hardware/bom/` | Bill of materials |
| `firmware/` | Microcontroller firmware |
| `software/` | Hosted software: gait, inverse kinematics, teleoperation |
| `docs/` | Architecture, build guide and [ADRs](docs/adr/README.md) |
| `tools/` | Development and build scripts |
| `libs/` | Third-party libraries (BOSL2, as a git submodule) |
| `build/` | Generated outputs (gitignored) |

Generated STL and PNG files are build outputs: they are never committed; CI builds them and uploads them as artifacts.

## Quick start

Clone with submodules (BOSL2 lives in `libs/BOSL2`):

```sh
git clone --recurse-submodules https://github.com/JSisques/hexapod.git
# already cloned without submodules:
git submodule update --init
```

Prerequisites: `make`, plus either a local OpenSCAD snapshot (with the Manifold backend) or Docker. With `TOOLCHAIN=auto` (default) a local `openscad` is used when found, otherwise the pinned Docker image. CI always uses the Docker image, so `TOOLCHAIN=docker` reproduces CI locally.

```sh
make help     # list targets
make doctor   # show the selected toolchain, version and submodule state
make stl      # export STL models to build/stl
make render   # render PNG previews to build/png
```

Any OpenSCAD warning or error fails the build. `make gate-test` proves the gate still fires.

The `firmware`, `software` and `docs` targets are placeholders for now and exit non-zero.

## Licenses

The repository is split-licensed. Full texts live in [`LICENSES/`](LICENSES/).

| Path | License |
| --- | --- |
| `hardware/`, `docs/` | [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt) |
| `firmware/`, `software/`, `tools/`, root build files | [MIT](LICENSES/MIT.txt) |
| `libs/BOSL2` | [BSD-2-Clause](LICENSES/BSD-2-Clause.txt) |
| `libs/` (other) | Each library keeps its own upstream license |

## Decisions

- [ADR-0001](docs/adr/0001-repository-layout-and-licensing.md): layout, STL policy and license split.
- [ADR-0002](docs/adr/0002-openscad-toolchain.md): OpenSCAD toolchain, pinned image, BOSL2, warnings gate and CI.
- [ADR-0003](docs/adr/0003-leg-servo-abstraction-and-tiers.md): servo profile abstraction, size tiers, torque gate and `asm-*` previews.
