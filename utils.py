"""
Utility functions for Tita's Clinic Management System
Handles date/time formatting, parsing, and validation
"""

import datetime
from typing import Optional
from config import DATETIME_FORMATS, VALIDATION


# ═══════════════════════════════════════════════════════════════════════════════
# DATE/TIME FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════

def format_time_12hr(time_24hr: str) -> str:
    """
    Convert 24-hour time to 12-hour format with AM/PM
    
    Args:
        time_24hr: Time string in HH:MM:SS format
        
    Returns:
        Formatted time string (e.g., "02:30 PM") or "—" if invalid
    """
    if not time_24hr:
        return "—"
    try:
        time_obj = datetime.datetime.strptime(time_24hr, DATETIME_FORMATS['time_24hr'])
        return time_obj.strftime(DATETIME_FORMATS['time_12hr'])
    except (ValueError, TypeError):
        return time_24hr


def format_timestamp(timestamp_str: str) -> str:
    """
    Format created_at timestamp for display
    
    Args:
        timestamp_str: SQLite timestamp string
        
    Returns:
        Formatted timestamp (e.g., "02:30:45 PM") or "—" if invalid
    """
    if not timestamp_str:
        return "—"
    try:
        # Parse SQLite timestamp format
        dt = datetime.datetime.strptime(timestamp_str, DATETIME_FORMATS['timestamp'])
        return dt.strftime(DATETIME_FORMATS['timestamp_display'])
    except (ValueError, TypeError):
        # Try alternate format
        try:
            dt = datetime.datetime.fromisoformat(timestamp_str)
            return dt.strftime(DATETIME_FORMATS['timestamp_display'])
        except (ValueError, TypeError):
            return timestamp_str


def parse_time_input(time_str: str) -> Optional[str]:
    """
    Parse user time input and convert to 24-hour format
    
    Accepts multiple input formats:
    - 12-hour: "02:30 PM", "2:30PM", "2 PM", "2PM"
    - 24-hour: "14:30", "14:30:00"
    
    Args:
        time_str: User input time string
        
    Returns:
        Time in HH:MM:SS format or None if invalid
    """
    if not time_str:
        return None
    
    time_str = time_str.strip()
    
    # Try 12-hour format first (e.g., "02:30 PM")
    for fmt in ["%I:%M %p", "%I:%M%p", "%I %p", "%I%p"]:
        try:
            dt = datetime.datetime.strptime(time_str, fmt)
            return dt.strftime(DATETIME_FORMATS['time_24hr'])
        except ValueError:
            continue

    # Try 24-hour format (e.g., "14:30")
    for fmt in ["%H:%M", "%H:%M:%S"]:
        try:
            dt = datetime.datetime.strptime(time_str, fmt)
            return dt.strftime(DATETIME_FORMATS['time_24hr'])
        except ValueError:
            continue
    
    return None


def get_current_date() -> str:
    """
    Get current date in MM/DD/YYYY format for UI
    
    Returns:
        Current date string
    """
    return datetime.date.today().strftime("%m/%d/%Y")


def get_current_time_12hr() -> str:
    """
    Get current time in 12-hour format
    
    Returns:
        Current time string (e.g., "02:30 PM")
    """
    return datetime.datetime.now().strftime(DATETIME_FORMATS['time_12hr'])


def get_current_time_24hr() -> str:
    """
    Get current time in 24-hour format
    
    Returns:
        Current time string in HH:MM:SS format
    """
    return datetime.datetime.now().strftime(DATETIME_FORMATS['time_24hr'])


def get_backup_timestamp() -> str:
    """
    Get timestamp for backup filenames
    
    Returns:
        Timestamp string (e.g., "20240206_143045")
    """
    return datetime.datetime.now().strftime(DATETIME_FORMATS['backup_filename'])


def get_export_timestamp() -> str:
    """
    Get timestamp for export filenames
    
    Returns:
        Timestamp string (e.g., "20240206")
    """
    return datetime.datetime.now().strftime(DATETIME_FORMATS['export_filename'])


def ui_date_to_db(date_str: str) -> Optional[str]:
    """Convert MM/DD/YYYY to YYYY-MM-DD"""
    if not date_str: return None
    try:
        dt = datetime.datetime.strptime(date_str, "%m/%d/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        # Fallback if already in DB format or other
        try:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None


def db_date_to_ui(date_str: str) -> str:
    """Convert YYYY-MM-DD to MM/DD/YYYY"""
    if not date_str: return ""
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%m/%d/%Y")
    except ValueError:
        return date_str


def format_time_parts(time_24hr: str) -> tuple[str, str, str]:
    """
    Split a 24-hour time string into (hour, minute, ampm) for UI pickers.
    
    Args:
        time_24hr: Time in HH:MM:SS format
        
    Returns:
        Tuple of (HH, MM, AM/PM)
    """
    if not time_24hr:
        now = datetime.datetime.now()
        return now.strftime("%I"), f"{(now.minute // 5) * 5:02d}", now.strftime("%p")
    
    try:
        dt = datetime.datetime.strptime(time_24hr, DATETIME_FORMATS['time_24hr'])
        return dt.strftime("%I"), dt.strftime("%M"), dt.strftime("%p")
    except (ValueError, TypeError):
        now = datetime.datetime.now()
        return now.strftime("%I"), f"{(now.minute // 5) * 5:02d}", now.strftime("%p")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════

def format_phone_number(phone: str) -> str:
    """
    Format phone number to 4-3-4 format: 0995 647 7081
    """
    if not phone:
        return "—"
    
    # Remove all non-digit characters
    digits = "".join(filter(str.isdigit, phone))
    
    if len(digits) == 11:
        return f"{digits[:4]} {digits[4:7]} {digits[7:]}"
    elif len(digits) == 10:
        # Assume missing leading zero
        digits = "0" + digits
        return f"{digits[:4]} {digits[4:7]} {digits[7:]}"
    
    return phone


def format_reference_number(ref: any) -> str:
    """
    Format reference number to 00-00-00 display format
    """
    if ref is None:
        return "—"
    
    # Ensure it's a string of at least 6 digits
    ref_str = str(ref).zfill(6)
    
    if len(ref_str) == 6:
        return f"{ref_str[:2]}-{ref_str[2:4]}-{ref_str[4:]}"
    
    return ref_str


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def validate_date(date_str: str) -> tuple[bool, str]:
    """
    Validate date string format (expects MM/DD/YYYY)
    
    Args:
        date_str: Date string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not date_str:
        return False, "Date is required"
    
    try:
        datetime.datetime.strptime(date_str, "%m/%d/%Y")
        return True, ""
    except ValueError:
        # Check if it's already in DB format (YYYY-MM-DD)
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return True, ""
        except ValueError:
            return False, "Invalid date format. Use MM/DD/YYYY"


def validate_contact_number(contact: str) -> tuple[bool, str]:
    """
    Validate contact number format
    """
    if not contact:
        return True, ""
        
    digits = "".join(filter(str.isdigit, contact))
    if len(digits) in [10, 11]:
        return True, ""
    return False, "Contact number must be 10 or 11 digits."


def validate_weight(weight: Optional[float]) -> tuple[bool, str]:
    """
    Validate weight value - no limits enforced

    Args:
        weight: Weight value to validate

    Returns:
        Tuple of (is_valid, error_message) - always valid
    """
    return True, ""


def validate_height(height: Optional[float]) -> tuple[bool, str]:
    """
    Validate height value - no limits enforced

    Args:
        height: Height value to validate

    Returns:
        Tuple of (is_valid, error_message) - always valid
    """
    return True, ""


def validate_temperature(temp: Optional[float]) -> tuple[bool, str]:
    """
    Validate temperature value - no limits enforced

    Args:
        temp: Temperature value to validate

    Returns:
        Tuple of (is_valid, error_message) - always valid
    """
    return True, ""


def validate_patient_name(name: str) -> tuple[bool, str]:
    """
    Validate patient name - no limits enforced

    Args:
        name: Patient name to validate

    Returns:
        Tuple of (is_valid, error_message) - always valid
    """
    return True, ""


def validate_contact_number(contact: str) -> tuple[bool, str]:
    """
    Validate contact number - no limits enforced

    Args:
        contact: Contact number to validate

    Returns:
        Tuple of (is_valid, warning_message) - always valid
    """
    return True, ""


def safe_float(val: str) -> Optional[float]:
    """
    Safely convert string to float
    
    Args:
        val: String value to convert
        
    Returns:
        Float value or None if conversion fails
    """
    val = val.strip()
    if not val:
        return None
    try:
        return float(val)
    except ValueError:
        return None


def calculate_age(dob_str: str) -> Optional[int]:
    """
    Calculate age from date of birth - OPTIMIZED O(1) date arithmetic
    
    Args:
        dob_str: Date of birth in YYYY-MM-DD format
        
    Returns:
        Age in years or None if invalid
    """
    if not dob_str:
        return None
    
    try:
        dob = datetime.datetime.strptime(dob_str, DATETIME_FORMATS['date_input']).date()
        today = datetime.date.today()
        
        # O(1) age calculation with leap year correction
        age = today.year - dob.year
        
        # Adjust if birthday hasn't occurred this year yet
        if (today.month, today.day) < (dob.month, dob.day):
            age -= 1
        
        return age
    except (ValueError, AttributeError):
        return None


def format_date_readable(date_str: str) -> str:
    """
    Format date to readable format - OPTIMIZED single parse
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Formatted date (e.g., "November 8, 2002") or original if invalid
    """
    if not date_str:
        return "Not provided"
    
    try:
        date_obj = datetime.datetime.strptime(date_str, DATETIME_FORMATS['date_input'])
        return date_obj.strftime("%B %d, %Y")
    except ValueError:
        return date_str