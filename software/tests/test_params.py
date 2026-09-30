"""Tests for the CAD parameter snapshot loader."""

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from hexapod.params import ParamsError, load_params


def _snapshot() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "src" / "hexapod" / "data" / "leg-params.json"
    data: dict[str, Any] = json.loads(path.read_text())
    return data


def _write(tmp_path: Path, data: dict[str, Any]) -> Path:
    path = tmp_path / "params.json"
    path.write_text(json.dumps(data))
    return path


def test_valid_load_of_committed_snapshot() -> None:
    params = load_params()
    assert params.leg.coxa_l == pytest.approx(30)
    assert params.leg.knee_to_foot == pytest.approx(86)
    assert params.leg.foot_dy == pytest.approx(-1.3)
    assert params.limits.fit_alpha == (-30, 0, 30)
    assert params.limits.fit_phi == (-15, 0, 20, 45)
    assert len(params.fk_golden) == 12
    assert all(len(row) == 5 for row in params.fk_golden)
    assert params.servo.range_deg == pytest.approx(180)


def test_schema_version_is_checked(tmp_path: Path) -> None:
    data = _snapshot()
    data["schema_version"] = 2
    with pytest.raises(ParamsError, match="schema_version"):
        load_params(_write(tmp_path, data))


def test_missing_key_names_fit_phi(tmp_path: Path) -> None:
    data = _snapshot()
    del data["limits"]["fit_phi"]
    with pytest.raises(ParamsError, match="fit_phi"):
        load_params(_write(tmp_path, data))


def test_unknown_keys_are_ignored(tmp_path: Path) -> None:
    data = _snapshot()
    data["future"] = {"x": 1}
    data["leg"]["extra"] = 5
    assert load_params(_write(tmp_path, data)) == load_params()


def test_provisional_is_or_of_servo_flag_and_list(tmp_path: Path) -> None:
    data = _snapshot()
    data["servo"]["provisional"] = False
    data["provisional"] = []
    assert not load_params(_write(tmp_path, data)).provisional
    data["provisional"] = ["servo"]
    assert load_params(_write(tmp_path, data)).provisional
    other = copy.deepcopy(data)
    other["provisional"] = []
    other["servo"]["provisional"] = True
    assert load_params(_write(tmp_path, other)).provisional
    assert load_params().provisional_names == ("servo",)


def test_non_numeric_value_rejected(tmp_path: Path) -> None:
    data = _snapshot()
    data["leg"]["coxa_l"] = "thirty"
    with pytest.raises(ParamsError, match="coxa_l"):
        load_params(_write(tmp_path, data))


def test_boolean_is_not_a_number(tmp_path: Path) -> None:
    data = _snapshot()
    data["leg"]["coxa_l"] = True
    with pytest.raises(ParamsError, match="coxa_l"):
        load_params(_write(tmp_path, data))


def test_missing_file_rejected(tmp_path: Path) -> None:
    with pytest.raises(ParamsError, match="not found"):
        load_params(tmp_path / "absent.json")
