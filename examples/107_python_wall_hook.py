

s1=surface_line_vector(sec_3d,[0,-30,0],1)
s2=sphere(20)
s3=intersection(swp(s1),swp(s2))
l2 = contiguous_chains(two_solids_intersection(s1, s2, 1, 1))
pl1=plane_from_equation([0,1,0,0],[50,50])
pl2=plane_from_equation([0,0,1,9.73],[50,50])
s4=flip(surface_line_vector(sec1_3d,[0,0,20]))
s3=difference(s3,swp(s4))
l3 = equidistant_path( contiguous_chains(two_solids_intersection(s2, s4, 0, 0))[0],50)
f1=flip(fillet_by_offset(l3,s2,s4,1.5,1.5,d=1))

l4 = contiguous_chains(two_solids_intersection(s1, s2, 0, 0))
x1=equidistant_pathc( l4[3],100)
f2=flip(fillet_by_offset(x1,s1,s2,1.5,-1.5,d=1,closed_loop=1))
l5 = contiguous_chains(two_solids_intersection(s1, s4, 0, 0))
x2=equidistant_path( l5[1],50)
f3=flip(fillet_by_offset(x2,s1,s4,1.5,1.5,d=1))
s3=resize(difference(s3,swp(f1),swp_c(f2),swp(f3)),[40,30,15])

show(s3)
