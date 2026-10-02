# Extrude a section along an open path
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# circular section extruded along open path
sec=circle(5)
path=c23(sinewave(l=100,n=2,a=10,p=100))
sol=sweep_sec2path(sec,path)
show(swp(sol))
