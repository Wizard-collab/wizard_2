@echo off
setlocal enabledelayedexpansion

set "user_path=%USERPROFILE%\Documents\wizard\"
if not exist "%user_path%" (
    mkdir "%user_path%"
)

set "log_file=%user_path%\%RANDOM%.log"

python\python.exe create_repository.py >> "%log_file%" 2>&1

endlocal