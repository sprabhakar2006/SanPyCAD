# Simple coil spring
# Real project from the ocad examples notebook.
# The coil path itself is just a plain Python list comprehension (a spiral
# parametrised by angle, growing linearly in radius and dropping in z),
# then projected onto the tapered cylinder's own surface with nlos()
# (nearest-line-on-surface) so it hugs the cylinder exactly instead of
# just passing near it, and drawn with p_line3d() alongside the cylinder.
# A good minimal example of building a path with plain math instead of a
# helper like helix().

coil=array([i/360*array([cos(d2r(i)),sin(d2r(i)),-1]) for i in linspace(0,3600,720)]).tolist()
cyl1=translate([0,0,-10],cylinder(r1=10,r2=0.1,h=10))
coil=nlos(cyl1,coil,1)
coil_t=translate([0,0,10],coil)
cyl1_t=translate([0,0,10],cyl1)
show(color(p_line3d(coil_t,.05),"blue"), swp(cyl1_t))
