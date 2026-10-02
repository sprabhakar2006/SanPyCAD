# Cable gripper / cable manager clip
# Real project from the ocad examples notebook.
# A compact, elegant example: surround() builds a 2D "race track" outline
# around a line segment, h_lines_sec() slices it into horizontal strips,
# and wrap_around() bends those strips around a cylindrical path - turning
# a flat 2D shape into a curved clip in just a few lines.

r=10/2 # radius of the gripper
t=1.25 # thickness of the gripper
l1=2*pi*r-2*r # unwrapped length - 2 * height of the gripper (in this case the diameter is height)
l2=[[0,r+.1],[0,l1+r]]
sec=surround(l2,r)
s1=h_lines_sec(sec,500,.01)
p1=rot('y90',circle(r+.05,s=200))
s2=[wrap_around(p,p1) for p in s1]
s3=surface_offset(s2,t)
sol=rot('y-90',solid_from_2surfaces(s2,s3))
show(swp(sol))
