# Wrap a wave polyline onto a path
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

c1=rot('x90',sinewave(100,5,5,100))
path=c23(arc(20,0,360,s=99))
c2=extrude_wave2path(c1,path)

show(
color(p_line3d(c1,.2),"blue"),
color(p_line3d(path,.2),"cyan"),
color(p_line3d(c2,.2,closed=1),"magenta"),
)
