# mesh_erode() on an externally imported STL -- shrinkage/solidification
# analysis on a real part (not just a primitive), the workflow this
# function was actually built for: export a shape from another CAD tool
# (or from SanPyCAD-Brep) as a genuine STL, import it here, then erode it
# to see which region is farthest from every outer surface (a rough
# geometric proxy for the last part of a casting to solidify/cool, i.e.
# the highest shrinkage-porosity risk).
#
# import_mesh(path) returns a Mesh whose .V (vertices) and .F (face
# indices) are exactly the (vertices, faces) numpy arrays mesh_erode()'s
# `f=` argument expects -- no manual triangulation needed, that's already
# done by whatever exported the STL.
#
# IMPORTANT: the file at `path` has to be a REAL STL (binary or ASCII),
# not some other format renamed with a .stl extension -- e.g. copying a
# .step file and just renaming it to .stl will load without a file-not-
# found error but fail with "import(): file contains no usable geometry",
# since the STEP text inside doesn't parse as STL triangles. Use a real
# export_stl(shape, path) call (SanPyCAD-Brep has this) to produce one.
#
# A bare filename here is looked up in the imports/ folder next to this
# app; the full path below is used as-is and will need updating to
# wherever your own exported STL actually lives.

m = import_mesh("/Users/sanjeevprabhakar/SanPyCAD/wall_hook.stl")
eroded = mesh_erode(m.V, 2, grid=[40, 40, 40], f=m.F)
show(eroded)
