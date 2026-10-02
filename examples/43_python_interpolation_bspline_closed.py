# Interpolation curve through points (closed loop)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# interpolation through bsplines closed loop
l1=cr2dt([[0,0],[10,0],[-3,7],[15,-5],[0,10],[-10,10],[-15,-5]])
# l2=interpolation_bspline_open(l1,50)
l3=interpolation_bspline_closed(l1,100)
show(
color(points(l1,.5),"blue"),
color(p_line3d(l3,.2),"cyan"),
)
