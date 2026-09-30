#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Convert the OpenSCAD `hexapod_params` echo line into deterministic JSON.

Usage: echo-to-json.py [ECHO_FILE]   (reads stdin when no file is given; JSON goes to stdout)

The exporter (tools/cad/export-params.scad) echoes a key/value list. OpenSCAD prints
it in a JSON-compatible syntax, so the conversion only has to turn key/value lists
into objects and refuse anything JSON cannot represent. Standard library only.
"""

import json
import re
import sys
from typing import Any

PREFIX = "ECHO: hexapod_params = "
# Bare tokens OpenSCAD prints for values JSON cannot hold (strings are stripped before matching).
BAD_TOKEN = re.compile(r"(?<![\w.])(undef|nan|-?inf)(?![\w.])")
STRING = re.compile(r'"(?:[^"\\]|\\.)*"')


def _to_object(value: Any) -> Any:
    """Turn lists of [string, value] pairs into dicts, recursively; reject duplicate keys."""
    if not isinstance(value, list):
        return value
    is_kv = bool(value) and all(
        isinstance(item, list) and len(item) == 2 and isinstance(item[0], str) for item in value
    )
    if not is_kv:
        return [_to_object(item) for item in value]
    result: dict[str, Any] = {}
    for key, item in value:
        if key in result:
            raise ValueError(f"duplicate key '{key}'")
        result[key] = _to_object(item)
    return result


def convert(text: str) -> str:
    lines = [ln[len(PREFIX) :] for ln in text.splitlines() if ln.startswith(PREFIX)]
    if len(lines) != 1:
        raise ValueError(f"expected exactly one '{PREFIX.strip()}' line, found {len(lines)}")
    match = BAD_TOKEN.search(STRING.sub('""', lines[0]))
    if match:
        raise ValueError(f"value '{match.group(1)}' is not representable in JSON")
    try:
        parsed = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise ValueError(f"echo line is not valid JSON: {exc}") from exc
    return json.dumps(_to_object(parsed), indent=2, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    try:
        if len(argv) > 2:
            raise ValueError("usage: echo-to-json.py [ECHO_FILE]")
        if len(argv) == 2:
            with open(argv[1], encoding="utf-8") as handle:
                text = handle.read()
        else:
            text = sys.stdin.read()
        sys.stdout.write(convert(text))
    except (OSError, ValueError) as exc:
        print(f"echo-to-json: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
