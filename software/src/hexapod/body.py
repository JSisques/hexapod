"""Body kinematics on a PROVISIONAL hexagonal layout (see ADR-0006).

Body frame B: origin at the body centre on the coxa plane, +X forward, +Y left, +Z up.
The world ground is z = 0. Leg k is mounted at angle 30 + 60k degrees and its frame is
the body frame rotated by that angle. Body values live here, not in the CAD snapshot.
"""

import math
from dataclasses import dataclass

import numpy as np

from hexapod.leg import FloatArray, JointAngles, UnreachableError, ik
from hexapod.limits import JointLimits, Violation, violations
from hexapod.params import LegGeometry, Params


@dataclass(frozen=True)
class BodyLayout:
    """Placeholder layout; every value is PROVISIONAL until the body is designed in CAD."""

    mount_radius: float = 80.0
    mount_angles: tuple[float, ...] = tuple(30.0 + 60.0 * k for k in range(6))
    stance_height: float = 60.0  # foot plane below the coxa frame
    reach: float = 100.0  # neutral foot distance from the coxa axis
    provisional: bool = True

    def neutral_pose(self) -> "BodyPose":
        return BodyPose(z=self.stance_height)


@dataclass(frozen=True)
class BodyPose:
    """Body position in the world (mm) and roll, pitch, yaw (degrees); R = Rz Ry Rx."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0


@dataclass(frozen=True)
class LegReport:
    reachable: bool
    q: JointAngles | None  # None when the target is unreachable
    violations: list[Violation]


class UnsupportedStanceError(ValueError):
    """The layout's neutral stance cannot be held by every leg."""


def _rz(deg: float) -> FloatArray:
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def _rotation(pose: BodyPose) -> FloatArray:
    cp, sp = math.cos(math.radians(pose.pitch)), math.sin(math.radians(pose.pitch))
    cr, sr = math.cos(math.radians(pose.roll)), math.sin(math.radians(pose.roll))
    ry = np.array([[cp, 0.0, sp], [0.0, 1.0, 0.0], [-sp, 0.0, cp]])
    rx = np.array([[1.0, 0.0, 0.0], [0.0, cr, -sr], [0.0, sr, cr]])
    rot: FloatArray = _rz(pose.yaw) @ ry @ rx
    return rot


def mount_points(layout: BodyLayout) -> FloatArray:
    """(6, 3) coxa-axis mount points in the body frame."""
    r = layout.mount_radius
    return np.array(
        [[r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0.0]
         for a in layout.mount_angles]
    )  # fmt: skip


def neutral_feet(layout: BodyLayout, g: LegGeometry) -> FloatArray:
    """(6, 3) world contact points for the neutral stance, on the ground plane."""
    mounts = mount_points(layout)
    lateral = np.array([layout.reach, g.foot_dy, 0.0])
    return np.array(
        [m + _rz(a) @ lateral for m, a in zip(mounts, layout.mount_angles, strict=True)]
    )


def leg_targets(
    pose: BodyPose, feet_world: FloatArray, layout: BodyLayout, g: LegGeometry
) -> FloatArray:
    """(6, 3) foot-sphere centres, each expressed in its own leg frame."""
    rot = _rotation(pose)
    origin = np.array([pose.x, pose.y, pose.z])
    lift = np.array([0.0, 0.0, g.ft_r])
    mounts = mount_points(layout)
    return np.array(
        [
            _rz(-a) @ (rot.T @ (foot + lift - origin) - m)
            for foot, m, a in zip(feet_world, mounts, layout.mount_angles, strict=True)
        ]
    )


def leg_reports(
    pose: BodyPose,
    feet_world: FloatArray,
    layout: BodyLayout,
    params: Params,
    limits: JointLimits,
) -> list[LegReport]:
    """Per-leg reachability and joint-limit check; each leg is evaluated independently."""
    reports = []
    for target in leg_targets(pose, feet_world, layout, params.leg):
        try:
            q = ik(target, params.leg)
        except UnreachableError:
            reports.append(LegReport(False, None, []))
        else:
            reports.append(LegReport(True, q, violations(limits, q)))
    return reports


def verify_stance(layout: BodyLayout, params: Params, limits: JointLimits) -> None:
    """Raise `UnsupportedStanceError` naming the first leg that cannot hold the neutral stance."""
    feet = neutral_feet(layout, params.leg)
    for k, r in enumerate(leg_reports(layout.neutral_pose(), feet, layout, params, limits)):
        if not r.reachable:
            raise UnsupportedStanceError(f"leg {k} cannot reach the neutral stance")
        if r.violations:
            joints = ", ".join(v.joint for v in r.violations)
            raise UnsupportedStanceError(f"leg {k} violates joint limits at neutral: {joints}")


def is_provisional(params: Params, layout: BodyLayout) -> bool:
    """The layout joins the provisional OR: True while any CAD or body value is a placeholder."""
    return params.provisional or layout.provisional
