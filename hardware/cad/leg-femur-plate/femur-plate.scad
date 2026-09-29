// SPDX-License-Identifier: CC-BY-SA-4.0
// Femur plates A and B (PETG): flat two-disc hulls, no spacers. Plate frame: inner face at z = 0, plate below.
// A carries the coxa and tibia servo horns; B carries the M4 pivots on the idler side.
// The servo cage and the idler boss set the plate-to-plate distance (leg_joint_span); no bolts join the plates.
include <../common/params.scad>

fp_d    = leg_plate_d;
fp_a_t  = leg_plate_a_t;
fp_b_t  = plate_t;
fp_gap  = 10;                   // print-pose distance between A and B

module _fp_blank(t) {
    hull() for (x = [0, femur_l]) move([x, 0, -t]) cyl(h = t, d = fp_d, anchor = BOTTOM);
}

module femur_plate_a() {
    difference() {
        _fp_blank(fp_a_t);
        for (x = [0, femur_l]) move([x, 0, 0]) zflip() horn_interface(servo, sv(servo, "horn_t") + tol_fit);
    }
}

module femur_plate_b() {
    difference() {
        _fp_blank(fp_b_t);
        for (x = [0, femur_l])
            move([x, 0, -fp_b_t - eps])
                cyl(h = fp_b_t + 2 * eps, d = fs(leg_mount_pivot, "pivot"), anchor = BOTTOM);
    }
}

// Cutter for the coxa bracket: the sweep of the plate A femur-end disc about the femur axis, over the plate A
// lane plus tol_loose on each side. Frame: origin on the femur axis at the lane offset, axis along world Y;
// plate A sits at y = -(top_h .. top_h + fp_a_t) from that origin.
module leg_plate_a_relief() {
    move([0, -sv(servo, "top_h") - fp_a_t / 2, 0]) ycyl(h = fp_a_t + 2 * tol_loose, d = fp_d + 2 * tol_loose);
}

// Print pose: both plates outer face down, inner face up.
module femur_plate_print() {
    up(fp_a_t) femur_plate_a();
    move([0, fp_d + fp_gap, fp_b_t]) femur_plate_b();
}
