import json
from dataclasses import replace
from importlib import resources
from pathlib import Path

import pytest

from hexapod.__main__ import main
from hexapod.body import BodyLayout
from hexapod.params import load_params
from hexapod.report import KNOWN_ISSUE, build_report, torque_rows

P = load_params()
L = BodyLayout()


def test_torque_rows_follow_the_cad_formula() -> None:
    rows = torque_rows(P, phi=20.0)
    assert [(r.joint, r.case) for r in rows] == [
        ("femur", "static"),
        ("femur", "peak"),
        ("tibia", "static"),
        ("tibia", "peak"),
    ]
    m_total = 18 * 0.055 + 6 * 0.6 * (30 + 55 + 80) / 1000 + 0.52
    f_static = m_total / 3
    tibia_static = f_static * 80 / 10 * 0.3420201433256687
    assert rows[2].tau == pytest.approx(tibia_static)
    assert rows[3].tau == pytest.approx(tibia_static * 1.5)
    assert rows[0].allowable == pytest.approx(11 * 0.6)
    assert rows[1].allowable == pytest.approx(11 * 0.8)
    assert all(r.ok for r in rows)


def test_report_contents() -> None:
    text = build_report(P, L)
    assert text.startswith("# Pose report")
    assert "PROVISIONAL" in text.splitlines()[2]
    for gait in ("tripod", "wave", "ripple"):
        assert f"## {gait}" in text
    assert "alpha margin" in text and "phi margin" in text
    assert "| femur | static |" in text and "| tibia | peak |" in text
    assert KNOWN_ISSUE in text
    assert "alpha != 0" in KNOWN_ISSUE


def test_report_flags_stride_violations_as_data() -> None:
    text = build_report(P, L, step_length=40.0, step_height=15.0)
    assert "VIOLATION" in text


def test_torque_warning_is_informational() -> None:
    weak = replace(P, torque=replace(P.torque, k_dyn=20.0))
    rows = torque_rows(weak, phi=20.0)
    assert not all(r.ok for r in rows)
    text = build_report(weak, L)
    assert "WARNING: torque budget exceeded" in text


def test_cli_report_and_plot_exit_zero(tmp_path: Path) -> None:
    assert main(["report", "--out", str(tmp_path)]) == 0
    assert (tmp_path / "report.md").read_text().startswith("# Pose report")
    assert main(["plot", "--out", str(tmp_path)]) == 0
    for name in ("tripod", "wave", "ripple"):
        assert (tmp_path / f"{name}.png").stat().st_size > 5_000


def test_cli_bad_usage_and_missing_params(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["frobnicate"])
    assert exc.value.code == 2
    assert main(["report", "--out", str(tmp_path), "--params", str(tmp_path / "nope.json")]) == 1


def test_cli_report_with_torque_warning_still_exits_zero(tmp_path: Path) -> None:
    text = resources.files("hexapod").joinpath("data/leg-params.json").read_text("utf-8")
    snapshot = json.loads(text)
    snapshot["torque"]["k_dyn"] = 20.0
    weak = tmp_path / "weak.json"
    weak.write_text(json.dumps(snapshot))
    assert main(["report", "--out", str(tmp_path), "--params", str(weak)]) == 0
    assert "WARNING: torque budget exceeded" in (tmp_path / "report.md").read_text()
