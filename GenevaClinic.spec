# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Geneva Clinic Management System
# Made by Rainberry Corp. | Designed by Jesbert V. Jalandoni

import os
import sys

block_cipher = None

# Get customtkinter path
import customtkinter
ctk_path = os.path.dirname(customtkinter.__file__)

# Get Pillow path (required by customtkinter)
try:
    import PIL
    pil_path = os.path.dirname(PIL.__file__)
    pil_data = [(pil_path, 'PIL')]
except ImportError:
    pil_data = []

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        (ctk_path, 'customtkinter'),
    ] + pil_data,
    hiddenimports=[
        'customtkinter',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        '_tkinter',
        'sqlite3',
        'hashlib',
        'csv',
        'shutil',
        'webbrowser',
        'datetime',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GenevaClinic',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False if sys.platform == 'win32' else True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=None,
)
