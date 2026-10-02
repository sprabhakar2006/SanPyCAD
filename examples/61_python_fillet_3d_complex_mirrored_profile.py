# Complex fillet using a mirrored fillet profile swept along a path
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# Complex fillets
l1=c23(cr2dt([[0,0],[50,0,4],[0,10,4],[-50,0,4],[0,10,4],
         [50,0,4],[0,10,4],[-50,0,4],[0,10,4],
         [50,0,4],[0,10,4],[-50,0,4],[0,10,4],[50,0]],22))
s1=square([50,60])
c1=circle(3)
sol1=path_extrude_open(c1,l1)
p1=cr2dt([[-3,-1.5],[3,0],[0,3],[-3,0]],10)
p2=cr2dt([[-3,-3],[3,0,1],[0,6,1],[-3,0]],10)
sol2=prism(s1,p1)
sol3=prism(s1,p2)
l2=point_vector([-5,1.5],[5,0])
l3=point_vector([-5,-1.5],[5,0])
f1=fillet_line_circle(l2,c1,2.5,3,s=21)
p0=s_int1([l2]+seg(c1))[0]
f1=[p0]+f1
f2=c32(flip(mirror_line(c23(f1),[0,1,0],[0,0,0])))
f3=c32(flip(mirror_line(c23(f1),[1,0,0],[0,0,0])))
f4=c32(flip(mirror_line(c23(f3),[0,1,0],[0,0,0])))
s2=path_extrude_open(f1,l1)
s3=path_extrude_open(f2,l1)
s4=path_extrude_open(f3,l1)
s5=path_extrude_open(f4,l1)
sol4=offset_solid_simple(sol1,-.25)
pl1=plane_from_equation([1,0,0,-2],[20,20])
pl2=translate([0,60,0],plane_from_equation([1,0,0,60],[20,20]))
a=nlos(pl1,sol4[0])
b=nlos(pl2,sol4[-1])
sol4=[a]+sol4+[b]
# OpenSCAD's difference()/intersection() only keep their FIRST child as
# a single item -- every subsequent child (including later for-loop
# iterations) is a separate operand, not auto-unioned. The original fo()
# text had no explicit union() wrapping [sol1,sol2] or [s2,s3,s4,s5], so
# this is sol1-sol2-sol4 and sol3 INTERSECTED individually with each of
# s2,s3,s4,s5 (not sol3 intersected with their union).
show(
difference(swp(sol1),swp(sol2),swp(sol4)),
intersection(swp(sol3),swp(s2),swp(s3),swp(s4),swp(s5)),
)
