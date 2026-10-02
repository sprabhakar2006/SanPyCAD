# Phone back-camera clamp/bezel
# Real project from the ocad examples notebook.
# Wraps a set of horizontal section lines (h_lines_sec()) around a curved
# path with wrap_around() to build the clamp's contoured surface, then
# derives a separate fillet ring from interpolation_bspline_open() applied
# to offset section lines.

sec=corner_radius(pts1([[-37/2,0.1,3],[37,0,3],[0,15,2],[-5,24,13.5],[-27,0,13.5],[-5,-24,2]]),20)
l1=h_lines_sec(sec,120)
path=corner_radius(pts1([[0,0],[15,0,3.5],[15,41.21]]),10)
path=rot('x90z90',path)
l2=[wrap_around(p,path) for p in l1]
l3=surface_offset(l2,2)
sol=solid_from_2surfaces(l2,l3)
sol1=translate([0,0,-3],linear_extrude(circle(9,[0,28],s=100),10))
sol1=[wrap_around(p,path) for p in sol1]
slit=rot('x70',translate([-.5,15,-17],linear_extrude(square([1,20]),10)))
cyl1=cylinder(d=4,h=5)
# creating fillet
l1=surface2sec(l2)
l2=surface2sec(l3)
l3=mid_line(l1,l2)
l4,l5=surface_offset([l1,l2],-1)
s1=[interpolation_bspline_open(p,20,2) for p in cpo([l4,l3,l5])]
s2=surface_offset(s1,-2)
sol2=solid_from_2surfaces(s1,s2)
sol2=flip(sol2+[sol2[0]])
show(difference(
swp(sol),
swp(sol1),
swp(slit),
swp_c(sol2),
*[swp(translate([i,5,-2],cyl1)) for i in [-27/2,27/2]],
))
