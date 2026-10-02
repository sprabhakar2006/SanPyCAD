# Fillet between two orthogonal offset solids via marching cubes
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)
# Computationally heavy: builds a fillet surface via marching cubes over many
# offset/intersection steps. May take a while to evaluate.

i_t=time.time()
a=o_solid([1,0,0],circle(7),50,-25)
b=o_solid([0,1,0],circle(7),50,-25)
r,n=2+2,40
a1=arc(r,180,270,[r,r],n)
a2=[offset_solid(a,x-2) for (x,y) in a1]
b2=[offset_solid(b,y-2) for (x,y) in a1]
l1=[two_solids_intersection(a2[i],b2[i]) for i in range(n)]
l2=concatenate(l1)
l3=homogenise(remove_seg_with_len_lessthan_d(l2,.01),.1)
v1,f1=mcm(l3,2,[30,30,30])
f1=[flip(p) for p in f1]

ax=o_solid([1,0,0],circle(6),55,-27.5)
bx=o_solid([0,1,0],circle(6),55,-27.5)
r,n=2+2,40
a1=arc(r,180,270,[r,r],n)
a2=[offset_solid(ax,x-2) for (x,y) in a1]
b2=[offset_solid(bx,y-2) for (x,y) in a1]
l1=[two_solids_intersection(a2[i],b2[i]) for i in range(n)]
l2=concatenate(l1)
l3=homogenise(remove_seg_with_len_lessthan_d(l2,.01),.1)
v2,f2=mcm(l3,2,[100,100,100])
f2=[flip(p) for p in f2]

# v1/f1 and v2/f2 are raw marching-cubes vertex/face arrays (from mcm()),
# not sols -- built into the same polyhedron(...) text swp() itself
# generates, so they can be used as shapes directly, same as swp()'s output.
poly1=f"polyhedron({v1},{f1},convexity=10)"
poly2=f"polyhedron({v2},{f2},convexity=10)"
show(
difference(
union(*[swp(p) for p in [a,b]],poly1),
union(*[swp(p) for p in [ax,bx]],poly2),
)
)
f_t=time.time()
f_t-i_t
