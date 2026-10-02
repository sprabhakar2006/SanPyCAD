# Polylines
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

l2=cr2dt([[0,0],[10,0],[0,10],[-10,0]])
show(
color(points(l2,.5),"blue"),
color(p_line3d(l2,.2),"magenta"),
)
