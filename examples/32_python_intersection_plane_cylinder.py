# Intersection between a plane and a cylinder
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

pl1=plane([-1,0,1],[100,100],[0,0,20])
c1=cylinder(r=10,h=80)
p0=ip_sol2sol(pl1,c1)
show(
color(swp_c(pl1),alpha=0.3),
color(swp_surf(c1),alpha=0.3),
color(p_line3d(p0,.5),"blue"),
)
