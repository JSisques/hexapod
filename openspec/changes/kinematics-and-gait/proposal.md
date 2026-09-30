# Proposal: Kinematics and Gait (Roadmap Phase 2)

## Intent

`software/` is a stub. Phase 2 needs tested leg and body kinematics plus gaits that use the CAD leg numbers. Copying those numbers by hand would let CAD and software drift apart.

## Scope

### In Scope
- ADR-0005 covering tooling, parameter sharing and the committed-generated-JSON exception
- Python 3.12 `software/` src layout: pytest, ruff, numpy, mypy
- Params bridge: OpenSCAD evaluates `asm-leg.scad`, writes a committed JSON snapshot, and a drift gate in `cad.yml` checks it
- Offset-aware leg FK/IK (86 mm foot centre, -1.3 mm lateral) in degrees (`alpha`, `phi`, new `theta`)
- Joint limits: hard limit = `fit_alpha`/`fit_phi` envelope; servo `range_deg` as an inclusion check
- Body kinematics on a PROVISIONAL hexagonal layout
- One phase-based gait engine for tripod, wave and ripple, with a stability margin
- Headless matplotlib visualiser; informational limit/torque pose report
- `software.yml` workflow, Makefile `software` target, `.editorconfig` `[*.py]`, config `strict_tdd: true` + `verify.test_command`

### Out of Scope
- Servo-command mapping (Phase 5); physics engine; interactive visualiser
- Fixing the `tau_femur` alpha != 0 inconsistency (recorded as a known issue)
- Widening the CAD envelope, coxa sweep, leg-vs-leg checks (Phase 3)

### PROVISIONAL placeholders (software-only until Phase 3)

| Value | Placeholder |
|---|---|
| Coxa yaw limit `theta` | ±45° |
| Mount radius | 80 mm |
| Mount angles | 30° + k·60° (k = 0..5) |
| Stance height (foot plane below coxa frame) | 60 mm |
| Neutral foot reach from coxa axis | 100 mm |

## Capabilities

### New Capabilities
- `params-bridge`: JSON export, snapshot, drift gate, loader
- `leg-kinematics`: FK/IK, conventions, joint limits
- `body-kinematics`: body pose to per-leg targets, provisional layout
- `gait-engine`: phase engine, tripod/wave/ripple, stability margin
- `software-tooling`: layout, lint/type/test, visualiser and report

### Modified Capabilities
- `repo-structure`: "Per-directory README" and "Deferred scope excluded" allow Python source under `software/`
- `ci`: add a drift-gate step to `cad.yml` and the new `software.yml`
- `repo-hygiene`: `make software` becomes real; `[*.py]` editor rule

## Approach

Use approach D from the exploration. The kinematics code is pure numpy functions in CAD frames and only reads the loaded parameter snapshot. The gait engine is written once and each gait is a parameter set.

## PR Chain (each PR under 400 lines)

| # | Scope |
|---|---|
| 1 | ADR, scaffold, hygiene, `software.yml`, spec deltas, config |
| 2 | Params bridge |
| 3 | Leg FK/IK + limits |
| 4 | Body kinematics |
| 5 | Gait engine + tripod |
| 6 | Wave, ripple, stability |
| 7 | Visualiser, report, CI artifact |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Path filters + required check leave PRs pending | Med | Always-run job or no required status |
| Narrow workspace makes gaits infeasible | Med | Placeholders are tunable; the report shows violations |
| Torque formula wrong when alpha != 0 | Med | Report only; follow-up issue |
| Envelope is only 12 sampled poses | Med | Documented; Phase 3 |
| Provisional values leak into later phases | Low | PROVISIONAL flag shown in output |

## Rollback Plan

Revert each PR in reverse order. CAD sources do not change, so reverting PR 1 restores the stub `software/` and the placeholder `make software`.

## Dependencies

- Pinned OpenSCAD image (for the exporter and drift gate)

## Success Criteria

- [ ] `make software` runs ruff, mypy and pytest, and all pass locally and in CI
- [ ] The drift gate fails when a CAD parameter changes without regenerating the snapshot
- [ ] IK(FK(q)) round-trips at the 12 grid poses
- [ ] Tripod, wave and ripple cycles stay within limits with a positive stability margin
- [ ] The visualiser and report are uploaded as CI artifacts
