// SPDX-License-Identifier: CC-BY-SA-4.0
// Global leg parameters. Side-effect free: no top-level instantiation, safe to include more than once.
// Every servo-dependent value is PROVISIONAL until the servo is measured (see servos/mg996r.scad).
include <BOSL2/std.scad>
include <servos/mg996r.scad>
include <servo.scad>
include <fasteners.scad>
include <torque.scad>

// Tolerances and render quality (mm)
tol_press = 0.10;
tol_fit   = 0.20;
tol_loose = 0.40;
eps       = 0.01;
$fa = 2;
$fs = 0.4;
wall    = 3.0;
plate_t = 4.0;

// Materials
material_default = "PETG";
material_foot    = "TPU";

// Tiers: [coxa, femur, tibia] in mm
leg_tiers = [["XS", [30, 55, 80]], ["S", [30, 60, 90]], ["M", [35, 80, 120]],
             ["L", [40, 100, 160]], ["XL", [45, 130, 200]]];
function leg_lengths(tier) = kv_get(leg_tiers, tier, "leg tier table");

leg_tier = "XS";
coxa_l   = leg_lengths(leg_tier)[0];
femur_l  = leg_lengths(leg_tier)[1];
tibia_l  = leg_lengths(leg_tier)[2];

servo = mg996r();

// Torque model inputs (guesses until calibrated; see docs/architecture/leg-torque-budget.md)
supply_v      = 6.0;
n_servo       = 18;
link_g_per_mm = 0.6;
m_body_kg     = 0.52;   // body + electronics + battery, guess
k_dyn         = 1.5;
phi_nom       = 20;
phi_stress    = 45;     // echo only, not asserted
alpha         = 0;
derate_static = 0.6;
derate_peak   = 0.8;
check_torque  = true;

// Leg mount interface
leg_mount_gap   = sv(servo, "body_h") + sv(servo, "top_h") + sv(servo, "horn_t") + 2 * tol_loose;
leg_mount_pivot = M4;
idler_boss_h    = 4.0;   // idler boss below a servo cage floor
leg_spigot_d    = 10.0;  // tibia spigot that carries the foot
leg_spigot_l    = 12.0;
// Distance between the two femur plate inner faces: horn-side plate face to idler boss end face.
leg_joint_span  = sv(servo, "top_h") + servo_cage_depth(servo) + idler_boss_h;

bed_max = 180;

// Per-part checks, called from a part's main.scad: provisional echo, torque gate, bed fit.
module leg_part_checks(name, size = undef) {
    echo(str("leg part: ", name));
    servo_provisional_echo(servo);
    if (check_torque) leg_torque_gate();
    else echo("torque gate skipped (check_torque=false)");
    if (size != undef)
        assert(max(size) <= bed_max,
               str(name, ": part size ", size, " exceeds bed_max ", bed_max, " mm"));
}
