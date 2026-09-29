# Delta for Repo Hygiene

## MODIFIED Requirements

### Requirement: Makefile entry point

A root `Makefile` MUST provide `help` as the default goal, listing all targets. `stl`, `render`, and `clean` MUST be real targets (see `cad-build`). The remaining targets (`firmware`, `software`, `docs`) MUST be placeholders that print "not implemented" and exit with a non-zero status.
(Previously: all targets other than `help` were placeholders.)

#### Scenario: Default goal lists targets

- GIVEN the repo root
- WHEN `make` runs with no arguments
- THEN it exits 0 and prints the available targets

#### Scenario: Placeholder target

- GIVEN a placeholder target such as `firmware`
- WHEN `make firmware` runs
- THEN the output contains "not implemented" and the exit code is non-zero (the recipe exits 1; make itself reports 2)

#### Scenario: CAD targets are real

- GIVEN the repo root
- WHEN `make clean` runs
- THEN it exits 0 and does not print "not implemented"
