// SPDX-License-Identifier: CC-BY-SA-4.0
// Leg torque feasibility model. Side-effect free: the gate runs only when a part calls it.
// Lengths in mm, masses in kg, forces in kgf, torques in kg.cm.

function leg_mass_total_kg(n_servo, m_servo_kg, g_per_mm, lengths, m_body_kg)
    = n_servo * m_servo_kg + 6 * g_per_mm * (lengths[0] + lengths[1] + lengths[2]) / 1000 + m_body_kg;
// Tripod stance: one leg carries a third of the weight; k scales for dynamic load.
function tripod_force_kgf(m_total, k = 1) = m_total / 3 * k;
function tau_tibia_kgcm(F, tibia_l, phi) = F * tibia_l / 10 * sin(phi);
function tau_femur_kgcm(F, femur_l, tibia_l, phi, alpha = 0)
    = F * (femur_l * cos(alpha) + tibia_l * sin(phi)) / 10;
function torque_allowable(stall, derate) = stall * derate;
function r2(x) = round(x * 100) / 100;

// Rows of [joint, case, tau, allowable].
function torque_rows(p, lengths, m_total, v, phi, k_dyn, d_s, d_p, alpha = 0) =
    let(stall = servo_stall_kgcm(p, v),
        Fs = tripod_force_kgf(m_total, 1),
        Fp = tripod_force_kgf(m_total, k_dyn))
    [["femur", "static", tau_femur_kgcm(Fs, lengths[1], lengths[2], phi, alpha), torque_allowable(stall, d_s)],
     ["femur", "peak",   tau_femur_kgcm(Fp, lengths[1], lengths[2], phi, alpha), torque_allowable(stall, d_p)],
     ["tibia", "static", tau_tibia_kgcm(Fs, lengths[2], phi), torque_allowable(stall, d_s)],
     ["tibia", "peak",   tau_tibia_kgcm(Fp, lengths[2], phi), torque_allowable(stall, d_p)]];

// Echo each row and assert tau <= allowable per row (needs params.scad globals).
module leg_torque_gate(p = servo, tier = leg_tier) {
    lengths = leg_lengths(tier);
    m_total = leg_mass_total_kg(n_servo, sv(p, "mass_kg"), link_g_per_mm, lengths, m_body_kg);
    rows = torque_rows(p, lengths, m_total, supply_v, phi_nom, k_dyn, derate_static, derate_peak, alpha);
    for (r = rows)
        echo(str("leg torque: ", r[0], " ", r[1], " ", r2(r[2]), " / ", r2(r[3]),
                 " kg.cm, margin ", r2(r[3] / r[2])));
    for (r = rows)
        assert(r[2] <= r[3],
               str("torque budget exceeded: ", r[0], " ", r[1], " ", r2(r[2]), " kg.cm > allowable ",
                   r2(r[3]), " kg.cm (servo ", sv(p, "name"), ", tier ", tier, ", ", supply_v, " V)"));
}
