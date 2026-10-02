# Offset of a path / polyline
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

s1=square(10)
s2=path_offset(s1,-3)
s3=path_offset(s1,3)

show(
color(p_line3d(s1,.2),"blue"), # original polyline
color(p_line3d(s2,.2),"magenta"), # offset inwards by 3mm
color(p_line3d(s3,.2),"cyan"), # offset outwards 3mm
)
