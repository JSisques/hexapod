// SPDX-License-Identifier: CC-BY-SA-4.0
include <BOSL2/std.scad>
include <../common/params.scad>
include <tibia.scad>

leg_part_checks("leg-tibia", tibia_size());
tibia_print();
