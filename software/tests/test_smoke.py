"""Smoke test: the package is importable and exposes a version."""

import hexapod


def test_package_imports() -> None:
    assert hexapod.__name__ == "hexapod"


def test_version_is_a_non_empty_string() -> None:
    assert isinstance(hexapod.__version__, str)
    assert hexapod.__version__ != ""
