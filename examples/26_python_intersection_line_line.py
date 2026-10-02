# Intersection between two lines (2D)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

l1=point_vector([2,3],[10,5])
l2=point_vector([2,10],[10,-10])
p0=s_int1([l1,l2])[0]
show(
*[color(p_line3d(p,.3),"blue") for p in [l1,l2]],
color(points([p0],.5),"magenta"),
)
