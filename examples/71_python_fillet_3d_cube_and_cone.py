# Fillet between a cube and a cone-tipped cylinder
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)
# Computationally heavy: builds a fillet surface via marching cubes over many
# offset/intersection steps. May take a while to evaluate.

a=cube([50,50,15])
b=translate([0,25,15+3],rot('y90',cylinder(r1=10,r2=.01,h=50)))
bx=translate([0.2,25,15+3],rot('y90',cylinder(r1=10,r2=.01,h=50-.2)))

r,n=3+.2,50
a1=arc(r,180,270,[r,r],n)
pl1=plane_from_equation([0,0,1,15],[150,150])
a2=[translate([0,0,x-.2],pl1) for (x,y) in a1]
b2=[offset_solid_simple(bx,y-.2) for (x,y) in a1]
l1=[surface_solid_open_intersection(a2[i],b2[i],1) for i in range(n)]
l2=homogenise(remove_seg_with_len_lessthan_d(concatenate(l1),0.01),.05)
v1,f1=mcm(l2,.2,[300,150,25])
f1=[flip(p) for p in f1]
# v1/f1 are a raw marching-cubes vertex/face array (not a sol) -- built
# into the same polyhedron(...) text swp() itself generates, so it can
# be used as a shape directly.
poly1=f"polyhedron({v1},{f1},convexity=10)"
show(
intersection(cube(50-1),poly1),
swp(a),
swp(b),
)
