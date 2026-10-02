# Internal fillet between two arcs
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# fillet between 2 arcs
c1=circle(20)
c2=circle(15,[20,20])
f1=two_cir_tarc_internal(c2,c1,r=3)
f2=two_cir_tarc_internal(c1,c2,r=3)
show(
color(p_line3d(c1,.3,closed=1),"blue"),
color(p_line3d(c2,.3,closed=1),"cyan"),
color(p_line3d(f1,.3),"magenta"),
color(p_line3d(f2,.3),"brown"),
)
