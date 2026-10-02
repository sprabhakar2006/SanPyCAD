# Projecting a line onto a surface
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

l1=rot('y90',helix(10,2,5,5))
l2=c23(arc(15,0,360*3,s=len(l1)-1))
l3=extrude_wave2path(l1,l2)
s1=sphere(30)
l4=plos(c_(s1),l3,[0,0,1])
l5=plos(c_(s1),l3,[0,1,0])
show(
color(p_line3d(l3,.3),"blue"),
color(p_line3d(l4,.3),"magenta"),
color(p_line3d(l5,.3),"cyan"),
)
