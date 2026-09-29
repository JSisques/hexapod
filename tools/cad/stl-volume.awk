# SPDX-License-Identifier: MIT
# Fit gate: signed volume of an ASCII STL. Facets with x < -500 are the sentinel (at least one must exist).
# Group g = int((x1 + 500) / 1000): g = 0 is the scene; with -v pairs=<log>, g >= 1 is fit pair g - 1
# (fit.scad offsets pair i by 1000 * (i + 1) mm in X) and names come from ECHO: "fit-pair", i, "a", "b".
# Usage: LC_ALL=C awk -v tol=0.1 -v name=<pose> [-v pairs=<log>] -f tools/cad/stl-volume.awk <file.stl>
BEGIN {
    if (tol == "") { err = "FIT_VOL_TOL is not set (fit_vol_tol not found in params.scad)"; exit 1 }
    if (pairs != "")
        while ((getline line < pairs) > 0)
            if (line ~ /^ECHO: "fit-pair"/) {
                split(line, f, "\""); i = f[3]; gsub(/[^0-9]/, "", i); label[i + 1] = f[4] " x " f[6]
            }
}
FNR == 1 && $1 != "solid" { err = "not an ASCII STL"; exit 1 }
$1 == "vertex" {
    k++; x[k] = $2 + 0; y[k] = $3 + 0; z[k] = $4 + 0
    if (k < 3) next
    k = 0
    if (x[1] < -500) { sentinel++; next }
    g = int((x[1] + 500) / 1000)
    a = x[1] - 1000 * g; b = x[2] - 1000 * g; c = x[3] - 1000 * g
    vol[g] += (a * (y[2] * z[3] - z[2] * y[3]) - b * (y[1] * z[3] - z[1] * y[3]) + c * (y[1] * z[2] - z[1] * y[2])) / 6
}
END {
    if (err == "" && !sentinel) err = "sentinel missing (truncated or empty export)"
    if (err != "") { printf "error: fit: %s: %s\n", name, err > "/dev/stderr"; exit 1 }
    if (pairs != "") {
        for (g in vol) {
            v = vol[g] < 0 ? -vol[g] : vol[g]
            if (g + 0 > 0 && v > tol + 0)
                printf "fit:   %s: %s: interference %.3f mm3\n", name, ((g in label) ? label[g] : "pair " (g - 1)), v > "/dev/stderr"
        }
        exit 0
    }
    v = vol[0] < 0 ? -vol[0] : vol[0]
    if (v > tol + 0) { printf "error: fit: %s: interference volume %.3f mm3 exceeds tolerance %s mm3\n", name, v, tol > "/dev/stderr"; exit 1 }
    printf "fit: %s: %.3f mm3, tolerance %s mm3\n", name, v, tol
}
