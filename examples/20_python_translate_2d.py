# Translate a 2D shape
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# example of translate in 2 d coordinates

c1=circle(10)
c2=translate_2d([20,20],c1)
show(
color(p_line3d(c1,.2),"blue"), # original circle
color(p_line3d(c2,.2),"magenta"), # translated circle
)
