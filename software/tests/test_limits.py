import pytest

from hexapod.leg import JointAngles, fk, ik
from hexapod.limits import JointLimits, servo_range_failures, violations
from hexapod.params import load_params

P = load_params()
LIM = JointLimits.from_params(P.limits)


def test_limits_come_from_the_envelope() -> None:
    assert (LIM.alpha, LIM.phi, LIM.theta) == ((-30, 30), (-15, 45), (-45, 45))


def test_within_limits() -> None:
    assert violations(LIM, JointAngles(0, 30, 45)) == []


def test_phi_violation_reports_joint_and_amount() -> None:
    (v,) = violations(LIM, JointAngles(0, 0, 60))
    assert v.joint == "phi"
    assert v.amount == pytest.approx(15)


def test_low_side_and_multiple_violations() -> None:
    found = {v.joint: v.amount for v in violations(LIM, JointAngles(-50, -40, -15))}
    assert found == {"theta": pytest.approx(5), "alpha": pytest.approx(10)}


def test_servo_range_covers_the_envelope() -> None:
    assert servo_range_failures(LIM, P.servo.range_deg) == []


def test_servo_inclusion_failure_names_the_joint() -> None:
    assert [v.joint for v in servo_range_failures(LIM, 80)] == ["theta", "phi"]


def test_placeholder_neutral_stance_is_feasible() -> None:
    """Design placeholder: foot 100 mm out and 52 mm below the coxa plane."""
    q = ik((100, P.leg.foot_dy, -52), P.leg)
    assert q.theta == pytest.approx(0, abs=1e-9)
    assert q.alpha == pytest.approx(9.9, abs=0.05)
    assert q.phi == pytest.approx(0.7, abs=0.05)
    assert violations(LIM, q) == []
    assert fk(q, P.leg)[2] == pytest.approx(-52)
