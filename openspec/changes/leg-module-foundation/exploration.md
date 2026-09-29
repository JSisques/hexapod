# Exploration: leg-module-foundation

## Current State
- Makefile builds parts via `SRCS := $(wildcard hardware/cad/*/main.scad)`: flat, one level. A dir without `main.scad` (e.g. `common/`) is ignored; nested part dirs are NOT found (use hyphenated names such as `leg-coxa-bracket`).
- `--hardwarnings` plus stderr scan for `WARNING|ERROR`: an `assert()` failure fails the gate and CI; `echo()` goes to stderr, so echo text must not contain WARNING/ERROR. A part with empty geometry emits a WARNING.
- `OPENSCADPATH=libs` exposes only BOSL2; helpers are included relatively (`include <../common/params.scad>`); `-d` dep files track them.
- Blocking spec: `repo-structure` "Deferred scope excluded" forbids `params.scad` and any `.scad` besides smoke. `cad-build` "Entry points and outputs" conflicts with preview-only dirs if filtered.

## 1. Servo profile abstraction
Layout (non-part helper dir, never built):
```
hardware/cad/common/
  params.scad  servo.scad  torque.scad  fasteners.scad
  servos/mg996r.scad   servos/sts3215.scad (future)
```
Options: A prefixed variables (no namespacing) / **B function returning `[[key,value],...]` plus getter `sv(p,key)` with assert on missing key (recommended)** / C built on BOSL2 `struct_val` (silent undef, needs wrapper).
Fields: identity (`name`, `provisional`, `source`), body dims, ears (span, thickness, hole pattern, hole d), output shaft (offsets, height, spline teeth, horn PCD), cable exit, electrical (mass, stall torque per voltage, voltage, stall current, pulse range, range), clearances. Axis conventions are normalised in the profile file only.
Ghost models: BOSL2 `ghost()`/`%` never reach STL or `--render` PNGs; assembly previews need real coloured geometry in `asm-*` parts.
PROVISIONAL: `provisional=true` flag plus an echo (no WARNING word); a `release` gate is a follow-up. Do not fail default `make stl` on provisional profiles.

## 2. params.scad
In `hardware/cad/common/params.scad`. Sections: globals and tolerances (`tol_press` 0.10, `tol_fit` 0.20, `tol_loose` 0.40), fasteners (M3 clearance 3.4, nut 5.5+0.3, insert pocket ~4.0-4.2), material note (PETG default), leg geometry (`coxa_l`, `femur_l`, `tibia_l`, tier), chosen servo, torque inputs, `leg_mount_*` (the only interface the body must know), `bed_max`. One flat part dir per printable piece; mirrors and multiples are print-list metadata.

## 3. Leg mechanics
Coxa yaw, femur pitch, tibia pitch (18 servos). Proportions femur:tibia about 4:6 to 1:1.5. Pieces: coxa bracket, femur plates, tibia, TPU foot tip, spacers; each piece within ~150-180 mm. Bearing support (623/684) on the side opposite the servo for medium-large loads. M3 default (M4 for pivots); nuts for structural joints, heat-set inserts only where re-driven often. PETG default, TPU feet.

## 4. Torque budget (static screening model)
Tripod worst case: `F = (m_total/3) * k_dyn`; `tau_tibia = F*L_t*sin(phi)`, `tau_femur = F*(L_f*cos(alpha) + L_t*sin(phi))`; nominal phi 20 deg, stress 45 deg; allowable 60% stall static, 80% peak, k_dyn 1.5. Mass model is a guess (servo 55 g, links 0.6 g/mm), to be calibrated.

| Tier | Lf/Lt (mm) | m_total (kg) | femur static / peak (kg.cm) | femur rating needed at 60% |
|---|---|---|---|---|
| XS | 55/80 | 2.1 | 5.8 / 8.7 | 9.7 |
| S | 60/90 | 2.3 | 7.1 / 10.6 | 11.8 |
| M | 80/120 | 2.7 | 10.9 / 16.4 | 18.2 |
| L | 100/160 | 3.1 | 16.1 / 24.2 | 26.8 |
| XL | 130/200 | 3.7 | 24.3 / 36.5 | 40.5 |

Findings: MG996R (13 kg.cm at 6 V; 9 at 4.8 V) is feasible only at XS at a regulated 6 V; S is borderline; M/L/XL are NOT feasible. Femur is the limiter. STS3215 12 V (about 30 kg.cm, per retailer specs) covers M, L borderline; XL needs a 35+ kg.cm class. Stall-current sources disagree (1.3 A vs about 2.5 A at 6 V): use the higher for supply sizing until measured. Field reports say cheap MG996R clones underperform the datasheet.
Check location: **A `assert` in scad (fails the gate) plus B derivation doc `docs/architecture/leg-torque-budget.md` (recommended)**; default tier and servo in params must agree or the repo stops building.

## 5. Assembly preview vs export
**A: `asm-*` dirs are PNG-only (`STL_PARTS := $(filter-out asm-%,$(PARTS))`)** (recommended, needs cad-build delta) / B build everything / C mode variable.

## 6. Spec and CI impact
1. `repo-structure` MODIFIED "Deferred scope excluded": allow `hardware/cad/common/` and real part dirs (blocking).
2. `cad-build` MODIFIED "Entry points and outputs" if 5A; ADDED helper-dir convention.
3. Likely new capability spec (e.g. `leg-design`): profile fields, PROVISIONAL marker, torque gate, default tier/servo agreement.
4. `ci`, `repo-hygiene`, `licensing`, `decision-records`: no delta. Add ADR-0003 (servo abstraction, tier, fasteners); ADR-0001 stays immutable.
5. Update `hardware/cad/README.md` and `openspec/config.yaml` context.
Delivery: PR 1 = common lib, profile, params, torque check, ADR, spec deltas; PR 2 = first printable parts and `asm-*` preview.

## Risks
Default tier/servo mismatch breaks the build; MG996R dimensions unmeasured (pockets provisional, soft enforcement only); mass model guessed; static model is a screening check; echo/assert text must avoid WARNING/ERROR; `--render` PNGs show no ghosts; flat part glob; unknown printer bed (assert `bed_max`).

## Product decisions
1. Size tier and servo strategy. 2. Torque enforcement. 3. Preview convention. 4. Materials. 5. Fasteners. 6. PROVISIONAL enforcement. 7. Bed size. 8. Helper dir name. 9. Power (regulated 6 V for MG996R).
Ready for proposal once 1, 2 and 3 are answered.
