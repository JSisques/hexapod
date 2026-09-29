# Tasks: Leg Module Foundation

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | PR1 ~340, PR2 ~280, PR3 ~270 (total ~890) |
| 400-line budget risk | High (total); Medium for PR1 |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 -> PR 2 -> PR 3 |
| Delivery strategy | ask-on-risk |
| Chain strategy | feature-branch-chain |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

PR1 with ADR-0003 is ~420 (> 400), so ADR-0003 and its index row move to PR3 (design rule). Bases: PR1 = tracker branch (from `main`); PR2 = PR1 branch; PR3 = PR2 branch.

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Common lib, MG996R profile, torque gate, fixture, Makefile | PR 1 | `make gate-test` | `make help` | `hardware/cad/common/`, fixture, Makefile |
| 2 | Four printable parts | PR 2 | `make stl` | `make render` | `hardware/cad/leg-*/` |
| 3 | asm-leg, torque doc, ADR, READMEs, config | PR 3 | `make render` | CI run | `asm-leg/`, `docs/`, README, config |

## Phase 1: Foundation (PR 1)

- [x] 1.1 Create `hardware/cad/common/servos/mg996r.scad`: `mg996r()` with all design-table keys, `provisional=true`.
- [x] 1.2 Create `hardware/cad/common/servo.scad`: `kv_get`, `sv`, `servo_stall_kgcm`, `servo_model`, `servo_pocket`, `servo_ear_holes`, `horn_interface`, `servo_provisional_echo`.
- [x] 1.3 Create `hardware/cad/common/fasteners.scad`: `M3`, `M4`, `fs`, `screw_clear`, `nut_trap`, `insert_pocket`.
- [x] 1.4 Create `hardware/cad/common/torque.scad`: formulas, `torque_rows`, `leg_torque_gate` (one assert per row, message `torque budget exceeded: ...`).
- [x] 1.5 Create `hardware/cad/common/params.scad`: tolerances, tiers, XS defaults, `servo`, torque inputs, `bed_max`, `leg_part_checks`; no top-level instantiation.
- [x] 1.6 Create `tools/cad/fixtures/torque-infeasible.scad` (tier M gate + `cube(1)`).
- [x] 1.7 Modify `Makefile`: `STL_PARTS` filter-out `asm-%`, help text, `gate-test` torque step.
- [x] 1.8 Apply-time check: `-D` overrides and a double `include` of `params.scad` emit no WARNING (scratch file).
- [x] 1.9 Apply-time check: every BOSL2 call used exists at pinned SHA `402be42` (`rg` in `libs/BOSL2`).

## Phase 2: Printable Parts (PR 2)

- [ ] 2.1 Create `hardware/cad/leg-coxa-bracket/{coxa-bracket,main}.scad` (C-bracket, femur cage, M4 idler).
- [ ] 2.2 Create `hardware/cad/leg-femur-plate/{femur-plate,main}.scad` (plates A+B, spacers).
- [ ] 2.3 Create `hardware/cad/leg-tibia/{tibia,main}.scad` (knee cage, beam, spigot).
- [ ] 2.4 Create `hardware/cad/leg-foot/{foot,main}.scad` (TPU socket, sphere tip).
- [ ] 2.5 Apply-time check: measure each part envelope from STL bounds; `max(size) <= bed_max` (180) and matches design estimate.
- [ ] 2.6 Run hard-coded dimension scan: `rg -n '40\.7|19\.7|54\.5|49\.5' hardware/cad --glob '!common/servos/**'` returns nothing.

## Phase 3: Assembly, Docs (PR 3)

- [ ] 3.1 Create `hardware/cad/asm-leg/main.scad` (coloured torque-model pose, no bed assert).
- [ ] 3.2 Apply-time check: colours survive in `build/png/asm-leg.png` with `--render`; monochrome is acceptable, record result.
- [ ] 3.3 Create `docs/architecture/leg-torque-budget.md` (recompute margins from `params.scad`).
- [ ] 3.4 Create `docs/adr/0003-leg-servo-abstraction-and-tiers.md` and add the row to `docs/adr/README.md`.
- [ ] 3.5 Modify `hardware/cad/README.md` (conventions, PROVISIONAL, torque gate, materials) and `openspec/config.yaml` (context line).

## Phase 4: Verification (each PR, cumulative)

- [ ] 4.1 `make clean stl render`: exit 0, no `WARNING|ERROR`; `eza build/stl build/png` shows 4 leg STLs, no `asm-leg.stl`, `asm-leg.png` present (PR3).
- [x] 4.2 `make gate-test` prints both `OK` lines.
- [ ] 4.3 Infeasible proof: `OPENSCADPATH=libs openscad --hardwarnings -D 'leg_tier="M"' -o $SCRATCH/x.stl hardware/cad/leg-tibia/main.scad` fails with `torque budget exceeded`.
- [ ] 4.4 `rg PROVISIONAL build/log/stl/leg-tibia.log` matches; missing-key scratch test asserts `key not found`.
- [ ] 4.5 `touch hardware/cad/common/params.scad && make stl` rebuilds leg STLs.
- [x] 4.6 `make help` lists asm-* PNG-only text; `git check-ignore build` succeeds. (PR 1 scope verified)
- [ ] 4.7 Push each PR and confirm the CI run is green (gate-test, stl, render artifacts).
