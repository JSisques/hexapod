# SPDX-License-Identifier: MIT
# Mesh bed gate. Usage: awk -v max=180 -v name=<part> -f tools/cad/stl-bbox.awk <file.stl>
BEGIN { if (max + 0 <= 0) { err = "BED_MAX is not set (bed_max not found in params.scad)"; exit 1 } }
FNR == 1 && $1 != "solid" { err = "not an ASCII STL"; exit 1 }
$1 == "vertex" {
    for (i = 1; i <= 3; i++) {
        v = $(i + 1) + 0
        if (n == 0 || v < lo[i]) lo[i] = v
        if (n == 0 || v > hi[i]) hi[i] = v
    }
    n++
}
END {
    if (err == "" && n == 0) err = "STL has no vertices"
    if (err != "") { printf "error: %s: %s\n", name, err > "/dev/stderr"; exit 1 }
    s = sprintf("[%.2f, %.2f, %.2f]", hi[1] - lo[1], hi[2] - lo[2], hi[3] - lo[3])
    if (hi[1] - lo[1] > max + 0 || hi[2] - lo[2] > max + 0 || hi[3] - lo[3] > max + 0) {
        printf "error: %s: STL size %s exceeds bed_max %s mm\n", name, s, max > "/dev/stderr"; exit 1
    }
    printf "%s: STL size %s mm, bed_max %s mm\n", name, s, max
}
