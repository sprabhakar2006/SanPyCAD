# The Python-mode equivalent of writing:
#   a = cube([20,20,10], center=True)
#   b = cylinder(r=6, h=20, center=True)
#
# union()/difference()/intersection()/hull() are ordinary functions here,
# and show() is what actually puts something in the 3D view.

a = cube([20, 20, 10], center=True)
b = cylinder(r=6, h=20, center=True)
show(difference(a, b))
