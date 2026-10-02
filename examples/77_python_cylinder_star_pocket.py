# Cylinder with a star-shaped pocket
# Real project from the ocad examples notebook.
# Builds a star profile by interleaving two circles' points via cpo() and
# rounding with corner_n_radius_list() (a per-corner radius list), then cuts
# it into a cylinder the same way as the rectangular-pocket example, using
# lines_fillets_solid() for the fillet where the pocket meets the walls.

t=2 # thickness
n=100 # number of segments of circle
s=5 # number of sides of the star
d=20 # outer diameter of the star
c1=circle(d,s=(s+1))
c2=c3t2(rot(f"z{360/(s+1)/2}",circle(d/4,s=(s+1))))
sec=l_(concatenate(cpo([c1,c2])))
r_l1=[1]*5
r_l2=[3]*5
r_l=l_(concatenate(cpo([r_l1,r_l2])))
sec=corner_n_radius_list(sec,r_l,10)
sec=homogenise(sec,.25,1)
c1=circle(20)
sol1=linear_extrude(c1,80)
sol2=linear_extrude(offset(c1,-t),80)
sol3=o_solid([1,0,0],sec,40,0,0,40)
e1=end_cap(sol1,t/2)
e2=end_cap_1(sol2,t/2)
l1,l2=ip(sol1,sol3),ip(sol2,sol3)
l3,l4,l5=mid_line(l1,l2),o_3d(l1,sol1,-t/2),o_3d(l2,sol2,-t/2)
sol4=lines_fillets_solid(l4,l1,l3,l2,l5,o=t/2)
sol4=sol4+[sol4[0]]
show(difference(
swp(sol1),
swp(sol2),
swp(sol3),
*[swp_c(p) for p in e1],
*[swp(p) for p in e2],
swp_c(sol4),
))
