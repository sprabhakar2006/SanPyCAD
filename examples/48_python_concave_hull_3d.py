# Concave hull (3D) -- requires optional 'alphashape' package
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)
# Requires: pip install alphashape (not bundled with SanPyCAD).

# concave_hull in 3d space, needs to install alphashape library 
# use terminal command: pip install alphashape
from alphashape import alphashape
a=random.random(100)*(20-0)+0
b=random.random(100)*(20-0)+0
c=random.random(100)*(20-0)+0
p0=l_(a_([a,b,c]).transpose(1,0))
v1=alphashape(p0,0.05).vertices
f1=alphashape(p0,0.05).faces
sol=l_(v1[f1])
show(
swp_triangles(sol),
color(points(p0,.5),"blue"),
)
