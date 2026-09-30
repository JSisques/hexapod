// SPDX-License-Identifier: CC-BY-SA-4.0
// Parameter exporter for the software package (see docs/adr/0005-software-tooling-and-parameter-bridge.md).
// Evaluates the leg assembly libraries and echoes one key/value record, `hexapod_params`.
// tools/cad/echo-to-json.py turns the echo into the committed snapshot; do not edit that JSON by hand.
// No geometry is produced. Run through `make params` / `make check-params`, never directly.
include <../../hardware/cad/asm-leg/asm-leg.scad>

// Foot-sphere centre in the leg frame for one pose (alpha, phi in degrees).
// This repeats the transform chain of asm_tibia_frame() plus the "foot" placement in asm_body()
// (hardware/cad/asm-leg/asm-leg.scad); keep the two in sync. Software tests compare its FK to these points.
function foot_centre(a, p) =
    apply(move([coxa_l, leg_lane_dy, cb_zmid]) * yrot(-a) * move([femur_l, 0, 0]) * yrot(-90 - p) * xrot(90)
          * move([-tibia_l - ft_floor, 0, tb_zax]) * yrot(90), [0, 0, ft_r]);

function rnd(x) = round(x * 1e6) / 1e6;

params = [
    ["schema_version", 1],
    ["generator", "tools/cad/export-params.scad"],
    ["license", "CC-BY-SA-4.0"],
    ["provisional", sv(servo, "provisional") ? ["servo"] : []],
    ["leg", [
        ["tier", leg_tier],
        ["coxa_l", coxa_l], ["femur_l", femur_l], ["tibia_l", tibia_l],
        ["leg_lane_dy", leg_lane_dy], ["cb_zmid", cb_zmid], ["tb_zax", tb_zax],
        ["ft_r", ft_r], ["ft_floor", ft_floor],
        ["knee_to_foot", tibia_l + ft_floor - ft_r],   // foot-sphere centre distance from the knee axis
        ["foot_dy", leg_lane_dy - tb_zax]               // lateral foot offset in the leg frame
    ]],
    ["limits", [["fit_alpha", fit_alpha], ["fit_phi", fit_phi]]],
    ["servo", [
        ["name", sv(servo, "name")], ["provisional", sv(servo, "provisional")],
        ["range_deg", sv(servo, "range_deg")], ["pulse_us", sv(servo, "pulse_us")],
        ["mass_kg", sv(servo, "mass_kg")], ["stall_kgcm", sv(servo, "stall_kgcm")],
        ["v_nom", sv(servo, "v_nom")]
    ]],
    ["torque", [
        ["supply_v", supply_v], ["n_servo", n_servo], ["link_g_per_mm", link_g_per_mm],
        ["m_body_kg", m_body_kg], ["k_dyn", k_dyn],
        ["derate_static", derate_static], ["derate_peak", derate_peak]
    ]],
    ["fk_golden", [for (a = fit_alpha, p = fit_phi) concat([a, p], [for (c = foot_centre(a, p)) rnd(c)])]]
];

echo(hexapod_params = params);
