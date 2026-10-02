# Intersection between a polyline (circle) and a line
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

c1=circle(20)
l1=point_vector([-20,-20],[50,20])
p0=s_int1([l1]+seg(c1))
show(
*[color(p_line3d(p,.2),"blue") for p in [l1,c1]],
color(points(p0,.5),"magenta"),
)
