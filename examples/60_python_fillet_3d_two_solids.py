# Fillet at the intersection of two solids
# From the "Basics of Drawing and 3D Modeling" tutorial (Python mode, SanPyCAD)

# fillets at the insection of 2 solids 
s1=sphere(20)
c1=rot('y45',cylinder(r=5,h=50,s=50))
l1=contiguous_chains(two_solids_intersection(s1,c1))[0]
l1=equidistant_pathc(l1,100)
l2=o_3d(l1,s1,-2,outside=0)
l3=o_3d(l1,c1,2,triangulation_type=1,outside=0)
f1=convert_3lines2fillet(l2,l3,l1,closed_loop=1)
show(
*[color(p_line3d(p,.2),"blue") for p in [l1,l2,l3]],
color(swp(s1),alpha=0.3),
color(swp(c1),alpha=0.3),
swp_c(f1),
)
