# Plane: y-z plane
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

n1=[1,0,0] 
l1=[[0,0,0],[10,0,0]]
# y-z plane
pl1=plane(n1,size=[50,50], intercept=[0,0,0])
show(
color(p_line3d(l1,.5),"magenta"),
swp_surf(pl1),
)
