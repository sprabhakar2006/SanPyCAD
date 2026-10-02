"""
brep_bridge.py

"Send to SanPyCAD-Brep" -- the one-click bridge that hands the shape(s)
currently in SanPyCAD's own editor over to the separate SanPyCAD-Brep
app (a different desktop process, build123d/OCCT-backed) so they can be
opened there as REAL B-rep solids and kept editing (fillets, chamfers,
booleans, STEP export, etc.) -- rather than staying the tessellated
triangle mesh this app itself is built on.

Two apps, two separate processes, no shared server, no recorded port,
and no OS file-association wired up between them (checked directly) --
so this necessarily works by (1) writing the current shape out as a
real STEP file (already exact B-rep, not a re-tessellation -- the same
code path "Export as STEP" uses, see app.py's Api.send_to_brep()), then
(2) launching a brand-new SanPyCAD-Brep process pointed at that file.

Remembering WHERE SanPyCAD-Brep is installed (its .app bundle on macOS,
its .vbs/.bat launcher on Windows, or its app.py for a from-source/
Linux install) reuses openscad_cli.py's existing sanpycad_config.json
settings file and its already-frozen-build-aware _config_path()/
_read_config() helpers, rather than inventing a second settings file --
one JSON file, one place it lives (and one place bundle_paths.py
already knows to relocate for a packaged build), just a new key in it.
"""

import json
import os
import platform
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

import openscad_cli as _oc

# Where a running SanPyCAD-Brep instance records its own port -- written
# by that app's own main() at startup (see SanPyCAD-Brep/app.py). Same
# fixed OS-temp-dir path on both sides since neither app knows the
# other's install location up front.
INSTANCE_REGISTRY_PATH = os.path.join(tempfile.gettempdir(), "sanpycad_brep_instance.json")


def get_brep_app_path():
    """The SanPyCAD-Brep install location remembered from a previous
    'Send to SanPyCAD-Brep' (or set directly via pick_brep_app_path()),
    or None if the user has never been asked yet (or cleared it)."""
    return _oc._read_config().get("brep_app_path") or None


def set_brep_app_path(path):
    """Persist `path` (or clear it, if falsy) to sanpycad_config.json --
    same file, same helpers openscad_cli.py's own OpenSCAD path uses."""
    data = _oc._read_config()
    data["brep_app_path"] = path or None
    with open(_oc._config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _resolve_mac_bundle_executable(app_path):
    """macOS only: given a SanPyCAD Brep.app bundle, find the real
    executable inside Contents/MacOS/ to run directly (bypassing `open
    -a`, which does not reliably hand a custom environment variable
    through to the app it launches -- see launch_brep()'s docstring)."""
    macos_dir = os.path.join(app_path, "Contents", "MacOS")
    name = None
    try:
        import plistlib
        with open(os.path.join(app_path, "Contents", "Info.plist"), "rb") as f:
            plist = plistlib.load(f)
        name = plist.get("CFBundleExecutable")
    except Exception:
        pass
    if name:
        candidate = os.path.join(macos_dir, name)
        if os.path.isfile(candidate):
            return candidate
    # Fall back to guessing from the bundle's own name (matches how
    # this project's own .app bundles are actually built: "SanPyCAD
    # Brep.app" -> "Contents/MacOS/SanPyCAD Brep").
    base = os.path.basename(app_path.rstrip("/"))
    if base.lower().endswith(".app"):
        guess = os.path.join(macos_dir, base[:-len(".app")])
        if os.path.isfile(guess):
            return guess
    if os.path.isdir(macos_dir):
        for fname in sorted(os.listdir(macos_dir)):
            candidate = os.path.join(macos_dir, fname)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
    raise FileNotFoundError(f"Could not find an executable inside {app_path!r}")


def launch_brep(step_path, brep_path):
    """Starts a new SanPyCAD-Brep process and hands it `step_path` (an
    already-written .step file this function doesn't create itself --
    see app.py's Api.send_to_brep()) to auto-import on startup.

    Why an environment variable and not a command-line argument: the
    two apps are entirely separate processes with no shared server, no
    recorded port, and no OS file-association wired up between them --
    so a NEW process has to be started either way, and SanPyCAD-Brep's
    own launchers (the macOS .app's two nested shell scripts, the
    Windows .vbs's shell.Run call and the .bat's plain `python app.py`,
    and a bare `python3 app.py`) already forward the parent process's
    environment straight through to the eventual `python app.py`
    without any changes needed -- none of them touch argv today.
    Teaching every one of those to also thread a positional file
    argument through multiple exec/shell.Run hops would mean editing
    each launcher script and trusting every one (including any a user
    might have customized) to keep forwarding "$@"/%* correctly
    forever after. An env var only needs SanPyCAD-Brep's own app.py to
    read it once, in one place -- see that file's main().

    `brep_path` is whatever pick_brep_app_path() returned and
    set_brep_app_path() persisted: a macOS .app bundle, a Windows
    .vbs/.bat launcher, a bare app.py, or a folder containing one.
    Raises on anything that doesn't resolve to something runnable --
    callers should catch that and surface it as an ordinary error
    rather than a silent no-op relaunch.
    """
    env = dict(os.environ)
    env["SANPYCAD_BREP_IMPORT"] = step_path

    system = platform.system()
    normalized = brep_path.rstrip("/\\")

    if system == "Darwin" and normalized.lower().endswith(".app") and os.path.isdir(normalized):
        exe = _resolve_mac_bundle_executable(normalized)
        subprocess.Popen([exe], env=env, close_fds=True)
        return

    if system == "Windows" and normalized.lower().endswith(".vbs"):
        subprocess.Popen(["wscript.exe", normalized], env=env,
                          cwd=os.path.dirname(normalized), close_fds=True)
        return

    if system == "Windows" and normalized.lower().endswith((".bat", ".cmd")):
        subprocess.Popen([normalized], env=env, cwd=os.path.dirname(normalized),
                          shell=True, close_fds=True)
        return

    # Fallback: a bare app.py path, or a folder containing one -- covers
    # a from-source install, Linux (no packaged launcher exists there
    # yet), or a user who picked something unexpected. Run it directly
    # with this same process's own Python interpreter.
    app_py = normalized
    if os.path.isdir(normalized):
        app_py = os.path.join(normalized, "app.py")
    if not os.path.isfile(app_py):
        raise FileNotFoundError(
            f"Don't know how to launch SanPyCAD Brep from {brep_path!r} "
            f"-- expected a .app bundle, a .vbs/.bat launcher, or app.py."
        )
    subprocess.Popen([sys.executable, app_py], env=env,
                      cwd=os.path.dirname(app_py), close_fds=True)


def find_running_instance(timeout=0.5):
    """Returns the port number of an already-running SanPyCAD-Brep
    instance, or None if none is found.

    The registry file alone isn't trustworthy -- a previous instance
    that crashed or was killed rather than exiting cleanly could leave
    a stale entry behind (its atexit cleanup never ran). So this always
    makes a short, live HTTP GET to that port's own /status route and
    only trusts it if the response actually identifies itself as
    SanPyCAD-Brep -- a step that also naturally handles "the port got
    reused by some unrelated process in the meantime".
    """
    try:
        with open(INSTANCE_REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        port = int(data.get("port"))
    except Exception:
        return None

    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/status")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

    if body.get("app") != "sanpycad-brep":
        return None
    return port


def send_to_running_instance(port, step_path, names, shape_kinds=None, timeout=2.0,
                              script_code=None):
    """POSTs the newly-exported STEP file + original variable names +
    each body's actual solid/surface kind to an already-running
    SanPyCAD-Brep instance's /import_from_sanpycad route.

    `script_code`, if given, is the newer, preferred handoff: the exact
    SanPyCAD script text to run directly in Brep instead of a STEP
    file (see app.py's send_to_brep()/_build_brep_script() for why --
    ocad.py is already flattened into Brep's own namespace, so this
    reproduces the shape natively with none of a STEP round-trip's
    cost). When given, `step_path`/`names`/`shape_kinds` are ignored
    server-side (see server.py's /import_from_sanpycad) and may be
    None/empty.

    This only stages the import server-side (bumps the generation
    counter the running instance's frontend polls for via
    /pending_import_check) -- it does NOT touch that instance's editor
    directly. If that editor currently has unsaved changes, its own
    frontend is what asks the user whether to save or discard them
    before actually loading the new shape in; that decision naturally
    belongs on that side since that's the editor (and the save button)
    the user would be looking at. Raises on any HTTP/network failure --
    callers should fall back to launch_brep() (spawn a new instance) in
    that case.

    `shape_kinds` -- {name: 'solid'|'surface'}, from step_export.py's
    last_shape_kinds() -- is the GROUND TRUTH of what each body actually
    got written as (not just what was asked for), so Brep's own starter-
    script generator can deterministically sort .solids()/.shells() back
    into the right names instead of re-guessing from geometry, which
    can't tell a Shell from a Solid apart reliably and previously
    silently dropped/misassigned one when both shared a Compound."""
    payload = json.dumps({
        "step_path": step_path,
        "names": names or [],
        "shape_kinds": shape_kinds or {},
        "script_code": script_code,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/import_from_sanpycad",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = {}
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            pass
        body.setdefault("error", f"HTTP {e.code}")
        body["status_code"] = e.code
        return body
