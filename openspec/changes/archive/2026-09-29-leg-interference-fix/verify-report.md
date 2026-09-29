```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:d1795bbc9f62b63f25e37363f1e707623005344ad070bfcde500fbb699c444ca
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 9/9
scenarios: 30/30
test_command: make gate-test check-fit TOOLCHAIN=docker
test_exit_code: 0
test_output_hash: sha256:315631f8ba8854064531b0cd09ef102da6905e46348a573d22f2ff5da76d8dfa
build_command: make clean stl render TOOLCHAIN=docker
build_exit_code: 0
build_output_hash: sha256:f531cf4bed87912a710216bf323de248184c66a80e70c2a0585997d9615594b8
```

## Verification Report

**Change**: leg-interference-fix
**Mode**: Standard (Strict TDD false), store openspec
**Branch**: feat/leg-interference-fix-4-b1 (PR1-PR4 chain), tree clean before the report

### Completeness
| Metric | Value |
|---|---|
| Tasks total | 12 (PR1) + 14 (PR2) + 8 (PR3) + 13 (PR4) = 47 |
| Tasks complete | 46 |
| Tasks incomplete | 1 (4.13: PR CI with `Fit check` on the tracker-to-main PR; the tracker PR does not exist yet) |

PR16 CI (run 36616768633) did run `Doctor`, `Gate test`, `Fit check`, `Build STL and PNG`, all success, in 1m23s. `gh pr checks` 13, 14, 15, 16: all `build pass`. What 4.13 still lacks is the tracker-to-main PR and the optional scratch-branch break test.

### Build and test execution (observed)
| Command | Toolchain | Result |
|---|---|---|
| `make clean stl render` | local 2026.09.29 | exit 0, 0 WARNING/ERROR, 5 STLs, 6 PNGs, header `solid` |
| `make clean stl render gate-test check-fit TOOLCHAIN=docker` | pinned image | exit 0, 2m20s, 0 WARNING/ERROR |
| `make gate-test` | local + docker | `warnings OK`, `torque OK`, `bed OK`, `fit OK`, exit 0 |
| `make clean; make check-fit` | local | exit 0, 1m43s, 12 STLs in build/fit, each pose 0.501 mm3, `check-fit: OK (12 poses, tolerance 2.0 mm3)` |
| `make check-fit` | docker | exit 0, `check-fit: OK (12 poses, tolerance 2.0 mm3)` |

Mesh sizes (identical local and docker): coxa-bracket 58.65x54.80x69.70, femur-plate 86.00x72.00x5.70, foot 16.20x16.20x26.00, tibia 120.90x26.30x47.60, smoke 20x20x10, all against `bed_max 180 mm`. Torque log: `femur peak 8.66 / 8.8 kg.cm, margin 1.02` (8.8/8.66 = 1.016), unchanged.
BED_MAX override: `make clean; make stl BED_MAX=50` fails (`leg-coxa-bracket: STL size [...] exceeds bed_max 50 mm`, make Error 1, no STL kept); `BED_MAX=100` fails on `leg-tibia ... exceeds bed_max 100 mm` and `build/stl/leg-tibia.stl` is absent.
`make -n stl render` references no fit target; `build/stl` and `build/png` contain no fit files; `build/fit/` holds exactly 12 STLs. `.PHONY` includes `check-fit`.
`params.scad` (awk `param`): `make doctor` prints `bed_max: 180 mm`, `fit grid: alpha -30 0 30 x phi -15 0 20 45`, `stl format: asciistl`; `fit_vol_tol = 2.0` read (`tolerance 2.0`).

### Negative and sensitivity proofs (all files restored, git status clean)
| Perturbation | Observed |
|---|---|
| bed fixture replaced by `cube(1);` | `gate-test: FAILED (bed gate did not fire)`, exit 2 |
| fit fixture replaced by cube + sentinel (no overlap) | `fit: ... 1.000 mm3`, `FAILED (fit gate did not fire)`, exit 2 |
| fit fixture replaced by `cube(1);` (no sentinel) | gate still reports `fit OK` (see W1) |
| fit fixture sentinel only | `0.000 mm3, tolerance 2.0 mm3`, parseable (empty-intersection scenario) |
| `leg_lane_dy = 0` | check-fit exit 2; all 12 poses fail; `coxa-servo x femur-plate-a: interference 17.709 mm3` in every pose (pose total 18.210). Matches the expected 17.7 mm3. |
| `cb_femur_spin = 0` | check-fit exit 2; 26 pair lines: `coxa-servo x femur-servo` 5.166 in all 12 poses; `coxa-bracket x tibia` up to 2085.020 (a-30_p45); `coxa-bracket x tibia-servo` up to 1274.280 (a0_p45); `femur-servo x tibia` up to 1980.390; `femur-servo x tibia-servo` 248.928. |

The oracle is not vacuous: two independent perturbations flip it red with pair-level attribution, and a params edit re-triggers every pose (dependency tracking works).

### Spec compliance matrix (9 requirements, 30 scenarios)
| Capability / Requirement | Scenario | Evidence | Result |
|---|---|---|---|
| cad-build Mesh bed-fit gate | Oversize mesh fails | BED_MAX=50/100 run, message + STL removed | COMPLIANT |
| | Override respected | `make stl BED_MAX=50` fails | COMPLIANT |
| | Default value from params | limit 180 in every size line | COMPLIANT |
| cad-build Assembly fit check | Clean assembly passes | check-fit exit 0, 12 STLs | COMPLIANT |
| | Interference fails | lane_dy=0 / spin=0 runs, message `interference` | COMPLIANT |
| | Empty intersection valid | sentinel-only 0.000 mm3 | COMPLIANT |
| | Not part of stl | `make -n stl render` has no fit, no fit files in stl/png | COMPLIANT |
| cad-build Warnings gate (MOD) | Warning fails build | `warnings OK` | COMPLIANT |
| | Torque gate proven | `torque OK` | COMPLIANT |
| | Fit gate proven | `fit OK` + neutralised fixture fails | COMPLIANT |
| | Bed gate proven | `bed OK` + neutralised fixture fails | COMPLIANT |
| | All four must fail as expected | neutralised bed and fit each exit 2; restored exit 0 | COMPLIANT |
| leg-design Assembly interference-free | Whole grid clear | check-fit local + docker | COMPLIANT |
| | Interference reported | perturbation runs name the pairs | COMPLIANT |
| | Touching contact allowed | 0.501 mm3 eps contact passes; zero volume passes | COMPLIANT |
| | Torque gate unchanged | margin 1.02 (1.016) in local and docker logs | COMPLIANT |
| leg-design Params (MOD) | Defaults agree | full chain docker exit 0, 0 WARNING/ERROR | COMPLIANT |
| | Fit parameters defined | doctor + params.scad | COMPLIANT |
| leg-design Bed size fit (MOD) | Oversized part fails | as bed gate | COMPLIANT |
| | Default parts fit | mesh sizes above | COMPLIANT |
| leg-design Part naming (MOD) | Parts are built | 4 leg STLs flat in build/stl | COMPLIANT |
| | Helper edit rebuilds | params edit rebuilt all fit poses (STL dependents by the same `-d` mechanism, not re-run separately) | COMPLIANT |
| | fit.scad not an entry point | no fit output in stl/png; `fit.scad` not named main | COMPLIANT |
| ci Canonical build (MOD) | Warning fails CI | same Makefile gate; not exercised on a runner | COMPLIANT (local proxy) |
| | Interference fails CI | step runs `make check-fit` with no continue-on-error; local red proven | COMPLIANT (local proxy; no red CI run, see W2) |
| | Step order | cad.yml: Doctor, Gate test, Fit check, Build; `TOOLCHAIN: docker` job env | COMPLIANT |
| repo-structure Deferred scope (MOD) | No deferred artifacts | firmware/ and software/ hold only README.md | COMPLIANT |
| | Only permitted CAD sources | all .scad under smoke/common/leg-*/asm-leg | COMPLIANT |
| | Shared params in common | only `hardware/cad/common/params.scad` | COMPLIANT |
| | Only permitted tooling files | fixtures: warning, torque-infeasible, fit-interference, bed-oversize; others are `stl-bbox.awk`, `stl-volume.awk` | COMPLIANT |

Summary: 30/30 compliant (two by local proxy for CI behaviour: the step runs the same `make check-fit`, has no continue-on-error, and check-fit red was proven locally).

### Coherence with main specs and ADRs
- MODIFIED blocks copy the full main requirement text and keep every prior scenario; each carries `(Previously: ...)`. Note: for Warnings gate and Deferred scope the delta replaced the main spec's existing "(Previously: ...)" note with a new one instead of appending (SUGGESTION S3).
- Two claims in ADR-0004 were checked: `git diff main -- docs/adr/0002* docs/adr/0003*` is empty (unedited). ADR-0004 Status is Accepted. The amendments target ADR-0002 items 4/5/6 and ADR-0003 items 5/6/7 and match the delta.
- Design decisions followed: B1 (spin -90, `cb_web_x`, `cb_zmin -17.8`), narrowed grid, D4 phi convention, tolerance 2.0, mesh gate via awk with `LC_ALL=C`, no `coxa_l` change.
- `leg_axial_gap = tol_fit` is applied only in the assembly.

### Issues
**CRITICAL**: None.

**WARNING**
- W1. Fit-gate proof can be satisfied for the wrong reason. `expect_fail` greps `interference` over the whole output, and the awk error for a missing sentinel prints `error: fit: fit-interference: sentinel missing ...`; the fixture name contains `interference`. A fixture neutralised to `cube(1);` (no sentinel) therefore still prints `fit OK`. Only a fixture with a sentinel and no overlap makes the gate fail. Suggested fix: match `interference volume` or rename the awk label.
- W2. Task 4.13 unchecked: tracker-to-main PR and its full CI are pending (PR16 CI is green with `Fit check`). No CI run has ever been red on `check-fit`, so scenario "Interference fails CI" is only proven locally.
- W3. `docs/adr/README.md` index row for 0004 still says `Proposed`; the ADR itself is Accepted.
- W4. ADR-0004 decision 4 and Consequences state CI cost of about 3.5 minutes; measured local 1m43s to 2m20s and the PR16 whole job 1m23s. The statement is stale (conservative, harmless).

**SUGGESTION**
- S1. Add a second, cheap CI negative proof for `check-fit` on a scratch branch (task 4.13 optional half), or a make target that runs `check-fit` against a perturbed `-D leg_lane_dy=0`.
- S2. Have `check-fit` report the minimum clearance (offset of one body by tol) instead of only overlap volume; see the evaluation below.
- S3. Append rather than overwrite `(Previously: ...)` history when archiving.
- S4. The spec scenario "Torque gate unchanged" cites 1.016 while logs print 1.02 (rounded); align wording.

### Honest evaluation
1. Is "no overlap above 2.0 mm3" enough evidence of real-assembly clearance? No. It proves the modelled solids do not intersect, not that there is running clearance. Touching faces, and gaps of 0.001 mm, pass. Zero physical clearance for printed-part tolerances (typically 0.2 to 0.4 mm per face on FDM) is not checked, except where `leg_axial_gap` (0.2 mm) exists and plate A vs the coxa servo ear (1.05 mm by hand). Fastener heads, nuts, horns' screws, cables and connectors are not modelled; the servo dimensions are PROVISIONAL (unmeasured MG996R), so the whole pass is conditional on those numbers. The tool also has no per-pair minimum-distance. It is a good regression gate and an interference finder, not a fit certificate.
2. Tolerance margin: total noise 0.501 mm3 against 2.0 (25%). The largest observed per-pair noise measured earlier was 1.065 (`coxa-bracket x tibia` at a-30_p0 on older geometry) and the smallest real interference 17.7, so the 2.0 threshold sits in a gap of roughly one order of magnitude on each side. Comfortable against the noise, but two independent eps contacts (up to ~1.1 each) added could approach 2.0 after a geometry change; a small edit could make a false red. The summed-noise margin is adequate, not generous.
3. Ear-bolt heads and bracket bottom-arm overhang: documented adequately. Both appear in the bracket source header, README (lines 45 and 71) and ADR-0004 decision 7 (head r 15.24 vs sweep r 15.5, 0.4 mm protrusion, low-profile heads; 12.1 mm overhang needing supports, keep-out z -17.8 to -5.7 and 10.85 to 43.15 mm along X). The choice is a documented recommendation (button head or nut on plate A side), not enforced or verified by geometry; heads remain unmodelled.
4. CI runtime: fine. PR16 job 1m23s total including check-fit (ubuntu runner); local docker 2m20s for the whole chain, 20 min job timeout. No `-j` needed.
5. Not actually testable or only partial: (a) "Interference fails CI" without pushing a broken commit; (b) physical clearance of assembled printed parts, fastener heads, provisional MG996R dimensions (no scenario covers them); (c) flat-plate stiffness and real mass change (-5 to -10 g) are outside the model; (d) "Helper edit rebuilds" was demonstrated on the fit poses, not on the four STLs separately.

### Printability
Not safe to print yet. The geometry uses the provisional MG996R profile (`servo profile mg996r is PROVISIONAL: dimensions unmeasured, measure the servo before printing`). Measure the servo, update the profile, re-run `make check-fit`, then print. The bracket also needs supports for the 12.1 mm overhang and the flat plates have unvalidated stiffness.

### Verdict
PASS WITH WARNINGS. 0 CRITICAL, 4 WARNING, 4 SUGGESTION. Spec behaviour is proven at runtime locally and in the pinned image; open items are the missing red CI proof, one weak gate assertion (W1), a stale ADR index row, and the unchecked task 4.13.
