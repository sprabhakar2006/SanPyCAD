# Concave hull of overlapping circles (2D)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# Draw a circle with radius 10 and centered at [5,0]
c1=circle(10,[5,0])

# Create 3 copies of the circle 'c1' rotated at 0, 120 and 240 deg from origin
cx=[ rot2d(i,c1) for i in [0,120,240]]

# homogenise the 3 copies of circles created above, so that distance between 
# each subsequent point of circle is 0.5 mm apart and these 3 circles are all 
# closed loop sections individually as well
cx=homogenise(cx,pitch=.5,closed_loop=1)

# calculate the concave hull for these points
cy=concave_hull(cx)

show(
color(points(cx,.2),"blue"),
color(p_line3d(cy,.2),"magenta"),
)
