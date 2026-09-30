# Params Bridge Specification

## Purpose

Share CAD leg parameters with software without manual copying: OpenSCAD evaluates the assembly, a committed JSON snapshot records the result, and CI gates drift.

## Requirements

### Requirement: Parameter export

The system MUST provide an exporter that evaluates `hardware/cad/asm-leg/asm-leg.scad` with OpenSCAD and writes a JSON document containing: `coxa_l`, `femur_l`, `tibia_l`, the femur-axis offset (x = `coxa_l`, y = `leg_lane_dy`, z = `cb_zmid`), the foot tip-centre distance from the knee (86 mm), the lateral foot offset (-1.3 mm), `fit_alpha`, `fit_phi`, servo `range_deg`, `stall_kgcm`, `mass_kg`, and a `provisional` list naming provisional values. Output MUST be deterministic (stable key order, fixed number formatting).

#### Scenario: Export is reproducible

- GIVEN unchanged CAD sources
- WHEN the exporter runs twice
- THEN both outputs are byte-identical

#### Scenario: Derived values present

- GIVEN the exporter output
- WHEN it is read
- THEN `coxa_l`, the 86 mm foot distance and the -1.3 mm offset are present as numbers

### Requirement: Committed snapshot

The repository MUST track the exported JSON as a snapshot. The snapshot MUST be the only source of CAD numbers for software code; software MUST NOT hard-code them.

#### Scenario: Software reads the snapshot only

- GIVEN the software sources
- WHEN searched for the literals 86, -1.3 and the fit envelopes
- THEN none appear outside tests and the loader reads them from the snapshot

### Requirement: Drift gate

A make target MUST regenerate the snapshot in the pinned OpenSCAD image and fail with a non-zero status when the result differs from the committed file. `cad.yml` MUST run it as a step.

#### Scenario: Stale snapshot fails

- GIVEN a CAD parameter changed and the snapshot not regenerated
- WHEN the drift gate runs
- THEN it exits non-zero and reports the differing file

#### Scenario: Fresh snapshot passes

- GIVEN a snapshot regenerated after the CAD change
- WHEN the drift gate runs
- THEN it exits 0

### Requirement: Loader

The software MUST provide a loader returning typed, immutable parameters from the snapshot. The loader MUST raise a clear error for a missing file, missing key or non-numeric value, and MUST expose the provisional list.

#### Scenario: Valid load

- GIVEN the committed snapshot
- WHEN the loader runs
- THEN it returns parameters and the provisional list

#### Scenario: Missing key

- GIVEN a snapshot lacking `fit_phi`
- WHEN the loader runs
- THEN it raises an error naming `fit_phi`
