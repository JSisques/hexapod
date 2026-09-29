// SPDX-License-Identifier: CC-BY-SA-4.0
// Tibia (PETG). Servo frame: knee axis = Z, beam toward -X, foot spigot at x = -tibia_l.
// The cage top wall and the beam top face share the plane z = tb_ztop, which lies on the bed in the print pose.
include <../common/params.scad>

tb_ztop  = sv(servo, "body_clear") + wall;
tb_h0    = 30;      // beam height at the cage
tb_h1    = 14;      // beam height and width at the spigot end
tb_x_end = -(tibia_l - leg_spigot_l);
tb_zax   = tb_ztop - tb_h1 / 2;

module tibia() {
    x0 = servo_cage_x(servo)[0];
    difference() {
        union() {
            servo_cage(servo);
            hull() {
                move([x0 - wall / 2 + eps, 0, tb_ztop - tb_h0 / 2]) cuboid([wall, servo_cage_w(servo), tb_h0]);
                move([tb_x_end, 0, tb_zax]) cuboid([eps, tb_h1, tb_h1]);
            }
            move([tb_x_end + eps, 0, tb_zax]) xcyl(l = leg_spigot_l + eps, d = leg_spigot_d, anchor = RIGHT);
        }
        // M3 cross pin through the spigot.
        move([tb_x_end - leg_spigot_l / 2, 0, tb_zax]) zcyl(l = leg_spigot_d + 2, d = fs(M3, "clear"));
    }
}

// Print pose: top wall and beam face on the bed, shaft axis vertical.
module tibia_print() { up(tb_ztop) xrot(180) tibia(); }
