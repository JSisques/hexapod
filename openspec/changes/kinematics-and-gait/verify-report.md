```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:2a929971c81377e6aca6a5b057a9d047ee170d99d77fc3066f16d3753f7cea22
verdict: fail
blockers: 1
critical_findings: 1
requirements: 24/29
scenarios: 48/53
test_command: make software gate-test check-params PYTHON=python3
test_exit_code: 0
test_output_hash: sha256:87fd7e1f56f5e76381dc256a770ee369eeeb69692e7254934dfae6a314736cdc
build_command: make stl render
build_exit_code: 0
build_output_hash: sha256:2898b0e9a5786a674b9e9e0d091534d0607dfbfcecb8ec00e02f32150d944210
```

## Verification Report

**Change**: kinematics-and-gait
**Branch**: feat/kinematics-7-viz-report (PR #26, tip of chain PR #19..#26), 9 commits ahead of main
**Mode**: Strict TDD (pytest, ruff, mypy --strict)

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 34 (PR1 8, PR2 8, PR3 6, PR4 2, PR5 3, PR6 3, PR7 4) |
| Tasks complete | 34 |
| Tasks incomplete | 0 |
| Delta specs | 8 (29 requirements, 53 scenarios) |

### Build & Tests Execution
`make software gate-test check-params PYTHON=python3`: exit 0. ruff check pass; ruff format 22 files clean; mypy strict 21 source files no issues; pytest 115 passed in 3.85 s (Python 3.14.7, not 3.12); gate-test warnings/torque/bed/fit/params-drift all OK; check-params OK.
`make stl render`: exit 0 (build_command from openspec/config.yaml).
`make software-report PYTHON=python3`: exit 0; wrote tripod.png, wave.png, ripple.png, report.md to build/software.
`make firmware`: prints "not implemented", make exit 2 (recipe exit 1). `make help`: exit 0, lists targets.
`git check-ignore software/.pytest_cache/x`: ignored (.gitignore:18). `git check-ignore` on `software/src/hexapod/data/leg-params.json`: not ignored.
Coverage: not available (config `coverage: false`). Python 3.12 not installed locally; CI pins 3.12.

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD evidence reported | Yes | "TDD Cycle Evidence" table for each of PR 1..7 in apply-progress.md |
| All tasks have tests | Yes | code tasks map to 11 test files; config/CI/docs tasks marked N/A |
| RED confirmed | Yes | every test file named in the RED column exists; RED entries record collection errors (ModuleNotFoundError) |
| GREEN confirmed | Yes | 115/115 pass on my run, matches the 115 reported for PR 7 |
| Triangulation adequate | Yes | parametrised grids (12 poses, 5 thetas, 3 gaits) |
| Safety net | Warning | PR 3+ modify Makefile/config etc. but no "safety net" column is reported (table format has no such column); not blocking |

Test layers: all unit (115 tests, 11 files, pytest); integration is CAD parity via `fk_golden` plus `gate-test`/`check-params` (Make-driven). No E2E tool configured.

Assertion quality: no tautologies, no ghost loops (loops in test_gait/test_gait_all iterate over non-empty `run()` output, guarded by `min(...)`/`len` asserts). Weak spots: `test_periodicity_phase_0_equals_phase_1` is near-tautological because `frame_at` does `s %= 1.0` (SUGGESTION); `test_torque_warning_is_informational` never checks an exit status (see W2).

### Spec Compliance Matrix
Status legend: C = compliant (passing runtime test or gate run); C(s) = compliant by static inspection of config/docs where no runtime exists; P = partial; F = fails/contradicted.

| Capability / Requirement | Scenario | Evidence | Result |
|---|---|---|---|
| body-kinematics / Provisional layout | Mount positions | test_body.py:35 `test_mount_points_at_80_mm_and_30_plus_60k`; body.py:22-26 | C |
| body / Body pose to leg targets | Neutral pose | test_body.py:48 `test_identity_pose_gives_identical_targets` | C |
| body / Body pose to leg targets | Body translation | test_body.py:54 `test_x_translation_shifts_targets_oppositely_in_each_leg_frame` | C |
| body / Reachability report | Infeasible pose | test_body.py:85 `test_infeasible_leg_is_flagged_and_others_stay_independent`; :93 limit case | C |
| ci / Canonical build (MOD) | Warning fails CI | `make gate-test`: "warnings OK" | C |
| ci / Canonical build | Interference fails CI | `make gate-test`: "fit OK" (cad.yml:31-32 runs check-fit) | C |
| ci / Canonical build | Step order | cad.yml:29-34: gate-test, check-fit, Params drift, TOOLCHAIN=docker at job level | C(s) |
| ci / Canonical build | Snapshot drift fails CI | `make gate-test`: "params drift OK" (`-D k_dyn=1.6` forces diff, exit non-zero) | C |
| ci / Software workflow | PR triggers run | software.yml:4-7 pull_request, push main, no path filters | C(s) |
| ci / Software workflow | Failing test fails CI | software.yml:26-27 `make software` (make propagates ruff/mypy/pytest exit); CI run not observed | P |
| ci / Software artifacts | Artifacts uploaded | software.yml:28-40 (png + report.md, retention-days 14, if-no-files-found error); paths exist after `make software-report`; run page not observable locally | P |
| gait-engine / Phase engine | Periodicity | test_gait.py:21 (near-trivial, see suggestion) | C |
| gait / Phase engine | Stance foot fixed | test_gait.py:27 asserts the stance foot MOVES at constant speed (frame is body-fixed); spec says world position unchanged | F |
| gait / Gait definitions | Support count | test_gait_all.py:41 min grounded 3/5/4 over 600 samples | C |
| gait / Stability margin | Positive margin | test_gait_all.py:48 all margins > 0, 3 gaits | C |
| gait / Stability margin | Unsupported | test_gait_all.py:68; test_stability.py:30,37 | C |
| gait / Limit compliance | Default cycles feasible | test_gait.py:66; test_gait_all.py:48,75 | C |
| gait / Limit compliance | Excess step length | test_gait.py:76 (stride 40/lift 15 -> phi violations by leg, phase `Frame.s`, joint); test_report.py:45 | C |
| gait / Torque informational | Torque above stall | test_report.py:50 warning text present; exit status only asserted for default (no-warning) run at :58 | P (see W2) |
| leg-kinematics / Conventions | Zero pose | test_leg.py:24 (85, -1.3, -62.9) | C |
| leg / Forward kinematics | Offset applied | test_leg.py:13 (12 CAD golden poses, 1e-3), :28 | C |
| leg / Inverse kinematics | Round trip on the grid | test_leg.py:19 (12 poses, 1e-6 deg), :33 | C |
| leg / Inverse kinematics | Unreachable target | test_leg.py:51 three reasons (`UnreachableError`) | C |
| leg / Joint limits | Within limits | test_limits.py:15 | C |
| leg / Joint limits | Violation reported | test_limits.py:19 (phi 60 -> 15 deg) | C |
| leg / Joint limits | Servo inclusion | test_limits.py:30,34 (`servo_range_failures` names joint) | C |
| params-bridge / Parameter export | Export is reproducible | test_echo_to_json.py:71 (converter bytes); `check-params` regenerates from scratch and diff is empty, gate-test runs it again | C |
| params / Parameter export | Derived values present | test_params.py:25 (coxa_l, knee_to_foot 86, foot_dy -1.3) | C |
| params / Committed snapshot | Software reads the snapshot only | `rg '86|1\.3|fit_alpha|fit_phi|23\.1'` over src: only field names in params.py/limits.py; no automated guard test | C(s) |
| params / Drift gate | Stale snapshot fails | gate-test "params drift OK" | C |
| params / Drift gate | Fresh snapshot passes | `check-params: OK` | C |
| params / Loader | Valid load | test_params.py:25 | C |
| params / Loader | Missing key | test_params.py:44 (names `fit_phi`) | C |
| repo-hygiene / Editor conventions (MOD) | Config present | .editorconfig: `root = true`, `[{Makefile,*.mk}]` tab | C(s) |
| repo-hygiene / Editor conventions | Python indentation | .editorconfig `[*.py] indent_size = 4`; indent_style=space inherited from `[*]` (see S3) | C(s) |
| repo-hygiene / Makefile entry point (MOD) | Default goal lists targets | `make help` exit 0 | C |
| repo-hygiene / Makefile entry point | Placeholder target | `make firmware`: "not implemented", exit 2 | C |
| repo-hygiene / Makefile entry point | CAD targets are real | `make stl render` exit 0; clean recipe `rm -rf build` (not run) | C |
| repo-hygiene / Makefile entry point | Software target is real | `make software` ran ruff, mypy, pytest | C |
| repo-hygiene / Python artifacts ignored | Cache ignored | `git check-ignore` reports it | C |
| repo-hygiene / Python artifacts ignored | Snapshot tracked | `git check-ignore` empty for leg-params.json | C |
| repo-structure / Per-directory README (MOD) | README in each directory | firmware/README.md, software/README.md present | C(s) |
| repo-structure / Per-directory README | Firmware stub holds no code | `fd -t f . firmware`: README.md only | C |
| repo-structure / Per-directory README | Software may hold Python | software/ tracks README, pyproject, src, tests | C |
| repo-structure / Deferred scope (MOD) | No deferred artifacts | firmware only README; no body/electronics files | C |
| repo-structure / Deferred scope | Only permitted CAD sources | diff vs main touches no hardware/cad files | C |
| repo-structure / Deferred scope | Shared params permitted | no new params.scad | C |
| repo-structure / Deferred scope | Only permitted tooling files | tools/cad adds echo-to-json.py and export-params.scad (see S4) | C(s) |
| software-tooling / Project layout | Toolchain installs | venv install worked on Python 3.14.7; 3.12 not exercised locally | P |
| software-tooling / Quality gate | Failure propagates | Makefile recipe lines run sequentially; no failing-case run performed | P |
| software-tooling / Headless visualiser | Render without display | test_viz.py:14,23 (Agg canvas, PNG magic, >5 kB) | C |
| software-tooling / Pose report | Report content | test_report.py:33 (margins, torque rows, PROVISIONAL, known issue) | C |
| software-tooling / Decision record and SDD config | Config enabled | config.yaml `strict_tdd: true`, `verify.test_command: make software gate-test` | C(s) |

**Compliance summary**: 48/53 (C and C(s) together, 4 P, 1 F). Requirements 24/29 fully compliant.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|---|---|---|
| Leg FK/IK, limits | Implemented | leg.py, limits.py match ADR-0006 maths; IK returns typed error, no NaN |
| Params bridge | Implemented | exporter, converter, snapshot (150 lines, `provisional: ["servo"]`), loader, drift gate |
| Body layout/targets | Implemented | body.py matches design formula |
| Gait engine | Implemented with a frame caveat | see C1 |
| Stability margin | Implemented | convex hull, `-inf` for unsupported |
| Visualiser / report / CLI | Implemented | exit 0 for findings, 1 load failure, 2 usage |
| CI | Implemented | cad.yml drift step after check-fit; software.yml with artifact upload |

### Coherence (Design)
| Decision | Followed? | Notes |
|---|---|---|
| 1-5 exporter, converter, golden poses, drift gate, snapshot location | Yes | |
| 6 pip + venv, mypy --strict | Yes | |
| 7 software.yml without path filters | Yes | |
| 8 knee-up IK, `UnreachableError`, limits separate | Yes | |
| 9 six unmirrored legs | Yes | |
| 10 single engine, gaits as data | Yes | |
| Interface `servo_range_ok -> bool` | Deviation | became `servo_range_failures -> list[Violation]` (documented in apply-progress; matches spec better) |
| `Params.provisional` = OR with BodyLayout | Deviation | Params has no layout; `body.is_provisional(params, layout)` (documented) |
| Snapshot `provisional` = servo flag | Deviation | list of names plus `servo.provisional` bool per params-bridge spec (documented); design text stale |
| `BodyLayout(..., theta_limit=45)` | Deviation | theta limit lives in `limits.THETA_LIMIT`; layout has no `theta_limit` field |
| Stance foot moves in the body-fixed frame | Conflicts with spec | see C1 |
| ADR-0006 conventions vs code | Yes | frames, signs, knee-up branch, `servo_range_failures`, neutral (100,-1.3,-52) -> alpha 9.876, phi 0.721 all match |

### Archive readiness of the deltas
- ci MODIFIED "Canonical build": carries the full requirement text and all scenarios (3 existing rewritten + "Snapshot drift fails CI"); replaces the main block cleanly.
- repo-hygiene MODIFIED "Editor conventions" and "Makefile entry point": full text, all main scenarios preserved plus new ones; clean.
- repo-structure MODIFIED "Per-directory README" and "Deferred scope excluded": full text; the rename "Stubs hold no code" -> "Firmware stub holds no code" replaces a scenario name (acceptable, whole block replaced).
- ADDED requirements (ci Software workflow/Software artifacts, hygiene Python artifacts ignored) do not collide with existing main names.
- Main `openspec/specs/ci/spec.md` line 40-41 lacks a blank line before `### Requirement: Artifacts`. Header-based merging is unaffected because the delta does not touch "Artifacts", but a line-oriented merge would leave the malformed spacing (see S1).
- New capabilities (body-kinematics, gait-engine, leg-kinematics, params-bridge, software-tooling) have no main spec yet; archive copies them as new.
- Delta wording in repo-structure "Only permitted tooling files" says "the params exporter source" (singular); tree has two files (see S4).

### Issues Found
**CRITICAL**
- C1. gait-engine / Phase engine / scenario "Stance foot fixed" ("its world foot position is unchanged") is contradicted by the implementation and its own test. `frame_at` moves a stance foot by `-L(u-0.5)` in the body-fixed frame (gait.py:59-65; design.md "Gait" paragraph), and `test_stance_foot_is_fixed_relative_to_ground` (test_gait.py:27-34) asserts the foot moves at constant speed. There is no test asserting an unchanged world position. Fix without code: reword the scenario in the delta (for example "stance foot moves backwards in the body frame at constant speed while the body advances, ground contact height unchanged") and rename the test; or model body translation so the world foot is truly fixed. Must be resolved before archive so main spec is not archived with a scenario the suite does not verify.

**WARNING**
- W1. Python 3.12 (the version the spec, ADR and CI pin) was never exercised locally; all runs on 3.14.7. `requires-python >=3.12` and ruff/mypy target 3.12 mitigate. Confirm on the CI run of PR #26.
- W2. Spec "Torque above stall ... exit status stays 0": no test drives the CLI with a warning-producing snapshot. Exit 0 is guaranteed by `main()` code (no path returns non-zero for findings) but is not test-covered. Add a CLI test with an override snapshot (`--params` with high `k_dyn`).
- W3. "Failure propagates", "Toolchain installs" and CI-only scenarios (failing test fails CI, artifacts on run page) rest on Makefile/YAML inspection; confirm on the PR #26 CI run.
- W4. ADR-0005 decision item 4 still says "The bridge itself lands in a later PR of this change"; the bridge is now shipped. Stale sentence.
- W5. Design.md not updated for documented deviations (`provisional` list, `servo_range_failures`, `is_provisional`, `theta_limit` field); design Open Questions checkboxes are still unchecked though tasks.md records them as confirmed. Tasks.md still shows "Chain strategy: pending".
- W6. `openspec/config.yaml` `verify.test_command` is `make software gate-test`; it omits `check-params`, which is part of the agreed verification command and success criterion 2.
- W7. No automated guard for "software reads the snapshot only" (params-bridge Committed snapshot); it relies on the one-off `rg` check from task 3.6.

**SUGGESTION**
- S1. Fix the missing blank line before `### Requirement: Artifacts` in `openspec/specs/ci/spec.md` (do it at archive time or in the delta).
- S2. `test_periodicity_phase_0_equals_phase_1` is trivially true because `frame_at` wraps `s %= 1.0`; add a check on the unwrapped formula (for example phase 0.999999 vs 0) for a real continuity signal.
- S3. Add `indent_style = space` explicitly to `[*.py]` so the "sets spaces with indent_size = 4" scenario is literal rather than inherited.
- S4. Reword the repo-structure delta to "the params exporter sources" (echo-to-json.py and export-params.scad).
- S5. PR 2 exceeded the 400-line budget (~490 authored) and was split; apply-progress recommends `size:exception`. Record it on the PR.
- S6. `software/src/hexapod.egg-info` and `__pycache__` are untracked but ignored; fine. `workflow_dispatch` was added to software.yml (not in spec, harmless).

### Verdict
FAIL

One CRITICAL: the "Stance foot fixed" scenario is contradicted by the tested behaviour (spec-text fix or model change needed). Every command passes (test exit 0, 115 tests, all gates OK, build exit 0); all other scenarios are covered or verified by inspection, with 7 warnings and 6 suggestions.
