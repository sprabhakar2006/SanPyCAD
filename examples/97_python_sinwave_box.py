# Sinewave box (4-sided rippled panel box)
# Real project from the ocad examples notebook.
# Uses sinewave() to build two rippled 2D curves, surface_from_2_waves() to
# loft a rippled panel between them, then arrays 4 rotated copies of that
# panel and stitches the gaps between neighboring panels with
# convert_3lines2fillet() to close the box into one continuous shell.

w1=rot('x90',sinewave(100,2.5,1.5,100))
w2=rot('x90z90',sinewave(60,1.5,1.5,60))
s1=translate([50,-30,0],rot('y-90',surface_from_2_waves(w1,w2,1.5)))
s2=[cpo(rot(f'z{i}',s1)) for i in [0,90,180,270]]
l1=s2[0][-1]
l2=s2[1][0]
l3=translate([0,20,0],l1)
f1=cpo(convert_3lines2fillet(l1,l2,l3,s=30))[:-1]
f2=[rot(f'z{i}',f1[1:-1]) for i in [0,90,180,270]]
s3=cpo(s2[0]+f2[0]+s2[1]+f2[1]+s2[2]+f2[2]+s2[3]+f2[3])
s4=offset_solid_simple(s3,-2)
sol=s3+flip(s4)[:-2]
l1=flip(s4)[-6]
l2=flip(s4)[-3]
l3=offset_3d(l2,-3)
f3=convert_3lines2fillet(l3,l1,l2,s=20,closed_loop=1)

show(union(swp(sol), swp_c(f3)))
