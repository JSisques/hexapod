// SPDX-License-Identifier: CC-BY-SA-4.0
// Coxa bracket (PETG). Frame: coxa axis = Z, bottom-arm underside at z = -cb_arm_t, femur axis along +Y at x = coxa_l.
// C-bracket around the body-mounted coxa servo (horn on the top arm, M4 pivot in the bottom arm) plus a cage for the femur servo.
include <../common/params.scad>
include <../leg-femur-plate/femur-plate.scad>   // leg_plate_a_relief()

cb_arm_d   = sv(servo, "horn_d") + 2 * wall;
cb_arm_t   = sv(servo, "horn_t") + tol_fit + wall;
cb_h       = leg_mount_gap + 2 * cb_arm_t;
cb_zmid    = leg_mount_gap / 2;
cb_cage_x  = servo_cage_x(servo) + [coxa_l, coxa_l];
cb_case_top = leg_mount_gap - sv(servo, "horn_t") - sv(servo, "top_h") - tol_loose;  // coxa servo case top face

// Femur servo frame: shaft toward -Y, cage floor and idler boss toward +Y, femur axis at x = coxa_l, z = cb_zmid.
module femur_servo_frame() move([coxa_l, leg_lane_dy, cb_zmid]) xrot(90) children();

module coxa_bracket() {
    difference() {
        union() {
            for (z0 = [-cb_arm_t, leg_mount_gap]) hull() {
                move([0, 0, z0]) cyl(h = cb_arm_t, d = cb_arm_d, anchor = BOTTOM);
                move([cb_cage_x[0] + wall, 0, z0]) cuboid([2 * wall, cb_arm_d, cb_arm_t], anchor = BOTTOM);
            }
            move([cb_cage_x[0] + wall, 0, -cb_arm_t]) cuboid([2 * wall, cb_arm_d, cb_h], anchor = BOTTOM);
            femur_servo_frame() servo_cage(servo);
        }
        // Coxa servo body and ear slab (near end outward), so the web clears them.
        move([0, 0, cb_case_top]) zrot(180) servo_pocket(servo);
        // Femur servo body and ear slab, so the web cannot overlap them.
        femur_servo_frame() servo_pocket(servo);
        // Plate A femur-end sweep (c3).
        move([coxa_l, leg_lane_dy, cb_zmid]) leg_plate_a_relief();
        // Horn recess and screws on the top arm underside.
        move([0, 0, leg_mount_gap]) horn_interface(servo, sv(servo, "horn_t") + tol_fit);
        // M4 pivot through the bottom arm, nut trap on its underside.
        move([0, 0, -cb_arm_t - eps]) cyl(h = cb_arm_t + 2 * eps, d = fs(leg_mount_pivot, "pivot"), anchor = BOTTOM);
        move([0, 0, -cb_arm_t]) nut_trap(leg_mount_pivot, fs(leg_mount_pivot, "nut_h"));
    }
}

// Print pose: bottom arm face on the bed.
module coxa_bracket_print() { up(cb_arm_t) coxa_bracket(); }
