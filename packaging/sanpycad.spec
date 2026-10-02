# -*- mode: python ; coding: utf-8 -*-
"""
sanpycad.spec -- PyInstaller recipe for the self-contained SanPyCAD
bundle: a CPython interpreter, every library the app needs, and the
app's own files in one folder the user can double-click. Nothing has
to be installed alongside it.

Build it with `python packaging/build_bundle.py` (which fetches the
editor/viewer assets first, then calls PyInstaller on this file)
rather than invoking pyinstaller by hand.

The one unusual thing here: backend/*.py are NOT frozen as code. They
are loader stubs that read backend/_protected/<name>.enc from a path
derived from their own __file__, so they must stay real files on disk
inside the bundle. They are therefore shipped as DATA, and their
module names are excluded so PyInstaller's own frozen importer can't
shadow the on-disk copies at runtime. Because their real source is
encrypted, PyInstaller cannot scan it for imports either -- so
everything those modules import is listed by hand in hiddenimports
below. Anything missing from that list shows up as an ImportError on
first render, not at build time.
"""
import os
import sys

from PyInstaller.building.datastruct import Tree
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))
IS_WINDOWS = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"

# Backend modules shipped as encrypted source + on-disk loader stub.
# Keep in sync with build_protected_backend.py's MODULES list.
PROTECTED_MODULES = [
    "ocad", "csg", "geom_bridge", "mesh_import", "openscad_cli",
    "python_eval", "scad_eval", "scad_lang", "server", "geom_ops",
    "cad_io", "step_export",
]
# Plain-source backend files that must also load from disk, so that
# their own __file__-relative paths (backend/_protected/, frontend/
# vendor/) keep resolving the same way they do from source.
BACKEND_LOADED_FROM_DISK = PROTECTED_MODULES + [
    "_crypto_loader", "openscad4", "vendor_assets",
]

# --- what the encrypted backend imports, since it can't be scanned ----
# The backend reaches for scipy.spatial (ConvexHull, cKDTree, Delaunay),
# scipy.interpolate (make_interp_spline), skimage.measure (marching
# cubes, find_contours, approximate_polygon), skimage.draw.polygon and
# sympy. Those pull in a web of internal submodules lazily -- skimage
# in particular uses lazy_loader, so nothing is importable at analysis
# time -- so whole packages are collected rather than named leaves.
# What is NOT collected is the image-I/O stack under skimage.io
# (OpenCV, Pillow, imageio and Qt): excluded below, it is never reached
# and would otherwise roughly triple the download.
hiddenimports = [
    "numpy", "sympy", "pyperclip", "webview",
    "scipy.spatial", "scipy.interpolate", "scipy.ndimage", "scipy.signal",
    "skimage.measure", "skimage.draw", "skimage._shared",
]
for pkg in ("scipy", "skimage", "sympy"):
    hiddenimports += collect_submodules(pkg)
hiddenimports += [
    "ast", "base64", "collections", "contextlib", "datetime", "functools",
    "http.server", "inspect", "io", "json", "math", "platform", "re",
    "shutil", "socket", "socketserver", "struct", "subprocess", "tempfile",
    "threading", "time", "traceback", "urllib.request", "warnings",
    "webbrowser", "xml.etree.ElementTree",
]

# csg.py's `import manifold3d` is a soft dependency -- it's a compiled
# C++ extension package (the exact boolean/hull engine), caught in a
# try/except ImportError there so the app still runs via the voxel
# fallback if it's missing. But because csg.py is itself one of the
# encrypted/disk-loaded modules above, PyInstaller can never see that
# import statement to auto-detect it -- without being told by hand like
# this, it silently never gets bundled at all, so every frozen build
# reports "manifold3d not installed" and only ever uses the rougher
# fallback, even though it is genuinely installed in the build venv.
#
# "manifold3d" itself is added unconditionally, NOT inside a try/except:
# an earlier version of this wrapped the whole
# `hiddenimports += ["manifold3d"] + collect_submodules(...)` expression
# in one try/except, which meant that if collect_submodules() raised for
# any reason, the += never ran at all (Python evaluates the right-hand
# side first) and "manifold3d" silently never made it into hiddenimports
# either -- exactly the kind of bug that looks like it should work but
# doesn't. collect_submodules/collect_dynamic_libs are supplementary (for
# any private submodules or bundled shared libraries respectively) so
# those two stay individually guarded, each only protecting itself.
hiddenimports += ["manifold3d"]
manifold_binaries = []
try:
    hiddenimports += collect_submodules("manifold3d")
except Exception:
    pass
try:
    manifold_binaries += collect_dynamic_libs("manifold3d")
except Exception:
    pass

# manifold3d's Windows wheel is repaired by delvewheel (standard practice
# for compiled-extension wheels on Windows), which bundles its runtime
# DLL dependencies into a SEPARATE sibling folder at the site-packages
# root -- e.g. "manifold3d.libs" next to the manifold3d module itself,
# not inside it. collect_dynamic_libs("manifold3d") above only ever
# looks inside a package's own directory -- and the CI build log
# (confirmed via "collect_dynamic_libs - skipping library collection
# for module 'manifold3d' as it is not a package") shows manifold3d
# ships as a single flat compiled module file directly in site-packages
# (e.g. manifold3d.cp311-win_amd64.pyd), not a package folder with its
# own __init__.py -- so it never had anything to look inside anyway.
#
# That flat-module layout is also why the first version of this fix
# still didn't work: it assumed a package (site-packages/manifold3d/
# __init__.py) and did dirname(dirname(file)) to climb from the
# package folder up to site-packages -- two levels up. For a flat
# module file, __file__ already sits directly in site-packages, so
# climbing two levels lands one directory too high (e.g. in Lib/
# instead of Lib/site-packages/), and the "manifold3d.libs" sibling
# folder was never found. Both possible layouts are checked below so
# this doesn't silently break again if the wheel's layout changes.
# No-op on macOS/Linux, where delocate/auditwheel repair wheels
# differently (no sibling .libs folder), and no-op if manifold3d isn't
# installed in this venv at all.
try:
    import importlib
    _m3d_mod = importlib.import_module("manifold3d")
    _m3d_file = os.path.abspath(_m3d_mod.__file__)
    _candidate_roots = {
        os.path.dirname(_m3d_file),                       # flat module file
        os.path.dirname(os.path.dirname(_m3d_file)),       # package folder
    }
    _found_libs_dirs = []
    for _site_root in _candidate_roots:
        if not os.path.isdir(_site_root):
            continue
        for _entry in os.listdir(_site_root):
            if _entry.lower().startswith("manifold3d") and _entry.lower().endswith(".libs"):
                _libs_dir = os.path.join(_site_root, _entry)
                _found_libs_dirs.append(_libs_dir)
                for _fname in os.listdir(_libs_dir):
                    manifold_binaries.append((os.path.join(_libs_dir, _fname), _entry))
    # Printed during the build (visible in CI logs) so a future failure
    # shows up as a log line instead of another silent no-op.
    print(f"[sanpycad.spec] manifold3d module file: {_m3d_file}")
    print(f"[sanpycad.spec] manifold3d .libs folders found: {_found_libs_dirs or 'NONE'}")
except Exception as _m3d_scan_exc:
    print(f"[sanpycad.spec] manifold3d .libs scan failed: {_m3d_scan_exc!r}")

datas = collect_data_files("sympy")

a = Analysis(
    [os.path.join(PROJECT_ROOT, "app.py")],
    pathex=[PROJECT_ROOT, os.path.join(PROJECT_ROOT, "packaging")],
    binaries=manifold_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    # open3d is imported lazily inside three ocad.py helpers and is an
    # optional extra; bundling it would add hundreds of MB for features
    # almost nobody calls. matplotlib/tkinter/IPython are pulled in as
    # incidental dependencies of scipy/sympy and are never used here.
    excludes=BACKEND_LOADED_FROM_DISK + [
        # open3d is imported lazily inside three ocad.py helpers and is
        # an optional extra. The rest arrive as incidental dependencies
        # of scipy/skimage/sympy and are never reached at runtime; cv2,
        # Pillow, imageio and Qt alone are ~350 MB.
        "open3d", "cv2", "PIL", "imageio", "imageio_ffmpeg", "skimage.io",
        "PyQt5", "PyQt6", "PySide2", "PySide6", "matplotlib", "tkinter",
        "IPython", "jupyter", "notebook", "pytest", "pandas",
        "build123d", "OCP",
    ],
    noarchive=False,
)

# The app's own files, copied in as data (see the module docstring).
a.datas += Tree(os.path.join(PROJECT_ROOT, "backend"), prefix="backend",
                excludes=["__pycache__", "_protected_src", "*.pyc"])
a.datas += Tree(os.path.join(PROJECT_ROOT, "frontend"), prefix="frontend",
                excludes=["__pycache__", "*.pyc"])
a.datas += Tree(os.path.join(PROJECT_ROOT, "examples"), prefix="examples",
                excludes=["__pycache__", "*.pyc"])
a.datas += Tree(os.path.join(PROJECT_ROOT, "packaging"), prefix="packaging",
                excludes=["__pycache__", "*.pyc", "*.spec", "build_bundle.py",
                          "entitlements.plist"])

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SanPyCAD",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # console=False everywhere: this is a windowed app. On Windows that
    # is what stops a black terminal opening behind the app window --
    # the thing SanPyCAD.vbs existed to work around.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=IS_MAC,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="SanPyCAD",
)

if IS_MAC:
    app = BUNDLE(
        coll,
        name="SanPyCAD.app",
        icon=None,
        bundle_identifier="com.sanpycad.app",
        info_plist={
            "CFBundleName": "SanPyCAD",
            "CFBundleDisplayName": "SanPyCAD",
            "CFBundleShortVersionString": os.environ.get("SANPYCAD_VERSION", "1.0.0"),
            "CFBundleVersion": os.environ.get("SANPYCAD_VERSION", "1.0.0"),
            "NSHighResolutionCapable": True,
            # Without this the app window opens behind other windows and
            # the app gets no Dock icon on some macOS versions.
            "LSBackgroundOnly": False,
            "NSRequiresAquaSystemAppearance": False,
        },
    )
