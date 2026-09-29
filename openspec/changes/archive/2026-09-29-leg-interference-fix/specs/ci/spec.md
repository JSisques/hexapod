# Delta for CI

## MODIFIED Requirements

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
