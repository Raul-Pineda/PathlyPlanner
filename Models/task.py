# models/task.py

from abc import ABC, abstractmethod
from datetime import timedelta, datetime

class Task(ABC):
    def __init__(self, name, duration, priority=0, is_immovable=False, dependencies=None, deadline=None):
        """
        Initialize a Task.

        :param name: The name or description of the task
        :param duration: The time duration of the task, as a timedelta
        :param priority: Priority level of the task (higher values indicate higher priority)
        :param is_immovable: Flag to indicate if the task cannot be rescheduled
        :param dependencies: List of other Task objects that must be completed before this one
        :param deadline: Optional deadline for task completion
        """
        self.name = name
        self.duration = duration  # timedelta object representing task duration
        self.priority = priority
        self.is_immovable = is_immovable
        self.dependencies = dependencies if dependencies else []
        self.deadline = deadline  # Optional, datetime object
        self.start_time = None  # Start time will be determined by schedule method
        self.end_time = None  # End time will be calculated after scheduling

    def add_dependency(self, task):
        """
        Add a dependency for this task.
        :param task: Task object that must be completed before this task
        """
        if task not in self.dependencies:
            self.dependencies.append(task)

    def is_ready_to_schedule(self):
        """
        Checks if all dependencies have been completed.
        :return: True if ready to schedule, otherwise False
        """
        for task in self.dependencies:
            if task.end_time is None or task.end_time > datetime.now():
                return False
        return True

    def has_deadline(self):
        """
        Check if the task has a deadline.
        :return: True if there is a deadline, False otherwise
        """
        return self.deadline is not None

    def is_overdue(self):
        """
        Check if the task is overdue.
        :return: True if the task is overdue, False otherwise
        """
        if self.deadline and datetime.now() > self.deadline:
            return True
        return False

    def set_scheduled_time(self, start_time):
        """
        Sets the start and end times for the task.
        :param start_time: datetime object indicating when the task should start
        """
        self.start_time = start_time
        self.end_time = start_time + self.duration

    @abstractmethod
    def schedule(self):
        """Abstract method to schedule the task. Must be implemented by subclasses."""
        pass