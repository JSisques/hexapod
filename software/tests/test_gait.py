import numpy as np

from hexapod.body import BodyLayout
from hexapod.gait import TRIPOD, GaitSpec, frame_at, run
from hexapod.params import load_params

P = load_params()
L = BodyLayout()
LEG_NAMES = ("LF", "LM", "LR", "RR", "RM", "RF")


def test_tripod_is_duty_half_with_two_alternating_triples() -> None:
    assert TRIPOD.duty == 0.5
    assert TRIPOD.offsets == (0.0, 0.5, 0.0, 0.5, 0.0, 0.5)
    assert (TRIPOD.step_length, TRIPOD.step_height) == (30.0, 10.0)
    swing = [f.stance for f in (frame_at(TRIPOD, 0.75, L, P), frame_at(TRIPOD, 0.25, L, P))]
    assert swing[0] == (False, True, False, True, False, True)
    assert swing[1] == tuple(not x for x in swing[0])


def test_periodicity_phase_0_equals_phase_1() -> None:
    a, b = frame_at(TRIPOD, 0.0, L, P), frame_at(TRIPOD, 1.0, L, P)
    assert a.stance == b.stance
    assert np.allclose(a.feet, b.feet)


def test_stance_foot_is_fixed_relative_to_ground() -> None:
    # The body is fixed in the world here, so a stance foot moves backwards at constant speed.
    a, b, c = (frame_at(TRIPOD, s, L, P) for s in (0.05, 0.15, 0.25))
    for leg in (0, 2, 4):  # stance for s in [0, 0.5)
        assert a.stance[leg] and b.stance[leg] and c.stance[leg]
        assert np.isclose(b.feet[leg, 2], 0.0)
        assert np.allclose(b.feet[leg] - a.feet[leg], c.feet[leg] - b.feet[leg])
        assert np.isclose((a.feet[leg] - b.feet[leg])[0], 0.1 / 0.5 * 30.0)


def test_foot_path_is_continuous_across_swing_and_stance() -> None:
    frames = run(TRIPOD, L, P, samples=1200)
    feet = np.array([f.feet for f in frames] + [frames[0].feet])
    steps = np.linalg.norm(np.diff(feet, axis=0), axis=2)
    assert steps.max() < 0.5  # per-sample motion is small; a jump would be tens of mm


def test_swing_lifts_by_step_height_and_stance_stays_on_ground() -> None:
    frames = run(TRIPOD, L, P)
    lift = np.array([f.feet[:, 2] for f in frames])
    assert np.isclose(lift.max(), 10.0, atol=0.05)
    assert np.allclose(lift.min(), 0.0)
    for f in frames:
        for leg in range(6):
            if f.stance[leg]:
                assert np.isclose(f.feet[leg, 2], 0.0)


def test_at_least_three_legs_grounded_at_every_sample() -> None:
    assert all(sum(f.stance) >= 3 for f in run(TRIPOD, L, P))


def test_heading_rotates_the_stride_direction() -> None:
    spec = GaitSpec("tripod-left", 0.5, TRIPOD.offsets, heading=90.0)
    a, b = frame_at(spec, 0.0, L, P), frame_at(TRIPOD, 0.0, L, P)
    delta = a.feet[0] - b.feet[0]
    assert np.isclose(delta[0], -15.0) and np.isclose(delta[1], 15.0)


def test_default_tripod_stays_inside_joint_limits_and_reports_min_phi() -> None:
    frames = run(TRIPOD, L, P)
    assert len(frames) == 120
    assert all(not f.violations for f in frames)
    assert all(q is not None for f in frames for q in f.q)
    phis = [q.phi for f in frames for q in f.q if q is not None]
    print(f"min phi over the tripod cycle: {min(phis):.3f} deg (limit {min(P.limits.fit_phi)})")
    assert min(phis) >= min(P.limits.fit_phi)


def test_stride_40_lift_15_is_reported_as_violation_data() -> None:
    spec = GaitSpec("tripod-long", 0.5, TRIPOD.offsets, step_length=40.0, step_height=15.0)
    frames = run(spec, L, P)  # must not raise
    found = [(f.s, v) for f in frames for v in f.violations]
    assert found
    assert any(v.joint == "phi" and v.leg in (0, 2, 3, 5) for _, v in found)
    assert all(v.amount > 0 for _, v in found)
