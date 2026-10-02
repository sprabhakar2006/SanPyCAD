# Rotation about multiple axes
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

l1=sinewave(100,2,10,100)
l2=rot('x90z45',l1) # multiple rotation of l1 (rotated by 90 deg along x-axis 
# and then 45 deg along z-axis
show(
color(p_line3d(l1,1),"blue"), # original line 'l1'
color(p_line3d(l2,1),"magenta"), # rotated line
)
