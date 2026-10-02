# Lamp shade
# Real project from the ocad examples notebook.
# Builds one tapered strand along a bezier() path with axis_rot() twisting
# it around the path's own tangent, then uses native OpenSCAD text inside
# fo() to array copies (rotate + mirror) around a full circle to form the
# radial strand pattern, capped by a ring base.

n=20 #number of strands in the lamp
t=5 # thickness of each strand
path=[[42,0],[62,50],[25,100],[25,180]]

path1=cytz(bezier(path,100))

path2=[axis_rot([0,0,1],path1[i],i/(len(path1)-1)*(180+1.8)) for i in range(len(path1)-1)]

sol=[]
for i in range(len(path2)):
    theta=ang(path2[i][0],path2[i][1])
    sol.append(translate(path2[i],rot(f'z{theta}', \
            offset(square(t,center=True),i/len(path2)*-1.5))))
sol=rot('z0',sol)

c1=circle(45)
c2=circle(30)


# The base ring is built by hollowing an extruded outer disc (c1) with an
# extruded inner disc (c2), using swp_prism_h() -- the Python equivalent of
# OpenSCAD's linear_extrude(2) difference(){polygon(c1);polygon(c2);}.
thetas=[i*360/n for i in range(n)]
sol_mirrored=mirror_surface(sol,[0,1,0],[0,0,0])
ring_sol=swp_prism_h(linear_extrude(c1,2),linear_extrude(c2,2))
show(
*[swp(rot(f'z{theta}',sol)) for theta in thetas],
*[swp(rot(f'z{theta}',sol_mirrored)) for theta in thetas],
swp_c(ring_sol),
)
