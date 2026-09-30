# Leg Kinematics Specification

## Purpose

Offset-aware forward and inverse kinematics for one leg in CAD frames, with joint limits.

## Requirements

### Requirement: Conventions

Angles MUST be degrees named `theta` (coxa yaw about Z), `alpha` (femur pitch, knee-up positive) and `phi` (knee angle relative to the femur; tibia angle from vertical = `phi + alpha`). The leg frame MUST have the coxa axis as Z at the origin. Kinematics MUST be pure functions reading only the loaded snapshot.

#### Scenario: Zero pose

- GIVEN `theta = alpha = phi = 0`
- WHEN forward kinematics runs
- THEN the result is deterministic and lies in the plane offset by the lateral foot offset from the femur plane

### Requirement: Forward kinematics

FK MUST return the tip-sphere centre (86 mm from the knee, lateral offset -1.3 mm) in the leg frame for `(theta, alpha, phi)`.

#### Scenario: Offset applied

- GIVEN any pose
- WHEN FK runs
- THEN the foot point includes the -1.3 mm lateral component rather than an ideal planar result

### Requirement: Inverse kinematics

IK MUST map a leg-frame foot point to `(theta, alpha, phi)` in the elbow configuration matching the CAD sign convention, compensating the lateral offset. For an unreachable point IK MUST return an explicit failure result and MUST NOT return NaN or raise silently.

#### Scenario: Round trip on the grid

- GIVEN the 12 poses of `fit_alpha` x `fit_phi` at `theta = 0`
- WHEN IK(FK(q)) runs
- THEN each result equals q within 1e-6 degrees

#### Scenario: Unreachable target

- GIVEN a point farther than the maximum reach
- WHEN IK runs
- THEN a failure result is returned

### Requirement: Joint limits

Hard limits MUST be the `fit_alpha` and `fit_phi` envelope (min to max) and, PROVISIONALLY, `theta` within ±45°. The system MUST verify that the envelope lies inside the servo `range_deg`. A limit check MUST report which joint violates and by how much.

#### Scenario: Within limits

- GIVEN `alpha = 30`, `phi = 45`, `theta = 0`
- WHEN limits are checked
- THEN no violation is reported

#### Scenario: Violation reported

- GIVEN `phi = 60`
- WHEN limits are checked
- THEN a `phi` violation of 15 degrees is reported

#### Scenario: Servo inclusion

- GIVEN a servo `range_deg` narrower than the envelope
- WHEN the inclusion check runs
- THEN it fails naming the joint
