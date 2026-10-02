# Fillet on a swept pentagon-derived profile
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

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
a1=cr2dt([[1.1,0],[-1.1,0,1.1],[0,1.1]],90)
a=l_(a_([path_extrude_open(offset(sec3,x,2),path2) for (x,y) in a1]).round(3))
b=l_(a_([path_extrude_open(offset(sec2,y,2),path1[25:35]) for (x,y) in a1]).round(3))

show(
*[intersection(swp(a[i]),swp(b[i])) for i in range(len(a1))],
color(swp(sol),"cyan"),
color(swp(sol1),"orange"),
)
t1=time.time()
t1-t0
