# CAD

OpenSCAD parts and assemblies.

## Part convention

- Each part lives in its own directory: `hardware/cad/<part>/`, where `<part>` uses only `[a-z0-9-]`.
- The entry point is `hardware/cad/<part>/main.scad`. Other `.scad` files are helpers and are never built on their own.
- Use BOSL2 with `include <BOSL2/std.scad>`; `make` sets `OPENSCADPATH=libs`.

## Outputs

- `make stl` writes `build/stl/<part>.stl`.
- `make render` writes `build/png/<part>.png` (1024x768).
- `smoke/` is a minimal part that proves the toolchain works.

## Warnings gate

Any OpenSCAD `WARNING` or `ERROR` fails the build, locally and in CI. `make gate-test` proves the gate still fires. See [ADR-0002](../../docs/adr/0002-openscad-toolchain.md).

STL and PNG files are build outputs produced by `make` and CI. They are never committed.

License: CC-BY-SA-4.0 — see [LICENSES/CC-BY-SA-4.0.txt](../../LICENSES/CC-BY-SA-4.0.txt)
