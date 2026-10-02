# Concave hull of two overlapping squares (2D)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

s1=square(20)
s2=square(20,center=True)

sx=homogenise([s1,s2],pitch=.5,closed_loop=1)
sy=concave_hull(sx)

show(
color(points(sx,.3),"blue"),
color(p_line3d(sy,.3),"magenta"),
)
