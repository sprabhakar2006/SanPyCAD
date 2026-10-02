# Solid
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

l2=cr2dt([[0,0],[10,0],[0,10],[-10,0]])
s1=linear_extrude(l2,10)
show(
*[color(points(p,.5),"blue") for p in s1],
*[color(p_line3d(p,.2,closed=1),"magenta") for p in s1],
swp(s1),
)
