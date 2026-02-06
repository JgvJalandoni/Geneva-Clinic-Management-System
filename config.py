"""
Configuration file for Tita's Clinic Management System
Contains all constants, color schemes, and application settings
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
    # Backgrounds - Soft whites with warm tint to reduce glare
    'bg_dark': '#f5f7fa',           # Soft light gray (main background)
    'bg_card': '#ffffff',           # Pure white (cards)
    'bg_card_hover': '#e8f4f8',     # Light blue hover (gentle feedback)
    
    # Accents - High contrast, saturated colors for clarity
    'accent_blue': '#0066cc',       # Strong blue (primary actions)
    'accent_green': '#28a745',      # Vibrant green (success/positive)
    'accent_red': '#dc3545',        # Clear red (warnings/alerts)
    'accent_orange': '#fd7e14',     # Bright orange (secondary actions)
    'accent_purple': '#6f42c1',     # Purple (special items)
    
    # Text - High contrast black for readability
    'text_primary': '#1a1a1a',      # Near-black (main text)
    'text_secondary': '#6c757d',    # Medium gray (secondary text)
    'text_muted': '#999999',        # Light gray (hints/placeholders)
    
    # Borders - Subtle but visible
    'border': '#dee2e6',            # Light gray border
    'border_focus': '#80bdff',      # Blue border for focused elements
    
    # Status colors - Clear visual feedback
    'status_success': '#d4edda',    # Light green background
    'status_warning': '#fff3cd',    # Light yellow background
    'status_danger': '#f8d7da',     # Light red background
    'status_info': '#d1ecf1',       # Light blue background
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