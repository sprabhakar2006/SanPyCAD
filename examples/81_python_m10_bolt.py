# M10 bolt with hex head
# Real project from the ocad examples notebook.
# Demonstrates c_hull() (convex hull of 2D sections) to build the hex-ish
# head blank, corner_radius3d_with_turtle() for the shank path, swp_prism_h()
# for the lofted transition, and convert_3lines2fillet() with i_p_p()/
# offset_3d() for the fillets under the head and at the shank tip.

c1=circle(17.5)
c2=circle(7.5,[14.5,0])
c3=circle(7.5,[-14.5,0])
sec1=c_hull(c1+c2+c3)
c4=circle(3,[14.5,0])
c5=circle(3,[-14.5,0])
c6=circle(10)
c7=circle(6.5)
path=corner_radius3d_with_turtle([[0,0,-0.01],[0,0,29,17.5],[-44,0,0]],30)
c8=circle(19.5)
c9,c10,c11,c12=[rot2d(i,circle(2.5,[15,0])) for i in [0,90,180,270]]
s1=linear_extrude(sec1,5.5)
s2,s3=[translate([0,0,0],linear_extrude(p,5.5)) for p in [c4,c5]]
s4=align_sol_1(path_extrude_open(c6,path))
s5=linear_extrude(c8,4)
s6,s7,s8,s9=[translate([0,0,0], linear_extrude(p,4)) for p in [c9,c10,c11,c12]]
s5,s6,s7,s8,s9=[translate(a_(path[-1])+[4.01,0,0], sol2vector([-1,0,0],flip(p))) for p in [s5,s6,s7,s8,s9]]
s10=align_sol_1(path_extrude_open(circle(6.5),path))
s11=swp_prism_h(s4,s10)
l1=i_p_p(s4,s4[0],5.5)
l2=offset_3d(l1,1.25)
l3=i_p_p(s4,s4[0],5.5+1.25)
f1=convert_3lines2fillet(l2,l3,l1,closed_loop=1)

l4=i_p_p(s4,s4[-1],-4)
l5=offset_3d(l4,1.25)
l6=i_p_p(s4,s4[-1],-4-1.25)
f2=convert_3lines2fillet(l6,l5,l4,closed_loop=1)
e1=end_cap(s1,1.25)
e2=end_cap(s5,1.25)
e3=end_cap_1(s2,.5)
e4=end_cap_1(s3,.5)
e5,e6,e7,e8=[ end_cap_1(p,.5)  for p in [s6,s7,s8,s9]]
e9=end_cap_1(s10,1.25)
ey=l_(concatenate([e3,e4,e5,e6,e7,e8,e9]))
# OpenSCAD's difference() only keeps its very FIRST child as the base --
# every other child (including later for-loop iterations) is subtracted,
# not unioned. So only s1 is the base; s5,s2,s3,s4,s6-s9,e1,e2,ey are all
# subtracted from it, matching the original fo() text exactly.
show(
union(
difference(
swp(s1),
swp(s5),
swp(s2),
swp(s3),
swp(s4),
swp(s6),
swp(s7),
swp(s8),
swp(s9),
*[swp_c(p) for p in e1],
*[swp_c(p) for p in e2],
*[swp(p) for p in ey],
),
difference(swp_c(s11), *[swp(p) for p in e9]),
swp_c(f1),
swp_c(f2),
)
)
