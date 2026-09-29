# CI Specification

## Purpose

Define the GitHub Actions workflow that builds CAD outputs canonically.

## Requirements

### Requirement: CAD workflow triggers

`.github/workflows/cad.yml` MUST run on every pull request and on pushes to `main`.

#### Scenario: PR triggers run

- GIVEN a pull request is opened
- WHEN GitHub evaluates workflows
- THEN the CAD workflow runs

### Requirement: Canonical build

The workflow MUST check out with submodules and run `make stl render`, `make gate-test` and `make check-fit` in the pinned Docker image, with `check-fit` as its own step after `gate-test`. Any warning, error or interference MUST fail the job.
(Previously: only `make stl render` ran; no gate-test or check-fit step.)

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
- THEN `gate-test` runs before `check-fit`, both in the pinned image
### Requirement: Artifacts

The workflow MUST upload STL and PNG outputs as artifacts with 14-day retention.

#### Scenario: Artifacts uploaded

- GIVEN a successful run
- WHEN the run page is viewed
- THEN artifacts contain `build/stl/smoke.stl` and `build/png/smoke.png`
- AND retention is 14 days

### Requirement: Least privilege

The workflow MUST declare `permissions: contents: read` and no broader scope.

#### Scenario: Permissions declared

- GIVEN `cad.yml`
- WHEN its permissions are read
- THEN only `contents: read` is granted
