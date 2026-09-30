# Tasks: Kinematics and Gait (Roadmap Phase 2)

Strict TDD: each PR writes RED tests first, then GREEN, then refactor. Defaults confirmed: stride 30 mm, lift 10 mm, stance 60 mm (not 70); pip + venv, `mypy --strict`.

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1980-2320 authored (+~90 generated JSON, excluded) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → 2 → 3 → 4 → 5 → 6 → 7 |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending (design proposes feature-branch-chain) |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | PR (est. lines) | Focused test | Runtime harness | Rollback |
|------|------|-----------------|--------------|-----------------|----------|
| 1 | Scaffold, ADR-0005, config | PR 1 (260-300) | `make software` | CI `software.yml` run | Revert PR 1 |
| 2 | Params bridge + drift gate | PR 2 (300-340) | `pytest software/tests/test_params.py test_echo_to_json.py` | `make check-params gate-test` | Revert PR 2 |
| 3 | Leg FK/IK, limits, ADR-0006 | PR 3 (350-390) | `pytest software/tests/test_leg.py test_limits.py` | N/A (pure maths) | Revert PR 3 |
| 4 | Body layout and targets | PR 4 (250-300) | `pytest software/tests/test_body.py` | N/A | Revert PR 4 |
| 5 | Gait engine + tripod | PR 5 (300-360) | `pytest software/tests/test_gait.py` | N/A | Revert PR 5 |
| 6 | Wave, ripple, stability | PR 6 (200-260) | `pytest software/tests/test_stability.py test_gait_all.py` | N/A | Revert PR 6 |
| 7 | Visualiser, report, artifact | PR 7 (320-370) | `pytest software/tests/test_report.py test_viz.py` | `python -m hexapod report --out build/software` | Revert PR 7 |

Base boundary (if feature-branch-chain): PR 1 base = tracker branch; PR N base = PR N-1 branch.

## PR 1: Scaffold (specs: software-tooling, repo-structure, repo-hygiene)

- [x] 1.1 RED: `software/tests/test_smoke.py` imports `hexapod` (fails, no package).
- [x] 1.2 Create `software/pyproject.toml` (py3.12, numpy; pinned dev: pytest, ruff, mypy, matplotlib) and `software/src/hexapod/__init__.py`.
- [x] 1.3 Add `make software` (venv, ruff check, format check, `mypy --strict`, pytest) to `Makefile`.
- [x] 1.4 Edit `.editorconfig` (`[*.py]` indent 4) and `.gitignore` (`.venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`; snapshot not ignored).
- [x] 1.5 Create `.github/workflows/software.yml` (no path filters, Python 3.12, `permissions: contents: read`).
- [x] 1.6 Update `software/README.md`.
- [x] 1.7 Write `docs/adr/0005-software-tooling-and-parameter-bridge.md`; index in `docs/adr/README.md`.
- [x] 1.8 Edit `openspec/config.yaml`: `strict_tdd: true`, pytest runner, `apply.tdd: true`, `verify.test_command: make software gate-test`.

## PR 2: Params bridge (specs: params-bridge, ci)

- [ ] 2.1 RED: `software/tests/test_echo_to_json.py` (0 or 2 echo lines, `undef`/`nan`/`inf`, duplicate key, deterministic bytes).
- [ ] 2.2 RED: `software/tests/test_params.py` (valid load, schema_version, missing key `fit_phi`, unknown key ignored, provisional OR, non-numeric, missing file).
- [ ] 2.3 Create `tools/cad/echo-to-json.py` (stdlib).
- [ ] 2.4 Create `tools/cad/export-params.scad` (params echo + 12 `fk_golden` poses).
- [ ] 2.5 Add `make params` and `make check-params` (`diff -u`, "params snapshot drift").
- [ ] 2.6 Generate `software/src/hexapod/data/leg-params.json`; create `software/src/hexapod/params.py`.
- [ ] 2.7 Extend `gate-test` in `Makefile` with a `-D` override proving `check-params` fails (gate-test proof that drift fires).
- [ ] 2.8 Add drift step after `check-fit` in `.github/workflows/cad.yml`.

## PR 3: Leg kinematics (specs: leg-kinematics)

- [ ] 3.1 RED: `software/tests/test_leg.py`: FK equals `fk_golden` (1e-3 mm); IK(FK(q)) within 1e-6 deg on the 12-pose grid; zero pose; -1.3 mm offset; unreachable reasons; theta wrap.
- [ ] 3.2 RED: `software/tests/test_limits.py`: within limits (30/45/0), phi=60 gives 15 deg violation, servo inclusion failure names the joint.
- [ ] 3.3 RED: placeholder feasibility re-assert: target (100, -1.3, -52) gives theta 0, alpha ~9.9 deg, phi ~0.7 deg, inside limits.
- [ ] 3.4 Create `software/src/hexapod/leg.py` (fk, ik, `JointAngles`, `UnreachableError`) and `limits.py`.
- [ ] 3.5 Write `docs/adr/0006-leg-frames-and-joint-conventions.md`; index it.
- [ ] 3.6 Refactor; no CAD literals in `src` (grep check).

## PR 4: Body kinematics (specs: body-kinematics)

- [ ] 4.1 RED: `software/tests/test_body.py`: six mount points at 80 mm / 30+60k; identity gives identical targets (100 mm reach, 60 mm below coxa); X translation and yaw round-trips; PROVISIONAL flag; infeasible leg flagged, others independent.
- [ ] 4.2 Create `software/src/hexapod/body.py` (`BodyLayout`, `BodyPose`, `neutral_feet`, `leg_targets`, per-leg reachability).

## PR 5: Gait engine and tripod (specs: gait-engine)

- [ ] 5.1 RED: `software/tests/test_gait.py`: periodicity phase 0 vs 1; stance foot fixed; continuous path; tripod >= 3 stance feet; no violations at defaults; stride 40 / lift 15 yields violations as data.
- [ ] 5.2 Create `software/src/hexapod/gait.py` (`GaitSpec`, `run`, `Frame`, `TRIPOD`; defaults step_length 30, step_height 10).
- [ ] 5.3 Re-assert stride 30 / lift 10 stays within limits for all six legs.

## PR 6: Wave, ripple, stability (specs: gait-engine)

- [ ] 6.1 RED: `software/tests/test_stability.py`: hull margin on triangle and square; negative with < 3 feet; unsupported flag.
- [ ] 6.2 RED: `software/tests/test_gait_all.py`: support counts (tripod 3, wave 5, ripple 4); margin > 0 and no violations; re-assert stride 30 / lift 10 feasible and neutral IK alpha ~9.9, phi ~0.7.
- [ ] 6.3 Create `software/src/hexapod/stability.py`; add `WAVE`, `RIPPLE` to `gait.py`; wire margin into `Frame`.

## PR 7: Visualiser, report, artifact (specs: software-tooling, ci)

- [ ] 7.1 RED: `software/tests/test_viz.py` (Agg, non-empty PNG, PROVISIONAL marked) and `test_report.py` (limit margins, torque rows, alpha != 0 caveat, PROVISIONAL banner, torque warning exit 0, CLI exit codes).
- [ ] 7.2 Create `software/src/hexapod/{viz,report,__main__}.py`.
- [ ] 7.3 Add `software-report` target to `Makefile`; upload PNG and report in `software.yml` (retention 14 days).
- [ ] 7.4 Final `make software gate-test check-params`; update `software/README.md`.
