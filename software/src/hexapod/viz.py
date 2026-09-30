"""Headless gait visualiser: top-down foot paths and stability margin, written as PNG.

Uses the Agg canvas directly (no pyplot, no display, no global backend state).
"""

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from hexapod.body import BodyLayout, is_provisional, mount_points
from hexapod.gait import Frame
from hexapod.params import Params

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def provisional_title(name: str, params: Params, layout: BodyLayout) -> str:
    """Plot title; carries the PROVISIONAL marker while any input is provisional."""
    banner = "PROVISIONAL - " if is_provisional(params, layout) else ""
    return f"{banner}{name} gait"


def render_gait(
    frames: Sequence[Frame], name: str, params: Params, layout: BodyLayout, out: Path
) -> None:
    """Write a PNG with foot trails (top view) and the stability margin over the cycle."""
    fig = Figure(figsize=(10, 5), dpi=100)
    FigureCanvasAgg(fig)
    top, margin = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.2, 1]})
    mounts = mount_points(layout)
    top.scatter(mounts[:, 0], mounts[:, 1], marker="s", color="black", label="coxa mounts")
    for k in range(6):
        trail = np.array([f.feet[k, :2] for f in frames])
        top.plot(trail[:, 0], trail[:, 1], label=f"leg {k}")
    top.set_aspect("equal")
    top.set_xlabel("x (mm)")
    top.set_ylabel("y (mm)")
    top.legend(fontsize=7, ncol=2)
    phase = [f.s for f in frames]
    margin.plot(phase, [f.margin for f in frames])
    margin.axhline(0.0, color="red", linewidth=0.8)
    margin.set_xlabel("phase")
    margin.set_ylabel("stability margin (mm)")
    fig.suptitle(
        provisional_title(name, params, layout),
        color="red" if is_provisional(params, layout) else "black",
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
