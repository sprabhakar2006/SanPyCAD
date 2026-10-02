# Projecting a line onto a surface (projection along a custom direction)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

l1=translate([-5*12/2,0,0],rot('y90',helix(1,5,12,5)))

s1=rsz3dc(sphere(30),[61,30,30])
l2=plos_v_1(c_(s1),l1,[[0,0,0],[1,0,0]])

show(
#color(p_line3d(l1,.3),"blue"),
color(p_line3d(l2,.3),"magenta"),
color(swp(s1),alpha=0.3),
)
