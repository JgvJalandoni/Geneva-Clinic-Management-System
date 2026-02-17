#!/bin/bash
echo "============================================"
echo " Geneva Clinic - Linux Build"
echo " © 2026 Rainberry Corp. All rights reserved."
echo " Created and Designed by Jesbert V. Jalandoni"
echo "============================================"
echo

echo "[1/6] Checking system dependencies..."
# Verify python3-tk is installed (required for tkinter)
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: python3-tk is not installed!"
    echo "Install it with:"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    echo "  Arch: sudo pacman -S tk"
    exit 1
fi
echo "  -> python3-tk OK"

# Verify _tkinter C extension
python3 -c "import _tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: _tkinter C extension not found!"
    echo "Install it with:"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    exit 1
fi
echo "  -> _tkinter OK"

echo
echo "[2/6] Installing Python dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "[3/6] Building executable..."
pyinstaller GenevaClinic.spec --clean --noconfirm
if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

chmod +x dist/GenevaClinic

echo
echo "[4/6] Creating wrapper script..."
# Create a wrapper script that sets up the environment properly
cat > dist/run_clinic.sh << 'WRAPPER_EOF'
#!/bin/bash
# Wrapper script for Geneva Clinic - ensures proper environment
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure DISPLAY is set (needed for X11/Wayland)
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    export DISPLAY=:0
fi

# Run the application, log errors to file for debugging
exec "$SCRIPT_DIR/GenevaClinic" "$@" 2>"$SCRIPT_DIR/clinic_error.log"
WRAPPER_EOF
chmod +x dist/run_clinic.sh

echo
echo "[5/6] Creating .desktop launcher..."
DIST_DIR="$(cd dist && pwd)"
cat > dist/GenevaClinic.desktop << DESKTOP_EOF
[Desktop Entry]
Name=Geneva Clinic
Comment=Geneva Clinic Management System
Exec=${DIST_DIR}/run_clinic.sh
Path=${DIST_DIR}
Terminal=false
Type=Application
Categories=Office;MedicalSoftware;
StartupNotify=true
X-GNOME-Autostart-enabled=true
DESKTOP_EOF
chmod +x dist/GenevaClinic.desktop

echo
echo "[6/6] Installing launcher & autostart..."
mkdir -p ~/.local/share/applications
mkdir -p ~/.config/autostart
cp dist/GenevaClinic.desktop ~/.local/share/applications/GenevaClinic.desktop
cp dist/GenevaClinic.desktop ~/.config/autostart/GenevaClinic.desktop
echo "  -> Installed to app menu (~/.local/share/applications/)"
echo "  -> Installed to autostart (~/.config/autostart/)"

echo
echo "Build complete!"
echo
echo "Executable is at: dist/GenevaClinic"
echo "Wrapper script:   dist/run_clinic.sh"
echo "Geneva Clinic will now launch automatically on login."
echo
echo "To disable autostart, run:"
echo "  rm ~/.config/autostart/GenevaClinic.desktop"
echo
echo "Run it manually with: ./dist/run_clinic.sh"
echo
echo "If the app doesn't start, check: dist/clinic_error.log"
