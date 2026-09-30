"""Static stability margin: distance from the body-centre projection to the support hull.

The support polygon is the convex hull of the grounded feet (monotone chain, numpy only).
The centre of mass is taken at the body origin (PROVISIONAL, see design.md).
"""

import math
from collections.abc import Sequence

import numpy as np

from hexapod.leg import FloatArray


def convex_hull(points: FloatArray) -> FloatArray:
    """Counter-clockwise hull without collinear or duplicate points; may return < 3 points."""
    pts = np.unique(np.asarray(points, dtype=float).reshape(-1, 2), axis=0)  # sorted by x, y
    if len(pts) < 3:
        return pts

    def half(seq: FloatArray) -> list[FloatArray]:
        out: list[FloatArray] = []
        for p in seq:
            while len(out) >= 2:
                a, b = out[-2], out[-1]
                if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) > 1e-12:
                    break
                out.pop()
            out.append(p)
        return out

    lower, upper = half(pts), half(pts[::-1])
    return np.array(lower[:-1] + upper[:-1])


def margin(stance_xy: FloatArray, com_xy: Sequence[float] = (0.0, 0.0)) -> float:
    """Signed distance from `com_xy` to the nearest hull edge; positive when inside.

    Unsupported input (fewer than 3 distinct, non-collinear feet) returns `-inf`.
    """
    hull = convex_hull(stance_xy)
    if len(hull) < 3:
        return -math.inf
    edges = np.roll(hull, -1, axis=0) - hull
    rel = np.asarray(com_xy, dtype=float) - hull
    cross = edges[:, 0] * rel[:, 1] - edges[:, 1] * rel[:, 0]  # > 0 when left of a CCW edge
    return float(np.min(cross / np.linalg.norm(edges, axis=1)))


def is_supported(stance_xy: FloatArray) -> bool:
    """True when the grounded feet span a polygon (at least 3 non-collinear points)."""
    return len(convex_hull(stance_xy)) >= 3
