// SPDX-License-Identifier: CC-BY-SA-4.0
// Servo helpers: asserting profile getter, preview solid and cutters. Side-effect free.
// Profile frame: Z = shaft up, origin on shaft axis at case top face, +X toward the far body end.
include <BOSL2/std.scad>
include <fasteners.scad>

function kv_get(table, key, what = "table") =
    let(hits = [for (kv = table) if (kv[0] == key) kv[1]])
    assert(len(hits) == 1, str(what, ": key not found or duplicated: ", key))
    hits[0];

// Profile getter; the profile name is its first pair.
function sv(p, key) = kv_get(p, key, str("servo profile ", p[0][1]));

function servo_stall_kgcm(p, v) =
    let(hits = [for (r = sv(p, "stall_kgcm")) if (r[0] == v) r[1]])
    assert(len(hits) == 1, str("servo profile ", p[0][1], ": no stall torque rated at ", v, " V"))
    hits[0];

// X of the case centre, Z of the ear mid-plane.
function _servo_cx(p) = -sv(p, "shaft_offset_x") + sv(p, "body_l") / 2;
function _servo_ear_zc(p) = sv(p, "ear_top_z") - sv(p, "ear_t") / 2;

// Real solid for previews and assemblies: case, ears, hub and spline. Uncoloured.
module servo_model(p) {
    bl = sv(p, "body_l"); bw = sv(p, "body_w"); bh = sv(p, "body_h");
    cx = _servo_cx(p);
    move([cx, 0, -bh / 2]) cuboid([bl, bw, bh]);
    difference() {
        move([cx, 0, _servo_ear_zc(p)]) cuboid([sv(p, "ear_span"), bw, sv(p, "ear_t")]);
        servo_ear_holes(p, sv(p, "ear_t") + 2 * eps, spec = [["clear", sv(p, "ear_hole_d")]]);
    }
    cyl(h = sv(p, "top_h"), d = bw / 2, anchor = BOTTOM);
    cyl(h = sv(p, "top_h") + sv(p, "horn_t"), d = sv(p, "spline_od"), anchor = BOTTOM);
}

// Body pocket (+ body_clear), open toward -Z (insertion side) with a cable slot at the +X end.
// A module default cannot reference an earlier parameter, so clear = undef means the profile body_clear.
module servo_pocket(p, clear = undef, extra_top = 0) {
    c = is_undef(clear) ? sv(p, "body_clear") : clear;
    bl = sv(p, "body_l"); bw = sv(p, "body_w"); bh = sv(p, "body_h");
    cx = _servo_cx(p);
    top = c + extra_top;
    // Case, from the top face (plus cance) down through the open -Z side.
    move([cx, 0, (top - bh - c - eps) / 2])
        cuboid([bl + 2 * c, bw + 2 * c, top + bh + c + eps]);
    // Ear slab slot.
    move([cx, 0, _servo_ear_zc(p)])
        cuboid([sv(p, "ear_span") + 2 * c, bw + 2 * c, sv(p, "ear_t") + 2 * c]);
    // Cable slot through the +X end.
    move([cx + bl / 2, 0, sv(p, "cable_exit_z")])
        cuboid([2 * c + 2 * wall, sv(p, "cable_exit_w"), sv(p, "cable_exit_w")]);
}

// Four through cutters of length l on the ear hole pattern, centred on the ear mid-plane.
module servo_ear_holes(p, l, spec = M3) {
    px = sv(p, "ear_hole_pitch_l") / 2; py = sv(p, "ear_hole_pitch_w") / 2;
    for (sx = [-1, 1], sy = [-1, 1])
        move([_servo_cx(p) + sx * px, sy * py, _servo_ear_zc(p)])
            cyl(h = l, d = fs(spec, "clear"));
}

// Horn disc recess and screw holes. Origin on the link face that meets the horn; cutters grow +Z.
module horn_interface(p, depth) {
    n = sv(p, "horn_hole_n");
    // Disc recess, overshooting the face by eps.
    move([0, 0, -eps]) cyl(h = depth + eps, d = sv(p, "horn_d") + tol_fit, anchor = BOTTOM);
    // Centre clearance and PCD screw holes, through the link.
    move([0, 0, -eps]) cyl(h = depth + wall + 2 * eps, d = sv(p, "horn_center_clear_d"), anchor = BOTTOM);
    for (i = [0 : n - 1])
        zrot(360 * i / n)
            move([sv(p, "horn_hole_pcd") / 2, 0, -eps])
                cyl(h = depth + wall + 2 * eps, d = sv(p, "horn_screw_d") + tol_fit, anchor = BOTTOM);
}

module servo_provisional_echo(p) {
    if (sv(p, "provisional"))
        echo(str("servo profile ", sv(p, "name"),
                 " is PROVISIONAL: dimensions unmeasured, measure the servo before printing"));
}

// Cage geometry in the servo frame: X extent [min, max], overall width (Y) and the depth from the
// case top face to the underside of the cage floor.
function servo_cage_x(p) =
    let(h = sv(p, "ear_span") / 2 + sv(p, "body_clear") + wall)
    [_servo_cx(p) - h, _servo_cx(p) + h];
function servo_cage_w(p) = sv(p, "body_w") + 2 * (sv(p, "body_clear") + wall);
function servo_cage_depth(p) = sv(p, "body_h") + sv(p, "body_clear") + wall;

// Printable cage around the servo body. The servo slides in through the +X end; ear bolts run along Z
// with nuts trapped in the floor underside; an idler boss with a pivot hole and nut recess sits below
// the floor, coaxial with the shaft. Cage top wall is at z = body_clear + wall.
module servo_cage(p, spec = M3) {
    c = sv(p, "body_clear"); bw = sv(p, "body_w"); bh = sv(p, "body_h");
    cx = _servo_cx(p);
    cl = servo_cage_x(p)[1] - servo_cage_x(p)[0];
    zf = -servo_cage_depth(p);
    pv = leg_mount_pivot;
    difference() {
        union() {
            move([cx, 0, -bh / 2]) cuboid([cl, servo_cage_w(p), bh + 2 * (c + wall)]);
            move([0, 0, zf + eps]) cyl(h = idler_boss_h + eps, d = fs(pv, "head_d") + 2 * wall, anchor = TOP);
        }
        servo_pocket(p);
        // Slide-in slot through the +X end, full pocket width.
        move([cx, 0, -bh / 2]) cuboid([cl / 2 + eps, bw + 2 * c, bh + 2 * c], anchor = LEFT);
        // Hub hole through the top wall.
        move([0, 0, c - eps]) cyl(h = wall + 2 * eps, d = bw / 2 + 2 * tol_loose, anchor = BOTTOM);
        // Ear bolts, with nut traps on the floor underside.
        servo_ear_holes(p, 2 * bh, spec);
        for (sx = [-1, 1], sy = [-1, 1])
            move([cx + sx * sv(p, "ear_hole_pitch_l") / 2, sy * sv(p, "ear_hole_pitch_w") / 2, zf])
                nut_trap(spec, fs(spec, "nut_h") + 1);
        // Idler pivot hole and nut recess in the boss end face.
        move([0, 0, zf - idler_boss_h - eps])
            cyl(h = idler_boss_h + wall + 2 * eps, d = fs(pv, "pivot"), anchor = BOTTOM);
        move([0, 0, zf - idler_boss_h]) nut_trap(pv, fs(pv, "nylock_h"));
    }
}
