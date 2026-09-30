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

## Report and plots

```sh
make software-report      # writes build/software/{tripod,wave,ripple}.png and report.md
python -m hexapod report --out DIR   # or `plot`, from an environment with the package installed
```

Plots are rendered headless (matplotlib Agg). Every plot title and the report banner
show `PROVISIONAL` while the servo profile or the body layout is unmeasured. The report
lists joint-limit margins and torque rows per gait. Limit violations and torque warnings
are findings in the report and never change the exit status (0 on completion, 1 when the
parameter snapshot cannot be loaded, 2 for bad usage). CI uploads the PNGs and the report
as the `software-report` artifact, kept for 14 days.

Known issue: the torque rows reuse the CAD `tau_femur` formula as-is, which is only
consistent at alpha = 0. The report states this caveat; do not read the femur rows as
verified margins for other alpha values.

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
