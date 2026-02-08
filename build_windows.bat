@echo off
echo ============================================
echo  Geneva Clinic - Windows Build
echo  (c) 2026 Rainberry Corp. All rights reserved.
echo  Created and Designed by Jesbert V. Jalandoni
echo ============================================
echo.

echo [1/3] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Building executable...
pyinstaller GenevaClinic.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [3/3] Build complete!
echo.
echo Executable is at: dist\GenevaClinic.exe
echo.
pause
