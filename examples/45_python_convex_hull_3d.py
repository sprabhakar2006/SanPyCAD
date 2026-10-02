# Convex hull (3D)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# convexhull in 3d 
a=random.random(100)*(20-0)+0
b=random.random(100)*(20-0)+0
c=random.random(100)*(20-0)+0
p0=l_(a_([a,b,c]).transpose(1,0))
sol=l_(a_(p0)[ConvexHull(p0).simplices])
show(
color(points(p0,.5),"blue"),
swp_triangles(sol),
)
