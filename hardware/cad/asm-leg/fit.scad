// SPDX-License-Identifier: CC-BY-SA-4.0
// Fit check (not an entry point: not named main.scad). One pose per run; make passes -D fit_a / fit_p / fit_diag.
// The output is the union of the intersection of every body pair plus a sentinel cube; its volume must be ~0.
// With fit_diag = true, pair i is offset by 1000 * (i + 1) mm in X and named in an ECHO, so stl-volume.awk can report it.
include <asm-leg.scad>

fit_a = alpha;
fit_p = phi_nom;
fit_diag = false;
fit_pairs = [for (i = [0 : len(asm_bodies) - 2], j = [i + 1 : len(asm_bodies) - 1]) [asm_bodies[i], asm_bodies[j]]];

for (i = [0 : len(fit_pairs) - 1]) {
    if (fit_diag) echo("fit-pair", i, fit_pairs[i][0], fit_pairs[i][1]);
    right(fit_diag ? 1000 * (i + 1) : 0) intersection() {
        asm_body(fit_pairs[i][0], fit_a, fit_p);
        asm_body(fit_pairs[i][1], fit_a, fit_p);
    }
}
move([-1000, -1000, -1000]) cube(1);   // sentinel: keeps the export non-empty; skipped by the awk
