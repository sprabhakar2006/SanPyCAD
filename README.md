<div align="center">

# SanPyCAD

**Code-first 3D modeling in Python or OpenSCAD syntax — with the fillets, sweeps and offsets that plain OpenSCAD makes painful.**

[![Download](https://img.shields.io/github/v/release/sprabhakar2006/SanPyCAD?label=download&color=2ea44f)](https://github.com/sprabhakar2006/SanPyCAD/releases/latest)
![Platforms](https://img.shields.io/badge/platform-macOS%20(Apple%20Silicon)%20%7C%20Windows-0a7bbb)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Video tutorials](https://img.shields.io/badge/YouTube-video%20tutorials-red?logo=youtube&logoColor=white)](https://www.youtube.com/@sanjeevprabhakar3837/videos)

[Download](#download) · [First model](#your-first-model) · [Video tutorials](#video-tutorials) · [Features](#features) · [Reference](docs/reference.md) · [SanPyCAD Brep](https://github.com/sprabhakar2006/sanpycad-brep)

<a href="https://www.youtube.com/watch?v=u2RLu20Z9K4">
  <img src="https://i.ytimg.com/vi/u2RLu20Z9K4/maxresdefault.jpg" width="820" alt="SanPyCAD: Python script on the left, a bracket rendered live on the right">
</a>

<sub>Click the screenshot to watch this bracket go from 2D sketch to finished part.</sub>

</div>

---

SanPyCAD is a desktop app for building 3D models with code. Type a script on the left, press **Render**, and the solid appears on the right. Underneath is the **ocad** geometry library — 600+ functions for fillets, offsets, sweeps along a path, lofts between sections, B-spline and Bezier curves, hulls, projections and intersections — plus a 2D sketcher, measuring and dimensioning tools, and multi-view drawings.

It is a single download. Python, every library, the editor and the 3D viewer are all inside, and it runs fully offline.

## Download

| Platform | Download | Open it |
|---|---|---|
| macOS (Apple Silicon) | [**SanPyCAD-mac-arm64.zip**](https://github.com/sprabhakar2006/SanPyCAD/releases/latest/download/SanPyCAD-mac-arm64.zip) | unzip, double-click `SanPyCAD.app` |
| Windows 10/11 (x64) | [**SanPyCAD-win-x64.zip**](https://github.com/sprabhakar2006/SanPyCAD/releases/latest/download/SanPyCAD-win-x64.zip) | unzip, open the folder, double-click `SanPyCAD.exe` |

All builds are on the [releases page](https://github.com/sprabhakar2006/SanPyCAD/releases). There's also a [7-minute install walkthrough](https://www.youtube.com/watch?v=F-FGGaWq4m0) if you'd like to see it done once.

> **First launch.** The app isn't signed by Apple or Microsoft yet, so the first launch shows a warning.
> **macOS:** right-click `SanPyCAD.app` → **Open** → **Open** (once only).
> **Windows:** on the SmartScreen banner, click **More info** → **Run anyway**.

> **Intel Mac or Linux?** There's no prebuilt bundle yet; [run it from source](#run-from-source) instead.

Nothing else needs installing: the exact boolean engine (manifold3d) is bundled inside the app.

## Your first model

Open the app, make sure **Python** is selected in the toolbar, paste this in and press **Render** (or <kbd>Ctrl</kbd>/<kbd>Cmd</kbd>+<kbd>Enter</kbd>):

```python
a = cube([30, 30, 10], center=True)
b = cylinder(r=8, h=40, center=True)
show(difference(a, b))
```

Now something that would be a real project in plain OpenSCAD — a helix wrapped around a circle and turned into a smooth closed tube (from the [3D Knots](https://www.youtube.com/watch?v=PYGRlvD9uGs) video):

```python
s1 = rot('y90', helix(3, 3, 5, 2))
p1 = c23(arc(5, 0, 360, s=len(s1)))
knot = extrude_wave2path(s1, p1)
show(p_line3d(knot, 1, closed=1, s=50))
```

And a true 3D fillet between two spheres, in one call:

```python
s1 = sphere(10)
s2 = sphere(7, [15, 15, 0])
f1 = fillet_2spheres(s1, s2, 7, s1=10, s2=40)
show(swp(s1), swp(s2), swp(f1))
```

From here, the **Examples…** dropdown has 100+ ready-made scripts — primitives, sweeps, offsets, hulls, fillets, and complete parts such as bolts, a ball bearing, a lamp, a drill bit and phone stands. The **📖 Reference** button searches every library function by name or description.

## Video tutorials

Each video is a real modeling session recorded in the app. Full list on the [YouTube channel](https://www.youtube.com/@sanjeevprabhakar3837/videos).

<table>
<tr>
<td width="33%" align="center"><a href="https://www.youtube.com/watch?v=OGjPWL4bfWg"><img src="https://i.ytimg.com/vi/OGjPWL4bfWg/mqdefault.jpg" alt="SanPyCAD with the 2D sketcher"></a><br><b>Sketch a profile, sweep it in 3D</b><br><sub>2D sketcher · 13:30</sub></td>
<td width="33%" align="center"><a href="https://www.youtube.com/watch?v=u2RLu20Z9K4"><img src="https://i.ytimg.com/vi/u2RLu20Z9K4/mqdefault.jpg" alt="SanPyCAD example 1: bracket"></a><br><b>A bracket with bosses and holes</b><br><sub>Sketch layers → extrude → booleans · 6:35</sub></td>
<td width="33%" align="center"><a href="https://www.youtube.com/watch?v=uxKMA-jtiKc"><img src="https://i.ytimg.com/vi/uxKMA-jtiKc/mqdefault.jpg" alt="Mobile stand"></a><br><b>A phone stand</b><br><sub>Sketching, sections and B-splines · 30:05</sub></td>
</tr>
<tr>
<td align="center"><a href="https://www.youtube.com/watch?v=-T89c6IfPoA"><img src="https://i.ytimg.com/vi/-T89c6IfPoA/mqdefault.jpg" alt="Explaining swp, swp_c, swp_surf and p_line3d"></a><br><b>swp, swp_c, swp_surf, p_line3d</b><br><sub>How point lists become solids · 11:23</sub></td>
<td align="center"><a href="https://www.youtube.com/watch?v=mVKa1ZQn5xs"><img src="https://i.ytimg.com/vi/mVKa1ZQn5xs/mqdefault.jpg" alt="Drill bit"></a><br><b>A drill bit</b><br><sub>Helical flutes with helix() · 2:19</sub></td>
<td align="center"><a href="https://www.youtube.com/watch?v=PYGRlvD9uGs"><img src="https://i.ytimg.com/vi/PYGRlvD9uGs/mqdefault.jpg" alt="3D knots"></a><br><b>3D knots</b><br><sub>Waves wrapped onto paths · 11:30</sub></td>
</tr>
<tr>
<td align="center"><a href="https://www.youtube.com/watch?v=XH54RntgQ9c"><img src="https://i.ytimg.com/vi/XH54RntgQ9c/mqdefault.jpg" alt="Creating threads"></a><br><b>Threads</b><br><sub>Model here, finish in SanPyCAD Brep · 20:27</sub></td>
<td align="center"><a href="https://www.youtube.com/watch?v=PIlZxFOpFlg"><img src="https://i.ytimg.com/vi/PIlZxFOpFlg/mqdefault.jpg" alt="3-way flange"></a><br><b>A 3-way pipe flange</b><br><sub>Model here, fillet in SanPyCAD Brep · 45:41</sub></td>
<td align="center"><a href="https://www.youtube.com/watch?v=F-FGGaWq4m0"><img src="https://i.ytimg.com/vi/F-FGGaWq4m0/mqdefault.jpg" alt="Installing SanPyCAD on Windows"></a><br><b>Installing on Windows</b><br><sub>Download to first render · 7:01</sub></td>
</tr>
</table>

## How a model usually comes together

This is the workflow the tutorials follow:

1. **Sketch the profile.** Open **▣ 2D Sketch**, draw the outline with lines, arcs, tangent arcs and rounded corners, and click **Send to SanPyCAD**. The profile lands in your script as a ready-to-use variable such as `sec1`. To sketch on an existing part, use **Sketch on Face** and click the face.
2. **Make it 3D in Python.** `linear_extrude()`, `prism()`, sweeps along a path or a `helix()`, lofts between sections.
3. **Combine.** `union()`, `difference()`, `intersection()`, `hull()`. Booleans are exact (bundled manifold3d).
4. **Check it.** Measure, add dimensions, or open the **Drawing** tab for front, top and side views.
5. **Export, or carry on in B-rep.** Export STL for printing, or click **Send to SanPyCAD Brep** to fillet the edges you pick and export a true STEP file.

## Features

### Two ways to write the same model
- **Python** — plain Python with the whole ocad library: loops, variables, numpy, your own helper functions.
- **OpenSCAD-style** — `cube([10,10,10]); difference() { ... }` for anyone who already thinks in OpenSCAD.

The toolbar switches between them and keeps a separate script for each.

### A geometry library built for the hard parts
600+ functions by Sanjeev Prabhakar, covering:
- **Fillets** — 2D (line-line, circle-circle, line-circle) and 3D (sphere-sphere, solid-solid, solid-surface, marching-cubes based)
- **Sweeps** — extrude along open or closed paths, sculpt along a path, wrap a section or surface around a path, helices and threads
- **Offsets** — 2D sections, 3D solids, surfaces, paths, and lines kept on a surface
- **Curves** — B-spline and Bezier, interpolation through points, sine and cosine waves
- **Hulls, projections and intersections** — convex and concave hulls in 2D and 3D, lines and surfaces projected onto surfaces, and line, polyline, plane and surface intersections

Four functions decide how a set of points becomes geometry, and they come up in nearly every model ([video](https://www.youtube.com/watch?v=-T89c6IfPoA)):

| Function | Use it for |
|---|---|
| `swp(sol)` | a closed solid with both ends capped |
| `swp_c(sol)` | a closed loop with no end caps (rings, tubes) |
| `swp_surf(surf)` | an open surface |
| `p_line3d(path, d)` | a round tube of diameter `d` along any 3D path |

### A real 2D sketcher
Lines, arcs (3-point, centre and angles, tangent), circles, rectangles, N-gons, B-spline and Bezier curves, and `y = f(x)` function curves. Round or chamfer corners, trim, extend, offset, mirror, linear and rotated arrays, convex and concave hulls, and text converted to outlines. Import DXF or SVG, or import a reference image, set its scale, and trace over it by hand or with **Auto-trace** (outline or centerline, with line/arc/circle fitting). Work in layers, then export DXF, SVG, PDF or Python, or send the sketch straight into your script.

### A notebook-style kernel
- Variables persist between renders, so a slow step can run once, be commented out, and everything after it iterated on for free. **Reset Memory** starts clean.
- The **Variables** panel lists everything in memory and previews any variable as a line or points in the 3D view.
- <kbd>Tab</kbd> completes function names and <kbd>Shift</kbd>+<kbd>Tab</kbd> shows a function's signature and docs, as in JupyterLab. A bare expression on its own line prints to the console.
- Find and Replace, resizable panes, and line wrap.

### Exact booleans
Every `union()`, `difference()`, `intersection()` and `hull()` runs on the bundled [manifold3d](https://github.com/elalish/manifold) library, so results are sharp and exact with nothing to install. A toolbar badge shows the active engine. OpenSCAD is not required; the optional **OpenSCAD path** setting in the app is only used to render raw `fo()` `.scad` text.

### Measure, dimension, draw
- **Measure** two vertices (distance plus x/y/z components) or two edges (lengths, angle, shortest distance). In Python mode a picked vertex also reports which point of which variable it came from, for example `sol1[0][10]`.
- **Dimension** places labelled dimensions on the model: point-to-point, edge-to-edge, face-to-face, point-to-edge, centre-to-edge, radius and centre distance, as a direct value or ΔX / ΔY / ΔZ.
- **Drawing** builds a sheet with one view, three views (front, top, right) or all six. **Add View** captures any angle you've orbited to, and section views cut the part along X, Y or Z. Add dimensions on the sheet, then download it as SVG or PDF.

### Get models in and out
- **Export:** STL, OBJ, SVG, DXF and STEP. STEP bodies are written as exact B-rep wherever the geometry still carries its cross-sections.
- **Export many bodies at once:** `export_step(swp(s1), swp_c(s2), swp_surf(s3), *rotary_array, "/path/model1")` writes one STEP file per variable into the folder (lists of solids such as rotary arrays stay together under one name). Add `one_file=True` for a single assembly file.
- **Import:** STL, OBJ and OFF meshes, and SVG outlines.
- **Save:** scripts are plain `.py` or `.scad` text, openable in any editor.
- **Send to SanPyCAD Brep:** pass the current shapes to [SanPyCAD Brep](https://github.com/sprabhakar2006/sanpycad-brep) to fillet and chamfer the edges you pick and export true STEP.
- **From a script:** `export_sanpycad_brep(swp(s1), swp_c(fl1), swp_surf(s2))` sends those bodies (including grouped lists, kept under one name) straight to a running SanPyCAD Brep window.

## SanPyCAD and SanPyCAD Brep

The two apps are designed to be used together.

| | **SanPyCAD** (this repo) | **[SanPyCAD Brep](https://github.com/sprabhakar2006/sanpycad-brep)** |
|---|---|---|
| Geometry | triangle mesh, built from point lists | exact B-rep (analytic and NURBS surfaces) |
| Engine | ocad library + manifold3d | build123d on OpenCASCADE |
| Strong at | freeform and organic shapes, sweeps, wraps, waves, point-driven design | mechanical parts, fillets and chamfers on picked edges, CAD-ready STEP |
| Script style | Python or OpenSCAD-style | Python |

A common pattern in the tutorials is to shape a part here, then click **Send to SanPyCAD Brep** for the final fillets and a STEP file that opens in FreeCAD, SolidWorks or Fusion.

## Known limitations

- No 2D booleans. `linear_extrude` and `rotate_extrude` take a single outline; subtract a 3D shape from the extruded solid instead.
- No `text()`, `surface()`, `minkowski()` or `render()` in OpenSCAD-style mode.
- Simplified module scoping in OpenSCAD-style mode: a module sees its own parameters plus globals.
- Builds aren't signed or notarized yet, hence the first-launch warnings.

The full list is in the [reference](docs/reference.md#known-limitations).

## Run from source

For development, or on an Intel Mac or Linux:

```bash
git clone https://github.com/sprabhakar2006/SanPyCAD.git
cd SanPyCAD
pip install numpy scipy sympy scikit-image manifold3d pywebview pyperclip
python app.py
```

Requires Python 3.10 or newer. Without `pywebview` the app opens in your default browser instead of its own window.

<details>
<summary><b>Building the downloadable bundle</b></summary>

```bash
pip install pyinstaller
python packaging/build_bundle.py
```

This produces `dist/SanPyCAD.app` (macOS) or `dist/SanPyCAD/` (Windows, Linux), plus a zip, with Python and every dependency inside. PyInstaller can't cross-compile, so build each platform on that platform. Pushing a `v*` tag runs `.github/workflows/build-installers.yml` on GitHub's macOS and Windows runners and attaches both zips to the release.

The packaged app keeps its settings, log (`SanPyCAD.log`) and `imports/` folder in `~/Library/Application Support/SanPyCAD` on macOS and `%APPDATA%\SanPyCAD` on Windows. The log is the first place to look if something misbehaves.

</details>

## Documentation

- **[docs/reference.md](docs/reference.md)** — the full guide to the app window, both scripting modes, booleans and limitations
- **📖 Reference** button in the app — every library function, searchable
- **[YouTube channel](https://www.youtube.com/@sanjeevprabhakar3837/videos)** — step-by-step modeling sessions

## Credits

Created by **Sanjeev Prabhakar**. The ocad geometry library, bundled in `backend/`, does the modeling work: every primitive, fillet, offset, sweep and hull. SanPyCAD is the editor, viewer, sketcher and language layer around it.

Built with [manifold3d](https://github.com/elalish/manifold), [CodeMirror](https://codemirror.net/) and [Three.js](https://threejs.org/).

## License

[MIT](LICENSE)
