// linear_extrude / rotate_extrude / hull

translate([-25, 0, 0])
    linear_extrude(height = 15, twist = 90, $fn = 30)
    circle(r = 6);

translate([0, 0, 0])
    rotate_extrude(angle = 360, $fn = 60)
    translate([8, 0]) circle(r = 3, $fn = 24);

translate([25, 0, 0])
    hull() {
        sphere(r = 4, $fn = 24);
        translate([0, 0, 15]) sphere(r = 2, $fn = 24);
    }
