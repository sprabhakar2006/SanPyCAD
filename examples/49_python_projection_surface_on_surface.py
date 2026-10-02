# Projection of one surface onto another
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

s1=sphere(30,s=200)
c1=circle(15,s=6)
c2=rot2d(360/5/2,circle(5,s=6))
s2=a_(c23(concatenate(cpo([c1,c2]))))+[0,0,2]
s2=cr2d(s2,10)
s3=c23([s2,offset(s2,-2.5),offset(s2,-4),offset(s2,-5)])
s3=bspline_surface(s3,3,3,100,10,[1,0])
s4=psos(c_(s1),s3,[0,0,1])
show(
#*[color(p_line3d(p,.03,closed=1),"blue") for p in s4],
color(swp(s1),alpha=0.3),
swp_c(s3),
swp_c(s4),
)
