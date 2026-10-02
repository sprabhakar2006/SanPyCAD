# Car mobile phone stand (dashboard mount)
# Real project from the ocad examples notebook.
# Companion piece to the wall/seat-back stand example - this one uses
# o_solid() to make an angled base plate, ip_sol2sol() to find where a
# vertical cutting plane crosses the base, and convert_3lines2fillet() to
# round the phone pocket's lip.

sec=corner_radius(pts1([[-160/2-4,-15/2-4,23/2-.1],[160+2*4,0,23/2-.1],[0,15+2*4,23/2-.1],[-160-2*4,0,23/2-.1]]),10)
sol=o_solid([0,1,sqrt(3)],sec,60)
sol1=surface_offset(sol,4)
sol2=swp_prism_h(sol,sol1)
surf1=translate([0,0,10],plane([0,0,1],200))
ip1=ip_sol2sol(surf1,sol,0)
surf2=ip1[:22]+translate([0,100,0],ip1[22:44])
surf3=translate([0,0,-4],surf2)
sol3=[surf3]+[surf2]
sol4=o_solid([0,0,1],square(200,center=True),20,-10)

sec1=corner_radius(pts1([[-130/2,0],[130,0],[5,60],[-130-2*5,0]]),10)
sol5=o_solid([0,-sqrt(3),1],sec1,10,5,0,10)

fillet1=convert_3lines2fillet(translate([0,5,0],ip1[22:]),translate([0,2.4,4.34],ip1[22:]),ip1[22:])
show(
difference(swp_c(sol2), swp(sol4), swp(sol5)),
swp(sol3),
swp(fillet1),
)
