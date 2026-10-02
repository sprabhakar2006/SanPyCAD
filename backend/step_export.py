"""
step_export.py -- loader stub. The exact-B-rep STEP (ISO 10303-21 / AP214)
exporter is shipped as encrypted source only, under
backend/_protected/step_export.enc -- see backend/_crypto_loader.py for
why and how, and build_protected_backend.py (in the main project folder,
not shipped here) for regenerating it after an edit.

Everything step_export.py exposes still works exactly the same via
`import step_export` -- this stub just hands the loading off
transparently.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _crypto_loader import load_protected  # noqa: E402

load_protected(__name__, os.path.abspath(__file__))
