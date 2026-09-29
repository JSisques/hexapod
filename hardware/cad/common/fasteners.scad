// SPDX-License-Identifier: CC-BY-SA-4.0
// Fastener tables and cutters. Depends on kv_get (servo.scad) and tol_fit/eps (params.scad) at call time.
// Cutters grow +Z from the origin and overshoot by eps where they cross a face.

M3 = [["d", 3], ["clear", 3.4], ["nut_af", 5.5], ["nut_h", 2.4], ["head_d", 5.5], ["head_h", 3.0],
      ["insert_d", 4.1], ["insert_h", 5.7]];
M4 = [["d", 4], ["clear", 4.5], ["pivot", 4.4], ["nut_af", 7.0], ["nut_h", 3.2], ["nylock_h", 5.0],
      ["head_d", 7.0], ["head_h", 4.0]];

function fs(spec, key) = kv_get(spec, key, "fastener");

// Through hole of length l, centred on the origin along Z.
module screw_clear(spec, l, teardrop = false) {
    cyl(h = l, d = fs(spec, "clear"), teardrop = teardrop);
}

// Hex nut pocket of the given depth; across-corners diameter from across-flats plus tol_fit.
module nut_trap(spec, depth) {
    translate([0, 0, -eps])
        cylinder(h = depth + eps, d = (fs(spec, "nut_af") + tol_fit) / cos(30), $fn = 6);
}

// Heat-set insert pocket.
module insert_pocket(spec) {
    translate([0, 0, -eps])
        cylinder(h = fs(spec, "insert_h") + eps, d = fs(spec, "insert_d"));
}
