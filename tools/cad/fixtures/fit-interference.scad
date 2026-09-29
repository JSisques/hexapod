// SPDX-License-Identifier: MIT
// Intentional interference for gate-test: the fit gate must reject 100 mm3 of overlap.
include <BOSL2/std.scad>
intersection() { cube(10); right(9) cube(10); }
move([-1000, -1000, -1000]) cube(1);   // sentinel, as in fit.scad
