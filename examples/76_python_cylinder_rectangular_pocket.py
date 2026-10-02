# Cylinder with a rectangular pocket
# Real project from the ocad examples notebook.
# Demonstrates o_solid() for extruding a rounded-rectangle profile straight
# into a cylinder wall, then ip() (surface/surface intersection) plus
# lines_fillets_solid() to build a filleted transition where the pocket
# meets the outer and inner cylinder surfaces.

c1=circle(20,s=100)
sol1=linear_extrude(c1,80)
sol2=linear_extrude(offset(c1,-2),80)
sec=homogenise(cr2dt([[-15/2,-25/2,2],[15,0,2],[0,25,2],[-15,0,2]],10),.5,1)
sol3=o_solid([1,0,0],sec,30,0,0,40)
e1=end_cap(sol1,1)
e2=end_cap_1(sol2,1)
l1,l2=ip(sol1,sol3),ip(sol2,sol3)
l3,l4,l5=mid_line(l1,l2),o_3d(l1,sol1,-1),o_3d(l2,sol2,-1)
sol4=flip(lines_fillets_solid(l5,l2,l3,l1,l4,o=-1))
sol4=sol4+[sol4[0]]
show(difference(
swp(sol1),
swp(sol2),
swp(sol3),
*[swp_c(p) for p in e1],
*[swp(p) for p in e2],
swp_c(sol4),
))
