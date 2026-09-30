"""Tests for tools/cad/echo-to-json.py (the OpenSCAD echo to JSON converter)."""

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "cad" / "echo-to-json.py"
PREFIX = "ECHO: hexapod_params = "


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("echo_to_json", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


conv = _load()


def _echo(body: str) -> str:
    return f"{PREFIX}{body}\n"


def test_converts_kv_list_to_sorted_object() -> None:
    text = conv.convert(_echo('[["b", 2], ["a", [["x", 1.5], ["y", "s"]]], ["c", [1, 2]]]'))
    assert json.loads(text) == {"a": {"x": 1.5, "y": "s"}, "b": 2, "c": [1, 2]}
    assert text.index('"a"') < text.index('"b"') < text.index('"c"')
    assert text.endswith("}\n")


def test_numeric_pair_lists_stay_lists() -> None:
    data = json.loads(conv.convert(_echo('[["stall", [[4.8, 9.4], [6, 11]]], ["empty", []]]')))
    assert data == {"stall": [[4.8, 9.4], [6, 11]], "empty": []}


def test_ignores_unrelated_echo_lines() -> None:
    text = "ECHO: other = 1\n" + _echo('[["a", 1]]') + 'ECHO: "note"\n'
    assert json.loads(conv.convert(text)) == {"a": 1}


def test_zero_echo_lines_rejected() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        conv.convert("ECHO: other = 1\n")


def test_two_echo_lines_rejected() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        conv.convert(_echo('[["a", 1]]') * 2)


@pytest.mark.parametrize("token", ["undef", "nan", "inf", "-inf"])
def test_non_finite_values_rejected(token: str) -> None:
    with pytest.raises(ValueError, match=token.lstrip("-")):
        conv.convert(_echo(f'[["a", {token}]]'))


def test_token_inside_string_is_allowed() -> None:
    assert json.loads(conv.convert(_echo('[["a", "undef nan inf"]]'))) == {"a": "undef nan inf"}


def test_duplicate_key_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate key 'a'"):
        conv.convert(_echo('[["a", 1], ["a", 2]]'))


def test_output_is_deterministic() -> None:
    text = _echo('[["b", 1], ["a", 2]]')
    first = conv.convert(text).encode()
    assert first == conv.convert(text).encode()
    assert first == conv.convert(_echo('[["a", 2], ["b", 1]]')).encode()
