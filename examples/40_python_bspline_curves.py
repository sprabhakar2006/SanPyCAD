# B-spline curves (open and closed)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

l1=cr2dt([[0,0],[10,0],[-3,7],[15,-5],[0,10],[-10,10],[-15,-5]])
l2=bspline_open(l1,3,50)
l3=bspline_closed(l1,3,100)
show(
color(points(l1,.5),"blue"),
color(p_line3d(l2,.2),"magenta"),
color(p_line3d(l3,.2),"cyan"),
)
