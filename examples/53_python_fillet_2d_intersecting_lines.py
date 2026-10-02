# Fillet between two intersecting lines (2D)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# fillets between 2 intersecting lines
l1=point_vector([-5,-5],[10,10])
l2=point_vector([-5,20],[10,-10])
l3=fillet_intersection_lines(l1,l2,r=3)
show(
color(p_line3d(l1,.3),"blue"),
color(p_line3d(l2,.3),"cyan"),
color(p_line3d(l3,.3),"magenta"),
)
