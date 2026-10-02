# Wrap a section around a path
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

c1=translate([0,20.1,0],circle(20))
path=rot('y90',circle(40.2/(2*pi)+.2))
c2=wrap_around(c1,path)

show(
color(p_line3d(c1,.2),"blue"),
color(p_line3d(path,.2),"cyan"),
color(p_line3d(c2,.2),"magenta"),
)
