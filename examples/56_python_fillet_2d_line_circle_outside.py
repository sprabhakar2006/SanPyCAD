# Fillet between a line and a circle (outside)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# fillet between line and circle (outside)
h=12
line=[[-10,h],[30,h]]
cir1=circle(10,[10,10])
r2=5
s=20
fillet1=fillet_line_circle(line,cir1,r2,1)
fillet2=fillet_line_circle(line,cir1,r2,2)
fillet3=fillet_line_circle(line,cir1,r2,3)
fillet4=fillet_line_circle(line,cir1,r2,4)
show(
color(p_line3d(line,.3,closed=1),"blue",.1),
color(p_line3d(cir1,.3,closed=1),"violet",.2),
color(p_line3d(fillet1,.3),"cyan"),
color(p_line3d(fillet2,.3),"blue"),
color(p_line3d(fillet3,.3),"magenta"),
color(p_line3d(fillet4,.3),"green"),
)
