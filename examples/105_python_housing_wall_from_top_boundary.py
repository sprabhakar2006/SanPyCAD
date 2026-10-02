# Housing wall built around the mouse body's own top-visible boundary,
# following the same 4-point-wedge technique used elsewhere in this
# project's own housing pipeline (project boundary to a plane, offset
# it outward in 3d, build a wall surface from that offset, project the
# original boundary onto the wall -- then sweep [inner-top, outer-top,
# outer-bottom, inner-bottom] all the way around).
#
# Same mouse-body construction as example 102.

a=cr2dt([[-20,0,15],[40,0,15],[0,40],[5,40,20],[-50,0,20],[5,-40]])
tx=a_(a).mean(0)
a=translate_2d(-tx,a)
b=translate([0,0,-20],sphere(50))
p1=[[0,0],[15,50]]
s1=prism(a,p1)
l1=translate_2d([-25,3],sinewave(50,1.5,3,50))
l1=mirror_line(l1,[0,1,0],[0,0,0])
l2=translate_2d([0,-20],circle(50))
l3=rot2d(30,[[0,0],[-10,0]])
l3=rot('x90z-90',flip(line2length( flip(line2length( cir_line_tangent(l2,l3),50)),100)))
s2=sweep_sec2path(l1,l3)
b=psos(s2,b,[0,0,-1]@xrot(-30),1e7,1,3)
b=[bspline_closed(p,3,50) for p in b]
l1=equidistant_pathc( contiguous_chains( two_solids_intersection(b,s1))[0],100)
l2=o_3d(l1,b,7,outside=0)
l3=o_3d(l1,s1,-3,outside=0)
f3=convert_3lines2fillet(l3,l2,l1,closed_loop=1)
f3=solid_from_fillet_closed(f3,-3)
sol=difference(intersection(swp(s1),swp(b)),swp_c(f3))

# The top-visible surface (occlusion-aware, not just normal-facing --
# see surface_split()'s own docstring), capped down into a solid.
tri=sol.V[sol.F]
tri_top=surface_split(tri,[0,0,1])
tri_1=psos(plane_from_equation([0,0,1,40],[100,100]), tri_top,[0,0,1])
sol1=union(*[ swp([t,b]) for t,b in zip(tri_top,tri_1)])

# The sharp corner where that top surface ends -- free edges of the
# tri_top patch (used by only one triangle) stitched into one loop.
# boundary_edges_tri() packages up the edge-counting logic directly.
boundary_segs = boundary_edges_tri(tri_top)
chains = contiguous_chains(boundary_segs)
l5 = chains[0]
for c in chains:
    if len(c) > len(l5):
        l5 = c
l5=equidistant_pathc(l5,100)

# l6: l5 projected straight down onto the flat parting plane.
# l7: l6 offset outward by 40 (in-plane, via the robust offset_3d()).
# s3: a vertical wall surface swept straight down from l7.
# l8: l5 projected onto that wall surface -- the wall's outer edge at
#     full (unflattened) height.
l6=nlos(plane_from_equation([0,0,1,40],[100,100]),l5)
l7=offset_3d(l6,40)
s3=surface_line_vector(l7,[0,0,-100])
l8=nlos(s3,l5,1)

# Each of the 100 stations is a 4-point wedge: inner-top(l5) ->
# outer-top(l8) -> outer-bottom(l7) -> inner-bottom(l6) -> back to
# inner-top(l5) -- swp_c() sweeps that all the way around into one
# closed tube (no caps needed, it's a full loop already).
sol2 = [l5, l8, l7, l6, l5]
sol3 = union(sol1, swp_c(sol2))

show(sol3)
