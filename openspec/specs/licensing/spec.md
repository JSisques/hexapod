# Licensing Specification

## Purpose

Define split licensing: CC-BY-SA-4.0 for hardware, MIT for firmware and software.

## Requirements

### Requirement: License texts

`LICENSES/` MUST contain the full, unmodified text of CC-BY-SA-4.0 and MIT, in `LICENSES/CC-BY-SA-4.0.txt` and `LICENSES/MIT.txt`.

#### Scenario: Both texts present

- GIVEN the `LICENSES/` directory
- WHEN its files are listed
- THEN both files exist and are non-empty
- AND the MIT file names a copyright holder and year

### Requirement: License table in README

The root `README.md` MUST include a table mapping each domain to its license: `hardware/` and `docs/` to CC-BY-SA-4.0; `firmware/`, `software/`, and `tools/` to MIT.

#### Scenario: Table complete

- GIVEN the root `README.md`
- WHEN the license table is read
- THEN every top-level domain directory has exactly one license entry

### Requirement: Per-directory license note

The `README.md` of each licensed directory MUST state its governing license by SPDX identifier.

#### Scenario: Note matches table

- GIVEN `hardware/README.md` and `firmware/README.md`
- WHEN each is read
- THEN they state `CC-BY-SA-4.0` and `MIT` respectively
- AND each matches the root table
### Requirement: Third-party library licenses

Third-party code under `libs/*` MUST keep its upstream license. For BOSL2 (BSD-2-Clause), the full text MUST exist at `LICENSES/BSD-2-Clause.txt`, and `libs/README.md` MUST note that `libs/BOSL2` is BSD-2-Clause and not covered by the repo's own licenses.

#### Scenario: BOSL2 license present

- GIVEN the tree after the change
- WHEN `LICENSES/BSD-2-Clause.txt` is read
- THEN it exists, is non-empty, and contains the BSD 2-Clause text

#### Scenario: Library note

- GIVEN `libs/README.md`
- WHEN it is read
- THEN it states `BSD-2-Clause` for `libs/BOSL2`
