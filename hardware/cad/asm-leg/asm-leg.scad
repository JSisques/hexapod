// SPDX-License-Identifier: CC-BY-SA-4.0
// Leg assembly library: posed bodies shared by the preview (main.scad) and the fit check (fit.scad).
// No top-level instantiation. World frame: coxa axis = Z at the origin, femur axis along Y at x = coxa_l, z = cb_zmid.
// alpha = femur pitch (knee up > 0). phi = knee joint angle from the femur-plate normal; at alpha = 0 it is the torque-model phi.
include <BOSL2/std.scad>
include <../common/params.scad>
include <../leg-coxa-bracket/coxa-bracket.scad>
include <../leg-femur-plate/femur-plate.scad>
include <../leg-tibia/tibia.scad>
include <../leg-foot/foot.scad>

asm_bodies = ["coxa-servo", "coxa-bracket", "femur-servo", "femur-plate-a", "femur-plate-b", "tibia-servo", "tibia", "foot"];
asm_colors = [["coxa-servo", "dimgray"], ["coxa-bracket", "orange"], ["femur-servo", "dimgray"], ["femur-plate-a", "steelblue"],
              ["femur-plate-b", "steelblue"], ["tibia-servo", "dimgray"], ["tibia", "orange"], ["foot", "black"]];

as_cage_depth = servo_cage_depth(servo);

// Femur servo frame (fixed in the bracket): shaft toward -Y, cage floor and idler boss toward +Y.
module asm_femur_servo_frame() move([coxa_l, leg_lane_dy, cb_zmid]) xrot(90) children();
// Femur link frame: the femur servo frame pitched by alpha about the femur axis.
module asm_link_frame(alpha) move([coxa_l, leg_lane_dy, cb_zmid]) yrot(-alpha) xrot(90) children();
// Tibia servo frame: knee axis parallel to the femur axis, beam rotated by the knee angle phi.
module asm_tibia_frame(alpha, phi) move([coxa_l, leg_lane_dy, cb_zmid]) yrot(-alpha) move([femur_l, 0, 0]) yrot(-90 - phi) xrot(90) children();

// One posed body by name; an unknown name is an error.
module asm_body(name, alpha, phi) {
    if (name == "coxa-servo") move([0, 0, cb_case_top]) zrot(180) servo_model(servo);
    else if (name == "coxa-bracket") coxa_bracket();
    else if (name == "femur-servo") asm_femur_servo_frame() servo_model(servo);
    else if (name == "femur-plate-a") asm_link_frame(alpha) move([0, 0, sv(servo, "top_h")]) xrot(180) femur_plate_a();
    else if (name == "femur-plate-b") asm_link_frame(alpha) move([0, 0, -(as_cage_depth + idler_boss_h)]) femur_plate_b();
    else if (name == "tibia-servo") asm_tibia_frame(alpha, phi) servo_model(servo);
    else if (name == "tibia") asm_tibia_frame(alpha, phi) tibia();
    else if (name == "foot") asm_tibia_frame(alpha, phi) move([-tibia_l - ft_floor, 0, tb_zax]) yrot(90) foot();
    else assert(false, str("asm body: unknown name ", name));
}

module asm_leg(alpha, phi) for (b = asm_bodies) color(kv_get(asm_colors, b, "asm colour")) asm_body(b, alpha, phi);
