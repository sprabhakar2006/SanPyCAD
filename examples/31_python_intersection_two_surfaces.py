# Intersection between two surfaces
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

s1=linear_extrude(square(20),20)
s2=translate([-10,10,10],rot('y90',linear_extrude(circle(5),50)))
l1=ip_sol2sol(s1,s2,n=-1)
l2=ip_sol2sol(s1,s2,n=0)

show(
color(swp_c(s1),alpha=0.3),
color(swp_surf(s2),alpha=0.3),
color(p_line3d(l1,.3),"blue"),
color(p_line3d(l2,.3),"magenta"),
)
# Note: To debug issues related to intersection:
# There are 2 surfaces surface1 (s1 in this case) and surface2(s2 in this case)
# surface 1 is intersected by surface 2
# So surface1 should be rendered with module "swp_c"
# surface2 should be rendered with module "swp_surf"
