"""Command line: `python -m hexapod report|plot --out DIR [--params FILE]`.

Exit status is 0 whenever the run completes, even if the report lists limit or torque
findings; it is 1 when the parameter snapshot cannot be loaded and 2 for bad usage.
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from hexapod.body import BodyLayout
from hexapod.gait import RIPPLE, TRIPOD, WAVE, run
from hexapod.params import ParamsError, load_params
from hexapod.report import build_report
from hexapod.viz import render_gait


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hexapod")
    parser.add_argument("command", choices=("report", "plot"))
    parser.add_argument("--out", type=Path, default=Path("build/software"))
    parser.add_argument(
        "--params", type=Path, default=None, help="snapshot JSON (default: bundled)"
    )
    args = parser.parse_args(argv)
    try:
        params = load_params(args.params)
    except (ParamsError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    layout = BodyLayout()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.command == "report":
        (args.out / "report.md").write_text(build_report(params, layout) + "\n")
        print(f"wrote {args.out / 'report.md'}")
    else:
        for spec in (TRIPOD, WAVE, RIPPLE):
            target = args.out / f"{spec.name}.png"
            render_gait(run(spec, layout, params), spec.name, params, layout, target)
            print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
