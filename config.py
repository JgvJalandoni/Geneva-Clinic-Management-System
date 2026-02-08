"""
Configuration file for Geneva Clinic Management System
© 2026 Rainberry Corp. All rights reserved. Created and Designed by Jesbert V. Jalandoni
https://jalandoni.jesbert.cloud/
"""

import customtkinter as ctk

# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Database
DB_NAME = "clinic_database.db"

# Window Settings
WINDOW_TITLE = "Geneva Clinic Management System"
WINDOW_SIZE = "1400x900"
WINDOW_MIN_SIZE = (1200, 700)

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE - BRIGHT & EYE-FRIENDLY FOR ACCESSIBILITY
# Optimized for older users with high contrast and reduced eye strain
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    # Backgrounds - Modern clean look
    'bg_dark': '#f0f4f8',           # Cool light gray (main background)
    'bg_card': '#ffffff',           # Pure white (cards)
    'bg_card_hover': '#f8fafc',     # Very light hover

    # Accents - Modern vibrant colors
    'accent_blue': '#3b82f6',       # Modern blue (primary actions)
    'accent_green': '#22c55e',      # Fresh green (success/positive)
    'accent_red': '#ef4444',        # Modern red (warnings/alerts)
    'accent_orange': '#f97316',     # Warm orange (encoding/special)
    'accent_purple': '#8b5cf6',     # Soft purple (special items)

    # Text - Clean readable contrast
    'text_primary': '#1e293b',      # Slate dark (main text)
    'text_secondary': '#64748b',    # Slate medium (secondary text)
    'text_muted': '#94a3b8',        # Slate light (hints/placeholders)

    # Borders - Subtle
    'border': '#e2e8f0',            # Light slate border
    'border_focus': '#3b82f6',      # Blue border for focused elements

    # Status colors
    'status_success': '#dcfce7',    # Light green background
    'status_warning': '#fef3c7',    # Light yellow background
    'status_danger': '#fee2e2',     # Light red background
    'status_info': '#dbeafe',       # Light blue background
}

# ═══════════════════════════════════════════════════════════════════════════════
# UI CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Font Configurations
FONTS = {
    'header_large': ("Segoe UI", 40),
    'header': ("Segoe UI", 24, "bold"),
    'subheader': ("Segoe UI", 18, "bold"),
    'title': ("Segoe UI", 16, "bold"),
    'body': ("Segoe UI", 12),
    'body_bold': ("Segoe UI", 12, "bold"),
    'small': ("Segoe UI", 11),
    'small_bold': ("Segoe UI", 11, "bold"),
    'tiny': ("Segoe UI", 10),
    'button': ("Segoe UI", 13, "bold"),
    'button_large': ("Segoe UI", 14, "bold"),
    'mono': ("Consolas", 13),
}

# Widget Heights
HEIGHTS = {
    'header': 80,
    'footer': 40,
    'button': 40,
    'button_large': 45,
    'button_xl': 50,
    'entry': 40,
    'entry_small': 35,
    'entry_large': 45,
}

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