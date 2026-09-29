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

The workflow MUST check out with submodules and run `make stl render` in the pinned Docker image. Any warning or error MUST fail the job.

#### Scenario: Warning fails CI

- GIVEN a part emitting a WARNING
- WHEN the workflow runs
- THEN the job fails

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
