# Roadmap

This is a living plan, not a commitment. Each phase names the SDD change that would deliver it, what it needs first, and the exit criteria that tell us it is done. Dates are deliberately absent: the critical path depends on parts arriving and on physical measurements.

Last updated: 2026-09-29.

## Where we are

| Area | State |
| --- | --- |
| Repository, licensing, ADRs | Done (ADR-0001) |
| OpenSCAD toolchain, CI, warnings gate | Done (ADR-0002) |
| Leg module (tier XS, provisional MG996R profile), torque gate | Done, modelled only (ADR-0003) |
| Mesh bed gate, assembly `check-fit` | Done (ADR-0004) |
| Anything physical (printed parts, measured servo, tests) | **Not started** |
| Body, electronics, firmware, software, vision | Not started |

Known limits carried forward: the MG996R profile is PROVISIONAL and unmeasured, `check-fit` is an interference gate and not a fit certificate, the femur peak torque margin is 1.02, and the flat femur plates are not yet validated for stiffness. **Nothing should be printed until Phase 1 step 1 is done.**

## Dependency map

```
Phase 1  Validate the leg (physical)  ──┬──> Phase 3  Body ──> Phase 5  Firmware on hardware ──> Phase 6  Vision
                                        │         ^                    ^
Phase 2  Kinematics + simulation ───────┼─────────┘                    │
         (no hardware needed)           │                              │
                                        └──> Phase 4  Electronics + power ──┘

Phase 7  Medium-large tier (stronger servo)  <── needs Phase 1 measurements; can start once Phase 3 defines the body
```

Phases 1 and 2 are independent and can run in parallel. That is the main lever for keeping momentum while parts ship.

## Phase 1 — Validate the leg (physical)

Goal: replace every provisional number with a measured one, and prove one leg works before building six.

Change: `leg-validation` (mostly docs and profile updates, with a small amount of code).

1. Order one pack of 4 MG996R-class servos (3 for the leg plus a spare). Measure with calipers: body, ear span and hole pattern, hole diameter, shaft offset and height, spline, horn. Update `hardware/cad/common/servos/mg996r.scad`, flip `provisional` to false with a dated `source`, and re-run `make check-fit` and `make gate-test`.
2. Weigh the servos and, once printed, the parts. Calibrate `link_g_per_mm` and `m_body_kg` in the torque model against real mass.
3. Print the four leg parts (PETG; TPU foot). The coxa bracket needs supports for its 12.1 mm overhang. Do a dry fit before adding servos.
4. Assemble one leg on a bench, powered from a regulated 6 V supply (never 7.4 V: it exceeds the servo maximum). Drive it with a servo tester.
5. Test: does it lift and hold its share of the estimated robot weight, how much play is there at each joint, are the flat plates stiff enough, do the servos overheat.

Exit criteria: measured servo profile committed; check-fit green on the measured profile; one leg holds the tripod-stance load at 6 V without stalling; findings recorded in an ADR or a torque-budget update. If the leg fails, the outcome is a decision (stronger servo, shorter leg, redesign), not a silent workaround.

Decision gate after this phase: **stay on MG996R at tier XS, or move up.** The torque analysis says medium-large tiers are not feasible with MG996R, so this gate decides how the rest of the roadmap is sized.

## Phase 2 — Kinematics and simulation (no hardware)

Goal: the software brain of the leg and the gait, testable without any robot.

Change: `kinematics-and-gait` (opens a `software/` toolchain).

1. Pick language and tooling (recommendation: Python with `pytest`; simulation with a lightweight 3D visualiser first, a physics engine later). Record in an ADR. Add CI for it (lint, unit tests) next to the CAD job.
2. Forward and inverse kinematics for one 3-DOF leg, taking link lengths and joint limits from the same numbers as `params.scad` (single source of truth, not copies).
3. Body kinematics for six legs: stance pose, body translation and rotation.
4. Tripod gait generator, then wave and ripple gaits.
5. Simulation: visualise the gait, and check joint angles against the servo range and the torque gate's poses.

Exit criteria: unit-tested IK/FK; a simulated tripod walk; joint limits checked against `fit_alpha` and `fit_phi` sweep ranges so software and CAD agree on the leg's reachable poses.

## Phase 3 — Body

Goal: a body that mounts six legs and everything else.

Change: `body-module` (extends `hardware/cad/`), likely two or three chained PRs.

1. Decide size and shape (hexagonal, leg mount radius, plate stack). Body size drives leg spacing and therefore stability.
2. Design around the leg-mount interface recorded in ADR-0004 and the README: the bracket z-range and the keep-out below its bottom arm are constraints on the body.
3. Electronics bay, battery bay, and cable routing from the start; retrofitting them is expensive.
4. Add a full-robot assembly preview and extend `check-fit` (six legs, plus body versus legs over the coxa sweep).
5. Re-run the torque gate with the real body mass, replacing the `m_body_kg` estimate.

Exit criteria: body prints in pieces under `bed_max`; six-leg assembly has no interference across the sweep; torque gate green at the real total mass.

## Phase 4 — Electronics and power

Goal: everything that moves and thinks has power and wiring that does not brown out.

Change: `electronics-v1` (extends `hardware/electronics/` and `hardware/bom/`).

1. Compute and servo driver architecture. Current recommendation: Raspberry Pi for high-level control and vision, with two PCA9685 boards (16 channels each) for the 18 servos. Alternative if better servos are chosen: a serial-bus servo adapter (fewer wires, position and current feedback). This is a real fork, decided in an ADR.
2. Power budget from measured stall and running currents in Phase 1, not from datasheets. 18 servos at a 6 V rail need a high-current regulator and thick wiring; size with margin and add fusing.
3. Battery choice (chemistry, capacity, protection) and a physical power switch and emergency cut.
4. Wiring harness and connector standard; BOM as `bom.csv`.
5. Electronics tooling decision (KiCad recommended, text-diffable) if a PCB is wanted.

Exit criteria: power budget measured with a full leg load; BOM complete; a wiring diagram in `docs/`.

## Phase 5 — Firmware and control on hardware

Goal: the robot stands, sits and walks.

Change: `firmware-v1` (uses `firmware/`), plus integration with Phase 2 software.

1. Servo driver layer (hardware abstraction) so servo type can change without touching the gait code, mirroring the servo-profile idea on the CAD side.
2. Calibration routine: per-joint offsets and limits stored in the repo or on the robot.
3. Stand, sit, then single-leg motion, then tripod walk. Each step gated by a safety check (current limit, watchdog, soft joint limits).
4. Teleoperation (gamepad or web).

Exit criteria: robot stands unassisted for ten minutes without overheating; a straight tripod walk of a few metres.

## Phase 6 — Vision and autonomy

Goal: the reason for choosing a Raspberry Pi.

Change: `vision-v1`.

1. Camera mount in the body design (an early Phase 3 provision, even if unused).
2. Camera pipeline, latency budget, thermal check.
3. First capability, the simplest useful one (obstacle avoidance or following a marker), before anything ambitious.
4. Decide on ROS 2 versus a lightweight stack once the first capability exists; do not adopt it speculatively.

Exit criteria: one vision-driven behaviour running on the robot.

## Phase 7 — Medium-large tier (upgrade path)

Goal: the size you originally wanted.

Change: `tier-m-upgrade`.

Not feasible with MG996R: femur torque at tier M is roughly 18 kg·cm rated stall needed against a 11–13 kg·cm servo. A servo in the 20–30 kg·cm class (for example a 12 V bus servo) is needed. Because of the servo-profile abstraction the change should be mostly:

1. A new servo profile file, a new tier in `params.scad`, new fasteners or horn adaptors as needed.
2. Re-run the torque gate and `check-fit`; expect part geometry changes, since a bigger servo changes pockets and cages.
3. Power and driver changes if the servo type changes (Phase 4 rework).

Exit criteria: torque gate and `check-fit` green at tier M with the measured profile; one leg validated as in Phase 1.

## Cross-cutting work (any time)

- **Releases:** attach STLs to a GitHub Release from a tag, so printable parts are downloadable without building. Today STLs are only short-lived CI artifacts.
- **Build guide:** `docs/build-guide/` grows with every phase: print list (parts ×6 legs), assembly steps, wiring.
- **Measured clearance:** `check-fit` reports overlap volume only. A minimum-distance report and FDM clearance rule (0.2–0.4 mm) would turn it into a fit check.
- **Red-CI proof:** show once, on a scratch branch, that an interference actually fails CI.
- **Housekeeping:** enable Dependabot for actions, delete merged branches automatically, keep the pinned OpenSCAD image and BOSL2 SHA under review, get Engram working again for session memory.

## Risk register

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| MG996R clone under-delivers torque | Femur peak margin is 1.02; a clone is below datasheet | Phase 1 measures before anything else; the gate blocks unsafe parameter changes |
| Servo dimensions differ from the profile | Every pocket and ear hole depends on it | Measure first; `check-fit` re-run; never print on provisional data |
| Power sag or brownout with 18 servos | Erratic behaviour, damaged hardware | Measured current budget, regulator margin, fusing, staged bring-up (one leg first) |
| Flat plates too flexible | Spacers were removed to fix interference | Physical test in Phase 1; if weak, revisit with outboard ties |
| Scope creep into vision/autonomy too early | Motivating but depends on a walking robot | Keep Phase 6 behind Phase 5 exit criteria |
| CI time growth | `check-fit` already 1–2 minutes | Watch runtime; parallelise poses if it passes ~5 minutes |

## Open decisions

| Decision | Needed by | Current recommendation |
| --- | --- | --- |
| Keep MG996R or move to a stronger servo | End of Phase 1 | Decide from measured torque, not from the datasheet |
| Software language and simulator | Start of Phase 2 | Python, lightweight visualiser first |
| Body size and shape | Start of Phase 3 | Derive from the chosen tier and leg reach |
| Compute and driver architecture | Start of Phase 4 | Raspberry Pi plus PCA9685; revisit if serial-bus servos are chosen |
| Battery chemistry and capacity | Phase 4 | Size from the measured power budget |
| ROS 2 or lightweight stack | After the first vision behaviour | Defer |
| Public release of STLs (GitHub Releases) | Any time | Do it once a measured, printed leg exists |

## Suggested next step

Order the servo pack and start Phase 2 while it ships. Phase 1 step 1 (measuring) unblocks the physical path, and Phase 2 needs nothing but a laptop.
