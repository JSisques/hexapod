# Apply Progress: kinematics-and-gait

Mode: Strict TDD. Chain: feature-branch-chain (tracker `feat/kinematics-and-gait`; PR 1 on `feat/kinematics-1-scaffold`).

## PR 1: Scaffold - COMPLETE (8/8)

- [x] 1.1 RED `software/tests/test_smoke.py`
- [x] 1.2 `software/pyproject.toml`, `software/src/hexapod/__init__.py` (+ `py.typed`)
- [x] 1.3 `make software` in `Makefile`
- [x] 1.4 `.editorconfig` `[*.py]`, `.gitignore` Python entries
- [x] 1.5 `.github/workflows/software.yml` (no path filters)
- [x] 1.6 `software/README.md`
- [x] 1.7 ADR-0005 and index
- [x] 1.8 `openspec/config.yaml`

## TDD Cycle Evidence

| Task | RED | GREEN | Triangulation | REFACTOR |
|------|-----|-------|---------------|----------|
| 1.1/1.2 | `pytest software/tests`: 1 collection error, `ModuleNotFoundError: hexapod` | `make software`: 2 passed | 2 tests (import, non-empty `__version__`) | None needed |
| 1.3-1.8 | N/A (config, CI, docs) | `make software` exit 0 | Skipped: purely structural | None |

## Work Unit Evidence

| Evidence | Value |
|---|---|
| Focused test | `make software PYTHON=python3` (python 3.14.7): ruff check pass, format check pass, mypy strict no issues (2 files), pytest 2 passed |
| Runtime harness | CI `software.yml` run (only observable on the PR); locally `make firmware` still prints "not implemented" and exits non-zero |
| Rollback boundary | Revert PR 1: `software/{pyproject.toml,src,tests,README.md}`, `software.yml`, ADR-0005 + index row, Makefile `software` target, `.editorconfig`/`.gitignore`/`openspec/config.yaml` edits |

## Deviations / Notes

- Python 3.12 is not installed locally (only 3.14.7); verified with `PYTHON=python3`. `requires-python = ">=3.12"`; CI pins 3.12. `brew install python@3.12` was attempted but did not finish.
- Makefile `PYTHON ?= python3.12` variable added; venv target `software/.venv/.installed` depends on `pyproject.toml`.
- `.gitignore` also ignores `*.egg-info/`.
- Size: ~280 authored lines, within the 400 budget.

## PR 2: Params bridge - COMPLETE (8/8)

Branch `feat/kinematics-2-params-bridge` (stacked on `feat/kinematics-1-scaffold`).

- [x] 2.1 RED `software/tests/test_echo_to_json.py` (12 tests)
- [x] 2.2 RED `software/tests/test_params.py` (8 tests)
- [x] 2.3 `tools/cad/echo-to-json.py` (stdlib; `convert()` + CLI)
- [x] 2.4 `tools/cad/export-params.scad` (params echo + 12 `fk_golden` poses)
- [x] 2.5 `make params`, `make check-params` (`diff -u`, "params snapshot drift"); `PARAMS_DEFS` and `PY3` variables
- [x] 2.6 `software/src/hexapod/data/leg-params.json` (generated in the pinned Docker image) and `software/src/hexapod/params.py`
- [x] 2.7 `gate-test` line: `check-params PARAMS_DEFS='-D k_dyn=1.6'` must fail with "params snapshot drift"
- [x] 2.8 `Params drift` step after `Fit check` in `.github/workflows/cad.yml`

### TDD Cycle Evidence (PR 2)

| Task | RED | GREEN | Triangulation | REFACTOR |
|------|-----|-------|---------------|----------|
| 2.1/2.3 | `pytest software/tests`: collection error `FileNotFoundError` (script absent) | 12 passed | 0/2 lines, undef/nan/inf/-inf, in-string token allowed, duplicate key, byte determinism, numeric pair lists stay lists | None needed |
| 2.2/2.6 | collection error `ModuleNotFoundError: hexapod.params` | 8 passed (`make software`: 22 passed) | version, missing `fit_phi`, unknown keys, provisional OR, string and bool non-numeric, missing file | Split long line (ruff E501); import order fixed by ruff |
| 2.4/2.5/2.7/2.8 | N/A (CAD, make, CI) | `make check-params` OK; `make gate-test` shows "params drift OK" | Drift fires with `-D k_dyn=1.6`, passes without it | None |

### Work Unit Evidence (PR 2)

| Evidence | Value |
|---|---|
| Focused test | `make software PYTHON=python3`: ruff pass, format pass, mypy strict 5 files no issues, pytest 22 passed |
| Runtime harness | `TOOLCHAIN=docker make check-params`: OK; `TOOLCHAIN=docker make gate-test`: all 5 gates OK incl. "params drift" (8.3 s) |
| Rollback boundary | Revert PR 2: `tools/cad/{echo-to-json.py,export-params.scad}`, `software/src/hexapod/{params.py,data/}`, the two new test files, Makefile params/check-params/gate-test additions, cad.yml drift step |

### Deviations / Notes (PR 2)

- Snapshot `provisional` is a list of names (`["servo"]`) per the params-bridge spec, plus `servo.provisional` bool; `Params.provisional` is their OR (BodyLayout joins the OR in PR 4). Design text said "servo flag".
- Local OpenSCAD 2026.09.29 and the pinned image (2026.01.19) produce a byte-identical snapshot; the committed file comes from the Docker image. OpenSCAD echo prints 6 significant digits.
- Size: ~490 authored lines (over the 400 budget; generated 150-line JSON excluded). Loader with typed validation is the largest part (186 lines); recommend `size:exception` for this PR.

## PR 3: Leg kinematics - COMPLETE (6/6)

Branch `feat/kinematics-3-leg-kinematics` (stacked on `feat/kinematics-2b-params-loader`).

- [x] 3.1 RED `software/tests/test_leg.py` (35 tests: 12 golden FK, 12 grid round-trips, zero pose, offset, theta round-trip and wrap, 3 unreachable reasons)
- [x] 3.2 RED `software/tests/test_limits.py` (7 tests, incl. servo inclusion naming the joint)
- [x] 3.3 RED placeholder feasibility (in `test_limits.py`)
- [x] 3.4 `software/src/hexapod/leg.py` (`fk`, `ik`, `JointAngles`, `Reason`, `UnreachableError`), `limits.py`
- [x] 3.5 `docs/adr/0006-leg-frames-and-joint-conventions.md` and index row
- [x] 3.6 Refactor; `rg` shows no CAD literals in `leg.py`/`limits.py` (only the PROVISIONAL `THETA_LIMIT = 45`)

### TDD Cycle Evidence (PR 3)

| Task | RED | GREEN | Triangulation | REFACTOR |
|------|-----|-------|---------------|----------|
| 3.1-3.4 | `pytest software/tests`: 2 collection errors (`hexapod.leg`/`hexapod.limits` missing) | `make software PYTHON=python3`: 64 passed | 12 CAD poses, 5 theta values, wrap 190 -> -170, 3 reasons | Split long line (E501); mypy `approx` comparison fixed in test |
| 3.5 | N/A (docs) | ADR indexed | N/A | None |

### Work Unit Evidence (PR 3)

| Evidence | Value |
|---|---|
| Focused test | `make software PYTHON=python3`: ruff pass, format pass, mypy strict 9 files no issues, pytest 64 passed |
| Runtime harness | N/A (pure maths) |
| Rollback boundary | Revert PR 3: `leg.py`, `limits.py`, `test_leg.py`, `test_limits.py`, ADR-0006 + index row |

### Deviations / Notes (PR 3)

- Design `servo_range_ok(lim, range_deg) -> bool` became `servo_range_failures(...) -> list[Violation]` so the failure names the joint (spec); empty list means OK.
- Actual neutral IK for (100, -1.3, -52): theta 0, alpha 9.876 deg, phi 0.721 deg.
- No `docs/architecture` page added (not required by tasks; ADR-0006 holds the conventions).
- Size: ~245 authored lines (ADR 36, src 109, tests 99, index 1), within budget.
