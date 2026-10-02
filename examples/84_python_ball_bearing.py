# Ball bearing
# Real project from the ocad examples notebook.
# A short one: two corner_radius() profiles are combined and cut with
# rotate_extrude() (native OpenSCAD text through fo()) to form the inner
# and outer races, then a ring of sphere() balls is placed with a for loop.

sec=corner_radius(pts1([[31,.5,0],[.5,-.5,0],[9.5,0,1],[0,15,1],[-9.5,0,0],[-.5,-.5,0]]),10)
sec1=corner_radius(pts1([[16,.5,0],[.5,-.5],[9,0,0],[0.5,.5,0],[0,14,0],[-.5,.5,0],[-9,0,0],[-.5,-.5,0]]),10)
sec2=circle(7,[28.5,7.5])

# rotate_extrude() has no Python-mode equivalent anywhere in this codebase
# (confirmed via grep), so the races (inner/outer ring) stay on this
# residual fo() call. The ball ring itself is fully converted to show()
# below since sphere()/rot()/translate() cover it directly.
balls=[sphere(6.8,cp=rot(f'z{i}',[[28.5,0,7.5]])[0],s=100) for i in range(0,360,30)]
show(*[swp(b) for b in balls])
fo(f'''
rotate_extrude($fn=200)
difference(){{
union(){{
polygon({sec});
polygon({sec1});
}}
polygon({sec2});
}}
''')
