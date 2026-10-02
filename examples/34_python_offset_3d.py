# Offset of a section in 3D
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

sec=rot('y-60',square(10))
sec1=offset_3d(sec,-3)
sec2=offset_3d(sec,3)

show(
color(p_line3d(sec,.2,closed=1),"blue"), # original square
color(p_line3d(sec1,.2,closed=1),"magenta"), # offset inwards by 3mm
color(p_line3d(sec2,.2,closed=1),"cyan"), # offset outwards 3mm
)
