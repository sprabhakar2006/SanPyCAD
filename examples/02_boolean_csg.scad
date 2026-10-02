// Boolean CSG: a plate with a rounded-off block and a through-hole and a
// bump, built from cube/cylinder/sphere. CSG runs through a voxel +
// marching-cubes pipeline (see README), so it's not razor-sharp like a
// CAD kernel -- raise "CSG detail" in the toolbar for a cleaner result.

difference() {
    union() {
        cube([30, 20, 8], center = true);
        translate([0, 0, 4]) sphere(r = 6, $fn = 40);
    }
    translate([0, 0, 0]) cylinder(r = 4, h = 30, center = true, $fn = 40);
    translate([10, 0, 0]) cylinder(r = 2, h = 30, center = true, $fn = 30);
    translate([-10, 0, 0]) cylinder(r = 2, h = 30, center = true, $fn = 30);
}
