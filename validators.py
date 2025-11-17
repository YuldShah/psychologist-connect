"""Validation utilities for appointment booking"""
import re
from datetime import datetime, time
from typing import Tuple, Optional


WORKING_DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
WORKING_START = time(9, 0)  # 9:00 AM
WORKING_END = time(18, 0)   # 6:00 PM
LUNCH_START = time(13, 0)   # 1:00 PM
LUNCH_END = time(14, 0)     # 2:00 PM


def parse_time(time_str: str) -> Optional[time]:
    """
    Parse time string in various formats (HH:MM, H:MM, HH:MM AM/PM)
    Returns time object or None if invalid
    """
    time_str = time_str.strip().upper()

    # Try format: HH:MM or H:MM (24-hour)
    match = re.match(r'^(\d{1,2}):(\d{2})$', time_str)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return time(hour, minute)

    # Try format: HH:MM AM/PM or H:MM AM/PM (12-hour)
    match = re.match(r'^(\d{1,2}):(\d{2})\s*(AM|PM)$', time_str)
    if match:
        hour, minute, period = int(match.group(1)), int(match.group(2)), match.group(3)
        if 1 <= hour <= 12 and 0 <= minute <= 59:
            if period == 'PM' and hour != 12:
                hour += 12
            elif period == 'AM' and hour == 12:
                hour = 0
            return time(hour, minute)

    return None


def parse_date(date_str: str) -> Optional[Tuple[str, datetime]]:
    """
    Parse date string in various formats
    Returns tuple of (day_name, datetime) or None if invalid
    """
    date_str = date_str.strip().lower()

    # Try parsing day name
    for day in WORKING_DAYS:
        if day in date_str:
            return (day, None)

    # Try parsing date formats
    date_formats = [
        '%d.%m.%Y',  # 15.10.2024
        '%d/%m/%Y',  # 15/10/2024
        '%Y-%m-%d',  # 2024-10-15
        '%d.%m',     # 15.10
        '%d/%m',     # 15/10
    ]

    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            # If year not provided, use current year
            if fmt in ['%d.%m', '%d/%m']:
                parsed_date = parsed_date.replace(year=datetime.now().year)

            day_name = parsed_date.strftime('%A').lower()
            return (day_name, parsed_date)
        except ValueError:
            continue

    return None


def validate_appointment_time(date_str: str, time_str: str) -> Tuple[bool, str]:
    """
    Validate appointment date and time
    Returns (is_valid, error_message)
    """
    # Parse date
    date_result = parse_date(date_str)
    if not date_result:
        return False, "❌ Invalid date format. Please use formats like: 'Monday', '15.10.2024', '15/10/2024'"

    day_name, parsed_date = date_result

    # Check if working day
    if day_name not in WORKING_DAYS:
        return False, f"❌ We don't work on {day_name.capitalize()}s. Please choose Monday-Friday."

    # Parse time
    parsed_time = parse_time(time_str)
    if not parsed_time:
        return False, "❌ Invalid time format. Please use formats like: '10:00', '14:30', '2:00 PM'"

    # Check working hours
    if parsed_time < WORKING_START or parsed_time >= WORKING_END:
        return False, f"❌ Time must be between {WORKING_START.strftime('%H:%M')} and {WORKING_END.strftime('%H:%M')}."

    # Check lunch time
    if LUNCH_START <= parsed_time < LUNCH_END:
        return False, f"❌ Lunch time ({LUNCH_START.strftime('%H:%M')}-{LUNCH_END.strftime('%H:%M')}). Please choose another time."

    # Check if date is in the past
    if parsed_date:
        appointment_datetime = datetime.combine(parsed_date.date(), parsed_time)
        if appointment_datetime < datetime.now():
            return False, "❌ Cannot book appointments in the past. Please choose a future date."

    return True, "✅ Valid appointment time"


def format_working_hours() -> str:
    """Get formatted working hours string"""
    return (
        f"📅 <b>Working Hours:</b>\n"
        f"• Days: Monday - Friday\n"
        f"• Time: {WORKING_START.strftime('%H:%M')} - {WORKING_END.strftime('%H:%M')}\n"
        f"• Lunch: {LUNCH_START.strftime('%H:%M')} - {LUNCH_END.strftime('%H:%M')} (closed)"
    )
