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
    except:
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
    except:
        # Try alternate format
        try:
            dt = datetime.datetime.fromisoformat(timestamp_str)
            return dt.strftime(DATETIME_FORMATS['timestamp_display'])
        except:
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
        except:
            continue
    
    # Try 24-hour format (e.g., "14:30")
    for fmt in ["%H:%M", "%H:%M:%S"]:
        try:
            dt = datetime.datetime.strptime(time_str, fmt)
            return dt.strftime(DATETIME_FORMATS['time_24hr'])
        except:
            continue
    
    return None


def get_current_date() -> str:
    """
    Get current date in YYYY-MM-DD format
    
    Returns:
        Current date string
    """
    return datetime.date.today().strftime(DATETIME_FORMATS['date_input'])


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


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def validate_date(date_str: str) -> tuple[bool, str]:
    """
    Validate date string format
    
    Args:
        date_str: Date string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not date_str:
        return False, "Date is required"
    
    try:
        datetime.datetime.strptime(date_str, DATETIME_FORMATS['date_input'])
        return True, ""
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"


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