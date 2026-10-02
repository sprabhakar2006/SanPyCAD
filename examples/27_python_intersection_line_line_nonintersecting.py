# Intersection point between two non-intersecting line segments
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# intersection point between 2 lines even if they are not directly intersecting 
l1=[[0,0],[10,5]]
l2=[[2,12],[8,10]]
p0=i_p2d(l1,l2)
show(
*[color(p_line3d(p,.3),"blue") for p in [l1,l2]],
color(points([p0],.5),"magenta"),
)
