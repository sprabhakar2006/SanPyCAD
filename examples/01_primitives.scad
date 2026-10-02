// Basic primitives, side by side.
translate([-20, 0, 0]) cube([10, 10, 10]);
translate([0, 0, 5]) sphere(r = 6, $fn = 48);
translate([20, 0, 0]) cylinder(r1 = 6, r2 = 3, h = 12, $fn = 40, center = true);
