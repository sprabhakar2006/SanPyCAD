# Material-handling trolley (hinge/piston assembly)
# Real project from the ocad examples notebook - the largest and most
# elaborate design in the set. A full frame + hinged-arm + hydraulic
# cylinder + counterweight + trolley-wheel assembly, built almost entirely
# from o_solid() (extrude a profile along a vector, offset from origin)
# and swp_prism_h() (loft between two same-length prisms). Each sub-part is
# commented by name (frame, hinge supports, long arm, cylinder body,
# piston, c-clamps, counterweight, trolley wheels) so it can be read as a
# catalog of how o_solid() covers most everyday mechanical shapes.

# frame
sec1=circle(12.5)
path1=c2t3(corner_radius(pts1([[0,0,5],[900,0,5],[0,600,5],[-900,0,5]]),10))

sol1=path_extrude_closed(sec1,path1)

path2=cr3dt([[600,0,0,5],[0,600,0,5],[0,0,500,5],[0,-600,0,5]],10)
sol2=align_sol_1(path_extrude_closed(sec1,path2))

sol3=translate([-100,0,0],sol2)

# hinge supports
fillet1=flip(fillet_line_circle([[0,75],[200,75]],circle(40,[100,120]),20,1))
fillet2=fillet_line_circle([[0,75],[200,75]],circle(40,[100,120]),20,3)
arc1=arc_long_2p(fillet1[-1],fillet2[0],40,-1)
sec2=[[0,0],[200,0],[200,75]]+fillet1+arc1+fillet2+[[0,75]]
sol4=translate([450,250,465],rot('x90',linear_extrude(sec2,20)))
sol5=translate([450,350,465],rot('x90',linear_extrude(sec2,20)))

# long arm
x1=o_solid([-1,0,0],circle(30),1800,-900,290,590,[0,0,0])
x2=o_solid([-1,0,0],circle(25),1800,-900,290,590,[0,0,0])
sol6=swp_prism_h(x1,x2)

# frame
sol7=o_solid([0,1,0],circle(12.5),600,0,100)
sol8=o_solid([0,1,0],circle(12.5),600,0,200)

# cylinder body
x3=o_solid([0,0,1],circle(40),300,135,150,-290)
x4=o_solid([0,0,1],circle(35),300,135,150,-290)
sol9=swp_prism_h(x3,x4)

# cylinder bottom cover
x5=o_solid([0,0,1],circle(40),20,135,150,-290)

# hinge of cylinder
sec1=corner_radius(pts1([[-20,-35,20],[40,0,20],[0,70],[-40,0]]))
sol10=o_solid([0,1,0],sec1,20,-10+290,150,125-20)

# piston
x6=o_solid([0,0,1],circle(35),20,175,150,-290)

# piston rod
x7=o_solid([0,0,1],circle(15),350,175,150,-290)

# cylinder top cover
x8=o_solid([0,0,1],circle(40),20,425,150,-290)


# c-clamp for hinge support
sec1=corner_radius(pts1([[-20,0,20],[40,0,20],[0,260,20],[-40,0,20]]),10)
sec1=equidistant_pathc(sec1,300)
sec2=offset(sec1,-19)

path1=corner_radius(pts1([[0,100],[0,-100,10],[70,0,10],[0,120]]),10)
path1=equidistant_path(path1,300)
path1=translate([0,0,0],rot('x90z90',path1))
fold1=wrap_around(sec1,path1)

fold2=wrap_around(sec2,path1)
surf1=[fold1]+[fold2]
surf2=surface_offset(surf1,-5)
sol11=[surf1[1]]+[surf1[0]]+[surf2[0]]+[surf2[1]]
sol11=translate([150,255,520],sol11)

# c-clamp for counterweight
x9=[surf1[1]]+[surf1[0]]+[surf2[0]]+[surf2[1]]
x9=translate([850,255,520],x9)

# catcher
arc1=c2t3(arc(200,-90,90,s=100))

sol12=path_extrude_open(circle(10),arc1)
sol12=translate([-1090,290,590],sol12)

# hinge pin c-clamp
sol13=o_solid([0,1,0],circle(5),100,240,150,590)

# hinge pin cylinder mounting
sol14=o_solid([0,1,0],circle(5),100,240,150,90)

# hinge pin long arm
sol15=o_solid([0,1,0],circle(5),140,220,550,590)

# hinge pin counterweight
x10=o_solid([0,1,0],circle(5),100,240,850,590)


# rod for counterweight
x11=o_solid([0,0,1],circle(15),300,225,850,-290)

# counterweight
s1=corner_radius(pts1([[100,20],[-120,0,19],[0,-40,19],[120,0]]),10)+arc_long_2p([100,-20],[100,20],100,1,50)

x12=o_solid([0,0,1],s1,100,235,850,-290,[90,0,0])

# support for counterweight
x13=o_solid([0,0,1],circle(100),10,225,850,-290)

# trolley wheel
s1=circle(15)
p1=rot('x90',circle(50))
wh=path_extrude_closed(s1,p1)
wh=align_sol_1(wh)
s2=circle(4)
p2=[[-50,0,0],[50,0,0]]
spk=[axis_rot([0,1,0],path_extrude_open(s2,p2),i) for i in linspace(0,360,6)[:-1]]


show(
# frame
swp_c(sol1),
swp_c(sol2),
swp_c(sol3),
swp(sol7),
swp(sol8),

# hinge supports
swp(sol4),
swp(sol5),
*[swp(translate([-400,i,-500],sol4)) for i in [20,80]],
swp_c(sol6),

# cylinder body
color(swp_c(sol9),alpha=0.3),
# cylinder bottom cover
swp(x5),

# hinge for cylinder
swp(sol10),

# piston
swp(x6),

# piston rod + cylinder top cover
color(union(swp(x7), swp(x8)),"cyan"),

# c-clamp for pivot point hinge support
swp(sol11),

# catcher
swp(sol12),

# hinge pin
color(swp(sol13),"cyan"),

# hinge pin cylinder
color(swp(sol14),"cyan"),

# hinge pin long arm
color(swp(sol15),"cyan"),

# c-clamp for counterweight
swp(x9),

# hinge pin counterweight
color(swp(x10),"cyan"),

# rod for counterweight
color(swp(x11),"cyan"),

# counterweight
swp(x12),

# counterweight support
color(swp(x13),"cyan"),

# trolley wheels
*[swp_c(translate([j,i,0],wh)) for j in [0,900] for i in [-30,630]],
*[swp(translate([j,i,0],p)) for j in [0,900] for i in [-30,630] for p in spk],
)
