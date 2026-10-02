# Plane: x-y plane
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

n1=[0,0,1] 
l1=[[0,0,0],[0,0,10]]
# x-y plane
pl1=plane(n1,size=[50,50], intercept=[0,0,0])
show(
color(p_line3d(l1,.5),"magenta"),
swp_surf(pl1),
)
