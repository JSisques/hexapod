import math

import numpy as np

from hexapod.stability import convex_hull, is_supported, margin


def test_triangle_margin_is_inradius_at_centroid() -> None:
    tri = np.array([[0.0, 2.0], [-math.sqrt(3), -1.0], [math.sqrt(3), -1.0]])  # circumradius 2
    assert np.isclose(margin(tri), 1.0)  # inradius of an equilateral triangle


def test_square_margin_is_half_side_and_off_centre_shrinks() -> None:
    sq = np.array([[1.0, 1.0], [-1.0, 1.0], [-1.0, -1.0], [1.0, -1.0]])
    assert np.isclose(margin(sq), 1.0)
    assert np.isclose(margin(sq, com_xy=(0.5, 0.0)), 0.5)


def test_centre_outside_hull_is_negative() -> None:
    sq = np.array([[1.0, 1.0], [3.0, 1.0], [3.0, 3.0], [1.0, 3.0]])
    assert margin(sq) < 0


def test_interior_and_duplicate_points_do_not_change_the_hull() -> None:
    sq = np.array([[1.0, 1.0], [-1.0, 1.0], [-1.0, -1.0], [1.0, -1.0], [0.2, 0.1], [1.0, 1.0]])
    assert len(convex_hull(sq)) == 4
    assert np.isclose(margin(sq), 1.0)


def test_fewer_than_three_feet_is_unsupported_and_not_positive() -> None:
    for pts in ([], [[1.0, 0.0]], [[1.0, 0.0], [-1.0, 0.0]]):
        p = np.array(pts, dtype=float).reshape(-1, 2)
        assert margin(p) == -math.inf
        assert not is_supported(p)


def test_collinear_and_coincident_feet_are_unsupported() -> None:
    line = np.array([[-1.0, 0.0], [0.0, 0.0], [1.0, 0.0]])
    same = np.array([[1.0, 1.0]] * 4)
    for p in (line, same):
        assert margin(p) == -math.inf
        assert not is_supported(p)


def test_three_non_collinear_feet_are_supported() -> None:
    assert is_supported(np.array([[0.0, 1.0], [-1.0, -1.0], [1.0, -1.0]]))
