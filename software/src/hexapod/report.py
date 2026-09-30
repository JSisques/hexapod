"""Text pose report: joint-limit margins, torque rows and the known-issue note.

Findings are data, never exit codes: a violation or a torque warning is written into the
report and does not change the process status.
"""

import math
from dataclasses import dataclass, replace

from hexapod.body import BodyLayout, is_provisional
from hexapod.gait import RIPPLE, TRIPOD, WAVE, Frame, GaitSpec, run
from hexapod.limits import JointLimits
from hexapod.params import Params

KNOWN_ISSUE = (
    "Known issue: the CAD `tau_femur` formula uses cos(alpha) and the CAD gate evaluates it at "
    "alpha = 0. Rows below use that formula as-is; for alpha != 0 they are inconsistent with the "
    "gait poses and must not be read as verified torque margins."
)


@dataclass(frozen=True)
class TorqueRow:
    joint: str
    case: str
    tau: float  # kg.cm
    allowable: float  # kg.cm

    @property
    def ok(self) -> bool:
        return self.tau <= self.allowable


def torque_rows(params: Params, phi: float, alpha: float = 0.0) -> list[TorqueRow]:
    """Mirror of `torque_rows` in hardware/cad/common/torque.scad (kg.cm), formula as-is."""
    g, t, s = params.leg, params.torque, params.servo
    stall = next(v for volts, v in s.stall_kgcm if volts == t.supply_v)
    m_total = (
        t.n_servo * s.mass_kg
        + 6 * t.link_g_per_mm * (g.coxa_l + g.femur_l + g.tibia_l) / 1000
        + t.m_body_kg
    )
    sin_phi = math.sin(math.radians(phi))
    rows = []
    for case, k, derate in (
        ("static", 1.0, t.derate_static),
        ("peak", t.k_dyn, t.derate_peak),
    ):
        force = m_total / 3 * k
        femur = force * (g.femur_l * math.cos(math.radians(alpha)) + g.tibia_l * sin_phi) / 10
        tibia = force * g.tibia_l / 10 * sin_phi
        rows.append(
            (
                TorqueRow("femur", case, femur, stall * derate),
                TorqueRow("tibia", case, tibia, stall * derate),
            )
        )
    return [rows[0][0], rows[1][0], rows[0][1], rows[1][1]]


def _joint_margins(frames: list[Frame], lim: JointLimits) -> tuple[float, float, float]:
    """Smallest bound distance (deg) for alpha and phi, and the largest phi (torque worst case)."""
    a = [q.alpha for f in frames for q in f.q if q is not None]
    p = [q.phi for f in frames for q in f.q if q is not None]
    a_margin = min(min(v - lim.alpha[0], lim.alpha[1] - v) for v in a)
    p_margin = min(min(v - lim.phi[0], lim.phi[1] - v) for v in p)
    return a_margin, p_margin, max(p)


def _gait_section(spec: GaitSpec, layout: BodyLayout, params: Params) -> list[str]:
    frames = run(spec, layout, params)
    lim = JointLimits.from_params(params.limits)
    a_margin, p_margin, phi = _joint_margins(frames, lim)
    bad = [v for f in frames for v in f.violations]
    lines = [
        f"## {spec.name}",
        "",
        f"- stride {spec.step_length:g} mm, lift {spec.step_height:g} mm, {len(frames)} samples",
        f"- min stability margin: {min(f.margin for f in frames):.3f} mm",
        f"- alpha margin: {a_margin:.3f} deg, phi margin: {p_margin:.3f} deg",
    ]
    if bad:
        worst = max(bad, key=lambda v: v.amount)
        lines.append(
            f"- VIOLATION: {len(bad)} limit violations, worst {worst.joint} "
            f"on leg {worst.leg} by {worst.amount:.3f} deg"
        )
    else:
        lines.append("- no joint limit violations")
    lines += [
        "",
        f"Torque at the largest phi of the cycle ({phi:.3f} deg), alpha = 0:",
        "",
        "| joint | case | tau (kg.cm) | allowable (kg.cm) | margin |",
        "|---|---|---|---|---|",
    ]
    for r in torque_rows(params, phi):
        ratio = r.allowable / r.tau if r.tau > 0 else math.inf
        lines.append(f"| {r.joint} | {r.case} | {r.tau:.2f} | {r.allowable:.2f} | {ratio:.2f} |")
        if not r.ok:
            lines.append(
                f"WARNING: torque budget exceeded: {r.joint} {r.case} "
                f"{r.tau:.2f} > {r.allowable:.2f} kg.cm"
            )
    return lines + [""]


def build_report(
    params: Params,
    layout: BodyLayout,
    step_length: float | None = None,
    step_height: float | None = None,
) -> str:
    """Render the Markdown report for the tripod, wave and ripple gaits."""
    banner = (
        "**PROVISIONAL**: servo and body layout values are unmeasured guesses."
        if is_provisional(params, layout)
        else "All inputs are marked final."
    )
    lines = ["# Pose report", "", banner, "", KNOWN_ISSUE, ""]
    for spec in (TRIPOD, WAVE, RIPPLE):
        if step_length is not None:
            spec = replace(spec, step_length=step_length)
        if step_height is not None:
            spec = replace(spec, step_height=step_height)
        lines += _gait_section(spec, layout, params)
    return "\n".join(lines)
