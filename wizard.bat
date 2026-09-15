@echo off
setlocal enabledelayedexpansion

rem Running python.exe directly off the network share causes random
rem access violation crashes (DLLs mapped over SMB). Instead, mirror the
rem python/ folder to a local disk cache and run it from there, keeping
rem this network share as the single source of truth for updates.
rem robocopy only transfers files that are missing or different, so this
rem is cheap to run on every launch.

set "LOCAL_CACHE=%LOCALAPPDATA%\wizard\python"

robocopy "python" "%LOCAL_CACHE%" /MIR /R:2 /W:1 /NFL /NDL /NJH /NJS
if !errorlevel! GEQ 8 (
    echo Failed to sync local python cache, falling back to network python.
    set "LOCAL_CACHE=python"
)

rem Exposed so the app's own restart/PyWizard launch code reuses the local python
set "WIZARD_PYTHON=%LOCAL_CACHE%\python.exe"

"%LOCAL_CACHE%\python.exe" app.py