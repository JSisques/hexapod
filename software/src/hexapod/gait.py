"""Phase-based gait engine: one implementation, gaits are parameter sets (see design.md).

Leg order is [LF, LM, LR, RR, RM, RF]. The body holds the neutral pose; each foot moves in
the body frame along the heading. Stance moves the foot backwards linearly, swing returns it
along a cosine path with a sine lift, so the path is continuous at the stance/swing joins.
"""

import math
from dataclasses import dataclass

import numpy as np

from hexapod.body import BodyLayout, leg_reports, neutral_feet
from hexapod.leg import FloatArray, JointAngles
from hexapod.limits import JointLimits
from hexapod.params import Params
from hexapod.stability import margin


@dataclass(frozen=True)
class GaitSpec:
    """Gait parameters. `heading` is degrees from body +X; lengths are millimetres."""

    name: str
    duty: float
    offsets: tuple[float, ...]
    step_length: float = 30.0
    step_height: float = 10.0
    heading: float = 0.0


TRIPOD = GaitSpec("tripod", 0.5, (0.0, 0.5, 0.0, 0.5, 0.0, 0.5))
WAVE = GaitSpec("wave", 5 / 6, (5 / 6, 4 / 6, 3 / 6, 0.0, 1 / 6, 2 / 6))
RIPPLE = GaitSpec("ripple", 2 / 3, (2 / 3, 1 / 3, 0.0, 1 / 2, 5 / 6, 1 / 6))


@dataclass(frozen=True)
class LegViolation:
    leg: int
    joint: str  # theta, alpha, phi, or "unreachable" (amount is then infinite)
    amount: float


@dataclass(frozen=True)
class Frame:
    s: float
    stance: tuple[bool, ...]
    feet: FloatArray  # (6, 3) world foot contact points
    q: tuple[JointAngles | None, ...]  # None for an unreachable leg
    violations: list[LegViolation]
    margin: float  # static stability margin in mm; -inf when unsupported

    @property
    def supported(self) -> bool:
        """False when fewer than three non-collinear feet are grounded."""
        return math.isfinite(self.margin)


def _foot_offset(spec: GaitSpec, s_leg: float) -> tuple[float, float, bool]:
    """(along-heading displacement, lift, in_stance) for a leg phase in [0, 1)."""
    half = spec.step_length / 2
    if s_leg < spec.duty:
        return -spec.step_length * (s_leg / spec.duty - 0.5), 0.0, True
    u = (s_leg - spec.duty) / (1 - spec.duty)
    return -half * math.cos(math.pi * u), spec.step_height * math.sin(math.pi * u), False


def frame_at(
    spec: GaitSpec, s: float, layout: BodyLayout, params: Params, limits: JointLimits | None = None
) -> Frame:
    """Evaluate the gait at global phase `s` (taken modulo 1) through leg kinematics."""
    limits = limits or JointLimits.from_params(params.limits)
    s %= 1.0
    h = math.radians(spec.heading)
    direction = np.array([math.cos(h), math.sin(h), 0.0])
    feet = neutral_feet(layout, params.leg)
    stance = []
    for k, offset in enumerate(spec.offsets):
        along, lift, grounded = _foot_offset(spec, (s + offset) % 1.0)
        feet[k] = feet[k] + along * direction + np.array([0.0, 0.0, lift])
        stance.append(grounded)
    found = []
    reports = leg_reports(layout.neutral_pose(), feet, layout, params, limits)
    for k, r in enumerate(reports):
        if not r.reachable:
            found.append(LegViolation(k, "unreachable", math.inf))
        found.extend(LegViolation(k, v.joint, v.amount) for v in r.violations)
    support_xy = feet[[k for k, g in enumerate(stance) if g], :2]
    return Frame(s, tuple(stance), feet, tuple(r.q for r in reports), found, margin(support_xy))


def run(spec: GaitSpec, layout: BodyLayout, params: Params, samples: int = 120) -> list[Frame]:
    """Sample one full cycle; limit violations are reported in the frames, never raised."""
    limits = JointLimits.from_params(params.limits)
    return [frame_at(spec, i / samples, layout, params, limits) for i in range(samples)]
