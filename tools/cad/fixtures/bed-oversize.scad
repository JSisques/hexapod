// SPDX-License-Identifier: MIT
// Intentional bed overflow for gate-test: the mesh bed gate must reject this part.
include <../../../hardware/cad/common/params.scad>
cube([bed_max + 10, 10, 10]);
