# Wrap a prism section along a helix path
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

c1=rot2d(-90,cr2dt([[-4,0],[8,0],[-4,6,1]],10))
path=m_points1_o(cr2dt([[-2,0],[2,0.5,2],[0,50,2],[-2,0.5]],10),200,.01)
sol=prism(c1,path)
path1=helix(10,8.5,5,10)
path1=path2path1(path,path1)
# extruding sol to path1
sol1=sol2path(sol,path1)
show(swp(sol1))
#show(color(p_line3d(path,.5,1),"blue"))
