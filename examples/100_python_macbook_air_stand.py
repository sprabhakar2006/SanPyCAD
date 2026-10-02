# MacBook Air M1 laptop stand
# Real project from the ocad examples notebook.
# Same technique family as the mobile-phone-stand examples: one turtle-
# style cr2dt() profile is duplicated and offset, then joined segment by
# segment with surface_from_4_lines() for straight runs and slice_sol()
# for the curved runs, and finally end_cap() closes the open ends.
# The final cut is plain Python -- show(difference(swp(sol1), *[swp_c(p)
# for p in e1])) -- instead of fo() text, now that swp()/swp_c() shapes
# carry real OpenSCAD geometry through difference() automatically.

a=cr2dt([[0,5,2.4],[0,-5,2.4],[160,0,2.4],[0,5,2.4],[7,0,2.4]@zrot(120),[5,0,2.4]@zrot(210),
        [4.1,0,.75]@zrot(300),[-15,0,5],[50,0,2.4]@zrot(150),[5,0,2.4]@zrot(240),
        [41.25,0,2.4]@zrot(330)],s=10)

a1=rot('x90',a)
a2=translate([0,150,0],a1)
arc1=arc_2p([0,0],[0,50],100)
arc2=rot('y60',arc_2p([0,0],[0,50],200))
arc3=rot('y30',arc_2p([0,0],[0,50],70))


l1=fit_pline2line(arc1,[a1[0],a2[0]])
l2=fit_pline2line(arc1,[a1[21],a2[21]])
l3=fit_pline2line(arc2,[a1[44],a2[44]])
l4=fit_pline2line(arc2,[a1[65],a2[65]])
l5=fit_pline2line(arc3,[a1[88],a2[88]])
l6=fit_pline2line(arc3,[a1[109],a2[109]])

s1=surface_from_4_lines(l1,l2,a1[:22],a2[:22])
s2=cpo(slice_sol([a1[22:44],a2[22:44]],20))
s3=surface_from_4_lines(l3,l4,a1[44:66],a2[44:66])
s4=cpo(slice_sol([a1[66:88],a2[66:88]],20))
s5=surface_from_4_lines(l5,l6,a1[88:110],a2[88:110])
s6=cpo(slice_sol([a1[110:],a2[110:]],20))
sol1=flip(cpo(s1+s2+s3+s4+s5+s6))

e1=end_cap(sol1,2.4)
show(
difference(
swp(sol1),
*[ swp_c(p) for p in e1]
)
)
