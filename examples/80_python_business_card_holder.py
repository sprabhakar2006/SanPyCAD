# Business card holder
# Real project from the ocad examples notebook.
# A compact example: a rounded-rectangle tray wall built by extruding the
# difference of an outer and inner offset() profile, plus a slanted back
# support prism(), combined with render() to force full CSG evaluation.

sec=corner_radius(pts1([[0,0,1],[95,0,1],[0,10,1],[-95,0,1]]),10)

sol2=linear_extrude(offset(sec,1),1)

sec1=corner_radius(pts1([[10,0,5],[50,0,5],[10,30],[-70,0]]),10)

sol3=translate([12.5,2,21],rot("x90",linear_extrude(sec1,5)))

# linear_extrude(50) difference(){polygon(offset(sec,1));polygon(sec);} builds
# a hollow wall -- the Python equivalent is swp_prism_h() to hollow an outer
# extruded prism with an inner one, rendered via swp_c().
wall_sol=swp_prism_h(linear_extrude(offset(sec,1),50),linear_extrude(sec,50))
# OpenSCAD's difference() subtracts EVERY child after the first from the
# first, not just the immediately-nested one -- so sol2 (last child of the
# outer difference()) is also subtracted, not unioned back in.
show(difference(swp_c(wall_sol), swp(sol3), swp(sol2)))
