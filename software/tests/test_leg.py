import numpy as np
import pytest

from hexapod.leg import JointAngles, Reason, UnreachableError, fk, ik
from hexapod.params import load_params

P = load_params()
G = P.leg
GRID = [(a, p) for a in P.limits.fit_alpha for p in P.limits.fit_phi]


@pytest.mark.parametrize(("alpha", "phi", "x", "y", "z"), P.fk_golden)
def test_fk_matches_cad_golden(alpha: float, phi: float, x: float, y: float, z: float) -> None:
    got = fk(JointAngles(0, alpha, phi), G)
    np.testing.assert_allclose(got, [x, y, z], atol=1e-3)


@pytest.mark.parametrize(("alpha", "phi"), GRID)
def test_ik_round_trip_on_grid(alpha: float, phi: float) -> None:
    q = ik(fk(JointAngles(0, alpha, phi), G), G)
    np.testing.assert_allclose([q.theta, q.alpha, q.phi], [0, alpha, phi], atol=1e-6)


def test_zero_pose_is_deterministic_and_offset() -> None:
    np.testing.assert_allclose(fk(JointAngles(0, 0, 0), G), [85, -1.3, -62.9], atol=1e-9)


def test_lateral_offset_rotates_with_theta() -> None:
    np.testing.assert_allclose(fk(JointAngles(90, 0, 0), G)[:2], [1.3, 85], atol=1e-9)


@pytest.mark.parametrize("theta", [-170.0, -45.0, 0.0, 33.0, 179.0])
def test_ik_round_trip_over_theta(theta: float) -> None:
    q = ik(fk(JointAngles(theta, 10, 20), G), G)
    assert q.theta == pytest.approx(theta, abs=1e-6)


def test_theta_wraps_into_half_open_range() -> None:
    q = ik(fk(JointAngles(190, 10, 20), G), G)
    assert q.theta == pytest.approx(-170, abs=1e-6)


@pytest.mark.parametrize(
    ("target", "reason"),
    [
        ((300, 0, 0), Reason.TOO_FAR),
        ((35, -1.3, 23.1), Reason.TOO_CLOSE),
        ((0.5, 0, -50), Reason.LATERAL),
    ],
)
def test_unreachable_reasons(target: tuple[float, float, float], reason: Reason) -> None:
    with pytest.raises(UnreachableError) as err:
        ik(target, G)
    assert err.value.reason is reason
