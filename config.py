"""
Configuration file for Geneva Clinic Management System
© 2026 Rainberry Corp. All rights reserved. Created and Designed by Jesbert V. Jalandoni
https://jalandoni.jesbert.cloud/
"""

import sys
import customtkinter as ctk

# Cross-platform font family
if sys.platform.startswith('linux'):
    FONT_FAMILY = "DejaVu Sans"
    MONO_FAMILY = "DejaVu Sans Mono"
elif sys.platform == 'darwin':
    FONT_FAMILY = "Helvetica Neue"
    MONO_FAMILY = "Menlo"
else:
    FONT_FAMILY = "Segoe UI"
    MONO_FAMILY = "Consolas"

# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def get_color(key):
    """Get single color value for current appearance mode (for ttk widgets that don't support tuples)"""
    val = COLORS[key]
    if isinstance(val, tuple):
        return val[1] if ctk.get_appearance_mode() == "Dark" else val[0]
    return val

# Database
DB_NAME = "clinic_database.db"

# Window Settings
WINDOW_TITLE = "Geneva Clinic Management System"
WINDOW_SIZE = "1400x900"
WINDOW_MIN_SIZE = (1200, 700)

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE - WARM & EYE-FRIENDLY FOR ACCESSIBILITY
# Muted earth-tone accents with warm neutrals for reduced eye strain
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    # Backgrounds — (light, dark)
    'bg_dark':        ('#f5f3f0', '#1c1c1e'),
    'bg_card':        ('#ffffff', '#2c2c2e'),
    'bg_card_hover':  ('#faf8f6', '#3a3a3c'),

    # Accents — slightly brighter in dark mode for visibility
    'accent_blue':    ('#4a7ccc', '#6a9fd8'),
    'accent_green':   ('#3a9e6e', '#5abb8a'),
    'accent_red':     ('#d94f4f', '#e67373'),
    'accent_orange':  ('#d98a3d', '#e8a960'),
    'accent_purple':  ('#7a6bbf', '#9a8dd4'),

    # Text — inverted for dark mode
    'text_primary':   ('#2c2c2e', '#e5e5e7'),
    'text_secondary': ('#6b6b6e', '#a1a1a3'),
    'text_muted':     ('#a0a0a3', '#6c6c6e'),

    # Borders
    'border':         ('#e5e2de', '#3a3a3c'),
    'border_focus':   ('#4a7ccc', '#6a9fd8'),

    # Status colors — dark tints for dark mode
    'status_success': ('#e2f5e9', '#1a3328'),
    'status_warning': ('#fef5e0', '#332a1a'),
    'status_danger':  ('#fce5e5', '#331a1a'),
    'status_info':    ('#e4ecf7', '#1a2533'),

    # Hover colors
    'hover_blue':     ('#3a6ab5', '#5889c0'),
    'hover_green':    ('#2e8a5c', '#4aa87a'),
    'hover_red':      ('#bf3f3f', '#d06060'),
    'hover_orange':   ('#c27530', '#d09050'),
    'hover_purple':   ('#665aaa', '#8880c0'),
}

# ═══════════════════════════════════════════════════════════════════════════════
# UI CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Font Configurations (base values before scaling)
BASE_FONTS = {
    'header_large': (FONT_FAMILY, 40),
    'header': (FONT_FAMILY, 24, "bold"),
    'subheader': (FONT_FAMILY, 18, "bold"),
    'title': (FONT_FAMILY, 16, "bold"),
    'body': (FONT_FAMILY, 12),
    'body_bold': (FONT_FAMILY, 12, "bold"),
    'small': (FONT_FAMILY, 11),
    'small_bold': (FONT_FAMILY, 11, "bold"),
    'tiny': (FONT_FAMILY, 10),
    'button': (FONT_FAMILY, 13, "bold"),
    'button_large': (FONT_FAMILY, 14, "bold"),
    'mono': (MONO_FAMILY, 13),
}

# Widget Heights (base values before scaling)
BASE_HEIGHTS = {
    'header': 80,
    'footer': 40,
    'button': 40,
    'button_large': 45,
    'button_xl': 50,
    'entry': 40,
    'entry_small': 35,
    'entry_large': 45,
}

# These get overwritten by apply_scaling() at startup
FONTS = dict(BASE_FONTS)
HEIGHTS = dict(BASE_HEIGHTS)
SCALE_FACTOR = 1.0


def get_scale_factor(root):
    """Calculate UI scale factor based on screen resolution.
    Base resolution: 1920x1080 = scale 1.0
    Larger screens get bigger UI, smaller screens get smaller UI.
    """
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    scale = min(sw / 1920, sh / 1080)
    return max(scale, 0.8)  # minimum 0.8 so tiny screens stay usable


def apply_scaling(root):
    """Apply resolution-based scaling to FONTS and HEIGHTS. Call after root window is created."""
    global FONTS, HEIGHTS, SCALE_FACTOR
    scale = get_scale_factor(root)
    SCALE_FACTOR = scale
    FONTS = {}
    for k, v in BASE_FONTS.items():
        size = max(int(v[1] * scale), 8)
        if len(v) > 2:
            FONTS[k] = (v[0], size, v[2])
        else:
            FONTS[k] = (v[0], size)
    HEIGHTS = {k: max(int(v * scale), 20) for k, v in BASE_HEIGHTS.items()}
    return scale

# Validation Ranges
VALIDATION = {
    'weight_min': 0.5,
    'weight_max': 300,
    'height_min': 30,
    'height_max': 250,
    'temp_min': 35,
    'temp_max': 42,
    'contact_min_length': 10,
    'contact_max_length': 11,
    'name_min_length': 2,
}

# Date/Time Formats
DATETIME_FORMATS = {
    'date_input': "%Y-%m-%d",
    'date_display': "%b %d, %Y",
    'time_12hr': "%I:%M %p",
    'time_24hr': "%H:%M:%S",
    'timestamp': "%Y-%m-%d %H:%M:%S",
    'timestamp_display': "%I:%M:%S %p",
    'backup_filename': "%Y%m%d_%H%M%S",
    'export_filename': "%Y%m%d",
}