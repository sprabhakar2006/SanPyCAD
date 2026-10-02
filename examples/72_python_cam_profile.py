# Cam profile
# Real project from the ocad examples notebook.
# Demonstrates corner_radius()/equidistant_path() for a 2D cam profile, then
# extrude_wave2path() to wrap it into a 3D cam surface, and path_extrude_open()
# to build the follower/pin solid that rides on it.

l_1=corner_radius(pts1([[0,50],[90,0,100],[180,-20,100],[360,0]]),30)
l_1=rot('x90',equidistant_path(l_1,360))
p1=c2t3(arc(30,0,362,s=360))
l_2=extrude_wave2path(l_1,p1)
l_3=[[-5,0],[5,0]]
surf_1=path_extrude_open(l_3,l_2)
surf_2=c2t3(c3t2(surf_1))
sol_1=[surf_2[i]+flip(surf_1[i]) for i in range(len(surf_1))]
c1=circle(3)
sol_2=path_extrude_open(c1,l_2[10:190])

show(difference(swp(sol_1), swp(sol_2)))
