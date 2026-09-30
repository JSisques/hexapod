# Gait Engine Specification

## Purpose

One phase-based engine producing tripod, wave and ripple gaits as parameter sets, with a static stability margin.

## Requirements

### Requirement: Phase engine

The engine MUST take a gait parameter set (per-leg phase offset, duty factor, step length, lift height, cycle time) and a global phase in [0, 1), and return each foot's world position and stance/swing state. There MUST be a single engine implementation; gaits differ only by parameters.

#### Scenario: Periodicity

- GIVEN any gait
- WHEN evaluated at phase 0 and phase 1
- THEN the outputs are equal

#### Scenario: Stance foot fixed

- GIVEN a leg in stance
- WHEN phase advances within stance
- THEN its world foot position is unchanged

### Requirement: Gait definitions

The system MUST provide tripod (duty 1/2, two alternating triples), wave (duty 5/6, one leg swinging at a time) and ripple (duty 2/3, legs offset in sequence) parameter sets.

#### Scenario: Support count

- GIVEN each gait sampled across a cycle
- WHEN grounded legs are counted
- THEN tripod always has at least 3, wave at least 5, ripple at least 4

### Requirement: Stability margin

The system MUST compute the static stability margin as the minimum distance from the body centre projection to the edges of the support polygon (convex hull of grounded feet), positive when inside.

#### Scenario: Positive margin

- GIVEN tripod, wave and ripple with default parameters
- WHEN sampled across a cycle
- THEN the margin is positive at every sample

#### Scenario: Unsupported

- GIVEN fewer than three grounded feet
- WHEN the margin is computed
- THEN the result is not positive and the state is flagged unsupported

### Requirement: Limit compliance

Default gait cycles on the provisional layout MUST cause no joint-limit violation. For altered parameters the engine MUST report violations as data rather than raising.

#### Scenario: Default cycles feasible

- GIVEN default tripod, wave and ripple
- WHEN every sample is solved through body and leg kinematics
- THEN all targets are reachable and within limits

#### Scenario: Excess step length

- GIVEN a step length beyond the workspace
- WHEN the cycle is evaluated
- THEN violations are listed by leg, phase and joint

### Requirement: Torque informational

Torque on gait poses MUST be reported for information only and MUST NOT fail a check.

#### Scenario: Torque above stall

- GIVEN a pose whose torque exceeds servo stall
- WHEN the report runs
- THEN it is listed as a warning and the exit status stays 0
