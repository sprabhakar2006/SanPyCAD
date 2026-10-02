# Offset of a solid
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

c1=cylinder(r=10,h=40)
c2=offset_solid(c1,-3)
c3=offset_solid(c1,3)
show(
color(swp_c(c1),"blue",.2), # original cylinder
color(swp_c(c2),"magenta",.2), # offset inwards by 3mm
color(swp_c(c3),"cyan",.2), # offset outwards 3mm
)
