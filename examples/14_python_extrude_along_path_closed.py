# Extrude a section along a closed path
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# triangular section extruded along closed path
sec=[[0,0],[5,0],[2.5,4]]
path=c23(circle(20))
sol=sweep_sec2path(sec,path,mirror=1,orientation=3,closed_loop=1)

# pay attention to the swp_c() call here -- swp_c() is to be used where
# the loop is closing like the way here
show(
swp_c(sol),
*[color(p_line3d(p,0.2,closed=1),"blue") for p in [sec,path]],
)
