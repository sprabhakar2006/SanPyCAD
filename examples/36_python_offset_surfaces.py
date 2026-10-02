# Offset of a surface
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

w1=rot('x90',sinewave(100,3,2,100))
w2=rot('x90z90',cosinewave(100,3,2,100))
s1=surface_from_2_waves(w1,w2,2)
s2=surface_offset(s1,3)
show(
swp_surf(s1), # original surface
color(swp_surf(s2),alpha=0.3), # offset surface
)
