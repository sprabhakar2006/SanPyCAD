# Plain Python for-loops work here directly -- no special loop syntax
# needed, unlike the OpenSCAD-style mode. translate()/rot()/scl3d()/etc
# are your library's own functions, used exactly like in your notebooks.

n = 10
radius = 25
teeth = []
for i in range(n):
    angle = i * 360 / n
    block = rot(f"z{angle}", translate([radius, 0, 0], cube([3, 6, 8], center=True)))
    teeth.append(block)

hub = cylinder(r=radius - 4, h=6, center=True)

show(union(hub, *teeth))
show(color(translate([0, 0, 6], sphere(r=3)), "red"))
