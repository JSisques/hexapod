```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:02487b3874c54bc52f645104dc4918e5e6e249321281e69cce11ce47dc827a34
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 13/13
scenarios: 24/24
test_command: make gate-test
test_exit_code: 0
test_output_hash: sha256:431f52cd98f03571222e760853365c9bfd29db51e210d4257d3a72f78e380d8c
build_command: make clean stl render TOOLCHAIN=docker
build_exit_code: 0
build_output_hash: sha256:d9c81cada35511c70cdb6f8c327e711e5b591910ba45245be8cd8da1d1f3b5c2
```

## Verification Report

**Change**: leg-module-foundation
**Version**: N/A
**Mode**: Standard (Strict TDD false; no test runner, verification by real make/openscad runs)
**Branch**: feat/leg-module-foundation-3-asm-docs (PR1 #9 + PR2 #10 + PR3 #11 chain), HEAD 03e93b2

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 34 (1.1-1.9, 2.1-2.6, 3.1-3.5, 4.1-4.7) |
| Tasks complete | 33 |
| Tasks incomplete | 1 (4.7 push + CI green; evidence below shows CI is green, box only needs ticking) |

### Build & Tests Execution
| Command | Exit | Observed |
|---|---|---|
| `make clean stl render` (local OpenSCAD) | 0 | 0 WARNING/ERROR; build/stl = 4 leg STLs + smoke; build/png = asm-leg + 4 leg + smoke; no asm-leg.stl, no common.stl/png |
| `make clean stl render TOOLCHAIN=docker` (pinned image) | 0 | 0 WARNING/ERROR; same outputs |
| `make gate-test` (local and TOOLCHAIN=docker) | 0 | `gate-test: OK` + `gate-test: torque OK` |
| `openscad --hardwarnings -D 'leg_tier="M"' leg-tibia/main.scad` | non-zero | `ERROR: Assertion '(r[2] <= r[3])' failed: "torque budget exceeded: femur static 9.51 kg.cm > allowable 6.6 kg.cm (servo mg996r, tier M, 6 V)"`; no STL written |
| same with `-D check_torque=false` | 0 | echo `torque gate skipped (check_torque=false)`, STL written |
| `-D bed_max=100` on leg-tibia | non-zero | `leg-tibia: part size [120.9, 26.3, 47.6] exceeds bed_max 100 mm` |
| `-D leg_tier="XL" -D check_torque=false` | non-zero | bed assert: size [240.9, ...] exceeds bed_max 180 mm |
| scratch `sv(servo,"nope")` | non-zero | `servo profile mg996r: key not found or duplicated: nope` |
| `rg PROVISIONAL build/log/stl/leg-tibia.log` | 0 | `ECHO: "servo profile mg996r is PROVISIONAL: dimensions unmeasured, measure the servo before printing"`; build exit 0 |
| `touch common/params.scad && make stl` | 0 | 4 leg STLs rebuilt (smoke not, correct: it does not include params) |
| `rg '40\.7|19\.7|54\.5|49\.5|37\.0' hardware/cad --glob '!**/servos/**'` | 1 (no match) | none outside servos |
| `gh pr checks 9 / 10 / 11` | 0 | build: pass (17s / 28s / 37s) on all three; all PRs OPEN, chained bases correct |

Coverage: not available.

Measured STL bounding boxes (mm, print pose, bed_max 180): coxa-bracket 86.4 x 59.8 x 57.6; femur-plate 86.0 x 72.0 x 30.8; tibia 120.9 x 26.3 x 47.6; foot 16.2 x 16.2 x 26.0. All <= 180 and equal the analytic sizes fed to `leg_part_checks`. Note the bed assert consumes analytic `*_size()`, not the mesh; they agree today but nothing enforces it (SUGGESTION).

### Spec Compliance Matrix
| Requirement | Scenario | Evidence | Result |
|---|---|---|---|
| leg-design: Servo profile contract | Profile exposes required fields | default build reads all keys through sv (torque gate, cages, horn) with exit 0 | COMPLIANT |
| Asserting getter | Missing key fails | scratch sv(servo,"nope") asserts naming key | COMPLIANT |
| Asserting getter | No hard-coded servo dims | rg outside `**/servos/**`: no match | COMPLIANT |
| Provisional marker | MG996R is provisional | profile provisional=true (visible in gate call trace) and echo emitted | COMPLIANT |
| Provisional marker | Echo emitted, build passes | leg-tibia.log contains echo, make stl exit 0 | COMPLIANT |
| Params location and defaults | Defaults agree | make clean stl render + gate-test exit 0, no WARNING/ERROR (local+docker) | COMPLIANT |
| Torque gate | Infeasible tier fails | -D leg_tier="M": non-zero, message present | COMPLIANT |
| Torque gate | Feasible default passes | XS echo rows, asserts hold (see re-derivation) | COMPLIANT |
| Bed size fit | Oversized part fails | -D bed_max=100 and XL both fail the assert | COMPLIANT |
| Fastener and material defaults | Foot material | hardware/cad/README.md: foot TPU, others PETG | COMPLIANT (documentation only) |
| Helper directory | No entry point in common | fd main.scad shows none under common/ | COMPLIANT |
| Part naming and inclusion | Parts are built | 4 flat STLs in build/stl | COMPLIANT |
| Part naming and inclusion | Helper edit rebuilds | touch params.scad, 4 STLs rebuilt | COMPLIANT |
| Echo/assert text hygiene | Provisional echo does not trip gate | echo present, 0 matches of WARNING/ERROR, exit 0 | COMPLIANT |
| Echo/assert text hygiene | Assertion failure is detected | make gate-test torque OK (fails and matched) | COMPLIANT |
| cad-build: Entry points and outputs | Smoke part built | smoke.stl and smoke.png present | COMPLIANT |
| Entry points and outputs | Non-entry files ignored | no output for non-main .scad (common, part modules) | COMPLIANT |
| Entry points and outputs | Assembly produces PNG only | asm-leg.png exists, asm-leg.stl absent | COMPLIANT |
| Entry points and outputs | Helper directory not built | no common.stl / common.png | COMPLIANT |
| Warnings gate | Warning fails build | gate-test: OK | COMPLIANT |
| Warnings gate | Gate-test proves the torque gate | gate-test: torque OK | COMPLIANT |
| repo-structure: Deferred scope excluded | No deferred artifacts | firmware/ and software/ hold only README.md | COMPLIANT |
| Deferred scope excluded | Only permitted CAD sources exist | every .scad is under smoke, common, leg-*, asm-leg | COMPLIANT |
| Deferred scope excluded | Shared params permitted in common | params.scad only at hardware/cad/common/ | COMPLIANT |

13 requirements, 24 scenarios (native heading count), 24/24 compliant.

### MODIFIED delta consistency with main specs
- cad-build "Entry points and outputs": delta keeps both original scenarios verbatim, adds the two new ones, states the original text via "Previously". Full requirement block, consistent.
- cad-build "Warnings gate": original sentence and scenario "Warning fails build" preserved verbatim; gate-test sentence and scenario added. Consistent.
- repo-structure "Deferred scope excluded": the main spec block still carries the older "MUST NOT add params.scad or real part designs" wording and its old scenarios (params.scad does not exist; only smoke part). Delta replaces both scenarios and the permit list (adds torque fixture, common/, leg-*, asm-leg). The replaced scenarios are now false by design, which is what MODIFIED is for. Other main requirements untouched. Consistent.
- Main specs under openspec/specs/ were not modified by this branch (archive will merge deltas).

### Torque re-derivation (independent, python from params.scad/torque.scad formulas)
m_total XS = 18*0.055 + 6*0.6*165/1000 + 0.52 = 2.104 kg; F 0.701 / 1.052 kgf; phi 20 deg.
- Femur static 5.776 / 6.60 = 1.143; peak 8.664 / 8.80 = **1.0156** (1.016 confirmed, 1.02 rounded); tibia static 1.919 / 6.60 (3.44), peak 2.878 / 8.80 (3.06). Matches the local make echo output and design.
- Tier rows S/M/L/XL and required-stall column (XS 10.83, S 12.24, M 17.82, L 25.05, XL 35.46) match docs/architecture/leg-torque-budget.md (rounded 10.8/12.2/17.8/25.0/35.5; L 25.05 shown as 25.0 is a rounding-half nit). Mass limit 2.137 kg (about +33 g) and femur_l 50 contingency (2.086 kg, 1.09) confirmed. Doc numbers all consistent with the code.
- Note: doc "Required stall" XS is 10.83 (peak-driven) and static-driven 9.63; the doc uses the worst, correct.

### Interference findings (scratch intersection tests, torque-model pose, not committed)
Reproduced exactly with a scratch scad (intersection of asm-leg objects, manifold backend):
| Pair | Overlap bbox (mm) | Location | Verdict |
|---|---|---|---|
| Femur servo vs femur plates (spacer bosses) | 9.0 x 37.0 x 19.7 | x 53-62 | Reproduced (servo body reaches +30.7 mm from femur axis; spacers at femur_l/2 = 27.5 mm sit in it) |
| Tibia (cage) vs coxa bracket (femur cage) | 4.7 x 43.6 x 12.9 | x 66.2-70.9, z 23.4-36.2 | Reproduced |
| Tibia servo vs coxa bracket | 1.2 x 37.0 x 3.0 | x 69.7-70.9 | additional sliver (same root cause as above) |
| Femur servo vs coxa bracket | 2.7 x 2.5 x 19.7 | x 13.1-15.8 | Reproduced (minor) |
| Coxa servo vs femur plates | 2.3 x 3.9 x 2.5 | x 14.6-16.9 | new minor (plate A end near the coxa servo ears) |
| Tibia vs femur servo | 0.2 x 2.5 x 0.5 | | sliver |
| Tibia vs femur plate | 13.0 x 0.0 x 13.0 | zero thickness | face contact only |
No overlap for: tibia servo vs tibia cage, tibia servo vs femur servo/plates, foot vs anything, coxa servo vs femur servo/tibia.

Severity: no spec scenario requires interference-free assembly (asm-leg is a preview; leg-design specs cover profile, gates, bed fit, naming). Therefore WARNING, not CRITICAL. They do invalidate the current STL set for printing/assembly.

**Are the printable parts safe to print? NO.** Do not print until (a) the interferences are fixed and (b) the real MG996R is measured (profile is provisional; every dimension P in the design). A fit test with the real servo is required regardless.

### Issues
**CRITICAL**: none.

**WARNING**
1. Femur servo body intersects femur-plate spacer bosses (9 x 37 x 19.7 mm). Fix: move the spacer bosses off the servo footprint (place at the far end of the plates, beyond femur_l + horn radius, or on the outer edge outside body_w) or shorten/relocate to clear x 0..30.7 along the femur; add a scratch/CI intersection gate in asm-leg to prove zero volume.
2. Tibia cage / servo intersect the coxa bracket femur cage (4.7 x 43.6 x 12.9 mm at phi 20 deg, plus 1.2 x 37 x 3 sliver). Fix: reduce the coxa-bracket cage extent toward +X (cb outer wall), or lengthen the femur (offset the tibia knee outward), or trim tibia knee cage on the inboard side; also check the swept range across phi, not just nominal.
3. Femur servo vs coxa bracket (2.7 x 2.5 x 19.7) and coxa servo vs femur plate A (2.3 x 3.9 x 2.5): minor; fix by enlarging body_clear / moving plate A inward or notching the bracket web.
4. Task 4.7 is unchecked in tasks.md although CI is green on PRs 9, 10, 11 (build pass). Tick it after merge chain decision.
5. Whole design rests on an unmeasured servo (provisional=true) with a 1.6% femur peak margin (1.016): a +33 g mass error fails CI (documented, accepted risk).

**SUGGESTION**
1. Add an interference check (scratch scad or make target) so assembly clashes fail CI; asm-leg is currently unchecked geometry.
2. Bed assert uses analytic size functions; add a non-CI mesh bbox check or comment linking them (mesh matches today).
3. Tier S also fails with MG996R (doc says so; design implied only M failing); consider a fixture for S too.
4. Foot TPU / PETG is documented only in hardware/cad/README.md; add a header comment in each part module for the scenario "part is documented".
5. apply-progress deviations (femur margin echo rounding 1.02 vs 1.016; servo_pocket default fix; femur_l 50 margin 1.09) are correctly reflected in docs.

### Design coherence
| Decision | Followed |
|---|---|
| Asserting getter profile format | Yes |
| No top-level instantiation in common | Yes (double include silent) |
| main.scad + module split | Yes |
| Torque fixture in gate-test | Yes |
| Datasheet 11.0 stall figure | Yes |
| `$preview` ghost servo | Yes (no % in exports; 0 warnings) |
| Deviations 1-5 (PR1), 1-6 (PR2), 1-4 (PR3) | Documented in apply-progress; none breaks a spec |
| Design glob `!common/servos/**` | Does not exclude in ripgrep; `!**/servos/**` used (design/tasks text should be corrected) |

### Verdict
PASS WITH WARNINGS. No spec violations; parts are NOT print-ready (interferences + unmeasured servo). Working tree left clean apart from this uncommitted report.
