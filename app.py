#!/usr/bin/env python3
"""
app.py -- launches SanPyCAD, the OpenSCAD-like desktop application.

This starts the local geometry backend (backend/server.py, built on your
ocad.py library) and opens it in its own application window using
pywebview, so this behaves like a normal desktop app rather than "go start
a server and open your browser". If pywebview isn't installed, it
transparently falls back to opening your default browser instead -- the
app still works, just as a browser tab.

Normally you don't need to run this file directly -- just double-click
SanPyCAD.app (in the same folder as this file) to launch SanPyCAD like
any other desktop app, no Terminal/command line needed. This is what
that shortcut actually runs under the hood; it's still runnable by hand
too if you ever want to:
    python3 app.py

To get the native window (recommended), install pywebview first:
    pip install pywebview
"""

import base64
import json
import os
import sys
import socket
import tempfile
import threading
import time
import traceback
import webbrowser


def _unblock_bundled_dlls():
    """Windows stamps every file extracted from a downloaded zip with a
    "this came from the internet" mark (an NTFS Zone.Identifier
    alternate data stream). .NET Framework refuses to load an assembly
    carrying that mark, which is what makes pywebview's winforms backend
    (it loads bundled DLLs via pythonnet/.NET) fail with a cryptic
    "Failed to resolve Python.Runtime.Loader.Initialize" RuntimeError on
    a plain unzip-and-run -- nothing to do with this app's own code.
    Removing the mark from every bundled DLL before webview is ever
    imported avoids that entirely. No-op on macOS/Linux or when running
    from source (only frozen Windows builds carry bundled DLLs)."""
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return
    base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    for root, _dirs, files in os.walk(base):
        for name in files:
            if name.lower().endswith(".dll"):
                try:
                    os.remove(os.path.join(root, name) + ":Zone.Identifier")
                except OSError:
                    pass  # no mark present, or the folder isn't writable


_unblock_bundled_dlls()

# Where backend/, frontend/ and examples/ live. Running from source
# that is simply this file's own folder. In a frozen (PyInstaller)
# build they are copied into the bundle's resource folder instead,
# which is not next to the executable -- see packaging/bundle_paths.py.
if getattr(sys, "frozen", False):
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    sys.path.insert(0, os.path.join(BASE_DIR, "packaging"))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

import server  # noqa: E402
import brep_bridge  # noqa: E402

try:
    import bundle_paths  # noqa: E402  (frozen builds only)
except ImportError:
    bundle_paths = None


def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def wait_for_server(url, timeout=5.0):
    import urllib.request
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=0.5)
            return True
        except Exception:
            time.sleep(0.05)
    return False


import re as _re  # noqa: E402

_TOP_LEVEL_SHOW_RE = _re.compile(r"^show\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:,.*)?\)\s*$")


def _build_brep_script(code, wanted_names):
    """Turns a SanPyCAD script into the exact script Brep should run for
    "Send to SanPyCAD Brep", instead of exporting/importing a STEP file.

    SanPyCAD's own geometry library (ocad.py) is already flattened into
    Brep's script namespace, and Brep overrides swp()/swp_c()/swp_surf()
    to build REAL B-rep shapes directly from the same section-grid data
    (see brep.py's python_eval.py "auto-promotion" wrappers) instead of
    ocad.py's own OpenSCAD-text output -- so re-running this exact script
    over there reproduces the shape natively and instantly, with none of
    the STEP round-trip's file-size/speed cost or the smooth-fit-vs-
    faceted mismatch that caused surfaces to come back dimpled. This is
    what the user asked for directly: "convert the sanpycad script to
    relevant sanpycad-brep script and then show will produce correct
    results."

    `wanted_names`, if given (from the Variables panel's "Send to Brep
    as..." selection), comments out every top-level show(<name>) call
    for a name NOT in that set (so only the checked variables render in
    Brep) and appends a show(<name>) for any wanted name the script
    didn't already show on its own. Left completely untouched, including
    every one of the script's own show() calls, when no selection was
    made -- matching "send everything currently shown" default.

    Only rewrites lines that are ENTIRELY a top-level `show(name)` call
    (no leading indentation, nothing else on the line) -- deliberately
    conservative, since every SanPyCAD script this app has ever
    generated or the user has written by hand in practice is flat, top-
    level code with no show() calls nested inside a function/loop body;
    leaving anything indented alone means this can never mangle a script
    structured differently than expected."""
    if not wanted_names:
        return code
    wanted = set(wanted_names)
    shown_already = set()
    out_lines = []
    for line in code.splitlines():
        m = _TOP_LEVEL_SHOW_RE.match(line)
        if m:
            nm = m.group(1)
            if nm in wanted:
                out_lines.append(line)
                shown_already.add(nm)
            else:
                out_lines.append(f"# {line}  # (not selected for Brep)")
        else:
            out_lines.append(line)
    for nm in wanted_names:
        if nm not in shown_already:
            out_lines.append(f"show({nm})")
    return "\n".join(out_lines)


import ast as _ast  # noqa: E402


def _free_names_in_script(code):
    """Names the script READS (Load context) that it never itself
    ASSIGNS (Store context) anywhere in its own text -- a plain,
    deliberately approximate "free variable" scan via the ast module
    (not real scope analysis: a name assigned only inside a nested
    function/comprehension still counts as "assigned" here, same as
    every other SanPyCAD script-text tool in this file, which all
    assume flat, top-level procedural code -- see _build_brep_script()'s
    own docstring for why that's a safe assumption in practice).

    Used by send_to_brep() to find variables like a "2D Sketch"-
    injected `sec`/`path`/`rect` that the CURRENT script's own text
    never defines at all -- those live only in this app's own
    persistent kernel namespace (python_eval.py's set_persisted_
    variable(), called by the 2D Sketch panel/GUI Functions), invisible
    to a script-mode send that only ever looks at the script's text."""
    try:
        tree = _ast.parse(code)
    except SyntaxError:
        return set()
    loaded, stored = set(), set()
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Name):
            if isinstance(node.ctx, _ast.Load):
                loaded.add(node.id)
            elif isinstance(node.ctx, (_ast.Store, _ast.Del)):
                stored.add(node.id)
        elif isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
            stored.add(node.name)
        elif isinstance(node, _ast.ClassDef):
            stored.add(node.name)
    return loaded - stored


_LITERAL_MAX_DEPTH = 25


def _to_plain_literal(value, _depth=0):
    """Recursively converts `value` to plain built-in types (None, bool,
    int, float, str, list, dict) that repr() round-trips as valid Python
    source -- e.g. a numpy array/scalar (common in this app's own
    ocad.py-computed values) via its own .tolist()/.item(), so the
    result can be written as a literal `name = <this>` line straight
    into a script. Raises TypeError/ValueError for anything that isn't
    plain data (a Mesh, a function, a custom class instance, ...) --
    callers should catch that and simply skip the variable rather than
    emit broken/misleading code, same as e.g. an un-injectable "GUI
    Function" result already gets skipped elsewhere in this app.

    Depth-capped (not just for pathological self-referential structures
    -- ordinary recursion depth is already bounded by Python's own
    limit -- but so a variable holding something absurdly deep doesn't
    hang building a repr() no one could read anyway)."""
    if _depth > _LITERAL_MAX_DEPTH:
        raise ValueError("value nested too deeply to send as a literal")
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [_to_plain_literal(v, _depth + 1) for v in value]
    if isinstance(value, dict):
        return {str(k): _to_plain_literal(v, _depth + 1) for k, v in value.items()}
    if hasattr(value, "tolist"):  # numpy array (or anything duck-typed like one)
        return _to_plain_literal(value.tolist(), _depth + 1)
    if hasattr(value, "item") and not hasattr(value, "__len__"):
        return _to_plain_literal(value.item(), _depth + 1)  # numpy scalar
    raise TypeError(f"not a plain-data value: {type(value).__name__}")


def _build_kernel_var_prelude(code, persisted_ns):
    """Prelude lines (`name = <literal>`, one per variable) to prepend
    to a script before sending it to Brep, for every name the script
    reads but never itself assigns (see _free_names_in_script()) AND
    that this app's own persistent kernel namespace actually has a
    value for right now -- most commonly a "2D Sketch"-injected `sec`/
    `path`/`rect`, but this covers anything a GUI Function or an
    earlier, since-commented-out line left sitting in memory too, the
    same "keeps a variable a prior run set" persistence this app's own
    Python-mode kernel already gives a normal Render (see python_eval.py's
    _save_persisted_vars() docstring) -- Brep starts a brand new kernel
    with none of that history, so this is what carries it over.

    REAL BUG FIX (user report: a script referencing a 2D-Sketch-drawn
    `sec`/`path`/`rect` rendered fine in SanPyCAD -- where these names
    were already sitting in the persistent kernel namespace from the
    sketch panel, entirely outside the script's own visible text -- but
    came back "NameError: name 'sec' is not defined" the moment the
    exact same script text was sent to Brep's own, separate, brand-new
    kernel, which never saw that injection at all).

    Silently skips (doesn't error, doesn't warn) any free name that
    either isn't currently in the persisted namespace (e.g. a genuine
    typo/undefined-variable bug in the user's own script -- Brep will
    raise the very same NameError SanPyCAD itself would have) or whose
    value isn't plain literal data (e.g. it holds a Mesh/other object
    that wouldn't mean anything to send as source text anyway)."""
    free = _free_names_in_script(code)
    lines = []
    for name in sorted(free):
        if name not in persisted_ns:
            continue
        try:
            literal = _to_plain_literal(persisted_ns[name])
        except (TypeError, ValueError):
            continue
        try:
            text = repr(literal)
        except Exception:
            continue
        lines.append(f"{name} = {text}")
    return lines


class Api:
    """Exposed to the frontend as `window.pywebview.api` (see js_api= below).

    export_file(): the native desktop window has no address bar, tabs, or
    back button, so the normal browser trick of building a Blob and
    clicking a hidden <a download> link doesn't work here: pywebview's
    underlying WKWebView (on macOS) doesn't honor the HTML5 download
    attribute, and instead just navigates the whole window to the blob's
    raw content -- which looks like the app "breaking" into a wall of
    vertex/face text with no way back except quitting and relaunching.
    Building the file here in Python and handing it to webview's own
    native Save panel avoids that entirely; the frontend only falls back
    to the Blob/<a download> approach when running as a plain browser tab
    (no window.pywebview), where it already works fine.

    import_pick_file(): same idea in reverse -- a native Open panel to
    pick a file to import(), instead of the browser-only <input type=file>
    + upload-the-bytes dance the frontend falls back to when there's no
    pywebview (see /import/save in server.py). Since this process already
    has direct filesystem access, there's no need to copy the chosen file
    anywhere first -- its real path is handed straight to import().

    save_script()/open_script(): same native-dialog approach, but for the
    script's own source code (.py/.scad) rather than rendered geometry --
    this is the app's equivalent of a normal text editor's File > Save/
    Save As/Open, so a design can be closed and reopened later instead of
    only ever exported as a one-way STL/OBJ/etc snapshot.

    save_pdf()/save_sketch()/open_sketch()/export_drawing()/
    import_drawing(): originally written for SanPyCAD-2D, the separate
    standalone app frontend/sketch2d.html was built for -- ported here
    verbatim (same signatures) when that whole file was embedded as an
    iframe in this app's own "2D Sketch" panel (see index.html), because
    that iframe has no window.pywebview of its own to call into: pywebview
    only injects its JS-API bridge into the top-level frame, so
    sketch2d.html's pywebviewApi() helper reaches these through
    window.parent.pywebview.api instead -- i.e., THIS Api instance, since
    index.html (this window's actual top-level page) is that parent.
    Without these 5 methods existing here too, every one of those features
    silently fell through to a Blob/<a download> click, which this
    window's webview navigates to instead of downloading -- confirmed
    directly against a user report: saving a sketch replaced the whole 2D
    Sketch panel with a wall of raw JSON text, with no way back except
    quitting and relaunching (the exact failure export_file()'s own
    fallback-avoidance above was written to prevent, just never extended
    to the embedded sketch panel's own save/open features).
    """

    def export_file(self, code, mode, csg_resolution, kind):
        try:
            csg_resolution = max(16, min(int(csg_resolution), 160))
            result, _ev = server.run_any(code, csg_resolution, mode)
            if result.get("error"):
                return {"error": result["error"]}
            meshes = list(server.ev_meshes_from_result(result))
            if not meshes:
                return {"error": "nothing to export (empty scene)"}

            if kind == "step":
                # STEP is the one format that is NOT built from the rendered
                # triangles: a raw sol still carries its cross-sections and
                # goes out as an exact B-rep, so we ask python_eval what the
                # just-finished run actually passed to show(). Anything
                # already reduced to a Mesh (a boolean result, an imported
                # mesh, a mesh_erode() core) can only be written faceted.
                import step_export as STEP
                import python_eval as PE
                bodies = list(PE.last_export_bodies()) if mode == "python" else []
                if not bodies:
                    bodies = [(f"body{i + 1}", (m.V, m.F))
                              for i, m in enumerate(meshes)]
                try:
                    data = STEP.sol_to_step_string(bodies, name="sanpycad_model")
                except STEP.StepExportError as e:
                    return {"error": f"STEP export failed: {e}"}
                n_exact = sum(1 for _n, k, _x in STEP.last_report() if k == "exact")
                print(f"[export/step] {len(bodies)} bodies "
                      f"({n_exact} exact B-rep, {len(bodies) - n_exact} faceted)")
                default_name = "model.step"
            else:
                builders = {
                    "stl": (server.build_stl_binary, "model.stl"),
                    "obj": (server.build_obj_text, "model.obj"),
                    "svg": (server.build_svg_text, "model.svg"),
                    "dxf": (server.build_dxf_text, "model.dxf"),
                }
                if kind not in builders:
                    return {"error": f"unknown export kind: {kind}"}
                builder, default_name = builders[kind]
                data = builder(meshes)

            window = webview.windows[0]
            save_dialog = getattr(getattr(webview, "FileDialog", None), "SAVE", None)
            if save_dialog is None:
                save_dialog = webview.SAVE_DIALOG  # older pywebview versions
            chosen = window.create_file_dialog(save_dialog, save_filename=default_name)
            if not chosen:
                return {"canceled": True}
            path = chosen[0] if isinstance(chosen, (list, tuple)) else chosen

            is_binary = isinstance(data, (bytes, bytearray))
            mode_flag = "wb" if is_binary else "w"
            # Explicit utf-8 for the text formats (OBJ/SVG/DXF) rather than
            # relying on the platform's default text encoding -- Windows'
            # default is a locale codepage (e.g. cp1252), not utf-8, so a
            # model with a non-ASCII color name or similar could otherwise
            # fail to save there even though the exact same script exports
            # fine on macOS/Linux.
            with open(path, mode_flag, **({} if is_binary else {"encoding": "utf-8"})) as f:
                f.write(data)
            return {"path": path}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    def pick_brep_app_path(self):
        """Native file picker for locating an existing SanPyCAD-Brep
        install -- used the first time 'Send to SanPyCAD-Brep' runs (or
        whenever the user wants to point it somewhere else). Filtered
        per platform to whatever actually launches that app: its .app
        bundle on macOS, its .vbs/.bat launcher on Windows, or app.py
        itself everywhere else (from-source installs, Linux). Persists
        the choice immediately via brep_bridge.set_brep_app_path(), same
        as pick_openscad_path()'s Settings-panel equivalent."""
        try:
            window = webview.windows[0]
            open_dialog = getattr(getattr(webview, "FileDialog", None), "OPEN", None)
            if open_dialog is None:
                open_dialog = webview.OPEN_DIALOG  # older pywebview versions
            if sys.platform == "darwin":
                file_types = ("Applications (*.app)", "All files (*.*)")
            elif sys.platform.startswith("win"):
                file_types = ("SanPyCAD Brep launcher (*.vbs;*.bat)", "All files (*.*)")
            else:
                file_types = ("Python files (*.py)", "All files (*.*)")
            chosen = window.create_file_dialog(open_dialog, file_types=file_types)
            if not chosen:
                return {"canceled": True}
            path = chosen[0] if isinstance(chosen, (list, tuple)) else chosen
            brep_bridge.set_brep_app_path(path)
            return {"path": path}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    def send_to_brep(self, code, mode, csg_resolution, brep_path=None, selection=None):
        """'Send to SanPyCAD-Brep': exports the INDIVIDUAL shape(s) a
        script builds -- not whatever boolean/union of them ends up
        shown -- as a real B-rep STEP file (one body per piece), then
        launches a brand-new SanPyCAD-Brep process pointed at it (see
        brep_bridge.launch_brep()) so each one can be opened there and
        kept editing as its own real B-rep solid: filleted, chamfered,
        booleaned with exact CSG, or exported to an exact STEP file of
        its own -- none of which this mesh-based app can do.

        Deliberately does NOT reuse export_file()'s "step" branch
        (last_export_bodies(), i.e. whatever was passed to show()):
        for a script like `a = cube(); b = cylinder(); c = a - b;
        show(c)`, that would send only `c` -- the boolean RESULT,
        already flattened to a faceted/"segmented" mesh the moment `-`
        ran (booleans discard cross-section data), and useless to redo
        anything exact with in Brep. python_eval.last_named_sols()
        instead returns every top-level variable still holding a raw,
        untouched, fully exact sol -- here, `a` and `b` themselves --
        so Brep gets the real pre-boolean pieces to combine with its
        own exact B-rep booleans, producing a clean result instead of
        one built from an already-segmented import. Only falls back to
        last_export_bodies()/the rendered mesh(es) (the old behavior)
        when a run leaves no individual raw-sol variable at all (e.g.
        a script built entirely from import_mesh()/booleans/OpenSCAD-
        mode, with nothing exact left to send piece-by-piece) --
        otherwise "Send to SanPyCAD Brep" would silently send nothing.

        `brep_path`, if given, overrides (and persists, same as
        pick_brep_app_path()) the remembered SanPyCAD-Brep location --
        used when the frontend just asked the user to locate it via
        pick_brep_app_path() and is now retrying this same call with
        the answer. If neither that nor a previously-remembered path
        exists, returns {"needs_path": True} instead of failing
        outright, so the frontend can prompt once and retry rather
        than just erroring.

        `selection`, if given, is a {variable_name: kind} dict built from
        the Variables panel's per-row "Send to Brep as..." choice, kind
        one of "auto"/"solid"/"closed"/"surface" (see step_export.py's
        sol_to_step_string() docstring for what each does). When given
        and non-empty, ONLY those named variables are sent (in last_
        named_sols() order) rather than every raw-sol variable in
        memory, and each is exported using its own explicit kind instead
        of geometry-based guessing -- this is what lets a genuine open
        surface (swp_surf()) round-trip as one instead of silently
        coming back as a solid, which geometry alone can't always tell
        apart from a surface that happens to close up. Omitted/empty
        selection keeps the old default: send every raw-sol variable,
        auto-detected."""
        try:
            target = brep_path or brep_bridge.get_brep_app_path()
            if not target:
                return {"needs_path": True}
            if brep_path:
                brep_bridge.set_brep_app_path(brep_path)

            csg_resolution = max(16, min(int(csg_resolution), 160))
            result, _ev = server.run_any(code, csg_resolution, mode)
            if result.get("error"):
                return {"error": result["error"]}

            import step_export as STEP
            import python_eval as PE
            bodies = list(PE.last_named_sols()) if mode == "python" else []
            sent_pieces = bool(bodies)

            # Preferred path: hand Brep the actual SCRIPT to re-run,
            # instead of a STEP export/import round-trip. ocad.py is
            # already flattened into Brep's own namespace and its
            # swp()/swp_c()/swp_surf() build real B-rep shapes directly
            # from the same section-grid data (see brep.py's "auto-
            # promotion" wrappers) -- so re-running this exact script
            # over there reproduces the shape natively, instantly, and
            # exactly like typing it into Brep by hand, with none of a
            # STEP file's size/speed cost or the smooth-fit-vs-faceted
            # mismatch a re-tessellation can introduce. Only for
            # mode=="python" (the only mode with real per-variable sols
            # to select from in the first place; other modes fall
            # through to the STEP-based path below unchanged).
            if mode == "python":
                wanted_names = None
                if selection:
                    wanted = {nm: k for nm, k in selection.items() if k}
                    if wanted:
                        wanted_names = [nm for nm, _obj in bodies if nm in wanted]
                        if not wanted_names:
                            return {"error": "none of the checked variables are still "
                                              "available to send (they may not be raw "
                                              "solids anymore -- re-render and try again)"}
                        sent_pieces = True

                # A "2D Sketch"-drawn sec/path/rect (or any other GUI-
                # injected variable) lives only in THIS app's own
                # persistent kernel namespace, invisible to the script's
                # own text -- Brep's brand-new kernel needs those values
                # carried over explicitly, or any reference to one raises
                # a NameError there even though it renders fine here. See
                # _build_kernel_var_prelude()'s own docstring.
                prelude = _build_kernel_var_prelude(code, PE.get_persisted_namespace())
                code_to_send = "\n".join(prelude + [code]) if prelude else code

                brep_script = _build_brep_script(code_to_send, wanted_names)
                n_bodies = len(wanted_names) if wanted_names else max(len(bodies), 1)

                port = brep_bridge.find_running_instance()
                if port is not None:
                    try:
                        resp = brep_bridge.send_to_running_instance(
                            port, None, None, None, script_code=brep_script)
                    except Exception:
                        resp = None
                    if resp and resp.get("ok"):
                        return {"ok": True, "n_bodies": n_bodies, "n_exact": n_bodies,
                                 "sent_pieces": sent_pieces, "reused_existing": True}
                    # Fall through to spawning a new instance below.

                fd, script_path = tempfile.mkstemp(
                    suffix=".sanpycad_script.py", prefix="sanpycad_to_brep_")
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(brep_script)

                try:
                    brep_bridge.launch_brep(script_path, target)
                except Exception as e:
                    return {"error": f"Couldn't launch SanPyCAD Brep: {e}"}
                return {"ok": True, "n_bodies": n_bodies, "n_exact": n_bodies,
                         "sent_pieces": sent_pieces, "reused_existing": False}

            if not bodies:
                # No individual pre-boolean pieces survived this run --
                # fall back to whatever was actually shown/rendered
                # (same source "Export as STEP" uses) rather than
                # sending nothing. This is the only path that can ever
                # send an already-booleaned/faceted result.
                bodies = list(PE.last_export_bodies()) if mode == "python" else []
                if not bodies:
                    meshes = list(server.ev_meshes_from_result(result))
                    if not meshes:
                        return {"error": "nothing to send (empty scene)"}
                    bodies = [(f"body{i + 1}", (m.V, m.F))
                              for i, m in enumerate(meshes)]

            kinds = {}
            if selection:
                wanted = {nm: k for nm, k in selection.items() if k}
                if wanted:
                    filtered = [(nm, obj) for nm, obj in bodies if nm in wanted]
                    if not filtered:
                        return {"error": "none of the checked variables are still "
                                          "available to send (they may not be raw "
                                          "solids anymore -- re-render and try again)"}
                    bodies = filtered
                    kinds = wanted
                    sent_pieces = True

            try:
                data = STEP.sol_to_step_string(bodies, name="sanpycad_model", kinds=kinds)
            except STEP.StepExportError as e:
                return {"error": f"STEP export failed: {e}"}
            # The GROUND TRUTH of what each body actually got written as
            # (solid vs. surface) -- not just what the user asked for, since
            # an "auto" body's outcome depends on its own geometry. Brep
            # needs this to reconstruct bodies correctly: splitting a multi-
            # body STEP Compound back into named variables by walking
            # .solids()/.children() alone can't tell a Solid from a Shell
            # apart from geometry either, and silently drops/misassigns a
            # Shell that shares a Compound with a Solid (the "sends 2, only
            # 1 renders, no error" bug this fixes).
            shape_kinds = STEP.last_shape_kinds()
            n_exact = sum(1 for _n, k, _x in STEP.last_report() if k == "exact")
            print(f"[send_to_brep] {len(bodies)} bodies "
                  f"({n_exact} exact B-rep, {len(bodies) - n_exact} faceted, "
                  f"{'individual pieces' if sent_pieces else 'shown/rendered result'})")

            fd, step_path = tempfile.mkstemp(suffix=".step", prefix="sanpycad_to_brep_")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(data)

            # A small sidecar, same idea as the "2D Sketch" sidecar
            # save_script() writes (<path>.sketch.json next to a saved
            # script) -- the STEP file itself carries geometry only, so
            # this is how SanPyCAD Brep's own app.py (see its
            # _pending_import_from_env()) learns each body's ORIGINAL
            # SanPyCAD variable name and can reuse it instead of
            # renaming everything s1/s2/... A failure here is non-fatal
            # (Brep just falls back to generic names) since the shapes
            # themselves are already safely written.
            names = [nm for nm, _ in bodies]

            # Prefer handing this off to an ALREADY-RUNNING SanPyCAD-Brep
            # instance over spawning a second process -- see
            # brep_bridge.find_running_instance()'s own docstring for why
            # a live HTTP POST is used here (the env-var handoff below
            # only works at process startup). If a running instance is
            # found but the live POST itself fails for some reason (e.g.
            # it quit between the liveness check and the POST), fall
            # through to the ordinary spawn-a-new-process path rather
            # than erroring out -- the user still gets their shapes.
            port = brep_bridge.find_running_instance()
            if port is not None:
                try:
                    resp = brep_bridge.send_to_running_instance(
                        port, step_path, names, shape_kinds)
                except Exception:
                    resp = None
                if resp and resp.get("ok"):
                    return {"ok": True, "n_bodies": len(bodies), "n_exact": n_exact,
                             "sent_pieces": sent_pieces, "reused_existing": True}
                # Fall through to spawning a new instance below.

            # A small sidecar, same idea as the "2D Sketch" sidecar
            # save_script() writes (<path>.sketch.json next to a saved
            # script) -- the STEP file itself carries geometry only, so
            # this is how SanPyCAD Brep's own app.py (see its
            # _pending_import_from_env()) learns each body's ORIGINAL
            # SanPyCAD variable name and can reuse it instead of
            # renaming everything s1/s2/... A failure here is non-fatal
            # (Brep just falls back to generic names) since the shapes
            # themselves are already safely written. Only needed for
            # this env-var/startup handoff path -- the live-instance
            # path above sends `names` directly in its POST body.
            try:
                with open(step_path + ".names.json", "w", encoding="utf-8") as f:
                    json.dump({"names": names, "shape_kinds": shape_kinds}, f)
            except Exception:
                pass

            try:
                brep_bridge.launch_brep(step_path, target)
            except Exception as e:
                return {"error": f"Couldn't launch SanPyCAD Brep: {e}"}
            return {"ok": True, "n_bodies": len(bodies), "n_exact": n_exact,
                     "sent_pieces": sent_pieces, "reused_existing": False}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    def import_pick_file(self):
        try:
            window = webview.windows[0]
            open_dialog = getattr(getattr(webview, "FileDialog", None), "OPEN", None)
            if open_dialog is None:
                open_dialog = webview.OPEN_DIALOG  # older pywebview versions
            chosen = window.create_file_dialog(
                open_dialog,
                file_types=(
                    "Importable files (*.stl;*.obj;*.off;*.svg)",
                    "Mesh files (*.stl;*.obj;*.off)",
                    "SVG files (*.svg)",
                    "All files (*.*)",
                ),
            )
            if not chosen:
                return {"canceled": True}
            path = chosen[0] if isinstance(chosen, (list, tuple)) else chosen
            return {"path": path}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    def save_script(self, code, mode, path=None, sketch_data=None, guifn_data=None):
        """Writes `code` to `path` directly if given (plain "Save", once a
        file's already been saved to/opened from once this session), else
        prompts a native Save dialog first (plain "Save As", or the first
        "Save" of a brand new, never-yet-saved script).

        `sketch_data`, if given, is the JSON text of any "2D Sketch" shapes
        currently sent to this script (see index.html's sketchSessions) --
        written to a small sidecar file next to the script itself
        (`<path>.sketch.json`) rather than into the script's own text, so
        reopening it later can silently re-inject those variables and
        restore the original editable sketch WITHOUT ever having spliced a
        big literal points list into the code the user actually wrote and
        sees. If there's nothing to save (every sketch was removed from
        the script since it was last saved, or it never had one), any
        stale sidecar left over from an earlier save is cleaned up rather
        than left around pointing at shapes the script no longer uses.

        `guifn_data`, if given, is the JSON text of every "GUI Functions"
        result currently in memory (see index.html's collectGuiFnSaveData/
        guiFnResults) -- same idea as sketch_data, written to its own
        sidecar (`<path>.guifn.json`) rather than the script's own text,
        so reopening later silently redefines those variables (no
        NameError on the next Render) and redraws their preview in the
        viewer, without ever splicing a points list into the code itself.
        """
        try:
            if not path:
                ext = "py" if mode == "python" else "scad"
                default_name = f"model.{ext}"
                window = webview.windows[0]
                save_dialog = getattr(getattr(webview, "FileDialog", None), "SAVE", None)
                if save_dialog is None:
                    save_dialog = webview.SAVE_DIALOG  # older pywebview versions
                chosen = window.create_file_dialog(save_dialog, save_filename=default_name)
                if not chosen:
                    return {"canceled": True}
                path = chosen[0] if isinstance(chosen, (list, tuple)) else chosen
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            sidecar_path = path + ".sketch.json"
            if sketch_data:
                with open(sidecar_path, "w", encoding="utf-8") as f:
                    f.write(sketch_data)
            else:
                try:
                    os.remove(sidecar_path)
                except OSError:
                    pass  # no sidecar existed -- nothing to clean up
            guifn_sidecar_path = path + ".guifn.json"
            if guifn_data:
                with open(guifn_sidecar_path, "w", encoding="utf-8") as f:
                    f.write(guifn_data)
            else:
                try:
                    os.remove(guifn_sidecar_path)
                except OSError:
                    pass  # no sidecar existed -- nothing to clean up
            return {"path": path}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    def open_script(self):
        try:
            window = webview.windows[0]
            open_dialog = getattr(getattr(webview, "FileDialog", None), "OPEN", None)
            if open_dialog is None:
                open_dialog = webview.OPEN_DIALOG  # older pywebview versions
            chosen = window.create_file_dialog(
                open_dialog,
                file_types=(
                    "SanPyCAD scripts (*.py;*.scad)",
                    "Python files (*.py)",
                    "OpenSCAD files (*.scad)",
                    "All files (*.*)",
                ),
            )
            if not chosen:
                return {"canceled": True}
            path = chosen[0] if isinstance(chosen, (list, tuple)) else chosen
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            result = {"path": path, "code": code}
            # See save_script()'s sidecar comment above -- if this script
            # was saved with one or more "2D Sketch" shapes attached, hand
            # its JSON straight back so the frontend can silently
            # re-inject those variables (no NameError on Render) and
            # restore the original editable sketch(es) in the panel.
            sidecar_path = path + ".sketch.json"
            if os.path.exists(sidecar_path):
                try:
                    with open(sidecar_path, "r", encoding="utf-8") as f:
                        result["sketch_data"] = f.read()
                except OSError:
                    pass  # non-fatal -- the script itself still opened fine
            # See save_script()'s guifn_data comment above -- same idea,
            # own sidecar, for "GUI Functions" results instead of 2D
            # Sketch shapes.
            guifn_sidecar_path = path + ".guifn.json"
            if os.path.exists(guifn_sidecar_path):
                try:
                    with open(guifn_sidecar_path, "r", encoding="utf-8") as f:
                        result["guifn_data"] = f.read()
                except OSError:
                    pass  # non-fatal -- the script itself still opened fine
            return result
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    def pick_openscad_path(self):
        """Native file picker for the Settings panel's 'OpenSCAD path'
        field. On macOS this is filtered to show .app bundles -- native
        Open panels (and Finder) present OpenSCAD.app as a single,
        non-navigable item rather than something you'd have to dig inside
        of to find the real executable, and the backend already knows how
        to resolve a .app path to the actual binary inside it (see
        openscad_cli._resolve_app_bundle). On Windows/Linux this filters
        to executables/all files instead, since there's no bundle concept
        there."""
        try:
            window = webview.windows[0]
            open_dialog = getattr(getattr(webview, "FileDialog", None), "OPEN", None)
            if open_dialog is None:
                open_dialog = webview.OPEN_DIALOG  # older pywebview versions
            if sys.platform == "darwin":
                file_types = ("Applications (*.app)", "All files (*.*)")
            elif sys.platform.startswith("win"):
                file_types = ("Executable files (*.exe)", "All files (*.*)")
            else:
                file_types = ("All files (*.*)",)
            chosen = window.create_file_dialog(open_dialog, file_types=file_types)
            if not chosen:
                return {"canceled": True}
            path = chosen[0] if isinstance(chosen, (list, tuple)) else chosen
            return {"path": path}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    # ---- 2D Sketch panel (frontend/sketch2d.html, loaded as an iframe) ----
    # See the class docstring above for why these exist here at all.

    def save_pdf(self, filename, b64data):
        window = webview.windows[0]
        result = window.create_file_dialog(
            webview.SAVE_DIALOG,
            directory=os.path.expanduser("~"),
            save_filename=filename or "sketch.pdf",
            file_types=("PDF Files (*.pdf)", "All files (*.*)"),
        )
        if not result:
            return None  # user cancelled
        # Different pywebview versions return either a bare path or a
        # 1-tuple/list containing it.
        path = result[0] if isinstance(result, (list, tuple)) else result
        if not path:
            return None
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64data))
        return path

    def save_sketch(self, filename, content):
        """Save a whole sketch (the JSON format sketch2d.html's own
        save/load uses) to a file the user picks via a real native Save
        dialog. `content` is plain text (JSON), not base64 -- unlike the
        PDF above, this is already just a string, so no encoding
        round-trip is needed to move it across the JS<->Python bridge."""
        window = webview.windows[0]
        result = window.create_file_dialog(
            webview.SAVE_DIALOG,
            directory=os.path.expanduser("~"),
            save_filename=filename or "sketch.json",
            file_types=("Sketch files (*.json)", "All files (*.*)"),
        )
        if not result:
            return None  # user cancelled
        path = result[0] if isinstance(result, (list, tuple)) else result
        if not path:
            return None
        if not path.lower().endswith((".json", ".sketch")):
            path += ".json"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def open_sketch(self):
        """Native Open dialog for loading (or combining in) a previously
        saved sketch. Returns {"path": ..., "content": ...} or None if the
        user cancelled -- sketch2d.html does the actual JSON parsing and
        entity merging (see its Open sketch / Combine sketch buttons)."""
        window = webview.windows[0]
        result = window.create_file_dialog(
            webview.OPEN_DIALOG,
            directory=os.path.expanduser("~"),
            file_types=("Sketch files (*.json;*.sketch)", "All files (*.*)"),
        )
        if not result:
            return None
        path = result[0] if isinstance(result, (list, tuple)) else result
        if not path:
            return None
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"path": path, "content": content}

    def export_drawing(self, filename, content, ext):
        """Native Save dialog for DXF/SVG export -- same reasoning as
        save_sketch() above. `ext` is 'dxf' or 'svg'; `content` is plain
        text either way (both formats are text, unlike the PDF export's
        binary/base64 path)."""
        window = webview.windows[0]
        ext = (ext or "dxf").lower().lstrip(".")
        label = "DXF" if ext == "dxf" else "SVG"
        result = window.create_file_dialog(
            webview.SAVE_DIALOG,
            directory=os.path.expanduser("~"),
            save_filename=filename or f"sketch.{ext}",
            file_types=(f"{label} files (*.{ext})", "All files (*.*)"),
        )
        if not result:
            return None
        path = result[0] if isinstance(result, (list, tuple)) else result
        if not path:
            return None
        if not path.lower().endswith("." + ext):
            path += "." + ext
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def import_drawing(self):
        """Native Open dialog for importing a DXF or SVG drawing. Returns
        {"path": ..., "content": ..., "ext": "dxf"|"svg"} or None if the
        user cancelled -- sketch2d.html picks /api/import_dxf vs
        /api/import_svg based on `ext` and feeds the result through the
        same mergeEntities() pipeline Combine-sketch already uses."""
        window = webview.windows[0]
        result = window.create_file_dialog(
            webview.OPEN_DIALOG,
            directory=os.path.expanduser("~"),
            file_types=("CAD drawings (*.dxf;*.svg)", "DXF files (*.dxf)", "SVG files (*.svg)", "All files (*.*)"),
        )
        if not result:
            return None
        path = result[0] if isinstance(result, (list, tuple)) else result
        if not path:
            return None
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"path": path, "content": content, "ext": ext}

    def copy_to_clipboard(self, text):
        """
        Writes `text` to the REAL system clipboard, from Python rather
        than the page's own JavaScript. Both "Copy to clipboard" buttons
        (the console's Copy button here, and the 2D Sketch panel's Export
        code Copy button in sketch2d.html) used to call
        navigator.clipboard.writeText() directly -- that call resolves
        successfully and the button shows "Copied" even when nothing
        actually reached the OS clipboard, because pywebview's embedded
        webview has JS clipboard ACCESS disabled by default on several
        backends (macOS's WKWebView needs the private
        javaScriptCanAccessClipboard/DOMPasteAllowed preferences
        pywebview doesn't set; see
        https://github.com/r0x0r/pywebview/issues/1561) -- so the paste a
        user then tries elsewhere comes up with whatever was on the
        clipboard before, not the copied text, and nothing in the UI ever
        indicated the write had silently failed.

        pyperclip (not tkinter) is used deliberately: this method runs on
        pywebview's own JS-bridge thread, not the main thread, and
        building a Tk() root off the main thread is unreliable-to-crashy
        on macOS's Cocoa. pyperclip instead shells out to each platform's
        own clipboard tool (pbcopy on macOS, a Win32 API call on Windows),
        neither of which cares which thread it's called from.

        Returns {"ok": True} on success or {"error": ...} if pyperclip
        isn't installed (or the platform copy tool it needs isn't
        available) -- the frontend falls back to the unreliable
        navigator.clipboard path in that case, since it's still better
        than nothing.
        """
        try:
            import pyperclip
            pyperclip.copy(text)
            return {"ok": True}
        except Exception as e:
            return {"error": str(e)}


def main():
    # Frozen builds keep their writable files (config, imports/) in the
    # per-user data folder, since the bundle itself is read-only. No-op
    # when running from source.
    if bundle_paths is not None:
        log_path = bundle_paths.start_logging()
        bundle_paths.redirect_writable_paths()
        if log_path:
            print(f"[SanPyCAD] logging this session to {log_path}")

    server.print_backend_status()
    port = find_free_port()
    httpd, port = server.serve(host="127.0.0.1", port=port)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    url = f"http://127.0.0.1:{port}/"
    wait_for_server(url)
    print(f"[SanPyCAD] backend running at {url}")

    def _fall_back_to_browser(reason):
        """Shared fallback: the app server itself is fine either way, so a
        pywebview failure is never fatal -- just less polished. Used both
        when pywebview isn't installed at all, and when it's installed but
        can't actually open a native window (e.g. on Windows, when the
        .NET/WebView2 runtime pywebview's winforms backend depends on is
        missing, blocked by antivirus, or otherwise broken on that
        machine -- that shows up as a RuntimeError/clr_loader failure, not
        an ImportError, which is why this is handled separately below)."""
        print(reason)
        webbrowser.open(url)
        print("[SanPyCAD] press Ctrl+C here to stop the app")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    try:
        global webview
        import webview
    except ImportError:
        _fall_back_to_browser(
            "[SanPyCAD] pywebview not installed -- opening your default "
            "browser instead. For a real app window, run: pip install pywebview"
        )
        httpd.shutdown()
        return

    try:
        api = Api()
        window = webview.create_window(
            "SanPyCAD", url, width=1400, height=900, min_size=(900, 600),
            js_api=api,
        )
        # debug=True enables "Inspect Element" in the app window, so JS
        # errors can be diagnosed the same way as in a regular browser if
        # something ever goes wrong -- but on some platforms/backends
        # (notably Windows' WebView2/EdgeChromium backend), it doesn't
        # just make that available on request: it pops the whole DevTools
        # panel open automatically, every single launch. That's a
        # developer/troubleshooting tool, not something anyone needs for
        # normal use, so it's off unless explicitly asked for.
        debug_mode = bool(os.environ.get("SANPYCAD_DEBUG"))
        webview.start(debug=debug_mode)
    except Exception as exc:
        # pywebview IS installed here, but failed to actually open a
        # native window -- on Windows this is almost always its winforms
        # backend failing to load the .NET/CLR runtime it needs (missing
        # or broken .NET Framework / WebView2 Runtime, or an antivirus
        # that quarantined part of the bundled pythonnet DLL). Rather
        # than crashing with a raw traceback, fall back to the browser so
        # the app is still usable, and say what's likely wrong.
        _fall_back_to_browser(
            f"[SanPyCAD] could not open the app window ({exc!r}) -- opening "
            "your default browser instead. This usually means Windows is "
            "missing (or has a broken) Microsoft Edge WebView2 Runtime or "
            ".NET Framework install; installing/repairing WebView2 from "
            "https://developer.microsoft.com/microsoft-edge/webview2/ "
            "and relaunching SanPyCAD should restore the native window."
        )

    httpd.shutdown()


if __name__ == "__main__":
    main()
