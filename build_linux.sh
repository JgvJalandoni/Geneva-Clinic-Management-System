#!/bin/bash
echo "============================================"
echo " Geneva Clinic - Linux Build"
echo " © 2026 Rainberry Corp. All rights reserved."
echo " Created and Designed by Jesbert V. Jalandoni"
echo "============================================"
echo

echo "[1/5] Installing dependencies..."
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
echo "[2/5] Building executable..."
pyinstaller GenevaClinic.spec --clean --noconfirm
if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

chmod +x dist/GenevaClinic

echo
echo "[3/5] Creating .desktop launcher..."
DIST_DIR="$(cd dist && pwd)"
cat > dist/GenevaClinic.desktop << DESKTOP_EOF
[Desktop Entry]
Name=Geneva Clinic
Comment=Geneva Clinic Management System
Exec=${DIST_DIR}/GenevaClinic
Path=${DIST_DIR}
Terminal=false
Type=Application
Categories=Office;MedicalSoftware;
StartupNotify=true
X-GNOME-Autostart-enabled=true
DESKTOP_EOF
chmod +x dist/GenevaClinic.desktop

echo
echo "[4/5] Installing launcher & autostart..."
mkdir -p ~/.local/share/applications
mkdir -p ~/.config/autostart
cp dist/GenevaClinic.desktop ~/.local/share/applications/GenevaClinic.desktop
cp dist/GenevaClinic.desktop ~/.config/autostart/GenevaClinic.desktop
echo "  -> Installed to app menu (~/.local/share/applications/)"
echo "  -> Installed to autostart (~/.config/autostart/)"

echo
echo "[5/5] Build complete!"
echo
echo "Executable is at: dist/GenevaClinic"
echo "Geneva Clinic will now launch automatically on login."
echo
echo "To disable autostart, run:"
echo "  rm ~/.config/autostart/GenevaClinic.desktop"
echo
echo "Run it manually with: ./dist/GenevaClinic"
