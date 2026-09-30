# Software

Python tooling for the hexapod: leg and body kinematics, gait generation and
reports. It is a pure-Python package (`hexapod`, `src` layout) that reads the
leg parameters exported from the OpenSCAD model.

## Requirements

- Python 3.12 (`python3.12` on `PATH`, or `make software PYTHON=<interpreter>`)
- No other tooling: `make software` creates `software/.venv` and installs the
  pinned dev dependencies (pytest, ruff, mypy, matplotlib) itself.

## Quality gate

From the repository root:

```sh
make software
```

This runs `ruff check`, `ruff format --check`, `mypy --strict` and `pytest`,
and exits non-zero if any of them fails.

## Layout

```
software/
  pyproject.toml     project metadata, pinned dev dependencies, tool config
  src/hexapod/       package sources
  tests/             pytest suite (tests are written before the code)
```

Decisions are recorded in
[ADR-0005](../docs/adr/0005-software-tooling-and-parameter-bridge.md).

License: MIT — see [LICENSES/MIT.txt](../LICENSES/MIT.txt)
