import math

import numpy as np
import pytest

from hexapod.body import (
    BodyLayout,
    BodyPose,
    UnsupportedStanceError,
    is_provisional,
    leg_reports,
    leg_targets,
    mount_points,
    neutral_feet,
    verify_stance,
)
from hexapod.leg import fk
from hexapod.limits import JointLimits
from hexapod.params import load_params

P = load_params()
LIM = JointLimits.from_params(P.limits)
L = BodyLayout()
FEET = neutral_feet(L, P.leg)
NEUTRAL = L.neutral_pose()
# Neutral foot-sphere centre in every leg frame: reach, lateral offset, stance height - ft_r.
EXPECTED = np.array([100.0, P.leg.foot_dy, -(60.0 - P.leg.ft_r)])


def _rz(deg: float) -> np.ndarray:
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def test_mount_points_at_80_mm_and_30_plus_60k() -> None:
    pts = mount_points(L)
    assert pts.shape == (6, 3)
    assert np.allclose(np.hypot(pts[:, 0], pts[:, 1]), 80)
    angles = np.degrees(np.arctan2(pts[:, 1], pts[:, 0])) % 360
    assert np.allclose(angles, [30, 90, 150, 210, 270, 330])
    assert np.allclose(pts[:, 2], 0)


def test_neutral_feet_lie_on_the_ground() -> None:
    assert np.allclose(FEET[:, 2], 0)


def test_identity_pose_gives_identical_targets() -> None:
    targets = leg_targets(NEUTRAL, FEET, L, P.leg)
    assert targets.shape == (6, 3)
    assert np.allclose(targets, EXPECTED)


def test_x_translation_shifts_targets_oppositely_in_each_leg_frame() -> None:
    pose = BodyPose(x=10, y=0, z=NEUTRAL.z, roll=0, pitch=0, yaw=0)
    shift = leg_targets(pose, FEET, L, P.leg) - EXPECTED
    for k, psi in enumerate(L.mount_angles):
        assert np.allclose(shift[k], _rz(-psi) @ [-10, 0, 0])


def test_yaw_round_trips_through_the_world_frame() -> None:
    pose = BodyPose(x=0, y=0, z=NEUTRAL.z, roll=0, pitch=0, yaw=15)
    targets = leg_targets(pose, FEET, L, P.leg)
    for k, psi in enumerate(L.mount_angles):
        world = _rz(15) @ (_rz(psi) @ targets[k] + mount_points(L)[k]) + [0, 0, NEUTRAL.z]
        assert np.allclose(world, FEET[k] + [0, 0, P.leg.ft_r])


def test_pitch_and_roll_change_targets_without_touching_the_ground_plane() -> None:
    pose = BodyPose(x=0, y=0, z=NEUTRAL.z, roll=5, pitch=-4, yaw=0)
    targets = leg_targets(pose, FEET, L, P.leg)
    assert not np.allclose(targets, EXPECTED)
    assert len({round(float(t[2]), 6) for t in targets}) > 1


def test_all_six_legs_reach_neutral_stance_within_limits() -> None:
    reports = leg_reports(NEUTRAL, FEET, L, P, LIM)
    assert len(reports) == 6
    for r in reports:
        assert r.reachable and r.q is not None and r.violations == []
        assert r.q.theta == pytest.approx(0, abs=1e-9)
        assert np.allclose(fk(r.q, P.leg), EXPECTED)


def test_infeasible_leg_is_flagged_and_others_stay_independent() -> None:
    feet = FEET.copy()
    feet[2] = feet[2] + [0, 0, 500]  # lift one foot far beyond reach
    reports = leg_reports(NEUTRAL, feet, L, P, LIM)
    assert not reports[2].reachable and reports[2].q is None
    assert all(r.reachable and r.violations == [] for i, r in enumerate(reports) if i != 2)


def test_reachable_target_outside_limits_reports_violations() -> None:
    low = BodyPose(x=0, y=0, z=NEUTRAL.z - 30, roll=0, pitch=0, yaw=0)
    reports = leg_reports(low, FEET, L, P, LIM)
    assert any(r.reachable and r.violations for r in reports)


def test_verify_stance_accepts_the_default_layout() -> None:
    verify_stance(L, P, LIM)


def test_unsupported_stance_raises_an_explicit_error() -> None:
    with pytest.raises(UnsupportedStanceError, match="leg 0"):
        verify_stance(BodyLayout(stance_height=200), P, LIM)


def test_layout_is_provisional_and_joins_the_params_flag() -> None:
    assert L.provisional is True
    assert is_provisional(P, L) is True
    assert is_provisional(P, BodyLayout(provisional=False)) is P.provisional
