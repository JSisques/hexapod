# Delta for CI

## MODIFIED Requirements

### Requirement: Canonical build

The workflow MUST check out with submodules and run `make stl render`, `make gate-test`, `make check-fit` and the params drift check in the pinned Docker image, with `check-fit` as its own step after `gate-test` and the drift check as its own step after `check-fit`. Any warning, error, interference or snapshot drift MUST fail the job.
(Previously: no drift-check step; the job failed only on warning, error or interference.)

#### Scenario: Warning fails CI

- GIVEN a part emitting a WARNING
- WHEN the workflow runs
- THEN the job fails

#### Scenario: Interference fails CI

- GIVEN an assembly with overlap above the tolerance
- WHEN the workflow runs
- THEN the `check-fit` step fails and the job fails

#### Scenario: Step order

- GIVEN `cad.yml`
- WHEN its steps are read
- THEN `gate-test` runs before `check-fit`, and the drift check runs after `check-fit`, all in the pinned image

#### Scenario: Snapshot drift fails CI

- GIVEN a CAD parameter changed without regenerating the snapshot
- WHEN the workflow runs
- THEN the drift-check step fails and the job fails

## ADDED Requirements

### Requirement: Software workflow

`.github/workflows/software.yml` MUST run on every pull request and on pushes to `main`, without path filters, so a required status is never left pending. It MUST set up Python 3.12, run `make software`, and declare only `permissions: contents: read`.

#### Scenario: PR triggers run

- GIVEN a pull request touching only CAD files
- WHEN GitHub evaluates workflows
- THEN the software workflow still runs and reports a status

#### Scenario: Failing test fails CI

- GIVEN a failing pytest, ruff or mypy check
- WHEN the workflow runs
- THEN the job fails

### Requirement: Software artifacts

The software workflow MUST upload the visualiser PNG and the pose report as artifacts with 14-day retention.

#### Scenario: Artifacts uploaded

- GIVEN a successful run
- WHEN the run page is viewed
- THEN the visualiser PNG and the report are attached
- AND retention is 14 days
