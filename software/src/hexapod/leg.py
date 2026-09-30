"""Forward and inverse kinematics of one leg in the CAD leg frame (see ADR-0006).

Pure functions of a `LegGeometry`. Angles are degrees, lengths are millimetres.
"""

import math
from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import ArrayLike, NDArray

from hexapod.params import LegGeometry

FloatArray = NDArray[np.float64]
_EPS = 1e-9


@dataclass(frozen=True)
class JointAngles:
    theta: float  # coxa yaw about +Z
    alpha: float  # femur pitch, knee up positive
    phi: float  # knee angle relative to the femur; tibia from vertical = alpha + phi


class Reason(Enum):
    LATERAL = "lateral"  # target too close to the coxa axis for the lateral offset
    TOO_FAR = "too_far"
    TOO_CLOSE = "too_close"


class UnreachableError(ValueError):
    """The target is geometrically out of reach; `reason` says why."""

    def __init__(self, reason: Reason, target: FloatArray) -> None:
        super().__init__(f"unreachable ({reason.value}): {target.tolist()}")
        self.reason = reason


def fk(q: JointAngles, g: LegGeometry) -> FloatArray:
    """Foot-sphere centre in the leg frame."""
    a, ap = math.radians(q.alpha), math.radians(q.alpha + q.phi)
    r = g.coxa_l + g.femur_l * math.cos(a) + g.knee_to_foot * math.sin(ap)
    z = g.cb_zmid + g.femur_l * math.sin(a) - g.knee_to_foot * math.cos(ap)
    th = math.radians(q.theta)
    c, s = math.cos(th), math.sin(th)
    return np.array([c * r - s * g.foot_dy, s * r + c * g.foot_dy, z])


def ik(p: ArrayLike, g: LegGeometry) -> JointAngles:
    """Knee-up, outward-coxa solution for a foot-sphere centre; raises `UnreachableError`."""
    x, y, z = target = np.asarray(p, dtype=np.float64)
    d, f, t = g.foot_dy, g.femur_l, g.knee_to_foot
    rho2 = x * x + y * y
    if rho2 <= d * d + _EPS:
        raise UnreachableError(Reason.LATERAL, target)
    r = math.sqrt(rho2 - d * d)
    theta = math.degrees(math.atan2(y, x) - math.atan2(d, r))
    theta = 180.0 - ((180.0 - theta) % 360.0)  # wrap into (-180, 180]
    u, w = r - g.coxa_l, z - g.cb_zmid
    c = (u * u + w * w - f * f - t * t) / (2 * f * t)
    if abs(c) > 1 + _EPS:
        raise UnreachableError(Reason.TOO_FAR if c > 0 else Reason.TOO_CLOSE, target)
    q2 = -math.acos(max(-1.0, min(1.0, c)))
    alpha = math.atan2(w, u) - math.atan2(t * math.sin(q2), f + t * math.cos(q2))
    return JointAngles(theta, math.degrees(alpha), 90 + math.degrees(q2))
