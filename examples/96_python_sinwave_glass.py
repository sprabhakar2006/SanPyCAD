# Sinewave-textured glass/vase
# Real project from the ocad examples notebook.
# Builds a 2D-indexed grid of z-height offsets with a double sin()
# modulation (one frequency along the height, one around the
# circumference), then wraps that rippled grid around an arc() path with
# wrap_around() to texture a curved vessel wall - a good example of
# treating a nested list comprehension as a height-field before wrapping it
# onto a solid.

height=125
dia=100
width=pi*dia
factor=round(width/height,0)
sec=[[[i,j,1*sin(d2r(i*360/height*3))*sin(d2r(j*360/width*3*factor))] for j in linspace(0,width,150)] for i in linspace(0,height,100)]
path=rot('y90',arc(dia/2,0,400,s=200))

surf1=[wrap_around(p,path)[:-1] for p in sec]

surf2=offset_solid_simple(surf1,-2)

sol1=rot('y-90',swp_prism_h(surf2,surf1))

p0=sol1[2][:-1]
p1=sol1[15][:-1]
p2=offset_3d(p0,-15)
fillet1=convert_3lines2fillet(p2,p1,p0,s=30,closed_loop=1)

sol3=flip(sol1)[:-15]+flip(cpo(fillet1)[1:-1])

sol4=cut_plane([-1,0,0],[300,300],300,0,0,0)
txt1=dim_radial(fillet1[10][:-1])
# dim_radial() builds raw OpenSCAD text()-based annotation text with no
# Python-mode equivalent -- kept as a small residual fo() call, same
# treatment as track_points() in example 30.
show(difference(swp(sol3), swp(sol4)))
fo(f'''{txt1}''')
