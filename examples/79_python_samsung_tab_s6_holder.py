# Samsung Tab S6 car-seat holder
# Real project from the ocad examples notebook.
# A single long corner_radius() profile (built from turtle-style [dx, dy,
# radius] triples using explicit cos()/sin() offsets) forms the holder's
# frame, linear_extrude()'d and then relieved with an inner offset() before
# several prism() ribs/clips are added back with a mix of union and
# difference in the native OpenSCAD text passed to fo().

sec=corner_radius(pts1([[0,0,.1],[124,0,3],[27*cos(45*pi/180),27*sin(45*pi/180),1],
             [15*cos(135*pi/180),15*sin(135*pi/180),1],
             [5*cos((180+45)*pi/180),5*sin((180+45)*pi/180),1],
             [10*cos(-45*pi/180),10*sin(-45*pi/180),1],
             [17*cos((180+45)*pi/180),17*sin((180+45)*pi/180),1],
             [10*cos(135*pi/180),10*sin(135*pi/180),1],
             [8*cos(225*pi/180),8*sin(225*pi/180),1],[20*cos(135*pi/180),20*sin(135*pi/180),1],
             [8*cos(45*pi/180),8*sin(45*pi/180),1],
             [105*cos(135*pi/180),105*sin(135*pi/180),1],
             [8*cos(225*pi/180),8*sin(225*pi/180),1],
             [20*cos(135*pi/180),20*sin(135*pi/180),1],
             [8*cos(45*pi/180),8*sin(45*pi/180),1],[10*cos(135*pi/180),10*sin(135*pi/180),1],
             [17*cos(45*pi/180),17*sin(45*pi/180),1],[10*cos(-45*pi/180),10*sin(-45*pi/180),1],
             [5*cos(45*pi/180),5*sin(45*pi/180),1],[15*cos(135*pi/180),15*sin(135*pi/180),1],
             [21*cos(225*pi/180),21*sin(225*pi/180),1],[0,30,2],[-4,0,1]]),10)


sec1=corner_radius(pts1([[0,0,2],[17,0,2],[0,85,2],[-17,17,2]]),5)
path1=[[0,0],[0,6]]
sol=translate([123.5,7.7,30],rot("x90z45",prism(sec1,path1)))


sol1=translate([5,129,130],rot("x90z45",prism(sec1,path1)))

sec2=corner_radius(pts1([[0,0,4],[10,0,4],[0,40,4],[-10,0,4]]),5)
path2=[[0,0],[0,8]]
sol2=translate([-0.25,140,40],rot("x90z90",prism(sec2,path2)))

sol3=translate([-0.25,140,170],rot("x90z90",prism(sec2,path2)))

sec4=corner_radius(pts1([[0,0,0],[15,0,5],[0,90,5],[-15,0,0]]),5)
path4=[[0,0],[0,3]]
sol4=translate([90,35,0],rot("z45",prism(sec4,path4)))

sec6=corner_radius(pts1([[0,0,5],[90,0,5],[0,110,5],[-90,90,5]]),5)
path6=[[0,0],[0,7]]

sol6=translate([15,6,25],rot("x90",prism(sec6,path6)))
sol7=translate([-1,15,25],rot("x90z90",prism(sec6,path6)))
sol8=translate([94,30,25],rot("x90z135",prism(sec6,path6)))

# rotate([90,0,0]) in the original applies to the whole assembly, so we
# rotate every raw point structure (before swp()) by x90 instead of the
# built shapes -- rot() only operates on raw point data, not Mesh objects.
base_outer_r=rot('x90',linear_extrude(sec,250))
base_inner_r=rot('x90',translate([0,0,-.05],linear_extrude(offset(sec,-4.5,2),250.1)))
sol_r=rot('x90',sol)
sol1_r=rot('x90',sol1)
sol2_r=rot('x90',sol2)
sol3_r=rot('x90',sol3)
sol4_r=rot('x90',sol4)
sol6_r=rot('x90',sol6)
sol7_r=rot('x90',sol7)
sol8_r=rot('x90',sol8)
show(
union(
difference(
swp(base_outer_r),
swp(base_inner_r),
swp(sol_r),
swp(sol1_r),
swp(sol2_r),
swp(sol3_r),
swp(sol6_r),
swp(sol7_r),
swp(sol8_r),
),
swp(sol4_r),
)
)
