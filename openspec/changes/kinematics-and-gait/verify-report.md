```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:b0fc61d13cb7f26fcc3d67b5af986ef32a111ef084a7eb28c5cc4079ace98ccd
verdict: pass
blockers: 0
critical_findings: 0
requirements: 29/29
scenarios: 53/53
test_command: make software gate-test check-params PYTHON=python3
test_exit_code: 0
test_output_hash: sha256:7e0fce57f358170d3f667a48c317e1a9b9b25b11bd5f7d40af2030d64224b71f
build_command: make stl render
build_exit_code: 0
build_output_hash: sha256:337f669f923bf16590877a236c12554f7545825a9d2c390edf3448f428abe624
```

## Verification Report

**Change**: kinematics-and-gait (RE-VERIFY after remediation commit a8914a0)
**Branch**: feat/kinematics-8-verify-fixes (PR #27, top of chain PR #19..#27)
**Mode**: Strict TDD (pytest, ruff, mypy --strict)
**Previous report**: FAIL (1 CRITICAL, 7 WARNING, 6 SUGGESTION)

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 34 (PR1 8, PR2 8, PR3 6, PR4 2, PR5 3, PR6 3, PR7 4) |
| Tasks complete | 34 |
| Tasks incomplete | 0 |
| Delta specs | 8 (29 requirements, 53 scenarios; counted from headings) |

### Build & Tests Execution
- `make software gate-test check-params PYTHON=python3`: exit 0. ruff check pass; ruff format 22 files clean; mypy strict 21 source files no issues; pytest 116 passed in 4.16 s (Python 3.14.7 locally); gate-test warnings/torque/bed/fit/params drift all OK; check-params OK.
- `make stl render`: exit 0 ("Nothing to be done for render", outputs up to date from the previous run).
- Failure propagation probe (detached scratch worktree, nothing in the repo touched): with an added failing test, `make software`: pytest "1 failed, 116 passed", make exit 2 (recipe Error 1). Worktree removed; `git status` clean.
- CI (gh): `gh pr checks 26`: build pass 1m33s, quality pass 39s. `gh pr checks 27`: build pass 1m38s, quality pass 37s. Run 36696295691 (software, PR #27 head): pytest on Python 3.12.14, 116 passed in 4.19 s; steps Quality gate, Pose report and plots, Upload report and plots all success. Artifact `software-report` exists, expires 2026-10-14 (created 2026-09-30, 14 days).
- Coverage: not available (config `coverage: false`).

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD evidence reported | Yes | "TDD Cycle Evidence" tables for PR 1..7; remediation section explains W2 test has no meaningful RED (behaviour pre-existed, guard test) |
| All tasks have tests | Yes | code tasks map to 11 test files; config/CI/docs tasks N/A |
| RED confirmed | Yes | all test files named in RED column exist |
| GREEN confirmed | Yes | 116/116 pass (115 reported for PR 7 plus the 1 test added in remediation) |
| Triangulation adequate | Yes | parametrised grids (12 poses, 5 thetas, 3 gaits) |
| Safety net | Warning | still no safety-net column in the evidence tables (format limitation, not blocking) |

Test layers: all unit (116 tests, 11 files); integration via CAD parity (`fk_golden`) and Make-driven gates. No E2E tool.
Assertion quality: no tautologies or ghost loops. The renamed stance test iterates legs (0, 2, 4) that are asserted stance in the same test, so the loop always runs. `test_periodicity_phase_0_equals_phase_1` remains near-tautological (S2, not addressed).

### Resolution of previous findings
| ID | Status | Evidence |
|----|--------|----------|
| C1 | RESOLVED | Scenario now reads "in the body frame its foot moves backwards along the heading at constant speed and stays at ground height / AND equivalent to a foot fixed in the world while the body advances". `test_stance_foot_moves_backwards_at_constant_speed_in_body_frame` (test_gait.py:27-34) asserts for legs 0, 2, 4 at s = 0.05, 0.15, 0.25: all stance, z == 0 (ground height), equal successive displacements (constant speed), and x displacement equals `0.1/0.5*30` (backwards along +x heading of default). It genuinely covers the reworded first THEN. The AND clause is an equivalence that no engine test models (the engine has no body translation); it is a mathematical corollary, not a separate observable, so it does not need its own test (see N1 for the residual wording issue). |
| W1 | RESOLVED | CI run for PR #27 ran on Python 3.12.14, 116 passed. PR #26 checks also green. |
| W2 | RESOLVED | `test_cli_report_with_torque_warning_still_exits_zero` (test_report.py:75-82) copies the packaged snapshot, sets `torque.k_dyn = 20`, runs `main(["report", "--out", ..., "--params", weak])`, asserts return 0 and that report.md contains "WARNING: torque budget exceeded". Non-vacuous: the warning text assertion proves the warning path was taken. |
| W3 | RESOLVED | Toolchain install and artifact upload confirmed on the CI run (3.12.14 venv install, artifact with 14-day expiry); failure propagation exercised locally (make exit 2 on a failing test) and the workflow step is a plain `make software` without continue-on-error. A red CI run was not provoked. |
| W4 | RESOLVED | ADR-0005 item 4 now says "The bridge ships in this change: exporter, converter, committed snapshot, loader and drift gate." |
| W5 | RESOLVED | design.md back-ported (git show a8914a0: 12 lines), Open Questions no longer show unchecked boxes (rg for `[ ]` in design.md and tasks.md: none), tasks.md Chain strategy = feature-branch-chain. |
| W6 | RESOLVED | openspec/config.yaml line 50 `test_command: "make software gate-test check-params"`. |
| W7 | OPEN (not addressed, stays WARNING) | No automated guard that software never parses CAD literals; relies on the one-off task 3.6 `rg` check. |
| S1 | OPEN | main `openspec/specs/ci/spec.md` still lacks a blank line before `### Requirement: Artifacts` (line 40-41). Fix at archive. |
| S2 | OPEN | Periodicity test still trivial due to `s %= 1.0`. |
| S3 | RESOLVED | `.editorconfig` `[*.py]` now has `indent_style = space` and `indent_size = 4` (lines 14-16). |
| S4 | RESOLVED | repo-structure delta says "the params exporter sources" in requirement text and scenario; tree has 2 exporter files (echo-to-json.py, export-params.scad) plus 2 awk scripts, no fixtures added. |
| S5 | RESOLVED with note | PR 2 split into 2a/2b and documented in apply-progress and tasks.md. `size:exception` label not needed after the split; PR #27 has no labels (nothing to record). |
| S6 | OPEN, informational | ignored egg-info/__pycache__; `workflow_dispatch` extra trigger. Harmless. |

### Spec Compliance Matrix
Legend: C = compliant (passing runtime test, gate run or observed CI); C(s) = compliant by static inspection of config/docs where no runtime exists.

| Capability / Requirement | Scenario | Evidence | Result |
|---|---|---|---|
| body-kinematics / Provisional layout | Mount positions | test_body.py:35 `test_mount_points_at_80_mm_and_30_plus_60k` | C |
| body / Body pose to leg targets | Neutral pose | test_body.py:48 `test_identity_pose_gives_identical_targets` | C |
| body / Body pose to leg targets | Body translation | test_body.py:54 `test_x_translation_shifts_targets_oppositely_in_each_leg_frame` | C |
| body / Reachability report | Infeasible pose | test_body.py:85, :93 | C |
| ci / Canonical build (MOD) | Warning fails CI | `make gate-test`: "warnings OK"; CI cad job pass | C |
| ci / Canonical build | Interference fails CI | gate-test "fit OK"; cad.yml runs check-fit | C |
| ci / Canonical build | Step order | cad.yml gate-test, check-fit, Params drift, TOOLCHAIN=docker | C(s) |
| ci / Canonical build | Snapshot drift fails CI | gate-test "params drift OK" (forced -D k_dyn=1.6 diff fails) | C |
| ci / Software workflow | PR triggers run | software.yml pull_request + push main, no path filters; software run observed on PR #27 | C |
| ci / Software workflow | Failing test fails CI | workflow step `make software`, no continue-on-error; failing-test probe gave make exit 2; CI run itself green so red not observed | C |
| ci / Software artifacts | Artifacts uploaded | run 36696295691: artifact `software-report`, 14-day expiry, upload step success | C |
| gait-engine / Phase engine | Periodicity | test_gait.py:21 (near-trivial, S2) | C |
| gait / Phase engine | Stance foot fixed (reworded) | test_gait.py:27 `test_stance_foot_moves_backwards_at_constant_speed_in_body_frame` | C |
| gait / Gait definitions | Support count | test_gait_all.py:41 min grounded 3/5/4 over 600 samples | C |
| gait / Stability margin | Positive margin | test_gait_all.py:48 | C |
| gait / Stability margin | Unsupported | test_gait_all.py:68; test_stability.py:30,37 | C |
| gait / Limit compliance | Default cycles feasible | test_gait.py:66; test_gait_all.py:48,75 | C |
| gait / Limit compliance | Excess step length | test_gait.py:76; test_report.py:45 | C |
| gait / Torque informational | Torque above stall | test_report.py:50 (warning text) and :75 (CLI exit 0 with warning) | C |
| leg-kinematics / Conventions | Zero pose | test_leg.py:24 | C |
| leg / Forward kinematics | Offset applied | test_leg.py:13, :28 | C |
| leg / Inverse kinematics | Round trip on the grid | test_leg.py:19, :33 | C |
| leg / Inverse kinematics | Unreachable target | test_leg.py:51 | C |
| leg / Joint limits | Within limits | test_limits.py:15 | C |
| leg / Joint limits | Violation reported | test_limits.py:19 | C |
| leg / Joint limits | Servo inclusion | test_limits.py:30, :34 | C |
| params-bridge / Parameter export | Export is reproducible | test_echo_to_json.py:71; check-params OK | C |
| params / Parameter export | Derived values present | test_params.py:25 | C |
| params / Committed snapshot | Software reads the snapshot only | `rg` over src shows only field names; no guard test (W7) | C(s) |
| params / Drift gate | Stale snapshot fails | gate-test "params drift OK" | C |
| params / Drift gate | Fresh snapshot passes | `check-params: OK` | C |
| params / Loader | Valid load | test_params.py:25 | C |
| params / Loader | Missing key | test_params.py:44 | C |
| repo-hygiene / Editor conventions (MOD) | Config present | .editorconfig `root = true`, `[{Makefile,*.mk}]` tab | C(s) |
| repo-hygiene / Editor conventions | Python indentation | .editorconfig `[*.py]` indent_style = space, indent_size = 4 (literal now) | C(s) |
| repo-hygiene / Makefile entry point (MOD) | Default goal lists targets | make help exit 0 (unchanged since previous run; Makefile not touched by a8914a0) | C |
| repo-hygiene / Makefile entry point | Placeholder target | make firmware "not implemented", exit non-zero (unchanged) | C |
| repo-hygiene / Makefile entry point | CAD targets are real | make stl render exit 0 | C |
| repo-hygiene / Makefile entry point | Software target is real | make software ran ruff, mypy, pytest | C |
| repo-hygiene / Python artifacts ignored | Cache ignored | .gitignore:18 (unchanged) | C |
| repo-hygiene / Python artifacts ignored | Snapshot tracked | leg-params.json tracked, not ignored | C |
| repo-structure / Per-directory README (MOD) | README in each directory | firmware/README.md, software/README.md | C(s) |
| repo-structure / Per-directory README | Firmware stub holds no code | `fd -t f . firmware`: README.md only | C |
| repo-structure / Per-directory README | Software may hold Python | software/ tracks README, pyproject, src, tests | C |
| repo-structure / Deferred scope (MOD) | No deferred artifacts | firmware README only | C |
| repo-structure / Deferred scope | Only permitted CAD sources | `git diff main --stat -- hardware`: empty | C |
| repo-structure / Deferred scope | Shared params permitted | no new params.scad | C |
| repo-structure / Deferred scope | Only permitted tooling files | tools/cad top level: echo-to-json.py, export-params.scad, 2 awk scripts (fixtures dir unchanged) | C(s) |
| software-tooling / Project layout | Toolchain installs | CI run on Python 3.12.14 installed and passed; local 3.14.7 also | C |
| software-tooling / Quality gate | Failure propagates | scratch-worktree probe: failing test gives make exit 2 | C |
| software-tooling / Headless visualiser | Render without display | test_viz.py:14, :23 | C |
| software-tooling / Pose report | Report content | test_report.py:33 | C |
| software-tooling / Decision record and SDD config | Config enabled | config.yaml `strict_tdd: true`, `verify.test_command` includes check-params | C(s) |

**Compliance summary**: 53/53 scenarios compliant (C or C(s)); 29/29 requirements.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|---|---|---|
| Leg FK/IK, limits | Implemented | unchanged |
| Params bridge | Implemented | unchanged |
| Body layout/targets | Implemented | unchanged |
| Gait engine | Implemented | now consistent with the reworded scenario (see N1 for wording residue) |
| Stability margin | Implemented | unchanged |
| Visualiser / report / CLI | Implemented | exit 0 for findings now test-covered |
| CI | Implemented | both workflows green on PR #26 and #27 |

### Coherence (Design)
Design.md was back-ported for the four documented deviations (provisional list, servo_range_failures, is_provisional, theta limit in limits.THETA_LIMIT). Decisions 1-10 followed; no remaining deviation is undocumented. The ADR-0006 conventions match code (neutral alpha 9.876, phi 0.721).

### Archive readiness of the deltas
- gait-engine is a new capability (no main spec): the reworded scenario is archived as new; consistent with the test.
- ci MODIFIED "Canonical build": full text and all scenarios; replaces the main block cleanly (main lines 36-40 show the old 2-scenario block). ADDED "Software workflow" and "Software artifacts" do not collide.
- repo-hygiene MODIFIED "Editor conventions" and "Makefile entry point": full text, all scenarios preserved. ADDED "Python artifacts ignored" clean.
- repo-structure MODIFIED "Per-directory README" (scenario renamed "Stubs hold no code" to "Firmware stub holds no code": whole block replaced) and "Deferred scope excluded" (main text says both dirs must be stubs; delta replaces it fully). Clean.
- S1: main ci spec blank-line defect before `### Requirement: Artifacts` remains; harmless to header-based merge, fix at archive.
- tasks.md task 1.8 text still reads "verify.test_command: make software gate-test" (historical description of PR 1; config now has check-params). Not blocking.

### New issues introduced by remediation
None blocking. Observations:
- N1 (WARNING, wording): the gait-engine "Phase engine" requirement text still says the engine returns "each foot's world position", and `Frame.feet` is documented as "(6, 3) world foot contact points" (gait.py:48), whereas the reworded scenario and the test define feet as body-frame points (the stance foot moves backwards). "World" here means ground-relative height/orientation with the body fixed at the xy origin. Reword requirement text and docstring to "body-frame foot position" (or state the convention) when convenient; no behavioural impact.
- The remediation commit also committed the previous verify-report.md; this report overwrites it.

### Issues Found
**CRITICAL**: None.

**WARNING**
- W7. No automated guard for "software reads the snapshot only" (carried over, not addressed).
- N1. "World foot position" wording in the Phase engine requirement and `Frame.feet` docstring versus the body-frame semantics of the reworded scenario.

**SUGGESTION**
- S1. Fix blank line before `### Requirement: Artifacts` in main ci spec at archive.
- S2. Strengthen the periodicity test (phase 0.999999 vs 0) because `frame_at` wraps `s %= 1.0`.
- S6. Informational: `workflow_dispatch` trigger and ignored artifacts, harmless.
- S7. Optionally update the historical text of tasks.md task 1.8 to mention check-params; add a Safety-net column to future TDD evidence tables.

### Verdict
PASS WITH WARNINGS

C1 is resolved (reworded scenario, renamed test genuinely asserting it), W1-W6 and S3-S5 resolved, CI on Python 3.12.14 is green with 116 tests and the 14-day artifact. Two warnings (W7, N1) and three suggestions remain; none blocks archive.
