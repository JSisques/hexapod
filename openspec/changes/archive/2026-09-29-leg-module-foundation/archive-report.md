# Archive Report: Leg Module Foundation

**Change**: leg-module-foundation
**Archived**: 2026-09-29
**Branch**: chore/archive-leg-module-foundation
**Status**: ARCHIVED

## Change Summary

The leg module foundation establishes the parametric hexapod leg design foundation with a provisional MG996R servo profile, tier XS validation (femur 55 mm / tibia 80 mm), torque feasibility gate, and shared library infrastructure. Three chained PRs (#9, #10, #11) merged into the tracker branch `feat/leg-module-foundation` with CI green on all stages. The change delivers a library contract (`hardware/cad/common/`), four printable parts (coxa bracket, femur plates, tibia, foot), one assembly preview, torque model and documentation, and architectural decision records.

## Task Completion Status

**Total tasks**: 27
**Completed**: 27
**Blocked**: 0

All implementation tasks across Phase 1 (Foundation), Phase 2 (Printable Parts), Phase 3 (Assembly & Docs), and Phase 4 (Verification) are marked complete in `tasks.md`:

- **Phase 1 (1.1–1.9)**: Common library, servo profiles, torque gate, Makefile, fixture — all 9 tasks complete.
- **Phase 2 (2.1–2.6)**: Four printable parts, envelope verification, hard-coded dimension scan — all 6 tasks complete.
- **Phase 3 (3.1–3.5)**: Assembly preview, torque documentation, ADR-0003, README/config updates — all 5 tasks complete.
- **Phase 4 (4.1–4.7)**: Build, gate-test, infeasibility proof, dependency tracking, CI verification — all 7 tasks complete.

Task 4.7 (CI green on PR chain) is confirmed: PRs #9, #10, #11 each show `build: pass` in `gh pr checks`.

## Verification Status

**Verdict**: PASS WITH WARNINGS
**Critical findings**: 0
**Warnings**: 5
**Suggestions**: 5
**Test exit code**: 0

Per `verify-report.md` and final-state facts (CI run chain 2026-09-29):

- `make clean stl render TOOLCHAIN=docker`: exit 0, no WARNING/ERROR.
- `make gate-test`: both "warning gate OK" and "torque gate OK" confirmed.
- All 13 requirements, 24 scenarios verified compliant.
- Torque re-derivation confirms femur peak margin 1.016 (critical: 1.6% margin at 11.0 kg.cm stall; +33 g mass error fails CI).
- Measured STL bounding boxes confirm all printable parts fit bed_max 180 mm.

## KNOWN OPEN ISSUES (Blocking Production Use)

**These issues carry forward to the new change `leg-interference-fix` and MUST be resolved before printing or assembly.**

### (a) Femur servo body intersects femur-plate spacer bosses
- **Overlap**: 9.0 × 37.0 × 19.7 mm at x 53–62 mm.
- **Root cause**: Servo body reaches +30.7 mm from femur axis; spacer bosses placed at femur_l/2 = 27.5 mm sit within the envelope.
- **Fix options**: Relocate spacer bosses beyond femur_l + horn radius, move to outer edge outside body_w, or shorten/reposition to clear x 0..30.7 mm along femur axis.
- **Impact**: Printable parts NOT safe to print until fixed.

### (b) Tibia cage intersects coxa-bracket femur cage
- **Overlap**: 4.7 × 43.6 × 12.9 mm at x 66.2–70.9 mm, z 23.4–36.2 mm (phi 20 deg nominal).
- **Root cause**: Coxa-bracket femur cage extent reaches past the tibia knee joint.
- **Fix options**: Reduce coxa-bracket cage extent toward +X (outboard wall), lengthen femur (offset tibia outward), or trim tibia knee cage on inboard side. Sweep analysis across phi range required.
- **Impact**: Printable parts NOT safe to print until fixed.

### (c) Minor femur servo vs coxa bracket + coxa servo vs femur plate A
- **Femur servo vs coxa bracket**: 2.7 × 2.5 × 19.7 mm at x 13.1–15.8 mm (minor).
- **Coxa servo vs femur plate A**: 2.3 × 3.9 × 2.5 mm at x 14.6–16.9 mm (new minor).
- **Fix options**: Enlarge body_clear tolerance, move plate A inboard, or notch bracket web.
- **Severity**: Minor; fix contingent on (a) and (b).

### (d) No assembly interference check in CI
- **Issue**: Assembly geometry (asm-leg) is unchecked in the build pipeline. Interference findings are scratch intersection tests, not automated gates.
- **Recommendation**: Add a `make target` or fixture that fails the build on non-zero overlap volume in asm-leg assembly (manifold backend tolerance-aware).

### (e) Bed assert uses analytic sizes, not mesh bounding box
- **Issue**: The `bed_max` assertion consumes analytic size functions computed during design; it does not validate STL mesh bounds at export time.
- **Finding**: Measured STL boxes agree with analytic sizes today, but nothing prevents future divergence.
- **Recommendation**: Add a mesh bbox check or document the link between analytic functions and STL exports.

### (f) MG996R profile is PROVISIONAL and unmeasured
- **Issue**: Every dimension marked P (provisional) in the profile design table is unmeasured. The servo is a generic MG996R clone; TowerPro datasheet dimensions are used with generic CAD drawings, not vendor measurement.
- **Risk**: Dimensions may differ ±1–2 mm from clones or future units.
- **Mitigation**: Profile emits provisional echo on every build. **Do not print parts until the real servo is measured and profile dimensions are verified.**

### (g) Femur peak torque margin 1.016 (11.0 kg.cm datasheet figure)
- **Issue**: At the TowerPro datasheet stall figure of 11.0 kg.cm, the femur peak margin is only 1.6% (margin ratio 1.016).
- **Headroom**: ~33 g of mass increase breaks the CI gate (m_total 2.104 kg + 0.033 kg = 2.137 kg → femur peak margin 1.0).
- **Contingency**: Femur length 50 mm (vs design choice 55 mm) yields margin 1.08, but this is a confirmed product decision not to implement.
- **Risk acceptance**: XS tier is marked as "validation stage, not end goal." A later change will move to tier M with a measured high-performance servo (STS3215 class, ~20–30 kg.cm stall). The 1.6% margin is accepted because MG996R is provisional and XS is temporary.

---

## Specs Merged

### leg-design (NEW)
- **Action**: Created `openspec/specs/leg-design/spec.md`
- **Content**: 13 requirements, 14 scenarios defining servo profile contract, provisional marker, torque gate, params location and defaults, fastener/material defaults, helper directory, part naming, and echo/assert hygiene.
- **Verification**: All 14 scenarios COMPLIANT.

### cad-build (MODIFIED)
- **Action**: Updated `openspec/specs/cad-build/spec.md` with two new scenarios and one requirement.
- **Changes**:
  - **Requirement: Entry points and outputs** — expanded with "Assembly produces PNG only" and "Helper directory not built" scenarios. Previously: only smoke part rule.
  - **Requirement: Warnings gate** — extended with "Gate-test proves the torque gate" scenario and torque fixture proof text. Previously: warning gate only.
  - **Preserved**: Toolchain selection, Library path and submodule guard, Dependency tracking, Clean requirements remain unchanged.
- **Verification**: 4 original + 4 new = 8 scenarios, all COMPLIANT.

### repo-structure (MODIFIED)
- **Action**: Updated `openspec/specs/repo-structure/spec.md` with expanded Deferred scope.
- **Changes**:
  - **Requirement: Deferred scope excluded** — updated permit list to include `hardware/cad/common/` (with `params.scad`), leg part directories (`leg-*`, `asm-leg`), and torque fixture `tools/cad/fixtures/torque-infeasible.scad`. Previously: forbade `params.scad` and parts; only smoke part permitted.
  - **Scenario changes**: "No deferred artifacts" and "Only permitted CAD sources exist" replaced with new rules reflecting the new structure. "Shared params permitted in common" added.
  - **Preserved**: Domain directory skeleton, Per-directory README, Root README repo map requirements.
- **Verification**: 3 original + 3 new = 6 scenarios, all COMPLIANT.

## Artifacts Archived

All change artifacts preserved in `openspec/changes/archive/2026-09-29-leg-module-foundation/`:

- ✅ `proposal.md` — change intent, scope, approach, delivery slices.
- ✅ `specs/` — delta specs (cad-build, leg-design, repo-structure).
- ✅ `design.md` — technical architecture, data flow, library API, torque budget.
- ✅ `tasks.md` — 27 completed implementation tasks, phase breakdown.
- ✅ `exploration.md` — design rationale, alternatives considered.
- ✅ `apply-progress.md` — implementation deviations and notes.
- ✅ `verify-report.md` — verification matrices, compliance, findings.
- ✅ `archive-report.md` (this file) — final state, issues, merged specs.

## Build Evidence

| Command | Result |
|---------|--------|
| `make clean stl render TOOLCHAIN=docker` | exit 0; 4 leg STLs + smoke.stl; 5 leg PNGs + asm-leg.png + smoke.png; no asm-leg.stl |
| `make gate-test` | exit 0; warning fixture OK; torque fixture OK |
| `gh pr checks 9 / 10 / 11` | build: pass on all three; chained bases correct |
| Infeasibility proof: `openscad -D 'leg_tier="M"' leg-tibia/main.scad` | non-zero; `torque budget exceeded` message |
| Torque re-derivation (independent Python from params.scad) | femur peak margin 1.016 confirmed; tier S also fails; L requires 25.05 kg.cm |
| Measured STL bounds (mm, bed_max 180) | coxa 86.4 × 59.8 × 57.6; femur 86.0 × 72.0 × 30.8; tibia 120.9 × 26.3 × 47.6; foot 16.2 × 16.2 × 26.0 |
| Provisional echo | present in `build/log/stl/leg-tibia.log`; no WARNING/ERROR gate trip |

## Recommendations for Follow-Up

**New change**: `leg-interference-fix`

### Immediate tasks (blocking printing/assembly)
1. Fix interference (a): servo/spacer collision
2. Fix interference (b): tibia/coxa-bracket collision
3. Fix interference (c): minor servo/bracket collisions
4. Measure the real MG996R servo and update profile dimensions
5. Re-run verify with measured servo and updated part geometry

### Optional improvements
- Add CI interference gate (mesh intersection check on asm-leg)
- Document mesh bbox vs analytic size relationship
- Consider tier S fixture for CI (S+MG996R also fails)
- Add material callout comments in part modules
- Plan tier M profile and STS3215 servo characterization

## Final State Authority Notes

This archive report records the state of the change **at close** per the SDD Final-State Authority hierarchy:

- **Persisted tasks artifact**: All 27 tasks checked complete in `openspec/changes/archive/2026-09-29-leg-module-foundation/tasks.md`.
- **Explicit final-state facts (from orchestrator launch prompt)**: PRs #9, #10, #11 merged into feat/leg-module-foundation via chain; CI green on all; verify PASS WITH WARNINGS (0 critical, 5 warnings, 5 suggestions); all 27 tasks complete.
- **Verify-report (intermediate snapshot, 2026-09-29)**: Reflects verification time state; intermediate assertions like "4.7 unchecked" are noted but superseded by later CI confirmation.

No contradictions between sources. The change is complete and ready for follow-up work on interference fixes and servo measurement.

## Key Learnings

1. Provisional servo profiles with unmeasured dimensions require echo warnings in the build pipeline to prevent silent misuse.
2. Torque feasibility gates with narrow margins (1.6%) are acceptable for validation stages but demand explicit acceptance and headroom documentation.
3. Assembly preview geometry (asm-leg) must be integrated into CI coverage to detect mechanical clashes early; scratch-test findings are not sufficient for production parts.
4. A parametric library contract (getter + kv_get assertions) is more robust than hard-coded servo dimensions scattered across parts.
5. Chained PR slices under 400 lines each keep review load manageable and enable incremental verification at each slice.
