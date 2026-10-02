# union()/difference()/intersection()/hull() can be nested arbitrarily,
# same as the OpenSCAD-style mode -- they just take Python values instead
# of being statements.

lower = cube([16, 16, 6], center=True)
bump = translate([0, 0, 10], sphere(r=5))
body = hull(lower, bump)

hole = cylinder(r=3, h=30, center=True)
result = difference(body, hole)

show(result)

# ocad.py's own union() (2D pattern generation) is unrelated to CSG
# and still reachable if you need it, since union() above only shadows
# the bare name inside this script:
#   ocad.union(...)
