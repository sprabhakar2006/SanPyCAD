"""
openscad_cli.py -- loader stub. The real-OpenSCAD-binary bridge (STL/SVG export, .scad rendering) is shipped as encrypted source only,
under backend/_protected/openscad_cli.enc -- see backend/_crypto_loader.py for
why and how, and build_protected_backend.py (in the main project
folder, not shipped here) for regenerating it after an edit.

Everything openscad_cli.py has always exposed still works exactly the same
via `import openscad_cli` -- this stub just hands the loading off
transparently.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _crypto_loader import load_protected  # noqa: E402

load_protected(__name__, os.path.abspath(__file__))
