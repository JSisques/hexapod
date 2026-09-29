# hexapod

A six-legged walking robot (18 servos, 3 DOF per leg), designed as code: parametric 3D models in OpenSCAD, plus firmware, software and documentation, all in one repository.

> Status: repository scaffolding. No CAD, firmware or software yet.

## Repository map

| Path | Purpose |
| --- | --- |
| `hardware/cad/` | OpenSCAD parametric parts and assemblies |
| `hardware/electronics/` | Schematics and PCB |
| `hardware/bom/` | Bill of materials |
| `firmware/` | Microcontroller firmware |
| `software/` | Hosted software: gait, inverse kinematics, teleoperation |
| `docs/` | Architecture, build guide and [ADRs](docs/adr/README.md) |
| `tools/` | Development and build scripts |
| `libs/` | Third-party libraries (e.g. BOSL2, planned) |
| `build/` | Generated outputs (gitignored) |

Generated STL and PNG files are build outputs: they are never committed and will be produced by CI.

## Quick start

```sh
make help
```

Targets other than `help` are placeholders for now and exit non-zero.

## Licenses

The repository is split-licensed. Full texts live in [`LICENSES/`](LICENSES/).

| Path | License |
| --- | --- |
| `hardware/`, `docs/` | [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt) |
| `firmware/`, `software/`, `tools/`, root build files | [MIT](LICENSES/MIT.txt) |
| `libs/BOSL2` | [BSD-2-Clause](LICENSES/BSD-2-Clause.txt) |
| `libs/` (other) | Each library keeps its own upstream license |

## Decisions

See [ADR-0001](docs/adr/0001-repository-layout-and-licensing.md) for the layout, STL policy and license split.
