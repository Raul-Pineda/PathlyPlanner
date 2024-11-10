# models/scheduled_task.py

from datetime import datetime

class ScheduledTask:
    def __init__(self, task, start_time):
        """
        Initialize a ScheduledTask.

        :param task: The original task being scheduled
        :param start_time: Start datetime of the scheduled task
        """
        self.task = task  # The original Task object
        self.start_time = start_time
        self.end_time = start_time + task.duration  # Calculate end time based on task duration

    def __repr__(self):
        return f"{self.task.name} scheduled from {self.start_time} to {self.end_time}"