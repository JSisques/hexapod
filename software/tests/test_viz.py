from pathlib import Path

import pytest

from hexapod.body import BodyLayout
from hexapod.gait import RIPPLE, TRIPOD, WAVE, run
from hexapod.params import load_params
from hexapod.viz import PNG_MAGIC, provisional_title, render_gait

P = load_params()
L = BodyLayout()


def test_render_writes_non_empty_png(tmp_path: Path) -> None:
    out = tmp_path / "tripod.png"
    render_gait(run(TRIPOD, L, P, samples=24), TRIPOD.name, P, L, out)
    data = out.read_bytes()
    assert data.startswith(PNG_MAGIC)
    assert len(data) > 5_000


@pytest.mark.parametrize("spec", [WAVE, RIPPLE])
def test_render_other_gaits(tmp_path: Path, spec) -> None:  # type: ignore[no-untyped-def]
    out = tmp_path / f"{spec.name}.png"
    render_gait(run(spec, L, P, samples=24), spec.name, P, L, out)
    assert out.stat().st_size > 5_000


def test_title_marks_provisional() -> None:
    assert P.servo.provisional
    assert "PROVISIONAL" in provisional_title("tripod", P, L)


def test_title_has_no_marker_when_nothing_is_provisional() -> None:
    from dataclasses import replace

    clean = replace(P, servo=replace(P.servo, provisional=False), provisional_names=())
    assert "PROVISIONAL" not in provisional_title("tripod", clean, replace(L, provisional=False))
