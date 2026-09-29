// SPDX-License-Identifier: CC-BY-SA-4.0
// MG996R servo profile. PROVISIONAL: dimensions come from generic drawings and are unmeasured.
// Frame: Z = output shaft up, origin on the shaft axis at the case top face, +X toward the far body end.
// Key status: P = provisional, S = standard / datasheet.

function mg996r() = [
    ["name", "mg996r"],                                                  // S
    ["provisional", true],                                               // S
    ["source", "TowerPro datasheet + generic drawings; unmeasured"],     // S
    ["body_l", 40.7], ["body_w", 19.7], ["body_h", 37.0],                // P
    ["top_h", 5.9],                                                      // P: hub above case
    ["shaft_offset_x", 10.0], ["shaft_offset_y", 0],                     // P: shaft to near end
    ["ear_span", 54.5], ["ear_t", 2.5], ["ear_top_z", -10.0],            // P
    ["ear_hole_pitch_l", 49.5], ["ear_hole_pitch_w", 10.0],              // P
    ["ear_hole_d", 4.2],                                                 // P
    ["mount_screw", "M3"],                                               // S
    ["body_clear", 0.3],                                                 // P
    ["spline_teeth", 25], ["spline_od", 5.8],                            // S / P
    ["horn_d", 25.0], ["horn_t", 2.5],                                   // P
    ["horn_hole_pcd", 18.0], ["horn_hole_n", 4], ["horn_screw_d", 2.0],  // P
    ["horn_center_clear_d", 8.0],                                        // P
    ["cable_exit_z", -33.0], ["cable_exit_w", 6.0],                      // P: at +X end
    ["mass_kg", 0.055],                                                  // S
    ["stall_kgcm", [[4.8, 9.4], [6.0, 11.0]]],                           // S: datasheet, [V, kg.cm]
    ["stall_a", 2.5],                                                    // P: highest source
    ["pulse_us", [500, 2500]], ["range_deg", 180],                       // P
    ["v_nom", 6.0]                                                       // S
];
