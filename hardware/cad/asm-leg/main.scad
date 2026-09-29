// SPDX-License-Identifier: CC-BY-SA-4.0
// Leg assembly preview (PNG only, never exported to STL). Torque-model pose: femur horizontal along +X,
// tibia phi_nom from vertical. Real part geometry and real (provisional) servo solids, coloured per part.
include <asm-leg.scad>

leg_part_checks("asm-leg");   // no bed check: this is not a printable part

asm_leg(alpha, phi_nom);
