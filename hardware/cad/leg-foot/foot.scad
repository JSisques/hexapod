// SPDX-License-Identifier: CC-BY-SA-4.0
// Foot (TPU). Frame: sphere tip at the bottom, socket opening up.
include <../common/params.scad>

ft_r     = 8;                                    // tip sphere radius (d16)
ft_od    = leg_spigot_d + tol_fit + 2 * wall;
ft_floor = ft_r + 6;                             // socket floor height

// Bounding box of the print pose: [x, y, z].
function foot_size() = [ft_od, ft_od, ft_floor + leg_spigot_l];

module foot() {
    difference() {
        hull() {
            move([0, 0, ft_r]) sphere(r = ft_r);
            move([0, 0, ft_floor]) cyl(h = leg_spigot_l, d = ft_od, anchor = BOTTOM);
        }
        move([0, 0, ft_floor]) cyl(h = leg_spigot_l + eps, d = leg_spigot_d + tol_fit, anchor = BOTTOM);
        // M3 cross hole along X, teardrop so it prints without support.
        move([0, 0, ft_floor + leg_spigot_l / 2]) zrot(90) teardrop(d = fs(M3, "clear"), l = ft_od + 2 * eps);
    }
}

// Print pose: as modelled, socket opening up.
module foot_print() { foot(); }
