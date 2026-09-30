import math

import numpy as np
import pytest

from hexapod.body import BodyLayout
from hexapod.gait import RIPPLE, TRIPOD, WAVE, GaitSpec, run
from hexapod.leg import ik
from hexapod.params import load_params

P = load_params()
L = BodyLayout()
GAITS = {"tripod": (TRIPOD, 3), "wave": (WAVE, 5), "ripple": (RIPPLE, 4)}


def test_wave_and_ripple_parameter_sets() -> None:
    assert WAVE.duty == pytest.approx(5 / 6)
    assert WAVE.offsets == pytest.approx((5 / 6, 4 / 6, 3 / 6, 0, 1 / 6, 2 / 6))
    assert RIPPLE.duty == pytest.approx(2 / 3)
    assert RIPPLE.offsets == pytest.approx((2 / 3, 1 / 3, 0, 1 / 2, 5 / 6, 1 / 6))
    for spec in (WAVE, RIPPLE):
        assert (spec.step_length, spec.step_height) == (30.0, 10.0)


def test_wave_swings_one_leg_at_a_time_in_sequence() -> None:
    order: list[int] = []
    for f in run(WAVE, L, P, samples=120):
        swinging = [k for k, g in enumerate(f.stance) if not g]
        assert len(swinging) <= 1
        if swinging and (not order or order[-1] != swinging[0]):
            order.append(swinging[0])
    assert order == [0, 1, 2, 5, 4, 3]  # LF, LM, LR, then RF, RM, RR (front to rear per side)


def test_ripple_swings_two_legs_at_once() -> None:
    counts = {sum(not g for g in f.stance) for f in run(RIPPLE, L, P, samples=120)}
    assert counts == {2}


@pytest.mark.parametrize("name", GAITS)
def test_min_grounded_legs_over_full_cycle(name: str) -> None:
    spec, minimum = GAITS[name]
    grounded = [sum(f.stance) for f in run(spec, L, P, samples=600)]
    assert min(grounded) == minimum


@pytest.mark.parametrize("name", GAITS)
def test_margin_positive_and_no_violations_at_defaults(name: str) -> None:
    spec, _ = GAITS[name]
    frames = run(spec, L, P)
    margins = [f.margin for f in frames]
    phis = [q.phi for f in frames for q in f.q if q is not None]
    print(f"{name}: min margin {min(margins):.3f} mm, min phi {min(phis):.3f} deg")
    assert all(m > 0 for m in margins)
    assert all(f.supported for f in frames)
    assert all(not f.violations for f in frames)
    assert min(phis) >= min(P.limits.fit_phi)


def test_margin_uses_grounded_feet_only() -> None:
    frames = run(TRIPOD, L, P)
    f = frames[0]
    xy = np.array([f.feet[k, :2] for k in range(6) if f.stance[k]])
    assert len(xy) == 3
    assert f.margin > 0


def test_unsupported_frame_is_flagged() -> None:
    spec = GaitSpec("all-swing", 0.1, (0.0,) * 6)  # every leg swings together at s = 0.5
    f = run(spec, L, P, samples=2)[1]
    assert not any(f.stance)
    assert f.margin == -math.inf and not f.supported and f.margin <= 0


def test_stride_30_lift_10_feasible_and_neutral_ik_unchanged() -> None:
    q = ik((100.0, -1.3, -52.0), P.leg)
    assert q.theta == pytest.approx(0.0, abs=1e-6)
    assert q.alpha == pytest.approx(9.9, abs=0.1)
    assert q.phi == pytest.approx(0.7, abs=0.1)
    for spec, _ in GAITS.values():
        assert (spec.step_length, spec.step_height) == (30.0, 10.0)
        assert all(not f.violations for f in run(spec, L, P))
