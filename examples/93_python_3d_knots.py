# 3D knots (trefoil)
# Real project from the ocad examples notebook.
# The knot is just a parametric path (a plain Python list comprehension
# over the trefoil formula) swept with a circular section via
# path_extrude_closed() + align_sol_1() (which keeps the section from
# twisting as it follows a closed, curving path). Alternative knot formulas
# (torus knots, cinquefoil, Lissajous, etc) are left as comments below to
# try - swap the active `path=` line to explore them.

# trefoil knot
path=[[10*(sin(t)+2*sin(2*t)),
      10*(cos(t)-2*cos(2*t)),
      -10*sin(3*t)] for t in d2r(arange(0,360))]

# circular sin theta knot
# path=[[60*(cos(t)),
#       60*(sin(t)),
#       20*sin(4*t)*cos(4*t)] for t in d2r(arange(0,360))]

# random knot
# path=[[20*(-0.22*cos(t) - 1.28*sin(t) - 0.44*cos(3*t) - 0.78*sin(3*t)),
# 20*(-0.1*cos(2*t) - 0.27*sin(2*t) + 0.38*cos(4*t) + 0.46*sin(4*t)),
# 20*(0.7*cos(3*t) - 0.4*sin(3*t))] for t in d2r(arange(0,360))]

# torus knots
# path=[[10*cos(3*t)*(3+cos(4*t)),
# 10*sin(3*t)*(3+cos(4*t)),
# 10*sin(4*t)] for t in d2r(arange(0,360))]

# cinquefoil torus knots
# a,p,q=3,11,12
# d=10
# radius of the torus = a*d ; section radius of the torus = d
# p is the number of cycles of the wrapping coil over the torus
# q is the number of turns of the wrapping coil over the torus
# path=[[d*cos(p*t)*(a+cos(q*t)),
# d*sin(p*t)*(a+cos(q*t)),
# -d*sin(q*t)] for t in d2r(arange(0,360,.25))]

# Lissajous knots
# path=[[10*cos(3*t+5),
# 10*cos(3*t+10),
# 10*cos(3*t+2)]for t in d2r(arange(0,360))]

r=4
sec=circle(r)
sol=align_sol_1(path_extrude_closed(sec,path))

sol1=o_solid([0,0,1],pts([[-50,-50],[100,0],[0,100],[-100,0]]),2,-15)
show(swp_c(sol), swp(sol1))
