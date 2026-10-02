# Honeycomb pattern with point-in-polygon filtering
# Real project from the ocad examples notebook.
# Short but instructive: honeycomb() generates a hex-grid point set, and
# pies1() (point-in-enclosed-section test) filters that grid down to only
# the points fully inside an arbitrary boundary profile.

sec4=honeycomb(1,6,15)
sec=corner_radius(pts1([[3,2,1],[8,3,3],[5,7,1],[-8,0,2],[-5,20,1]]),30)
pnts1=[p for p in sec4 if len(pies1(sec,p))==6]
show(
*[p_line3d(p,.1,closed=1) for p in sec4],
color(p_line3d(sec,.1,closed=1),"blue"),
*[color(p_line3d(p,.1,closed=1),"cyan") for p in pnts1],
)
