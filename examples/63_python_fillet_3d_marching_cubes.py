# Fillet surface reconstructed with marching cubes
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)
# Computationally heavy: builds a fillet surface via marching cubes over many
# offset/intersection steps. May take a while to evaluate.

l1=c23(cr2dt([[0,0],[50,0,4],[0,10,4],[-50,0,4],[0,10,4],
         [50,0,4],[0,10,4],[-50,0,4],[0,10,4],
         [50,0,4],[0,10,4],[-50,0,4],[0,10,4],[50,0]],22))
c1=circle(3)
sol1=path_extrude_open(c1,l1)
sol2=translate([0,0,-1.5],cube([50,60,3]))
r=1+.2
n=40
a1=arc(r,180,270,[r,r],n)
a=[offset_solid(sol1,x-.2) for (x,y) in a1 ]
b=[offset_solid(sol2,y-.2) for (x,y) in a1 ]
l1=[ two_solids_intersection(a[i],b[i],1,1) for i in range(n)]
l1=concatenate([ homogenise(p,0.1) for p in l1]).tolist()
s1=marching_cubes_surface_from_points_list(l1,.2,[208,248,20])
show(
swp_triangles(s1),
swp(sol1),
swp(sol2),
)
# use following commands in terminal
# /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD -o trial.obj trial.scad
# above will create an .obj file with file size much compressed
