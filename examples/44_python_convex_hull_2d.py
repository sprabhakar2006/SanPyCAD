# Convex hull (2D)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

c1=circle(10,[5,0])
cx=[ rot2d(i,c1) for i in [0,120,240]]
cx=homogenise(cx,.5,1)
cy=convex_hull(cx)
show(
color(points(cx,.2),"blue"),
color(p_line3d(cy,.2),"magenta"),
)
