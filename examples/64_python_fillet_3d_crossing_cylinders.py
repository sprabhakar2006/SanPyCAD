# Fillet between two crossing cylinders (hull strategy)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# another approach to create fillets

s2=translate([0,35,0],rot('x90',cylinder(r=5,h=70)))
s3=translate([-35,0,0],rot('y90',cylinder(r=5,h=70)))

p1=corner_radius_with_turtle([[1.5,0],[-1.5,0,1.5],[0,1.5]],20)
s4=[translate([0,35,0],rot('x90',cylinder(r=(5+x),h=70))) for (x,y) in p1]
s5=[translate([-35,0,0],rot('y90',cylinder(r=(5+y),h=70))) for (x,y) in p1]

show(
color(swp(s2),alpha=0.3),
color(swp(s3),alpha=0.3),
*[hull(
    intersection(swp(s4[i]),swp(s5[i])),
    intersection(swp(s4[i+1]),swp(s5[i+1])),
  ) for i in range(20)],
)
