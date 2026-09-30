# Design: Kinematics and Gait (Roadmap Phase 2)

## Technical Approach

Approach D from the proposal. OpenSCAD evaluates the real leg assembly libraries and echoes one parameter record. A stdlib-only converter turns it into a committed JSON snapshot. `cad.yml` regenerates it and fails on any difference. The Python package (`software/`, src layout) loads only that snapshot plus clearly flagged PROVISIONAL body placeholders. It holds pure numpy functions in CAD frames, in degrees, with CAD angle names. CAD sources are not modified.

## Architecture Decisions

| # | Topic | Choice | Rejected | Rationale |
|---|---|---|---|---|
| 1 | Exporter | `tools/cad/export-params.scad` includes `asm-leg/asm-leg.scad` and runs one `echo(hexapod_params = [[key, value], ...])` | Text-parsing `params.scad`; editing CAD to emit JSON | Only evaluation yields `cb_zmid`, `tb_zax` and the foot geometry. The echoed kv list is valid JSON |
| 2 | Converter | `tools/cad/echo-to-json.py` (python3 stdlib): requires exactly one `ECHO: hexapod_params = ` line, rejects `undef`/`nan`/`inf` and duplicate keys, writes `json.dumps(indent=2, sort_keys=True)` + newline | awk JSON writer; OpenSCAD string JSON (escaped quotes) | Deterministic bytes, easy to review, and the runner already has python3 |
| 3 | FK golden poses | The exporter also computes the foot centre at the 12 `fit_alpha` x `fit_phi` poses with BOSL2 matrix functions, using the same call chain as `asm_tibia_frame` | Trusting the hand-derived FK | Python FK is tested against CAD-evaluated points (1e-3 mm). The duplicated chain is marked with a comment that points to `asm-leg.scad` |
| 4 | Drift gate | `make check-params` writes `build/params/leg-params.json` and runs `diff -u` against the committed file. `make params` updates the committed file. `gate-test` proves the gate fires by using a `-D` override | `git diff` on a regenerated working tree | No working-tree mutation and no git dependency. Runs locally the same way |
| 5 | Snapshot location | `software/src/hexapod/data/leg-params.json`, loaded with `importlib.resources` | Top-level `params/` | Package data. The loader does not depend on paths |
| 6 | Python toolchain | `python3.12 -m venv software/.venv`, `pip install -e 'software[dev]'` with exact pins in `pyproject.toml`, `mypy --strict`, ruff check + format | uv | Nothing to install beyond CPython. Pins give reproducibility. Switching to uv later is cheap |
| 7 | CI layout | Separate `software.yml` **without path filters** (always runs, about 1 min) | Path filters; job inside `cad.yml` | Avoids required checks that stay pending. Matches `cad.yml`, which has no filters either |
| 8 | IK branch | Knee-up (`q2 = -acos(c)`), outward coxa (`r > 0`). Geometric infeasibility raises `UnreachableError`. Limits are checked separately | Returning NaN; clamping | Only the knee-up branch intersects the envelope (`phi` in [-15, 45] means `q2` in [-105, -45]). Callers decide how to handle violations |
| 9 | Legs | Six identical, unmirrored legs (lateral offset `d` is the same in every leg frame) | Mirrored left/right builds | CAD models one leg. Mirroring would be a Phase 3 CAD decision |
| 10 | Gait | One engine; `GaitSpec` is data; tripod, wave and ripple are constants | One class per gait | Required by the proposal. Adding a new gait adds no code |

## Frames and Maths (leg)

Leg frame L: origin on the coxa axis, at the coxa frame plane. +Z up. +X radial out when `theta = 0`. +Y along the femur axis. All angles are in degrees.

- `theta`: coxa yaw, counter-clockwise about +Z (right-hand rule). `alpha`: femur pitch, knee up is positive. `phi`: knee angle relative to the femur. The tibia angle from vertical is `alpha + phi`.
- Exported constants: `a = coxa_l` (30), `zf = cb_zmid` (23.1), `f = femur_l` (55), `t = tibia_l + ft_floor - ft_r` (86), `d = leg_lane_dy - tb_zax` (-1.3), `ft_r` (8).
- Derived from `asm_tibia_frame` + foot placement (BOSL2 `yrot(a)` is the right-handed rotation about Y):

```
r(alpha,phi) = a + f cos(alpha) + t sin(alpha+phi)
FK: p = Rz(theta) [r, d, zf + f sin(alpha) - t cos(alpha+phi)]
Neutral check: q = (0,0,0) gives (85, -1.3, -62.9)
```

- IK for target `p = (x, y, z)`, the foot-sphere centre:
  1. `rho = hypot(x, y)`. If `rho <= |d|`, raise `UnreachableError(LATERAL)`.
  2. `r = sqrt(rho^2 - d^2)`, `theta = atan2(y, x) - atan2(d, r)`, wrapped to (-180, 180].
  3. `u = r - a`, `w = z - zf`, `c = (u^2 + w^2 - f^2 - t^2) / (2 f t)`. If `|c| > 1 + 1e-9`, raise `UnreachableError(TOO_FAR | TOO_CLOSE)`. Otherwise clamp `c`.
  4. `q2 = -acos(c)`, `phi = 90 + q2`, `alpha = atan2(w, u) - atan2(t sin q2, f + t cos q2)`.
- Limits: `alpha` in [min, max] of `fit_alpha` = [-30, 30]; `phi` in [min, max] of `fit_phi` = [-15, 45]; `theta` in ±45 (PROVISIONAL). Servo inclusion: `max|limit| <= range_deg / 2` for each joint. Neutral = 0 is assumed.

### Placeholder verification (hand-computed; PR 3/6 tests MUST re-assert)

The foot-contact plane sits 60 mm below the coxa frame, so the foot centre is at `z = -52`. Neutral target: `(100, d, -52)`.

| Check | Result |
|---|---|
| Neutral stance IK | `theta = 0`, `alpha ≈ 9.9°`, `phi ≈ 0.7°`: **inside the envelope** |
| Radial reach on the ground at `z = -52` | about 78 to 137 mm (`phi >= -15` sets the inner bound, `phi <= 45` the outer). 100 mm is inside |
| Maximum lift at `rho = 100` | about 19.7 mm (bound by `phi >= -15`) |
| Stride 40 / lift 15 (front and rear legs) | **Violates** `phi` (about -15.6°) early in swing near the inner end |
| Stride 30 / lift 10 | Feasible for all six legs (spot-checked) |

Mount radius 80 mm puts the tripod feet on a radius of about 180 mm. The static margin is about 90 minus half the stride, so it is positive. **Default gait parameters: `step_length = 30`, `step_height = 10`.** The binding constraint is `phi_min = -15°`. Raising the stance height to 70 mm increases lift headroom. That is a tunable placeholder, not a CAD change.

## Data Flow

```
params.scad + asm-leg.scad ─┐
tools/cad/export-params.scad ┴─openscad (scad macro, warnings gate)─> build/params/hexapod-params.echo
   ─python3 echo-to-json.py─> build/params/leg-params.json
        ├─ make params ──────> software/src/hexapod/data/leg-params.json (committed)
        └─ make check-params ─ diff -u ─> fail "params snapshot drift" (cad.yml)

leg-params.json ─load_params()─> Params ─┬─ leg.fk / leg.ik / limits
BodyLayout (PROVISIONAL) ────────────────┴─ body.leg_targets ─> gait.run(GaitSpec) ─> Frames
Frames ─> stability.margin, limits.violations ─> report.md + viz PNGs (build/software/)
```

## Snapshot Schema (v1)

Top-level keys (sorted): `schema_version: 1`, `generator` (`tools/cad/export-params.scad`), `license` (`CC-BY-SA-4.0`), `provisional` (servo flag), `leg` {`tier`, `coxa_l`, `femur_l`, `tibia_l`, `leg_lane_dy`, `cb_zmid`, `tb_zax`, `ft_r`, `ft_floor`, `knee_to_foot`, `foot_dy`}, `limits` {`fit_alpha`, `fit_phi`}, `servo` {`name`, `provisional`, `range_deg`, `pulse_us`, `mass_kg`, `stall_kgcm`, `v_nom`}, `torque` {`supply_v`, `n_servo`, `link_g_per_mm`, `m_body_kg`, `k_dyn`, `derate_static`, `derate_peak`}, `fk_golden` [[alpha, phi, x, y, z] x 12].

The loader requires `schema_version == 1` and every key listed above, and ignores unknown keys. Removing, renaming or changing the meaning of a key bumps the version. `Params.provisional` is the OR of the servo flag and `BodyLayout.provisional`. Every report and plot title shows `PROVISIONAL` while it is true.

## Interfaces (package `hexapod`, `software/src/hexapod/`)

```python
# params.py
def load_params(path: Path | None = None) -> Params            # Params: leg: LegGeometry, limits, servo, torque, fk_golden
# leg.py
@dataclass(frozen=True) class JointAngles: theta: float; alpha: float; phi: float
def fk(q: JointAngles, g: LegGeometry) -> FloatArray             # shape (3,), foot-sphere centre, leg frame
def ik(p: ArrayLike, g: LegGeometry) -> JointAngles              # raises UnreachableError(reason)
# limits.py
@dataclass(frozen=True) class JointLimits: ...; def violations(self, q) -> list[Violation]
def servo_range_ok(lim: JointLimits, range_deg: float) -> bool
# body.py   BodyLayout(mount_radius=80, mount_angles=30+60k, stance_height=60, reach=100, theta_limit=45, provisional=True)
@dataclass(frozen=True) class BodyPose: x, y, z, roll, pitch, yaw   # R = Rz(yaw) Ry(pitch) Rx(roll)
def neutral_feet(layout, g) -> FloatArray                        # (6,3) world contact points
def leg_targets(pose, feet_world, layout, g) -> FloatArray       # (6,3) leg-frame foot centres
# gait.py
@dataclass(frozen=True) class GaitSpec: name; duty: float; offsets: tuple[float, ...6]; step_length=30; step_height=10; heading=0
TRIPOD, WAVE, RIPPLE
def run(spec, layout, params, samples=120) -> list[Frame]        # Frame: s, stance mask, feet, q, violations, margin
# stability.py
def margin(stance_xy: FloatArray, com_xy=(0, 0)) -> float        # signed distance to hull edge; -inf if < 3 feet
# report.py / viz.py / __main__.py: python -m hexapod report|plot --out build/software
```

Body frame B: origin at the body centre on the coxa plane. +X forward, +Y left, +Z up. Leg k (k = 0..5, where 0 is left-front and the count goes counter-clockwise) is mounted at `psi_k = 30 + 60k`, `m_k = 80 (cos psi_k, sin psi_k, 0)`, and its frame is rotated by `Rz(psi_k)`. The world ground is `z = 0` and the neutral body sits at `z = 60`. The leg target is `Rz(-psi_k)(R^T(f_w + [0, 0, ft_r] - p_body) - m_k)`.

Gait: `s_k = (s + offset_k) mod 1`. In stance (`s_k < duty`, `u = s_k / duty`) the foot moves by `-L (u - 0.5)` along the heading. In swing (`u = (s_k - duty) / (1 - duty)`) the foot moves `-(L/2) cos(pi u)` along the heading and lifts by `h sin(pi u)`. Offsets with leg order [LF, LM, LR, RR, RM, RF]:

| Gait | duty | offsets |
|---|---|---|
| tripod | 1/2 | 0, 1/2, 0, 1/2, 0, 1/2 |
| wave | 5/6 | 5/6, 4/6, 3/6, 0, 1/6, 2/6 |
| ripple | 2/3 | 2/3, 1/3, 0, 1/2, 5/6, 1/6 |

Stability margin: the static margin, with the centre of mass at the body origin (PROVISIONAL). The support polygon is the convex hull of the stance contact points (monotone chain, numpy only, no scipy).

## File Changes

| File | Action | PR |
|---|---|---|
| `docs/adr/0005-software-tooling-and-parameter-bridge.md`, `docs/adr/README.md` | Create / Modify | 1 |
| `software/pyproject.toml`, `software/src/hexapod/__init__.py`, `software/tests/test_smoke.py`, `software/README.md` | Create / Modify | 1 |
| `Makefile` (`software`, later `params`, `check-params`, `software-report`, gate-test line), `.editorconfig` (`[*.py]` indent 4), `.gitignore` (`.venv`, `__pycache__`, `.mypy_cache`) | Modify | 1, 2, 7 |
| `.github/workflows/software.yml` | Create (artifact step in PR 7) | 1, 7 |
| `openspec/config.yaml` (`strict_tdd: true`, runner pytest, `apply.tdd: true`, `test_command: make software`, verify `make software gate-test`) | Modify | 1 |
| `tools/cad/export-params.scad`, `tools/cad/echo-to-json.py`, `.github/workflows/cad.yml` (Params drift step after Doctor), `software/src/hexapod/{params.py,data/leg-params.json}` | Create / Modify | 2 |
| `software/src/hexapod/{leg,limits}.py`, `docs/adr/0006-leg-frames-and-joint-conventions.md` | Create | 3 |
| `software/src/hexapod/body.py` | Create | 4 |
| `software/src/hexapod/gait.py` | Create | 5, 6 |
| `software/src/hexapod/stability.py` | Create | 6 |
| `software/src/hexapod/{viz,report,__main__}.py` | Create | 7 |

## PR Chain and Tests

| PR | Est. authored lines | Tests (RED first, strict TDD) |
|---|---|---|
| 1 Scaffold | 260-300 | Smoke test imports `hexapod`. `make software` passes ruff, format check, mypy and pytest |
| 2 Params bridge | 300-340 (+~90 generated, excluded) | Loader: version, missing key, unknown key, provisional flag. Converter: 0 or 2 echo lines, `undef`, duplicate key. `gate-test` shows drift firing |
| 3 Leg FK/IK + limits + ADR-0006 | 350-390 | FK equals `fk_golden` (12 poses, 1e-3 mm). IK(FK(q)) equals q at the grid. Unreachable reasons. Theta wrap. Servo inclusion. Neutral placeholder inside limits |
| 4 Body | 250-300 | Identity pose returns the neutral targets. Pure translation and yaw round-trips. The six mount angles. The PROVISIONAL flag |
| 5 Engine + tripod | 300-360 | Phase wrap. Stance/swing boundaries. Continuous foot path. Tripod: 3 stance feet at every sample. All samples within limits |
| 6 Wave, ripple, stability | 200-260 | Hull margin on known triangles and squares. Negative margin with < 3 feet. Each gait has margin > 0 and no violations. Stride 40 / lift 15 is reported as a violation |
| 7 Visualiser, report, artifact | 320-370 | Agg backend writes PNGs. The report lists limit and torque rows (CAD formula, `alpha != 0` caveat) and the PROVISIONAL banner. CLI exit codes |

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | Maths, loader, engine, margin | pytest + numpy.testing, and parametrised grids |
| Integration | CAD parity | `fk_golden` from OpenSCAD compared with Python FK; drift gate in `cad.yml` |
| E2E | Report pipeline | `python -m hexapod report` in CI, uploaded as an artifact (14 days) |

## Threat Matrix

| Boundary | Applicability |
|---|---|
| Documentation-like paths | N/A: nothing classifies or executes files by path; `pyproject.toml` is ordinary config |
| Git repository selection | N/A: the drift gate uses `diff`, not git |
| Commit state / Push state / PR commands | N/A: no VCS or PR automation |

## ADR Outlines

- **0005 Software tooling and parameter bridge**: context (drift risk, text parsing is incomplete). Decision: Python 3.12, pinned toolchain, evaluated export, and a committed generated JSON as a **policy exception** (the only committed build output, byte-checked in CI, CC-BY-SA data inside an MIT tree). Alternatives A, B, C and uv. Consequences: CAD edits need `make params`; software never reads `.scad`.
- **0006 Leg frames and joint conventions**: frames L and B, signs, units (mm and degrees), the 86 mm foot centre, `d = -1.3`, the knee-up branch, the limit policy (hard envelope + servo inclusion), and the PROVISIONAL placeholders. Consumed by Phase 5 servo mapping.

## Migration / Rollout

No migration required. PRs merge in order 1 to 7 (a feature-branch chain). Rollback reverts them in reverse order. CAD sources are untouched. The drift step can be dropped without affecting the CAD gates.

## Open Questions

- [ ] Accept the default stride 30 / lift 10 (or raise the stance height to 70 mm) given the `phi_min` headroom finding.
- [ ] Confirm pip + venv (not uv) and `mypy --strict`. These were left open in the exploration and not covered by the confirmed decisions.
