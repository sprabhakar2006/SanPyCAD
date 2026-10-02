# M35 bolt with engineering dimension callouts
# Real project from the ocad examples notebook.
# The geometry itself is a bolt/hub design built with wrap_around() and
# solid_from_2surfaces(), but the real teaching point here is the
# dim_linear()/dim_radial()/dim_angular() functions, which generate 3D
# text+leader-line annotations (txt1..txt19 below) that get dropped straight
# into the fo() text alongside the model - a technique not shown elsewhere
# in these examples.

p0=[15,0]
p1=[15,45]
cir1=circle(7.5,[0,75-7.5])
p2=p_cir_t(p1,cir1)
p4=[-15,45]
p3=cir_p_t(cir1,p4)
arc1=arc_2p(p2,p3,7.5,-1,45)
p5=[-15,0]
p0,p1,arc1,p4,p5=[[15,0,0]],[[15,45,20]],c2t3(arc1),[[-15,45,20]],[[-15,0,0]]
sec=corner_radius(p0+p1+arc1+p4+p5,10)
sec=translate([0,.1,0],sec)

path=corner_radius(pts1([[0,0],[45,0,7],[45*cos(d2r(30)),45*sin(d2r(30))]]),50)
path=rot('x90z90',path)

surf0=wrap_around(sec,path)
surf1=sec2surface_1(surf0)
surf2=surface_offset(surf1,4)
sol=solid_from_2surfaces(surf1,surf2)
sol=translate([0,0,9],rot('z-90',sol))

sec2=translate([0,0,-2],linear_extrude(circle(3.75,[0,75-7.5]),6.1))
surf3=[ wrap_around(p,path) for p in sec2]

sol1=flip(translate([0,0,9],rot('z-90',surf3)))

path1=cytz(pts([[0,9],[25.5+19.5,0],[(30-7.5)*cos(45*pi/180),(30-7.5)*sin(45*pi/180)]]))

sec3=[[-30,-15]]+arc_2p([0,-15],[0,15],15,-1,20)+[[-30,15]]
p6=l_cir_ip([[-30,-15+10.5],[0,-15+10.5]],circle(7.5))
p7=l_cir_ip([[-30,15-10.5],[0,15-10.5]],circle(7.5))
sec4=[[-30,-15+10.5]]+arc_long_2p(p6[0],p7[0],7.5,-1,30)+[[-30,15-10.5]]

sec5=circle(6)
path2=corner_radius(pts1([[0,-15.1],[0,4.6],[-3,0],[0,21],[3,0],[0,4.6]]),5)
sol2=translate([-30+12,0,11.25],rot('x-90',prism(sec5,path2)))


sec6=[[25.5+9,-15.1]]+arc_2p([25.5+9,0],[25.5,0],4.5,-1)+[[25.5,-15.1]]
txt1=dim_linear(translate([0,0,9],[sec6[-1],sec6[0]]),3)
txt2=dim_linear(point_vector(translate([0,0,9],sec6[-1]),[0,0,4]),-2)
txt3=dim_radial(translate([0,0,22.5],sec4[10:-1]))
txt4=dim_linear(translate([0,0,22.5],[sec4[-1],sec4[0]]),2)
txt5=dim_radial(sol1[0][10:])
txt6=dim_radial(sol2[0])
txt7=dim_radial(sol2[2])
txt8=dim_radial(translate([0,0,22.5],sec3[12:-1]),outside=1)
txt9=dim_linear(translate([0,0,22.5],[sec3[-1],sec3[0]]),10)
l1=translate([0,-20,9],rot('z-90',path))[:2]
l2=translate([0,-20,9],rot('z-90',path))[-2:]

txt10=dim_angular(l1,l2)
txt11=dim_radial(translate([0,0,13],sec6[1:-1]))
txt12=dim_linear(translate([0,0,13],mid_line(flip(sec6[:2]),sec6[-2:])))
txt13=dim_linear(point_vector(c23(sec3[0]),[0,0,22.5]),6)
txt14=dim_radial(translate([0,0,9],rot('z-90',surf0[20:30])),outside=1)
txt15=dim_radial(translate([0,0,9],rot('z-90',surf0[1:10])),outside=1)
l1=translate([0,0,22.5],[sec4[-1],sec4[0]])
p0=center_arc3d(translate([0,0,22.5],sec4[1:-1]))
p1=vcost1(l1,p0)
txt16=dim_linear([p0,p1],0)
p0=center_arc3d(sol2[0])
l1=c23(sec3[:2])
p1=vcost1(l1,p0)
txt17=dim_linear(translate([0,-2,0],[p1,p0]),0)

l1=point_vector(c23(sec3[-1]),[0,0,22.5])
p0=center_arc3d(sol2[-1])
p1=vcost1(l1,p0)
txt18=dim_linear([p0,p1],2)

l1=cpo(sol2)[0][-2:]
txt19=dim_linear(l1,-5)
# dim_linear()/dim_radial()/dim_angular() build raw OpenSCAD text()-based
# leader-line annotations (no polyhedron() structure), so they have no
# Python-mode equivalent -- kept as a small residual fo() call, same
# treatment as track_points() in example 30. The model geometry itself is
# fully converted to show() below.
ring2_sol=swp_prism_h(linear_extrude(sec3,22.5),linear_extrude(sec4,22.5))
show(
color(difference(
swp(sol),
swp(linear_extrude(sec4,22.5)),
swp(flip(sol1)),
swp(linear_extrude(sec6,22.5)),
),alpha=0.3),
difference(swp_c(ring2_sol), swp(sol2)),
)
fo(f'''
{txt1}{txt2}{txt3}{txt4}{txt5}{txt6}{txt7}{txt8}{txt9}{txt10}{txt11}{txt12}
{txt13}{txt14}{txt15}{txt16}{txt17}{txt18}{txt19}
''')
