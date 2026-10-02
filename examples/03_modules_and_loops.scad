// User-defined modules, for-loops, and variables.

module gear_tooth_block(w = 3, h = 10, d = 6) {
    translate([0, 0, d / 2]) cube([w, h, d], center = true);
}

n = 12;
radius = 25;

for (i = [0 : n - 1]) {
    a = i * 360 / n;
    rotate([0, 0, a])
        translate([radius, 0, 0])
        gear_tooth_block();
}

cylinder(r = radius - 4, h = 6, center = true, $fn = 60);
