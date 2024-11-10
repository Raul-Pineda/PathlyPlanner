# models/recurring_task.py

from datetime import datetime, timedelta
from Models.task import Task

class RecurringTask(Task):
    def __init__(self, name, start_time, duration, recurrence_pattern, priority=0, is_immovable=False):
        """
        Initialize a RecurringTask.

        :param start_time: Start datetime of the first occurrence
        :param recurrence_pattern: Pattern of recurrence (e.g., daily, weekly)
        """
        super().__init__(name, duration, priority, is_immovable)
        self.start_time = start_time
        self.end_time = start_time + duration
        self.recurrence_pattern = recurrence_pattern  # e.g., "daily", "weekly"

    def schedule(self):
        """Logic to schedule each occurrence based on recurrence pattern."""
        print(f"Scheduling {self.name} recurring {self.recurrence_pattern} starting {self.start_time}")

    def get_next_occurrence(self, current_time):
        """Calculate the next occurrence of the recurring task after a given time."""
        if self.recurrence_pattern == "daily":
            return current_time + timedelta(days=1)
        elif self.recurrence_pattern == "weekly":
            return current_time + timedelta(weeks=1)
        # Add more patterns as needed