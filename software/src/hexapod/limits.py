"""Joint limits: the CAD fit envelope plus a PROVISIONAL coxa yaw range (see ADR-0006)."""

from dataclasses import dataclass

from hexapod.leg import JointAngles
from hexapod.params import Limits

THETA_LIMIT = 45.0  # PROVISIONAL: no CAD source yet for the coxa yaw range


@dataclass(frozen=True)
class Violation:
    joint: str
    amount: float  # degrees beyond the nearest bound, always > 0


@dataclass(frozen=True)
class JointLimits:
    alpha: tuple[float, float]
    phi: tuple[float, float]
    theta: tuple[float, float] = (-THETA_LIMIT, THETA_LIMIT)

    @classmethod
    def from_params(cls, lim: Limits) -> "JointLimits":
        a, p = lim.fit_alpha, lim.fit_phi
        return cls(alpha=(min(a), max(a)), phi=(min(p), max(p)))


def violations(lim: JointLimits, q: JointAngles) -> list[Violation]:
    """Every joint outside its hard limits, in the order theta, alpha, phi."""
    found = []
    for joint, value in (("theta", q.theta), ("alpha", q.alpha), ("phi", q.phi)):
        lo, hi = getattr(lim, joint)
        if value < lo or value > hi:
            found.append(Violation(joint, lo - value if value < lo else value - hi))
    return found


def servo_range_failures(lim: JointLimits, range_deg: float) -> list[Violation]:
    """Joints whose largest limit magnitude exceeds half the servo range (neutral = 0)."""
    half = range_deg / 2
    reach = {j: max(abs(b) for b in getattr(lim, j)) for j in ("theta", "alpha", "phi")}
    return [Violation(j, m - half) for j, m in reach.items() if m > half]
