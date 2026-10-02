# The actual top-visible SURFACE (not just its outline) of the mouse
# body from example 102/103, looking from [0,0,1].
#
# ocad already has a purpose-built tool for this: surface_split(
# sol, v1) -- for each triangle it casts a ray from that triangle's own
# center along v1 and keeps the triangle only if that ray hits no OTHER
# triangle first, i.e. true occlusion-aware "visible from this
# direction", not just a normal-facing filter. Its own docstring:
# "if you are looking at the object from the top use vector [0,0,1],
# if from right [1,0,0], from left [-1,0,0], from front [0,1,0],
# from back [0,-1,0]..." -- so the same call works for any of the 6
# (or any arbitrary) viewing directions, not just top.
#
# surface_split() wants its input as a plain (n_tri, 3, 3) array -- one
# [p0,p1,p2] per triangle -- not a Mesh. sol.V[sol.F] (numpy fancy
# indexing) builds exactly that from the real Mesh difference()/
# union()/intersection() already gave us. The result comes back in
# that same per-triangle-points format, which is exactly what
# swp_triangles() turns into a real polyhedron() shape for show().
#
# Note: this is an O(n_triangles^2) ray-test (every triangle checked
# against every other), so it can take a few seconds on a dense mesh --
# lower CSG detail first if it's too slow.

# (reuses `sol` from 103_outer_boundary_from_top.py -- run that
# construction first, or paste it above this.)

tri = sol.V[sol.F]                          # (n_tri, 3, 3)
tri_top = surface_split(tri, [0, 0, 1])      # only triangles visible from straight above

show(
    color(sol, alpha=0.2),
    color(swp_triangles(tri_top), 'lime'),
)
