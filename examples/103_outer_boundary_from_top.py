# Outer boundary ("silhouette") of the mouse body from example 102,
# viewed from directly above (direction [0,0,1]).
#
# Once a shape is built via union()/difference()/intersection()/hull()
# (Python mode's live boolean ops), the result "sol" is a real Mesh --
# sol.V is an Nx3 numpy array of its actual (real-OpenSCAD-tessellated)
# vertex coordinates, sol.F its triangle indices. That's what unlocks
# this: looking from [0,0,1] just means dropping Z, and finding the
# outer edge of that flattened point cloud is exactly what
# concave_hull() already does (same tool examples 46/47 use on small
# hand-built 2D point sets -- here it's fed the flattened mesh
# vertices of a real solid instead).
#
# mesh_vf()/boundary_edges_sol() etc. don't apply here -- those need a
# structured [row][col] point grid (raw prism()/swp() input), and
# `sol` below is a post-boolean triangle soup, not a grid.

a = cr2dt([[-20, 0, 15], [40, 0, 15], [0, 40], [5, 40, 20], [-50, 0, 20], [5, -40]])
tx = a_(a).mean(0)
a = translate_2d(-tx, a)
b = translate([0, 0, -20], sphere(50))
p1 = [[0, 0], [15, 50]]
s1 = prism(a, p1)
l1 = translate_2d([-25, 3], sinewave(50, 1.5, 3, 50))
l1 = mirror_line(l1, [0, 1, 0], [0, 0, 0])
l2 = translate_2d([0, -20], circle(50))
l3 = rot2d(30, [[0, 0], [-10, 0]])
l3 = rot('x90z-90', flip(line2length(flip(line2length(
    cir_line_tangent(l2, l3), 50)), 100)))
s2 = sweep_sec2path(l1, l3)
b = psos(s2, b, [0, 0, -1] @ xrot(-30), 1e7, 1, 3)
b = [bspline_closed(p, 3, 50) for p in b]
l1 = equidistant_pathc(contiguous_chains(two_solids_intersection(b, s1))[0], 100)
l2 = o_3d(l1, b, 7, outside=0)
l3 = o_3d(l1, s1, -3, outside=0)
f3 = convert_3lines2fillet(l3, l2, l1, closed_loop=1)
f3 = solid_from_fillet_closed(f3, -3)

sol = difference(intersection(swp(s1), swp(b)), swp_c(f3))

# Project along [0,0,1] = drop Z. Round + dedupe first -- otherwise
# every vertical-wall vertex stack contributes a near-duplicate point
# at the same (x,y), which just slows the boundary walk down for no
# benefit.
pts2d = np.round(sol.V[:, :2], 2)
pts2d = np.unique(pts2d, axis=0).tolist()

# n = starting neighbourhood size for the boundary walk, engaging_angle
# caps how sharp a turn it'll take -- raised from the defaults (3/270)
# because this point cloud is a dense mesh surface, not a handful of
# hand-placed points; if the walk still snags on a concave detail,
# raise n further (e.g. 12-15).
outline = concave_hull(pts2d, n=8, engaging_angle=250)

# Lift the outline back to 3d, sitting just above the shape's own top,
# purely so it's visible against the solid in the viewer.
z_top = float(sol.V[:, 2].max())
outline3d = [[p[0], p[1], z_top + 0.5] for p in outline]

show(
    color(sol, alpha=0.35),
    color(p_line3d(outline3d, 1, closed=1), 'red'),
)
