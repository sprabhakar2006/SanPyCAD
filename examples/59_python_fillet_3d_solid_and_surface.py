# Fillet at the intersection of a solid and a surface
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# fillet at the intersection of a solid and a surface
s1=triangulate_solid_openx(sphere(20))
l1=translate([-10,0,0],sinewave(20,2,2,50))
s2=triangulate_surface(surface_line_vector(l1,[5,5,50]))
l1=contiguous_chains( two_tri_intersection(s1,s2))[0]
l1=equidistant_path(l1,100)
l2=o_3d_tri(l1,s1,2)
l3=o_3d_tri(l1,s2,2)
f1=convert_3lines2fillet(l2,l3,l1)

show(
*[color(p_line3d(p,.2),"blue") for p in [l1,l2,l3]],
color(swp_triangles(s1),alpha=0.3),
color(swp_triangles(s2),alpha=0.3),
swp(f1),
)
