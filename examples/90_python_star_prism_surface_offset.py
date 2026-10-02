# Star prism through a curved shell, with a socket-and-pin joint
# Real project from the ocad examples notebook.
# Demonstrates offset_3d() on a section that is *not* planar (a star ring
# with alternating z-heights) plus ip_surf() to intersect a swept shell
# with the star prism, and sol2vector() to re-orient an assembled sub-part
# so it sits flush against an arbitrary surface normal.

t=1.1 # thickness
s=10 # number of sides of the star
d=20 # outer diameter of the star
h=50 # height of the star prism
cir1=circle(d,s=(s+1))
cir2=c3t2(rot(f"z{360/(s+1)/2}",circle(d/4,s=(s+1))))
sec1=array(c2t3([cir1,cir2]))
sec1=sec1.transpose(1,0,2).reshape(-1,3)
sec1=[(sec1[i]+[0,0,1]).tolist() if i%2==0 else (sec1[i]+[0,0,t]).tolist() for i in range(len(sec1)) ]
sec1=m_points(corner_radius(sec1,20),1.1)
sol1=linear_extrude(sec1,h)

line1=corner_radius(pts1([[-20,0],[20,15,30],[20,-15]]),40)
line2=cytz(line1)
surf1=surf_extrude(line1,line2)

ip1=ip_surf(surf1,sol1)
ip2=offset_3d(ip1,-2.01)

surf4=[ip2,ip1,translate([0,0,-t],ip1),translate([0,0,-t],ip2),ip2]
avg2=array(surf4).mean(0).mean(0)

sec3=circle(5)
path3=m_points_o(corner_radius(pts1([[-4,0],[0,15,2],[3.5,4,2],[0,1]]),5),.5)

sol3=prism(sec3,path3)

path4=rot('z90x90',cytz([[i,3*sin(d2r(i*20))] for i in linspace(0,20,44)]))
sol4=sol2path(sol3,path4)
v1=-array(nv(sol4[-1]))
avg1=array(sol4[-1]).mean(0)
surf4=translate(-avg2+[0,0,-.5],surf4)
surf4=sol2vector(v1,surf4,avg1)

arc1=arc_2p([0.01,0],[4.65,0],3,-1)
arc2=[rot(f'z{i}',arc1) for i in arange(0,360,360/50)]
arc2p=translate([0,0,5],arc2)
arc2=array([arc2,arc2p]).transpose(1,0,2,3)

arc3=arc_2p([0.01,0],[4.65,0],3,1)
arc4=[rot(f'z{i}',arc3) for i in arange(0,360,360/50)]
arc4p=translate([0,0,5],arc4)
arc4=array([arc4,arc4p]).transpose(1,0,2,3)

arc5=circle(4.5)
path5=arc_2p([0,0],[-4.5,2],10,-1)
sol5=prism(arc5,path5)

ip1=[ip_sol2sol(sol5,p,-1) for p in arc2]
ip2=[ip_sol2sol(sol5,p,-1) for p in arc4]

ip1=sol2vector(v1,ip1,avg1)
ip2=sol2vector(v1,ip2,avg1)
sol5=sol2vector(v1,sol5,avg1)

show(
swp_c(flip(surf4)),
swp(sol4),
difference(
swp(flip(sol5)),
*[p_line3d(p,.05,rec=1) for p in ip1],
*[p_line3d(p,.05,rec=1) for p in ip2],
),
)
