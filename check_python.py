# coding: utf-8
"""Quick check of which python.exe is actually running the app."""

import os
import sys

print("sys.executable :", sys.executable)
print("sys.version    :", sys.version)
print("cwd            :", os.getcwd())
print("WIZARD_PYTHON  :", os.environ.get("WIZARD_PYTHON", "<not set>"))

if sys.executable.lower().startswith(os.environ.get("LOCALAPPDATA", "\0").lower()):
    print("-> Running from the LOCAL cache (good).")
elif sys.executable.upper().startswith("P:"):
    print("-> Running directly from the NETWORK share (should be avoided).")
else:
    print("-> Running from an unrecognized location.")
