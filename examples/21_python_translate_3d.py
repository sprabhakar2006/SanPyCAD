# Translate a 3D solid
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# example of translate in 3d coordinate
c1=linear_extrude(circle(10),50)
c2=translate([20,20,0],c1)
show(
swp(c1), # original cylinder
color(swp(c2),"cyan"), # translated cylinder by vector [20,20,0]
)
