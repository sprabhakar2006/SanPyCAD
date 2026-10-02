# Drill bit
# Real project from the ocad examples notebook.
# Combines a prism()-based fluted body with two helix() paths swept with
# p_line3d() (as flute grooves) inside a difference(), and uses render()
# to force full CSG evaluation of the cut.

sec=circle(7.5,s=100)
path=pts([[-7.49*cos(360/200*pi/180),0],[7.5,5],[0,70]])
sol=prism(sec,path)
hx1=helix(7.5,20,2,5)
hx2=rot('z180',hx1)
show(difference(
color(swp(sol),"orange"),
color(p_line3d(hx1,4.5,s=70),"cyan"),
color(p_line3d(hx2,4.5,s=70),"cyan"),
))
