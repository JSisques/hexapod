// SPDX-License-Identifier: CC-BY-SA-4.0
// Femur plates A and B (PETG). Plate frame: inner face at z = 0, plate below, spacer bosses above.
// A carries the coxa and tibia servo horns; B carries the M4 pivots on the idler side.
include <../common/params.scad>

fp_d       = sv(servo, "horn_d") + 2 * wall;
fp_a_t     = sv(servo, "horn_t") + tol_fit + wall;
fp_b_t     = plate_t;
fp_spacer_h = leg_joint_span / 2;   // each plate carries half of the plate-to-plate distance
fp_spacer_d = fs(M3, "d") + 2 * wall;
fp_spacer_y = 8;
fp_gap      = 10;                   // print-pose distance between A and B

// Bounding box of the print pose: [x, y, z].
function femur_plate_size() =
    [femur_l + fp_d, 2 * fp_d + fp_gap, max(fp_a_t, fp_b_t) + fp_spacer_h];

module _fp_blank(t) {
    hull() for (x = [0, femur_l]) move([x, 0, -t]) cyl(h = t, d = fp_d, anchor = BOTTOM);
    for (y = [-fp_spacer_y, fp_spacer_y])
        move([femur_l / 2, y, -eps]) cyl(h = fp_spacer_h + eps, d = fp_spacer_d, anchor = BOTTOM);
}

// M3 spacer bolts from the outer face; A gets a head recess, B a nut trap.
module _fp_bolts(t, is_a) {
    for (y = [-fp_spacer_y, fp_spacer_y]) move([femur_l / 2, y, -t - eps]) {
        cyl(h = t + fp_spacer_h + 2 * eps, d = fs(M3, "clear"), anchor = BOTTOM);
        if (is_a) cyl(h = fs(M3, "head_h") + eps, d = fs(M3, "head_d") + tol_fit, anchor = BOTTOM);
        else nut_trap(M3, fs(M3, "nut_h") + 1);
    }
}

module femur_plate_a() {
    difference() {
        _fp_blank(fp_a_t);
        for (x = [0, femur_l]) move([x, 0, 0]) zflip() horn_interface(servo, sv(servo, "horn_t") + tol_fit);
        _fp_bolts(fp_a_t, true);
    }
}

module femur_plate_b() {
    difference() {
        _fp_blank(fp_b_t);
        for (x = [0, femur_l])
            move([x, 0, -fp_b_t - eps])
                cyl(h = fp_b_t + 2 * eps, d = fs(leg_mount_pivot, "pivot"), anchor = BOTTOM);
        _fp_bolts(fp_b_t, false);
    }
}

// Print pose: both plates outer face down, inner face and spacers up.
module femur_plate_print() {
    up(fp_a_t) femur_plate_a();
    move([0, fp_d + fp_gap, fp_b_t]) femur_plate_b();
}
