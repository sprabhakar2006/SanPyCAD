# Offset a polyline while keeping it on a surface
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

s1=sphere(20)
s2=rot('y90',cylinder(r=5,h=50))
l1=ip_sol2sol(s1,s2)
l2=o_3d(l1,s1,-2,outside=0)

show(
color(swp_c(s1),alpha=0.3),
color(swp_surf(s2),alpha=0.3),
color(p_line3d(l1,.2),"blue"), # original intersection line
color(p_line3d(l2,.2),"magenta"), # offset line on sphere
)
