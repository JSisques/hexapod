# Exploration: kinematics-and-gait (Roadmap Phase 2)

Status: exploration complete, product decisions pending confirmation. Artifact store: openspec.

## Current state

- `software/` holds only a stub README. The `repo-structure` spec requires `software/` and `firmware/` to stay stubs, so this change needs a MODIFIED delta ("Per-directory README", "Deferred scope excluded"; each MODIFIED block carries the full requirement).
- `make software` is a `NOT_IMPLEMENTED` placeholder (Makefile ~L150). `.editorconfig` defaults to indent 2 (needs a `[*.py]` block with indent 4). `openspec/config.yaml` has `runner: none`, `strict_tdd: false`, `linter: none`.
- Leg numbers are spread across files:

| Value | Location | Form |
|---|---|---|
| `leg_tiers` (XS = [30, 55, 80]) | `params.scad` L25-26 | multi-line list |
| `coxa_l`, `femur_l`, `tibia_l` | `params.scad` L30-32 | function-call expressions |
| `fit_alpha` [-30, 0, 30], `fit_phi` [-15, 0, 20, 45], `fit_vol_tol` | `params.scad` L63-65 | one-line literals (Makefile awk reads these) |
| Torque inputs | `params.scad` L37-46 | literals |
| Servo `range_deg`, `pulse_us`, `stall_kgcm`, `mass_kg` | `servos/mg996r.scad` | PROVISIONAL |
| `cb_zmid` = 23.1 | `leg-coxa-bracket/coxa-bracket.scad` | derived |
| `leg_lane_dy` = -5 | `params.scad` | literal |
| `ft_r` = 8, `ft_floor` = 14 | `leg-foot/foot.scad` | part file |
| `tb_zax` = -3.7 | `leg-tibia/tibia.scad` | derived in part file |

A text parser over `params.scad` cannot recover `coxa_l`, `cb_zmid` or foot geometry. Only OpenSCAD evaluating `asm-leg/asm-leg.scad` yields all of it.

## Joint conventions (derived from asm-leg.scad and torque.scad)

- Leg frame: coxa axis is Z at origin; femur axis along Y at x = `coxa_l`, y = -5, z = 23.1.
- `alpha` = femur pitch (knee-up positive). `phi` = knee angle relative to the femur; world tibia angle from vertical = `phi + alpha`.
- IK foot point: tip-sphere centre is `tibia_l + ft_floor - ft_r` = 86 mm from the knee (not 80).
- Constant lateral foot offset of -1.3 mm (lane -5 + `tb_zax` -3.7); planar 3R IK would ignore it.
- Coxa yaw has no sweep range or limit anywhere in the CAD.
- Inconsistency: `tau_femur` uses `sin(phi)` as a world angle; for alpha != 0 it should use `sin(phi+alpha)`. The gate only evaluates alpha = 0.
- `check-fit` samples 12 poses; interference-freedom between samples is assumed.

## Approaches

1. Tooling: Python 3.12 + pytest + ruff + numpy + matplotlib (recommended) vs Rust/C++ vs TypeScript.
2. Parameter sharing: A text-parse (incomplete) / B OpenSCAD as evaluator (non-hermetic) / C invert source to JSON (high effort, rewrites gated file) / **D = B + committed generated JSON + CI drift gate (recommended)**.
3. Fidelity: offset-aware closed-form IK in CAD frames (recommended).
4. Limits: hard limit = `fit_alpha`/`fit_phi` envelope; servo range as inclusion check; new provisional coxa yaw parameter.
5. Gait: one phase-based engine producing tripod, wave, ripple as parameter sets.

## PR slicing (~2000 lines, chain required)

| PR | Scope | Est. lines |
|---|---|---|
| 1 | ADR-0005, `software/` scaffold, editorconfig/gitignore, `software.yml`, Makefile targets, spec deltas, config | 250-320 |
| 2 | Params bridge: exporter, JSON snapshot, drift gate, loader, tests | 220-320 |
| 3 | Leg FK/IK, limits, tests at 12 grid poses, conventions doc | 330-390 |
| 4 | Body kinematics | 250-330 |
| 5 | Gait engine + tripod | 300-380 |
| 6 | Wave, ripple, stability margin | 200-300 |
| 7 | Visualisation, limit/torque-pose report, CI artifact | 300-390 |

## Open product decisions

1. Tooling details (uv vs pip/venv, mypy strictness).
2. Param sharing: D vs B vs A (is one committed generated JSON acceptable?).
3. Visualiser: matplotlib headless vs interactive.
4. Model 6 mm foot extension and -1.3 mm offset (recommended) vs ideal planar.
5. Angle API in degrees with CAD names (`alpha`, `phi`, new `theta`).
6. Placeholder body layout (mount radius, angles, stance height).
7. Coxa yaw limits (no CAD number exists).
8. Limit policy: hard limit = sweep envelope, or widen `fit_alpha`/`fit_phi`.
9. Torque checks on gait poses: informational or failing; resolve alpha != 0 inconsistency.
10. CI layout: separate `software.yml` with path filters vs job in `cad.yml`.
11. Enable `strict_tdd` and `verify.test_command`.
12. One SDD change (7-PR chain) vs two changes.
13. Done scope (wave, ripple, stability metric, CI runtime cap).

## Risks

- CAD/software drift if parameters are copied (drift gate mitigates).
- Torque formula disagrees with assembly geometry when alpha != 0.
- Envelope is 12 sampled poses; no coxa sweep or leg-vs-leg check until Phase 3.
- Workspace is narrow; widening the envelope touches frozen CAD and raises `check-fit` cost.
- Provisional servo and body values propagate; software must surface the PROVISIONAL flag.
- Committed generated JSON is a policy exception; record in ADR.
- `repo-structure` "stubs hold no code" scenarios become false; MODIFIED blocks need full requirements.
- `.editorconfig` indent-2 conflicts with ruff's 4-space style.
