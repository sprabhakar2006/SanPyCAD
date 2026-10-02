# Parametric sculptural artifact
# Real project from the ocad examples notebook.
# A generative surface: 200 height "stages" are each given their own radius
# modulation (via sin()-based helper functions f()/a() and a signed-power
# pauw() function) so the outline breathes in and out with height, then
# f_offset() creates matching inner-wall points and convert_3lines2fillet()
# closes the base. Warning: this recomputes every stage in Python, so it
# can take a couple of minutes to evaluate.

stages =200
stage_height = 1.25
rad = 50
f1 = 25
f2 = 25
phase1 = 0
phase2 = 180
height_depth=5
depth1 = 20
depth2 = 20
myslices = 5
angle_step=.5
var=1

def pauw(x,p):
    return sign(x)*abs(x)**p

def f(i,stages):
    return sin(d2r(i/stages * 120))**2 * 7 + 1

def a(i,stages,var,height_depth):
    return (sin(d2r((i/stages*360*f(i,stages))%360)) * 0.5 + 0.5) * (var * height_depth)


# generate outer points
points_base=[[
    [
        sin(d2r(j)) * (rad+a(i,stages,var,height_depth)+(pauw(sin(d2r(j *f1+phase1)),0.5)*0.5+0.5)*depth1*i/stages+(pauw(sin(d2r(j *f2+phase2)),0.5)*0.5+0.5)*depth2*(1-i/stages)),
        cos(d2r(j)) * (rad+a(i,stages,var,height_depth)+(pauw(sin(d2r(j *f1+phase1)),0.5)*0.5+0.5)*depth1*i/stages+(pauw(sin(d2r(j *f2+phase2)),0.5)*0.5+0.5)*depth2*(1-i/stages)),
        i*stage_height
    ]
    for j in arange(0,360,angle_step)] for i in range(stages+1)]

thickness = 2
p1,p2=[],[]
for i in range(stages):
    points_base1= flip(c3t2(points_base[i]))
    points_base2=f_offset(points_base1,-thickness)
    p1.append(translate([0,0,i*stage_height],points_base1))
    p2.append(translate([0,0,i*stage_height],points_base2))


p2=flip(p2)
l1,l2=p2[-5],p2[-3]
l3=translate([0,0,2.5],f_offset(c3t2(p1[2]),-7))
f1=cpo(convert_3lines2fillet(l1,l3,l2))[:-1]
sol=p1+p2[:-6]+f1
show(swp(sol))
