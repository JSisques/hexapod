// SPDX-License-Identifier: MIT
// Intentional torque assertion failure for gate-test: tier M is infeasible with the MG996R.
// The cube keeps the geometry non-empty, so only the assert can fail this build.
include <../../../hardware/cad/common/params.scad>

leg_torque_gate(servo, "M");
cube(1);
