# Intersection between two polylines in 3D space
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# intersection between 2 polylines in 3d space
s1=sphere(20)
l1=c23(homogenise([[-10,0],[10,5]],1))
l1=plos(s1,l1,[0,0,1])
l2=c23(homogenise([[0,-15,0],[-7,5,0]],1))
l2=plos(s1,l2,[1,2,2])
p0=s_int1_3d_with_list(seg(l1)+seg(l2),o=0.1)[0]
show(
color(swp_surf(s1),alpha=0.3),
*[color(p_line3d(p,.3),"blue") for p in [l1,l2]],
color(points([p0[1]],.5),"magenta"),
)
# track_points() labels each point with its index via real OpenSCAD
# text()/linear_extrude() -- no Python-mode equivalent yet, so this one
# small piece still needs fo().
fo(f'''
{track_points(p0)}
''')
