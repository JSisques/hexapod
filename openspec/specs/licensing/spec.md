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
