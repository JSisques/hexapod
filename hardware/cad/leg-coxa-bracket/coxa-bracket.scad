// SPDX-License-Identifier: CC-BY-SA-4.0
// Coxa bracket (PETG). Frame: coxa axis = Z, bottom-arm underside at z = -cb_arm_t, femur axis along +Y at x = coxa_l.
// C-bracket around the body-mounted coxa servo (horn on the top arm, M4 pivot in the bottom arm) plus a cage for the femur servo.
// B1: the femur servo body points down (spun cb_femur_spin about its shaft), so the cage hangs below the femur axis and
// reaches below the bottom arm: bracket z-range [cb_zmin, cb_h - cb_arm_t]. The servo slides in from the open bottom
// rim and its cable leaves downward. Ear bolts run along world Y (heads on the plate A side, nuts trapped on the +Y floor).
// Ear-bolt heads: use low-profile heads (M3 button/low-cap) or fit the bolts with the nut on the plate A side; the near-end
// heads (r 15.24 mm) would otherwise protrude about 0.4 mm into the plate A sweep (r 15.5 mm). Heads are not modelled.
include <../common/params.scad>
include <../leg-femur-plate/femur-plate.scad>   // leg_plate_a_relief()

cb_arm_d   = sv(servo, "horn_d") + 2 * wall;
cb_arm_t   = sv(servo, "horn_t") + tol_fit + wall;
cb_h       = leg_mount_gap + 2 * cb_arm_t;
cb_zmid    = leg_mount_gap / 2;
cb_cage_hw = servo_cage_w(servo) / 2;                       // cage half-width across the femur axis (world X)
cb_web_x   = coxa_l - cb_cage_hw - wall;                     // web centre plane, abutting the cage side wall
cb_zmin    = cb_zmid - servo_cage_x(servo)[1];               // open bottom rim of the femur cage
cb_case_top = leg_mount_gap - sv(servo, "horn_t") - sv(servo, "top_h") - tol_loose;  // coxa servo case top face

// Femur servo frame: shaft toward -Y, cage floor and idler boss toward +Y, femur axis at x = coxa_l, z = cb_zmid.
// The spin maps the servo +X axis (far body end, slide-in slot, cable) to world -Z.
module femur_servo_frame() move([coxa_l, leg_lane_dy, cb_zmid]) xrot(90) zrot(cb_femur_spin) children();

module coxa_bracket() {
    difference() {
        union() {
            for (z0 = [-cb_arm_t, leg_mount_gap]) hull() {
                move([0, 0, z0]) cyl(h = cb_arm_t, d = cb_arm_d, anchor = BOTTOM);
                move([cb_web_x, 0, z0]) cuboid([2 * wall, cb_arm_d, cb_arm_t], anchor = BOTTOM);
            }
            move([cb_web_x, 0, cb_zmin]) cuboid([2 * wall, cb_arm_d, cb_h - cb_arm_t - cb_zmin], anchor = BOTTOM);
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

// Print pose: cage and web rim on the bed; the bottom arm then overhangs by -cb_zmin - cb_arm_t and needs supports.
module coxa_bracket_print() { up(-cb_zmin) coxa_bracket(); }
