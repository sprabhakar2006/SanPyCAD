# Mobile phone stand (wall / car seat-back hanging holder)
# Real project from the ocad examples notebook.
# Builds a single turtle-style profile with cr2dt() using inline @zrot(...)
# corner rotations, offsets it into two rails, and stitches the two rails
# into a surface per-segment with surface_from_4_lines() (for the straight
# runs) and slice_sol() (for the curved runs), finishing with end_cap().

a=cr2dt([[0,5,2.4],[0,-5,2.4],[120,0,2.4],[0,5,2.4],[7,0,2.4]@zrot(120),[5,0,2.4]@zrot(210),
        [4.1,0,.75]@zrot(300),[-15,0,5],[50,0,2.4]@zrot(120),[5,0,2.4]@zrot(210),
        [47.1,0,2.4]@zrot(300)],s=10)

a=rot('x90',a)
b=translate([0,150,0],a)
l1=c23(arc_2p([0,0],[0,50],100))
l2=rot('y60',l1)
l1p=c23(arc_2p([0,0],[0,50],200))
l2p=rot('y60',l1p)
l3=fit_pline2line(l1,[a[0],b[0]])
l4=fit_pline2line(l1,[a[21],b[21]])
s1=surface_from_4_lines(l3,l4,a[0:22],b[0:22])
s2=cpo(slice_sol([a[22:44],b[22:44]],20))
l5=fit_pline2line(l2p,[a[44],b[44]])
l6=fit_pline2line(l2p,[a[65],b[65]])
s3=surface_from_4_lines(l5,l6,a[44:66],b[44:66])
s4=cpo(slice_sol([a[66:88],b[66:88]],20))
l7=fit_pline2line(l2,[a[88],b[88]])
l8=fit_pline2line(l2,[a[109],b[109]])
s5=surface_from_4_lines(l7,l8,a[88:110],b[88:110])
s6=cpo(slice_sol([a[110:121],b[110:121]],20))
surf=flip(cpo(s1+s2+s3+s4+s5+s6))
e1=end_cap(surf,2)
show(difference(swp(surf), *[swp_c(p) for p in e1]))
