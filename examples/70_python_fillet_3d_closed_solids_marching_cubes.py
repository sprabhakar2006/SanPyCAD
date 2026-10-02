# Fillet between two closed swept solids via marching cubes
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)
# Computationally heavy: builds a fillet surface via marching cubes over many
# offset/intersection steps. May take a while to evaluate.

t0=time.time()
a=sweep_sec2path(circle(5),c23(circle(20)),closed_loop=1)
b=rot('x90',a)
r,n=2+3,40
a1=arc(r,180,270,[r,r],n)
a2=[offset_solid_closed(a,x-3) for (x,y) in a1]
b2=[offset_solid_closed(b,y-3) for (x,y) in a1]
l1=[two_solids_intersection(a2[i],b2[i]) for i in range(n)]
l2=concatenate(l1)
l3=homogenise(remove_seg_with_len_lessthan_d(l2,.01),.1)

v1,f1=mcm(l3,3,[200,60,60])
# v1/f1 are a raw marching-cubes vertex/face array (not a sol) -- built
# into the same polyhedron(...) text swp() itself generates, so it can
# be used as a shape directly.
poly1=f"polyhedron({v1},{f1})"
show(
poly1,
swp(a),
swp(b),
)
t1=time.time()
t1-t0
