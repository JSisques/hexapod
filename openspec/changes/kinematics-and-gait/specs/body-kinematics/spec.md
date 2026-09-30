# Body Kinematics Specification

## Purpose

Convert a body pose and world foot positions into per-leg targets on a PROVISIONAL hexagonal layout.

## Requirements

### Requirement: Provisional layout

The layout MUST have six legs with mount radius 80 mm, mount angles 30° + k·60° (k = 0..5), stance height 60 mm (foot plane below the coxa frame) and neutral reach 100 mm from the coxa axis. Every layout value MUST be flagged PROVISIONAL in any output that shows it.

#### Scenario: Mount positions

- GIVEN the default layout
- WHEN mount points are listed
- THEN six points lie at radius 80 mm at 30°, 90°, 150°, 210°, 270°, 330°

### Requirement: Body pose to leg targets

Given a body pose (position and roll, pitch, yaw) and world foot points, the system MUST return each foot point in its own leg frame, with the leg frame rotated by the mount angle.

#### Scenario: Neutral pose

- GIVEN the identity body pose and neutral feet
- WHEN targets are computed
- THEN every leg target is identical (100 mm reach, 60 mm below the coxa frame)

#### Scenario: Body translation

- GIVEN feet fixed in the world and the body translated 10 mm in X
- WHEN targets are computed
- THEN each leg target shifts by the opposite displacement expressed in that leg frame

### Requirement: Reachability report

The system MUST report per leg whether its target is reachable and within joint limits.

#### Scenario: Infeasible pose

- GIVEN a body height that puts a foot beyond reach
- WHEN the report runs
- THEN that leg is flagged unreachable and the others are evaluated independently
