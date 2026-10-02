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
import os
import sys
import socket
import threading
import time
import traceback
import webbrowser

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

    try:
        global webview
        import webview
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
    except ImportError:
        print("[SanPyCAD] pywebview not installed -- opening your default "
              "browser instead. For a real app window, run: pip install pywebview")
        webbrowser.open(url)
        print("[SanPyCAD] press Ctrl+C here to stop the app")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    httpd.shutdown()


if __name__ == "__main__":
    main()
