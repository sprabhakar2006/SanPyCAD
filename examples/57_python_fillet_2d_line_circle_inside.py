# Fillet between a line and a circle (inside)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# fillet between line and circle (inside)
h=15
line=[[-10,h],[30,h]]
cir1=circle(10,[10,10])
s=20
fillet5=fillet_line_circle_internal(line,cir1,2,1)
fillet6=fillet_line_circle_internal(line,cir1,4,2)
fillet7=fillet_line_circle_internal(line,cir1,2,3)
fillet8=fillet_line_circle_internal(line,cir1,4,4)
show(
color(p_line3d(line,.3,closed=1),"blue",.1),
color(p_line3d(cir1,.3,closed=1),"violet",.2),
color(p_line3d(fillet5,.3),"blue"),
color(p_line3d(fillet6,.3),"magenta"),
color(p_line3d(fillet7,.3),"cyan"),
color(p_line3d(fillet8,.3),"green"),
)
