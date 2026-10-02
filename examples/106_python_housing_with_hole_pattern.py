sol1=linear_extrude(sec1,10)
sol2=translate([0,0,2],prism(sec2,path))
sol3=[linear_extrude(p,10) for p in holes]
e1= concatenate([ end_cap_1(p,1,s=2) for p in sol3])
e2= end_cap_1(sol2,1)[1]
e3=end_cap(sol1,1)
show(
difference(
swp(sol1),
    swp(sol2),
    *[ swp(p) for p in sol3],
    *[ swp(p) for p in e1],
    swp(e2),
    *[swp_c(p) for p in e3]
)
)