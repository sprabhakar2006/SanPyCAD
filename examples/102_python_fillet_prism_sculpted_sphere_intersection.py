# Fillet along the real intersection curve of two arbitrary (non-
# primitive) solids: a swept prism and a sphere whose surface has been
# sculpted with a projected sine-wave groove.
#
# Pipeline:
#   1. a: a closed 2D profile (cr2dt), re-centered on its own centroid so
#      the prism swept from it sits nicely at the origin.
#   2. s1 = prism(a, p1): sweeps that profile along path p1 -- one of the
#      two solids being filleted.
#   3. b starts as a plain sphere, then gets sculpted: l1/l2/l3 build a
#      sine-wave path swept into a surface (s2 = sweep_sec2path(l1, l3)),
#      and psos() projects that surface onto the sphere along a tilted
#      direction -- b=psos(s2, b, ...) -- imprinting a wavy groove into
#      the sphere's own surface without losing its original point count.
#      Each resulting ring is then smoothed with bspline_closed() (a
#      raw per-station projection can leave a slightly rough surface).
#   4. two_solids_intersection(b, s1) finds where the two solids'
#      surfaces actually cross; contiguous_chains()[0] takes the first
#      closed loop of that (a real intersection can come back as several
#      disconnected chains), and equidistant_pathc() resamples it to a
#      uniform point spacing so the fillet built from it is well-behaved.
#   5. o_3d(l1, b, 7, outside=0) / o_3d(l1, s1, -3, outside=0) offset
#      that intersection curve a short distance ALONG each solid's own
#      surface (one into b, one into s1) -- convert_3lines2fillet() then
#      bezier-blends between those 2 offset curves and the original
#      intersection curve to build the fillet ribbon, and
#      solid_from_fillet_closed() closes it into a genuine solid.
#   6. The final shape is the overlap of the two solids
#      (intersection(swp(s1), swp(b))) with the fillet solid subtracted
#      (swp_c(f3)) -- rounding the internal seam where they meet, the
#      same technique 60_python_fillet_3d_two_solids.py uses on simpler
#      primitives, here applied to a swept prism and a non-spherical
#      (sculpted) blob.
#
# The commented-out color(p_line3d(...)) lines are handy while tuning the
# offset distances in step 5 -- uncomment them to see l1/l2/l3 (the
# intersection curve and its two offsets) drawn directly on top of the
# solids before committing to the fillet/subtract result below.

a=cr2dt([[-20,0,15],[40,0,15],[0,40],[5,40,20],[-50,0,20],[5,-40]])
tx=a_(a).mean(0)
a=translate_2d(-tx,a)
b=translate([0,0,-20],sphere(50))
p1=[[0,0],[15,50]]
s1=prism(a,p1)
l1=translate_2d([-25,3],sinewave(50,1.5,3,50))
l1=mirror_line(l1,[0,1,0],[0,0,0])
l2=translate_2d([0,-20],circle(50))
l3=rot2d(30,[[0,0],[-10,0]])
l3=rot('x90z-90',flip(line2length( flip(line2length( cir_line_tangent(l2,l3),50)),100)))
s2=sweep_sec2path(l1,l3)
b=psos(s2,b,[0,0,-1]@xrot(-30),1e7,1,3)
b=[bspline_closed(p,3,50) for p in b]
l1=equidistant_pathc( contiguous_chains( two_solids_intersection(b,s1))[0],100)
l2=o_3d(l1,b,7,outside=0)
l3=o_3d(l1,s1,-3,outside=0)
f3=convert_3lines2fillet(l3,l2,l1,closed_loop=1)
f3=solid_from_fillet_closed(f3,-3)
show(
    # *[color(p_line3d(p,0.2),'blue') for p in [l1,l2,l3]],
color(difference(intersection(swp(s1),swp(b)),swp_c(f3)),alpha=1),
# swp_surf(s2)
)
