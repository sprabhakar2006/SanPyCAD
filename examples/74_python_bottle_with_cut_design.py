# Bottle with a wrapped cut design
# Real project from the ocad examples notebook.
# Demonstrates psos() - projecting a surface onto another solid without
# losing its original point layout - to stamp a repeated decorative cut
# pattern (rotated 3x by 120 degrees) onto a bottle body built with prism().

sec=circle(10,s=100)
path=corner_radius(pts1([[-3,0],[3,0,3],[3,5,7],[-5,20,100],
                        [8,30,20],[-11,10,5],[0,10,0]]),30)
path=equidistant_path(path,100)
sol=prism(sec,path)

sec1=corner_radius(pts1([[-7.5,10,3],[15,0,3],[0,20,30],
                        [-3,20,30],[0,10,4.4],[-9,0,4.4],
                        [0,-10,30],[-3,-20,30]]),10)

sec1=equidistant_pathc(sec1,100)
sec1=reorient_sec(sec1)
path1=corner_radius(pts1([[1,0],[-1,0,1],[-1,2,2],[-2,0]]),10)
path1=equidistant_path(path1,10)
s1=prism2cpo(prism(sec1,path1))
s1=[equidistant_path(p,100) for p in s1]
p1=rot('y90',path)
s1=[wrap_around(p,p1)  for p in s1]
s1=translate([0,10,0],rot('z-90',s1))
p2=rot('y90',circle(10,s=200))
s1=[wrap_around(p,p2) for p in s1]
s1=rot('y-90z30',s1)
sol=psos(s1,sol,[0,-1,0],1e5,1,4)
s1=rot('z120',s1)
v1=rot('z120',[0,-1,0])
sol=psos(s1,sol,v1,1e5,1,4)
s1=rot('z120',s1)
v1=rot('z240',[0,-1,0])
sol=psos(s1,sol,v1,1e5,1,4)
sol1=surface_offset(sol,.5)
bottle=sol+flip(sol1)[:-16]
bottle=smoothening_by_subdivison_surf(bottle,2,[1,0])
show(swp(bottle))
