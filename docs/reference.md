# SanPyCAD reference

Everything the app can do, in detail: the window and its controls, both
scripting modes, the OpenSCAD-style language, how booleans are computed,
and the current limitations.

New here? Start with the [README](../README.md) instead -- it covers
installing and the first five minutes.

## The app window

Either way, a window titled "SanPyCAD" opens: a code editor on the left,
a live 3D viewport on the right. Write a script, press **Render** (or
Ctrl/Cmd+Enter), and it draws the model. The **Export** dropdown (next to
the OpenSCAD-style/Python toggle) saves the current scene as STEP, STL, OBJ,
SVG (a 2D isometric wireframe projection of the model's edges), or DXF
(labeled honestly rather than as "DWG" -- true .dwg is AutoCAD's
proprietary binary format and needs a paid SDK to write; DXF is the open
interchange format AutoCAD and every other major CAD tool reads
natively, so it covers the same "get this into AutoCAD" goal). The
**Import** button loads an external STL/OBJ/OFF mesh file, or an SVG 2D
shape, and inserts a working `import(...)` snippet (or, in Python mode,
`import_mesh(...)`/`import_profile(...)`) at the cursor -- the same idea
as OpenSCAD's own `import()`, just with a file picker instead of typing
the path by hand. SVG is a 2D format, same as `circle()`/`square()`/
`polygon()`, so it only actually produces something inside
`linear_extrude()`/`rotate_extrude()` -- the inserted snippet already
wraps it that way. Files can also be referred to by filename alone if
dropped into the `imports/` folder next to `app.py` (created
automatically the first time it's needed).

**STEP export is different from the other formats.** STL/OBJ/SVG/DXF all
write out the *rendered triangles*. STEP writes a real CAD solid, and how
good it is depends on what the shape still remembers about itself.

A **raw sol** -- whatever `cube()`/`sphere()`/`linear_extrude()`/a swept
prism handed back -- still has its cross-sections, and an m x n stack of
sections is exactly the control net a B-spline surface wants. Those go out
as an **exact B-rep**: real B-spline faces, sharp edges wherever the
section actually creases, flat `PLANE` caps on flat ends, and a handful of
faces instead of thousands of triangles. A swept square becomes 6 faces, a
cylinder 4. That is a file another CAD package can fillet, cut and edit.

Anything that has been through `union()`/`difference()`/`intersection()`/
`hull()` comes back from OpenSCAD as an STL, so its sections are gone for
good and no exporter can recover them -- same for `import_mesh()` and
`mesh_erode()` results. Those are written **faceted** instead: planar
faces, with coplanar triangles merged back into single polygonal faces (a
boolean of prismatic parts collapses to a handful of faces; an organic or
marching-cubes surface has nothing to merge and stays large).

A raw sol is also written faceted when its own cross-sections are too
unlike one another for a single shared parameterisation -- a B-spline
surface has one knot vector per direction, so every section has to agree
on where each point sits along the profile. When they disagree badly (one
section collapsing a span that another stretches over 20 mm, say), fitting
anyway yields a smooth surface that wanders off the shape, so the exporter
measures that disagreement up front and falls back rather than shipping a
distorted solid. The console names the reason.

The console says which path each body took. Because of this, exporting the
raw shapes and doing the booleans in the receiving CAD usually gives a far
more useful result than exporting the finished boolean -- separate
editable bodies rather than one lump:

```
export_step([("boss", s1), ("tool", s2)], "parts.step")
```

Several bodies are written as one file each inside a folder named after the
path -- `parts/boss.step` and `parts/tool.step` above -- so any one of them
can be picked up on its own. `one_file=True` writes a single multi-body STEP
instead, keeping them positioned relative to each other as an assembly. A
single shape is always just one file. The Export menu, being a download,
always produces one file.

`export_step()` is built in -- no import line needed, same as `show()`.
Resolution matters in the opposite direction to meshes: a cubic B-spline
through a `$fn=16` circle is roughly 400x more accurate than the 16-gon
mesh, so for exact export `$fn=16..24` is the sweet spot; cranking it to
128 only inflates the file, since interpolation needs one control point
per input point.

Note that Export/Import are about the *rendered geometry* (STL/OBJ/etc.),
not the script that produced it. To save your actual design so you can
close SanPyCAD and reopen it later, use **Save** (writes to whatever file
you last saved to/opened from -- a native Save dialog the very first
time), **Save As** (always prompts for a new file), or **Open** (loads a
previously saved script back into the editor, switching between
OpenSCAD-style and Python mode automatically based on whether it's a
`.scad` or `.py` file). Ctrl/Cmd+S is the same as clicking Save. This
writes plain `.py`/`.scad` text files -- ordinary source code, openable
in any text editor, not a proprietary format.

The **Examples** dropdown in the toolbar has a few starter scripts. The
toolbar also has a toggle between the two ways to write a
script (see below) — switching keeps whatever you'd written in each one
separately, so you can flip back and forth. The **Orthographic** checkbox
switches the 3D viewport between perspective and orthographic (no
vanishing-point distortion) projection, keeping your current view.
Rotate/zoom/pan stop exactly where you release them -- no drift/momentum
to fight when lining up a precise view, and pan/zoom speed is tuned to
match OpenSCAD's own feel. The **Axes** checkbox toggles OpenSCAD's own
two-part axis display: a small colored X/Y/Z cross through the origin,
and a separate small x/y/z indicator fixed in the viewport's lower-left
corner that tracks the camera's current orientation. There's no
reference ground grid or numbered ruler ticks, matching OpenSCAD's own
Show Axes (it doesn't draw those either). The **Edges** checkbox
outlines every triangle edge in the model, the same as OpenSCAD's View >
Show Edges, handy for seeing the
underlying mesh structure. The **View** dropdown snaps the camera to a
standard angle -- Top, Bottom, Front, Back, Left, Right, or Diagonal --
the same set OpenSCAD's own View menu offers, keeping your current
zoom/pan instead of also re-fitting the model. **Fit** re-centers and
zooms the camera to frame the current model -- since the render pipeline
otherwise never touches your camera position after the very first render
(scrolling, panning, and orbiting are always exactly where you left
them, on purpose), this is how you get back if you've scrolled/panned
the model out of view entirely -- the same idea as OpenSCAD's View >
Reset View. The editor pane and the
3D viewport are resizable -- drag the thin bar between them (and the one
between the editor and the console panel) to adjust how much space each
gets. The **Measure** dropdown (Off/Vertices/Edges) lets you click on the
model to measure it, the same idea as OpenSCAD's own Measure tool:
in **Vertices** mode, clicking snaps to the nearest corner of whatever
face you click (marked with a small dot), and once two are picked shows
the distance between them (plus its x/y/z components); in **Edges**
mode, clicking selects a whole edge (highlighted; this temporarily turns
the Edges overlay on if it was off, so there's something to click),
and once two are picked shows each edge's length, the angle between
them (always the acute 0-90 deg angle, regardless of which way each
edge happens to be wound internally), and the shortest distance between
them (handles two edges that don't actually touch). A click is only
treated as a pick if the pointer barely moved between press and release
-- drag as usual to orbit, click to measure. **Clear** resets the
current selection, and picking a third point/edge automatically starts
a new selection. In Python mode, if a picked vertex can be traced back
to a specific point of a script variable, the panel also shows exactly
which one -- e.g. `sol1[0][10]` for the 11th point of the 1st cross-
section of `sol1` -- so you know exactly how to reference that point
back in your script. This works for both ways of showing a shape:
`show()`ing (or `color()`ing) a raw shape directly (not a `union()`/
etc result, which has no such 1:1 correspondence), and the
`fo(f'''{swp(sol1)}...''')` workflow -- `swp()`/`swp_c()`/`swp_surf()`/
`swp_triangles()` are watched for calls on a named variable, and their
points are matched (with a small tolerance, since going through real
OpenSCAD's STL export loses exact bit-for-bit precision) against
whatever vertices come back. In the
editor, brackets/quotes auto-close as you type, and (same as JupyterLab)
**Tab** brings up autocomplete when you're mid-identifier (every
`ocad.py` function name in Python mode, or the language's keywords in
OpenSCAD-style mode, plus whatever identifiers you've already typed in the
current script) and otherwise just indents/inserts a tab as normal. It
matches anywhere in the name, not just the start -- typing `extr` finds
`linear_extrude`/`rotate_extrude`/`path_extrude_open`/etc, not just names
that begin with those letters (matches that do start with what you typed
are still listed first). **Shift+Tab** on a function name shows its
signature and docstring in a popup, also JupyterLab style (works for
every `ocad` function and this app's own `union()`/`show()`/etc
in Python mode; OpenSCAD-style mode gets a short built-in reference for
its primitives/keywords since those aren't real Python functions with
docstrings to pull from). The toolbar's **📖 Reference** button opens a
searchable browser over that same documentation — every one of
the library's 600+ functions plus the DSL's built-in primitives/
keywords, all in one alphabetical list — so you can look something up
by name or just search for a word in its description (e.g. searching
"offset" turns up every offset-related function at once) without
already having it typed in the editor the way Shift+Tab needs. (This
list deliberately excludes the ~500 numpy/scipy names that are only
technically visible because `ocad.py` opens with `from numpy
import *` — those aren't functions the library actually defines, and
including them would bury the real ones alphabetically.) The **Wrap** checkbox toggles line-wrapping in
the editor, for long lines (e.g. a big embedded points list) without
scrolling sideways to read them.

## Two ways to write a script

**OpenSCAD-style** — a small text language modeled on OpenSCAD's own
syntax (`cube([10,10,10]); difference() { ... }`), described in full
below. Good if you think in OpenSCAD terms already, or want something
closer to a `.scad` file.

**Python** — plain Python that calls the `ocad` library functions
directly, the same way you would in a notebook:

```python
a = cube([20, 20, 10], center=True)
b = cylinder(r=6, h=20, center=True)
show(difference(a, b))
```

Instead of `fo(f''' ... ''')` writing a `.scad` file for real OpenSCAD to
render, call **`show(x)`** on whatever shape(s) you want drawn in the app
(if a script has exactly one shape-like variable and never calls
`show()`, that one gets shown automatically — anything more ambiguous
than that, you need to call `show()` explicitly). `union()`,
`difference()`, `intersection()`, and `hull()` are ordinary functions here
— they take one or more shapes (a raw value straight out of
`cube()`/`sphere()`/`cylinder()`/etc, or the result of another
`union()`/`difference()`/etc call) and run them through the same CSG
engine as the OpenSCAD-style mode. `color(x, "red", alpha=0.5)` tags a
shape with a color. `print()` and `echo()` both show up in the console
panel. Everything else — `translate()`, `rot()`, `scl3d()`, loops,
variables, helper functions you define — is just normal Python calling
the library, no new syntax to learn.

One name is intentionally shadowed: `ocad.py` already has its own
`union()` (2D pattern generation, unrelated to CSG); inside a Python-mode
script the bare name `union` refers to the CSG version instead, since
that's what you want when composing shapes here. The original is still
reachable as `ocad.union(...)`.

`import_mesh("file.stl")` loads an external STL/OBJ/OFF file as a shape
usable with `union()`/`color()`/`show()`/etc -- Python mode's equivalent
of OpenSCAD's `import()` (named `import_mesh` instead, since `import` is
a reserved word in Python). `import_profile("file.svg")` is the 2D
counterpart -- returns a plain `[[x,y], ...]` point list, the same thing
`circle()`/`square()` return, so it plugs straight into
`linear_extrude()`/`rotate_extrude()`, but only gives you the single
largest shape in the file. `import_profiles("file.svg")` (plural) returns
a list of *every* separate closed shape instead, for multi-part artwork:

```python
profiles = import_profiles("flower.svg")
show(union(*[linear_extrude(p, h=5) for p in profiles]))
```

In Python mode, any bare expression on its own line gets its value
echoed to the console panel, the same way a Jupyter cell auto-displays
whatever you type — so `len(a)`, `a.shape`, `type(a)`, or any other
one-off check can just be typed on its own line without wrapping it in
`print()`/`echo()`:

```python
a = cube([20, 20, 10], center=True)
len(a)          # -> shows up in the console panel
show(a)
```

(`None` and shape values — the result of `cube()`/`show()`/`color()`/
`union()`/etc — are quietly skipped so this doesn't spam the console with
`show(x)` calls you already have in your scripts; it's meant for
inspecting plain values.)

**`union()`/`difference()`/`intersection()`/`hull()`/`show()`/`color()` also accept `swp()`/`swp_c()`/`swp_surf()`/`swp_triangles()` text directly**, not just a raw sol:

```python
a = cube([20, 20, 10], center=True)
b = cylinder(r=6, h=20, center=True)
show(difference(swp(a), swp(b)))
```

This matters because the library has four different ways to turn a shape into a polyhedron, each with different face connectivity for a reason (`swp()` caps both ends, `swp_c()` leaves them open for a closed loop, `swp_surf()` is an open triangulated surface, `swp_triangles()` is an explicit triangle list) — passing a plain sol into `union()`/`show()` always used `swp()`'s capped logic regardless of which the shape actually needed, which for anything that should've used `swp_c()`/`swp_surf()`/`swp_triangles()` instead could silently produce a non-manifold mesh (real OpenSCAD then rejects it during a boolean, even though the same mesh displays fine on its own). Passing the actual `swp*()` string tells the app exactly which connectivity you intended, and that exact text is handed to real OpenSCAD verbatim for any boolean op it's used in — no re-triangulation, no guessing. Plain sols still work as before (via `swp()`-equivalent auto-capping) for the common case where that's what you want.

**`fo()` also renders in the viewer.** If you write scripts the notebook way — `swp()` to turn a sol into `polyhedron()`
text, `fo(f'''...''')` to write it out as a `.scad` file for real OpenSCAD,
calling any of the helper modules real `fo()` always appends to the file
(`p_line()`, `p_line3d()`, `p_line3dc()`, `points()`, `swp()`, `swp_c()`,
`swp_surf()`, etc, as native OpenSCAD code) — that still works exactly as
before (the file is still written, and those helpers are available), but
`fo()`'s contents are *also* run through real OpenSCAD right now and the
result is dropped straight into this app's viewer, so you don't need to
add a separate `show()`/`union()` call in the app's own vocabulary just to
see it here too. If a script calls both `fo()` and `show()`, both show up
(as separate objects). If OpenSCAD isn't installed, `fo()` still writes
the file but says so in the console instead of silently doing nothing.

**Colors and `%`/`#` inside `fo()` text.** None of OpenSCAD's command-line
export formats (STL included) actually preserve `color()` — that's a real
OpenSCAD limitation, not something specific to this app. To work around
it, `fo()`'s top-level statements are each rendered as their own separate
OpenSCAD call — so `color("blue")`, `color("red", 0.3)` (alpha as a second
argument, or `alpha=`, or a 4-element `[r,g,b,a]` array — all of OpenSCAD's
own forms work), `%some_shape();` (rendered translucent, since real
OpenSCAD's CLI export would otherwise drop `%`-marked geometry entirely —
it's normally preview-only), and `#some_shape();` (rendered in a distinct
highlight color to make it easy to spot) all come through into the viewer.
`*` still disables/omits a statement entirely, same as real OpenSCAD. `%`/`#`
are also picked up nested inside a shared block, not just at the top level
— e.g. `difference(){ swp(a); #swp(b); }` still subtracts `b` normally
(a `#` doesn't change the geometry, same as real OpenSCAD) *and* draws
`b` again separately as a highlighted overlay so you can see what got
cut away, the same idea as OpenSCAD's own debug-highlight preview.

**Every `fo()` statement gets its own render call, even same-colored ones
— this is what keeps open/non-manifold surfaces (`swp_surf()`, most
commonly) from disappearing.** Real OpenSCAD's STL export always
implicitly unions every top-level object in whatever file it's given —
that's what F6/Render does (unlike F5/Preview, which just draws each
object's raw geometry with no CGAL involved at all, so open surfaces show
up fine there). That implicit union needs a valid CGAL Nef polyhedron,
and silently drops any non-manifold operand caught up in it, even though
the exact same object exports perfectly fine completely on its own. If
two unrelated statements merely happened to land in the same file
together (they used to, whenever they shared a color, purely to save a
subprocess call), one could vanish from the viewer for a reason that had
nothing to do with color — the same "there in Preview, gone in Render"
symptom real OpenSCAD itself would show for the same geometry. Rendering
every statement completely on its own avoids that: each one only goes
through real CSG evaluation for whatever boolean ops it itself explicitly
contains (a `difference(){...}` block, say — which legitimately still
needs it, same as real OpenSCAD's own F6), never because it happened to
share a file with something else.

This mode runs your script with a plain Python `exec()` — no sandboxing
beyond that, same trust level as running it in a notebook.

**Variables persist between runs, Jupyter-style.** Python mode keeps a
kernel-like namespace alive across Render clicks: whatever your script
assigns is still there the next time you press Render, even if you've
since commented out the line that computed it. This is meant for the
same workflow a notebook enables — compute something heavy once, then
comment that line out and keep iterating on everything downstream of it
without paying for the heavy part again:

```python
# heavy_result = some_very_slow_function(...)   # computed once, now commented out
show(translate([10, 0, 0], heavy_result))
```

The toolbar shows a **N vars in memory** indicator (hover it to see which
names), and a **Reset Memory** button next to it clears everything —
the Python-mode equivalent of restarting a Jupyter kernel. Use it
whenever old variables from a previous script might be shadowing
something in the one you're working on now; nothing does this
automatically (switching scripts, opening a different example, etc. all
leave existing memory alone), so it's a manual, explicit action. A
script that errors partway through still keeps whatever it assigned
before the error, same as a Jupyter cell would.

Examples for both modes are in `examples/` (`*.scad` and `*.py`), and the
Examples dropdown filters to whichever mode is currently selected.

`05_python_points.py` through `71_python_fillet_3d_cube_and_cone.py` are a
larger set of Python-mode examples covering the `fo(f'''...''')`/`swp()`-text
workflow specifically -- points, lines, polylines, surfaces, solids, planes,
extruding/sculpting along a path, rotation, translation, wrapping a section
or surface around a path, 2D/3D intersections, offsetting (2D sections, 3D
solids, surfaces, paths, and offsetting-while-staying-on-a-surface), b-spline/
bezier/interpolation curves, convex and concave hulls (2D and 3D), projecting
a line or surface onto another surface, and 2D/3D fillets (line-line,
circle-circle, line-circle, sphere-sphere, and several solid/solid and
solid/surface fillet strategies, including ones reconstructed via marching
cubes). These were adapted from a walkthrough notebook one function/technique
at a time -- each file is self-contained and safe to run on its own. A couple
need things beyond what ships with SanPyCAD: `48_python_concave_hull_3d.py`
needs `pip install alphashape` (says so in a comment at the top), and the
`_marching_cubes`-suffixed fillet examples are computationally heavy and may
take a while to render.

## What's implemented (OpenSCAD-style mode)

**Primitives** — `cube`, `sphere`, `cylinder`, `polyhedron`, and 2D
`circle` / `square` / `polygon` (usable inside extrudes).

**Transforms** — `translate`, `rotate` (both `rotate([x,y,z])` and
`rotate(a, v=axis)`), `scale`, `mirror`, `color` (named colors or
`[r,g,b]` / `[r,g,b,a]`), `resize`.

**Boolean CSG** — `union`, `difference`, `intersection`, `hull`.

**Extrusion** — `linear_extrude` (height, twist, center, `$fn`),
`rotate_extrude` (angle, `$fn`).

**Import** — `import("file.stl")` (also `.obj`, `.off`) loads an external
mesh as a shape usable with `translate()`/`color()`/`union()`/etc, same
as OpenSCAD's own `import()`. `import("file.svg")` loads a 2D shape
instead (`<path>`/`<rect>`/`<circle>`/`<ellipse>`/`<polygon>`, with
`<g transform=...>` applied; content inside `<defs>`/`<clipPath>`/
`<mask>`/`<symbol>` or marked `display:none`/`visibility:hidden` is
skipped, since that's never directly-rendered artwork -- e.g. the
canvas-sized crop rect many icon SVGs put in a `<clipPath>`), usable the
same way `circle()`/`square()`/`polygon()` are -- only inside
`linear_extrude()`/`rotate_extrude()`. If the SVG has more than one
separate closed shape (a flower icon's individual petals, say), every one
of them gets extruded and the results are automatically unioned into a
single solid, rather than only the largest shape being used. See
`backend/mesh_import.py`.

**Language** — variables, arithmetic/comparison/boolean expressions,
vectors, ranges (`[a:b]`, `[a:step:b]`), `for`, `if`/`else`, `let`,
`module` definitions (with `children()`), `function` definitions,
`echo()`, `$fn`/`$fa`-style special variables, comments, and the
`# % ! *` modifier characters in front of a shape (highlight / background
/ show-only / disable — `!` currently just renders normally rather than
hiding the rest of the scene).

**Every primitive and extrusion is generated by calling straight into your
`ocad.py`** (`cube`, `sphere`, `cylinder`, `circle`, `square`,
`linear_extrude`, `translate`, and `triangulate_solid_open` — which itself
uses `earclip_3d` for capping — are all called directly). Only
`rotate_extrude` has no equivalent in the library, so that one revolve
routine is written directly with numpy.

## How CSG booleans work

This app checks for a real OpenSCAD install at startup (look for the
**"Exact CSG (OpenSCAD)" / "Approximate CSG (voxel)"** badge in the
toolbar, or the message printed to the terminal when `app.py` starts) and
uses it automatically when present:

**With OpenSCAD installed (exact)** — this is your existing swp()/fo()
workflow, automated: each operand mesh is written out as its own
`polyhedron(points=..., faces=..., convexity=10)` (in Python mode, using
the *exact* text `swp()`/`swp_c()`/`swp_surf()`/`swp_triangles()` returned
if you passed that in directly, rather than re-deriving it), wrapped in
`union(){}` / `difference(){}` / `intersection(){}` / `hull(){}`, and
rendered headless with `openscad --backend=Manifold -o out.stl in.scad` --
Manifold is OpenSCAD's newer boolean engine, explicitly selected rather
than left to whatever backend your local OpenSCAD preferences happen to
have set, since it's both faster and considerably more robust than the
older CGAL engine (which has known internal-assertion crashes on
otherwise-valid geometry, e.g. two operands that touch along an exactly
coincident seam). If your OpenSCAD build predates the `--backend` flag,
this app retries once without it automatically. The STL result is read
back in as the final mesh. Sharp, exact, no voxel artifacts — this is
what you get by default once OpenSCAD is on your machine; nothing else to
configure. It's looked for on `PATH` and in the usual per-OS install
locations (e.g. `/Applications/OpenSCAD.app/...` on macOS; on Windows,
both `Program Files`/`Program Files (x86)` -- the "install for all
users" default -- and `%LocalAppData%\Programs` -- the "install for me
only" option some installers offer instead, which doesn't need admin
rights -- are checked, including an `OpenSCAD (Nightly)` folder name for
nightly builds).

**If it's installed but still shows as "Approximate CSG (voxel)"**
(most often on Windows, if it was installed to a custom folder, or as a
portable/zip build extracted somewhere of your own choosing): hover the
badge -- its tooltip lists every location that was actually checked. Set
the `SANPYCAD_OPENSCAD_PATH` environment variable to the exact full path
of `openscad.exe` (or the `OpenSCAD`/`openscad` binary on other
platforms) and restart SanPyCAD; that path is always checked first,
ahead of every built-in guess. On Windows, setting it for your account
(**System Properties > Environment Variables > New...** under "User
variables", or `setx SANPYCAD_OPENSCAD_PATH "C:\path\to\openscad.exe"` in
a Command Prompt, then restart SanPyCAD) is the simplest way to do this.

**Without OpenSCAD (fallback)** — a **voxel sample + marching-cubes**
approximation, so the app still works fully standalone if you don't have
OpenSCAD:

1. sample a 3D grid over the operands' bounding box
2. classify each grid point inside/outside each mesh with a vectorized
   ray-parity test — the same technique `points_inside_solid()` uses,
   generalized here to work on any triangle mesh
3. combine the inside/outside grids per the operator
4. run `skimage.measure.marching_cubes` (already a dependency of the library) to extract the resulting surface, then a Taubin smoothing pass
   to soften the voxel "staircase" look

This fallback is **not perfectly sharp** and thin features can disappear
at low detail — if you ever see it in use, the **CSG detail** slider in
the toolbar (`csg_resolution`, up to 120) raises quality at the cost of
render time. If OpenSCAD is installed but a particular call to it fails
for some reason, the app falls back to this automatically too and says so
in the console panel (with the reason), rather than failing the whole
render.

Plain (non-boolean) shapes like a bare `cube()` or `cylinder()` never go
through either CSG pipeline — they come straight from `ocad.py` and
are always exact regardless of whether OpenSCAD is installed.

## Known limitations

- **2D booleans aren't supported.** `linear_extrude`/`rotate_extrude` take
  a single 2D outline (`circle`/`square`/`polygon`, optionally wrapped in
  `translate`/`rotate`/`scale`) — you can't `difference()` two 2D shapes
  before extruding. The robust workaround (and honestly the usual OpenSCAD
  pattern anyway) is to extrude a solid block and then subtract a 3D shape
  from it — see `examples/02_boolean_csg.scad`.
- Non-convex `polygon()` end caps use ear-clipping via `earclip_3d`,
  which should handle most simple polygons, but self-intersecting outlines
  aren't validated.
- Module/function scoping is simplified: a module body sees its own
  parameters plus top-level (global) variables, not full OpenSCAD-style
  dynamic scoping of caller locals. `children()` is supported for the
  common "wrapper module" pattern.
- `!` (show-only) parses but doesn't hide the rest of the scene yet.
- `import()` supports STL/OBJ/OFF (3D) and SVG (2D, single largest closed
  shape only -- no multi-part shapes with holes, no 3MF/AMF/DXF import). No
  `text()`, `surface()`, `minkowski()`, `render()`.

## Project layout

```
SanPyCAD.app/            <- double-click this to launch (macOS)
Fix Mac Security Warning.command  <- run once after unzipping, before first launch (macOS)
SanPyCAD.vbs              <- double-click this to launch (Windows)
run_sanpycad.bat          <- backup Windows launcher (visible console; use if .vbs is blocked)
app.py                    <- what the launchers above run; also runnable directly
backend/
  ocad.py            <- the library, unmodified
  scad_lang.py            <- tokenizer + parser for the OpenSCAD-style language
  scad_eval.py            <- walks the parsed script, calls ocad.py, applies transforms
  python_eval.py          <- runs Python-mode scripts (exec + union/difference/.../show helpers)
  geom_bridge.py          <- shared "sol -> watertight mesh" conversion, used by both modes
  csg.py                  <- boolean CSG + hull: tries openscad_cli.py first, voxel fallback
  openscad_cli.py         <- shells out to the real OpenSCAD app for exact CSG, if installed
  mesh_import.py          <- STL/OBJ/OFF readers for import()/import_mesh()
  step_export.py          <- STEP (AP214) writer: exact B-rep from sols, faceted fallback
  vendor_assets.py        <- downloads CodeMirror/Three.js into frontend/vendor/ once, for offline use
  server.py               <- stdlib HTTP server (routes: /, /status, /render, /export/stl, /examples)
frontend/
  index.html              <- code editor (CodeMirror) + 3D viewer (Three.js), single file
  vendor/                  <- local copies of CodeMirror/Three.js (downloaded on first run; see above)
examples/
  *.scad                  <- OpenSCAD-style examples
  *.py                    <- Python-mode examples
imports/                  <- drop STL/OBJ/OFF files here to import() by filename
                             (created automatically the first time it's needed)
```

If you'd rather run it as a plain local web page (e.g. to open it in a
regular browser tab yourself, or host it for someone else on your
network), you can skip `app.py` and run `python3 backend/server.py`
directly, then open the printed `http://127.0.0.1:8743/` URL.

