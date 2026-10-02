# Sculpting a section along a path (prism)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

sec=circle(10)
path=[[0,0],[5,10],[0,20]] # x-coordinates work as offset and y-coordinates work as z-translate of sec
sol=prism(sec,path)
show(
color(p_line3d(sec,.3),"blue"),
color(p_line3d(path,.3),"magenta"),
color(swp(sol),alpha=0.3),
)
