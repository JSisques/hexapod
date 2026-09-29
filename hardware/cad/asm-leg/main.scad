// SPDX-License-Identifier: CC-BY-SA-4.0
// Leg assembly preview (PNG only, never exported to STL). Torque-model pose: femur horizontal along +X,
// tibia phi_nom from vertical. Real part geometry and real (provisional) servo solids, coloured per part.
// World frame: coxa axis = Z at the origin, femur axis along Y at x = coxa_l, z = cb_zmid.
include <BOSL2/std.scad>
include <../common/params.scad>
include <../leg-coxa-bracket/coxa-bracket.scad>
include <../leg-femur-plate/femur-plate.scad>
include <../leg-tibia/tibia.scad>
include <../leg-foot/foot.scad>

leg_part_checks("asm-leg");   // no bed assert: this is not a printable part

as_cage_depth = servo_cage_depth(servo);

// Femur servo frame: shaft toward -Y, cage floor and idler boss toward +Y.
module _femur_frame() { move([coxa_l, 0, cb_zmid]) xrot(90) children(); }
// Tibia servo frame: knee axis parallel to the femur axis, beam rotated phi_nom from vertical.
module _tibia_frame() { move([coxa_l + femur_l, 0, cb_zmid]) yrot(-90 - phi_nom) xrot(90) children(); }

// Coxa servo, body-mounted (body itself is out of scope); horn on the bracket top arm.
color("dimgray") move([0, 0, cb_case_top]) zrot(180) servo_model(servo);
color("orange") coxa_bracket();

_femur_frame() {
    color("dimgray") servo_model(servo);
    // Plate A on the horn side (inner face at the hub end), plate B on the idler side.
    color("steelblue") move([0, 0, sv(servo, "top_h")]) xrot(180) femur_plate_a();
    color("steelblue") move([0, 0, -(as_cage_depth + idler_boss_h)]) femur_plate_b();
}

_tibia_frame() {
    color("dimgray") servo_model(servo);
    color("orange") tibia();
    color("black") move([-tibia_l - ft_floor, 0, tb_zax]) yrot(90) foot();
}
