# Lines
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

l1=[[10,0,0],[10,0,10]]

# p_line3d() is used for showing lines or polylines -- in this example
# line "l1" of diameter 0.2 mm is shown
show(
color(points(l1,.5),"blue"),
color(p_line3d(l1,.2),"magenta"),
)
