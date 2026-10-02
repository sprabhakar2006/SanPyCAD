# Move an intersection line along the intersecting surface
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

s1=sphere(20)
s2=rot('y90',cylinder(r=5,h=50))
l1=ip_sol2sol(s1,s2)
l2=i_p_p(s2,l1,2)

show(
color(swp_c(s1),alpha=0.3),
color(swp_surf(s2),alpha=0.3),
color(p_line3d(l1,.2),"blue"),
color(p_line3d(l2,.2),"magenta"),
)
