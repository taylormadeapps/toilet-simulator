@echo off
echo ========================================
echo   TOILET SIMULATOR - Starting up...
echo ========================================
echo.

REM Try python, then py (Windows launcher), then python3
set PYTHON_CMD=
where python >nul 2>&1 && set PYTHON_CMD=python
if not defined PYTHON_CMD (
    where py >nul 2>&1 && set PYTHON_CMD=py
)
if not defined PYTHON_CMD (
    where python3 >nul 2>&1 && set PYTHON_CMD=python3
)
if not defined PYTHON_CMD (
    echo ERROR: Python is not installed or not in PATH.
    echo Install Python 3.12+ from https://python.org
    echo Make sure to tick "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo Found Python: %PYTHON_CMD%
%PYTHON_CMD% --version

REM Install/update dependencies using python -m pip (always works if Python is found)
echo.
echo Installing dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo pip failed. Trying to install pip first...
    %PYTHON_CMD% -m ensurepip --upgrade
    %PYTHON_CMD% -m pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies.
        echo Try running: %PYTHON_CMD% -m pip install pygame-ce
        pause
        exit /b 1
    )
)

echo.
echo Launching Toilet Simulator...
echo.
%PYTHON_CMD% src/main.py
if errorlevel 1 (
    echo.
    echo Game crashed! Check the error above.
    pause
)
