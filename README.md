# SanPyCAD

**Code-first 3D modeling, with fillets that actually work.**

Write a script, press Render, and watch the solid appear next to it.
SanPyCAD reads OpenSCAD-style syntax *and* plain Python, and ships with
a 600-function geometry library covering the operations that are
famously painful in plain OpenSCAD: fillets, offsets, sweeps along a
path, lofts between sections, b-spline and Bezier curves, and concave
hulls.

Download it, double-click it, and start modeling. There is no Python to
install, no packages to pip, and no build step.

<!-- TODO: add a screen recording here -- a fillet or a sweep being
     rendered live. On a visual tool this is the single most useful
     thing on the page. Drop the file in docs/ and reference it as:
     ![SanPyCAD](docs/demo.gif) -->

---

## Install

Grab the build for your machine from the
[latest release](../../releases/latest), unzip it, and open it. Each
download carries its own Python and every library it needs.

| Platform | Download | Open it |
|---|---|---|
| macOS (Apple Silicon) | `SanPyCAD-mac-arm64.zip` | double-click `SanPyCAD.app` |
| macOS (Intel) | `SanPyCAD-mac-intel.zip` | double-click `SanPyCAD.app` |
| Windows 10/11 (x64) | `SanPyCAD-win-x64.zip` | open the folder, double-click `SanPyCAD.exe` |

**First launch on macOS** shows "SanPyCAD cannot be opened because the
developer cannot be verified" — the app is not notarized by Apple.
Right-click the app → **Open** → **Open**, once. Every launch after that
is a normal double-click.

**First launch on Windows** may show a SmartScreen banner for the same
reason: **More info** → **Run anyway**.

Prefer to run from the source instead? See
[Running from source](#running-from-source).

## Your first model

Open the app and pick **Python** in the toolbar, then:

```python
a = cube([30, 30, 10], center=True)
b = cylinder(r=8, h=40, center=True)
show(difference(a, b))
```

Press **Render** (or Ctrl/Cmd+Enter). Now the thing you came here for —
a real fillet, in one call:

```python
s1 = sphere(10)
s2 = sphere(7, [15, 15, 0])
f1 = fillet_2spheres(s1, s2, 7, s1=10, s2=40)
show(swp(s1), swp(s2), swp(f1))
```

The **Examples** dropdown has 100+ ready scripts, from primitives to
marching-cubes fillets. The **📖 Reference** button searches every
function in the library by name or description.

## What you get

**Two ways to write the same model.** An OpenSCAD-style language
(`cube([10,10,10]); difference() { ... }`) for anyone who already thinks
that way, and plain Python — loops, variables, your own helper
functions, numpy — for anything the little language would make painful.
The toolbar switches between them and keeps both scripts.

**A notebook-style kernel.** Variables persist between renders, so an
expensive computation can be run once, commented out, and everything
downstream of it iterated on for free. Tab completes function names,
Shift+Tab shows a signature and docstring, and bare expressions echo to
the console — the same habits as JupyterLab.

**Exact booleans when OpenSCAD is installed.** SanPyCAD finds a local
[OpenSCAD](https://openscad.org/downloads.html) install automatically
and hands boolean CSG to its Manifold engine, so results are sharp and
exact. Without it the app still works standalone, falling back to a
voxel + marching-cubes approximation. The toolbar badge says which one
is in use. OpenSCAD is optional, and it is the only thing worth
installing alongside SanPyCAD.

**Measure what you modeled.** Click two vertices for a distance and its
x/y/z components, or two edges for their lengths, the angle between
them, and the shortest distance across. In Python mode a picked vertex
also reports which point of which variable it came from — `sol1[0][10]`
— so it can be referenced straight back in the script.

**Get the model out.** Export STL, OBJ, SVG, DXF, or STEP. STEP bodies
come out as an exact B-rep rather than triangles wherever the geometry
still carries its cross-sections. Import STL, OBJ, OFF, and SVG back in.
Scripts save as ordinary `.py` / `.scad` text files, openable in any
editor.

**Runs offline.** The editor and 3D viewer are bundled, so after the
download nothing is fetched from the network, ever.

Full details: **[docs/reference.md](docs/reference.md)**.

## What it doesn't do yet

- **No 2D booleans.** `linear_extrude`/`rotate_extrude` take a single
  outline; subtract a 3D shape from a solid instead.
- **No `text()`, `surface()`, `minkowski()`, or `render()`** in the
  OpenSCAD-style mode.
- **Simplified module scoping** — a module body sees its own parameters
  plus globals, not the caller's locals.
- **Not signed or notarized**, hence the first-launch warnings above.

The [full list](docs/reference.md#known-limitations) is in the reference.

## Running from source

Useful if you want to modify it, or if you are on Linux (no prebuilt
bundle yet).

```bash
git clone https://github.com/sprabhakar2006/SanPyCAD.git
cd SanPyCAD
pip install numpy scipy sympy scikit-image pywebview pyperclip
python app.py
```

Python 3.10 or newer (the geometry library uses `match` statements).
The prebuilt bundles ship 3.11. Without `pywebview` the app still runs —
it opens in your default browser instead of its own window.

## Building the bundle

```bash
pip install pyinstaller
python packaging/build_bundle.py
```

This produces `dist/SanPyCAD.app` (macOS) or `dist/SanPyCAD/` (Windows,
Linux) plus a zip of it, with Python and every dependency inside.

PyInstaller cannot cross-compile, so each platform's bundle has to be
built on that platform. `.github/workflows/build-installers.yml` runs
this same script on GitHub's macOS and Windows runners: push a `v*` tag
and the finished bundles are attached to a release automatically, or
start it by hand from the **Actions** tab.

Where the frozen app keeps its files:

| | macOS | Windows |
|---|---|---|
| Settings, log, `imports/` | `~/Library/Application Support/SanPyCAD` | `%APPDATA%\SanPyCAD` |

`SanPyCAD.log` in that folder holds the console output of the last
session — the first place to look if something misbehaves.

## Credits

SanPyCAD is built on the `ocad` geometry library (bundled in
`backend/`), written by **Sanjeev Prabhakar**. That library does the
actual modeling work -- every primitive, fillet, offset, sweep and hull
-- and SanPyCAD is the editor, viewer, and language layer around it.

Also built on [OpenSCAD](https://openscad.org/) (optional, for exact
boolean CSG), [CodeMirror](https://codemirror.net/) and
[Three.js](https://threejs.org/).

## License

[MIT](LICENSE).
