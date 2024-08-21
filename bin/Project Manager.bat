@echo off
setlocal enabledelayedexpansion

cd ..\

set "user_path=%USERPROFILE%\Documents\wizard\"
if not exist "%user_path%" (
    mkdir "%user_path%"
)

set "log_file=%user_path%\%RANDOM%.log"

python\python.exe app.py -project_manager >> "%log_file%" 2>&1

endlocal