::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdDiDJGqnxmsAHCdDRR6DLm+FVIkO7fvo4P+VoUgOaOs8d4HI5qOHOuEB7nrtdpkjmHNZl6s=
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSjk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdDiDJGqnxmsAHCdDRR6DLm+FVIkv7frt6vjJp1UYNA==
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
setlocal enabledelayedexpansion

set "user_path=%USERPROFILE%\Documents\wizard\"
if not exist "%user_path%" (
    mkdir "%user_path%"
)

set "log_file=%user_path%\main.log"
set "temp_log_file=%user_path%\temp_main_%RANDOM%.log"

python\python.exe >> "%temp_log_file%" 2>&1

if exist "%log_file%" (
    type "%temp_log_file%" >> "%log_file%"
    del "%temp_log_file%"
) else (
    ren "%temp_log_file%" "%log_file%"
)

endlocal