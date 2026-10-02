# Fillet on a closed-path sweep using a rolling-arc strategy
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

t0=time.time()
# another strategy for filleting
c1=circle(5)
p1=sec_start_pos(c23(circle(20)),35)
sol1=path_extrude_closed(c1,p1)
sol2=rot('x90',sol1)
r=2
a1=cr2dt([[r,0],[-r,0,r],[0,r]],50)
a=l_(a_([path_extrude_open(offset(c1,x,2),p1[10:19]) for (x,y) in a1]).round(3))
b=l_(a_([ rot('x90',path_extrude_open(offset(c1,y,2),p1[10:19])) for (x,y) in a1]).round(3))
show(
swp_c(sol1),
swp_c(sol2),
*[intersection(swp(rot(f'z{ang}',a[i])),swp(rot(f'z{ang}',b[i])))
  for ang in [0,180] for i in range(len(a1))],
)

t1=time.time()
t1-t0
