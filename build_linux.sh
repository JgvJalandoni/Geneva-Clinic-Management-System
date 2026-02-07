#!/bin/bash
echo "============================================"
echo " Geneva Clinic - Linux Build"
echo " Made by Rainberry Corp."
echo " Designed by Jesbert V. Jalandoni"
echo "============================================"
echo

echo "[1/3] Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Make sure you have python3-tk installed:"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    echo "  Arch: sudo pacman -S tk"
    exit 1
fi

echo
echo "[2/3] Building executable..."
pyinstaller GenevaClinic.spec --clean --noconfirm
if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

chmod +x dist/GenevaClinic

echo
echo "[3/3] Build complete!"
echo
echo "Executable is at: dist/GenevaClinic"
echo "Run it with: ./dist/GenevaClinic"
