# Chimney panel support bracket
# Real project from the ocad examples notebook.
# The bracket profile follows a bezier()-smoothed path built from
# arc_3p_3d() (arc through 3 points in 3D).

sec=corner_radius(pts1([[0,5],[0,-5,3.5],[10,0,4],[2,1,1],[34,0,4],[1,3.5]]),10)
sec1=path_offset(sec,-3)
path=bezier([[-27.5,0,3]]+ arc_3p_3d([[-27,0,3],[0,0,0],[27,0,3]],100)+[[27.5,0,3]],100)
sol=path_extrude_open(sec,path)
sol1=path_extrude_open(sec1,path[1:-1])
sec2=corner_radius(pts1([[0,0],[25,0,.5],[0,4,.5],[-1,3,.5],[-1.5,0,.5],[-2,-3,1],[-20.5,0]]),10)
sol2=translate([0,-17,1],path_extrude_open(sec2,path[47:-47]))
sec3=corner_radius(pts1([[-6,-5,5],[12,0,5],[0,10.0001,5],[-12,0,5]]),10)
sol3=o_solid([0,0,1],sec3,5,0,0,37)
sec4=corner_radius(pts1([[0,0],[5,0,10],[7,7,10],[14,0]]),20)
sec5=path_offset(sec4,-3)
sec6=sec4+flip(sec5)
sol4=translate([0,-25,1],path_extrude_open(sec6,path[16:30]))
sol5=translate([0,-25,1],path_extrude_open(sec6,path[-30:-16]))
# rotate([-90,0,0]) wraps the whole assembly -- rotate each raw point
# structure before swp() since rot() doesn't operate on built Mesh objects.
sol_r,sol1_r,sol2_r,sol3_r,sol4_r,sol5_r=[rot('x-90',p) for p in [sol,sol1,sol2,sol3,sol4,sol5]]
show(
union(
difference(swp(sol_r), swp(sol1_r), swp(sol3_r)),
swp(sol2_r),
swp(sol4_r),
swp(sol5_r),
)
)
