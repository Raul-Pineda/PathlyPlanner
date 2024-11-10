# utils/date_helpers.py

from datetime import datetime, timedelta

def calculate_time_difference(start_time, end_time):
    """Calculate the difference between two times and return a timedelta object."""
    return end_time - start_time

def add_buffer_time(start_time, buffer_minutes):
    """Add buffer time to a start time and return the new time."""
    return start_time + timedelta(minutes=buffer_minutes)

def is_within_time_range(task_start, task_end, check_time):
    """Check if a given time falls within a task's time range."""
    return task_start <= check_time <= task_end

def format_datetime(dt):
    """Format a datetime object as a string for consistent display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_datetime(date_str, fmt="%Y-%m-%d %H:%M:%S"):
    """Parse a date string to a datetime object using a specified format."""
    return datetime.strptime(date_str, fmt)