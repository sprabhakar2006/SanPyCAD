# Fillet between two spheres
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# fillet between 2 spheres
s1=sphere(10)
s2=sphere(7,[15,15,0])
f1=fillet_2spheres(s1,s2,7,s1=10,s2=40)
pl1=plane_from_equation([1,1,0,-5])
s1=psos(pl1,s1,[1,1,0])
show(
swp(s1),
swp(s2),
swp(f1),
)
