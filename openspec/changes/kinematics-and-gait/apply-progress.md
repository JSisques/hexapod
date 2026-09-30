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
