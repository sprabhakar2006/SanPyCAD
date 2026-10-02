# Intersection between two polylines (circles)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

c1=circle(10)
c2=circle(15,[10,10])
p0=s_int1(seg(c1)+seg(c2))
show(
*[color(p_line3d(p,.2),"blue") for p in [c1,c2]],
color(points(p0,.5),"magenta"),
)
