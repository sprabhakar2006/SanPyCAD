# Car seat surface model
# Real project from the ocad examples notebook - the most advanced
# surface-modeling example in the set. Builds the whole seat as a network
# of free-form surfaces: surface_from_4_lines()/convert_3lines2surface()
# stitch boundary curves into patches, and mirror_surface()/mirror_line()
# reuse the left-half geometry for the right half. Padding/stitching
# details (seams, vents, and their surrounding fillets) are built with a
# repeated pattern of offset_3d()/bezier_closed() (cross-section loops) +
# psos() (project a surface onto another without losing its point layout)
# + solid_from_2surfaces(). i_t/f_t time the run with time.time() (already
# available -- ocad.py imports the time module itself).
# This one is long and computationally heavy - expect it to take a while.

i_t=time.time()
l1=cr2dt([[0,800],[0,-300],[0,-500/cos(d2r(30)),0]@rt(30), [400,0],
         [100,0,0]@rt(30),[0,70,0]@rt(30)])
l2=path_offset(l1[:2],-30)
a=arc_2p(l1[-1],l1[2],400,-1)
b=arc_2p(l1[2],l1[1],375,-1)
c=two_cir_tarc(a,b,100,s=10)
d=fillet_line_circle(l2,b,100,o=3)
l3=lineFromStartTillPoint(a,c[0],5)+c[1:]+ \
lineFromPointToPointOnLine(b,c[-1],d[0],5)[1:]+d+[l2[0]]
p0,p1,p2,p3=translate([0,0,100],l1[0]),translate([0,0,180],l1[1]), \
translate([0,0,110],l1[2]), translate([0,0,220],l1[3])
a1=arc_2p_3d([1,0,0],p0,p1,700)
a2=arc_2p_3d([1,0,0]@rt(30),p1,p2,800)
a3=arc_2p_3d([0,1,0],p2,p3,800)
x1,x2,x3=extend_arc3d(a3,15),extend_arc3d(flip(a1),10),flip(a2)
x4=fit_pline2line(x3,[x1[-1],x2[-1]])
s1=surface_from_4_lines(x1,x2,x3,x4)
l3p=plos(s1,c23(l3),[0,0,1],1,3)
a1m=mirror_line(a1,[0,0,1],[0,0,0])
a2m=mirror_line(a2,[0,0,1],[0,0,0])
a3m=mirror_line(a3,[0,0,1],[0,0,0])
l4=cr2dt([[0,0],[30,0],[50,-50],[50,0],[50,50],[30,0]])
l4m=mirror_line(l4,[1,0,0],[0,0,0])
l4=rot('y90z30',bspline_open(flip(l4m)+l4[1:],deg=3,s=20))
p4=c23(movePointOnLine(l1,l1[4],40))
l4=move(l4,p4,[0,0,0])
pl1=plane([0,1,0],[1000,1000],[700,0,0])
l4p=plos(pl1,l4,[-1,0,0]@rt(30),1,3)
x1,x2=l4p,l4
x3=plos(s1,equidistant_path([x1[0],x2[0]],10),[0,0,1],0,3)
x4=mirror_line(x3,[0,0,1],[0,0,0])
s2=slice_surface(surface_from_4_lines(x1,x2,x3,x4),20)
a2c=c23(bezier([[0,450],[150,100],[240,0]],20))
s3=slice_surface(convert_3lines2surface(a2,a2c,a2m,s=19),40)
x1,x2=s3[-1],s2[0]
x3=lineFromStartTillPoint(a3,x2[0],10)
x4=mirror_line(x3,[0,0,1],[0,0,0])
s4=slice_surface(surface_from_4_lines(x1,x2,x3,x4),40)
x1,x2,x3,x4=equidistant_path([a1[0],a1m[0]],19),s3[0],a1,a1m
s5=slice_surface(surface_from_4_lines(x1,x2,x3,x4),40)
surf1=s5+s3[1:]+s4[1:]+s2[1:]
x1=cpo(surf1)[0]
x2=path2path1(x1,flip(l3p))
s6=psos(s1,slice_sol([x2,x1],10),[0,0,1],1e7,1,3)
s7=flip(mirror_surface(s6,[0,0,1],[0,0,0]))
surf2=cpo(s6+cpo(surf1)[1:]+s7[1:])
surf3=cpo([ equidistant_path(line,100) for line in cpo(surf2)])
surf4=[ path_offset3d(p,-30) for p in surf3]
sol1=solid_from_2surfaces(surf3,surf4)
sol2=[ equidistant_pathc(bspline_closed(homogenise(p,30),3,200),200) for p in sol1]
sol2=cpo([equidistant_path(bspline_open(homogenise(p,30),3,200),200) for p in cpo(sol2)])
# maximum time consuming step
sol3=cpo([bezier(p,200) for p in cpo(sol2)])
s8=[p[100:] for p in sol3]
l1=bezier_closed(bezier_closed(surface2sec(s2),100),100)
l2=[offset_3d(l1,-i) for i in linspace(0,50,5)]
l2=psos(s8,l2,[0,1,0]@rt(30),1e7,0,3)
l3=translate([0,30,0]@rt(30),l2)
l4=flip(l2)+l3
pad1=cpo([bezier(p,30) for p in cpo(l4)])
l1=bezier_closed(offset_3d(bezier_closed(surface2sec(s4),100),-10),100)
l2=[offset_3d(l1,-i) for i in linspace(0,120,10)]
l2=psos(s8,l2,[0,1,0],1e7,1,3)
l3=translate([0,30,0],l2)
l4=flip(l2)+l3
pad2=cpo([ bezier(p,50) for p in cpo(l4)])
l1=bezier_closed(offset_3d(bezier_closed(surface2sec(s3),100),-30),100)
l2=[offset_3d(l1,-i) for i in linspace(0,130, 10)]
l2=psos(s8,l2,[1,0,0]@rt(30),1e7,0,3)
l3=translate([30,0,0]@rt(30),l2)
l4=flip(l2)+l3
pad3=cpo([bezier(p,70) for p in cpo(l4)])
l1=bezier_closed(offset_3d(bezier_closed(surface2sec(s5),100),-20),100)
l2=[offset_3d(l1,-i) for i in linspace(0,100,5)]
l2=psos(s8[:60],l2,[1,0,0],1e7,0,3)
l3=translate([30,0,0],l2)
l4=flip(l2)+l3
pad4=cpo([ bezier(p,30) for p in cpo(l4)])
l1=bezier(bspline_closed(homogenise(surface2sec(s6[:-2])[10:-17],50),3,300),100)
l2=bspline_closed(offset_3d(homogenise(l1,50),-10),3,200)
l3=[offset_3d(l2,-i) for i in linspace(0,30,5)]
l4=psos(cpo(s8)[:-5],l3,[-.2,-.2,.8],1e7,0,3)
l5=translate(a_([.2,.2,-1])*30,l4)
pad5=cpo([ bezier(p,30) for p in cpo(flip(l4)+l5)])
pad6=mirror_surface(pad5,[0,0,1],[0,0,0])
l1=sol3[0]
l2=i_p_p(sol3,l1,20)
l3=offset_3d(l1,-14.5)
f1=convert_3lines2fillet(l3,l2,l1,closed_loop=0)
ar1=solid_from_fillet_closed(f1,-15)
l1=sol3[-1]
l2=i_p_p(sol3,l1,-20)
l3=offset_3d(l1,-14.5)
f2=convert_3lines2fillet(l2,l3,l1)
ar2=solid_from_fillet_closed(f2,-15)
# rotate([90,0,0]) wraps the whole assembly -- rotate each raw point
# structure before swp() since rot() doesn't operate on built Mesh objects.
sol3_r,ar1_r,ar2_r=[rot('x90',p) for p in [sol3,ar1,ar2]]
pads_r=[rot('x90',p) for p in [pad1,pad2,pad3,pad4,pad5,pad6]]
show(
union(
difference(swp(sol3_r), swp_c(ar1_r), swp_c(ar2_r)),
*[swp(p) for p in pads_r],
)
)
f_t=time.time()
f_t-i_t
