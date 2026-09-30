# Software Tooling Specification

## Purpose

Define the Python project layout, quality gates, visualiser, report and decision record for `software/`.

## Requirements

### Requirement: Project layout and toolchain

`software/` MUST be a Python 3.12 project with a `src` layout, declaring numpy, and pytest, ruff, mypy and matplotlib as tooling. It MUST keep a `README.md`.

#### Scenario: Toolchain installs

- GIVEN a clean Python 3.12 environment
- WHEN the project is installed with dev dependencies
- THEN ruff, mypy and pytest run

### Requirement: Quality gate

`make software` MUST run ruff, mypy and pytest and exit non-zero if any fails. Type checking MUST cover the package sources.

#### Scenario: Failure propagates

- GIVEN a failing test
- WHEN `make software` runs
- THEN it exits non-zero

### Requirement: Headless visualiser

The system MUST render a pose or gait cycle to a PNG without a display, marking PROVISIONAL values.

#### Scenario: Render without display

- GIVEN no display server
- WHEN the visualiser runs
- THEN a non-empty PNG is written

### Requirement: Pose report

The system MUST produce a text report of limit and torque status for gait poses. It MUST show the PROVISIONAL flag and the known `tau_femur` alpha != 0 inconsistency. Its findings MUST NOT change the exit status.

#### Scenario: Report content

- GIVEN a report run
- WHEN it is read
- THEN it lists limit margins, torque values, PROVISIONAL items and the known-issue note

### Requirement: Decision record and SDD config

ADR-0005 MUST record the tooling choice, the params-sharing approach and the committed-generated-JSON exception. `openspec/config.yaml` MUST set `strict_tdd: true` and a `verify.test_command`.

#### Scenario: Config enabled

- GIVEN `openspec/config.yaml`
- WHEN read
- THEN `strict_tdd` is true and `verify.test_command` is non-empty
