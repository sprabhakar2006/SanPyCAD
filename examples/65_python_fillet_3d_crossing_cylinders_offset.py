# Fillet between two crossing cylinders (offset + hull strategy)
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

s2=linear_extrude(circle(10,s=200),30)
s3=translate([10,0,5],linear_extrude(circle(5,s=100),20))
p1=corner_radius_with_turtle([[1,0],[-1,0,1],[0,1]],20)
s4=[ translate([10,0,5-x],linear_extrude(offset(circle(5,s=100),x),20+2*x)) for (x,y) in p1]
s5=[linear_extrude( offset(circle(10,s=200),y),30) for(x,y) in p1]

show(
swp(s2),
swp(s3),
*[hull(
    intersection(swp(s4[i]),swp(s5[i])),
    intersection(swp(s4[i+1]),swp(s5[i+1])),
  ) for i in range(20)],
)
