# Wrap a surface around a path
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

c1=translate_2d([0,20.1],circle(20))
s1=h_lines_sec(c1,100)
path=rot('y90',circle(40.2/(2*pi)+.2))
c2=wrap_around(c1,path)
s2=[wrap_around(p,path) for p in s1]
show(
color(p_line3d(c1,.2),"blue"),
color(p_line3d(path,.2),"cyan"),
color(p_line3d(c2,.2),"magenta"),
*[color(p_line3d(p,.1,1),"blue") for p in s1],
*[color(p_line3d(p,.1,1),"magenta") for p in s2],
)
