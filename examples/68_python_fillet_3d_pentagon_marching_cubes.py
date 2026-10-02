# Fillet on a swept pentagon profile, reconstructed via marching cubes
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)
# Computationally heavy: builds a fillet surface via marching cubes over many
# offset/intersection steps. May take a while to evaluate.

t0=time.time()
sec1=circle(10,s=6)
pent1=circle(7,s=6)
pent2=c3t2(rot(f'z{360/5/2}',circle(3.5,s=6)))
sec2=concatenate(cpo([pent1]+[pent2])).tolist()
sec2=corner_radius(array(c2t3(sec2))+[0,0,.3],5)
sec3=concatenate(cpo([pent1]+[pent2])).tolist()
sec3=offset(sec3,-1)
sec3=corner_radius(array(c2t3(sec3))+[0,0,.3],5)
path1=helix(20,30,1,5)
path2=[[0,0,10],[-30,20,13]]
sol=path_extrude_open(sec2,path1)
sol1=path_extrude_open(sec3,path2)
sol2=sol[20:40]
r=1+.2
n=50
a1=arc(r,180,270,[r,r],n)
a=[offset_solid(sol2,x-.2) for (x,y) in a1]
b=[offset_solid(sol1,y-.2) for (x,y) in a1]
l1=[two_solids_intersection(a[i],b[i]) for i in range(n)]

l2=concatenate([homogenise(remove_seg_with_len_lessthan_d(p,.01),.1) for p in l1]).tolist()
s1=marching_cubes_surface_from_points_list(l2,0.2,[104,101,79])
show(
swp(sol),
swp(sol1),
swp_triangles(s1),
)
t1=time.time()
t1-t0
