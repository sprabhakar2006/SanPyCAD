# Rotation about the x-axis
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

l1=sinewave(100,2,10,100)
l2=rot('x90',l1) # l1 rotated by 90 deg along x-axis
show(
color(p_line3d(l1,1),"blue"), # original line 'l1'
color(p_line3d(l2,1),"magenta"), # rotated line
)
